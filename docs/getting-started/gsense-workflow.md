# GSense Workflow

#### Using GSense involves following a workflow that utilizes its various functions.&#x20;

{% stepper %}
{% step %}
### [import](../basics/import/ "mention")

Load a batch of RGB or hyperspectral images.
{% endstep %}

{% step %}
### [markdown.md](../basics/markdown.md "mention")

Compute pseudo-RGB for hyperspectral data.
{% endstep %}

{% step %}
### [editor](../basics/editor/ "mention")

Segment images using Segment Anything Model (SAM) to get all masks.

1. Initialize the segmentation model (default or custom).
2. Run segmentation.
{% endstep %}

{% step %}
### [annotation](../basics/annotation/ "mention") (optional)

Refine masks using Napari's editing tools.
{% endstep %}

{% step %}
### [binarizer.md](../basics/binarizer.md "mention") (optional)

Binarize labels
{% endstep %}

{% step %}
### [export.md](../basics/export.md "mention")

Save masks and computed pseudo-RGB images
{% endstep %}
{% endstepper %}
