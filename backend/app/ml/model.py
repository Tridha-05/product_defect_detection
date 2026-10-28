"""ResNet50 model definition (transfer learning)."""
import torch.nn as nn
from torchvision import models

# ImageFolder sorts folders alphabetically: defective=0, normal=1
DEFAULT_CLASS_NAMES = ["defective", "normal"]


def build_model(pretrained: bool = True, num_classes: int = 2) -> nn.Module:
    """ResNet50 with a new 2-class head. pretrained=True downloads ImageNet weights."""
    weights = models.ResNet50_Weights.DEFAULT if pretrained else None
    model = models.resnet50(weights=weights)
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(model.fc.in_features, num_classes),
    )
    return model
