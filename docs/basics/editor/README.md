---
icon: images
description: with Meta AI's Segment Anything Model (SAM)
---

# Image Segmentation

The image segmentation feature integrates Meta AI's Segment Anything Model (SAM) to partition image pixels into distinct, meaningful segments. This state-of-the-art Vision Transformer based promptable segmentation algorithm with zero-shot generalization allows for precise isolation of image components.

{% hint style="info" %}
GSense supports Vit-h, Vit-b SAM backbones and uses the hugging face transformers library. Downloading model checkpoints for default Vit-h and Vit-b weights is not required.
{% endhint %}

<figure><img src="../../.gitbook/assets/image (4).png" alt="" width="360"><figcaption></figcaption></figure>

### Usage

#### **Prepare the Model for Segmentation**

Segmentation in GSense requires initializing a segmentation model. You can choose between a **default checkpoint** or a **custom checkpoint**.







#### **Run Image Segmentation**

