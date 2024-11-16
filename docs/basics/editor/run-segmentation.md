# Run Segmentation

Once the model is initialized, follow these steps to perform segmentation:

**Prerequisites:**

* Ensure you have [loaded images](../import/) (either RGB or hyperspectral).&#x20;
* Ensure you have generated pseudo-RGB images using the [markdown.md](../markdown.md "mention")tab.

1.  **Run Segmentation**:

    * Click the `Run Segmentation` button.

    All generated pseudo-RGB images of all loaded images will be processed. The segmentation may take some time, depending on the number of images and model complexity.
2.  **View Results**:

    Once segmentation is complete, the segmented masks will appear as additional layers in the viewer.

    * Each pseudo-RGB image will have its mask as a new layer. Select the `Pseudo-RGB x-x` button of choice to view its mask.
    * You can toggle the visibility of the layers using the **Layer List** dock (enable from the **Layers** button).
