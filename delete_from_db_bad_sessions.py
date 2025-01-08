import sqlite3

conn = sqlite3.connect('pool_practice.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("📊 Tables:", cursor.fetchall())

# Delete invalid session records
cursor.execute("DELETE FROM shots WHERE NOT session_id GLOB '[0-9]*';")
conn.commit()

print("✅ Invalid sessions deleted.")
conn.close()
