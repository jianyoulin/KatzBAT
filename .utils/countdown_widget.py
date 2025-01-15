import tkinter as tk
from tkinter import ttk

class CountdownWidget:
    def __init__(self, root, seconds):
        self.root = root
        self.seconds = seconds
        self.running = False

        # Create a label to display the countdown
        self.label = ttk.Label(root, text=self.format_time(self.seconds), font=("Helvetica", 48))
        self.label.pack(pady=20)

        # Start button
        self.start_button = ttk.Button(root, text="Start", command=self.start_countdown)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop button
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_countdown)
        self.stop_button.pack(side=tk.RIGHT, padx=10)

        # Automatically start the countdown when the widget is created
        self.start_countdown()

    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        mins, secs = divmod(seconds, 60)
        return f"{mins:02}:{secs:02}"

    def start_countdown(self):
        """Start the countdown if it's not already running"""
        if not self.running:
            self.running = True
            self.update_countdown()

    def stop_countdown(self):
        """Stop the countdown"""
        self.running = False

    def update_countdown(self):
        """Update the countdown every second"""
        if self.running and self.seconds > 0:
            self.seconds -= 1
            self.label.config(text=self.format_time(self.seconds))
            self.root.after(1000, self.update_countdown)
        else:
            self.running = False
            self.label.config(text="Time's up!")

    def destroy(self):
        """Destroy the countdown widget"""
        self.root.destroy()