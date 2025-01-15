import tkinter as tk
import sys
from countdown_widget import CountdownWidget

def main(dur):
    root = tk.Tk()
    root.title("Countdown Timer App")

    # Create a countdown widget with a 30-second countdown
    countdown = CountdownWidget(root, dur)

    # Add a button to destroy the countdown widget
    destroy_button = tk.Button(root, text="Close Countdown", command=countdown.destroy)
    destroy_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main(int(sys.argv[1]))