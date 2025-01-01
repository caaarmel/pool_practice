import tkinter as tk
from tkinter import BOTH

# Main GUI Window
root = tk.Tk()
root.title("Pool Practice Timer - Simple Monitor")
root.configure(bg='black')

# Fullscreen Behavior
root.geometry("1024x600")
root.state('zoomed')

# ---------------- HEADER SECTION ----------------
header_frame = tk.Frame(root, bg='green', height=60)
header_frame.pack(fill='x', side='top')

timer_label = tk.Label(header_frame, text="00:00", font=("Arial", 32, 'bold'), fg='white', bg='green')
timer_label.pack(expand=True)

# ---------------- MIDDLE SECTION ----------------
middle_frame = tk.Frame(root, bg='black')
middle_frame.pack(fill=BOTH, expand=True)

# LEFT: Shot Summary + Progress Bar
left_frame = tk.Frame(middle_frame, bg='black', width=300)
left_frame.pack(side='left', fill='both', expand=True)

progress_canvas = tk.Canvas(left_frame, bg='white', width=20, highlightthickness=0)
progress_canvas.pack(side='left', fill='y')

stats_frame = tk.Frame(left_frame, bg='black')
stats_frame.pack(fill='both', expand=True)

stats_label = tk.Label(stats_frame, text="Total Shots: 0\nShots Made: 0\nShots Missed: 0",
                       font=("Arial", 24), fg='white', bg='black', justify='left')
stats_label.place(relx=0.5, rely=0.5, anchor='center')

# RIGHT: Cue Ball Graphic + English Indicator
right_frame = tk.Frame(middle_frame, bg='black')
right_frame.pack(side='right', fill='both', expand=True)

cue_canvas = tk.Canvas(right_frame, bg='black', highlightthickness=0)
cue_canvas.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.6, relheight=0.6)

# Draw Cue Ball
cue_canvas.create_oval(0, 0, cue_canvas.winfo_reqwidth(), cue_canvas.winfo_reqheight(),
                       fill='white', outline='black')

# English Indicator Text
english_label = tk.Label(right_frame, text="English: Center", font=("Arial", 16), fg='white', bg='black')
english_label.place(relx=0.5, rely=0.9, anchor='center')

# ---------------- FOOTER SECTION ----------------
footer_frame = tk.Frame(root, bg='gray', height=30)
footer_frame.pack(fill='x', side='bottom')

feedback_label = tk.Label(footer_frame, text="Action Feedback: Ready", font=("Arial", 14), fg='white', bg='gray')
feedback_label.pack(expand=True)

# ---------------- RESPONSIVE BEHAVIOR ----------------
def resize_elements(event):
    # Ensure the cue ball stays centered
    cue_canvas.delete('all')
    size = min(right_frame.winfo_width(), right_frame.winfo_height()) * 0.6
    cue_canvas.config(width=size, height=size)
    cue_canvas.create_oval(0, 0, size, size, fill='white', outline='black')

    # Adjust stats dynamically
    stats_label.config(font=("Arial", max(16, int(left_frame.winfo_height() * 0.05))))

root.bind("<Configure>", resize_elements)

# Start GUI Loop
root.mainloop()
