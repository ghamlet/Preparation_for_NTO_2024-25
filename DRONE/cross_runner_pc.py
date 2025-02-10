import cv2
import numpy as np

from road_utils import *

import socket
import pickle
import struct

HOST = '192.168.4.12'
PORT = 8080

data = b""
payload_size = struct.calcsize(">L")


THRESHOLD = 200
DIST_METER = 1825 

find_lines = centre_mass2


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind((HOST,PORT))
s.listen(10)
print('Socket created')

conn, addr = s.accept()




while True:


    while len(data) < payload_size:
        data += conn.recv(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

   
    

    frame = cv2.resize(frame, SIZE)

    cv2.imshow("frame", frame)
    cv2.waitKey(1)

    bin = binarize(frame, THRESHOLD, show=True)

    wrapped = trans_perspective(bin, TRAP, RECT, SIZE, d=True)

    
#     bin_line = bin.copy()
    
#     left, right = find_lines(wrapped, d=True)
    
#     k = cv2.waitKey(1)
#     if k == ord("q"):
#         break




# cv2.destroyAllWindows()