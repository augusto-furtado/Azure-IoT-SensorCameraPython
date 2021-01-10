#sensor tp223 - sensor vcc pin must be wired to a 3v pin; sensor sig pin is the i/o pin which can be wired to any gpio pin; sensor gnd pin is the ground pin;
#this app consider the pin on raspberry being gpio #17


import os
from time import sleep
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN,pull_up_down=GPIO.PUD_UP)
 
while True:
    if (GPIO.input(17) == True):
       print ('pressed')
    sleep(1);
