#!/usr/bin/env python3
#
# $Id: bipolar_class.py,v 1.6 2023/05/23 09:20:03 bob Exp $
# Raspberry Pi bipolar Stepper Motor Driver Class
# Hardware Nema17 12 Volt Stepper High Torque Motor
# Gear Reduction Ratio: 1/64 
# Uses the A4988 H-bridge circuit driver board.
#
# Author : Bob Rathbone
# Site   : http://www.bobrathbone.com
#

import sys
import os
import time
import numpy as np

import RPi.GPIO as GPIO

# The stepper motor can be driven in five different modes 
# See http://en.wikipedia.org/wiki/Stepper_motor

# Step resolution (The last column is the multiplier for one revolution)
FullStep = [0,0,0,1]
HalfStep = [1,0,0,2]
QuarterStep = [0,1,0,4]
EighthStep = [1,1,0,8]
SixteenthStep = [1,1,1,16]

# Other definitions
ENABLE = GPIO.LOW
DISABLE = GPIO.HIGH
STEPS = 200 # 200 step motor (Full)

class Motor:
    # Direction
    CLOCKWISE = 0
    ANTICLOCKWISE = 1

    # Step sizes (Don't change values)
    FULL = 1
    HALF = 2
    QUARTER = 4
    EIGHTH = 8
    SIXTEENTH = 16

    pulse = 0.0007
    interval = 0.0007
    oneRevolution = STEPS

    def __init__(self, step, direction, enable, ms1, ms2, ms3):
        self.step = step
        self.direction = direction
        self.enable = enable
        self.ms1 = ms1
        self.ms2 = ms2
        self.ms3 = ms3
        return

    # Initialise GPIO pins for this bipolar motor
    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.direction,GPIO.OUT)
        GPIO.setup(self.step,GPIO.OUT)
        GPIO.setup(self.enable,GPIO.OUT)
        GPIO.setup(self.ms1,GPIO.OUT)
        GPIO.setup(self.ms2,GPIO.OUT)
        GPIO.setup(self.ms3,GPIO.OUT)
        self.zeroPosition()
        self.setStepSize(self.FULL)
        return  

    # Reset (stop) motor
    def reset(self):
        GPIO.output(self.step,GPIO.LOW)
        GPIO.output(self.direction,GPIO.LOW)
        GPIO.output(self.enable,GPIO.HIGH)
        GPIO.output(self.ms1,GPIO.LOW)
        GPIO.output(self.ms2,GPIO.LOW)
        GPIO.output(self.ms3,GPIO.LOW)
        return  

    # Set up stepper resolution
    def setStepResolution(self,stepres):
        GPIO.output(self.ms1,stepres[0])
        GPIO.output(self.ms2,stepres[1])
        GPIO.output(self.ms3,stepres[2])
        self.oneRevolution = STEPS * stepres[3]
        return self.oneRevolution

    # Turn the motor
    def turn(self,steps,direction):
        count = steps
        GPIO.output(self.enable,ENABLE)
        GPIO.output(self.direction,direction)
        while count > 0:
            GPIO.output(self.step,GPIO.HIGH)
            time.sleep(self.pulse)
            GPIO.output(self.step,GPIO.LOW)
            time.sleep(self.interval)
            count -= 1
        GPIO.output(self.enable,DISABLE)
        return

    def interrupt(self):
        self.halt = True
        return

    # Increment current position 
    def incrementPosition(self):
        return

    # Increment current position 
    def decrementPosition(self):
        return 

    # Increment current position 
    def zeroPosition(self):
        self.position = 0
        return self.position

    # Goto a specific position
    def goto(self, position):
        newpos = position
        while newpos > self.oneRevolution:
                newpos -= self.oneRevolution

        delta =  newpos - self.position

        # Figure which direction to turn
        if delta > self.oneRevolution/2:
            delta = self.oneRevolution/2 - delta

        elif delta < (0-self.oneRevolution/2):
                delta = self.oneRevolution + delta

        # Turn the most the efficient direction
        if delta > 0:
                self.turn(delta,self.CLOCKWISE)

        elif delta < 0:
                delta = 0 - delta
                self.turn(delta,self.ANTICLOCKWISE)

        self.position = newpos
        if self.position == self.oneRevolution:
                self.position = 0
        return self.position

    # Homing the motor
    def home(self, he_pin = None): #, adjust_steps=None):
        # setup hall effect input
        inport = he_pin
        GPIO.setup(inport, GPIO.IN)
        
        if not GPIO.input(inport):
            cck_steps = int(self.oneRevolution/(360/20))
            self.turn(cck_steps,self.ANTICLOCKWISE)
            
        GPIO.output(self.enable,ENABLE)
        GPIO.output(self.direction, 0) # 0 CLOCKWISE
        cur_time = time.time()
        status = 0
        n_steps, on_steps = 0, 0
        
        last_status = GPIO.input(inport)
        while n_steps < self.oneRevolution:
        #while GPIO.input(inport) and (time.time()-cur_time) <= 5:
            GPIO.output(self.step,GPIO.HIGH)
            time.sleep(self.pulse)
            GPIO.output(self.step,GPIO.LOW)
            time.sleep(self.interval)
            n_steps = n_steps + 1
            
            cur_status = GPIO.input(inport)
            
            if cur_status != last_status: # gets close enough to trigger sensor
                # break
                status = status + 1
            if status== 1: # Magnet becomes close
                on_steps = on_steps + 1
            if status == 2: #Magnet becomes far again
                break
            last_status = GPIO.input(inport)
        
        print(on_steps)
        
        time.sleep(0.5)
        
        self.turn(on_steps//2, self.ANTICLOCKWISE)
        #self.turn(adjust_steps,self.CLOCKWISE)
        
        time.sleep(0.5)
        GPIO.output(self.enable, DISABLE)
        return

    
    # Stop the motor (calls reset)
    def stop(self):
        self.reset()    
        return

    # Lock the motor (also keeps motor warm)
    def lock(self):
        return  

    # Set Step size
    def setStepSize(self,size):

        if size == self.HALF:
            steps = self.setStepResolution(HalfStep)    
        elif size == self.QUARTER:
            steps = self.setStepResolution(QuarterStep) 
        elif size == self.EIGHTH:
            steps = self.setStepResolution(EighthStep)  
        elif size == self.SIXTEENTH:
            steps = self.setStepResolution(SixteenthStep)   
        else:
            steps = self.setStepResolution(FullStep)    

        self.oneRevolution = steps
        return self.oneRevolution


    # Get number of revolution steps
    def getRevolution(self):
        return self.oneRevolution
        

# End of Unipolar Motor class

def get_cw_steps(cur_pos, dest_pos, tot_pos = None):
    """ count number of steps needed to the destination in clockwise direction"""
    seq = np.arange(cur_pos, cur_pos+tot_pos)
    seq[seq > tot_pos] = seq[seq > tot_pos] - tot_pos
#    print(seq)
    steps_to_dest = np.where(seq == dest_pos)[0] - \
                    np.where(seq == cur_pos)[0]
    return int(steps_to_dest)

def get_ccw_steps(cur_pos, dest_pos, tot_pos = None):
    """ count number of steps needed to the destination in counter-clockwise direction"""
    seq = np.arange(cur_pos+tot_pos, cur_pos, -1)
    seq[seq > tot_pos] = seq[seq > tot_pos] - tot_pos
#    print(seq)
    steps_to_dest = np.where(seq == dest_pos)[0] - \
                    np.where(seq == cur_pos)[0]
    return int(steps_to_dest)

def rotate_dir(cur_pos, dest_pos, tot_pos = 8):
    """determine the steps and rotation direction"""
    cw_steps = get_cw_steps(cur_pos, dest_pos, tot_pos = tot_pos)
    ccw_steps = get_ccw_steps(cur_pos, dest_pos, tot_pos = tot_pos)
#    print(f'cw_steps={cw_steps}; ccw_steps={ccw_steps}')
    if cw_steps <= ccw_steps:
        return 1, cw_steps 
    else:
        return 0, ccw_steps 

