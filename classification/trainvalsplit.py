#!/usr/bin/env python3
"""
Create an 80/20 train/val split for a species-folder YOLO dataset.

Expected structure:
root/
├── images/
│   └── train/
│       ├── alfalfa_weevil/
│       ├── aphids/
│       └── ...
└── labels/
    └── train/
        ├── alfalfa_weevil/
        ├── aphids/
        └── ...

Output:
- moves 20% of each class from train -> val
- preserves image/label pairing
- creates:
    images/val/<species>/
    labels/val/<species>/

Behavior:
- split is per species folder
- random but reproducible with fixed seed
- moves files, does not copy
"""

from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

VAL_RATIO = 0.20
SEED = 42


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTS


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def gather_pairs(
    images_species_dir: Path,
    labels_species_dir: Path
) -> Tuple[List[Tuple[Path, Path]], List[Path], List[Path]]:
    image_files = sorted([p for p in images_species_dir.iterdir() if is_image(p)])
    label_files = sorted([p for p in labels_species_dir.glob("*.txt") if p.is_file()])

    labels_by_stem: Dict[str, Path] = {p.stem: p for p in label_files}
    images_by_stem: Dict[str, Path] = {p.stem: p for p in image_files}

    pairs: List[Tuple[Path, Path]] = []
    missing_labels: List[Path] = []
    missing_images: List[Path] = []

    for img in image_files:
        lbl = labels_by_stem.get(img.stem)
        if lbl is None:
            missing_labels.append(img)
        else:
            pairs.append((img, lbl))

    for lbl in label_files:
        if lbl.stem not in images_by_stem:
            missing_images.append(lbl)

    return pairs, missing_labels, missing_images


def move_pair(
    img_path: Path,
    lbl_path: Path,
    dst_img_dir: Path,
    dst_lbl_dir: Path
) -> None:
    ensure_dir(dst_img_dir)
    ensure_dir(dst_lbl_dir)

    dst_img = dst_img_dir / img_path.name
    dst_lbl = dst_lbl_dir / lbl_path.name

    if dst_img.exists() or dst_lbl.exists():
        raise FileExistsError(
            f"Destination already exists:\n"
            f"  {dst_img}\n"
            f"  {dst_lbl}"
        )

    shutil.move(str(img_path), str(dst_img))
    shutil.move(str(lbl_path), str(dst_lbl))


def main() -> None:
    root = Path.cwd()

    train_images_root = root / "images" / "train"
    train_labels_root = root / "labels" / "train"
    val_images_root = root / "images" / "val"
    val_labels_root = root / "labels" / "val"

    if not train_images_root.exists():
        raise SystemExit(f"Missing folder: {train_images_root}")
    if not train_labels_root.exists():
        raise SystemExit(f"Missing folder: {train_labels_root}")

    random.seed(SEED)

    species_dirs = sorted([p for p in train_images_root.iterdir() if p.is_dir()])
    if not species_dirs:
        raise SystemExit(f"No species folders found in {train_images_root}")

    total_moved = 0
    total_pairs = 0
    total_missing_labels = 0
    total_missing_images = 0

    for images_species_dir in species_dirs:
        species_name = images_species_dir.name
        labels_species_dir = train_labels_root / species_name

        if not labels_species_dir.exists() or not labels_species_dir.is_dir():
            print(f"[WARN] Missing matching labels folder for species: {species_name}")
            continue

        pairs, missing_labels, missing_images = gather_pairs(
            images_species_dir,
            labels_species_dir
        )

        total_missing_labels += len(missing_labels)
        total_missing_images += len(missing_images)
        total_pairs += len(pairs)

        if missing_labels:
            print(f"\n[WARN] {species_name}: images with no matching label:")
            for p in missing_labels:
                print(f"  {p.name}")

        if missing_images:
            print(f"\n[WARN] {species_name}: labels with no matching image:")
            for p in missing_images:
                print(f"  {p.name}")

        n = len(pairs)
        if n == 0:
            print(f"{species_name}: 0 matched pairs, skipping")
            continue

        n_val = int(round(n * VAL_RATIO))

        # Prevent stupid edge cases
        if n > 1 and n_val == 0:
            n_val = 1
        if n_val >= n and n > 1:
            n_val = n - 1

        random.shuffle(pairs)
        val_pairs = pairs[:n_val]

        dst_img_dir = val_images_root / species_name
        dst_lbl_dir = val_labels_root / species_name

        for img_path, lbl_path in val_pairs:
            move_pair(img_path, lbl_path, dst_img_dir, dst_lbl_dir)

        total_moved += len(val_pairs)
        print(f"{species_name}: moved {len(val_pairs)} of {n} pairs to val")

    print("\n=== DONE ===")
    print(f"Root: {root}")
    print(f"Total matched pairs seen: {total_pairs}")
    print(f"Total moved to val: {total_moved}")
    print(f"Images missing labels: {total_missing_labels}")
    print(f"Labels missing images: {total_missing_images}")
    print(f"Seed: {SEED}")
    print(f"Validation ratio: {VAL_RATIO:.2f}")


if __name__ == "__main__":
    main()
