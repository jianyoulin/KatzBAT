import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
import glob
import time
import json

import RPi.GPIO as GPIO
from bipolar_class import Motor
from util_tools import *

########
# global variables and functions
########

# 40 pin header for newer Raspberry Pi's  
# (BPhysicals location, BCM locations)
# GPIO pins used for step motor
board_nums = [38,40,22,12,10,8]
BCM_nums = [24,23,25,18,15,14]
step, direction, enable, ms1, ms2, ms3 = BCM_nums
hall_e = 16 #11

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

# Function to move the stepper motor
def move_stepper(rotate_degree, rotate_dir): 
    motora = Motor(step,direction,enable,ms1,ms2,ms3)
    motora.init()
    revolution = motora.setStepSize(motora.SIXTEENTH) # Motor.EIGHTH
    print(revolution)
    if rotate_degree != 0:
        rotate_steps = revolution/(int(360/rotate_degree))
        motora.turn(rotate_steps, rotate_dir)

def initial_align(he_inport = hall_e, adjust_degree=0):
    motora = Motor(step, direction, enable, ms1, ms2, ms3)
    motora.init()
    # rotate motor to move spout outside licking hole
    revolution = motora.setStepSize(motora.SIXTEENTH)
    motora.home(he_pin = he_inport)
    time.sleep(1)
    
    rotate_dir = 0 if adjust_degree > 0 else 1
    move_stepper(abs(adjust_degree), rotate_dir)
    
class RunBAT:
    def __init__(self, master, window_width=800, window_height=400):
        self.master = master
        self.window_width = window_width
        self.window_height = window_height
        self.master.title("Experiment Information")
        self.master.geometry(f"{self.window_width}x{self.window_height}")

        # Variable to store the selected value
        self.selected_value = tk.IntVar()  # Use IntVar to store the selected value

        # Variable to store the selected value
        self.laser_value = tk.BooleanVar()

        # Create a frame to hold data file name and to-be-saved folder
        self.data_frame = tk.Frame(self.master, relief=tk.RIDGE, borderwidth=4)
        self.data_frame.grid(row=0, column=2, rowspan=5,
                             padx=15, pady=15) #, sticky="nsew")

        # Create a frame to hold motor adjustment widgets
        self.motor_frame = tk.Frame(self.master, relief=tk.RIDGE, borderwidth=4)
        self.motor_frame.grid(row=4, column=0, rowspan=5, columnspan=2, 
                              padx=20, pady=10) #, sticky="nsew")

        # Create a frame to hold selection widgets for motor types
        self.mtype_frame = tk.Frame(self.motor_frame, relief=tk.RIDGE, borderwidth=4)
        self.mtype_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5) #, sticky="nsew")

        # Initialize the UI
        self.create_widgets()
        self.create_motor_widgets()

    def create_widgets(self):
        # RatID label and entry
        ratID_label = tk.Label(self.master, text="RatID:")
        ratID_label.grid(row=0, column=1, padx=10, pady=10) #, sticky="e")

        self.ratID_entry = tk.Entry(self.master)
        self.ratID_entry.insert(0, "ratID")
        self.ratID_entry.grid(row=1, column=1, padx=10, pady=10) #, sticky="w")
        self.ratID_entry.bind("<KeyRelease>", self.update_fileName)

        # Dropdown menu for data folder
        folder_options = self.list_data_dirs()
        try:
            with open('./.utils/prior_selected_folder.txt', 'r') as f:
                prior_f = f.readline().strip()
                f_index = folder_options.index(prior_f)
                folder_options[0], folder_options[f_index] = folder_options[f_index], folder_options[0]
                print(prior_f, f_index)
        except:
            print('No prior selected folder is found')

        self.datFolder_var = tk.StringVar(value=folder_options[0])
        dropdown_label = tk.Label(self.data_frame, text="Select data folder:")
        dropdown_label.grid(row=0, column=0, padx=10, pady=10) #, sticky="w")

        # dropdown_menu = tk.OptionMenu(self.data_frame, self.datFolder_var, *folder_options)
        # dropdown_menu.grid(row=1, column=0, padx=10, pady=10) #, sticky="w")
        # dropdown_menu.config(bg="darkgreen")

        dropdown_menu = tk.OptionMenu(self.data_frame, self.datFolder_var, *folder_options,
                                      command=self.update_selection)
        dropdown_menu.grid(row=1, column=0, padx=10, pady=5) #, sticky="w")
        dropdown_menu.config(bg="darkgreen")

        # Label to display the selected value
        self.flabel = tk.Label(self.data_frame, text="Selected: None")
        self.flabel.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            

        # File name label and entry
        fileName_label = tk.Label(self.data_frame, text="File name:")
        fileName_label.grid(row=3, column=0, padx=5, pady=10) #, sticky="w")

        self.fileName_entry = tk.Entry(self.data_frame)
        self.fileName_entry.insert(0, f"{time.strftime('%Y%m%d')}ratID.txt")
        self.fileName_entry.grid(row=4, column=0, padx=5, pady=10) #, sticky="w")

        # Dropdown menu for protocol file
        protocol_options = self.list_params_files()
        try:
            with open('./.utils/prior_selected_protocol.txt', 'r') as f:
                prior_p = f.readline().strip()
                p_index = protocol_options.index(prior_p)
                protocol_options[0], protocol_options[p_index] = protocol_options[p_index], protocol_options[0]
                print(prior_p, p_index)
        except:
            print('No prior selected protocol is found')

        self.protocol_var = tk.StringVar(value=protocol_options[0])
        protocol_label = tk.Label(self.master, text="Select protocol file:")
        protocol_label.grid(row=0, column=0, padx=10, pady=10) #, sticky="e")

        protocol_menu = tk.OptionMenu(self.master, self.protocol_var, *protocol_options)
        protocol_menu.grid(row=1, column=0, padx=10, pady=10) #, sticky="w")
        protocol_menu.config(bg="darkgreen")

        # checkbox for using laser or not
        laser_checkbox = tk.Checkbutton(self.master, text="Using laser?", variable=self.laser_value, 
                                        onvalue=True, offvalue=False)
        laser_checkbox.grid(row=7, column=2, padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(self.master, text="Submit", command=self.submit)
        submit_button.grid(row=8, column=2, padx=10, pady=10) #, sticky="se")

    def create_motor_widgets(self):
        # Create labels for the buttons
        self.adjust_button = tk.Button(self.motor_frame, text="Stepper alignment",
                                   command=self.open_adjust_window)
        self.adjust_button.grid(row=0, column=0, rowspan=2, columnspan=2, 
                              padx=20, pady=20)

        # motor_frame_title = tk.Button(self.motor_frame, text="Initialize and align motor", 
        #                               command=self.subtract_number)
        # motor_frame_title.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # # Create labels for the buttons
        # subtract_label = tk.Label(self.motor_frame, text="Counter-\nClockwise")
        # subtract_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        # add_label = tk.Label(self.motor_frame, text="Clockwise")
        # add_label.grid(row=1, column=2, padx=10, pady=10, sticky="w")

        # # Create buttons and entry
        # subtract_button = tk.Button(self.motor_frame, text="-", command=self.execute_external_function)
        # subtract_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        # self.entry = tk.Entry(self.motor_frame, justify='center')
        # self.entry.insert(0, "0")
        # self.entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # add_button = tk.Button(self.motor_frame, text="+", command=self.execute_external_function)
        # add_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")

        self.create_selection_widgets()

    def create_selection_widgets(self):
        """Create and place widgets inside the frame."""
        # Radio buttons for single selection
        radio1 = tk.Radiobutton(self.mtype_frame, text="8 positions", variable=self.selected_value, value=4)
        radio1.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        radio2 = tk.Radiobutton(self.mtype_frame, text="12 positions", variable=self.selected_value, value=8)
        radio2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        radio3 = tk.Radiobutton(self.mtype_frame, text="16 positions", variable=self.selected_value, value=16)
        radio3.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    def execute_external_function(self):
        # Call the external function here
        external_function()

    def update_fileName(self, *args):
        """Update the file name based on RatID."""
        ratID = self.ratID_entry.get()
        if ratID:
            self.fileName_entry.delete(0, tk.END)
            self.fileName_entry.insert(0, f"{time.strftime('%Y%m%d')}{ratID}.txt")

    def update_selection(self, selected):
        """Update the label with the selected value."""
        if selected == "Custom":
            self.open_custom_popup()  # Open the pop-up if "Custom" is selected
        else:
            self.flabel.config(text=f"Selected: {selected}")

    def open_custom_popup(self):
        """Open a pop-up window for custom input."""
        self.popup = tk.Toplevel(self.data_frame) #master)  # Create a pop-up window
        self.popup.title("Custom Option")
        self.popup.geometry("300x100")

        # Label and Entry for custom input
        tk.Label(self.popup, text="Enter custom folder name:").grid(row=0, column=0, padx=10, pady=5)
        self.custom_entry = tk.Entry(self.popup)
        self.custom_entry.grid(row=1, column=0, padx=10, pady=5)

        # Button to confirm the custom input
        confirm_button = tk.Button(self.popup, text="Confirm", command=self.confirm_custom_input)
        confirm_button.grid(row=2, column=0, padx=10, pady=5)

    def confirm_custom_input(self, path='./KatzBATDats/'):
        """Confirm the custom input and update the selected value."""
        custom_value = self.custom_entry.get().strip()  # Get the custom input
        if custom_value:
            update_path = path + custom_value
            self.datFolder_var.set(update_path)  # Update the selected value
            self.popup.destroy()  # Close the pop-up window
            self.update_selection(update_path)  # Update the displayed selection
        else:
            messagebox.showwarning("Invalid Input", "Please enter a custom folder.")

    def list_params_files(self):
        """List parameter files."""
        path = Path(os.path.join(os.getcwd(), 'Parameters'))
        files = os.listdir(path)
        return [f for f in files if '.pro' in f]

    def list_data_dirs(self, path='./KatzBATDats/'):
        """List data directories."""
        path = Path(path)
        items = glob.glob(os.path.join(path, '*'))
        options = [i for i in items if os.path.isdir(i)]
        options.append('Custom')
        return options

       # Function to open a new window with a countdown timer
    def open_adjust_window(self):
        # Create a new window
        self.adjust_window = tk.Toplevel(self.master)
        self.adjust_window.title("Motor Adjustment")

        # create a button for initial homing
        self.inital_home = tk.Button(self.adjust_window, text="Initial \nHoming",
                                     command=self.initial_homing)
        self.inital_home.grid(row=0, column=0, rowspan=2, columnspan=2, 
                              padx=20, pady=10)
        
        self.adjust_frame = tk.Frame(self.adjust_window, 
                                     relief=tk.RIDGE, borderwidth=4)
        self.adjust_frame.grid(row=2, column=0, rowspan=4, columnspan=2, 
                              padx=10, pady=10) #, sticky="nsew")
        # Direction Selection
        self.direction = tk.IntVar(value=0)
        clockwise = tk.Radiobutton(self.adjust_frame, text="Clockwise",
                       variable=self.direction, value=0)
        clockwise.grid(row=0, column=1, padx=10, pady=10)

        counter_clockwise = tk.Radiobutton(self.adjust_frame, text="Counter-Clockwise", variable=self.direction, value=1)
        counter_clockwise.grid(row=0, column=0, padx=10, pady=10)

        # Degrees Entry
        degree_label = tk.Label(self.adjust_frame, text="Degrees:")
        degree_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.drgrees_entry = tk.Entry(self.adjust_frame)
        self.drgrees_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Move Button
        self.move_button = tk.Button(self.adjust_frame, text="Move",
                                     command=self.move_motor)
        self.move_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        # Done_adjustment Button
        self.done_button = tk.Button(self.adjust_frame, text="Done with alignment",
                                     command=self.done)
        self.done_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def move_motor(self):
        degrees = int(self.drgrees_entry.get())
        direction = self.direction.get()
        move_stepper(degrees, direction)
        
    def initial_homing(self):
        initial_align(he_inport = hall_e, adjust_degree=0)
        
    def done(self):
        self.adjust_window.destroy()
        
    def add_number(self):
        try:
            current_value = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(current_value + 1))
        except ValueError:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0")

    def subtract_number(self):
        try:
            current_value = int(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(current_value - 1))
        except ValueError:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0")

    def save_to_json(self, dict):
        """Save the selected value to a JSON file."""
        with open("./.utils/exp_info.json", "w") as file:
            json.dump(dict, file)
        print("Selection saved to 'exp_info.json'.")

    def submit(self):
        """Submit data and close the application."""
        ratID = self.ratID_entry.get()
        datFolder = self.datFolder_var.get()
        fileName = self.fileName_entry.get()
        protocol = self.protocol_var.get()
        spots_num = self.selected_value.get()
        laser = self.laser_value.get()

        with open('./.utils/prior_selected_protocol.txt', 'w') as f:
            f.write(protocol)
        with open('./.utils/prior_selected_folder.txt', 'w') as f:
            f.write(datFolder)

        if ratID:
            submitted_data = {
                "ratID": ratID,
                "datFolder": datFolder,
                "fileName": fileName,
                "protocol": protocol,
                "spots_num": spots_num,
                "laser_used": laser,
            }

            messagebox.showinfo("Input Received", f"RatID: {ratID}\nData Folder: {datFolder}\nFile Name: {fileName}\nProtocol: {protocol}")
            self.expInfo = submitted_data
            self.save_to_json(submitted_data)
            self.master.destroy()
        else:
            messagebox.showwarning("Missing Information", "Please fill out all fields.")


if __name__ == "__main__":
    root = tk.Tk()
    app = RunBAT(root)
    root.mainloop()

    # Cleanup GPIO on exit
    GPIO.cleanup()