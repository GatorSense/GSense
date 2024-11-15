---
icon: images
description: with Meta AI's Segment Anything Model (SAM)
---

# Image Segmentation

The image segmentation feature integrates Meta AI's Segment Anything Model (SAM) to partition image pixels into distinct, meaningful segments. This state-of-the-art Vision Transformer based promptable segmentation algorithm with zero-shot generalization allows for precise isolation of image components.

{% hint style="info" %}
GSense supports Vit-h, Vit-b SAM backbones and uses the hugging face transformers library. Downloading model checkpoints for default Vit-h and Vit-b weights is not required.
{% endhint %}



<figure><img src="../../.gitbook/assets/image (1).png" alt="" width="360"><figcaption></figcaption></figure>

###

#### Default model checkpoint

####







#### Custom model checkpoint

Download custom model checkpoint for root segmentation and move to the 'ckpt' folder (Optional)

To use a model checkpoint obtained from fine-tuning SAM Vit-b model with [peanut and sweetcorn root images](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MAYDHT), download the custom checkpoint from below link and move it to the 'ckpt' folder.

Download [Custom model checkpoint](https://uflorida-my.sharepoint.com/:u:/g/personal/ma\_naikodi\_ufl\_edu/EQPiLVyRX3JJjba-COypQuYBItpvAA23xR4QWx3ZmqxI6A?e=llgAXU)

Note: Make sure to choose 'Vit-b' model type from the dropdown field in the Model Settings tab when using the downloaded custom model checkpoint.



### Usage

#### **Prepare the Model for Segmentation**

Segmentation in GSense requires initializing a segmentation model. You can choose between a **default checkpoint** or a **custom checkpoint**.



**Option 1: Using Default Model Checkpoints**

1. Select Model Type
   * In the **Model Settings** tab, choose the model type from the dropdown menu. Available options include:
     * `vit-h` (Vision Transformer - Huge)
     * `vit-b` (Vision Transformer - Base)
2. Select Checkpoint
   * Select the `default` option in the **Checkpoint** dropdown.
3.  Initialize the Model

    * Click on the `Initialize Model` button.
    * A message box will confirm if the model initialization is successful.

    Note: Initializing takes a longer time the first time.

***

**Option 2: Using Custom Model Checkpoints**

If you have your own model checkpoint file, follow these steps:

1. **Select Model Type**:
   * In the **Model Settings** tab, select the model type (`vit-h` or `vit-b`) matching the model architecture of your custom checkpoint.
2. **Load the Custom Checkpoint**:
   * Click on the `Load Custom Checkpoint` button.
   * A file dialog will appear; browse and select your checkpoint file (`.pth` format).
3. **Initialize the Model**:
   * After loading the checkpoint, click the `Initialize Model` button.
   * A message box will confirm if the model initialization is successful.

***

#### **Run Image Segmentation**

Once the model is initialized, follow these steps to perform segmentation:

**Prerequisites:**

* Ensure you have already loaded images (either RGB or hyperspectral). Refer to the [import](../import/ "mention")section for instructions.
* Ensure you have generated pseudo-RGB images using the [markdown.md](../markdown.md "mention")tab.

1. **Run Segmentation**:
   * Click the `Run Segmentation` button.
   * GSense will process all generated pseudo-RGB images of all loaded images.
   * The segmentation may take some time, depending on the number of images and model complexity.
2. **View Results**:
   * Once segmentation is complete, the segmented masks will appear as additional layers in the viewer.
   * Each pseudo-RGB image will have its mask as a new layer. Select the `Pseudo-RGB image x-x` button of choice to view its mask.
   * You can toggle the visibility of the layers using the **Layer List** dock (enable from the **Layers** button).

***

#### 3. .

***

#### 4. **Handle Errors**

If you encounter issues during segmentation:

* **Error during model initialization**:
  * Double-check the selected model type and checkpoint file.
  * Ensure the checkpoint file matches the model architecture.
* **Segmentation failed**:
  * Verify that valid images are loaded.
  * Ensure the model is initialized before running segmentation.

If errors persist, consult the **Troubleshooting** section.

***

####

***

#### Screenshots to Include:

1. **Model Settings Tab**:
   * Show dropdowns for selecting model type and checkpoint.
   * Highlight the "Initialize Model" button.
2. **Segmentation Process**:
   * Example of segmentation running in the Napari viewer.
   * Screenshot of segmented masks overlaid on an image.
3. **Error Message**:
   * Example of a model initialization or segmentation error and how to resolve it.



