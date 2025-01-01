import sqlite3

# Initialize database connection
conn = sqlite3.connect('pool_practice.db')
cursor = conn.cursor()

# Create sessions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    end_time TEXT,
    total_duration INTEGER,
    total_shots INTEGER,
    balls_potted INTEGER,
    balls_missed INTEGER
)
''')

# Create shots table
cursor.execute('''
CREATE TABLE IF NOT EXISTS shots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    shot_number INTEGER,
    result TEXT,
    spin TEXT,
    timestamp TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
)
''')

conn.commit()
conn.close()
print("Database initialized successfully!")
