"""Grad-CAM: shows WHICH regions of the image influenced the model's decision."""
import cv2
import numpy as np
import torch


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.activations = None
        self.gradients = None
        target_layer.register_forward_hook(self._save_activation)

    def _save_activation(self, module, inputs, output):
        self.activations = output.detach()
        if output.requires_grad:
            output.register_hook(lambda grad: setattr(self, "gradients", grad.detach()))

    def run(self, x: torch.Tensor):
        """Forward + backward once. Returns (probabilities, predicted_index, cam[0..1] 7x7-ish)."""
        self.model.eval()
        self.model.zero_grad()
        x = x.clone().requires_grad_(True)  # guarantees gradients flow
        with torch.enable_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1)[0].detach()
            pred_idx = int(probs.argmax().item())
            logits[0, pred_idx].backward()

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)          # importance of each channel
        cam = torch.relu((weights * self.activations).sum(dim=1))[0]      # weighted sum
        cam = cam.cpu().numpy()
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        return probs.cpu().numpy(), pred_idx, cam


def overlay_heatmap(original_rgb: np.ndarray, cam: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Blend a coloured heatmap on top of the original image (RGB uint8 in, RGB uint8 out)."""
    h, w = original_rgb.shape[:2]
    cam_resized = cv2.resize(cam, (w, h), interpolation=cv2.INTER_CUBIC)
    cam_resized = np.clip(cam_resized, 0, 1)
    heat_bgr = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    heat_rgb = cv2.cvtColor(heat_bgr, cv2.COLOR_BGR2RGB)
    blended = (alpha * heat_rgb + (1 - alpha) * original_rgb).astype(np.uint8)
    return blended
