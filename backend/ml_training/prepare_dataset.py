"""
STEP 1 of training: turn the raw MVTec AD folders into a labelled
normal-vs-defective dataset with a strict train / val / test split.

Raw MVTec layout:   data/mvtec_ad/<category>/train/good/*.png
                    data/mvtec_ad/<category>/test/good/*.png
                    data/mvtec_ad/<category>/test/<defect_type>/*.png

Output:             data/processed/{train,val,test}/{normal,defective}/*.png
                    data/processed/metadata.csv

Run (from the backend folder):
    python ml_training/prepare_dataset.py --categories bottle
    python ml_training/prepare_dataset.py --categories bottle cable screw
    python ml_training/prepare_dataset.py --categories all
"""
import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp"}


def list_images(folder: Path):
    return sorted(p for p in folder.glob("*") if p.suffix.lower() in IMG_EXT)


def collect(mvtec_dir: Path, categories):
    rows = []
    for cat in categories:
        cat_dir = mvtec_dir / cat
        if not cat_dir.exists():
            print(f"[warn] category folder not found, skipping: {cat_dir}")
            continue
        # Normal = defect-free images from both train/good and test/good
        for sub in ("train/good", "test/good"):
            for img in list_images(cat_dir / sub):
                rows.append({"path": str(img), "label": "normal", "category": cat, "defect_type": "good"})
        # Defective = every other folder inside test/
        test_dir = cat_dir / "test"
        if test_dir.exists():
            for defect_dir in sorted(d for d in test_dir.iterdir() if d.is_dir() and d.name != "good"):
                for img in list_images(defect_dir):
                    rows.append({"path": str(img), "label": "defective", "category": cat,
                                 "defect_type": defect_dir.name})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mvtec-dir", default=str(PROJECT_ROOT / "data" / "mvtec_ad"))
    parser.add_argument("--out-dir", default=str(PROJECT_ROOT / "data" / "processed"))
    parser.add_argument("--categories", nargs="+", default=["bottle"],
                        help="e.g. bottle cable  OR  all")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    mvtec_dir, out_dir = Path(args.mvtec_dir), Path(args.out_dir)
    if not mvtec_dir.exists():
        sys.exit(f"[error] MVTec folder not found: {mvtec_dir}\n"
                 f"        Put the downloaded category folders (e.g. bottle/) inside it.")

    if args.categories == ["all"]:
        categories = sorted(d.name for d in mvtec_dir.iterdir() if (d / "test").exists())
    else:
        categories = args.categories
    print(f"Categories: {categories}")

    df = collect(mvtec_dir, categories)
    if df.empty:
        sys.exit("[error] No images found. Check the folder structure (see README).")

    # Strict split: 70% train / 15% val / 15% test, stratified by label
    train_df, temp_df = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=args.seed)
    val_df, test_df = train_test_split(temp_df, test_size=0.50, stratify=temp_df["label"], random_state=args.seed)
    train_df, val_df, test_df = train_df.assign(split="train"), val_df.assign(split="val"), test_df.assign(split="test")
    full = pd.concat([train_df, val_df, test_df], ignore_index=True)

    if out_dir.exists():
        shutil.rmtree(out_dir)

    new_paths = []
    for _, r in full.iterrows():
        src = Path(r["path"])
        dst_dir = out_dir / r["split"] / r["label"]
        dst_dir.mkdir(parents=True, exist_ok=True)
        # prefix avoids name clashes (every defect folder has a 000.png)
        dst = dst_dir / f"{r['category']}_{r['defect_type']}_{src.name}"
        shutil.copy2(src, dst)
        new_paths.append(str(dst))
    full["processed_path"] = new_paths
    full.to_csv(out_dir / "metadata.csv", index=False)

    print("\nDataset ready in:", out_dir)
    print(full.groupby(["split", "label"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()
