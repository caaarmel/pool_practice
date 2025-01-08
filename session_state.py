# Shared session state across modules

session_state = {
    # 🟢 Session State
    'session_id': None,              # Session identifier
    'session_active': False,         # Tracks if a session is active
    'start_time': None,              # Session start time
    'pause_time': None,              # Pause time (if applicable)
    'total_paused_duration': 0,      # Total duration paused

    # 🎱 Shot Tracking
    'shots': [],                     # List of shot logs [{'result': 'Potted', 'spin': {...}, 'time': 'hh:mm:ss'}]
    'balls_potted': 0,               # Count of successful shots
    'balls_missed': 0,               # Count of missed shots
    'total_shots': 0,                # Total number of shots taken

    # 🌀 Spin State
    'current_spin': {                # Active spin state
        'top': 0,
        'bottom': 0,
        'left': 0,
        'right': 0
    },
    'current_spin_display': 'Center', # Human-readable spin display

    # ⏱️ Timer & Feedback
    'timer': '00:00',                # Timer in hh:mm
    'feedback': 'Ready',             # Action feedback for the user
}



#FROM MAIN
# session_state = {
#     'session_id': '-',
#     'session_active': False,
#     'total_shots': 0,
#     'balls_potted': 0,
#     'balls_missed': 0,
#     'current_spin_display': 'Center',
#     'current_spin': {  # Added this
#         'top': 0,
#         'bottom': 0,
#         'left': 0,
#         'right': 0
#     }
# }

#FROM GAME_LOGIC
# 📝 Session State
# session_state = {
#     'session_active': False,
#     'start_time': None,
#     'pause_time': None,
#     'total_paused_duration': 0,
#     'shots': [],
#     'balls_potted': 0,
#     'balls_missed': 0,
#     'total_shots': 0,
#     'current_spin': {
#         'top': 0,
#         'bottom': 0,
#         'left': 0,
#         'right': 0
#     }
# }