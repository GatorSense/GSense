---
description: >-
  Using model checkpoints obtained from fine-tuning Segment Anything Model
  pretrained models on custom dataset.
---

# Custom models

If you have your own SAM fine-tuned model checkpoint file (.pth) or would like to use one obtained from fine-tuning SAM's vit-b model with root images, follow these steps:

1.  **Select Model Type**:

    * In the **Model Settings** tab, select the model type (`vit-h` or `vit-b`) matching the model architecture of your custom checkpoint.

    <figure><img src="../../.gitbook/assets/image (2) (1).png" alt="" width="364"><figcaption></figcaption></figure>
2. **Load the Custom Checkpoint**:
   * Click on the `Load Custom Checkpoint` button.
   * A file dialog will appear; browse and select your checkpoint file (`.pth` format).

{% hint style="info" %}
To use a model checkpoint obtained from fine-tuning SAM Vit-b model with [peanut and sweetcorn root images](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MAYDHT), download the [custom checkpoint](https://uflorida-my.sharepoint.com/:u:/r/personal/ma\_naikodi\_ufl\_edu/Documents/GSense\_shared/GSense\_custom\_ckpt/roots\_10ep\_patches\_gray\_nointerpol\_model\_checkpoint.pth?csf=1\&web=1\&e=20TWb3) and move it to the 'ckpt' folder.

Make sure to choose '**Vit-b**' model type with this custom model checkpoint.

Load the custom model checkpoint by clicking on the `Load Custom Checkpoint` button.
{% endhint %}

3. **Initialize the Model**:

* After loading the checkpoint, click the `Initialize Model` button.
* A message box will confirm if the model initialization is successful.

***



Once the model is initialized, you can now run segmentation:

**Prerequisites:**

* Ensure you have [loaded images](../image-loading-and-managing/) (either RGB or hyperspectral).&#x20;
* Ensure you have generated pseudo-RGB images using the [markdown.md](../markdown.md "mention")tab.

1.  Run Segmentation:

    * Click the `Run Segmentation` button.

    All generated pseudo-RGB images of all loaded images will be processed. The segmentation may take some time, depending on the number of images and model complexity.
2.  View Results:

    Once segmentation is complete, the segmented masks will appear as additional layers in the viewer.

    * Each pseudo-RGB image will have its mask as a new layer. Select the `Pseudo-RGB x-x` button of choice to view its mask.
    * You can toggle the visibility of the layers using the **Layer List** dock (enable from the **Layers** button).

{% hint style="info" %}
Using custom model comes with the option to use a threshold slider to control the generated mask. Tick the 'Threshold' checkbox to make the slider visible.
{% endhint %}



Video demo link to segment images with SAM ViT-b model checkpoint obtained from fine tuning with root images:

{% embed url="https://youtu.be/2B-SyXIpiHQ" %}

