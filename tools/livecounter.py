#!/usr/bin/env python3
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT = Path("test_suite")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

# Starting offsets for classes that already have images elsewhere
# Add any other classes here if needed
STARTING_INDEX = {
    "alfalfa_weevil": 56,
}

def get_next_index(class_dir: Path) -> int:
    """Figure out the next index based on existing files in the folder."""
    class_name = class_dir.name
    existing = [
        f for f in class_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    ]

    # Find highest existing index from already-renamed files
    max_index = 0
    for f in existing:
        stem = f.stem  # e.g. alfalfa_weevil_0056
        if stem.startswith(class_name + "_"):
            try:
                idx = int(stem[len(class_name) + 1:])
                max_index = max(max_index, idx)
            except ValueError:
                pass

    # If no renamed files exist yet, use the starting offset if defined
    if max_index == 0:
        return STARTING_INDEX.get(class_name, 1)
    else:
        return max_index + 1


def rename_file(path: Path):
    """Rename a newly added image to follow class naming convention."""
    class_dir = path.parent
    class_name = class_dir.name

    # Small delay to ensure the file is fully written before renaming
    time.sleep(0.5)

    if not path.exists():
        return  # File may have already been renamed or moved

    next_idx = get_next_index(class_dir)
    new_name = f"{class_name}_{next_idx:04d}.png"
    new_path = class_dir / new_name

    try:
        path.rename(new_path)
        print(f"  [RENAMED] {path.name} -> {new_name}")
    except Exception as e:
        print(f"  [ERROR] Could not rename {path.name}: {e}")


def count_images():
    counts = {}
    for class_dir in ROOT.iterdir():
        if class_dir.is_dir():
            counts[class_dir.name] = sum(
                1 for f in class_dir.iterdir()
                if f.is_file() and f.suffix.lower() in IMAGE_EXTS
            )
    return counts


def print_counts():
    counts = count_images()
    print("\n=== Current Counts ===")
    for cls in sorted(counts):
        print(f"  {cls:<25} {counts[cls]}")
    print("----------------------")


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            path = Path(event.src_path)
            if path.suffix.lower() in IMAGE_EXTS:
                print(f"\n[NEW] Detected: {path.name} in '{path.parent.name}'")
                rename_file(path)
                print_counts()

    def on_deleted(self, event):
        if not event.is_directory:
            path = Path(event.src_path)
            if path.suffix.lower() in IMAGE_EXTS:
                print(f"\n[DELETED] {path.name} from '{path.parent.name}'")
                print_counts()


if __name__ == "__main__":
    if not ROOT.exists():
        print("Create a 'ToAdd' folder first.")
        exit()

    print("Watching folder:", ROOT.resolve())
    print_counts()

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, str(ROOT), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()