#!/usr/bin/env python3
"""
Collapse species-level YOLO labels into bucket-level YOLO labels.

Expected root structure:
./data.yaml
./yolo.yaml
./images/train/<species_name>/*
./labels/train/<species_name>/*.txt
./images/val/<species_name>/*
./labels/val/<species_name>/*.txt

Output:
./collapsed/train/images/*
./collapsed/train/labels/*
./collapsed/val/images/*
./collapsed/val/labels/*

Behavior:
- reads original species names from data.yaml
- reads bucket names from yolo.yaml
- uses hardcoded species -> bucket mapping
- scans all species subfolders under images/{split} and labels/{split}
- rewrites labels from species IDs to bucket IDs
- copies matching images into collapsed/{split}/images
- copies, never moves
- quarantines files containing ignored/unmapped species
- handles filename collisions in flattened YOLO output
"""

from __future__ import annotations

import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import yaml

IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"]

SPECIES_TO_BUCKET = {
    "alfalfa_weevil": "weevils",
    "aphids": "tiny_pests",
    "army_worm": "caterpillars",
    "black_cutworm": "caterpillars",
    "blister_beetle": "blister_beetle",
    "corn_borer": "borers",
    "flea_beetle": "flea_beetle",
    "strawberry_root_weevil": "weevils",
    "grub": "soil_larvae",
    "miridae": "plant_bugs",
    "peach_borer": "borers",
    "red_spider": "tiny_pests",
    "tarnished_plant_bug": "plant_bugs",
    "thrips": "tiny_pests",
    "wireworm": "soil_larvae",
    "four_lined_plant_bug": "plant_bugs",
    "grape_flea_beetle": "flea_beetle",
    "black_blister_beetle": "blister_beetle",
    "brown_marmorated_stink_bug": "stink_bugs",
    "colorado_potato_beetle": "potato_beetle",
    "green_stink_bug": "stink_bugs",
    "striped_blister_beetle": "blister_beetle",
    "striped_flea_beetle": "flea_beetle",
}

IGNORED_SPECIES = {
    "oides_decempunctata",
}

QUARANTINE_ON_IGNORED = True
SPLITS = ["train", "val"]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_names_map(yaml_path: Path) -> Dict[int, str]:
    data = load_yaml(yaml_path)
    names = data.get("names")
    if names is None:
        raise ValueError(f"'names' not found in {yaml_path}")

    out: Dict[int, str] = {}
    if isinstance(names, dict):
        for k, v in names.items():
            out[int(k)] = str(v)
    elif isinstance(names, list):
        for i, v in enumerate(names):
            out[i] = str(v)
    else:
        raise ValueError(f"'names' must be dict or list in {yaml_path}")
    return out


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def write_lines(path: Path, lines: List[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")


def find_matching_image(images_species_dir: Path, stem: str) -> Optional[Path]:
    for ext in IMAGE_EXTS:
        p = images_species_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def next_flat_paths(
    out_images_dir: Path,
    out_labels_dir: Path,
    base_stem: str,
    image_suffix: str,
    label_suffix: str = ".txt",
) -> tuple[Path, Path]:
    out_label_path = out_labels_dir / f"{base_stem}{label_suffix}"
    out_image_path = out_images_dir / f"{base_stem}{image_suffix}"

    if not out_label_path.exists() and not out_image_path.exists():
        return out_image_path, out_label_path

    i = 1
    while True:
        candidate_label = out_labels_dir / f"{base_stem}_{i}{label_suffix}"
        candidate_image = out_images_dir / f"{base_stem}_{i}{image_suffix}"
        if not candidate_label.exists() and not candidate_image.exists():
            return candidate_image, candidate_label
        i += 1


def validate_bucket_mapping(
    source_id_to_species: Dict[int, str],
    bucket_name_to_id: Dict[str, int],
) -> None:
    bad_bucket_names = sorted(set(SPECIES_TO_BUCKET.values()) - set(bucket_name_to_id.keys()))
    if bad_bucket_names:
        raise SystemExit(
            "These bucket names from SPECIES_TO_BUCKET are missing in yolo.yaml:\n"
            + "\n".join(f"  - {name}" for name in bad_bucket_names)
        )

    unmapped_species = []
    for _, species_name in sorted(source_id_to_species.items()):
        if species_name not in SPECIES_TO_BUCKET and species_name not in IGNORED_SPECIES:
            unmapped_species.append(species_name)

    if unmapped_species:
        print("[WARN] These species are in data.yaml but not mapped or ignored:")
        for name in unmapped_species:
            print(f"  - {name}")


def process_split(
    split: str,
    root: Path,
    source_id_to_species: Dict[int, str],
    bucket_name_to_id: Dict[str, int],
    stats: defaultdict,
) -> None:
    images_root = root / "images" / split
    labels_root = root / "labels" / split

    out_images_dir = root / "collapsed" / split / "images"
    out_labels_dir = root / "collapsed" / split / "labels"

    quarantine_images_dir = root / "collapsed_quarantine" / split / "images"
    quarantine_labels_dir = root / "collapsed_quarantine" / split / "labels"

    if not images_root.exists():
        print(f"[WARN] Missing images root for split '{split}': {images_root}")
        stats[f"{split}_missing_split_images_root"] += 1
        return

    if not labels_root.exists():
        print(f"[WARN] Missing labels root for split '{split}': {labels_root}")
        stats[f"{split}_missing_split_labels_root"] += 1
        return

    label_species_dirs = sorted([p for p in labels_root.iterdir() if p.is_dir()])
    if not label_species_dirs:
        print(f"[WARN] No species folders found in {labels_root}")
        stats[f"{split}_no_species_folders"] += 1
        return

    for labels_species_dir in label_species_dirs:
        species_folder = labels_species_dir.name
        images_species_dir = images_root / species_folder

        if not images_species_dir.exists() or not images_species_dir.is_dir():
            print(f"[WARN] Missing matching image folder for {split}/{species_folder}")
            stats[f"{split}_missing_species_image_folders"] += 1
            continue

        label_files = sorted(labels_species_dir.glob("*.txt"))

        for label_path in label_files:
            stem = label_path.stem
            image_path = find_matching_image(images_species_dir, stem)

            if image_path is None:
                print(f"[WARN] Missing image for label: {split}/{species_folder}/{label_path.name}")
                stats[f"{split}_missing_images"] += 1
                continue

            output_lines: List[str] = []
            saw_valid = False
            saw_ignored_or_unmapped = False
            bad_format = False

            with label_path.open("r", encoding="utf-8") as f:
                for line_num, raw in enumerate(f, start=1):
                    line = raw.strip()
                    if not line:
                        continue

                    parts = line.split()
                    if len(parts) < 5:
                        print(f"[WARN] Bad YOLO line in {label_path}:{line_num} -> {line}")
                        bad_format = True
                        break

                    try:
                        src_id = int(float(parts[0]))
                    except ValueError:
                        print(f"[WARN] Bad class ID in {label_path}:{line_num} -> {parts[0]}")
                        bad_format = True
                        break

                    species_name = source_id_to_species.get(src_id)
                    if species_name is None:
                        print(f"[WARN] Unknown source class id {src_id} in {label_path}:{line_num}")
                        saw_ignored_or_unmapped = True
                        continue

                    if species_name in IGNORED_SPECIES:
                        saw_ignored_or_unmapped = True
                        continue

                    bucket_name = SPECIES_TO_BUCKET.get(species_name)
                    if bucket_name is None:
                        saw_ignored_or_unmapped = True
                        continue

                    bucket_id = bucket_name_to_id[bucket_name]
                    new_line = " ".join([str(bucket_id)] + parts[1:])
                    output_lines.append(new_line)
                    saw_valid = True

            if bad_format:
                stats[f"{split}_bad_labels"] += 1
                continue

            if saw_ignored_or_unmapped and QUARANTINE_ON_IGNORED:
                q_image_path, q_label_path = next_flat_paths(
                    quarantine_images_dir,
                    quarantine_labels_dir,
                    label_path.stem,
                    image_path.suffix,
                    label_path.suffix,
                )
                copy_file(label_path, q_label_path)
                copy_file(image_path, q_image_path)
                stats[f"{split}_quarantined_ignored_or_unmapped"] += 1
                continue

            if not saw_valid:
                stats[f"{split}_empty_after_collapse"] += 1
                continue

            out_image_path, out_label_path = next_flat_paths(
                out_images_dir,
                out_labels_dir,
                label_path.stem,
                image_path.suffix,
                label_path.suffix,
            )

            write_lines(out_label_path, output_lines)
            copy_file(image_path, out_image_path)
            stats[f"{split}_written"] += 1


def main() -> None:
    root = Path.cwd()

    species_yaml = root / "data.yaml"
    bucket_yaml = root / "yolo.yaml"

    if not species_yaml.exists():
        raise SystemExit(f"Missing data.yaml: {species_yaml}")
    if not bucket_yaml.exists():
        raise SystemExit(f"Missing yolo.yaml: {bucket_yaml}")

    source_id_to_species = load_names_map(species_yaml)
    bucket_id_to_name = load_names_map(bucket_yaml)
    bucket_name_to_id = {name: idx for idx, name in bucket_id_to_name.items()}

    validate_bucket_mapping(source_id_to_species, bucket_name_to_id)

    stats = defaultdict(int)

    for split in SPLITS:
        print(f"\n=== PROCESSING {split.upper()} ===")
        process_split(split, root, source_id_to_species, bucket_name_to_id, stats)

    print("\n=== DONE ===")
    print(f"Root: {root}")

    print("\n=== BUCKET IDS FROM yolo.yaml ===")
    for idx, name in sorted(bucket_id_to_name.items()):
        print(f"{idx}: {name}")

    print("\n=== OUTPUT STRUCTURE ===")
    for split in SPLITS:
        print(f"collapsed/{split}/images")
        print(f"collapsed/{split}/labels")
        print(f"collapsed_quarantine/{split}/images")
        print(f"collapsed_quarantine/{split}/labels")

    print("\n=== STATS ===")
    for k in sorted(stats):
        print(f"{k}: {stats[k]}")


if __name__ == "__main__":
    main()
