import RPi.GPIO as GPIO	
from threading import Timer	
import time

import RPi.GPIO as GPIO	
from threading import Timer	
import time

pin_rotary = 4	

 # We'll be reading on/off hook events from BCM GPIO 3	
pin_onhook = 3	

 # After 900ms, we assume the rotation is done and we get	
# the final digit. 	
digit_timeout = 0.9	

 # We keep a counter to count each pulse.	
current_digit = 0	

 # Simple timer for handling the number callback	
number_timeout = None	

last_input = 0	

 # Timer to ensure we're on hook	
onhook_timer = None	
should_verify_hook = True	


__init__(self):	
    # Set GPIO mode to Broadcom SOC numbering	
    GPIO.setmode(GPIO.BCM)	

     # Listen for rotary movements	
    GPIO.setup(self.pin_rotary, GPIO.IN)	
    GPIO.add_event_detect(self.pin_rotary, GPIO.BOTH, callback = self.NumberCounter)	

     # Listen for on/off hooks	
    GPIO.setup(self.pin_onhook, GPIO.IN)	
    GPIO.add_event_detect(self.pin_onhook, GPIO.BOTH, callback = self.HookEvent, bouncetime=100)	

    self.onhook_timer = Timer(2, self.verifyHook)	
    self.onhook_timer.start()	

 # Handle counting of rotary movements and respond with digit after timeout	
def NumberCounter(self, channel):	
    input = GPIO.input(self.pin_rotary)	
    print "[INPUT] %s (%s)" % (input, channel)	
