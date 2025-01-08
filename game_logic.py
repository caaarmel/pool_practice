
import sqlite3
import os
from datetime import datetime, timedelta
from session_state import session_state

DATABASE = os.path.join(os.path.dirname(__file__), 'pool_practice.db')
connection = sqlite3.connect(DATABASE)

# ✅ Timer Functions
def get_current_time():
    return datetime.now()

def get_elapsed_time():
    if session_state['start_time']:
        elapsed = (get_current_time() - session_state['start_time']).total_seconds()
        return int(elapsed - session_state['total_paused_duration'])
    return 0

# 🎯 Session Management
def start_session():
    if not session_state['session_active']:
        session_state['session_active'] = True
        session_state['start_time'] = get_current_time()
        session_state['total_paused_duration'] = 0

        # Save the session to the database and retrieve the session ID
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (start_time, end_time, total_duration, total_shots, balls_potted, balls_missed)
                VALUES (?, NULL, 0, 0, 0, 0)
            ''', (session_state['start_time'],))
            session_state['session_id'] = cursor.lastrowid  # Store session ID
            conn.commit()

        print(f"🎯 Session started! Session ID: {session_state['session_id']}")

def reconcile_sessions_and_shots():
    """
    Reconciles sessions and shots tables after ending a session.
    """
    with connection as conn:
        cursor = conn.cursor()
        
        # Reconcile Sessions Table
        cursor.execute('''
            SELECT id, start_time, end_time FROM sessions
            ORDER BY start_time;
        ''')
        sessions = cursor.fetchall()
        
        for i in range(len(sessions)):
            if not sessions[i][2]:
                if i + 1 < len(sessions):
                    next_start_time = datetime.fromisoformat(sessions[i + 1][1])
                    adjusted_end_time = next_start_time - timedelta(seconds=1)
                else:
                    adjusted_end_time = datetime.now()
                
                cursor.execute('''
                    UPDATE sessions
                    SET end_time = ?
                    WHERE id = ?
                ''', (adjusted_end_time.isoformat(), sessions[i][0]))
        
        conn.commit()
        print("✅ Sessions table reconciled: Empty end times populated.")

        # Optional: Check for overlapping session times
        cursor.execute('''
            SELECT id, start_time, end_time FROM sessions
            ORDER BY start_time;
        ''')
        sessions = cursor.fetchall()

        for i in range(len(sessions) - 1):
            current_end = datetime.fromisoformat(sessions[i][2])
            next_start = datetime.fromisoformat(sessions[i + 1][1])

            # Check if current_end >= next_start (instead of just >)
            if current_end >= next_start:
                print(f"⚠️ Session {sessions[i][0]} (ends: {current_end}) and {sessions[i+1][0]} (starts: {next_start}) have overlapping or touching times!")


        # Reconcile Shots Table
        cursor.execute('''
            UPDATE shots
            SET session_id = (
                SELECT id FROM sessions
                WHERE shots.timestamp BETWEEN sessions.start_time AND sessions.end_time
                LIMIT 1
            )
            WHERE session_id IS NULL;
        ''')
        print("✅ Shots table reconciled: Assigned session_id based on timestamps.")

        # Assign unmatched shots to the most recent session
        cursor.execute('''
            UPDATE shots
            SET session_id = (
                SELECT id FROM sessions ORDER BY end_time DESC LIMIT 1
            )
            WHERE session_id IS NULL;
        ''')
        print("✅ Shots without matching session timestamps assigned to the latest session.")

        conn.commit()
        print("🔄 Database reconciliation complete!")

        # 🚨 Delete sessions with zero shots
        cursor.execute('''
            DELETE FROM sessions
            WHERE id NOT IN (SELECT DISTINCT session_id FROM shots WHERE session_id IS NOT NULL);
        ''')
        conn.commit()
        print("🗑️ Deleted sessions with zero shots associated.")

        print("🔄 Database reconciliation complete!")

def end_session():
    """
    Ends the current session, calculates session duration, and saves session details.
    """
    if session_state['session_active']:
        session_state['session_active'] = False
        session_state['end_time'] = datetime.now()
        session_duration = (session_state['end_time'] - session_state['start_time']).total_seconds() - session_state['total_paused_duration']

        with connection as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?, total_duration = ?, total_shots = ?, balls_potted = ?, balls_missed = ?
                WHERE id = ?
            ''', (
                session_state['end_time'].isoformat(),
                session_duration,
                session_state['total_shots'],
                session_state['balls_potted'],
                session_state['balls_missed'],
                session_state['session_id']
            ))
            conn.commit()

        print(f"✅ Session {session_state['session_id']} ended. Duration: {session_duration} seconds.")
        
        # Always reconcile after ending the session
        reconcile_sessions_and_shots()

        # Clear session state
        session_state['session_id'] = None
        session_state['shots'] = []
        session_state['total_shots'] = 0
        session_state['balls_potted'] = 0
        session_state['balls_missed'] = 0
        session_state['start_time'] = None
        session_state['end_time'] = None
        session_state['total_paused_duration'] = 0

        print("🏁 Session cleared and ready for the next.")
    else:
        print("❌ No active session to end.")

def reset_session_state():
    global session_state
    session_state.update({
        'session_active': False,
        'start_time': None,
        'pause_time': None,
        'total_paused_duration': 0,
        'shots': [],
        'balls_potted': 0,
        'balls_missed': 0,
        'total_shots': 0,
        'current_spin': {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
    })

# 🌀 Spin Logic
def toggle_spin(direction):
    """
    Toggles spin for the given direction while ensuring no conflicting spins are active.
    If conflicting spin exists, reset to center before applying the new spin.
    """
    if direction == 'top':
        if session_state['current_spin']['bottom'] > 0:
            # Reset conflicting spin
            session_state['current_spin']['bottom'] = 0
            session_state['current_spin']['top'] = 0
            print("🔄 Reset to Center from Bottom before applying Top.")
        else:
            session_state['current_spin']['top'] = (session_state['current_spin']['top'] + 1) % 3

    elif direction == 'bottom':
        if session_state['current_spin']['top'] > 0:
            session_state['current_spin']['top'] = 0
            session_state['current_spin']['bottom'] = 0
            print("🔄 Reset to Center from Top before applying Bottom.")
        else:
            session_state['current_spin']['bottom'] = (session_state['current_spin']['bottom'] + 1) % 3

    elif direction == 'left':
        if session_state['current_spin']['right'] > 0:
            session_state['current_spin']['right'] = 0
            session_state['current_spin']['left'] = 0
            print("🔄 Reset to Center from Right before applying Left.")
        else:
            session_state['current_spin']['left'] = (session_state['current_spin']['left'] + 1) % 3

    elif direction == 'right':
        if session_state['current_spin']['left'] > 0:
            session_state['current_spin']['left'] = 0
            session_state['current_spin']['right'] = 0
            print("🔄 Reset to Center from Left before applying Right.")
        else:
            session_state['current_spin']['right'] = (session_state['current_spin']['right'] + 1) % 3

    # Debug print for current spin state
    spin_state = " + ".join(
        f"{k.capitalize()} ({'None' if v == 0 else 'Top' if v == 1 else 'Max'})"
        for k, v in session_state['current_spin'].items() if v > 0
    ) or "Center"
    print(f"🌀 Spin State Updated: {spin_state}")



# 🎯 Shot Handling
def record_shot(result):
    """
    Records a shot with the current spin settings and saves it to the database.
    """
    if 'session_id' not in session_state or session_state['session_id'] is None:
        print("❌ Error: Cannot record shot without an active session.")
        return

    spin_map = {
        'top': ['Top', 'Max Top'],
        'bottom': ['Stun', 'Max Draw'],
        'left': ['Left', 'Max Left'],
        'right': ['Right', 'Max Right']
    }

    # Build the spin string
    spin = [
        spin_map[key][value - 1]
        for key, value in session_state['current_spin'].items()
        if value > 0
    ]
    spin_str = " + ".join(spin) if spin else "Center"

    # Increment the shot number
    shot_number = session_state['total_shots'] + 1

    # Add shot to session state
    shot = {
        #'session_id': session_state['session_id'],
        'shot_number': shot_number,
        'result': result,
        'spin': spin_str,
        'timestamp': datetime.now().isoformat()
    }
    session_state['shots'].append(shot)
    session_state['total_shots'] += 1

    if result == 'Potted':
        session_state['balls_potted'] += 1
    elif result == 'Missed':
        session_state['balls_missed'] += 1

    # Save to the database
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shots (session_id, shot_number, result, spin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_state['session_id'], shot_number, result, spin_str, shot['timestamp']
        ))
        conn.commit()

    print(f"🎱 Shot {shot_number} Recorded: {result} | Spin: {spin_str} | Session ID: {session_state['session_id']}")

def undo_last_shot():
    """
    Undo the last recorded shot in both session state and database.
    """
    if session_state['shots']:
        last_shot = session_state['shots'].pop()
        session_state['total_shots'] -= 1

        if last_shot['result'] == 'Potted':
            session_state['balls_potted'] -= 1
        elif last_shot['result'] == 'Missed':
            session_state['balls_missed'] -= 1

        # Remove from the database
        with connection as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM shots
                WHERE id = (
                    SELECT id FROM shots
                    WHERE timestamp = ?
                    ORDER BY id DESC
                    LIMIT 1
                );
            ''', (last_shot['timestamp'],))
            conn.commit()

        print(f"↩️ Last shot undone: {last_shot['result']} | Spin: {last_shot['spin']}")
    else:
        print("❌ No shots to undo.")
