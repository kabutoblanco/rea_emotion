import cv2 as cv
import math
import numpy as np
import time

from constants import mesh_annotation


def is_blink_deep(face_contour, prev_blink, frame, model, input, output, ppi, threshold=0.5):
    prev_blink, prev_time = prev_blink
    img_h, img_w, _ = frame.shape

    leftEyeOut = mesh_annotation["leftEyeOut"]
    rightEyeOut = mesh_annotation["rightEyeOut"]

    leftEyeOut = [face_contour[idx] for idx in leftEyeOut]
    rightEyeOut = [face_contour[idx] for idx in rightEyeOut]

    min_x_l = min(leftEyeOut, key=lambda x: x.x).x
    max_x_l = max(leftEyeOut, key=lambda x: x.x).x
    min_y_l = min(leftEyeOut, key=lambda y: y.y).y
    max_y_l = max(leftEyeOut, key=lambda y: y.y).y

    min_x_r = min(rightEyeOut, key=lambda x: x.x).x
    max_x_r = max(rightEyeOut, key=lambda x: x.x).x
    min_y_r = min(rightEyeOut, key=lambda y: y.y).y
    max_y_r = max(rightEyeOut, key=lambda y: y.y).y

    x_ll, y_ll = int(min_x_l * img_w), int(min_y_l * img_h)
    x_lh, y_lh = int(max_x_l * img_w), int(max_y_l * img_h)
    cv.rectangle(frame, (x_ll, y_ll), (x_lh, y_lh), (0,255,255), 2) 

    x_rl, y_rl = int(min_x_r * img_w), int(min_y_r * img_h)
    x_rh, y_rh = int(max_x_r * img_w), int(max_y_r * img_h)
    cv.rectangle(frame, (x_rl, y_rl), (x_rh, y_rh), (0,255,255), 2) 

    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # alpha = 2.0  # Constrats
    # beta = 0.5  # Brightness
    # frame = np.clip(alpha * frame + beta, 0, 255).astype(np.uint8)

    # frame = cv.merge((frame, frame, frame))

    eye_l_ = frame[y_ll:y_lh, x_ll:x_lh]
    eye_l_ = cv.resize(eye_l_, (48,48))
    eye_l = ppi(eye_l_)

    eye_r_ = frame[y_rl:y_rh, x_rl:x_rh]
    eye_r_ = cv.resize(eye_r_, (48,48))
    eye_r = ppi(eye_r_)

    eyes = [eye_r, eye_l]

    model.set_tensor(input[0]['index'], eyes)
    model.invoke()
    output_data_eye = model.get_tensor(output[0]['index'])
    blink_rate = np.average(output_data_eye)

    text_blink = 'No'
    is_blink = 0
    if blink_rate < threshold and prev_blink >= threshold:
        text_blink = 'Yes'
        is_blink = 1

    current_time = time.time()
    is_close_eye = 0
    if current_time - prev_time > 5 and blink_rate < threshold and prev_blink < threshold:
        prev_time = current_time
        is_close_eye = 1
    elif blink_rate < threshold and prev_blink >= threshold:
        prev_time = current_time

    return blink_rate, is_blink, text_blink, is_close_eye, prev_time, None, eye_l, eye_r

def is_blink_geometry(face_contour, prev_blink, threshold=0.4):
    prev_blink, prev_time = prev_blink
    eye_up_l1 = face_contour[160]
    eye_down_l1 = face_contour[144]
    eye_up_l2 = face_contour[158]
    eye_down_l2 = face_contour[153]
    eye_left_l = face_contour[33]
    eye_right_l = face_contour[133]

    eye_l_h1 = get_distance(eye_down_l1, eye_up_l1)
    eye_l_h2 = get_distance(eye_down_l2, eye_up_l2)
    eye_l_w = get_distance(eye_left_l, eye_right_l)

    eye_up_r1 = face_contour[387]
    eye_down_r1 = face_contour[373]
    eye_up_r2 = face_contour[385]
    eye_down_r2 = face_contour[380]
    eye_left_r = face_contour[362]
    eye_right_r = face_contour[263]

    eye_r_h1 = get_distance(eye_down_r1, eye_up_r1)
    eye_r_h2 = get_distance(eye_down_r2, eye_up_r2)
    eye_r_w = get_distance(eye_left_r, eye_right_r)

    blink_l = (eye_l_h1 + eye_l_h2) / eye_l_w
    blink_r = (eye_r_h1 + eye_r_h2) / eye_r_w
    blink_rate = (blink_l + blink_r) / 2

    metric = (blink_l, blink_r)

    text_blink = 'No'
    is_blink = 0
    if blink_rate < threshold and prev_blink >= threshold:
        text_blink = 'Yes'
        is_blink = 1

    current_time = time.time()
    is_close_eye = 0
    if current_time - prev_time > 5 and blink_rate < threshold and prev_blink < threshold:
        prev_time = current_time
        is_close_eye = 1
    elif blink_rate < threshold and prev_blink >= threshold:
        prev_time = current_time

    return blink_rate, is_blink, text_blink, is_close_eye, metric

def get_distance(point1, point2):
    x1 = point1.x
    y1 = point1.y

    x2 = point2.x
    y2 = point2.y

    p1 = (x1 - x2)**2
    p2 = (y1 - y2)**2

    return math.sqrt(p1 + p2)

def get_angle_face(face_landmarks, bounds, threshold=10):
    img_h, img_w = bounds
    face_2d = []
    face_3d = []
    
    for idx, lm in enumerate(face_landmarks.landmark):
        if idx in [33, 263, 1, 61, 291, 199]:
            if idx == 1:
                nose_2d = (lm.x * img_w, lm.y * img_h)
                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z)
            x, y = int(lm.x * img_w),int(lm.y * img_h)

            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])

    #Get 2d Coord
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    focal_length = 1 * img_w

    cam_matrix = np.array([[focal_length, 0, img_h/2], [0, focal_length,img_w/2], [0, 0, 1]])
    distortion_matrix = np.zeros((4, 1),dtype=np.float64)

    _, rotation_vec, _ = cv.solvePnP(face_3d, face_2d, cam_matrix, distortion_matrix)

    # Getting rotational of face
    rmat, _ = cv.Rodrigues(rotation_vec)

    angles, _, _, _, _, _ = cv.RQDecomp3x3(rmat)

    x = angles[0] * 360
    y = angles[1] * 360
    z = angles[2] * 360

    p1 = (int(nose_2d[0]), int(nose_2d[1]))
    p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] -x * 10))
    
    if y < threshold * -1:
        text = 'L'
    elif y > threshold:
        text = 'R'
    elif x < threshold * -1:
        text = 'D'
    elif x > threshold:
        text = 'U'
    else:
        text = 'F'

    return x, y, z, p1, p2, text