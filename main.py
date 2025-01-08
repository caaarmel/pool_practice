import pygame
import threading
import queue
import platform
from game_logic import (
    start_session,
    end_session,
    toggle_spin,
    record_shot,
    undo_last_shot,
    get_elapsed_time,
    get_last_session_stats,
    get_recent_sessions
)

from session_state import session_state

# Check if running on Raspberry Pi (ARM platform)
if platform.system() == "Linux" and "arm" in platform.machine():
    from gui.gui_touchscreen import start_touchscreen_gui
    start_touchscreen_gui()
else:
    from gui.gui_simple_monitor import start_gui
    


# 🎮 Controller Initialization
pygame.init()
controller = None
for i in range(pygame.joystick.get_count()):
    controller = pygame.joystick.Joystick(i)
    controller.init()
    print(f"🎮 Controller connected: {controller.get_name()}")

# GUI Queue for Communication
gui_queue = queue.Queue()

# Track previous button states
previous_button_state = {
    'start': False, 'select': False, 'undo': False,
    'potted': False, 'missed': False,
    'x': False, 'b': False, 'y': False, 'a': False
}

# GUI Thread - Only One Time
# Start GUI Thread Once
if 'gui_thread' not in globals() or not threading.active_count() > 1:
    # print("🚀 Starting GUI Thread")
    gui_thread = threading.Thread(target=start_gui, args=(gui_queue,), daemon=True)
    gui_thread.start()
else:
    print("✅ GUI Thread already running")


# Application State
running = True

# 🎯 Main Loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # BUTTON PRESS EVENTS
        if event.type == pygame.JOYBUTTONDOWN:
            # Start/End Session (Mapped to Start Button)
            if event.button == 7 and not previous_button_state['start']:  # Start Button
                if session_state['session_active']:
                    end_session()
                    session_state['session_active'] = False
                    gui_queue.put({'session_active': False, 'feedback': 'Session ended!'})
                else:
                    start_session()
                    session_state['session_active'] = True
                    gui_queue.put({'session_id': 1, 'timer': '00:00', 'session_active': True, 'feedback': 'Session started!'})
                previous_button_state['start'] = True
                
            # ↩️ Undo Shot (Select Button)
            if event.button == 6 and not previous_button_state['select']:  # Select Button
                undo_last_shot()
                gui_queue.put({'feedback': 'Undo Last Shot!'})
                previous_button_state['select'] = True

            # ✅ Ball Potted (Right Trigger, Button 5)
            if event.button == 5 and not previous_button_state['potted']:  # Right Trigger
                record_shot(result='Potted')
                gui_queue.put({'feedback': 'Shot Potted!', 'stats': {
                    'total': session_state['total_shots'],
                    'made': session_state['balls_potted'],
                    'missed': session_state['balls_missed']
                }})
                previous_button_state['potted'] = True

            # ❌ Ball Missed (Left Trigger, Button 4)
            if event.button == 4 and not previous_button_state['missed']:  # Left Trigger
                record_shot(result='Missed')
                gui_queue.put({'feedback': 'Shot Missed!', 'stats': {
                    'total': session_state['total_shots'],
                    'made': session_state['balls_potted'],
                    'missed': session_state['balls_missed']
                }})
                previous_button_state['missed'] = True

            # 🌀 Spin Controls with Debouncing
            if event.button == 3 and not previous_button_state['x']:  # X Button - Top
                toggle_spin('top')
                session_state['current_spin_display'] = 'Top'
                gui_queue.put({'feedback': 'Top Spin Applied!'})
                previous_button_state['x'] = True

            if event.button == 0 and not previous_button_state['b']:  # B Button - Bottom
                toggle_spin('bottom')
                session_state['current_spin_display'] = 'Bottom'
                gui_queue.put({'feedback': 'Bottom Spin Applied!'})
                previous_button_state['b'] = True

            if event.button == 2 and not previous_button_state['y']:  # Y Button - Left
                toggle_spin('left')
                session_state['current_spin_display'] = 'Left'
                gui_queue.put({'feedback': 'Left Spin Applied!'})
                previous_button_state['y'] = True

            if event.button == 1 and not previous_button_state['a']:  # A Button - Right
                toggle_spin('right')
                session_state['current_spin_display'] = 'Right'
                gui_queue.put({'feedback': 'Right Spin Applied!'})
                previous_button_state['a'] = True

        # 🛑 Reset Spin States on Button Release
        if event.type == pygame.JOYBUTTONUP:
            for key in previous_button_state:
                previous_button_state[key] = False
        
    # 🖥️ Display State
    # 🌀 Display Spin State
    spin_state = " + ".join([
    ('Top' if session_state['current_spin'].get('top') == 1 else 'Max Top') if session_state['current_spin'].get('top') else '',
    ('Stun' if session_state['current_spin'].get('bottom') == 1 else 'Max Draw') if session_state['current_spin'].get('bottom') else '',
    ('Left' if session_state['current_spin'].get('left') == 1 else 'Max Left') if session_state['current_spin'].get('left') else '',
    ('Right' if session_state['current_spin'].get('right') == 1 else 'Max Right') if session_state['current_spin'].get('right') else ''
])

    # Remove any extra '+' caused by empty strings
    spin_state = " + ".join(filter(None, spin_state.split(" + "))) or "Center"

    session_state['current_spin_display'] = spin_state

    if not session_state['session_active']:
        last_stats = get_last_session_stats()
        recent_sessions = get_recent_sessions(limit=3)

        if last_stats:
            gui_queue.put({
                'session_active': False,
                'feedback': 'No active session - Displaying last session stats',
                'last_session': {
                    'duration': round(int(last_stats['duration'] / 60)),
                    'total_shots': last_stats['total_shots'],
                    'balls_potted': last_stats['balls_potted'],
                    'balls_missed': last_stats['balls_missed'],
                },
                'recent_sessions': recent_sessions  # Ensure recent_sessions is included
            })
        else:
            gui_queue.put({
                'session_active': False,
                'feedback': 'No active session and no previous session data available',
                'recent_sessions': recent_sessions
            })


    if session_state.get('session_active', False):
        gui_event = {
        'timer': f'{get_elapsed_time() // 60:02}:{get_elapsed_time() % 60:02}',
        'session_id': session_state['session_id'],
        'session_active': session_state['session_active'],
        'feedback': 'Timer Updated!',
        'stats': {
            'total': session_state['total_shots'],
            'made': session_state['balls_potted'],
            'missed': session_state['balls_missed']
        },
        'progress': {
            'percentage': round((session_state['balls_potted'] / session_state['total_shots']) * 100) if session_state['total_shots'] else 0
        },
        'english': session_state['current_spin_display']
        }
        gui_queue.put(gui_event)

    print(f"🕒 Elapsed Time: {get_elapsed_time()}s | 🟢 Active: {session_state['session_active']}")
    if session_state['session_active']:
        print(f"🎯 Shots: {session_state['total_shots']} | ✅ Potted: {session_state['balls_potted']} | ❌ Missed: {session_state['balls_missed']}")
        print(f"🌀 Current Spin: {spin_state}")

    pygame.time.wait(500)  # Prevent CPU Overload

