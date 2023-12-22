# Face-tracking-kiosk

## 1. Introduction
It is a final proejct for embeded system in 2023.
The normal kiosk is designed for adults. It is difficult to use kiosks for people with physical difficulties.
So, i suggested kiosk arm which tracking user's face to improve accesibility.

![image](https://github.com/gigohe2/Face-tracking-kiosk/assets/59073888/425015cd-2f86-45d1-a1b6-290c0a3d143f)

## 2. Implementation
### HW
1) raspberry pi 4B
2) Google coral TPU
3) Camera
4) Servo motor
5) tact switch
6) 
![image](https://github.com/gigohe2/Face-tracking-kiosk/assets/59073888/e237d85b-584d-4d7d-a6c8-b996987e7859)

To recognize face region, I used Goolge coral accelerator to avoid delay. It was hard to run large deep-learning model on raspberry pi.
So, this TPU computes face recognition deep-learning model. SSD MobileNet(Pre-trained) was used to do this.

![image](https://github.com/gigohe2/Face-tracking-kiosk/assets/59073888/e208acfa-d421-4c74-800a-cadc04da9119)

After get face region from TPU, compute the error between ceter pixel of image and center pixel of face.
Then, apply PID control to get each servo motor position.

![image](https://github.com/gigohe2/Face-tracking-kiosk/assets/59073888/174346ea-f210-454e-8837-39b72b738bed)

Also, there is 2-interrupt service routine(ISR). Not pooling
1) Reset ISR
 -> user can initialize servo motor position by push tact switch 1.
2) Shutdown ISR
 -> user can shutdown main program by push tact switch 2.

https://youtu.be/_tYapHzxim4
You can check the real-time demonstration of our kiosk arm via above youtube link.
