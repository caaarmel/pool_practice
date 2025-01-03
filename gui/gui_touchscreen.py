import tkinter as tk
from tkinter import Canvas

# Initialize GUI
root = tk.Tk()
root.title("Pool Practice Timer - Touchscreen")
root.geometry("480x320")  # Fixed resolution for the 3.5-inch screen

# Header Section
header_frame = tk.Frame(root, bg="darkgreen")
header_frame.pack(fill="x", pady=2)
header_label = tk.Label(header_frame, text="Session: - | Timer: 00:00", bg="darkgreen", fg="white", font=("Arial", 12))
header_label.pack()

# Stats Section
stats_frame = tk.Frame(root, bg="black")
stats_frame.pack(fill="both", expand=True)

stats_label = tk.Label(stats_frame, text="Made: 0 | Missed: 0 | Total: 0", fg="white", bg="black", font=("Arial", 20))
stats_label.pack(pady=10)

# Cue Ball Display
cue_canvas = Canvas(stats_frame, bg="black", width=150, height=150)
cue_canvas.pack(pady=10)
cue_canvas.create_oval(10, 10, 140, 140, fill="white")

# Progress Section
progress_label = tk.Label(root, text="Success: 0%", fg="white", bg="gray", font=("Arial", 12))
progress_label.pack(fill="x", pady=2)

# Footer
feedback_label = tk.Label(root, text="Status: Ready", fg="white", bg="gray", font=("Arial", 12))
feedback_label.pack(fill="x", pady=2)

# Main Loop
def start_touchscreen_gui():
    root.mainloop()