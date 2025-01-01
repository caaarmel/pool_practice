import sqlite3

# Connect to the database
conn = sqlite3.connect('pool_practice.db')
cursor = conn.cursor()

# Verify sessions table
cursor.execute("PRAGMA table_info(sessions);")
print("📊 Sessions Table Structure:")
for row in cursor.fetchall():
    print(row)

# Verify shots table
cursor.execute("PRAGMA table_info(shots);")
print("\n📊 Shots Table Structure:")
for row in cursor.fetchall():
    print(row)

# Fetch session data
cursor.execute("SELECT * FROM sessions;")
sessions = cursor.fetchall()

print("\n🎯 Session Logs:")
if sessions:
    for session in sessions:
        print(session)
else:
    print("No session logs found in the database.")

# Fetch shots data
cursor.execute("SELECT * FROM shots;")
shots = cursor.fetchall()

print("\n🎯 Shot Logs:")
if shots:
    for shot in shots:
        print(shot)
else:
    print("No shot logs found in the database.")

# Close connection
conn.close()
