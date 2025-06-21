import os
import sys
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QCheckBox
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

BLOCK_SIZE = 135168  # 0x21000
EXPECTED_SIZE = 138412032  # 0x8400000

# Use bundled resource path
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# File writer
def write_binary_section(target_file, source_file, seek_blocks):
    offset = BLOCK_SIZE * seek_blocks
    with open(source_file, 'rb') as sf:
        data = sf.read()
    with open(target_file, 'r+b') as tf:
        tf.seek(offset)
        tf.write(data)

# Drag-and-drop input
from PyQt6.QtWidgets import QLineEdit
class DragDropLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.setText(urls[0].toLocalFile())

# Main GUI
class PatchGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MR33 NAND Image Patcher")
        self.setFixedSize(400, 400)

        layout = QGridLayout()
        self.setLayout(layout)

        self.infile_path = self.add_row(layout, 0, "Input NAND image:", False)
        self.outfile_path = self.add_row(layout, 1, "Output patched image:", True)

        self.use_art_checkbox = QCheckBox("Apply ART patch (block 88)")
        layout.addWidget(self.use_art_checkbox, 2, 0, 1, 3)

        self.run_button = QPushButton("Run Patching")
        self.run_button.clicked.connect(self.run_patching)
        layout.addWidget(self.run_button, 3, 0, 1, 3)

    def add_row(self, layout, row, label_text, save_mode):
        label = QLabel(label_text)
        path_edit = DragDropLineEdit()
        browse_btn = QPushButton("Browse")

        def choose_file():
            if save_mode:
                file, _ = QFileDialog.getSaveFileName(self, f"Select {label_text}")
            else:
                file, _ = QFileDialog.getOpenFileName(self, f"Select {label_text}")
            if file:
                path_edit.setText(file)

        browse_btn.clicked.connect(choose_file)
        layout.addWidget(label, row, 0)
        layout.addWidget(path_edit, row, 1)
        layout.addWidget(browse_btn, row, 2)
        return path_edit

    def run_patching(self):
        try:
            infile = self.infile_path.text()
            outfile = self.outfile_path.text()
            use_art = self.use_art_checkbox.isChecked()

            self.validate_inputs(infile, outfile)

            shutil.copyfile(infile, outfile)
            write_binary_section(outfile, resource_path("ubootmr332012.bin"), 56)
            write_binary_section(outfile, resource_path("ubimr33.bin"), 96)
            if use_art:
                write_binary_section(outfile, resource_path("art_repaired.bin"), 88)

            QMessageBox.information(self, "Success", "Patching completed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def validate_inputs(self, infile, outfile):
        if not os.path.exists(infile):
            raise FileNotFoundError("Input NAND image not found.")
        if not outfile:
            raise ValueError("No output file selected.")
        if os.path.abspath(infile) == os.path.abspath(outfile):
            raise ValueError("Input and output files cannot be the same.")
        if os.path.exists(outfile):
            raise FileExistsError("Output file already exists.")
        if os.path.getsize(infile) != EXPECTED_SIZE:
            raise ValueError("Input image size is invalid. Should be 138412032 bytes.")

# Enable dark mode
def enable_dark_theme(app):
    dark = QPalette()
    dark.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    enable_dark_theme(app)
    gui = PatchGUI()
    gui.show()
    sys.exit(app.exec())
