#!/usr/bin/python3
import RPi.GPIO as GPIO  
import math, sys, os
import subprocess
import socket

PIN_ROTATING_1 = 17 #4
PIN_ROTATING_2 = 4  #17

PIN_PULSE_1 = 22 #27
PIN_PULSE_2 = 27 #22

PIN_HOOK_1 = 23
PIN_HOOK_2 = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  
GPIO.setup(PIN_ROTATING_1, GPIO.OUT)
GPIO.setup(PIN_PULSE_1, GPIO.OUT)
GPIO.setup(PIN_HOOK_1, GPIO.OUT)

GPIO.output(PIN_ROTATING_1, GPIO.HIGH)
GPIO.output(PIN_PULSE_1, GPIO.HIGH)
GPIO.output(PIN_HOOK_1, GPIO.HIGH)

GPIO.setup(PIN_ROTATING_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_PULSE_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_HOOK_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def hook(pin):
    print "Hook is in state %d" % GPIO.input(PIN_HOOK_2)

GPIO.add_event_detect(PIN_HOOK_2, GPIO.BOTH, callback=hook, bouncetime=10)

c=0
last = 0

def count(pin):
    print "Event on pin %d"%pin
    global c 
    c = c + 1

GPIO.add_event_detect(PIN_ROTATING_2, GPIO.BOTH)

while True:
   try:
      if GPIO.event_detected(PIN_ROTATING_2):
          current = GPIO.input(PIN_ROTATING_2)
          print "Event on pin %d current %d" % (PIN_ROTATING_2, current)
          if(last != current):
              if(current == 1):
                  GPIO.add_event_detect(PIN_PULSE_2, GPIO.BOTH, callback=count, bouncetime=10)
              else:
                  GPIO.remove_event_detect(PIN_PULSE_2)
                  number = int((c-1)/2)+1
                  if number >= 10:
                    number = 0
      	                       
                  print ("You dial", number)
                  c= 0                 
                  
                  
              last = GPIO.input(PIN_ROTATING_2)
   except KeyboardInterrupt:
       break
