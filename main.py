import sqlite3
import pygame
import time
from game_logic import (
    start_session,
    end_session,
    toggle_spin,
    record_shot,
    undo_last_shot,
    session_state,
    get_elapsed_time
)

# Initialize Pygame and Controller
pygame.init()
pygame.joystick.init()

controller_connected = False
controller = None

# 🎮 Attempt to connect controller
while not controller_connected:
    if pygame.joystick.get_count() > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        controller_connected = True
        print(f"🎮 Controller connected: {controller.get_name()}")
    else:
        print("⌛ Waiting for controller connection...")
        time.sleep(1)  # Sleep instead of reinitializing pygame.joystick

# Track previous button states
previous_button_state = {
    'start': False,
    'select': False,
    'undo': False,
    'potted': False,
    'missed': False,
    'x': False,
    'b': False,
    'y': False,
    'a': False
}

try:
    print("\nPress Start to begin/end Session, Select to undo last shot.\n")

    while True:
        try:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    # 🎯 Start/Pause Session
                    if event.button == 7:
                        if session_state['session_active']:
                            end_session()
                        else:
                            start_session()

                    # ↩️ Undo Shot
                    if event.button == 6 and session_state['session_active']:
                        undo_last_shot()
                        print("Undo last shot!")

                    # ✅ Ball Potted
                    if event.button == 5:
                        record_shot('Potted')

                    # ❌ Ball Missed
                    if event.button == 4:
                        record_shot('Missed')

                    # 🌀 Spin Controls
                    if event.button == 3:  # X Button → Top
                        toggle_spin('top')
                    if event.button == 0:  # B Button → Bottom
                        toggle_spin('bottom')
                    if event.button == 2:  # Y Button → Left
                        toggle_spin('left')
                    if event.button == 1:  # A Button → Right
                        toggle_spin('right')

        except pygame.error as e:
            print(f"⚠️ Pygame event error: {e}")
            time.sleep(1)

        # 🖥️ Display State
        if session_state['session_active']:
            spin_state = " + ".join(
                spin for spin in [
                    ('Top' if session_state['current_spin']['top'] == 1 else 'Max Top') if session_state['current_spin']['top'] else '',
                    ('Stun' if session_state['current_spin']['bottom'] == 1 else 'Max Draw') if session_state['current_spin']['bottom'] else '',
                    ('Left' if session_state['current_spin']['left'] == 1 else 'Max Left') if session_state['current_spin']['left'] else '',
                    ('Right' if session_state['current_spin']['right'] == 1 else 'Max Right') if session_state['current_spin']['right'] else ''
                ] if spin
            ) or "Center"
            print(f"🕒 Elapsed Time: {get_elapsed_time()}s | 🟢 Active: {not session_state['session_paused']}")
            print(f"🎯 Shots: {session_state['total_shots']} | ✅ Potted: {session_state['balls_potted']} | ❌ Missed: {session_state['balls_missed']}")
            print(f"🌀 Current Spin: {spin_state}")
            time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Program terminated by user.")
finally:
    pygame.quit()
