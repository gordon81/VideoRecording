#!/usr/bin/python3
import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget,QTabWidget)

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
from picamera2.previews.qt import QGlPicamera2

from panZoom import panTab

frame_rate = 60
picam2_list = []
config_list = []
filenames = [
    'left',
    'right'
]
cam = 1
recording = False

camara_list = Picamera2.global_camera_info()
for i in range(len(camara_list)):
    picam2_list.append(Picamera2(i))
    cam = cam + 1

app = QApplication([])
layout_preview = QHBoxLayout()
layout_info = QHBoxLayout()

for picam2 in picam2_list:
    picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)}, lores={"size": (1920, 1080)}))
    picam2.set_controls({"AfMode": 2, "AfTrigger": 0})
    layout_width = 100 // cam
    layout_preview.addWidget(QGlPicamera2(picam2, width=800, height=480, keep_ar=False),layout_width )

def on_button_clicked():
    global recording
    if not recording:
        i = 0
        for picam2 in picam2_list:
            filename = f"Videos/{filenames[i]}{int(time.time())}.mp4"
            encoder = H264Encoder(10000000)
            output = FfmpegOutput(filename, audio=True)
            picam2.start_encoder(encoder, output, quality=Quality.VERY_HIGH)
            i=i+1

        button.setText("Stop recording")
        recording = True
    else:
        for picam2 in picam2_list:
            picam2.stop_encoder()

        button.setText("Start recording")
        recording = False

button = QPushButton("Start recording")
button.clicked.connect(on_button_clicked)

pan_zoom_list = []
for picam2 in picam2_list:
    pan_zoom_list.append( panTab(picam2))

layout_zoom = QHBoxLayout()
for pan_tab in pan_zoom_list:
    layout_zoom.addWidget(pan_tab,25)

layout_base = QVBoxLayout()
layout_base.addWidget(button)
layout_base.addLayout(layout_preview, 100)
layout_base.addLayout(layout_info, 50)
layout_base.addLayout(layout_zoom,100)

window = QWidget()
window.setWindowTitle("Video Recording App")
window.resize(1200, 720)
window.setLayout(layout_base)


p=0
for picam2 in picam2_list:
    picam2.start()
    pan_zoom_list[p].pan_display.update()
    p = p+1

window.show()
app.exec()






