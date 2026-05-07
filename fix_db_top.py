import sqlite3
import os
import hashlib
import uuid
from datetime import datetime, date

DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    DB_PATH = None
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'focus_platform.db')


def get_db():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn
