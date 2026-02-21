## Overview

GrowLiv-Dataset contains annotated insect pest images used for training
the GrowLiv detection and classification pipeline.

The dataset focuses on Ontario-relevant agricultural pest species.

## Folder Structure

```
GrowLiv-Dataset/
├── images/
│   ├── alfalfa_weevil/
│   ├── aphids/
│   ├── army_worm/
│   └── ...
│
├── labels/
│   ├── alfalfa_weevil/
│   ├── aphids/
│   ├── army_worm/
│   └── ...
│
└── test/
    ├── alfalfa_weevil/
    ├── aphids/
    ├── army_worm/
    └── ...
```

- `images/` — Training images organized by species
- `labels/` — YOLO-format annotations corresponding to images/
- `test/` — Evaluation images organized by species (not used during training)

## Annotation Format

Annotations follow YOLO format:

```
<class_id> <x_center> <y_center> <width> <height>
```

- Coordinates are normalized (0–1).
- Each image has a corresponding `.txt` file with the same filename.
- Class IDs correspond to the bucket mapping used for YOLO training.

## Dataset Classes (17 Classes Currently)

This dataset currently contains the following insect pest classes:

1. **alfalfa_weevil** — Alfalfa Weevil  
2. **aphids** — Aphids  
3. **army_worm** — Army Worm  
4. **black_cutworm** — Black Cutworm  
5. **blister_beetle** — Blister Beetle  
6. **corn_borer** — Corn Borer  
7. **flea_beetle** — Flea Beetle  
8. **strawberry_root_weevil** - Strawberry Root Weevil
9. **grub** — Grub (generic larval stage)  
10. **miridae** — Miridae (plant bugs)  
11. **oides_decempunctata** — Oides Decempunctata (Ten-spotted leaf beetle)  
12. **peach_borer** — Peach Borer  
13. **red_spider** — Two Spotted Spider Mite
14. **tarnished_plant_bug** — Tarnished Plant Bug  
15. **thrips** — Thrips  
16. **wireworm** — Wireworm  
17. **four_lined_plant_bug**

Folder names correspond directly to MobileNetV3 class identifiers.

## YOLO Identification Coarse Groups

1.  **tiny_pests** — Aphids, Thrips, Red Spider
2.  **beetles** — Oides Decempunctata (Ten-spotted Leaf Beetle), Flea Beetle, Blister Beetle
3.  **borers** — Peach Borer, Corn Borer
4.  **caterpillars** — Army Worm, Black Cutworm
5.  **plant_bugs** — Miridae (Plant Bugs), Tarnished Plant Bug, Four-Lined Plant Bug
6.  **soil_larvae** — Grub, Wireworm
7.  **weevils** — Alfalfa Weevil, Strawberry Root Weevil

Course groups alongside the species contained within