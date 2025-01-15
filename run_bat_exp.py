# this code initiates a window to collect information the experiment to run
# ask the user to specify
# 1) experimental protocol
# 2) Rat ID
# 3) data name and folder to be saved
# 4) using laser or not
# 5) align the motor to "Zero" 
# once information is collected, execute the correponding script 
# execute the code with python run_bat.py 

import sys
import os
import time
from datetime import datetime, date
from pathlib import Path
import numpy as np
import pickle
# import easygui
import json

import board
import busio
import digitalio
import adafruit_mpr121

import atexit
from bipolar_class import Motor
from bipolar_class import rotate_dir

import subprocess
import signal
from subprocess import Popen, PIPE

from util_tools import *
from RunBAT_grid import RunBAT

# def read_json_file(fname = "exp_info.json"):
#     """Read and display the selected value from the JSON file."""
#     try:
#         with open(fname, "r") as file:
#             data = json.load(file)
#         return data
#     except FileNotFoundError:
#         print(f"The file '{fname}' does not exist. Please make a selection first.")
#     except json.JSONDecodeError:
#         print(f"The file '{fname}' is corrupted or invalid.")

proj_path = os.getcwd() #'/home/rig337-testpi/Desktop/katz_lickometer'
print(proj_path)

# open GUI to get Exp info
root = tk.Tk()
app = RunBAT(root)
root.mainloop()

submitted_data = app.expInfo


if submitted_data['laser_used']:   
    print('Laser will be used in your experiment!!')
    print('\n --Place a Goggle on your rodent-- \n')
#     try:
#         subprocess.run(["python", "katz_BAT_lasers_v1.py"]) #, check=True)
#         messagebox.showinfo("Success", "Script executed successfully.")
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to execute script: {e}")
else:
#     try:
#         subprocess.run(["python", "katz_BAT_v2.py"], check=True)
#         messagebox.showinfo("Success", "Script executed successfully.")
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to execute script: {e}")
    print('You are good to go')

try:
    subprocess.run(["python", "katz_BAT.py"]) #, check=True)
#     messagebox.showinfo("Success", "Script executed successfully.")
except Exception as e:
    messagebox.showerror("Error", f"Failed to execute script: {e}")
