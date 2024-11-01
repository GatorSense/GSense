import napari
import numpy as np
import torch
from torch.nn.functional import threshold, normalize, interpolate
from tkinter import filedialog
from skimage import io
from qtpy.QtWidgets import QWidget, QStyle, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QDockWidget, QMenu, QCheckBox, QSlider, QTabWidget
from qtpy.QtWidgets import QVBoxLayout, QLineEdit,QPlainTextEdit
from qtpy.QtCore import QThread, Signal
from qtpy.QtGui import QFont
from qtpy.QtCore import Qt
from transformers import pipeline, SamModel, SamProcessor
import os
import shutil
import subprocess
from spectral import open_image
from app.worker import Worker
from app.core import compute_channel, segment_images_with_pipeline, segment_images_with_custom_model, save_all_layers, save_selected_layer
from app.core import device



class CustomWidget(QWidget):
    def __init__(self, viewer, layer_list_dock, layer_controls_dock):
        super().__init__()
        self.viewer = viewer
        self.layer_list_dock = layer_list_dock
        self.layer_controls_dock = layer_controls_dock
                
        self.images = []  # List to hold loaded images
        self.file_paths = []  # List to hold file paths of loaded images
        self.current_image_index = 0  # Index of the current image being displayed
        self.current_img_idx = 0  # To track currently displayed image index
        self.current_rgb_idx = 0  # To track currently displayed pseudo-RGB index
        self.pseudo_rgb_images_per_image = []  # Store pseudoRGB images for each loaded image
        self.masks_per_image = []  # Store segmentation masks for each loaded image

        self.model = None
        self.processor = None
        self.pseudo_rgb_buttons = []
        self.mask_generator = None
        self.upscaled_masks = None  # Cached low-res masks for thresholding
        self.threshold_checkbox = None
        self.threshold_slider = None
        self.threshold_value = None
        self.upscaled_masks_per_image = []         

        layout = QVBoxLayout()
        
        tab_widget = QTabWidget()
        
        # Create a horizontal layout for buttons you want to move to the bottom
        self.bottom_layout = QHBoxLayout()
        
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
        
        self.compute_button = QPushButton("Compute PseudoRGB", self)
        self.compute_button.clicked.connect(self.compute_image)
        spectral_layout.addWidget(self.compute_button)

        spectral_mixing_widget.setLayout(spectral_layout)

        ######### Model Settings Tab #########
        model_settings_widget = QWidget()
        model_layout = QVBoxLayout()
        
        self.model_type_combo = QComboBox(self)
        self.model_type_combo.addItems(["vit-h", "vit-b"])
        model_layout.addWidget(QLabel("Select Model Type (ViT):"))
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
        
        self.binarize_status_label = QLabel(self)  # Label to show the status
        binarize_layout.addWidget(self.binarize_status_label)
        
        binarize_widget.setLayout(binarize_layout)

        # Add tabs to the QTabWidget
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
        self.hsi_button.clicked.connect(self.show_hyperspectral_image)
        layout.addWidget(self.hsi_button, stretch=0)
        
        
        
        ######### Pseudo-RGB Buttons #########

        self.pseudo_rgb_buttons_layout = QVBoxLayout()
        layout.addLayout(self.pseudo_rgb_buttons_layout)

        ######### Navigation Buttons #########        

        # Add Next and Previous buttons for navigation
        self.previous_button = QPushButton("Previous Image", self)
        self.previous_button.clicked.connect(self.show_previous_image)
        self.previous_button.setEnabled(False)  # Disabled until multiple images are loaded
        # layout.addWidget(self.previous_button)

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
        self.save_button = QPushButton("Save Selected", self)
        save_icon = self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton'))
        self.save_button.setIcon(save_icon)
        self.save_button.setToolTip("Save Selected Layer")
        self.save_button.clicked.connect(lambda: save_selected_layer(self.viewer))
        self.save_button.setEnabled(False)  # Initially disabled
        save_buttons_layout.addWidget(self.save_button, Qt.AlignRight)

        # Save All Layers Button
        self.save_all_button = QPushButton("Save All", self)
        save_all_icon = self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton'))
        self.save_all_button.setIcon(save_all_icon)
        self.save_all_button.setToolTip("Save All Layers")
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

    # Add buttons to hide/show the Layer Controls and Layer List dock widgets
    def toggle_layer_list(self):
        self.layer_list_dock.setVisible(not self.layer_list_dock.isVisible())

    def toggle_layer_controls(self):
        self.layer_controls_dock.setVisible(not self.layer_controls_dock.isVisible())

        
    def binarize_labels(self):
        label_text = self.label_input.toPlainText()
        if not label_text:
            binarize_values = [1]  # Default to label 1
        else:
            label_ranges = label_text.split(',')
            binarize_values = []
            for label_range in label_ranges:
                if '-' in label_range:
                    start, end = label_range.split('-')
                    binarize_values.extend(range(int(start), int(end) + 1))
                else:
                    binarize_values.append(int(label_range.strip()))

        # Get the current mask layer corresponding to the current pseudo-RGB image
        mask_layer_name = f"Mask Layer {self.current_img_idx + 1}-{self.current_rgb_idx + 1}"
        if mask_layer_name in self.viewer.layers:
            layer = self.viewer.layers[mask_layer_name]
            if isinstance(layer, napari.layers.Labels):
                data = layer.data
                binary_mask = np.isin(data, binarize_values).astype(np.uint8)
                self.viewer.add_labels(binary_mask, name=f"Binarized {layer.name}")
                # print(f"Layer {layer.name} binarized successfully.")

            self.binarize_status_label.setText("Binarization applied successfully.")
            # print("Binarization applied successfully.")

    def load_custom_checkpoint(self):
        file_path = filedialog.askopenfilename(filetypes=[("Checkpoint files", "*.pth")])
        if file_path:
            self.checkpoint_combo.addItem(f"Custom Checkpoint: {file_path}", userData=file_path)
            self.checkpoint_combo.setCurrentIndex(self.checkpoint_combo.count() - 1)
            
    def create_pseudo_rgb_button(self, img_idx, rgb_idx):
        """Create a pseudo-RGB button and add right-click context menu."""
        button = QPushButton(f"Pseudo-RGB {img_idx + 1}-{rgb_idx + 1}", self)
        button.clicked.connect(lambda: self.show_pseudo_rgb_image(img_idx, rgb_idx))
        
        # Add right-click context menu to the button
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda pos, img_idx=img_idx, rgb_idx=rgb_idx: self.show_context_menu(button, pos, img_idx, rgb_idx))
        
        self.pseudo_rgb_buttons.append(button)
        self.pseudo_rgb_buttons_layout.addWidget(button)
        
    def show_context_menu(self, button, pos, img_idx, rgb_idx):
        """Show a context menu with delete options when right-clicking a pseudo-RGB button."""
        menu = QMenu(self)

        # Option 1: Delete this specific pseudo-RGB image for the current image
        delete_single_action = menu.addAction("Delete this Pseudo-RGB Image")
        delete_single_action.triggered.connect(lambda: self.delete_single_pseudo_rgb(img_idx, rgb_idx))

        # Option 2: Delete this pseudo-RGB image for all batch images
        delete_all_action = menu.addAction("Delete this Pseudo-RGB Image for all images")
        delete_all_action.triggered.connect(lambda: self.delete_pseudo_rgb_for_all_images(rgb_idx))

        # Show the context menu
        menu.exec_(button.mapToGlobal(pos))

    def delete_single_pseudo_rgb(self, img_idx, rgb_idx):
        """Delete a specific pseudo-RGB image for the selected image."""
        # Remove the pseudo-RGB image
        if 0 <= img_idx < len(self.pseudo_rgb_images_per_image):
            if 0 <= rgb_idx < len(self.pseudo_rgb_images_per_image[img_idx]):
                del self.pseudo_rgb_images_per_image[img_idx][rgb_idx]

        # Update UI: remove the button
        self.update_pseudo_rgb_buttons(img_idx)
        self.viewer.layers.clear()

    def delete_pseudo_rgb_for_all_images(self, rgb_idx):
        """Delete a specific pseudo-RGB image for all batch images."""
        # Remove the pseudo-RGB image for each image in the batch
        for idx, pseudo_rgb_images in enumerate(self.pseudo_rgb_images_per_image):
            if 0 <= rgb_idx < len(pseudo_rgb_images):
                del self.pseudo_rgb_images_per_image[idx][rgb_idx]

        # Update UI: remove buttons for the current image
        self.update_pseudo_rgb_buttons(self.current_image_index)
        self.viewer.layers.clear()

    def update_pseudo_rgb_buttons(self, img_idx):
        """Update the pseudo-RGB buttons for the current image."""
        # Clear existing buttons
        for button in self.pseudo_rgb_buttons:
            self.pseudo_rgb_buttons_layout.removeWidget(button)
            button.deleteLater()
        self.pseudo_rgb_buttons = []

        # Recreate the buttons for the current image
        if self.pseudo_rgb_images_per_image[img_idx]:
            for i, _ in enumerate(self.pseudo_rgb_images_per_image[img_idx]):
                self.create_pseudo_rgb_button(img_idx, i)

    def initialize_model(self):
        model_type = self.model_type_combo.currentText()
        checkpoint_option = self.checkpoint_combo.currentData()
        print(f"Device: {device}")

        try:
            if model_type == "vit-h":
                if checkpoint_option is None or checkpoint_option == "default":
                    print("Loading default vit-h model via pipeline...")
                    self.mask_generator = pipeline("mask-generation", model="facebook/sam-vit-huge", device=0)
                else:
                    print(f"Loading custom vit-h model from: {checkpoint_option}")
                    self.mask_generator = None
                    self.model = SamModel.from_pretrained("facebook/sam-vit-huge")
                    self.processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")
                    self.model.load_state_dict(torch.load(checkpoint_option))
                    self.model.to(device)

            elif model_type == "vit-b":
                if checkpoint_option is None or checkpoint_option == "default":
                    print("Loading default vit-b model via pipeline...")
                    self.mask_generator = pipeline("mask-generation", model="facebook/sam-vit-base", device=0)
                else:
                    print(f"Loading custom vit-b model from: {checkpoint_option}")
                    self.mask_generator = None
                    self.model = SamModel.from_pretrained("facebook/sam-vit-base")
                    self.processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
                    self.model.load_state_dict(torch.load(checkpoint_option))
                    self.model.to(device)
                    
            
            if self.threshold_checkbox:
                self.threshold_checkbox.setVisible(False)
            
            if self.threshold_slider:
                self.threshold_slider.setVisible(False)

            # print("Model and processor initialized successfully")
            QMessageBox.information(self, "Success", "Model initialized successfully!")
            # Enable the segmentation button
            self.segment_button.setEnabled(True)

        except Exception as e:
            print(f"Error initializing model: {e}")
            QMessageBox.warning(self, "Error", f"Failed to initialize model: {str(e)}")
            
    def load_images(self):
        # Open file dialog in the main thread
        file_types = [("Image files", "*.png;*.jpg;*.tif;*.bmp;*.raw;*.dat")]
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
        images = []
        pseudo_rgb_images_per_image = []
        masks_per_image = []

        # Store all paths that lack corresponding .hdr files
        dat_files_without_hdr = []

        for file_path in file_paths:
            file_extension = os.path.splitext(file_path)[1]
            if file_extension == '.raw':
                # Process raw files (convert to TIFF)
                tiff_file = os.path.splitext(file_path)[0] + '_converted.tif'
                subprocess.run(["gdal_translate", "-of", "GTiff", file_path, tiff_file])
                hyperspectral_data = io.imread(tiff_file)
                images.append(hyperspectral_data)
            elif file_extension == '.dat':
                # Check if the corresponding .hdr file exists
                hdr_file_path = file_path.replace('.dat', '.hdr')
                if not os.path.exists(hdr_file_path):
                    dat_files_without_hdr.append(file_path)
                else:
                    # Read the hyperspectral data using the hdr file
                    hsi_image = open_image(hdr_file_path)
                    hyperspectral_data = hsi_image.load().astype(np.float32)
                    images.append(hyperspectral_data)
            else:
                # Load standard image formats
                hyperspectral_data = io.imread(file_path)
                images.append(hyperspectral_data)

        # Handle .dat files without .hdr files
        if dat_files_without_hdr:
            # Since file dialogs are UI, they must happen on the main thread
            return dat_files_without_hdr, images

        # If images were loaded successfully, return them
        if images:
            pseudo_rgb_images_per_image = [[] for _ in range(len(images))]
            masks_per_image = [[] for _ in range(len(images))]
        
        return None, images, pseudo_rgb_images_per_image, masks_per_image


    def handle_images_loaded(self, result):
        dat_files_without_hdr, images, pseudo_rgb_images_per_image, masks_per_image = result

        if dat_files_without_hdr:
            # Ask the user to select .hdr file for the .dat files that don't have them
            hdr_file_path = filedialog.askopenfilename(
                title="Select the .hdr file to be used for .dat files without a corresponding .hdr file", 
                filetypes=[("HDR files", "*.hdr")]
            )
            if hdr_file_path:
                for file_path in dat_files_without_hdr:
                    try:
                        temp_hdr_path = file_path.replace('.dat', '.hdr')
                        shutil.copy(hdr_file_path, temp_hdr_path)

                        hsi_image = open_image(temp_hdr_path)
                        hyperspectral_data = hsi_image.load().astype(np.float32)
                        images.append(hyperspectral_data)

                        # Clean up temporary .hdr file
                        os.remove(temp_hdr_path)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
            else:
                QMessageBox.warning(self, "No .hdr file selected", "Some .dat files were skipped.")
                return

        # Now that all images have been loaded (with any .hdr files included), assign them
        self.images = images
        self.pseudo_rgb_images_per_image = pseudo_rgb_images_per_image
        self.masks_per_image = masks_per_image

        # Show the first image
        if len(self.images) > 0:
            self.show_image(0)

        # Enable navigation buttons if more than one image is loaded
        if len(self.images) > 1:
            self.previous_button.setEnabled(True)
            self.next_button.setEnabled(True)


    def handle_loading_error(self, error_msg):
        QMessageBox.warning(self, "Image Loading Error", f"An error occurred: {error_msg}")


    def show_image(self, index):
        self.current_image_index = index
        hyperspectral_image = self.images[index]

        # Clear all layers in the viewer and display the current image
        self.viewer.layers.clear()
        self.viewer.add_image(hyperspectral_image, colormap='gray', name=f"Image {index+1}")

        # Update the pseudo-RGB buttons for the current image
        self.update_pseudo_rgb_buttons(index)

        self.set_spectral_mixing_enabled(True)
        self.save_button.setEnabled(False)
        self.hsi_button.setVisible(True)  # Hide the Image button initially

    def show_pseudo_rgb_image(self, img_idx, rgb_idx):
        # Store current image and RGB index
        self.current_img_idx = img_idx
        self.current_rgb_idx = rgb_idx

        pseudo_rgb_image = self.pseudo_rgb_images_per_image[img_idx][rgb_idx]

        self.viewer.layers.clear()
        self.viewer.add_image(pseudo_rgb_image, rgb=True, name=f"Pseudo-RGB Image {img_idx + 1}-{rgb_idx + 1}")
        self.save_button.setEnabled(True)

        # Enable the Image button to allow switching back to the actual image
        self.hsi_button.setVisible(True)
        self.hsi_button.setEnabled(True)

        if len(self.masks_per_image[img_idx]) > rgb_idx:
            self.show_image_and_mask(img_idx, rgb_idx)

    def show_next_image(self):
        # Save the current pseudo-RGB images and masks before navigating
        self.save_current_pseudo_rgb_and_masks()

        # Move to the next image
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.show_image(self.current_image_index)

    def show_previous_image(self):
        # Save the current pseudo-RGB images and masks before navigating
        self.save_current_pseudo_rgb_and_masks()

        # Move to the previous image
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.show_image(self.current_image_index)

    def save_current_pseudo_rgb_and_masks(self):
        # Get the current pseudo-RGB images and corresponding masks from the viewer
        for rgb_idx, _ in enumerate(self.pseudo_rgb_buttons):
            # Retrieve the pseudo-RGB image and corresponding mask for each button
            pseudo_rgb_layer_name = f"Pseudo-RGB Image {self.current_img_idx + 1}-{rgb_idx + 1}"
            mask_layer_name = f"Mask Layer {self.current_img_idx + 1}-{rgb_idx + 1}"

            pseudo_rgb_image = None
            mask_layer = None

            # Find layers in the viewer
            for layer in self.viewer.layers:
                if layer.name == pseudo_rgb_layer_name:
                    pseudo_rgb_image = layer.data
                    self.pseudo_rgb_images_per_image[self.current_image_index][rgb_idx] = pseudo_rgb_image
                elif layer.name == mask_layer_name:
                    mask_layer = layer.data
                    # print("Data: ", mask_layer)
                    self.masks_per_image[self.current_image_index][rgb_idx] = mask_layer
        
    def compute_image(self):
        r_expr = self.r_input.text()
        g_expr = self.g_input.text()
        b_expr = self.b_input.text()

        # Create a QThread object
        self.thread = QThread()

        # Create a worker object for computation
        self.worker = Worker(self.compute_pseudo_rgb_in_thread, r_expr, g_expr, b_expr)

        # Move the worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result.connect(self.handle_pseudo_rgb_computed)
        self.worker.error.connect(self.handle_computation_error)

        # Start the thread
        self.thread.start()

    def compute_pseudo_rgb_in_thread(self, r_expr, g_expr, b_expr):
        for idx, hyperspectral_data in enumerate(self.images):
            channels = {i: hyperspectral_data[:, :, i] for i in range(hyperspectral_data.shape[-1])}
            red_channel = compute_channel(channels, r_expr)
            green_channel = compute_channel(channels, g_expr)
            blue_channel = compute_channel(channels, b_expr)
            pseudo_rgb_image = np.stack([red_channel, green_channel, blue_channel], axis=-1)
            self.pseudo_rgb_images_per_image[idx].append(pseudo_rgb_image)

        return self.pseudo_rgb_images_per_image

    def handle_pseudo_rgb_computed(self, result):
        self.pseudo_rgb_images_per_image = result
        self.update_pseudo_rgb_buttons(self.current_image_index)
        
    def handle_computation_error(self, error_msg):
        QMessageBox.warning(self, "Computation Error", f"An error occurred: {error_msg}")

            
    def show_hyperspectral_image(self):
        hyperspectral_image = self.images[self.current_image_index]
        self.viewer.layers.clear()
        self.viewer.add_image(hyperspectral_image, colormap='gray', name="Image")
        self.save_button.setEnabled(False)
        self.set_spectral_mixing_enabled(True)
    
    def run_segmentation(self):
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
        try:
            segmented_masks_list = []  # To store all segmented masks
            min_val, max_val = None, None  # Initialize min and max values

            for idx, pseudo_rgb_images in enumerate(self.pseudo_rgb_images_per_image):
                if not pseudo_rgb_images:
                    continue  # Skip if no pseudo-RGB images have been computed for this image

                all_pseudo_rgb_images = [rgb_image for rgb_image in pseudo_rgb_images]

                # Check if using default model or custom model
                if self.mask_generator:
                    segmented_masks = segment_images_with_pipeline(self.mask_generator, all_pseudo_rgb_images)
                elif self.model and self.processor:
                    segmented_masks, upscaled_masks = segment_images_with_custom_model(self.model, self.processor, all_pseudo_rgb_images)

                    # Get min and max values for the thresholding controls
                    min_val, max_val = upscaled_masks.min().item(), upscaled_masks.max().item()

                    # Cache the upscaled masks for thresholding later
                    self.upscaled_masks_per_image[idx] = upscaled_masks

                # Append segmented masks to the list
                segmented_masks_list.append(segmented_masks)

            # If no segmentation was done, return empty result
            if not segmented_masks_list:
                return None, None, None

            # Return the masks and min-max values for thresholding
            return segmented_masks_list, min_val, max_val

        except Exception as e:
            raise RuntimeError(f"Segmentation failed: {str(e)}")


    def handle_segmentation_result(self, result):
        segmented_masks_list, min_val, max_val = result

        # If we received valid segmented masks, update the UI and show them
        if segmented_masks_list:
            self.masks_per_image = segmented_masks_list
            self.binarize_button.setEnabled(True)
            
            # Display the first image and its first mask
            self.show_image_and_mask(0, 0)

            # Show threshold controls if valid min and max values are available
            if min_val is not None and max_val is not None:
                self.show_threshold_controls(min_val, max_val)
            
            self.viewer.status = "Masks generated"
        else:
            self.viewer.status = "Segmentation failed"
            QMessageBox.warning(self, "Segmentation Error", "No segmentation masks were produced.")

    def show_image_and_mask(self, img_idx, rgb_idx):
        pseudo_rgb_image = self.pseudo_rgb_images_per_image[img_idx][rgb_idx]
        mask_set = self.masks_per_image[img_idx][rgb_idx]
        
        # print("Mask set: ", mask_set)

        # Clear previous layers and show the image
        self.viewer.layers.clear()
        self.viewer.add_image(pseudo_rgb_image, rgb=True, name=f"Pseudo-RGB Image {img_idx + 1}-{rgb_idx + 1}")

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


    # Add the show_threshold_controls function back:
    def show_threshold_controls(self, min_val, max_val):
        # Add threshold checkbox and slider
        if not self.threshold_checkbox:
            self.threshold_checkbox = QCheckBox("Apply Threshold", self)
            self.threshold_checkbox.stateChanged.connect(self.toggle_threshold)
            self.layout().addWidget(self.threshold_checkbox)

        if not self.threshold_slider:
            self.threshold_slider = QSlider(Qt.Horizontal, self)
            print("Min and max values: ", int(min_val), int(max_val))
            self.threshold_slider.setMinimum(int(min_val))  # Convert to int for the slider
            self.threshold_slider.setMaximum(int(max_val))
            self.threshold_slider.setVisible(False)
            self.threshold_slider.valueChanged.connect(self.update_masks_with_threshold)
            self.layout().addWidget(self.threshold_slider)

        # Show the checkbox
        self.threshold_checkbox.setVisible(True)

    # Handle segmentation error
    def handle_segmentation_error(self, error_msg):
        QMessageBox.warning(self, "Segmentation Error", f"{error_msg}")
        self.segment_button.setEnabled(True)

    def toggle_threshold(self, state):
        # Show or hide the threshold slider based on the checkbox state
        if state == Qt.Checked:
            self.threshold_slider.setVisible(True)
        else:
            self.threshold_slider.setVisible(False)
            # Update to use self.current_img_idx and self.current_rgb_idx
            self.show_image_and_mask(self.current_img_idx, self.current_rgb_idx)

    def update_masks_with_threshold(self, value):
        # Update the thresholded masks based on the slider value
        upscaled_masks = self.upscaled_masks_per_image[self.current_img_idx]
        if upscaled_masks is not None:
            # print("Threshold value updated to: ", value)
            thresholded_masks = normalize(threshold(upscaled_masks, threshold=value, value=0)).squeeze(1)
            self.masks_per_image[self.current_img_idx][self.current_rgb_idx] = thresholded_masks.cpu()
            # Call show_image_and_mask with current img and rgb indices
            self.show_image_and_mask(self.current_img_idx, self.current_rgb_idx)


    def set_spectral_mixing_enabled(self, enabled):
        self.r_input.setEnabled(enabled)
        self.g_input.setEnabled(enabled)
        self.b_input.setEnabled(enabled)
        self.compute_button.setEnabled(enabled)
