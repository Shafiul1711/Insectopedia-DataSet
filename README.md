# GrowLiv-Dataset

## Overview

**GrowLiv-Dataset** contains annotated insect pest images used to train and evaluate the GrowLiv multi-stage insect detection and classification pipeline.

The dataset focuses on agricultural pest species relevant to Ontario crop systems and was curated to support real-world pest identification from field images.

Images were collected from publicly available sources and manually curated to improve dataset diversity and model robustness.

---

## Repository Structure

```
GrowLiv-Dataset/
│
├── classification/
│   ├── images/
│   └── labels/
│
├── YOLO/
│   ├── train/
│   └── valid/
│
├── test_suite/
│   ├── images/
│   └── labels/
│
├── Models/
│
├── PIPELINE_TOOLS/
│
└── README.md
```

### classification
Species-level dataset used to train MobileNet / ResNet classifiers.

### YOLO
Dataset used to train the YOLO insect detection model.

### test_suite
Held-out dataset used for end-to-end pipeline evaluation.

### Models
Saved weights for trained YOLO and classification models.

### PIPELINE_TOOLS
Scripts used for dataset preparation and pipeline evaluation.

---

## Annotation Format

Annotations follow **YOLO format**:

```
<class_id> <x_center> <y_center> <width> <height>
```

- Coordinates are normalized between **0 and 1**
- Each image has a corresponding `.txt` annotation file
- Class IDs correspond to the mapping defined below

---

## YOLO Detection Buckets

The detection model first predicts **coarse insect groups**, which are then routed to species classifiers.

```
0: tiny_pests
   - aphids
   - thrips
   - spider_mite

1: flea_beetle
   - flea_beetle
   - grape_flea_beetle
   - striped_flea_beetle

2: caterpillars
   - army_worm
   - black_cutworm
   - corn_borer

3: plant_bugs
   - miridae
   - tarnished_plant_bug
   - four_lined_plant_bug

4: soil_larvae
   - grub
   - wireworm

5: weevils
   - alfalfa_weevil
   - strawberry_root_weevil

6: stink_bugs
   - green_stink_bug
   - brown_marmorated_stink_bug

7: blister_beetle
   - blister_beetle
   - black_blister_beetle
   - striped_blister_beetle

8: potato_beetle
   - colorado_potato_beetle
   - striped_cucumber_beetle
```

---

## Species Classes

The dataset currently contains **25 insect species classes**:

```
0:  alfalfa_weevil
1:  aphids
2:  army_worm
3:  black_cutworm
4:  blister_beetle           (YOLO detection only)
5:  corn_borer
6:  flea_beetle              (YOLO detection only)
7:  strawberry_root_weevil
8:  grub
9:  miridae                  (YOLO detection only)
10: oides_decempunctata      (YOLO detection only)
12: spider_mite
13: tarnished_plant_bug
14: thrips
15: wireworm
16: four_lined_plant_bug
17: grape_flea_beetle
18: black_blister_beetle
19: brown_marmorated_stink_bug
20: colorado_potato_beetle
21: green_stink_bug
22: striped_blister_beetle
23: striped_flea_beetle
24: striped_cucumber_beetle
```

Some species are used **only for detection** and are excluded from the classification stage.

---

## Dataset Sources

Images were curated from publicly available sources including:

- **iNaturalist**  
  https://www.inaturalist.org/

- **IP102 Dataset**  
  Wu, X., Zhan, C., Lai, Y., Cheng, M., & Yang, J. (2019).  
  *IP102: A Large-Scale Benchmark Dataset for Insect Pest Recognition.*  
  CVPR.

Images were manually reviewed and curated to remove unsuitable observations and improve dataset quality.

---

## Dataset Statistics

Approximate dataset scale:

- **10,000+ curated images**
- **4,800+ manually annotated bounding boxes**
- **12,000+ classification crops generated via segmentation**
- **1,524-image held-out evaluation test suite**

---

## Purpose

This dataset supports the **GrowLiv insect identification pipeline**, which combines multiple computer vision stages:

```
Image
 ↓
YOLO Object Detection
 ↓
SAM Segmentation
 ↓
Species Classification
```

The goal is accurate identification of agricultural pest species from real-world crop images.

---

## License and Usage

Images originate from public datasets and observation platforms.  
Users should respect the licensing terms of the original data sources.

Dataset curated and annotated as part of the GrowLiv capstone project at the University of Windsor (2026).
