# Import things for running pi codes
import time
import sys
#from rgbled_class import RGBLed
import board
import digitalio

def main(dur=5, laser = None):

    # set up RGB LEDs
#     red_pin, green_pin, blue_pin = board.D13, board.D19, board.D26
#     led = RGBLed(red_pin, green_pin, blue_pin)

    # set up lasers
    laser1_pin = board.D25
#     laser2_pin = board.D6

    laser1 = digitalio.DigitalInOut(laser1_pin)
    laser1.direction = digitalio.Direction.OUTPUT
#     laser2 = digitalio.DigitalInOut(laser2_pin)
#     laser2.direction = digitalio.Direction.OUTPUT
    
      
    # turn on laser
    if laser != 0:
        laser1.value=True
#         laser2.value=True

#     # turn on LED_light depending on the laser conditions
#     if laser == 1:
#         led.green_on()
#     elif laser == 2:
#         led.red_on()
#     else:
#         led.blue_on()

    time.sleep(dur)

    if laser != 0:
        laser1.value=False
#         laser2.value=False

#     # turn off LED_light 
#     if laser == 1:
#         led.green_off()
#     elif laser == 2:
#         led.red_off()
#     else:
#         led.blue_off()


if __name__ == '__main__':
    print('Laser is activated')
    main(dur=int(sys.argv[1]), laser=int(sys.argv[2]))
    
