# Insectopedia Dataset

## Overview

**Insectopedia Dataset** contains annotated insect pest images used to train and evaluate the Insectopedia computer vision system for agricultural pest identification.

The dataset focuses on agricultural pest species relevant to Ontario crop systems and was curated to support real-world pest identification from field images.

Images were collected from publicly available sources and manually curated to improve dataset diversity and model robustness.

This repository contains the dataset structure, documentation, and benchmark results used in the development of the Insectopedia system.

---

## Benchmark Overview

The following figure summarizes a benchmark comparing the Insectopedia system against several general-purpose multimodal AI models on a held-out evaluation dataset.

<<<<<<< HEAD
![Insectopedia Benchmark](benchmarks/insectopedia_benchmark.jpg)
=======
![Insectopedia Benchmark](benchmark/insectopedia_benchmark.png)
>>>>>>> e446a32f (Adjusted infographic)

## Repository Structure

```
Insectopedia-Dataset/
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
├── benchmark/
│
└── README.md
```

### classification
Species-level dataset used to train classification models (MobileNet / ResNet).

### YOLO
Dataset used to train the insect detection model.

### test_suite
Held-out dataset used for end-to-end evaluation of the Insectopedia pipeline.

### benchmark
Evaluation results and visual summaries of system performance.

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

The detection model first predicts **coarse insect groups**, which are then routed to species-level classifiers.

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

The dataset currently contains **24 insect species classes**.

```
0:  alfalfa_weevil
1:  aphids
2:  army_worm
3:  black_cutworm
4:  blister_beetle
5:  corn_borer
6:  flea_beetle
7:  strawberry_root_weevil
8:  grub
9:  miridae
10: oides_decempunctata
11: spider_mite
12: tarnished_plant_bug
13: thrips
14: wireworm
15: four_lined_plant_bug
16: grape_flea_beetle
17: black_blister_beetle
18: brown_marmorated_stink_bug
19: colorado_potato_beetle
20: green_stink_bug
21: striped_blister_beetle
22: striped_flea_beetle
23: striped_cucumber_beetle
```

Some species are used **only during detection** and are excluded from the classification stage.

---

## Dataset Sources

Images were curated from publicly available sources including:

**iNaturalist**  
https://www.inaturalist.org/

**IP102 Dataset**  
Wu, X., Zhan, C., Lai, Y., Cheng, M., & Yang, J. (2019).  
*IP102: A Large-Scale Benchmark Dataset for Insect Pest Recognition.*  
CVPR.

Images were manually reviewed and curated to remove unsuitable observations and improve dataset quality.

---

## Dataset Statistics

Approximate dataset scale:

- **10,000+ curated images**
- **5,000+ manually annotated bounding boxes**
- **12,000+ classification crops generated via segmentation**
- **1,524-image held-out evaluation test suite**

---

## Insectopedia System Overview

The dataset supports the **Insectopedia computer vision pipeline**, which performs species identification using a multi-stage architecture:

```
Image
 ↓
YOLO Object Detection
 ↓
Segmentation
 ↓
Species Classification
```

The goal is accurate identification of agricultural pest species from real-world crop images.

Core training pipeline and application components are maintained in **private repositories** while the system is under active development.

---

## License and Usage

Images originate from public datasets and observation platforms.  
Users should respect the licensing terms of the original data sources.

Dataset curated and annotated as part of a computer vision capstone project at the University of Windsor (2026).

## Related Components

The Insectopedia project consists of several components developed as part of an applied computer vision system for agricultural pest identification.

**Insectopedia Dataset (this repository)**  
Annotated insect image dataset used for model training and evaluation.

**Insectopedia Pipeline**  
Machine learning training and inference pipeline used to train detection and classification models.

**Insectopedia App**  
Mobile application integrating the trained ML models with a Flutter interface, a SQL-backed data layer for pest metadata and logging, and a human-in-the-loop correction workflow.

Some components are maintained in separate repositories while the system is under active development.
