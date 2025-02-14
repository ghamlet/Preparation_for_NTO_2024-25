import cv2
from stream_server_class import UDPStreamer

video_server = UDPStreamer(host_ip="192.168.0.69", port=9999)



cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    video_server.send_frame(frame)
