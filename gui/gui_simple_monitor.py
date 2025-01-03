import math
import tkinter as tk
from tkinter import ttk  # Import ttk for Progressbar and other themed widgets
import queue


def start_gui(gui_queue):
    global root
    # Main GUI Window
    root = tk.Tk()
    root.title("Pool Practice Timer - Simple Monitor")
    root.geometry("1024x600")
    root.configure(bg='black')

    # Fullscreen Behavior
    # root.state('zoomed') #removing for now

    # ---------------- HEADER SECTION ----------------
    header_frame = tk.Frame(root, bg='gray', height=60)
    header_frame.pack(fill='x', side='top')

    header_label = tk.Label(
        header_frame,
        text="Session ID: - | Timer: 00:00",
        font=("Arial", 24, 'bold'),
        fg='white',
        bg='gray'
    )
    header_label.pack(expand=True)


    # ---------------- MIDDLE SECTION ----------------
    middle_frame = tk.Frame(root, bg='black')
    middle_frame.pack(fill='both', expand=True)

    # LEFT: Shot Summary + Progress Bar (2/3 of space)
    left_frame = tk.Frame(middle_frame, bg='black')
    left_frame.place(relx=0, rely=0, relwidth=0.67, relheight=1)  # 2/3 of width
    
    stats_label = tk.Label(
        left_frame,
        # stats_frame,
        text="Made: 0\nMissed: 0\n\nTotal: 0",
        font=("Arial", 28),
        fg='white',
        bg='black',
        justify='center',
        anchor='center'
    )
    stats_width = left_frame.winfo_width()
    stats_height = left_frame.winfo_height()
    padding_x = max(stats_width // 20, 10)
    padding_y = max(stats_height // 20, 10)
    stats_label.pack_configure(padx=padding_x, pady=padding_y)
    stats_label.pack(expand=True, fill='both')

    # RIGHT: Cue Ball Graphic + English Indicator
    right_frame = tk.Frame(middle_frame, bg='black')
    right_frame.place(relx=0.66, rely=0, relwidth=0.34, relheight=1.0)  # Takes 1/3 of the width

    cue_canvas = tk.Canvas(right_frame, bg='black', highlightthickness=0)
    cue_canvas.pack(expand=True, fill='both')
    cue_canvas.create_oval(0, 0, 100, 100, fill='white', outline='black')

    english_label = tk.Label(
        right_frame,
        text="Center",
        font=("Arial", 16),
        fg='white',
        bg='black',
        justify='center',
        anchor='center'
    )
    english_label.pack(pady=10)

    # ---------------- DYNAMIC RESIZING ----------------

    def draw_cue_ball_with_spin(english='Center'):
        """
        Draw the cue ball and red dot based on the current spin state,
        ensuring the red dot never exceeds the edge.
        """
        canvas_width = cue_canvas.winfo_width()
        canvas_height = cue_canvas.winfo_height()
        size = min(canvas_width, canvas_height) * 0.8  # Cue ball scales to 80% of the smaller dimension

        cue_canvas.delete("all")  # Clear existing graphic

        # Draw Cue Ball
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        radius = size / 2
        cue_canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill='white', outline='black'
        )

        # Calculate Red Dot Position Based on Spin State
        # print(f"🌀 Spin State: {english}")  # Debug print
        dot_radius = radius * 0.08  # The red dot is 8% of the cue ball radius

        # Default Dot Position (Center)
        dot_x, dot_y = center_x, center_y

        # Parse the English State
        spin_parts = english.split('+')
        x_offset, y_offset = 0, 0

        # Define weight for max and non-max spins
        SPIN_WEIGHTS = {
            'Top': -0.25,
            'Max Top': -0.85,  # Slightly less than the edge
            'Stun': 0.25,
            'Max Draw': 0.85,
            'Left': -0.25,
            'Max Left': -0.85,
            'Right': 0.25,
            'Max Right': 0.85
        }

        for part in spin_parts:
            part = part.strip()
            if part in ['Top', 'Max Top', 'Stun', 'Max Draw']:
                y_offset += SPIN_WEIGHTS.get(part, 0)
            elif part in ['Left', 'Max Left', 'Right', 'Max Right']:
                x_offset += SPIN_WEIGHTS.get(part, 0)

        # Normalize for diagonal combinations
        magnitude = math.sqrt(x_offset ** 2 + y_offset ** 2)
        if magnitude > 0:
            scaling_factor = min(1.0, 0.85 / magnitude)  # Keep magnitude within 85% of the radius
            x_offset *= scaling_factor
            y_offset *= scaling_factor

        # Apply offset to calculate final dot position
        dot_x = center_x + (x_offset * radius)
        dot_y = center_y + (y_offset * radius)

        # Draw Red Dot
        cue_canvas.create_oval(
            dot_x - dot_radius, dot_y - dot_radius,
            dot_x + dot_radius, dot_y + dot_radius,
            fill='red', outline=''
        )

        # print(f"🔴 Red Dot Drawn at: ({dot_x}, {dot_y})")



    
    # Update resize_widgets function to ensure redraw
    def resize_widgets(event):
        stats_width = left_frame.winfo_width()
        stats_height = left_frame.winfo_height()
        
        if stats_width > 0 and stats_height > 0:
            new_font_size = min(stats_width // 10, stats_height // 5)
            new_font_size = max(new_font_size, 18)
            stats_label.config(font=("Arial", new_font_size))

        padding_x = max(stats_width // 20, 10)
        padding_y = max(stats_height // 20, 10)
        stats_label.pack_configure(padx=padding_x, pady=padding_y)

        draw_cue_ball_with_spin(english_label.cget("text").split(":")[-1].strip())


    # ---------------- FOOTER SECTION ----------------
    footer_frame = tk.Frame(root, bg='gray', height=30)
    footer_frame.pack(fill='x', side='bottom')

    feedback_label = tk.Label(
        footer_frame,
        text="Action Feedback: Ready",
        font=("Arial", 14),
        fg='white',
        bg='gray'
    )
    feedback_label.pack(expand=True)

    # ---------------- SUCCESS BAR ----------------
    progress_label = tk.Label(
        root,
        text="Success Percentage: 0%",
        font=("Arial", 16),
        fg='white',
        bg='black'
    )
    progress_label.pack()
    progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
    progress_bar.pack(pady=10)

    # ---------------- GUI UPDATE LOOP ----------------
    def update_gui():
        try:
            while not gui_queue.empty():
                data = gui_queue.get_nowait()
                # print("🛠️ GUI Debug (Data Received):", data)

                # Header Updates
                if 'session_id' in data:
                    session_active = data.get('session_active', False)
                    header_label.config(
                        text=f"Session ID: {data.get('session_id', '-')} | Timer: {data.get('timer', '00:00')}"
                    )
                                
                # Stats Updates
                if 'stats' in data:
                    stats = data['stats']
                    stats_label.config(
                        text=f"Made: {stats.get('made', 0)}\n"
                            f"Missed: {stats.get('missed', 0)}\n\n"
                            f"Total: {stats.get('total', 0)}\n"
                    )
                
                # Success Percentage Updates
                if 'progress' in data:
                    progress_percentage = data['progress'].get('percentage', 0)
                    progress_label.config(text=f"Success Percentage: {progress_percentage}%")
                    progress_bar['value'] = progress_percentage
                
                # Cue Ball English Updates
                if 'english' in data:
                    english_label.config(text=f"English: {data['english']}")
                    draw_cue_ball_with_spin(data['english'])
                
                # Feedback Message
                if 'feedback' in data:
                    feedback_label.config(text=data['feedback'])
        
        except queue.Empty:
             print("⚠️ GUI Debug (Queue Empty)")
             pass

        root.after(100, update_gui)  # Schedule the next update

    update_gui()
    # print(" GUI MAIN LOOP STARTING")
          
    
    # Start GUI Update Loop
    root.mainloop()

if __name__ == '__main__':
#    print("🚀 Starting GUI Directly")
    import tkinter as tk
    import queue

    gui_queue = queue.Queue()

    # Start GUI
    start_gui(gui_queue)