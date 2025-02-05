import napari
from tkinter import Tk
from qtpy.QtWidgets import QDockWidget
from qtpy import QtGui
from app.ui import CustomWidget
import os

def main():
    root = Tk()
    root.withdraw()

    # Initialize the viewer
    viewer = napari.Viewer()
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(project_root, 'assets', 'logo2.png')
    bg_logo_path = os.path.join(project_root, 'assets', 'logo.png')
    
    if os.path.exists(bg_logo_path):
        viewer.open(bg_logo_path, rgb=True, name='Logo')
    else:
        # print("Logo image not found at:", bg_logo_path)
        print("Logo image not found at:", bg_logo_path)
        viewer.text_overlay.text = "Welcome to GSense"


    # Add Save Selected Layer button to the layer list dock widget
    layer_list_dock = viewer.window._qt_window.findChild(QDockWidget, "layer list")
    layer_controls_dock = viewer.window._qt_window.findChild(QDockWidget, "layer controls")

    # Hide Layer List and Controls initially
    layer_list_dock.setVisible(False)
    layer_controls_dock.setVisible(False)

    viewer.window._qt_window.setWindowTitle("GSense")
    viewer.window._qt_window.setWindowIcon(QtGui.QIcon(logo_path))

    # Add custom widget for batch image loading, spectral mixing, and segmentation
    channel_selection_widget = CustomWidget(viewer, layer_list_dock, layer_controls_dock)
    viewer.window.add_dock_widget(channel_selection_widget, area='right', name='Tools')

    napari.run()

if __name__ == "__main__":
    main()
