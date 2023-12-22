import time
import pigpio
from math import trunc


class ServoControl:
    def __init__(self):
        self.servo_pins = [6, 13, 19]
        self.center_degrees = [2000, 2000, 1700]
        self.cur_degrees = [2000, 2000, 1700]
        self.pi = pigpio.pi()
        self.delta = 0

        # Set initial servo pulsewidth
        for pin, degree in zip(self.servo_pins, self.cur_degrees):
            self.pi.set_servo_pulsewidth(pin, degree)

    def P_control(self, err):
        Kp = -0.5
        return Kp*err

    def end_of_degree(self, motor_num, deg):
        if motor_num == 0:
            deg = max(min(deg, 2350), 1200)
        elif motor_num == 1:
            deg = max(min(deg, 2100), 1400)
        elif motor_num == 2:
            deg = max(min(deg, 1900), 1500)
        return deg

    def lr_control(self, err_x):
        dx = self.P_control(err_x)
        self.cur_degrees[0] = self.end_of_degree(0, dx + self.cur_degrees[0])
        self.pi.set_servo_pulsewidth(self.servo_pins[0], self.cur_degrees[0])
        time.sleep(0.05)

    def vertical_control(self, err_y):
        dy = -0.3 * self.P_control(err_y)
        self.cur_degrees[2] += dy
        self.cur_degrees[2] = self.end_of_degree(2, self.cur_degrees[2])
        self.pi.set_servo_pulsewidth(self.servo_pins[2], self.cur_degrees[2])
        time.sleep(0.05)

    def control_by_face(self, err):
        
        self.lr_control(-1*err[0])
        self.vertical_control(err[1])

    def reset(self):
        
        while True:
            for i in range(3):
                if self.cur_degrees[i] > self.center_degrees[i]:
                    self.cur_degrees[i] -= 10
                else:
                    self.cur_degrees[i] += 10
                self.cur_degrees[i] = trunc(self.cur_degrees[i])
                self.pi.set_servo_pulsewidth(self.servo_pins[i], self.cur_degrees[i])
            if self.is_in_center():
                
                break
            time.sleep(0.01)

    def is_in_center(self):
        return (self.cur_degrees[0] >= 1985 and self.cur_degrees[0] <= 2015) and \
               (self.cur_degrees[1] >= 1985 and self.cur_degrees[1] <= 2015) and \
               (self.cur_degrees[2] >= 1685 and self.cur_degrees[2] <= 1715)
