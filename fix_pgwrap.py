with open('database/db.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

old = """def get_db():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn"""

new = """def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False

        class PGWrapper:
            def __init__(self, conn):
                self._conn = conn
            def execute(self, sql, params=None):
                sql = sql.replace('?', '%s')
                sql = sql.replace('datetime(', 'to_timestamp(extract(epoch from now()))--datetime(')
                cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params or ())
                return cur
            def cursor(self):
                return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            def commit(self):
                self._conn.commit()
            def close(self):
                self._conn.close()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self._conn.close()

        return PGWrapper(conn)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn"""

if old in content:
    content = content.replace(old, new)
    print('Pattern trouve et remplace')
else:
    print('Pattern non trouve - recherche alternative')
    print(content[300:600])

with open('database/db.py', 'w', encoding='utf-8') as f:
    f.write(content)
