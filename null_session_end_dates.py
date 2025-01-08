import sqlite3

# 📝 Configuration
DATABASE_PATH = 'pool_practice.db'  # Ensure this matches your database path
SESSION_IDS = [2,3, 4,5,6,7,8,9,10,11,12,13,14,15,16]  # Replace with the session IDs you want to nullify

def nullify_session_end_dates(session_ids):
    """
    Sets end_time to NULL for the specified session IDs.
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        for session_id in session_ids:
            cursor.execute('''
                UPDATE sessions
                SET end_time = NULL
                WHERE id = ?
            ''', (session_id,))
            print(f"✅ End time nulled for session ID: {session_id}")
        conn.commit()
    print("🔄 Database updated successfully.")

if __name__ == '__main__':
    nullify_session_end_dates(SESSION_IDS)
