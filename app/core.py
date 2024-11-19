import napari
import numpy as np
import torch
from torch.nn.functional import interpolate
from tkinter import filedialog
from typing import Tuple
from PIL import Image
import os
import imageio
import warnings
from qtpy.QtWidgets import QMessageBox
from app.logging import logger
import re

warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data.dataloader")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def validate_expression(expr):
    ''' Validate the input expression for pseudo-RGB computation '''
    # Allow numbers, ch[i] syntax, and basic operators (+, -, *, /)
    pattern = r"^(ch\[\d+\]|\d+)(\s*[\+\-\*/]\s*(ch\[\d+\]|\d+))*$"
    return re.match(pattern, expr.strip()) is not None


def normalize_channel(channel):
    channel_min = np.min(channel)
    channel_max = np.max(channel)
    if channel_max > channel_min:
        normalized_channel = (channel - channel_min) / (channel_max - channel_min) * 255
    else:
        normalized_channel = np.zeros_like(channel)
    return normalized_channel.astype(np.uint8)

def compute_channel(channels, expression):
    for idx, data in channels.items():
        expression = expression.replace(f"ch[{idx}]", f"channels[{idx}]")
    computed_channel = eval(expression)
    return normalize_channel(computed_channel)


def segment_images_with_pipeline(mask_generator, images):
    # convert numpy arrays to PIL Images for mask_generator
    pil_images = [Image.fromarray(image) if isinstance(image, np.ndarray) else image for image in images]
    outputs = mask_generator(pil_images, points_per_batch=1, batch_size=1, num_workers=0)
    segmented_masks = [output['masks'] for output in outputs]
  
    return segmented_masks


# Function to build all layer point grids
def build_all_layer_point_grids(grid_size, min_value, max_value):
    points = []
    step = (max_value - min_value) / (grid_size - 1)
    for i in range(grid_size):
        for j in range(grid_size):
            points.append([min_value + step * i, min_value + step * j])
    return np.array(points)

def get_input_points(images, grid_size = 32, img_resolution = 1024, point_batch_size = 1):
    batch_size = len(images)
    input_points = torch.as_tensor(build_all_layer_point_grids(grid_size, 0, 1) * img_resolution, dtype=torch.int64).to(device)
    input_points = input_points.unsqueeze(0).unsqueeze(0)
    input_points = input_points.repeat(batch_size, point_batch_size, 1, 1)
    return input_points

def postprocess_masks(masks: torch.Tensor, input_size: Tuple[int, ...], original_size: Tuple[int, ...], image_size=1024) -> torch.Tensor:
    masks = interpolate(
        masks,
        (image_size, image_size),
        mode="bilinear",
        align_corners=False,
    )
    masks = masks[..., : input_size[0], : input_size[1]]
    masks = interpolate(masks, original_size, mode="bilinear", align_corners=False)
    return masks


def segment_images_with_custom_model(model, processor, images):
    # batch_size = len(images)
    input_points = get_input_points(images)
    inputs = processor(images=images, input_points = input_points.cpu(), return_tensors="pt").to(device)

    model.eval()
    with torch.no_grad():
        outputs = model(**inputs, multimask_output=False)
    
    low_res_masks = outputs.pred_masks.cpu()    
    # To return for thresholding
    upscaled_masks = postprocess_masks(low_res_masks.squeeze(1).cpu(),inputs["reshaped_input_sizes"][0].tolist(), inputs["original_sizes"][0].tolist()).to(device)

    # Post-process masks
    masks = processor.image_processor.post_process_masks(
        low_res_masks, inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu()
    )
    
    return masks, upscaled_masks


# Save selected layer function
def save_selected_layer(viewer):
    logger.info("Saving selected layer in viewer.")  
    selected_layers = viewer.layers.selection
    if not selected_layers:
        QMessageBox.warning(None, "Error", "No layer selected.")
        return
    for layer in selected_layers:
        data = layer.data
        if isinstance(layer, napari.layers.Labels):
            # Scale labels to 0-255
            max_val = data.max()
            if max_val > 0:  # Avoid division by zero
                data = (data.astype(np.float32) / max_val * 255).astype(np.uint8)
                file_path = filedialog.asksaveasfilename(defaultextension=".tif", filetypes=[("TIFF files", "*.tif")])
                if not file_path:
                    continue
                imageio.imwrite(file_path, data)
                # print("Saving labels")
            else:
                QMessageBox.warning(None, "Error", "Label layer has no valid labels.")
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".tif", filetypes=[("TIFF files", "*.tif")])
            if not file_path:
                continue
            # print("Saving image")
            imageio.imwrite(file_path, data)
        print(f"Layer {layer.name} saved to {file_path}")
        logger.info(f"Layer {layer.name} saved as'{os.path.basename(file_path)}'")  # Log only the filename

# Save all layers function
def save_all_layers(viewer):
    logger.info("Saving all layers in viewer.")  
    for layer in viewer.layers:
        data = layer.data
        file_path = f"exports/{layer.name}.tif"
        if isinstance(layer, napari.layers.Labels):
            # Scale labels to 0-255
            max_val = data.max()
            if max_val > 0:  # Avoid division by zero
                data = (data.astype(np.float32) / max_val * 255).astype(np.uint8)
                imageio.imwrite(file_path, data)
                print("Saving labels")
            else:
                print(f"Label layer {layer.name} has no valid labels.")
        else:
            print("Saving image")
            imageio.imwrite(file_path, data)
        print(f"Layer {layer.name} saved to '{file_path}'")
        logger.info(f"Layer {layer.name} saved in \exports as '{os.path.basename(file_path)}'")
