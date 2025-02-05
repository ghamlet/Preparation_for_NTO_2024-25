# -*- coding: utf-8 -*-
import robot
import serial
import time


r = robot.Robot()
r.connect('/dev/ttyACM0', None) #подключение к dinamixel

time.sleep(1)


r.setJoint( 'j2', 0)

r.setJoint( 'j3', -90)
r.setJoint( 'j1', 0)
r.setJoint( 'j4', 30)  # отрицательное не использовать
r.setJoint( 'j5', 110) # вращение запястья

r.setJoint( 'j6', 10) # 10 - захват полностью закрыт

