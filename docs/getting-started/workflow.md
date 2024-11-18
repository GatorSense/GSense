# Workflow

Using GSense involves following a workflow that utilizes its various functions.&#x20;

{% stepper %}
{% step %}
### [image-loading-and-managing](../basics/image-loading-and-managing/ "mention")

Load a batch of RGB or hyperspectral images.
{% endstep %}

{% step %}
### [markdown.md](../basics/markdown.md "mention")

Compute pseudo-RGB for hyperspectral data.

{% embed url="https://youtu.be/paEhtIxgODE" %}
{% endstep %}

{% step %}
### [editor](../basics/editor/ "mention")

Segment images using Segment Anything Model (SAM) to get all masks.

1. Initialize the segmentation model (default or custom).
2. Run segmentation.

{% embed url="https://youtu.be/uBdL8lptTIM" %}

{% embed url="https://youtu.be/2B-SyXIpiHQ" %}
{% endstep %}

{% step %}
### [annotation.md](../basics/annotation.md "mention") (optional)

Refine masks using Napari's editing tools.
{% endstep %}

{% step %}
### [binarizer.md](../basics/binarizer.md "mention") (optional)

Binarize labels
{% endstep %}

{% step %}
### [export.md](../basics/export.md "mention")

Save masks and computed pseudo-RGB images



**Watch the below video for a complete workflow:**

* Loading 2 hyperspectral images of TIFF file format, 1 jpg RGB image
* Run Segmentation with ViT-h default model
* Binarize generated masks
* Export selected/all layers

{% embed url="https://youtu.be/ocnVNgcP190" %}


{% endstep %}
{% endstepper %}
