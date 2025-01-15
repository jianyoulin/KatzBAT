# this code record number oof licks via MPR121 touch sensor
# execute the code with python licking_test.py [rat_id] [experimental duration]
# this code equipped with laser to peeturb neural systems during licking


import sys
import os
import time
from datetime import datetime, date
from pathlib import Path
import numpy as np
import pickle
import easygui
import json

import board
import busio
import digitalio
import adafruit_mpr121

import atexit
from bipolar_class import Motor
from bipolar_class import rotate_dir
# from rgbled_class import RGBLed
#from turn_motor import *

import subprocess
import signal
from subprocess import Popen, PIPE

from util_tools import *
# from RunBAT_grid import RunBAT

proj_path = os.getcwd() #'/home/rig337-testpi/Desktop/katz_lickometer'
print(proj_path)

submitted_data = read_json_file()
# print(submitted_data)

rat_id = submitted_data['ratID']
date = time.strftime("%Y%m%d")

d, f = submitted_data['datFolder'], submitted_data['fileName']
protocol_N = submitted_data['protocol']
param_file = os.path.join(proj_path, 'Parameters', protocol_N)
# print(param_file)
saved_dat = os.path.join(proj_path, d, f)
backup_dir = os.path.join(proj_path, 'backups')
# print(saved_dat)
spout_num = submitted_data['spots_num']

# gather experimental parameter values
initial_wait = int(var_data(param_file, var_name='IPITimes')[0])//1000
exp_dur = int(var_data(param_file, var_name='SessionTimeLimit')[0])//1000
max_trial_time = int(var_data(param_file, var_name='MaxWaitTime')[0])//1000
max_lick_time = int(var_data(param_file, var_name='LickTime')[0])//1000
iti = int(var_data(param_file, var_name='IPITimes')[0])//1000
t_list = var_data(param_file, var_name='Solutions')
conc_list = var_data(param_file, var_name='Concentrations')
trial_list = list(map(int, var_data(param_file, var_name='TubeSeq')))
# print(f'{trial_list}')

# taste positions: rotation spot with a fluid stimulus
taste_positions = list(np.unique(trial_list))
tastes = [i for i in t_list if len(i) > 0]
params = [initial_wait, max_trial_time, len(trial_list), iti, exp_dur, max_lick_time]

# Tube: trial_list for data saving in dat_file
tube_seq = trial_list
conc_seq = [conc_list[i-1] for i in trial_list]
solution_seq = [t_list[i-1] for i in trial_list]
IPI_seq = var_data(param_file, var_name='IPITimes')
Length_seq = var_data(param_file, var_name='LickTime')

# making sequnce of laser conditions across tria_trial lists
#lasers = np.int64(lasers)
laser_dur = 3 # laser duration
lasers = [0 for _ in range(len(trial_list))]

# print laser conditions
laser_label = {0: "No Laser control trial",
               1: "Laser triggered by trial start",
               2: "Laser triggered by first lick of the trial"
               }

if submitted_data['laser_used']:
    for t in taste_positions:
        this_taste_trial_index = np.where(trial_list == t)[0]
        for i, j in enumerate(this_taste_trial_index):
            if i%len(laser_label.keys()) == 0:
                this_order = list(np.random.choice(list(laser_label.keys()), replace= False,
                                                   size= len(laser_label.keys())))
            lasers[j] = int(this_order[i%len(laser_label.keys())])

laser_conditions = list(np.unique(lasers))

# # print experiment information
# print(params)
# print([f'Spout-{taste_positions[i]}: {tastes[i]}' for i in range(len(tastes))])
# print('taste sequency: {}'.format(trial_list))
# print('laser sequency: {}'.format(lasers))

# detect if there are uneven trials cross laser conditions
conditions, counts = np.unique(lasers, return_counts=True)
if not np.all(counts == (counts[0])):
    print(f'Uneven trials across laser conditions \n{counts}')
    print('Pleasde use the correct number of trials per taste')
    sys.exit()
    # next_step = input('Do you still want to proceed (yes/no)?')
    # if next_step[0].lower() == 'n':
    #     sys.exit()

# touch sensor: Create MPR121 instance via I2C module
i2c=busio.I2C(board.SCL, board.SDA)
# mpr121 = adafruit_mpr121.MPR121(i2c)
cap = adafruit_mpr121.MPR121(i2c)

# # setup nose poke beam break detection
# nosepokeIR = digitalio.DigitalInOut(board.D6)
# nosepokeIR.direction = digitalio.Direction.INPUT
# nosepokeIR.pull = digitalio.Pull.UP

print('\nPress Ctrl-C to quit.\n')
input('===  Please press ENTER to start the experiment! ===')

### wait for the first trial to start
time.sleep(initial_wait)

exp_init_time = time.time()

# trigger the coundown widget window

Popen(['python', './.utils/countdown_main.py',
       f'{exp_dur}'], shell=False)

exp_init = datetime.now() # experimentt starting time as hr,min, sec
# make empty list/dictionary to save lick data
spout_locs = ['Position {}'.format(i) for i in taste_positions]
licks = {spout:[[] for _ in (laser_conditions)] \
         for spout in spout_locs}
ordered_licks = {}

dat_folder = make_dat_folder(proj_path, d)
backup_dir = make_dat_folder(backup_dir, f'{date}')
# create dat_file to recording licking performance
lines_to_save = [saved_dat,
                 'Version #, 0.1',
                 'System ID, 1',
                 f'Start Date, {time.strftime("%Y/%m/%d")}',
                 f'Start Time, {exp_init.hour}:{exp_init.minute}:{exp_init.second}',
                 f'Animal ID, {rat_id}',
                 'Condition,',
                 f'Max Wait for first Lick is, {max_trial_time}',
                 f'Max Number Presentations, {len(trial_list)}',
                 'PRESENTATION,TUBE,CONCENTRATION,SOLUTION,IPI,LENGTH,LICKS,Latency,Laser,Open/Close Error'
                ]
save_lines_to_file(saved_dat, lines_to_save)
dat_file = open(saved_dat, "a")

# making text file to save experimental data / backup purpose
trial_start_time = open(os.path.join(backup_dir, f'{rat_id}_trial_start.txt'), "w")
trial_end_time = open(os.path.join(backup_dir, f'{rat_id}_trial_end.txt'), "w")
lick_latency = open(os.path.join(backup_dir, f'{rat_id}_latency.txt'), "w")
lick_on_trials = open(os.path.join(backup_dir, f'{rat_id}_lick_on_trials.txt'), "w")
latency= {}

col_labels = lines_to_save[9].split(',')
col_width = [len(i) for i in col_labels]

for index, trial in enumerate(trial_list):
    this_trial_start_time = time.time()
    ordered_licks[f'{index}'] = []
    if time.time() - exp_init_time >= exp_dur: # if reaches experiment time, exit the for loop
        break

    #Record trial start time
    trial_start_time.write(repr(this_trial_start_time)+',')
    trial_start_time.flush()
    
    # on-screen reminder
    print("\nTrial {}_spout{} ({}) in Progress~".format(index, trial, solution_seq[index]))
    print(laser_label[lasers[index]])
    #print("\n")
#     np.save('current_trial.npy', np.array(index, dtype=np.int))

    # empty list to save licks for each trial
    this_spout = 'Position {}'.format(trial)
    licks[this_spout][lasers[index]].append([])
    # get the number of current trial for that particular spout
    this_trial_num = len(licks[this_spout]) - 1 
    
    # create Motor instance
    motora = Motor(step, direction, enable, ms1, ms2, ms3)
    motora.init()
    revolution = motora.setStepSize(Motor.SIXTEENTH)

    # turn on lasers if laser is triggered by shutter (trial start)
    if lasers[index] == 1:
        laser_process = Popen(['python', './.utils/deliver_laser.py', 
                               f'{laser_dur}', f'{lasers[index]}'],
                              shell=False)

    # setup surrent and destinate spout positions
    if index == 0:
        cur_pos = 1
        dest_pos = trial_list[0]
    # using rotate_dir function to get the move of the motor
    turn_dir, n_shift = rotate_dir(cur_pos, dest_pos, tot_pos = spout_num)
#     print(f'{turn_dir=}, {cur_pos=}, {dest_pos=}')   
    # rotate motor to move spout outside licking hole
    motora.turn(n_shift * (revolution/spout_num), turn_dir)
    # if turn_dir == -1: # turn clockwise
    #     motora.turn(n_shift * (revolution/spout_num), Motor.CLOCKWISE)
    # else:
    #     motora.turn(n_shift * (revolution/spout_num), Motor.ANTICLOCKWISE)

    trial_init_time = time.time()
    cur_trial_time = max_trial_time
    trial_latency = 0
    print('Start detecting licks')
    this_latency = cur_trial_time
    
    # detecting the current status of touch sensor
    last_touched = cap.touched_pins # return status (touched or not) for each pin as a tuple
    while any(last_touched):
        last_touched = cap.touched_pins # make sure last_touched is not touched
        
    # determine when to exit a trial
    while (time.time() - trial_init_time < cur_trial_time) and \
          (time.time() - exp_init_time < exp_dur):
        current_touched = cap.touched_pins
        # Check each pin's last and current state to see if it was pressed or released.
        for i in range(12):
            # First check if transitioned from not touched to touched.
            if current_touched[i] and not last_touched[i]:
                touch = time.time()

            # Next check if transitioned from touched to not touched.
            if not current_touched[i] and last_touched[i]:
                #print('{0} released!'.format(i))
                release = time.time()

                if release - touch > 0.02: # to avoid noise (from motor)- induced licks
                    licks[this_spout][lasers[index]][-1].append(touch)
                    ordered_licks[f'{index}'].append(touch)

                    if len(licks[this_spout][lasers[index]][-1]) == 1:
                        first_lick = touch
                        this_latency = first_lick - this_trial_start_time
                        if lasers[index] == 2: # laser triggered by first lick 
                            laser_process = Popen(['python', './.utils/deliver_laser.py', 
                                                   f'{laser_dur}', f'{lasers[index]}'],
                                                  shell=False)
                            

                        trial_init_time = first_lick # if lick happens, reset the trial_init time
                        cur_trial_time = max_lick_time # if lick happens, reset trial time to maximal lick time
                    print('{} licked! -- Lick_{}'.\
                          format(this_spout, len(licks[this_spout][lasers[index]][-1])))

        # Update last state and wait a short period before repeating.
        last_touched = current_touched
        time.sleep(0.001)

    # log trial end time
    trial_end_time.write(repr(time.time())+',')
    trial_end_time.flush()
    
    # log lick latency (how long get to lick the spout) and ILIs of this trial
    # construct ILI string list for data saving
    if len(ordered_licks[f'{index}']) > 0:
        lick_latency.write(repr(this_latency)+',')
        lick_trian = ordered_licks[f'{index}']
        ilis = np.diff(lick_trian)
        ilis_str = [repr(round(1000*i)) for i in ilis]
        ilis_str.append('\n')
        ilis_indexed_str = np.insert(ilis_str, 0, repr(index+1))  # trial index starting at 1
        ilis_str = ','.join(ilis_indexed_str)
        lick_on_trials.write(ilis_str)
    
    else: # if no licks
        lick_latency.write(repr(cur_trial_time)+',')
        lick_on_trials.write(repr(index+1)+'\n')
    lick_latency.flush()
    lick_on_trials.flush()
    
    # calculate latency for this trial
    if len(licks[this_spout][lasers[index]][-1]) > 0:
        latency[f'trial_{index}'] = this_latency #first_lick - trial_init_time
    else:
        latency[f'trial_{index}'] = cur_trial_time

    # write data to dat_file
    this_row = [index+1, tube_seq[index], conc_seq[index], solution_seq[index], int(IPI_seq[index])//1000,
                int(Length_seq[index])//1000,
                len(ordered_licks[f'{index}']), round(1000*this_latency), lasers[index], 0]
    formatted_row = ", ".join(f"{str(value).rjust(width)}" for value, width in zip(this_row, col_width))
    dat_file.write(formatted_row + "\n")  # Add a comma at the end of the linedat_file.write()
    dat_file.flush

    
    # find rest_direction
    if index < len(trial_list) - 1:
        rest_dir, _ = rotate_dir(trial_list[index], trial_list[index+1], tot_pos = spout_num)
    else:
        rest_dir = -1
    cur_pos = trial_list[index]
    adjust_dir = 1 if rest_dir == 1 else -1
    dest_pos = cur_pos + adjust_dir
    dest_pos = dest_pos if dest_pos<=spout_num else dest_pos-spout_num
    
    # rotate to rest position
    turn_dir, n_shift = rotate_dir(cur_pos, dest_pos, tot_pos = spout_num)
#     print(f'{turn_dir=}, {cur_pos=}, {dest_pos=}')
    motora.turn(n_shift * (revolution/spout_num), turn_dir)
    # if turn_dir == -1: # turn clockwise
    #     motora.turn(n_shift * (revolution/spout_num), Motor.CLOCKWISE)
    # else:
    #     motora.turn(n_shift * (revolution/spout_num), Motor.ANTICLOCKWISE)

    # setup cur_post and dest_pos for next trial
    if index < len(trial_list) - 1:
        cur_pos, dest_pos = dest_pos, trial_list[index+1]
    else:
        pass
    
    # Reset the motor otherwise it will become hot
    motora.reset()
        
    # print out number of licks being made on this trial
    print('{} licks on Trial {}'.\
          format(len(licks[this_spout][lasers[index]][-1]), index))
    print('\n')
    print(' =====  Inter-Trial Interval =====')
    #print('\n')
    time.sleep(iti) # inter - trial intervals
    
#print(licks)
print("Total number of licks in each spout across laser consitions")
for k, v in licks.items():
    spout_licks = [len(np.concatenate(v[i])) for i in range(len(v))]
    for index, n_licks in enumerate(spout_licks):
        print(f'{k}: laser_con {index} - {n_licks} licks')

# save inter-lick intervals to dat_file
lick_on_trials.close()
with open(os.path.join(backup_dir, f'{rat_id}_lick_on_trials.txt'), 'r') as f:
    dat_file.write("\n")
    dat_file.flush()
    dat_file.write(f.read())
    dat_file.flush()
        
dat_file.close()

# for spout in spout_locs:
#     num_licks_trial = [len(i) for i in licks[spout]]
#     print(spout, num_licks_trial)
#      
#     tot_licks = np.concatenate(licks[spout])
#     print("Total number of licks on {}: {}".format(spout, len(tot_licks)))

with open(os.path.join(backup_dir, "{}_lickTime.pkl".format(rat_id)), 'wb') as handle:
    pickle.dump(licks, handle, protocol=pickle.HIGHEST_PROTOCOL)

# save experimental info
param_dict = {}
param_dict['initial_wait'] = initial_wait
param_dict['exp_dur'] = exp_dur
param_dict['max_trial_time'] = max_trial_time
param_dict['max_lick_time'] = max_lick_time
param_dict['iti'] = iti
param_dict['taste_list'] = {k:t for k, t in zip([f'spout-{(i+1)*2}' for i in range(4)], t_list)}
#param_dict['latency'] = latency
param_dict['trial_list'] = trial_list
param_dict['lasers'] = lasers


"""Save the selected value to a JSON file."""
with open(os.path.join(backup_dir, "{}_all_info.json".format(rat_id)), "w") as file:
    json.dump(param_dict, file)
        
with open(os.path.join(backup_dir, "{}_all_info.pkl".format(rat_id)), 'wb') as handle:
    pickle.dump(param_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
print('\n\n======= Remove rat from the box to its home cage =======')
