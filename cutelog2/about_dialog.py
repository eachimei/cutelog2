from qtpy.QtWidgets import QDialog
from qtpy.uic import loadUi

from .config import CONFIG
from .resources_loader import get_ui_path


class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.ui = loadUi(get_ui_path("about_dialog.ui"), baseinstance=self)
        self.nameLabel.setText(CONFIG.full_name)
