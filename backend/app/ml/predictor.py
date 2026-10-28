"""Loads the trained model once and runs predictions (+ Grad-CAM)."""
import threading
import urllib.request
from dataclasses import dataclass

import numpy as np
import torch
from PIL import Image

from app.config import MODEL_PATH, MODEL_URL
from app.ml.gradcam import GradCAM, overlay_heatmap
from app.ml.model import DEFAULT_CLASS_NAMES, build_model
from app.ml.preprocess import eval_transform


@dataclass
class PredictionResult:
    label: str
    confidence: float
    normal_prob: float
    defective_prob: float
    heatmap_rgb: np.ndarray


class DefectPredictor:
    def __init__(self):
        self.model = None
        self.gradcam = None
        self.class_names = DEFAULT_CLASS_NAMES
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._lock = threading.Lock()  # Grad-CAM uses shared state -> one request at a time

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def load(self) -> bool:
        """Try to load the trained weights. Returns True on success."""
        if not MODEL_PATH.exists() and MODEL_URL:
            print(f"[model] Downloading model from MODEL_URL ...")
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

        if not MODEL_PATH.exists():
            print(f"[model] NOT FOUND: {MODEL_PATH}\n"
                  f"        Train the model first (see README). API will run but /predict returns 503.")
            return False

        checkpoint = torch.load(MODEL_PATH, map_location=self.device)
        self.class_names = checkpoint.get("class_names", DEFAULT_CLASS_NAMES)
        model = build_model(pretrained=False)
        model.load_state_dict(checkpoint["model_state"])
        model.to(self.device).eval()
        self.model = model
        self.gradcam = GradCAM(model, model.layer3)
        print(f"[model] Loaded ResNet50 from {MODEL_PATH} on {self.device}")
        return True

    def predict(self, image: Image.Image) -> PredictionResult:
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded")
        image = image.convert("RGB")
        original = np.array(image)
        x = eval_transform(image).unsqueeze(0).to(self.device)

        with self._lock:
            probs, pred_idx, cam = self.gradcam.run(x)

        defective_idx = self.class_names.index("defective")
        normal_idx = self.class_names.index("normal")
        return PredictionResult(
            label=self.class_names[pred_idx],
            confidence=float(probs[pred_idx]),
            normal_prob=float(probs[normal_idx]),
            defective_prob=float(probs[defective_idx]),
            heatmap_rgb=overlay_heatmap(original, cam),
        )


predictor = DefectPredictor()  # one shared instance
