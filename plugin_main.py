from .csv_viewer import CsvViewerDockWidget
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import os

class CsvViewerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dock_widget = None
        self.action = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Create dock widget
        self.dock_widget = CsvViewerDockWidget(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        
        # Create action
        icon_path = os.path.join(os.path.dirname(__file__), 'logo.webp')
        self.action = QAction(
            QIcon(icon_path),
            "CSV Viewer",
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        self.action.setChecked(False)
        self.action.triggered.connect(self.toggle_dock_widget)
        
        # Add menu item
        self.iface.addPluginToMenu("CSV Viewer", self.action)
        # Add to toolbar
        self.iface.addToolBarIcon(self.action)
        
        # dock widget을 처음에 숨김
        self.dock_widget.hide()

    def toggle_dock_widget(self):
        """Show/hide the dock widget."""
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
            self.action.setChecked(False)
        else:
            self.dock_widget.show()
            self.action.setChecked(True)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("CSV Viewer", self.action)
        self.iface.removeToolBarIcon(self.action)
        
        if self.dock_widget:
            self.dock_widget.close()
            self.dock_widget = None 