with open('database/db.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

old = """def get_db():
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

new = """def get_db():
    if DATABASE_URL:
        import psycopg2

        class PGRow:
            def __init__(self, row, description):
                self._row = row
                self._keys = [d[0] for d in description] if description else []
            def __getitem__(self, key):
                if isinstance(key, int):
                    return self._row[key]
                return self._row[self._keys.index(key)]
            def keys(self):
                return self._keys

        class PGCursor:
            def __init__(self, cur):
                self._cur = cur
            def fetchone(self):
                row = self._cur.fetchone()
                if row is None:
                    return None
                return PGRow(row, self._cur.description)
            def fetchall(self):
                rows = self._cur.fetchall()
                return [PGRow(r, self._cur.description) for r in rows]
            def __iter__(self):
                for row in self._cur:
                    yield PGRow(row, self._cur.description)
            def __getattr__(self, name):
                return getattr(self._cur, name)

        class PGWrapper:
            def __init__(self, conn):
                self._conn = conn
            def execute(self, sql, params=None):
                sql = sql.replace('?', '%s')
                sql = sql.replace("datetime('now')", 'NOW()')
                sql = sql.replace('datetime(', 'NOW()--datetime(')
                sql = sql.replace("date('now')", 'CURRENT_DATE')
                cur = self._conn.cursor()
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                return PGCursor(cur)
            def cursor(self):
                return self._conn.cursor()
            def commit(self):
                self._conn.commit()
            def close(self):
                self._conn.close()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self._conn.close()

        conn = psycopg2.connect(DATABASE_URL)
        return PGWrapper(conn)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn"""

if old in content:
    content = content.replace(old, new)
    print('Remplace avec succes')
else:
    print('Pattern non trouve')

with open('database/db.py', 'w', encoding='utf-8') as f:
    f.write(content)
