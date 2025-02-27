import cv2
from USEFULL_SCRIPTS import UDPStreamer

video_server = UDPStreamer()



cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    video_server.send_frame(frame)
