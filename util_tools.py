import sys
import os
import time
from pathlib import Path
import numpy as np
import pickle
# import easygui
import json

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import subprocess
import glob
from pathlib import Path

# text_file = 'JY_tested.pro'
def var_data(text_file, var_name=None):
    """
    Reads a text file and extracts the data associated with a specific variable name.

    Parameters:
        text_file (str): Path to the text file to read.
        var_name (str, optional): Name of the variable to search for. If None, no specific variable is searched.

    Returns:
        list or numpy.nan: A list of data values associated with the variable name, or numpy.nan if not found.
    """

    import numpy as np
    
    with open(text_file, 'r') as f:
        while True:
            this_line = f.readline()
            if len(this_line) == 0:
                break

            if '=' in this_line:
                if this_line.split('=')[0] == var_name:
                    dat = this_line.split('=')[1].strip().split(',')
                    break
                else:
                    dat = np.nan
    try:
        if np.isnan(dat): 
            print(f"Can't find the data associated with variable name as {var_name}")
    except:
        pass

    return dat

# function for testing in RunBAT class

def external_function():
    print("Hello from the external function!")

def read_json_file(fname = "./.utils/exp_info.json"):
    """Read and display the selected value from the JSON file."""
    try:
        with open(fname, "r") as file:
            data = json.load(file)
            # selected_value = data.get("selected_value")
            # print(f"Selected value read from JSON: {selected_value}")
        return data
    except FileNotFoundError:
        print(f"The file '{fname}' does not exist. Please make a selection first.")
    except json.JSONDecodeError:
        print(f"The file '{fname}' is corrupted or invalid.")
        
# detect and make a datafolder
def make_dat_folder(path, datF_name=None):
    new_dir = os.path.join(path, datF_name)
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    else:
        print(f"Do nothing as {datF_name} exists")
    return new_dir

def save_lines_to_file(filename, lines):
    """Saves multiple lines of text to a file.

    Args:
        filename: The name of the file to save to.
        lines: A list of strings representing the lines to write.
    """

    with open(filename, "w") as file:
        labels = lines[9].split(',')
        # Desired column widths
        column_widths = [len(i) for i in labels]
        for i, row in enumerate(lines):
            #print(i, row)
            if i < 9:
                file.write(row + ",\n")  # Add a comma at the end of the line
            else:
                row_splitted = row.split(',')
                # Format each column to be right-aligned and end with a comma
                formatted_row = ", ".join(f"{str(value).rjust(width)}" \
                                          for value, width in zip(row_splitted, 
                                                                  column_widths))
                file.write(formatted_row + ",\n")
    print(f"Data written to {filename}")

# motor pinouts
step = 24
direction = 23
enable = 25     # Not required - leave unconnected
ms1 = 18
ms2 = 15
ms3 = 14
he_pin = 16 # Hall effect pin
# motor_pinouts = {'step': 24,
#                  'direction': 23,
#                  'enable': 25,
#                  'ms1': 18,
#                  'ms2': 15,
#                  'ms3': 14,
#                  'he_pin': 16
#                 }
                     
    # # Create a frame for Name and Address
    # data_frame = tk.Frame(root, relief=tk.RIDGE, borderwidth=2)
    # data_frame.place(x=500, y=10, width=200, height=250)
    
    # # Create and place dropdown menu for which protocol to run
    # protocol_options = list_params_files()
    # protocol_var = tk.StringVar(value=protocol_options[0])
    # dropdown_label = tk.Label(root, text="Select protocol file:", bg="white")
    # dropdown_label.place(x=80, y=30)
    # dropdown_menu = ttk.OptionMenu(root, protocol_var, *protocol_options)
    # dropdown_menu.place(x=80, y=60)
    
    # # Create and place labels and entry fields for name, address, birthday, and folder
    # ratID_label = tk.Label(root, text="RatID:", bg="white")
    # ratID_label.place(x=330, y=30)
    # ratID_entry = tk.Entry(root) #, width=30)
    # ratID_entry.insert(0, "ratID")
    # ratID_entry.place(x=280, y=60)
    # ratID_entry.bind("<KeyRelease>", update_fileName)
    
    # # Create and place dropdown menu for which folder to save data
    # folder_options = list_data_dirs()
    # datFolder_var = tk.StringVar(value=folder_options[0])
    # dropdown_label = tk.Label(data_frame, text="Select data folder:", bg="white")
    # dropdown_label.place(x=50, y=20)
    # dropdown_menu = ttk.OptionMenu(data_frame, datFolder_var, *folder_options)
    # dropdown_menu.place(x=50, y=50)
    
    # # Create and place labels and entry fields for name, address, birthday, and folder
    # fileName_label = tk.Label(data_frame, text="File name:", bg="white")
    # fileName_label.place(x=75, y=160)
    # fileName_entry = tk.Entry(data_frame) #, width=30)
    # fileName_entry.insert(0, f"{time.strftime('%Y%m%d')}{ratID_entry.get()}.txt")
    # fileName_entry.place(x=50, y=190)
    
    # # Create and place the submit button
    # submit_button = tk.Button(root, text="Submit", command=self.submit)
    # submit_button.place(x=400, y=300)
    
    # # Start the Tkinter event loop
    # root.mainloop()
    # return submitted_data