import time

import cv2
import numpy as np
import socket

from arduino import Arduino
from road_utils import *
import pickle
import struct



def is_car_stopped(data, threshold=4, stability_count=45):
    """
    Определяет, остановлена ли машина на основе показаний "left" и "right".

    :param data: Список кортежей с показаниями (left, right)
    :param threshold: Максимальное изменение для определения остановки
    :param stability_count: Количество последовательных измерений, которые должны быть стабильными
    :return: True, если машина остановлена, иначе False
    """
    stable_count = 0

    for i in range(1, len(data)):
        left_change = abs(data[i][0] - data[i - 1][0])
        right_change = abs(data[i][1] - data[i - 1][1])

        if left_change <= threshold and right_change <= threshold:
            stable_count += 1
        else:
            stable_count = 0  # Сброс, если изменения превышают порог

        if stable_count >= stability_count:
            return True  # Машина остановлена

    return False  # Машина не остановлена



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.4.12', 8080))

DIST_METER = 1825  # ticks to finish 1m
CAR_SPEED = 1558         #1555
THRESHOLD = 200
CAMERA_ID = '/dev/video0'
ARDUINO_PORT = '/dev/ttyUSB0'


encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

GO = 'GO'
STOP = 'STOP'
CROSS_STRAIGHT = 'CROSS_STRAIGHT'
CROSS_RIGHT = 'CROSS_RIGHT'
CROSS_LEFT = 'CROSS_LEFT'
_CROSS_LEFT_STRAIGHT = '_CROSS_LEFT_STRAIGHT'
_CROSS_LEFT_LEFT = '_CROSS_LEFT_LEFT'
_CROSS_LEFT_STRAIGHT_AGAIN = '_CROSS_LEFT_STRAIGHT_AGAIN'

PREV_SUBSTATE = None
SUBSTATE = None



START_ACTION = False

STATE = GO
PREV_STATE = None

try:
    arduino = Arduino(ARDUINO_PORT, baudrate=115_200, timeout=0.1)

    time.sleep(2)
    # arduino.set_speed(CAR_SPEED + 5)
    # time.sleep(0.2)


except:
    pass
# print("Arduino port:", arduino.port)


cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print('[ERROR] Cannot open camera ID:', CAMERA_ID)
    quit()

find_lines = centre_mass2

# wait for stable white balance
for i in range(30):
    ret, frame = cap.read()



last_err = 0
ped_log_state_prev = None


DATA_left_and_right = []


while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    
    arduino_status = arduino.read_data()
    print(arduino_status)



    #---------------------
    # send frame to pc

    result, frame_to_send = cv2.imencode('.jpg', frame, encode_param)
    data = pickle.dumps(frame_to_send, 0)
    size = len(data)


    client_socket.sendall(struct.pack(">L", size) + data)

    #----------------------------------


    orig_frame = frame.copy()
    frame = cv2.resize(frame, SIZE)
    bin = binarize(frame, THRESHOLD)
    wrapped = trans_perspective(bin, TRAP, RECT, SIZE)

    bin_line = bin.copy()
    left, right = find_lines(wrapped)
    

    # TODO: ДАННАЯ ТЕМА ПРИМЕНЯЕТСЯ ДЛЯ ПРЕОДОЛЕНИЯ ПЕРЕКРЕСТКОВ В ЗАДАННОМ ПОРЯДКЕ, ПОЭТОМУ ОБНОВЛЯЕМ ПЕРЕМЕННУЮ START_ACTION НА ПРЯМОМ УЧАСТКЕ ДОРОГИ


    if STATE == GO:
        if (not find_lines.left_found) or (not find_lines.right_found):
            # print("Линия пропала Я на повороте")

            if (not find_lines.left_found):
                print("левая линия")
                left = 30 #создаем мнимую линию  30 - среднее значение на повороте

            

            elif (not find_lines.right_found):
                print("правая линия")

                # print("Left line ", find_lines.right_found)
                right = 500
                # right = wrapped.shape[1] - 1




    # print("left: ", left, "right: ", right)

    DATA_left_and_right.append([left, right])
    

    
    flag = True

    while is_car_stopped(DATA_left_and_right):
        print(" i am stopping")
        
        if flag:
            CAR_SPEED_start = CAR_SPEED
            flag = False
            
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, SIZE)
        bin = binarize(frame, THRESHOLD)
        wrapped = trans_perspective(bin, TRAP, RECT, SIZE)
        bin_line = bin.copy()
        
        left, right = find_lines(wrapped)

        DATA_left_and_right.append([left, right])

        CAR_SPEED_start+=0.2
        arduino.set_speed(min(CAR_SPEED_start, 1570))
        
        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount):
            
            break

    DATA_left_and_right = []


    

        
  
    # --- GO RIGHT --- #
    #* Из списка действий допустим первая таска поворот направо и когда левая линия пропадет из поля видимости START_ACTION = True


    SKIP = None

    if STATE == CROSS_RIGHT:
        if not START_ACTION and not find_lines.left_found:
            START_ACTION = True
        
    if STATE == CROSS_RIGHT and START_ACTION:
        SKIP, angle = True, 60

        print("SKIP")

        # left = int(right - wrapped.shape[1] * 0.6) #создаем мнимую линию

        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount):
            STATE = GO
    # --- GO RIGHT END --- #




    # --- GO STRAIGHT --- #
    if STATE == CROSS_STRAIGHT:
        if not START_ACTION:    # START_ACTION станет False когда айкар доедет до стоп линии, тобишь до перекрестка
            START_ACTION = True
            SUBSTATE = 0
        
    if STATE == CROSS_STRAIGHT and START_ACTION:
        if SUBSTATE == 0:
            bottom_offset_percet = 0.3
            line_amount_percent = 0.15
        else:
            bottom_offset_percet = 0.1
            line_amount_percent = 0.3

        pixel_offset = int(bin.shape[1] * 0.3)
        idx, max_dist = cross_center_path_v4_2(bin, pixel_offset=pixel_offset, bottom_offset_percent=bottom_offset_percet,
                                               line_amount_percent=line_amount_percent, show_all_lines=False)

        left = idx
        right = idx
        cv2.line(bin_line, (idx, 0), (idx, bin_line.shape[0]), 255)

        img_h, img_w = bin.shape[:2]
        h = int(0.9 * img_h)
        w = int(0.7 * img_w)
        cv2.line(bin_line, (w, h), (img_w, h), 200) # hori
        cv2.line(bin_line, (w, 0), (w, img_h), 200) # vert
        crop = bin[h:, w:]
        crop_pixels = crop.shape[0] * crop.shape[1]
        crop_white_pixels = np.sum(crop)//255
        if crop_white_pixels == 0:
            SUBSTATE = 1

        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount) and not detect_stop(wrapped):
            STATE = GO
    # --- GO STRAIGHT END --- #
    


    # --- GO LEFT --- #
    if STATE == CROSS_LEFT:
        STATE = _CROSS_LEFT_STRAIGHT
        meters = 0.4
        arduino.dist(int(DIST_METER*meters))
        print(f'Task: go {meters} meters ({int(DIST_METER*meters)} ticks)')

    if STATE == _CROSS_LEFT_STRAIGHT_AGAIN:
        pixel_offset = int(bin.shape[1] * 0.1)
        idx, max_dist = cross_center_path_v4_2(bin, pixel_offset=pixel_offset, line_amount_percent=0.3,
                                               bottom_offset_percent=0.1)
        idx = max(0, idx)
        left = idx
        right = idx
        cv2.line(bin_line, (idx, 0), (idx, bin_line.shape[0]), 255)

        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount) and not detect_stop(wrapped):
            STATE = GO

    if STATE == _CROSS_LEFT_LEFT:
        # left = right = 0
        arduino.check()
        if arduino.waiting():
            arduino_status = arduino.read_data()
            if 'end' in arduino_status:
                STATE = _CROSS_LEFT_STRAIGHT_AGAIN
                # arduino.dist(int(DIST_METER*0.7))

    if STATE == _CROSS_LEFT_STRAIGHT:
        pixel_offset = int(bin.shape[1] * 0.3)
        idx, max_dist = cross_center_path_v4_2(bin, pixel_offset=pixel_offset)
        left = idx
        right = idx
        cv2.line(bin_line, (idx, 0), (idx, bin_line.shape[0]), 255)

        # check_start = time.time()
        
        arduino.check()
        if arduino.waiting():
            arduino_status = arduino.read_data()
            if 'end' in arduino_status:
                STATE = _CROSS_LEFT_LEFT
                meters = 0.7
                arduino.dist(int(DIST_METER*meters))
                print(f'Task: go {meters} meters ({int(DIST_METER*meters)} ticks)')
    # --- GO LEFT END --- #



    if SKIP is None:
        center_mass = (left + right) // 2
        center = wrapped.shape[1] // 2

        err = 0-(center_mass - center)
        angle = int(90 + KP * err + KD * (err - last_err)) 
        last_err = err
    
        angle = min(max(50, angle), 120)

    else:
        print("ANGLE: ", angle)
    


    if STATE == _CROSS_LEFT_LEFT:
        angle = 120


    
    if STATE == GO and detect_stop(wrapped):
        print("Detect stop line")

        arduino.set_speed(1550)
        time.sleep(1)

        # arduino.set_speed(1500)

        START_ACTION = False
        #STATE = random.choice([CROSS_RIGHT, CROSS_STRAIGHT, CROSS_LEFT])
        STATE = CROSS_RIGHT

    
    if PREV_STATE != STATE or PREV_SUBSTATE != SUBSTATE:
        print(f'STATE: {STATE} ({SUBSTATE})')
        PREV_STATE = STATE
        PREV_SUBSTATE = SUBSTATE


    # arduino.dist(100)
    # print(arduino.read_data())
    
    if STATE != STOP:

        # if SKIP:
        #     arduino.set_speed(CAR_SPEED-2)

        # else:

            arduino.set_speed(CAR_SPEED)
            arduino.set_angle(angle)

    else:
        arduino.stop()

