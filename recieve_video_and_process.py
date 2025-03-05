from USEFULL_SCRIPTS import UDPClient
from USEFULL_SCRIPTS import ColorTracker

import cv2

# client = UDPClient(host_ip="172.16.65.104", port=9999)
# tracker = ColorTracker()


while True:
    frame = "http://172.16.65.104:8088"    
    cv2.imshow("Receiving Frame", frame,dad)
    # tracker.process_frame(frame)

    
    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break