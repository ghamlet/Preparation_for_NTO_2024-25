from USEFULL_SCRIPTS import UDPClient
from USEFULL_SCRIPTS import ColorTracker

import cv2

client = UDPClient(host_ip="127.0.0.1", port=4444)
tracker = ColorTracker()


while True:
    frame = client.receive_frame()
    
    cv2.imshow("Receiving Frame", frame)
    tracker.process_frame(frame)

    
    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break