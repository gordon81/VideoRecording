#!/usr/bin/python3
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
from picamera2.previews.qt import QGlPicamera2


def post_callbackA(request):
    labelA.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))
    
def post_callbackB(request):
    labelB.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))

frame_rate = 60
filenameA = f"Videos/left{int(time.time())}.mp4"
picam2a = Picamera2(0)
picam2a.post_callback = post_callbackA
picam2a.configure(picam2a.create_video_configuration(main={"size": (1920, 1080)},lores={"size": (1280,720)}))
picam2a.set_controls({"AfMode": 2 ,"AfTrigger": 0})
filenameB = f"Videos/right{int(time.time())}.mp4"
picam2b = Picamera2(1)
picam2b.post_callback = post_callbackB
picam2b.configure(picam2b.create_video_configuration(main={"size": (1920, 1080)},lores={"size": (1280,720)}))
picam2b.set_controls({"AfMode": 2 ,"AfTrigger": 0})

app = QApplication([])


def on_button_clicked():
    global recording
    if not recording:
        encoderA = H264Encoder(10000000)
        outputA = FfmpegOutput(filenameA)
        picam2a.start_encoder(encoderA, outputA, quality=Quality.HIGH)
        
        encoderB = H264Encoder(10000000)
        outputB = FfmpegOutput(filenameB)
        picam2b.start_encoder(encoderB, outputB, quality=Quality.HIGH)
        
        button.setText("Stop recording")
        recording = True
    else:
        picam2a.stop_encoder()
        picam2b.stop_encoder()
        button.setText("Start recording")
        recording = False


qpicamera2a = QGlPicamera2(picam2a, width=800, height=480, keep_ar=False)
qpicamera2b = QGlPicamera2(picam2b, width=800, height=480, keep_ar=False)
button = QPushButton("Start recording")
button.clicked.connect(on_button_clicked)
labelA = QLabel()
labelB = QLabel()
window = QWidget()
window.setWindowTitle("Video Recording App")
recording = False

labelA.setFixedWidth(400)
labelB.setFixedWidth(400)
labelA.setAlignment(QtCore.Qt.AlignTop)
labelB.setAlignment(QtCore.Qt.AlignTop)
layout_h = QHBoxLayout()
layout_c = QHBoxLayout()
layout_v = QVBoxLayout()
layout_c.addWidget(labelA)
layout_c.addWidget(labelB)
layout_v.addWidget(button)
layout_h.addWidget(qpicamera2a, 50)
layout_h.addWidget(qpicamera2b, 50)
layout_v.addLayout(layout_h, 100)
layout_v.addLayout(layout_c, 50)
window.resize(1200, 720)
window.setLayout(layout_v)

picam2a.start()
picam2b.start()
window.show()
app.exec()
