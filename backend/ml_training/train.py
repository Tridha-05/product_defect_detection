"""
STEP 2 of training: fine-tune ResNet50 on data/processed.

Run (from the backend folder):
    python ml_training/train.py                 # quick: trains layer4 + classifier (good for CPU)
    python ml_training/train.py --epochs 15
    python ml_training/train.py --full          # fine-tune the whole network (slower, needs GPU ideally)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets us import "app"

import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm

from app.config import MODEL_PATH
from app.ml.model import build_model
from app.ml.preprocess import IMAGE_SIZE, IMAGENET_MEAN, IMAGENET_STD, eval_transform

PROJECT_ROOT = Path(__file__).resolve().parents[2]

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.15, contrast=0.15),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])


def set_trainable(model, full: bool):
    for p in model.parameters():
        p.requires_grad = full
    if not full:  # only the last block + classifier learn (fast, works well on small data)
        for p in list(model.layer4.parameters()) + list(model.fc.parameters()):
            p.requires_grad = True


def set_train_mode(model, full: bool):
    model.train()
    if not full:  # keep the frozen part's BatchNorm statistics fixed
        for m in (model.conv1, model.bn1, model.layer1, model.layer2, model.layer3):
            m.eval()


def run_epoch(model, loader, device, criterion, optimizer=None, full=False):
    training = optimizer is not None
    if training:
        set_train_mode(model, full)
    else:
        model.eval()
    total_loss, preds_all, labels_all = 0.0, [], []
    for images, labels in tqdm(loader, leave=False, desc="train" if training else "val  "):
        images, labels = images.to(device), labels.to(device)
        with torch.set_grad_enabled(training):
            outputs = model(images)
            loss = criterion(outputs, labels)
            if training:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        total_loss += loss.item() * images.size(0)
        preds_all += outputs.argmax(1).cpu().tolist()
        labels_all += labels.cpu().tolist()
    n = len(labels_all)
    acc = sum(int(p == l) for p, l in zip(preds_all, labels_all)) / n
    f1 = f1_score(labels_all, preds_all, average="macro")
    return total_loss / n, acc, f1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(PROJECT_ROOT / "data" / "processed"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--full", action="store_true", help="fine-tune ALL layers")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not (data_dir / "train").exists():
        sys.exit(f"[error] {data_dir}/train not found. Run prepare_dataset.py first.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_ds = datasets.ImageFolder(data_dir / "train", transform=train_transform)
    val_ds = datasets.ImageFolder(data_dir / "val", transform=eval_transform)
    class_names = train_ds.classes  # ['defective', 'normal']
    print("Classes:", class_names, "| train:", len(train_ds), "| val:", len(val_ds))

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)

    # Class weights: handles "many more defective than normal" (or vice-versa)
    counts = torch.bincount(torch.tensor(train_ds.targets), minlength=len(class_names)).float()
    class_weights = (counts.sum() / (len(class_names) * counts)).to(device)
    print("Class weights:", dict(zip(class_names, [round(w, 2) for w in class_weights.tolist()])))
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    model = build_model(pretrained=True).to(device)   # downloads ImageNet weights the first time
    set_trainable(model, args.full)
    optimizer = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=args.lr)

    best_f1, history = -1.0, []
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        tr_loss, tr_acc, _ = run_epoch(model, train_loader, device, criterion, optimizer, args.full)
        va_loss, va_acc, va_f1 = run_epoch(model, val_loader, device, criterion)
        history.append({"epoch": epoch, "train_loss": tr_loss, "train_acc": tr_acc,
                        "val_loss": va_loss, "val_acc": va_acc, "val_f1": va_f1})
        flag = ""
        if va_f1 > best_f1:
            best_f1 = va_f1
            torch.save({"model_state": model.state_dict(), "class_names": class_names,
                        "image_size": IMAGE_SIZE, "val_f1": float(va_f1)}, MODEL_PATH)
            flag = "  <-- saved best model"
        print(f"Epoch {epoch:02d}/{args.epochs} | train loss {tr_loss:.4f} acc {tr_acc:.3f} | "
              f"val loss {va_loss:.4f} acc {va_acc:.3f} F1 {va_f1:.3f}{flag}")

    (MODEL_PATH.parent / "training_history.json").write_text(json.dumps(history, indent=2))
    print(f"\nDone. Best val F1 = {best_f1:.3f}. Model saved at: {MODEL_PATH}")


if __name__ == "__main__":
    main()
