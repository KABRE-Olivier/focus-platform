import os

with open('database/db.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = "DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'focus_platform.db')"

new = """DATABASE_URL = os.environ.get('DATABASE_URL', '')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'focus_platform.db')"""

content = content.replace(old, new)

# Modifier get_db pour utiliser PostgreSQL si DATABASE_URL existe
old2 = """def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn"""

new2 = """def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn"""

content = content.replace(old2, new2)

with open('database/db.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')
