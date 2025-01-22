'''
pi_rig contrains basic functions for using the raspberry pi behavior and electrophysiology rig in the Katz Lab

These functions can be used directly via ipython in a terminal window or called by other codes
'''

# Import things for running pi codes
import time
import RPi.GPIO as GPIO
import os

def laser_test(pin, dur = 20):
    """
    pin as an integer
    """

    # Setup pi board GPIO ports
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT) 
    run_laser = True

    while run_laser:
        GPIO.output(pin, 1)
        time.sleep(dur)
        GPIO.output(pin, 0)
        time.sleep(1)
        re_run = input('Do you want to re-run the laser (Y or N)?')
        if re_run[0].lower == 'n':
            run_laser = False

    print('Fiber has been measured.')