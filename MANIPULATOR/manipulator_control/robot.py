# -*- coding: utf-8 -*-
import time
import pypot.dynamixel
import serial
import logging
logger = logging.getLogger(__name__)


class Robot(object):
    _dxl_io: pypot.dynamixel.DxlIO = None
    _ard_io: serial.Serial = None

    to_storage_move_speed = 500
    to_storage_move_speed1 = 100
    to_storage_move_speed2 = 300
    to_storage_move_speed3 = 200

    to_storage_move_fwd_time = 2
    to_storage_move_fwd_time1 = 1
    to_storage_move_left_time = 1.35
    to_storage_move_left_time1 = 2
    to_storage_move_fwd_time2 = 3
    to_storage_move_right_time = 2.5

    def __init__(self):
        self.motors = {
            'j1': [1, 'joint'],
            'j2': [2, 'joint'],
            'j3': [3, 'joint'],
            'j4': [4, 'joint'],
            'j5': [5, 'joint'],
            'j6': [6, 'joint']
        }

    def connect(self, dxl_port, ard_port=None):
        print('Connecting to DXL port ', dxl_port)
        self._dxl_io = pypot.dynamixel.DxlIO(dxl_port)
        print('DXL Connected!')

        # for m in self.motors:
        #     self.setup_motor(self.motors[m])
        #     print("Motor " + m + " configured")

        if not(ard_port is None):
            print('Connecting to Arduino port ', ard_port)
            self._ard_io = serial.Serial(ard_port, 1000000) 
    


    def setup_motor(self, motor):
        motor_id = motor[0]
        if self._dxl_io.ping(motor_id):
            if motor[1] == 'wheel':
                self._dxl_io.set_wheel_mode([motor_id])
            else:
                self._dxl_io.set_joint_mode([motor_id])
            self._dxl_io.enable_torque([motor_id])
        else:
            raise IOError('Motor ' + str(motor_id) + ' not responded')

    def close(self):
        if not (self._dxl_io is None):
            self._dxl_io.close()
            self._dxl_io = None
            print('DXL Connection closed')

        if not (self._ard_io is None):
            self._ard_io.close()
            self._ard_io = None
            print('Arduino Connection closed')

    def set_speed(self, motors):
        s = {}
        for m in motors:
            s[self.motors[m][0]] = motors[m]
        self._dxl_io.set_moving_speed(s)

    def set_pos(self, motors, wait=False):
        s = {}
        for m in motors:
            s[self.motors[m][0]] = motors[m]

        self._dxl_io.enable_torque(s.keys())
        self._dxl_io.set_goal_position_speed_load(s)
        if wait:
            self.wait(s.keys())

    def wait(self, motors):
        moving = True
        while moving:
            try:
                mov = self._dxl_io.is_moving(motors)
                moving = False
                for m in mov:
                    if m:
                        moving = m
                        break
            except:
                self._dxl_io.enable_torque(motors)

    #############################################################################

    def init(self):
         self.set_pos({
             'j1': [10, 10, 10],
             'j2': [0, 100, 100],
             'j3': [0, 100, 100],
             'j4': [90, 100, 100],
             'j5': [0, 100, 100],
             'j6': [50, 100, 100]
         }, True)

    # def movet(self):
    #     self.set_pos({
    #         'j1': [90, 100, 100],
    #         'j2': [-130, 100, 100],
    #     }, True)
    #
    def setJoint(self, joint, pos):
         self.set_pos({
             joint: [pos,50,50]
        }, True)

    def stop(self):
         self.set_speed({"front": 0, "rear": 0, "left": 0, "right": 0})



