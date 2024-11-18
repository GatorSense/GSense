# Load images

## Hyperspectral (remote sensing) images

#### ENVI format

* [ ] Click the `Load Images` button in the main interface.
* [ ] Load a batch of hyperspectral images by selecting multiple `.raw` or `.dat` files.
  1. If the selected files have corresponding `.hdr` files with the same names as those of the files
     1. Images are loaded into the application successfully.
  2. If the selected files have a single common `.hdr` file
     1. A file dialog will prompt to select the `.hdr` file.
        1. Choose the `.hdr` file that should be applied to all selected `.raw`/`.dat` files.
        2. Images are then loaded successfully.
* [ ] Navigate through the loaded batch of images using the `Previous Image` and `Next Image` buttons.
* [ ] The loaded images are stored and an image is accessible using the`Image data` button.

#### TIF/TIFF format

* [ ] Click the `Load Images` button in the main interface.
* [ ] Load a batch of hyperspectral images in TIF/TIFF format by selecting multiple files from the file dialog.
* [ ] Images are loaded successfully. Navigate through the loaded batch of images using the `Previous Image` and `Next Image` buttons.

## RGB Images

* [ ] Click the `Load Images` button in the main interface.
* [ ] Select one or multiple image files from your system of format types: `.png`, `.jpg` or `.bmp`
* [ ] Navigate through the loaded batch of images using the `Previous Image` and `Next Image` buttons.

Images are loaded without the horizontal sliding scroll bar that appears with hyperspectral images to view different channels.&#x20;

{% hint style="info" %}
GSense is primarily developed for hyperspectral images but all the features work with RGB images. In order to perform segmentation on the loaded images, pseudo-RGB images must be generated however, even if the loaded images are 3 channel images. \
\
Enter expressions in the Spectral Indexing tool and compute pseudo-RGB image to be able to run segmentation on loaded RGB images:

Red channel: ch\[0]

Green channel: ch\[2]

Blue channel: ch\[1]
{% endhint %}
