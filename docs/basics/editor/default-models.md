---
description: Using default model checkpoints with ViT-huge and ViT-base backbones
---

# Default models

1. Select Model Type
   *   In the **Model Settings** tab, choose the model type from the dropdown menu. Available options include:

       * `vit-h` (Vision Transformer - huge)
       * `vit-b` (Vision Transformer - base)

       <figure><img src="../../.gitbook/assets/image (6).png" alt="" width="364"><figcaption></figcaption></figure>
2. Select Checkpoint
   * Select the `default` option in the **Checkpoint** dropdown.
3.  Initialize the Model

    * Click on the `Initialize Model` button.
    * A message box will confirm if the model initialization is successful.

    Note: Initializing takes a longer time the first time.

<figure><img src="../../.gitbook/assets/image (1) (1) (1).png" alt=""><figcaption></figcaption></figure>

***



Once the model is initialized, you can now run segmentation:

**Prerequisites:**

* Ensure you have [loaded images](../image-loading-and-managing/) (either RGB or hyperspectral).&#x20;
* Ensure you have generated pseudo-RGB images using the [markdown.md](../markdown.md "mention")tab.

1.  **Run Segmentation**:

    * Click the `Run Segmentation` button.

    All generated pseudo-RGB images of all loaded images will be processed. The segmentation may take some time, depending on the number of images and model complexity.
2.  **View Results**:

    Once segmentation is complete, the segmented masks will appear as additional layers in the viewer.

    * Each pseudo-RGB image will have its mask as a new layer. Select the `Pseudo-RGB x-x` button of choice to view its mask.
    * You can toggle the visibility of the layers using the **Layer List** dock (enable from the **Layers** button).

Video demo link to segment images with default SAM ViT-h and ViT-b models:

{% embed url="https://youtu.be/uBdL8lptTIM" %}

