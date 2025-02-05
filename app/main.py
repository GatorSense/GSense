import napari
from qtpy.QtWidgets import QDockWidget
from qtpy import QtGui
from app.ui import CustomWidget
from pathlib import Path

def main():
    # Initialize the viewer
    viewer = napari.Viewer()

    project_root = Path(__file__).resolve().parent.parent  
    logo_path = project_root / 'assets' / 'logo2.png'
    bg_logo_path = project_root / 'assets' / 'logo.png'

    print("Project root:", project_root)
    print(f"Looking for logo at: {bg_logo_path}")

    if bg_logo_path.exists():
        viewer.open(str(bg_logo_path), rgb=True, name='Logo')
    else:
        print("Logo image not found at:", bg_logo_path)
        viewer.text_overlay.text = "Welcome to GSense"

    # Add Save Selected Layer button to the layer list dock widget
    layer_list_dock = viewer.window._qt_window.findChild(QDockWidget, "layer list")
    layer_controls_dock = viewer.window._qt_window.findChild(QDockWidget, "layer controls")

    # Hide Layer List and Controls initially
    layer_list_dock.setVisible(False)
    layer_controls_dock.setVisible(False)

    viewer.window._qt_window.setWindowTitle("GSense")

    # Set the window icon
    viewer.window._qt_window.setWindowIcon(QtGui.QIcon(str(logo_path)))

    # Add custom widget for batch image loading, spectral mixing, and segmentation
    channel_selection_widget = CustomWidget(viewer, layer_list_dock, layer_controls_dock)
    viewer.window.add_dock_widget(channel_selection_widget, area='right', name='Tools')

    napari.run()

if __name__ == "__main__":
    main()
