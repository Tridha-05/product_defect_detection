"""
STEP 3 of training: test the saved model on the UNSEEN test split.
Prints accuracy / precision / recall / F1 and saves a confusion matrix image.

Run (from the backend folder):
    python ml_training/evaluate.py
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")  # no pop-up window needed
import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from torch.utils.data import DataLoader
from torchvision import datasets

from app.config import MODEL_PATH
from app.ml.model import build_model
from app.ml.preprocess import eval_transform

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(PROJECT_ROOT / "data" / "processed"))
    args = parser.parse_args()

    if not MODEL_PATH.exists():
        sys.exit(f"[error] No trained model at {MODEL_PATH}. Run train.py first.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(MODEL_PATH, map_location=device)
    class_names = ckpt["class_names"]
    model = build_model(pretrained=False)
    model.load_state_dict(ckpt["model_state"])
    model.to(device).eval()

    test_ds = datasets.ImageFolder(Path(args.data_dir) / "test", transform=eval_transform)
    loader = DataLoader(test_ds, batch_size=16, shuffle=False, num_workers=0)

    y_true, y_pred = [], []
    with torch.no_grad():
        for images, labels in loader:
            out = model(images.to(device))
            y_pred += out.argmax(1).cpu().tolist()
            y_true += labels.tolist()

    pos = class_names.index("defective")  # "positive" = defective
    metrics = {
        "test_images": len(y_true),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_defective": precision_score(y_true, y_pred, pos_label=pos, zero_division=0),
        "recall_defective": recall_score(y_true, y_pred, pos_label=pos, zero_division=0),
        "f1_defective": f1_score(y_true, y_pred, pos_label=pos, zero_division=0),
    }
    cm = confusion_matrix(y_true, y_pred)

    print("\n=== TEST RESULTS (unseen images) ===")
    for k, v in metrics.items():
        print(f"{k:22s}: {v:.4f}" if isinstance(v, float) else f"{k:22s}: {v}")
    print("\n", classification_report(y_true, y_pred, target_names=class_names, zero_division=0))
    print("Confusion matrix (rows = true, cols = predicted):", class_names)
    print(cm)

    out_dir = MODEL_PATH.parent
    (out_dir / "test_metrics.json").write_text(json.dumps({**metrics, "confusion_matrix": cm.tolist(),
                                                           "classes": class_names}, indent=2))
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.imshow(cm, cmap="Greens")
    ax.set_xticks(range(len(class_names)), class_names)
    ax.set_yticks(range(len(class_names)), class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion Matrix")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=14,
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(out_dir / "confusion_matrix.png", dpi=150)
    print(f"\nSaved: {out_dir / 'test_metrics.json'} and confusion_matrix.png")


if __name__ == "__main__":
    main()
