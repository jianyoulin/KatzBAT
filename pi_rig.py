'''
pi_rig contrains basic functions for using the raspberry pi behavior and electrophysiology rig in the Katz Lab

These functions can be used directly via ipython in a terminal window or called by other codes
'''

# Import things for running pi codes
import time
import RPi.GPIO as GPIO
import os
import board, busio, digitalio
# import busio
# import digitalio

def laser_test(pin=25, dur = 20):
    """
    pin as an integer
    """

    # Setup pi board GPIO ports
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    GPIO.setup(pin, GPIO.OUT) 
    run_laser = True
    
    while run_laser:
        GPIO.output(pin, 1)
        time.sleep(dur)
        GPIO.output(pin, 0)
        time.sleep(1)
        re_run = input('Do you want to re-run the laser (Y or N)?')
        if re_run[0].lower() == 'n':
            run_laser = False

    print('Fiber output power has been measured.')

def beambreak_test(pin=board.D6):
    # setup nose poke beam break detection
    nosepokeIR = digitalio.DigitalInOut(pin)
    nosepokeIR.direction = digitalio.Direction.INPUT
    nosepokeIR.pull = digitalio.Pull.UP
    
    last_poke = nosepokeIR.value # return status (broken or not) for each pin as a tuple
    while not last_poke: # stay here if beam broken
        last_poke = nosepokeIR.value # make sure nose-poke is not blocked when starting
        
    while True: 
        current_poke = nosepokeIR.value
        # First check if transitioned from not poke to poke.
        if current_poke == 0 and last_poke == 1: # 0 indicates poking
            beam_break = time.time()
            print('!!! Break !!!')

        # Next check if transitioned from poke to not poke.
        if current_poke == 1 and last_poke == 0:
            beam_unbroken = time.time()
            print('No Break')
        
        # Update last state and wait a short period before repeating.
        last_poke = nosepokeIR.value
        time.sleep(0.001)
