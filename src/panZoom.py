#!/usr/bin/python3
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QFormLayout, QLabel,
                             QWidget)
import numpy as np


class panZoomDisplay(QWidget):
    updated = pyqtSignal()

    def __init__(self,picam2):
        super().__init__()
        self.picam2 = picam2
        self.scaler_crop = self.picam2.camera_properties["ScalerCropMaximum"]
        self.setMinimumSize(201, 151)
        self.scale = 200 / self.picam2.camera_properties["ScalerCropMaximum"][2]
        self.zoom_level_ = 1.0
        self.max_zoom = 10.0
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
        full_img = self.picam2.camera_properties["ScalerCropMaximum"]
        self.scale = 200 / full_img[2]
        # Whole frame
        scaled_full_img = [int(i * self.scale) for i in full_img]
        origin = scaled_full_img[:2]
        scaled_full_img[:2] = [0, 0]
        painter.drawRect(*scaled_full_img)
        # Cropped section
        print(self.scaler_crop)
        scaled_scaler_crop = [int(i * self.scale) for i in self.scaler_crop]
        scaled_scaler_crop[0] -= origin[0]
        scaled_scaler_crop[1] -= origin[1]
        painter.drawRect(*scaled_scaler_crop)
        painter.end()
        self.updated.emit()

    def draw_centered(self, pos):
        center = [int(i / self.scale) for i in pos]
        full_img = self.picam2.camera_properties["ScalerCropMaximum"]
        w = self.scaler_crop[2]
        h = self.scaler_crop[3]
        x = center[0] - w // 2 + self.picam2.camera_properties["ScalerCropMaximum"][0]
        y = center[1] - h // 2 + self.picam2.camera_properties["ScalerCropMaximum"][1]
        new_scaler_crop = [x, y, w, h]

        # Check still within bounds
        new_scaler_crop[1] = max(new_scaler_crop[1], full_img[1])
        new_scaler_crop[1] = min(new_scaler_crop[1], full_img[1] + full_img[3] - new_scaler_crop[3])
        new_scaler_crop[0] = max(new_scaler_crop[0], full_img[0])
        new_scaler_crop[0] = min(new_scaler_crop[0], full_img[0] + full_img[2] - new_scaler_crop[2])
        self.scaler_crop = tuple(new_scaler_crop)
        self.picam2.controls.ScalerCrop = self.scaler_crop
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        pos = (pos.x(), pos.y())
        self.draw_centered(pos)

    def setZoom(self):
        if self.zoom_level < 1:
            self.zoom_level = 1.0
        if self.zoom_level > self.max_zoom:
            self.zoom_level = self.max_zoom
        factor = 1.0 / self.zoom_level
        full_img = self.picam2.camera_properties["ScalerCropMaximum"]
        current_center = (self.scaler_crop[0] + self.scaler_crop[2] // 2, self.scaler_crop[1] + self.scaler_crop[3] // 2)
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
        self.scaler_crop = tuple(new_scaler_crop)
        self.picam2.controls.ScalerCrop = self.scaler_crop
        self.update()

    def wheelEvent(self, event):
        zoom_dir = np.sign(event.angleDelta().y())
        self.zoom_level += zoom_dir * self.zoom_step
        self.setZoom()
        # If desired then also center the zoom on the pointer
        # self.draw_centered((event.position().x(), event.position().y()))



class panTab(QWidget):
    def __init__(self, picam2):
        super().__init__()
        # Pan/Zoom
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.picam2 = picam2

        self.label = QLabel((
            "Pan and Zoom Controls\n"
            "To zoom in/out, scroll up/down in the display below\n"
            "To pan, click and drag in the display below"),
            alignment=Qt.AlignCenter)
        self.zoom_text = QLabel("Current Zoom Level: 1.0", alignment=Qt.AlignCenter)
        self.pan_display = panZoomDisplay(self.picam2)
        self.pan_display.updated.connect(lambda: self.zoom_text.setText(
            f"Current Zoom Level: {self.pan_display.zoom_level:.1f}x"))

        self.layout.addRow(self.label)
        self.layout.addRow(self.zoom_text)
        self.layout.addRow(self.pan_display)
        self.layout.setAlignment(self.pan_display, Qt.AlignCenter)

