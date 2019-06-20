"""
This module implements the interface with the hardware of the phone, the
earpiece hook and the rotary dialler.
"""


# from threading import Timer  # Not currently needed with Astral hardware.
from RPi import GPIO
import time


class HardwareAbstractionLayer(object):
    """
    Superclass to allow disambiguation between different implementations of
    dialer hardware from different phone conversion projects.
    """

    pulse_count = 0  # Count the number of pulses detected

    onhook_timer = None  # Timer object to ensure we're on hook
    debounce_timer = None  # Timer object for debounce cleaning.

    dialing = False
    hook = False

    last = 0

    pins = {
        "earpiece": None,
        "digits": None,
        "dialing": None,
        "power_pins": None
    }

    callback_digit = None
    callback_onhook = None
    callback_offhook = None

    pulse_table = {
        1:1,
        2:2,
        3:3,
        4:4,
        5:5,
        6:6,
        7:7,
        8:8,
        9:9,
        10:0
    }

    def __init__(self):
        GPIO.setmode(GPIO.BCM)  # Broadcom pin numbers.

        GPIO.setup(self.pins["dialing"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Listen for dialing start/end.
        GPIO.add_event_detect(self.pins["dialing"],
                              GPIO.BOTH,
                              callback=self.dialing_state, bouncetime=10)

        GPIO.setup(self.pins["digits"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Listen for digits.
#        GPIO.add_event_detect(self.pins["digits"],
#                              GPIO.BOTH,
#                              callback=self.detect_clicks)

        # Listen for on/off hooks
        GPIO.setup(self.pins["earpiece"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.pins["earpiece"],
                              GPIO.BOTH,
                              callback=self.earpiece_event,
                              bouncetime=1)  # Is bouncetime a debounce constant!?

        if "power_pins" in self.pins:
            GPIO.setup(self.pins["power_pins"], GPIO.OUT)
            GPIO.output(self.pins["power_pins"], GPIO.HIGH)

    def clean_exit(self):
        """
        Safely close the GPIO when closing the app.
        """
        GPIO.cleanup()

    def dialing_state(self, channel):
        """
        GPIO detects whether the rotary dial is active.
        """
        current = GPIO.input(channel)
        # print "Event on pin %d current %d" % (channel, current)
        if(self.last != current):
            if(current == 1):
                GPIO.add_event_detect(self.pins["digits"], GPIO.BOTH, callback=self.detect_clicks, bouncetime=1)
            else:
                GPIO.remove_event_detect(self.pins["digits"])
                number = int((self.pulse_count-1)/2)+1
                if number >= 10:
                    number = 0
                #print ("You dialed", number)
                self.callback_digit(number)
                self.pulse_count= 0                 
            self.last = GPIO.input(channel)
            
       #if not GPIO.input(channel):
       #    return None

       #if not self.dialing:
       #    self.dialing = True
       #    self.pulse_count = 0
       #else:
       #    pulses = self.pulse_count
       #    if pulses % 2:
       #        raise IOError("Count is not divisible by 2")
       #    self.callback_digit(self.pulse_table[pulses])

    def detect_clicks(self, channel):
        """
        GPIO detects a state change on the rotary detection pin. This is where
        I count the clicks and assemble a digit from the data.
        """
        #if GPIO.input(channel):
        self.pulse_count += 1

    def earpiece_event(self, channel):
        """
        GPIO detects a state change
        """
        self.hook = bool(GPIO.input(channel))
        if self.hook:
            self.callback_onhook()
        else:
            self.callback_offhook()

    def register_callbacks(self,
                           callback_digit,
                           callback_onhook,
                           callback_offhook):
        """
        Register callbacks for the interface with the calling application
        """
        self.callback_digit = callback_digit
        self.callback_onhook = callback_onhook
        self.callback_offhook = callback_offhook


class AutomaticElectricHAL(HardwareAbstractionLayer):
    """
    Subclass of HardwareAbstractionLayer to support the dialer in phones from
    the late period of AutomaticElectric.
    """
    def __init__(self):
        self.pins = {
            "earpiece": 23,
            "digits" : 27,
            "dialing": 4,
            "power_pins": [17, 22, 24]
        }
        self.bounce_time = 10
        super(AutomaticElectricHAL, self).__init__()

class AstralHAL(HardwareAbstractionLayer):
    """
    Subclass of HardwareAbstractionLayer to support the dialer in phones from
    the late period of Astral PLC.
    """
    def __init__(self):
        self.pins = {
            "earpiece": 22,
            "digits" : 17,
            "dialing": 27
        }
        super(AstralHAL, self).__init__()


class ElektriskHAL(HardwareAbstractionLayer):
    """
    Subclass of HardwareAbstractionLayer to support the dialer in the
    AS Elektrisk Bureau desk phone.
    """

    def __init__(self):
        self.pins = {
            "earpiece": 3,
            "digits": 4,
            "dialing": None
        }
        super(ElektriskHAL, self).__init__()


if __name__ == "__main__":
    numbers = []
    working = True

    def digit(number):
        global working
        print number
        numbers.append(number)
        if len(numbers) > 1 and numbers[-1] == 0 and numbers[-2] == 0:
            print "\nExiting"
            working = False
        
    def onhook():
        print "On hook"

    def offhook():
        print "Off hook"

    hal = AutomaticElectricHAL()
    hal.register_callbacks(digit, onhook, offhook)

    print "Dial two 0 to exit. (or ctrl+c)"
    while working:
        time.sleep(0.1)

