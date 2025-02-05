import napari
import numpy as np
import torch
from torch.nn.functional import threshold, normalize
from tkinter import filedialog
from skimage import io
from qtpy.QtWidgets import QWidget, QStyle, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QMenu, QCheckBox, QSlider, QTabWidget
from qtpy.QtWidgets import QVBoxLayout, QLineEdit,QPlainTextEdit
from qtpy.QtCore import QThread
from qtpy.QtGui import QFont
from qtpy.QtCore import Qt
from transformers import pipeline, SamModel, SamProcessor
import os
import shutil
import subprocess
from spectral import open_image
from app.worker import Worker
from app.core import validate_expression, compute_channel, segment_images_with_pipeline, segment_images_with_custom_model, save_all_layers, save_selected_layer
from app.core import device
from app.logging import logger



class CustomWidget(QWidget):
    def __init__(self, viewer, layer_list_dock, layer_controls_dock):
        super().__init__()
        self.viewer = viewer
        self.layer_list_dock = layer_list_dock
        self.layer_controls_dock = layer_controls_dock
        
        self.viewer.status = "device: "+str(device)
                
        self.images = []  # List to hold loaded images
        self.file_paths = []  # List to hold file paths of loaded images
        self.current_image_index = 0  # Index of the current image being displayed
        self.current_rgb_idx = 0  # Index of the currently displayed pseudo RGB image
        self.pseudo_rgb_images_per_image = []  # Store pseudo RGB images for each loaded image
        self.masks_per_image = []  # Store segmentation masks for each loaded image
        self.binarized_masks_per_image = []  # Store binarized masks for each loaded image

        self.model = None   # SAM model
        self.processor = None       # SAM processor
        self.pseudo_rgb_buttons = []    # List to hold pseudo-RGB buttons#
        self.mask_generator = None      # SAM pipeline for mask generation
        self.upscaled_masks = None      # Cached low-res masks for thresholding
        self.threshold_checkbox = None  # Checkbox for enabling thresholding
        self.threshold_slider = None    # Slider for thresholding
        self.threshold_value = None     # Threshold value for binarization
        self.upscaled_masks_per_image = []     # Store upscaled masks for each loaded image
            
        layout = QVBoxLayout()        # Main widget layout
        tab_widget = QTabWidget()     # Tab widget for main functionalities - Spectral Indexing, SAM Model Settings, Binarize Labels
        
        
        self.bottom_layout = QHBoxLayout() # Layout for navigation buttons
        
        # Add Load Images button
        self.load_images_btn = QPushButton("Load Images", self)
        self.load_images_btn.clicked.connect(self.load_images)  # Connect the button to the load_images method
        layout.addWidget(self.load_images_btn)
        
        ########## Spectral Mixing Tab ##########
        spectral_mixing_widget = QWidget()
        spectral_layout = QVBoxLayout()
        
        self.r_input = QLineEdit(self)
        self.g_input = QLineEdit(self)
        self.b_input = QLineEdit(self)
        
        # Set tab order between the text fields
        self.setTabOrder(self.r_input, self.g_input)
        self.setTabOrder(self.g_input, self.b_input)
        self.setTabOrder(self.b_input, self.r_input)

        # so user can press enter to compute
        self.r_input.returnPressed.connect(self.compute_image)
        self.g_input.returnPressed.connect(self.compute_image)
        self.b_input.returnPressed.connect(self.compute_image)
    
        spectral_layout.addWidget(QLabel("Red channel expression:"))
        spectral_layout.addWidget(self.r_input)
        spectral_layout.addWidget(QLabel("Green channel expression:"))
        spectral_layout.addWidget(self.g_input)
        spectral_layout.addWidget(QLabel("Blue channel expression:"))
        spectral_layout.addWidget(self.b_input)
        
        note = QLabel("Enter expressions using ch[i] to reference a channel")
        tiny_font = QFont()
        tiny_font.setPointSize(8)
        note.setFont(tiny_font)
        spectral_layout.addWidget(note)
        
        self.compute_button = QPushButton("Compute", self)
        self.compute_button.clicked.connect(self.compute_image)
        spectral_layout.addWidget(self.compute_button)

        spectral_mixing_widget.setLayout(spectral_layout)

        ######### Model Settings Tab #########
        model_settings_widget = QWidget()
        model_layout = QVBoxLayout()
        
        self.model_type_combo = QComboBox(self)
        self.model_type_combo.addItems(["ViT-huge", "ViT-base"])
        model_layout.addWidget(QLabel("Select segmentation model type (ViT):"))
        model_layout.addWidget(self.model_type_combo)
        
        self.checkpoint_combo = QComboBox(self)
        self.checkpoint_combo.addItems(["default"])
        model_layout.addWidget(QLabel("Select Checkpoint:"))
        model_layout.addWidget(self.checkpoint_combo)

        self.load_custom_checkpoint_btn = QPushButton("Load Custom Checkpoint", self)
        self.load_custom_checkpoint_btn.clicked.connect(self.load_custom_checkpoint)
        model_layout.addWidget(self.load_custom_checkpoint_btn)
        
        self.initialize_model_btn = QPushButton("Initialize Model", self)
        self.initialize_model_btn.clicked.connect(self.initialize_model)
        model_layout.addWidget(self.initialize_model_btn)

        model_settings_widget.setLayout(model_layout)
        
        
        ######### Binarizer Tab #########
        binarize_widget = QWidget()
        binarize_layout = QVBoxLayout()
        
        self.label_input = QPlainTextEdit(self)
        self.label_input.setPlaceholderText("Enter label values to assign to 1 (e.g., 1-8, 14, 17, 19-21)")
        binarize_layout.addWidget(self.label_input)

        self.binarize_button = QPushButton("Binarize Labels", self)
        self.binarize_button.clicked.connect(self.binarize_labels)
        binarize_layout.addWidget(self.binarize_button)
        self.binarize_button.setEnabled(False) # Initially disabled
        
        self.binarize_status_label = QLabel(self)  # Label to show the status
        binarize_layout.addWidget(self.binarize_status_label)
        
        binarize_widget.setLayout(binarize_layout)

        # add as tabs
        tab_widget.addTab(spectral_mixing_widget, "Spectral Indexing")
        tab_widget.addTab(model_settings_widget, "Model Settings")
        tab_widget.addTab(binarize_widget, "Binarize Labels")
        

        layout.addWidget(tab_widget, 0, Qt.AlignTop)
        
        
        ######### Segmentation Button #########

        self.segment_button = QPushButton("Run Segmentation", self)
        self.segment_button.clicked.connect(self.run_segmentation)
        self.segment_button.setEnabled(False)
        layout.addWidget(self.segment_button, stretch=0, alignment=Qt.AlignTop)
        
        ######### Image Button #########
        self.hsi_button = QPushButton("Image data", self)
        self.hsi_button.clicked.connect(self.show_image_data)
        self.hsi_button.setEnabled(False)     # Disable until image(s) are loaded
        layout.addWidget(self.hsi_button, stretch=0)
               
        ######### Pseudo-RGB Buttons #########

        self.pseudo_rgb_buttons_layout = QVBoxLayout()
        layout.addLayout(self.pseudo_rgb_buttons_layout)

        ######### Navigation Buttons #########        

        # Add Next and Previous buttons for navigation
        self.previous_button = QPushButton("Previous Image", self)
        self.previous_button.clicked.connect(self.show_previous_image)
        self.previous_button.setEnabled(False)  # Disabled until multiple images are loaded

        self.next_button = QPushButton("Next Image", self)
        self.next_button.clicked.connect(self.show_next_image)
        self.next_button.setEnabled(False)  # Disabled until multiple images are loaded
        
        # # Add buttons to this new layout
        self.bottom_layout.addWidget(self.previous_button, stretch=0)
        self.bottom_layout.addWidget(self.next_button, stretch=0)

        # Add the bottom layout to the main layout
        layout.addLayout(self.bottom_layout)
        
        ######## Save Buttons #########
        
        # Save Buttons with Icons
        save_buttons_layout = QHBoxLayout()

        # Save Selected Layer Button
        self.save_button = QPushButton("Save selected", self)
        save_icon = self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton'))
        self.save_button.setIcon(save_icon)
        self.save_button.setToolTip("Save selected layer from Layers menu")
        self.save_button.clicked.connect(lambda: save_selected_layer(self.viewer))
        self.save_button.setEnabled(False)  
        save_buttons_layout.addWidget(self.save_button, Qt.AlignRight)

        # Save All Layers Button
        self.save_all_button = QPushButton("Save all", self)
        save_all_icon = self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton'))
        self.save_all_button.setIcon(save_all_icon)
        self.save_all_button.setToolTip("Save all layers in selected view")
        self.save_all_button.clicked.connect(lambda: save_all_layers(self.viewer))
        save_buttons_layout.addWidget(self.save_all_button, Qt.AlignRight)
     
        ######### Layer Controls and Layer List Buttons #########
        
        # Adding buttons for toggling the visibility of layer controls and layer list
        self.layer_list_toggle_btn = QPushButton("Layers", self)
        self.layer_list_toggle_btn.clicked.connect(self.toggle_layer_list)
        save_buttons_layout.addWidget(self.layer_list_toggle_btn, Qt.AlignRight)

        self.layer_controls_toggle_btn = QPushButton("Layer Controls", self)
        self.layer_controls_toggle_btn.clicked.connect(self.toggle_layer_controls)
        save_buttons_layout.addWidget(self.layer_controls_toggle_btn, Qt.AlignRight)
        
        layout.addLayout(save_buttons_layout)

        self.setLayout(layout)
       
    #########################

    ## UI-only methods and helper methods
    def toggle_layer_list(self):
        new_state = not self.layer_list_dock.isVisible()
        state_str = "shown" if new_state else "hidden"
        logger.info(f"Layer list visibility toggled. New state: {state_str}")
        self.layer_list_dock.setVisible(new_state)

    def toggle_layer_controls(self):
        new_state = not self.layer_controls_dock.isVisible()
        state_str = "shown" if new_state else "hidden"
        logger.info(f"Layer controls visibility toggled. New state: {state_str}")
        self.layer_controls_dock.setVisible(new_state)
    
    def show_next_image(self):
        logger.info("Next button clicked.")
        # Save the current pseudo RGB images and masks before navigating
        self.save_pseudo_rgbs_and_masks_current()
        # Move to the next image and loop
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        
        #If masks are present, show the pseudo RGB image and mask, else show Image
        if len(self.masks_per_image[self.current_image_index]) > 0:
            self.update_pseudo_rgb_buttons()
            self.show_image_and_mask(self.current_image_index, 0)
            self.update_button_highlight(0) # highlight first pseudo RGB button of current image index
        else:
            self.show_image_data()
            self.update_button_highlight(None) # highlight "Image" button of current image index 

    def show_previous_image(self):
        logger.info("Previous button clicked.")
        # Save the current pseudo-RGB images and masks before navigating
        self.save_pseudo_rgbs_and_masks_current()
        # Move to the previous image and loop
        self.current_image_index = (self.current_image_index - 1) % len(self.images) 
        if len(self.masks_per_image[self.current_image_index]) > 0:
            self.update_pseudo_rgb_buttons()
            self.show_image_and_mask(self.current_image_index, 0)
            self.update_button_highlight(0) # highlight first pseudo RGB button of current image index
        else:
            self.show_image_data()
            self.update_button_highlight(None) # highlight "Image" button of current image index 

            
    def update_button_highlight(self, rgb_idx):
        '''Highlight the button corresponding to the input image and pseudo-RGB index.'''
        # Clear the styles of all pseudo-RGB buttons
        for button in self.pseudo_rgb_buttons:
            button.setStyleSheet("")  # Reset to default style

        # Highlight the Image button if `rgb_idx` is None
        if rgb_idx is None:
            self.hsi_button.setStyleSheet("background-color: darkgray;")  # Highlight style
        else:
            self.hsi_button.setStyleSheet("")  # Reset the style if not displaying the base image

        # Highlight the specific pseudo-RGB button if `rgb_idx` is not None
        if rgb_idx is not None and rgb_idx < len(self.pseudo_rgb_buttons):
            self.pseudo_rgb_buttons[rgb_idx].setStyleSheet("background-color: darkgray;")  # Highlight style
        
        
    def set_spectral_mixing_enabled(self, enabled):
        self.r_input.setEnabled(enabled)
        self.g_input.setEnabled(enabled)
        self.b_input.setEnabled(enabled)
        self.compute_button.setEnabled(enabled)

    def delete_single_pseudo_rgb(self):
        '''Delete a specific pseudo-RGB image for the selected image.'''
        img_idx = self.current_image_index
        rgb_idx = self.current_rgb_idx
                
        if 0 <= img_idx < len(self.pseudo_rgb_images_per_image):
            if 0 <= rgb_idx < len(self.pseudo_rgb_images_per_image[img_idx]):
                del self.pseudo_rgb_images_per_image[img_idx][rgb_idx]
        
        # Remove pseudoRGB idx button
        self.update_pseudo_rgb_buttons()
        self.viewer.layers.clear()
        self.show_image_data()
        logger.info(f"Deleted {img_idx+1}-{rgb_idx+1}.")

    def delete_pseudo_rgb_for_all_images(self, rgb_idx):
        '''Delete a specific pseudo-RGB image for all batch images.'''
        # Remove the pseudo-RGB image for each image in the batch
        for idx, pseudo_rgb_images in enumerate(self.pseudo_rgb_images_per_image):
            if 0 <= rgb_idx < len(pseudo_rgb_images):
                del self.pseudo_rgb_images_per_image[idx][rgb_idx]
        self.update_pseudo_rgb_buttons()
        self.viewer.layers.clear()
        self.show_image_data()
        logger.info(f"Deleted pseudo RGB {rgb_idx+1} for all images.")
        
    def update_pseudo_rgb_buttons(self):
        '''Update the pseudo-RGB buttons for the current image index.'''
        img_idx = self.current_image_index
        # Clear existing buttons
        for button in self.pseudo_rgb_buttons:
            self.pseudo_rgb_buttons_layout.removeWidget(button)
            button.deleteLater()
        self.pseudo_rgb_buttons = []
        # Add buttons only if there are valid pseudo RGB images
        if self.pseudo_rgb_images_per_image[img_idx]:
            for i, _ in enumerate(self.pseudo_rgb_images_per_image[img_idx]):
                self.create_pseudo_rgb_button(img_idx, i)
        else:
            logger.info(f"No pseudo-RGB images to update for image index {img_idx+1}.")
                
    def create_pseudo_rgb_button(self, img_idx, rgb_idx):
        '''Create a pseudo RGB button and add right-click context menu.'''
        button = QPushButton(f"Pseudo-RGB {img_idx + 1}-{rgb_idx + 1}", self)
        button.clicked.connect(lambda: self.show_pseudo_rgb_image(img_idx, rgb_idx))
        
        # Add right-click context menu to the button
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda pos, img_idx=img_idx, rgb_idx=rgb_idx: self.show_context_menu(button, pos, img_idx, rgb_idx))
        
        self.pseudo_rgb_buttons.append(button)
        self.pseudo_rgb_buttons_layout.addWidget(button)
        
    def show_context_menu(self, button, pos, img_idx, rgb_idx):
        '''Create a context menu with delete options for right click on pseudo RGB buttons.'''
        menu = QMenu(self)
        # Option 1: Delete this specific pseudo RGB image for the current image
        delete_single_action = menu.addAction("Delete this pseudo-RGB image")
        delete_single_action.triggered.connect(self.delete_single_pseudo_rgb)

        # Option 2: Delete this pseudo RGB image for all batch images
        delete_all_action = menu.addAction("Delete this pseudo-RGB image for all images")
        delete_all_action.triggered.connect(lambda: self.delete_pseudo_rgb_for_all_images(rgb_idx))

        # Show the context menu
        menu.exec_(button.mapToGlobal(pos))
        
    def show_pseudo_rgb_image(self, img_idx, rgb_idx):
        ''' Display the pseudo-RGB image for the selected image and RGB index.
        Called only when pseudo RGB button is pressed.'''
        logger.info(f"Pseudo RGB button {img_idx+1}-{rgb_idx+1} pressed.")
        pseudo_rgb_image = self.pseudo_rgb_images_per_image[img_idx][rgb_idx]
        self.save_pseudo_rgb_and_masks_current()
        self.save_button.setEnabled(True)
        # Update current rgb index
        self.current_rgb_idx = rgb_idx
        # If masks are present, show the pseudo RGB image and mask, else show pseudo RGB image
        if len(self.masks_per_image[img_idx]) > rgb_idx:
            self.show_image_and_mask(img_idx, rgb_idx)
        else:
            self.viewer.layers.clear()
            self.viewer.add_image(pseudo_rgb_image, rgb=True, name=f"Pseudo RGB Image {img_idx + 1}-{rgb_idx + 1}")
        self.update_button_highlight(rgb_idx)
              

    def save_pseudo_rgbs_and_masks_current(self):
        '''Save mask layers of all pseudo-RGB images of current image idx.'''
        for rgb_idx, _ in enumerate(self.pseudo_rgb_buttons): # rgb_idx is pseudo rgb buttons of current img index only
            pseudo_rgb_layer_name = f"Pseudo-RGB Image {self.current_image_index + 1}-{rgb_idx + 1}"
            mask_layer_name = f"Mask Layer {self.current_image_index + 1}-{rgb_idx + 1}"
            binarized_layer_name = f"Binarized {mask_layer_name}"
            for layer in self.viewer.layers:
                if layer.name == pseudo_rgb_layer_name:
                    self.pseudo_rgb_images_per_image[self.current_image_index][rgb_idx] = layer.data
                elif layer.name == mask_layer_name:
                    self.masks_per_image[self.current_image_index][rgb_idx] = layer.data
                elif layer.name == binarized_layer_name:
                    self.binarized_masks_per_image[self.current_image_index][rgb_idx] = layer.data
                    
    def save_pseudo_rgb_and_masks_current(self):
        '''Save mask layers of current pseudo-RGB img only.'''
        rgb_idx = self.current_rgb_idx
        pseudo_rgb_layer_name = f"Pseudo-RGB Image {self.current_image_index + 1}-{rgb_idx + 1}"
        mask_layer_name = f"Mask Layer {self.current_image_index + 1}-{rgb_idx + 1}"
        binarized_layer_name = f"Binarized {mask_layer_name}"
        for layer in self.viewer.layers:
            if layer.name == pseudo_rgb_layer_name:
                self.pseudo_rgb_images_per_image[self.current_image_index][rgb_idx] = layer.data
            elif layer.name == mask_layer_name:
                self.masks_per_image[self.current_image_index][rgb_idx] = layer.data
            elif layer.name == binarized_layer_name:
                self.binarized_masks_per_image[self.current_image_index][rgb_idx] = layer.data

    def show_image_data(self):
        ''' Display the Image data for the current image index.'''
        image_data = self.images[self.current_image_index]
        self.viewer.layers.clear()
        self.viewer.add_image(image_data, colormap='gray', name="Image")
        # Adjust axes order for hyperspectral images
        if image_data.ndim == 3:  
            self.viewer.dims.order = (2, 0, 1) # Hyperspectral 
        else:
            self.viewer.dims.order = (0, 1, 2) # RGB image
        self.update_pseudo_rgb_buttons()
        self.save_button.setEnabled(False)
        self.set_spectral_mixing_enabled(True)
        self.update_button_highlight(None)
        self.hsi_button.setEnabled(True) 
    
    def show_image_and_mask(self, img_idx, rgb_idx):
        ''' Display the pseudo-RGB image and corresponding masks for the selected image and RGB index '''
        pseudo_rgb_image = self.pseudo_rgb_images_per_image[img_idx][rgb_idx]
        mask_set = self.masks_per_image[img_idx][rgb_idx]
        try:
            self.viewer.layers.clear()
            self.viewer.add_image(pseudo_rgb_image, rgb=True, name=f"Pseudo-RGB Image {img_idx + 1}-{rgb_idx + 1}")
        except Exception as e:
            logger.error(f"Failed to clear layers: {e}")
        
        # Create a combined mask to display
        combined_mask = np.zeros(pseudo_rgb_image.shape[:2], dtype=np.int32)

        if isinstance(mask_set, list) and isinstance(mask_set[0], np.ndarray):
            for j, mask in enumerate(mask_set):
                if torch.is_tensor(mask):
                    mask = mask.cpu().numpy()
                combined_mask[mask > 0] = j + 1
        elif torch.is_tensor(mask_set):
            mask_set = mask_set.cpu().numpy()

            if len(mask_set.shape) == 4:  # If the tensor has a batch dimension
                mask_set = mask_set.squeeze(1)
                
            for j in range(mask_set.shape[0]):
                mask = mask_set[j]
                unique_vals = np.unique(mask)
                val_map = {val: idx for idx, val in enumerate(unique_vals)}
                for val in unique_vals:
                    combined_mask[mask == val] = val_map[val]
        elif isinstance(mask_set, np.ndarray) and mask_set.dtype in [np.uint8, np.int32]:
            combined_mask = mask_set ## Napari's labels layer updating

        # Display the combined mask
        self.viewer.add_labels(combined_mask, name=f"Mask Layer {img_idx + 1}-{rgb_idx + 1}")
        self.display_label_range()
        
        if hasattr(self, 'binarized_masks_per_image') and len(self.binarized_masks_per_image) > img_idx:
            if len(self.binarized_masks_per_image[img_idx]) > rgb_idx:
                # print("testing show_image_and_mask passing binarized layer condition")
                binarized_layer = self.binarized_masks_per_image[img_idx][rgb_idx]
                if binarized_layer is not None and len(np.unique(binarized_layer)) > 1:
                    self.viewer.add_labels(binarized_layer, name=f"Binarized Mask Layer {img_idx + 1}-{rgb_idx + 1}")

        
    #########################
    ## Functionality based methods
    
    ### Image loading
    def load_images(self):
        ''' Load images from file dialog '''
        logger.info("User initiated image loading.")
        
        # Dynamic file filter including "All files"
        file_types = [("Image files", "*.png;*.jpg;*.tif;*.bmp;*.raw;*.dat"), 
                  ("All files", "*.*")]
        file_paths = filedialog.askopenfilenames(filetypes=file_types)

        if not file_paths:
            QMessageBox.warning(self, "No files selected", "Please select one or more image files.")
            return

        # Now run the actual image loading in a separate thread
        self.thread = QThread()
        self.worker = Worker(self.load_images_in_thread, file_paths)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result.connect(self.handle_images_loaded)
        self.worker.error.connect(self.handle_loading_error)

        self.thread.start()
        

    def load_images_in_thread(self, file_paths):
        ''' Load images in a separate thread '''
        images = []
        pseudo_rgb_images_per_image = []
        masks_per_image = []
        binarized_masks_per_image = []

        # Store all paths that lack corresponding .hdr files
        dat_files_without_hdr = []

        for file_path in file_paths:
            # Extract just the file name and extension, avoiding the full path
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            logger.info(f"Processing file: {file_name} (Format: {file_extension})")

            if file_extension == '.raw':
                tiff_file = os.path.splitext(file_path)[0] + '_converted.tif'
                subprocess.run(["gdal_translate", "-of", "GTiff", file_path, tiff_file])
                logger.info(f"Loading {file_extension} file after converting to TIFF format")
                hyperspectral_data = io.imread(tiff_file)
                images.append(hyperspectral_data)
            elif file_extension == '.dat':
                hdr_file_path_lower = file_path.replace('.dat', '.hdr')  
                hdr_file_path_upper = file_path.replace('.dat', '.HDR') 
                
                # Check if either exists
                if not os.path.exists(hdr_file_path_lower) and not os.path.exists(hdr_file_path_upper):
                    logger.warning(f"No corresponding .hdr file found for {file_name}.")
                    dat_files_without_hdr.append(file_path)
                else:
                    # Use the one that exists
                    hdr_file_path = hdr_file_path_lower if os.path.exists(hdr_file_path_lower) else hdr_file_path_upper
                    logger.info(f"Detected .dat file with existing .hdr: {os.path.basename(hdr_file_path)}")
                    hsi_image = open_image(hdr_file_path)
                    hyperspectral_data = hsi_image.load().astype(np.float32)
                    images.append(hyperspectral_data)   
            else:
                logger.info(f"Loading standard image format: {file_extension}")
                hyperspectral_data = io.imread(file_path)
                images.append(hyperspectral_data)

        if dat_files_without_hdr:
            logger.warning(f"User needs to provide .hdr file for {len(dat_files_without_hdr)} .dat files.")
            return dat_files_without_hdr, images, None, None, None

        if images:
            pseudo_rgb_images_per_image = [[] for _ in range(len(images))]
            masks_per_image = [[] for _ in range(len(images))]
            binarized_masks_per_image = [[] for _ in range(len(self.images))]

        return None, images, pseudo_rgb_images_per_image, masks_per_image, binarized_masks_per_image
    
    
    def handle_images_loaded(self, result):
        ''' Handle the result of image loading '''
        dat_files_without_hdr, images, pseudo_rgb_images_per_image, masks_per_image, binarized_masks_per_image = result

        if dat_files_without_hdr:
            hdr_file_path = filedialog.askopenfilename(
                title="Select the .hdr file to be used for .dat files without a corresponding .hdr file", 
                filetypes=[("HDR files", "*.hdr;*.HDR")])  
            if hdr_file_path:
                for file_path in dat_files_without_hdr:
                    try:
                        temp_hdr_path = file_path.replace('.dat', '.hdr')
                        shutil.copy(hdr_file_path, temp_hdr_path)
                        logger.info(f"Copied .hdr file to {temp_hdr_path} for {file_path}.")

                        hsi_image = open_image(temp_hdr_path)
                        hyperspectral_data = hsi_image.load().astype(np.float32)
                        images.append(hyperspectral_data)

                        # Remove temporary .hdr file
                        os.remove(temp_hdr_path)
                        logger.info(f"Temporary .hdr file removed: {temp_hdr_path}")
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
            else:
                QMessageBox.warning(self, "No .hdr file selected", "Some .dat files were skipped.")
                return  # Exit the function since required .hdr files were not provided

        # Ensure all containers are initialized properly
        if pseudo_rgb_images_per_image is None:
            pseudo_rgb_images_per_image = [[] for _ in range(len(images))]
        if masks_per_image is None:
            masks_per_image = [[] for _ in range(len(images))]
        if binarized_masks_per_image is None:
            binarized_masks_per_image = [[] for _ in range(len(images))]

        # Update instance variables with the loaded data
        self.images = images
        self.pseudo_rgb_images_per_image = pseudo_rgb_images_per_image
        self.masks_per_image = masks_per_image
        self.binarized_masks_per_image = binarized_masks_per_image
        logger.info(f"Images loaded successfully: {len(self.images)} images.")

        # Handle image display and navigation button updates
        if len(self.images) > 0:
            self.current_image_index = 0
            self.show_image_data()
            self.update_button_highlight(None)

        # Enable navigation buttons if more than one image is loaded
        self.previous_button.setEnabled(len(self.images) > 1)
        self.next_button.setEnabled(len(self.images) > 1)


    def handle_loading_error(self, error_msg):
        ''' Handle errors that occur during image loading '''
        logger.error(f"Image loading error: {error_msg}")
        QMessageBox.warning(self, "Image Loading Error", f"An error occurred: {error_msg}")
    
    ### Spectral Indexing  
    def compute_image(self):
        ''' Compute pseudo-RGB image based on user input '''        
        logger.info(f"User initiated pseudo-RGB computation.")
        if not self.images:
            QMessageBox.warning(self, "No Images Loaded", "Please load images before computing a pseudo-RGB image.")
            return
        
        r_expr = self.r_input.text()
        g_expr = self.g_input.text()
        b_expr = self.b_input.text()

        if not r_expr or not g_expr or not b_expr:
            QMessageBox.warning(self, "Invalid Input", "Please fill all fields (Red, Green, and Blue expressions).")
            logger.warning(f"Invalid input. Missing input in field(s). Expressions entered. Red: {r_expr} ; Green: {g_expr} ; Blue: {b_expr}")
            return
        
        # Validate expressions
        if not validate_expression(r_expr) or not validate_expression(g_expr) or not validate_expression(b_expr):
            QMessageBox.warning(self, "Invalid Input", "Please enter valid channel expressions using ch[i] (e.g., ch[10]/ch[3] + ch[20]*2 + 5)")
            logger.warning(f"Invalid channel expressions entered. Red: {r_expr} ; Green: {g_expr} ; Blue: {b_expr}")
            return
        
        logger.info(f"Valid expressions entered: Red: {r_expr} ; Green: {g_expr} ; Blue: {b_expr}")

        # Create a QThread object
        self.thread = QThread()

        # Create a worker object for computation
        self.worker = Worker(self.compute_pseudo_rgb_in_thread, r_expr, g_expr, b_expr)
        self.worker.moveToThread(self.thread)    # Move the worker to the thread

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result.connect(self.handle_pseudo_rgb_computed)

        # Start the thread
        self.thread.start()

    
    def compute_pseudo_rgb_in_thread(self, r_expr, g_expr, b_expr):
        ''' Compute pseudo-RGB image in a separate thread '''
        skipped_images = []
        pseudo_rgb_results = [[] for _ in range(len(self.images))]  # Initialize list of lists for each image

        for idx, hyperspectral_data in enumerate(self.images):
            num_channels = hyperspectral_data.shape[-1]
            channels = {i: hyperspectral_data[:, :, i] for i in range(num_channels)}
            try:
                # Validate expressions before computation
                red_channel = compute_channel(channels, r_expr)
                green_channel = compute_channel(channels, g_expr)
                blue_channel = compute_channel(channels, b_expr)
                
                # Create pseudo-RGB image
                pseudo_rgb_image = np.stack([red_channel, green_channel, blue_channel], axis=-1)
                pseudo_rgb_results[idx].append(pseudo_rgb_image)  # Append new image to the list
                logger.info(f"Computed pseudo-RGB image for image {idx + 1}")

            except KeyError as e:
                logger.error(f"Error computing channel for image {idx + 1}: {e}")
                skipped_images.append(idx)
            except Exception as e:
                logger.error(f"Unexpected error for image {idx + 1}: {e}")
                skipped_images.append(idx)

        return pseudo_rgb_results, skipped_images
        
    
    def handle_pseudo_rgb_computed(self, result):
        ''' Handle the result of pseudo-RGB computation '''
        pseudo_rgb_results, skipped_images = result

        # Append the new pseudo-RGB results to the existing list
        for idx, results in enumerate(pseudo_rgb_results):
            if results:
                if idx >= len(self.pseudo_rgb_images_per_image):
                    self.pseudo_rgb_images_per_image.append(results)
                else:
                    self.pseudo_rgb_images_per_image[idx].extend(results)

        if skipped_images:
            logger.warning(f"The following images were skipped due to invalid channels: {skipped_images}")
            QMessageBox.warning(
                self, 
                "Channel Error", 
                f"The following images were skipped due to invalid channels: {skipped_images}"
            )

        if all(not images for images in self.pseudo_rgb_images_per_image):
            QMessageBox.critical(self, "Error", "Pseudo-RGB computation failed for all images.")
            logger.error("No pseudo-RGB images were generated for any image.")
            return

        # Update buttons for the current image index
        self.update_pseudo_rgb_buttons()


    ### SAM Model Settings
    def initialize_model(self):
        ''' Initialize Segment Anything Model based on user input '''
        model_type = self.model_type_combo.currentText()
        checkpoint_option = self.checkpoint_combo.currentData()
        print(f"Device: {device}")
        logger.info(f"Device: {device}")
        try:
            if model_type == "ViT-huge":
                if checkpoint_option is None or checkpoint_option == "default":
                    # print("Loading default vit-h model via pipeline...")
                    logger.info("Loading default vit-h model.")
                    self.mask_generator = pipeline("mask-generation", model="facebook/sam-vit-huge", device=0)
                else:
                    # print(f"Loading custom vit-h model from: {checkpoint_option}")
                    logger.info(f"Loading custom vit-h model from checkpoint: {checkpoint_option}")
                    self.mask_generator = None
                    self.model = SamModel.from_pretrained("facebook/sam-vit-huge")
                    self.processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")
                    self.model.load_state_dict(torch.load(checkpoint_option, weights_only=True))
                    self.model.to(device)

            elif model_type == "ViT-base":
                if checkpoint_option is None or checkpoint_option == "default":
                    logger.info("Loading default vit-b model.")
                    self.mask_generator = pipeline("mask-generation", model="facebook/sam-vit-base", device=0)
                else:
                    logger.info(f"Loading custom vit-b model from checkpoint: {checkpoint_option}")
                    self.mask_generator = None
                    self.model = SamModel.from_pretrained("facebook/sam-vit-base")
                    self.processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
                    self.model.load_state_dict(torch.load(checkpoint_option, weights_only=True))
                    self.model.to(device)
                                
            if self.threshold_checkbox:
                self.threshold_checkbox.setVisible(False)
            
            if self.threshold_slider:
                self.threshold_slider.setVisible(False)

            QMessageBox.information(self, "Success", "Model initialized successfully!")
            self.segment_button.setEnabled(True)
            logger.info("Model initialized successfully.")

        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            QMessageBox.warning(self, "Error", f"Failed to initialize model: {str(e)}")           

    def load_custom_checkpoint(self):
        ''' Load a custom checkpoint file for the model '''
        file_path = filedialog.askopenfilename(filetypes=[("Checkpoint files", "*.pth")])
        if file_path:
            self.checkpoint_combo.addItem(f"Custom Checkpoint: {file_path}", userData=file_path)
            self.checkpoint_combo.setCurrentIndex(self.checkpoint_combo.count() - 1)
    
    
    ### Segmentation        
    def run_segmentation(self):
        ''' Run segmentation on the pseudo-RGB images '''
        logger.info("Segmenting..")
        self.viewer.status = "Segmentation is running..."
        
        self.masks_per_image = [[] for _ in range(len(self.images))]
        self.upscaled_masks_per_image = [[] for _ in range(len(self.images))]

        # Start a new thread for segmentation
        self.thread = QThread()

        # Create the worker for segmentation
        self.worker = Worker(self.segment_images_in_thread)

        # Move the worker to the new thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result.connect(self.handle_segmentation_result)
        self.worker.error.connect(self.handle_segmentation_error)

        # Start the thread
        self.thread.start()

    def segment_images_in_thread(self):
        ''' Segment the pseudo-RGB images in a separate thread '''
        try:
            segmented_masks_list = []  # To store all segmented masks
            min_val, max_val = None, None  # Initialize min and max values

            for idx, pseudo_rgb_images in enumerate(self.pseudo_rgb_images_per_image):
                if not pseudo_rgb_images:
                    logger.info("Segmentation run with no pseudo RGB images computed.")
                    continue  # Skip if no pseudo-RGB images have been computed for this image

                all_pseudo_rgb_images = [rgb_image for rgb_image in pseudo_rgb_images]
                
                if self.mask_generator:   # Default model
                    segmented_masks = segment_images_with_pipeline(self.mask_generator, all_pseudo_rgb_images)
                elif self.model and self.processor:   # Custom model
                    segmented_masks, upscaled_masks = segment_images_with_custom_model(self.model, self.processor, all_pseudo_rgb_images)
                    # Get min and max values for the thresholding controls
                    min_val, max_val = upscaled_masks.min().item(), upscaled_masks.max().item()

                    # Cache the upscaled masks for thresholding later
                    self.upscaled_masks_per_image[idx] = upscaled_masks

                segmented_masks_list.append(segmented_masks)

            # If no segmentation was done, return empty result
            if not segmented_masks_list:
                return None, None, None

            # Return the masks and min-max values for thresholding
            return segmented_masks_list, min_val, max_val

        except Exception as e:
            raise RuntimeError(f"Segmentation failed: {str(e)}")


    def handle_segmentation_result(self, result):
        ''' Handle the result of segmentation '''
        segmented_masks_list, min_val, max_val = result

        # If we received valid segmented masks, update the UI and show them
        if segmented_masks_list:
            logger.info("Segmentation completed successfully.")
            self.masks_per_image = segmented_masks_list
            self.binarize_button.setEnabled(True)
            
            # Initialize binarized_masks_per_image with zeros
            self.binarized_masks_per_image = [
                [
                    np.zeros(mask.shape[:2], dtype=np.uint8) if isinstance(mask, np.ndarray) else None
                    for mask in image_masks
                ]
                for image_masks in self.masks_per_image
            ]
            # Display the current image and its mask
            self.show_image_and_mask(self.current_image_index, 0)
            self.update_button_highlight(0)

            # Show threshold controls if valid min and max values are available
            if min_val is not None and max_val is not None:
                self.show_threshold_controls(min_val, max_val)
            
            self.viewer.status = "Masks generated"
        else:
            logger.warning("Segmentation returned no masks.")
            self.viewer.status = "Segmentation failed"
            QMessageBox.warning(self, "Segmentation Error", "No segmentation masks were produced.")


    def handle_segmentation_error(self, error_msg):
        ''' Handle errors that occur during segmentation '''
        logger.error(f"Segmentation error: {error_msg}")
        QMessageBox.warning(self, "Segmentation Error", f"{error_msg}")
        self.segment_button.setEnabled(True)

         
    ### Binarizer
    
    def binarize_labels(self):
        ''' Binarize the labels in the current mask layer based on user input '''
        label_text = self.label_input.toPlainText()
        logger.info("Binarize button clicked.")

        if not label_text:
            binarize_values = [1]  # Default to label 1
            logger.info("No label values provided; defaulting to label 1.")
        else:
            label_ranges = label_text.split(',')
            binarize_values = []
            for label_range in label_ranges:
                if '-' in label_range:
                    start, end = label_range.split('-')
                    binarize_values.extend(range(int(start), int(end) + 1))
                else:
                    binarize_values.append(int(label_range.strip()))
            logger.info(f"Label values provided for binarization: {binarize_values}")

        # current mask layer of current pseudo-RGB image
        mask_layer_name = f"Mask Layer {self.current_image_index + 1}-{self.current_rgb_idx + 1}"
        if mask_layer_name in self.viewer.layers:
            layer = self.viewer.layers[mask_layer_name]
            if isinstance(layer, napari.layers.Labels):
                data = layer.data
                binary_mask = np.isin(data, binarize_values).astype(np.uint8)
                self.binarized_masks_per_image[self.current_image_index][self.current_rgb_idx] = binary_mask
                self.viewer.add_labels(binary_mask, name=f"Binarized {layer.name}")
                logger.info(f"Binarization applied successfully to {mask_layer_name}.")
            self.binarize_status_label.setText("Mask binarized. Find the binarized mask in the Layers menu.")

    def display_label_range(self):
        ''' Display the range of labels in the current mask layer in Binarizer tab'''
        mask_layer_name = f"Mask Layer {self.current_image_index + 1}-{self.current_rgb_idx + 1}"
        if mask_layer_name in self.viewer.layers:
            layer = self.viewer.layers[mask_layer_name]
            if isinstance(layer, napari.layers.Labels):
                unique_labels = np.unique(layer.data)
                label_range_text = f"Labels in current mask range from {unique_labels.min()} to {unique_labels.max()}"
                self.binarize_status_label.setText(label_range_text) 
        
    ### Mask thresholding with custom model
    
    def show_threshold_controls(self, min_val, max_val):
        # Add threshold checkbox and slider
        if not self.threshold_checkbox:
            self.threshold_checkbox = QCheckBox("Apply Threshold", self)
            self.threshold_checkbox.stateChanged.connect(self.toggle_threshold)
            self.layout().addWidget(self.threshold_checkbox)

        if not self.threshold_slider:
            self.threshold_slider = QSlider(Qt.Horizontal, self)
            # print("Min and max values: ", int(min_val), int(max_val))
            self.threshold_slider.setMinimum(int(min_val))  # Convert to int for the slider
            self.threshold_slider.setMaximum(int(max_val))
            self.threshold_slider.setVisible(False)
            self.threshold_slider.valueChanged.connect(self.update_masks_with_threshold)
            self.layout().addWidget(self.threshold_slider)
        # Show the checkbox
        self.threshold_checkbox.setVisible(True)

    def toggle_threshold(self, state):
        if state == Qt.Checked:
            self.threshold_slider.setVisible(True)
            logger.info("Threshold checkbox state True.")  
        else:
            self.threshold_slider.setVisible(False)
            logger.info("Threshold checkbox state False.")

    def update_masks_with_threshold(self, value):
        # Update the thresholded masks based on the slider value
        logger.info("Threshold slider value updated.")
        upscaled_masks = self.upscaled_masks_per_image[self.current_image_index]
        if upscaled_masks is not None:
            thresholded_masks = normalize(threshold(upscaled_masks, threshold=value, value=0)).squeeze(1)
            self.masks_per_image[self.current_image_index][self.current_rgb_idx] = thresholded_masks.cpu()
            self.show_image_and_mask(self.current_image_index, self.current_rgb_idx)
            self.update_button_highlight(self.current_rgb_idx)

