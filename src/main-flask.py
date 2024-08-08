import argparse
import cv2 as cv
import numpy as np
import math
import mediapipe as mp
import paho.mqtt.client as mqtt
import queue
import tensorflow as tf
import time

from keras.applications.resnet import preprocess_input
from keras.applications.mobilenet_v2 import preprocess_input as ppi_mobilenet

from db import ConexionSQLite
from constants import classes
from models import get_model
from record import Record
from utils import get_angle_face, is_blink_deep as is_blink
from visual import chart_bar, chart_plot


parser = argparse.ArgumentParser()
parser.add_argument('--watch', help='Watch stream', type=int, default=0)
parser.add_argument('--delay', help='Speed rate frames', type=int, default=1)

args = parser.parse_args()
is_show = bool(args.watch)
delay = args.delay

path_model_emotions = './models/model_7.tflite'
path_model_eye = './models/model_eye9.tflite'
    
if len(tf.config.list_physical_devices('GPU')) > 0:
    with tf.device('/GPU:0'):
        face_mesh = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        mp_face_mesh = mp.solutions.face_mesh
        mp_drawing = mp.solutions.drawing_utils

        model, input_model, output_model = get_model(path_model_emotions)
        model_eye, input_model_eye, output_model_eye = get_model(path_model_eye, 2)

        print('WORKING GPU')
else:
    face_mesh = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils

    model, input_model, output_model = get_model(path_model_emotions)
    model_eye, input_model_eye, output_model_eye = get_model(path_model_eye, 2)

    print('NOT WORKING CPU')

conexion = ConexionSQLite()
sesion = conexion.get('SELECT id FROM sesion WHERE in_live = 1 LIMIT 1')

rea_pos = 'I'
rea_action = '-'
rea_media = 0
is_init = len(sesion) > 0

sesion_id = sesion[0][0] if is_init else '-'

def on_connect(client, userdata, flags, rc, _):
    if rc == 0:
        print('Conexión exitosa al broker MQTT')
        client.subscribe('action')
        client.subscribe('rea')
        client.subscribe('info')
        client.publish('status', 2)
    else:
        print(f'Error al conectar al broker. Código de retorno: {rc}')

def on_message(client, userdata, msg):
    global sesion_id, is_init
    topic = msg.topic
    msg = msg.payload.decode()
    print(f'Mensaje recibido en el topic \'{topic}\': {msg}')
    if topic == 'action':
        msg = msg.split(',')
        if msg[0] == '0':
            start(client)
            sesion_id = msg[1]
        elif msg[0] == '1':
            is_init = False
            restart()
            client.publish('status', int(is_init))
    if topic == 'info' and msg == '0': 
        client.publish('status', int(is_init))
        client.publish('status', 2)
    if topic == 'rea':
        action_user(msg)

def on_publish(client, userdata, mid, reason_code, properties):
    print('Mensaje publicado con éxito')

def restart():
    global rea_action, rea_pos, rea_media, sesion_id, count_rate
    if not is_init:
        if sesion_id != '-':
            conexion.insert('UPDATE sesion SET in_live = 0 WHERE id = ?', (sesion_id,))
        rea_pos = 'I'
        rea_action = '-'
        rea_media = 0
        sesion_id = '-'
    count_rate = 0

def start(client):
    global is_init
    is_init = not is_init
    client.publish('status', int(is_init))
    restart()

def action_user(msg):
    global rea_pos, rea_action, rea_media
    msg = msg.split(',')
    action, msg = msg[0], msg[1]
    if action == 'position':
        rea_pos = msg
    if action == 'action':
        rea_action = msg
    if action == 'media':
        rea_media = msg

def kill():
    global is_init
    is_init = False
    client.publish('status', int(is_init))
    client.publish('status', 3)
    restart()
    exit()

# Configura el cliente MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect("0.0.0.0", 1883)
client.loop_start()


num_classes = len(classes)
lines_emotions = np.zeros((num_classes,80))
lines_blink = np.zeros((2,80))
prev_blink = (0, time.time())
is_catch = False

# Para determinar cuando registrar en la BD
prev_record = time.time()
# Se determina por ventaneo absoluto
rate_record = 1

# Para determinar cuando limpiar el contador de ojos cerrados
prev_engagement = time.time()
# Se determina por ventaneo relativo
count_close_eye = 0
count_blink = 0
rate_engagement = 20

# Bloque de variables que serán mantenidas durante el rate general
is_blink_g = False
is_close_eye_g = False
is_engagement_g = True
text_head_pos_g = 'F'
blink_rate_s = math.inf
emotions_g = np.zeros(7)
count_rate = 0

queue_ = queue.Queue()
record_processing = Record(queue_, 0.5)
record_processing.start()

w_screen = 940

cap = cv.VideoCapture(0)
# cap = cv.VideoCapture('./videos/test1.mp4')
if not cap.isOpened():
    print('Cannot open camera')
    exit()

def update():
    global count_rate, prev_record, prev_blink, prev_engagement, emotions_g, is_blink_g, is_close_eye_g, is_engagement_g, lines_emotions, lines_blink, is_catch, count_close_eye, count_blink, emotions_plot, emotions_bar, blinks_plot, blink_rate_s, text_head_pos_g, is_init

    while cap.isOpened(): 
        current_time = time.time()
        prev = current_time

        is_range_time = current_time - prev_record > rate_record
        if is_range_time:
            prev_record = current_time

        is_range_engagement = current_time - prev_engagement > rate_engagement
        if is_range_engagement:
            prev_engagement = current_time

        ret, frame = cap.read()
        is_blink_s, is_close_eye_s = 0, 0
        text_head_pos_s, is_engagement_s = 'F', 0,
        pred = np.zeros(7).tolist()

        if ret:
            frame = cv.resize(frame, (frame.shape[1]//1, frame.shape[0]//1))
            img_h, img_w, img_c = frame.shape

            results = face_mesh.process(frame)

            if is_show:
                emotions_bar = chart_bar(np.zeros(num_classes), frame.shape, classes)
                if not is_catch:
                    emotions_plot, lines_emotions = chart_plot(lines_emotions, (img_h, w_screen, img_c), classes, np.zeros(num_classes))
                    blinks_plot, lines_blink = chart_plot(lines_blink, (img_h, w_screen, img_c), classes, np.zeros(2))

            # Check if faces detect
            if results.multi_face_landmarks:
                is_catch = True
                for face_landmarks in results.multi_face_landmarks:
                    xp, yp, _, p1, p2, text_head_pos = get_angle_face(face_landmarks, (img_h, img_w), 15)

                    face_contour = face_landmarks.landmark

                    # Bounds contour face
                    min_x = min(face_contour, key=lambda x: x.x).x
                    max_x = max(face_contour, key=lambda x: x.x).x
                    min_y = min(face_contour, key=lambda y: y.y).y
                    max_y = max(face_contour, key=lambda y: y.y).y

                    x = int(min_x * img_w)
                    y = int(min_y * img_h)
                    x_w = int(max_x * img_w)
                    y_h = int(max_y * img_h)

                    # Crop contour face
                    face_image = frame[y:y_h, x:x_w]

                    try:
                        # Preprocessing image face
                        face_image = cv.cvtColor(face_image, cv.COLOR_BGR2GRAY)
                        face_image = cv.merge([face_image, face_image, face_image])
                        resized_frame = preprocess_input(cv.resize(face_image, (48,48)))
                        input_image = np.expand_dims(resized_frame, axis=0).astype('float32')

                        if is_show:
                            cv.imshow('Face', input_image[0])

                        # Inferecence model emotions                    
                        model.set_tensor(input_model[0]['index'], input_image)
                        model.invoke()
                        output_data = model.get_tensor(output_model[0]['index'])
                        class_ = np.argmax(output_data)
                        prediction = classes[class_]                                  

                        # Detect blink
                        blink_rate, is_blink_, text_blink, is_close_eye, prev_time, _, eye_r, eye_l = is_blink(face_contour, prev_blink, frame, model_eye, input_model_eye, output_model_eye, ppi_mobilenet, 0.3)
                        prev_blink = (blink_rate, prev_time)

                        if is_show:
                            cv.imshow('eye', np.concatenate((eye_r, eye_l), axis=1))

                        count_blink += is_blink_
                        count_close_eye += is_close_eye

                        if is_show:
                            emotions_bar = chart_bar(output_data[0], frame.shape, classes)
                            blinks_plot, lines_blink = chart_plot(lines_blink, (img_h, w_screen, img_c), classes, np.array([is_blink_, blink_rate]))
                            emotions_plot, lines_emotions = chart_plot(lines_emotions, (img_h, w_screen, img_c), classes, output_data[0])

                        # Detect engagement
                        is_positive = class_ in [classes.index('HAPPY'), classes.index('NEUTRAL'), classes.index('SURPRISE')]

                        if is_positive and (count_blink < 15 or count_close_eye < 2) and text_head_pos == 'F':
                            is_engagement = True
                        elif not is_positive and count_blink >= 15 and (text_head_pos == 'U' or text_head_pos == 'D' or text_head_pos == 'L' or text_head_pos == 'R'):
                            is_engagement = False
                        else: 
                            is_engagement = False

                        is_blink_g |= is_blink_
                        is_close_eye_g |= is_close_eye
                        is_engagement_g &= is_engagement
                        blink_rate_s = blink_rate if is_blink_ else blink_rate_s
                        text_head_pos_g = text_head_pos if text_head_pos != 'F' else text_head_pos_g

                        emotions_g = np.maximum(emotions_g, output_data[0])

                        if is_show:
                            cv.line(frame, p1, p2, (255,0,0), 3)
                            cv.rectangle(frame, (x, y), (x_w, y_h), (0,255,0), 2)
                            cv.putText(frame, f'Eye blink: {text_blink} | {count_blink} | {count_close_eye}', (10,90), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                            cv.putText(frame, f'Class: {prediction}', (10,30), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                            cv.putText(frame, f'Engagement: {is_engagement} | {text_head_pos}', (10,60), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                        if is_range_time:
                            pred = emotions_g.tolist()
                            is_blink_s = is_blink_g                            
                            is_close_eye_s = is_close_eye_g
                            text_head_pos_s = text_head_pos_g
                            is_engagement_s = is_engagement_g
                            blink_rate_s = blink_rate if blink_rate_s == math.inf else blink_rate_s
                            if is_init:
                                queue_.put((sesion_id, *pred, float(blink_rate_s), text_head_pos, xp, yp, int(is_engagement_g), is_close_eye_g, is_blink_g, rea_pos, rea_action, rea_media, int(time.time()), count_rate))

                            is_blink_g = False
                            is_close_eye_g = False
                            is_engagement_g = True
                            text_head_pos_g = 'F'
                            emotions_g = np.zeros(7)

                        if is_range_engagement:
                            count_blink = 0
                            count_close_eye = 0
                        
                    except Exception as e:
                        print(e)
            else: is_catch = False

            if is_range_time:
                blink_rate_s = 0 if blink_rate_s == math.inf else blink_rate_s
                client.publish('blink', f'{count_rate},{is_blink_s},{is_close_eye_s},{round(blink_rate_s, 2)};')
                client.publish('head', f'{count_rate},{text_head_pos_s};')
                client.publish('engagement', f'{count_rate},{is_engagement_s};')
                client.publish('emotions', f'{count_rate},{",".join([str(round(x, 2)) for x in pred])};')                

                blink_rate_s = math.inf
                count_rate += rate_record

        last = time.time()
        total_time = last - prev
        fps = int(1//total_time)

        if is_show:
            cv.putText(frame, f'FPS: {fps}', (img_w - 145, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            frame = np.concatenate((frame, emotions_bar), axis=1)
            frame = np.concatenate((frame, emotions_plot), axis=0)
            frame = np.concatenate((frame, blinks_plot), axis=0)

            cv.imshow('FER', frame)

            if cv.waitKey(delay) & 0xFF == ord('q'):
                break
        else: time.sleep(delay/1000)

    cap.release()
    record_processing.stop()

    kill()

try:
    update()
except KeyboardInterrupt as e:
    kill()