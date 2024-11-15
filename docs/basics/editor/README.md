---
icon: images
description: with Meta AI's Segment Anything Model (SAM)
---

# Image Segmentation

The image segmentation feature employs Meta AI's Segment Anything Model (SAM) to partition images into distinct, meaningful segments. This state-of-the-art Vision Transformer based promptable segmentation algorithm with zero-shot generalization allows for precise isolation of image components.&#x20;

###

### Usage

#### Download custom model checkpoint for root segmentation and move to the 'ckpt' folder (Optional)

GSense supports Vit-h, Vit-b SAM backbones and uses the hugging face transformers library. Downloading model checkpoints for default Vit-h and Vit-b weights is not necessary.

To use a model checkpoint obtained from fine-tuning SAM Vit-b model with [peanut and sweetcorn root images](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MAYDHT), download the custom checkpoint from below link and move it to the 'ckpt' folder.

Download [Custom model checkpoint](https://uflorida-my.sharepoint.com/:u:/g/personal/ma\_naikodi\_ufl\_edu/EQPiLVyRX3JJjba-COypQuYBItpvAA23xR4QWx3ZmqxI6A?e=llgAXU)

Note: Make sure to choose 'Vit-b' model type from the dropdown field in the Model Settings tab when using the downloaded custom model checkpoint.



