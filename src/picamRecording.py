#!/usr/bin/python3
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
from picamera2.previews.qt import QGlPicamera2


frame_rate = 60
picam2_list = []
config_list = []
filenames = [
    'left',
    'right'
]
recording = False
app = QApplication([])
layout_preview = QHBoxLayout()
layout_info = QHBoxLayout()
def post_callback(request):
    label = QLabel()
    label.setFixedWidth(400)
    label.setAlignment(QtCore.Qt.AlignTop)
    label.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))
    layout_info.addWidget(label)

camara_list = Picamera2.global_camera_info()

for i in range(0,len(camara_list)):
    picam2_list.append(Picamera2(i))
#   config_list.append(picam2_list[i].still_configuration())
#    picam2_list[i].post_callback = post_callback
    picam2_list[i].configure(picam2_list[i].create_video_configuration(main={"size": (1920, 1080)},lores={"size": (1280,720)}))
    picam2_list[i].set_controls({"AfMode": 2 ,"AfTrigger": 0})
    layout_preview.addWidget( QGlPicamera2(picam2_list[i], width=800, height=480, keep_ar=False), 50)


def on_button_clicked():
    global recording
    if not recording:
        filename = f"Videos/{filenames[i]}{int(time.time())}.mp4"
        encoder = H264Encoder(10000000)
        output = FfmpegOutput(filename)
        for picam2 in picam2_list:
            picam2.start_encoder(encoder, output, quality=Quality.HIGH)

        button.setText("Stop recording")
        recording = True
    else:
        for picam2 in picam2_list:
            picam2.stop_encoder()

        button.setText("Start recording")
        recording = False

button = QPushButton("Start recording")
button.clicked.connect(on_button_clicked)

layout_base = QVBoxLayout()
layout_base.addWidget(button)
layout_base.addLayout(layout_preview, 100)
layout_base.addLayout(layout_info, 50)


window = QWidget()
window.setWindowTitle("Video Recording App")
window.resize(1200, 720)
window.setLayout(layout_base)

for picam2 in picam2_list:
    picam2.start()

window.show()
app.exec()