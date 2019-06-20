import RPi.GPIO as GPIO
import time

class Tester:
  def __init__(self):
    self.bcm_mode()
    self.setup()
    self.trigger_detection()
    self.test()

  def board_mode(self):
    GPIO.setmode(GPIO.BOARD)
    self.in_to_out = {8: 10, 11: 13, 15: 16}

  def bcm_mode(self):
    GPIO.setmode(GPIO.BCM)
    self.in_to_out = {4: 17, 27: 22, 23: 24}

  def setup(self):
    for p_in, p_out in self.in_to_out.iteritems():
      GPIO.setup(p_in, GPIO.IN)
      GPIO.setup(p_out, GPIO.OUT)
      GPIO.output(p_out, GPIO.HIGH)

  def light(self):
    print("----\r"),
    for p_in, p_out in self.in_to_out.iteritems():
      GPIO.output(p_out, not GPIO.input(p_in))
      on = not GPIO.input(p_in)
      print("%d: %s " % ( p_in, "ON " if on else "OFF" )),

  def test(self):
    print("testing")
    while True:
        time.sleep(5) 
 
  def my_callback(channel, edge):
    print('Edge detected on channel %s %s' %(channel, edge))

  def trigger_detection(self):
    for p_in, p_out in self.in_to_out.iteritems():
      GPIO.add_event_detect(p_in, GPIO.BOTH, callback=self.my_callback, bouncetime=25)

  def cleanup(self):
    GPIO.cleanup()    

if __name__ == '__main__':
    Tester()
