import detect
import tflite_runtime.interpreter as tflite
from time import sleep
from PIL import Image
from PIL import ImageDraw
import cv2
import numpy as np
import time
import os
import timeit
import pigpio
from servo_motor import ServoControl

class Kiosk:
    def __init__(self):
        self.err = [0, 0]
        self.center = [160, 160]
        self.cur_degrees = [2000, 2000, 1700, 1300]
        self.pi = pigpio.pi()
        self.shutdown = False

        # button interrupt handler initialize
        self.pin1 = 20
        self.pin2 = 21
        self.but1_time = time.time()
        self.but2_time = time.time()
        self.pi.set_mode(self.pin1, pigpio.INPUT)
        self.pi.set_mode(self.pin2, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin1, pigpio.PUD_UP)  
        self.pi.set_pull_up_down(self.pin2, pigpio.PUD_UP)  
        self.reset_cb = self.pi.callback(self.pin1, pigpio.EITHER_EDGE, self.reset_callback)
        self.shutdown_cb = self.pi.callback(self.pin2, pigpio.EITHER_EDGE, self.shutdown_callback)

        # face detector initialize
        self.interpreter = interpreter = tflite.Interpreter(os.path.join(os.getcwd(),
             "ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite"),
            experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')]
            )
        self.interpreter.allocate_tensors()
        self.cap = cv2.VideoCapture(-1)

        # servo motor initialize
        self.servo_handler = ServoControl()
        
    def reset_callback(self, gpio, level, tick):
        if level == 0:  
            if time.time() - self.but1_time > 1:
                print("reset by button")
                self.servo_handler.reset()
                self.but1_time = time.time()
        
    def shutdown_callback(self, gpio, level, tick):
        if level == 0 :
            if time.time() - self.but2_time > 1:
                print("shutdown program") 
                self.shutdown = True
                self.but2_time = time.time()  

    def draw_objects(self ,image, objs):
        for obj in objs:
            bbox = obj.bbox
            
            cv2.rectangle(image,(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0, 255, 0),2)
            bbox_point_w = bbox.xmin + ((bbox.xmax-bbox.xmin) // 2)
            bbox_point_h = bbox.ymin + ((bbox.ymax-bbox.ymin) // 2) 

            self.err = [self.center[0] - bbox_point_w, self.center[1] - bbox_point_h] 

            cv2.circle(image, (bbox_point_w, bbox.ymax-bbox.ymin), 5, (0,0,255),-1)
            cv2.putText(image, text='%d%%' % (obj.score*100), org=(bbox.xmin, bbox.ymin), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
    
    def main(self):
        while not self.shutdown:
            ret, image = self.cap.read()
            # image reshape
            image = cv2.resize(image, dsize=(320, 320), interpolation=cv2.INTER_AREA)
            # image BGR to RGB
            image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

            tensor = detect.input_tensor(interpreter=self.interpreter)[:, :] = image.copy() 
            tensor.fill(0)  # padding        
            self.interpreter.invoke()  # start

            objs = detect.get_output(self.interpreter, 0.5, (1.0, 1.0))

            if len(image):
                self.draw_objects(image, objs)
                if len(objs):
                    print("control by face")
                    self.servo_handler.lr_control(-1*self.err[0])
                    self.servo_handler.vertical_control(1*self.err[1])
                else:
                    #print("reset by face")
                    self.servo_handler.reset()
            image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            cv2.imshow('face detector', image)

            k = cv2.waitKey(30) & 0xff
            if k == 27: # press 'ESC' to quit # ESC exit
                break

            print(self.err, self.servo_handler.cur_degrees)
            time.sleep(0.02)

if __name__ == '__main__':
    kiosk = Kiosk()
    kiosk.main()
