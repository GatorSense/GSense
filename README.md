# GSense ([Documentation](https://gatorsense-uf.gitbook.io/gsense_how_to_guide))

GSense is a GUI-based tool for the analysis and annotation of hyperspectral images and RGB images leveraging [Napari](https://napari.org/) and [Segment Anything Model (SAM)](https://github.com/facebookresearch/segment-anything).

The tool provides functionality to load a batch of images (hyperspectral, multispectral or RGB), perform spectral indexing, segment the images using SAM (Segment Anything Model), binarize the labels if needed, annotate or modify the segmentation masks using Napari's built-in brush, line, point, polygon and eraser tools, and export annotations in TIF format.

## Functionalities

- **Load batch of Hyperspectral/RGB Images**: Supports various image formats including PNG, JPG, TIF, BMP, RAW, and DAT files.
- **Spectral Indexing**: Allows users to compute pseudo-RGB images using specified channel expressions.
- **Segmentation**: Integrates with SAM (Segment Anything Model) for image segmentation using either default or custom checkpoints.
- **Binarization**: Enables users to binarize mask labels generated from the segmentation.
- **Annotation**: Allows users to modify the mask labels generated from the segmentation using Napari's built-in brush, line, polygon, point, eraser, label picker and other tools.
- **Save Annotations**: Save selected or all generated image and mask layers to local storage.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/GatorSense/GSense.git
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

3. Navigate into the GSense directory and install the core dependencies:

   ```bash
   cd GSense
   pip install -e .
   ```

4. Install `torch` based on your system's GPU capability:

   - **For systems without a GPU:**

     ```bash
     pip install torch torchvision torchaudio
     ```

   - **For systems with a CUDA-enabled GPU:**

     Please refer to the [PyTorch website](https://pytorch.org/get-started/locally/) for specific PyTorch and Torchvision installation instructions based on your system.

   Note: Installing PyTorch and torchvision with CUDA support is recommended.

## Running the Application

After installation, you can run the application using the following command:

```bash
gsense
```

or

```bash
python -m app.main
```


### Features and Instructions

For a detailed how-to guide, refer to the [documentation](https://gatorsense-uf.gitbook.io/gsense_how_to_guide)

Loading Images

1. Click on the Load Images button.
2. Select the image files you want to load.
3. For DAT files without corresponding HDR files of the same filename, select the HDR file when prompted.

Spectral Mixing

1. Enter expressions for the red, green, and blue channels using ch[i] to reference a specific channel.
2. Click the Compute button to generate pseudo-RGB images.

Segmentation

1. Configure the model type (ViT-huge or ViT-base) and select the checkpoint.
2. Click Initialize Model to set up the segmentation model.
3. Click Run Segmentation to segment the loaded images.

GSense supports ViT-huge and ViT-base SAM backbones and uses the hugging face transformers library. Downloading model checkpoints for default Vit-h and Vit-b weights is not necessary.

To use a model checkpoint obtained from fine-tuning SAM Vit-b model with [peanut and sweetcorn root images](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MAYDHT), download the custom checkpoint from below link and move it to the 'ckpt' folder.

Download [Custom model checkpoint](https://uflorida-my.sharepoint.com/:u:/g/personal/ma_naikodi_ufl_edu/EQPiLVyRX3JJjba-COypQuYBItpvAA23xR4QWx3ZmqxI6A?e=llgAXU)

Note: Make sure to choose 'ViT-base' model type from the dropdown field in the Model Settings tab when using the downloaded custom model checkpoint.

Binarization

1. Enter the label values to be considered as 1 (e.g., 1-8,14,17,19-21).
2. Click Binarize Labels to generate the binarized mask layer.

Saving Layers

1. Save Selected Layer: Click Save Selected to save the currently selected layer of selected pseudo RGB image.
2. Save All Layers: Click Save All to save all layers of selected pseudo RGB image.

## License

This project is licensed under the GNU GPL 3.0 License. See the LICENSE file for more details.

## Contact

If you have any questions or issues, feel free to open an issue on GitHub or contact us at ma.naikodi@ufl.edu.

## References

Sofroniew, N., Lambert, T., Bokota, G., Nunez-Iglesias, J., Sobolewski, P., Sweet, A., Gaifas, L., Evans, K., Burt, A., Doncila Pop, D., Yamauchi, K., Weber Mendonça, M., Buckley, G., Vierdag, W., Royer, L., Can Solak, A., Harrington, K. I. S., Ahlers, J., Althviz Moré, D., Amsalem, O., Anderson, A., Annex, A., Boone, P., Bragantini, J., Bussonnier, M., Caporal, C., Eglinger, J., Eisenbarth, A., Freeman, J., Gohlke, C., Gunalan, K., Har-Gil, H., Harfouche, M., Hilsenstein, V., Hutchings, K., Lauer, J., Lichtner, G., Liu, Z., Liu, L., Lowe, A., Marconato, L., Martin, S., McGovern, A., Migas, L., Miller, N., Muñoz, H., Müller, J., Nauroth-Kreß, C., Palecek, D., Pape, C., Perlman, E., Pevey, K., Peña-Castellanos, G., Pierré, A., Pinto, D., Rodríguez-Guerra, J., Ross, D., Russell, C. T., Ryan, J., Selzer, G., Smith, M., Smith, P., Sofiiuk, K., Soltwedel, J., Stansby, D., Vanaret, J., Wadhwa, P., Weigert, M., Windhager, J., Winston, P., & Zhao, R. napari: a multi-dimensional image viewer for Python [Computer software]. https://github.com/napari/napari

Kirillov, A., Mintun, E., Ravi, N., Mao, H., Rolland, C., Gustafson, L., ... & Girshick, R. (2023). Segment anything. In Proceedings of the IEEE/CVF International Conference on Computer Vision (pp. 4015-4026).

Chang, S. J., Chowdhry, R., Song, Y., Mejia, T., Hampton, A., Kucharski, S., ... & Zare, A. (2024). HyperPRI: a dataset of hyperspectral images for underground plant root study. Computers and Electronics in Agriculture, 225, 109307.
