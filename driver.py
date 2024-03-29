# import tensorflow
# pip install cv2-contrib-package
#python-socketio==4.6.1
# python-engineio==3.13.2

import socketio
import eventlet
from flask import Flask
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

sio = socketio.Server()
app = Flask(__name__)

speed_limit = 17
print(speed_limit)

def preprocess_img(img):
    img = img[60:135, :, :]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img / 255
    return img

def send_control(steering_angle, throttle):
    sio.emit('steer', data={'steering_angle': steering_angle.__str__(), 'throttle': throttle.__str__()})

@sio.on('telemetry')
def telemetry(sid, data):
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = preprocess_img(image)
    image = np.array([image])
    speed = float(data['speed'])
    steering_angle = float(model.predict(image)) * 0.65
    throttle = 1.0 - (speed / speed_limit)
    send_control(steering_angle, throttle)

@sio.on('connect')
def connect(sid, environ):
    print('Connected')
    send_control(0, 0)


if __name__ == '__main__':
    # same as Models/model_epoch20_batch200_steps700.h5
    model = load_model('final_model.h5')
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)