#!/usr/bin/python3
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox,
                             QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QSlider, QSpinBox,
                             QTabWidget, QVBoxLayout, QWidget)



class panZoomDisplay(QWidget):
    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(201, 151)
        self.scale = 200 / picam2.camera_properties["ScalerCropMaximum"][2]
        self.zoom_level_ = 1.0
        self.max_zoom = 7.0
        self.zoom_step = 0.1

    @property
    def zoom_level(self):
        return self.zoom_level_

    @zoom_level.setter
    def zoom_level(self, val):
        if val != self.zoom_level:
            self.zoom_level_ = val
            self.setZoom()

    def setZoomLevel(self, val):
        self.zoom_level = val

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        full_img = picam2.camera_properties["ScalerCropMaximum"]
        self.scale = 200 / full_img[2]
        # Whole frame
        scaled_full_img = [int(i * self.scale) for i in full_img]
        origin = scaled_full_img[:2]
        scaled_full_img[:2] = [0, 0]
        painter.drawRect(*scaled_full_img)
        # Cropped section
        scaled_scaler_crop = [int(i * self.scale) for i in scaler_crop]
        scaled_scaler_crop[0] -= origin[0]
        scaled_scaler_crop[1] -= origin[1]
        painter.drawRect(*scaled_scaler_crop)
        painter.end()
        self.updated.emit()

    def draw_centered(self, pos):
        global scaler_crop
        center = [int(i / self.scale) for i in pos]
        full_img = picam2.camera_properties["ScalerCropMaximum"]
        w = scaler_crop[2]
        h = scaler_crop[3]
        x = center[0] - w // 2 + picam2.camera_properties["ScalerCropMaximum"][0]
        y = center[1] - h // 2 + picam2.camera_properties["ScalerCropMaximum"][1]
        new_scaler_crop = [x, y, w, h]

        # Check still within bounds
        new_scaler_crop[1] = max(new_scaler_crop[1], full_img[1])
        new_scaler_crop[1] = min(new_scaler_crop[1], full_img[1] + full_img[3] - new_scaler_crop[3])
        new_scaler_crop[0] = max(new_scaler_crop[0], full_img[0])
        new_scaler_crop[0] = min(new_scaler_crop[0], full_img[0] + full_img[2] - new_scaler_crop[2])
        scaler_crop = tuple(new_scaler_crop)
        picam2.controls.ScalerCrop = scaler_crop
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        pos = (pos.x(), pos.y())
        self.draw_centered(pos)

    def setZoom(self):
        global scaler_crop
        if self.zoom_level < 1:
            self.zoom_level = 1.0
        if self.zoom_level > self.max_zoom:
            self.zoom_level = self.max_zoom
        factor = 1.0 / self.zoom_level
        full_img = picam2.camera_properties["ScalerCropMaximum"]
        current_center = (scaler_crop[0] + scaler_crop[2] // 2, scaler_crop[1] + scaler_crop[3] // 2)
        w = int(factor * full_img[2])
        h = int(factor * full_img[3])
        x = current_center[0] - w // 2
        y = current_center[1] - h // 2
        new_scaler_crop = [x, y, w, h]
        # Check still within bounds
        new_scaler_crop[1] = max(new_scaler_crop[1], full_img[1])
        new_scaler_crop[1] = min(new_scaler_crop[1], full_img[1] + full_img[3] - new_scaler_crop[3])
        new_scaler_crop[0] = max(new_scaler_crop[0], full_img[0])
        new_scaler_crop[0] = min(new_scaler_crop[0], full_img[0] + full_img[2] - new_scaler_crop[2])
        scaler_crop = tuple(new_scaler_crop)
        picam2.controls.ScalerCrop = scaler_crop
        self.update()

    def wheelEvent(self, event):
        zoom_dir = np.sign(event.angleDelta().y())
        self.zoom_level += zoom_dir * self.zoom_step
        self.setZoom()
        # If desired then also center the zoom on the pointer
        # self.draw_centered((event.position().x(), event.position().y()))



class panTab(QWidget):
    def __init__(self):
        super().__init__()
        # Pan/Zoom
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.label = QLabel((
            "Pan and Zoom Controls\n"
            "To zoom in/out, scroll up/down in the display below\n"
            "To pan, click and drag in the display below"),
            alignment=Qt.AlignCenter)
        self.zoom_text = QLabel("Current Zoom Level: 1.0", alignment=Qt.AlignCenter)
        self.pan_display = panZoomDisplay()
        self.pan_display.updated.connect(lambda: self.zoom_text.setText(
            f"Current Zoom Level: {self.pan_display.zoom_level:.1f}x"))

        self.layout.addRow(self.label)
        self.layout.addRow(self.zoom_text)
        self.layout.addRow(self.pan_display)
        self.layout.setAlignment(self.pan_display, Qt.AlignCenter)

