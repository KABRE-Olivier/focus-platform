import sqlite3
conn = sqlite3.connect('focus_platform.db')
conn.execute("UPDATE users SET status='active' WHERE role='admin'")
conn.commit()
conn.close()
print('Admin active')
