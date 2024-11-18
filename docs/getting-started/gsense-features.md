---
description: >-
  GSense provides 3 main functionalities for the analysis and annotation of
  hyperspectral images - spectral indexing, image segmentation, and label
  binarization.
---

# GSense Features

<figure><img src="../.gitbook/assets/image (5) (1).png" alt=""><figcaption></figcaption></figure>



<details>

<summary><a data-mention href="../basics/markdown.md">markdown.md</a></summary>

Lets you compute pseudo-RGB images from spectral bands by referencing them in mathematical expressions using channel indices.

Example of acceptable expressions:

```
Red: ch[10] + ch[20]/4 + 3/ch[2]
Green: ch[50]
Blue: ch[2] - ch[6]
```

Note: If an image in the loaded batch does not have the referenced channel data, pseudo-RGB image computation for that image is skipped.

<img src="../.gitbook/assets/spectral indexing.png" alt="" data-size="original">

</details>

<details>

<summary><a data-mention href="../basics/editor/">editor</a></summary>

Segment generated pseudo-RGB images using Meta AI's Segment Anything Model. Choose your model type and default or custom fine-tuned checkpoint to run segmentation with.

![](<../.gitbook/assets/image (2).png>)

</details>

<details>

<summary><a data-mention href="../basics/binarizer.md">binarizer.md</a></summary>

We use SAM to generates all masks and the label binarizer helps reduce the labels to binary instead.

![](<../.gitbook/assets/image (5).png>)

</details>

