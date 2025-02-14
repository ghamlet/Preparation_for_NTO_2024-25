from udp_client_class import UDPClient
import cv2

client = UDPClient(host_ip="192.168.0.69", port=9999)

while True:
    frame = client.receive_frame()
    
    cv2.imshow("Receiving Frame", frame)
    
    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break