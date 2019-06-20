#!/bin/bash
gpio mode 1 pwm
gpio pwm-ms
gpio pwmc 32
gpio pwmr 36144

# Change to a larger value to turn the volume up
#gpio pwm 1 1000
gpio pwm 1 10000
sleep 1

gpio pwm 1 10000
sleep 1

gpio pwm 1 10000
sleep 1

gpio pwm 1 0
