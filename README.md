# GSenseg

GSenseg is a Napari-based tool for the analysis and segmentation of hyperspectral images and RGB images.

The tool provides functionality to load a batch of images (hyperspectral, multispectral or RGB), perform spectral indexing, segment the images using SAM (Segment Anything Model), binarize the labels if needed, annotate or modify the segmentation masks using Napari's built-in brush, line, point, polygon and eraser tools.

## Functionalities

- **Load batch of Hyperspectral/RGB Images**: Supports various image formats including PNG, JPG, TIF, BMP, RAW, and DAT files.
- **Spectral Indexing**: Allows users to compute pseudo-RGB images using specified channel expressions.
- **Segmentation**: Integrates with SAM (Segment Anything Model) for image segmentation using either default or custom checkpoints.
- **Binarization**: Enables users to binarize mask labels generated from the segmentation.
- **Annotation**: Allows users to modify the mask labels generated from the segmentation using Napari's built-in brush, line, polygon, point, eraser, label picker and other tools.
- **Save Annotations**: Save selected or all generated image and mask layers to local storage.

## Installation

1. Clone the repository and navigate into it:

   ```bash
   git clone https://github.com/GatorSense/GSense.git
   cd GSense
   ```

2. Set Up a Virtual Environment (Recommended)

   Using venv (Python >= 3.9)

   ```bash
   python3 -m venv gsense_env
   source gsense_env/bin/activate   # On Linux/macOS
   gsense_env\Scripts\activate      # On Windows
   ```

   Using Conda

   ```bash
   conda create -n gsense_env python=3.9
   conda activate gsense_env
   ```

3. Install the core dependencies:

   ```bash
   pip install .
   ```

4. Install `torch` based on your system's GPU capability:

   - **For systems without a GPU:**

     ```bash
     pip install torch torchvision torchaudio
     ```

   - **For systems with a CUDA-enabled GPU:**

     Please refer to the [PyTorch website](https://pytorch.org/get-started/locally/) for specific PyTorch and Torchvision installation instructions based on your system.

   Note: Installing PyTorch and torchvision with CUDA support is recommended.

## Usage

### Running the Application

After installation, you can run the application using the following command:

```sh
gsense
```

### Features and Instructions

Loading Images

1. Click on the Load Images button.
2. Select the image files you want to load.
3. For DAT files without corresponding HDR files, select the HDR file when prompted.

Spectral Mixing

1. Enter expressions for the red, green, and blue channels using ch[i] to reference a specific channel.
2. Click the Compute button to generate pseudo-RGB images.

Segmentation

1. Configure the model type (ViT-H or ViT-B) and select the checkpoint.
2. Click Initialize Model to set up the segmentation model.
3. Click Run Segmentation to segment the loaded images.

Binarization

1. Enter the label values to be considered as 1 (e.g., 1-8,14,17,19-21).
2. Click Binarize Labels to generate the binarized mask layer.

Saving Layers

1. Save Selected Layer: Click Save Selected to save the currently selected layer.
2. Save All Layers: Click Save All to save all generated layers.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact

If you have any questions or issues, feel free to open an issue on GitHub or contact us at ma.naikodi@ufl.edu.
