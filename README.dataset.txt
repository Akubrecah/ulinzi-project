# aerial-cows-kt2wd-3jxcj-fsod-uvfx > 2025-11-27 7:09pm
https://universe.roboflow.com/akubrecah-entertainment/aerial-cows-kt2wd-3jxcj-fsod-uvfx-h3sx1

Provided by a Roboflow user
License: MIT

# Overview

- [Introduction](#introduction)
- [Object Classes](#object-classes)

# Introduction

This dataset is designed to solve the task of detecting cows in aerial images, aiding in applications such as livestock counting and monitoring. The dataset consists of a single class:

- **Cow**: Represents individual cows as observed from above. 

# Object Classes

## Cow

### Description

Cows in this dataset appear as distinct shapes on open landscapes. From an aerial view, cows may seem small but are recognizable by their characteristic body shape and size, typically larger than other features in the landscape such as rocks or bushes. 

### Instructions

- **Bounding Rules**: Draw a bounding box around each cow visible in the image. Each box should encompass the entire cow's visible body, including any extremities like tails or legs if visible.

- **Object Appearance**: Cows often appear as elongated shapes from above. They are typically situated in open areas and may cast a shadow, which should not be included in the annotation.

- **Occlusion**: If a cow is partially occluded by terrain, include the visible portions in the bounding box as accurately as possible. Do not annotate if less than 20% of the cow is visible.

- **Size Constraints**: Do not label objects smaller than 10 pixels in either dimension to ensure that the object is a cow.

- **Clarity and Identification**: Only annotate if the object clearly resembles a cow. Do not include any objects that might be confused with other elements like rocks or terrain features unless you can clearly distinguish the cow-like form.

While annotating, ensure each cow is bounded separately, avoiding overlaps in annotation with other cows or labels.