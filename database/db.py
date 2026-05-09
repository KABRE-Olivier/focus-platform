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
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_certificate_uid() -> str:
    return "FOCUS-" + str(uuid.uuid4()).upper()[:12]


# ─────────────────────────────────────────
# USERS
# ─────────────────────────────────────────

def create_user(full_name, email, password, establishment="", city=""):
    """Create a new member. Returns user id or None if email exists."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, establishment, city)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, email, hash_password(password), establishment, city))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return user


def authenticate_user(email, password):
    """Returns user row if credentials valid, else None."""
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password_hash=? AND status='active'",
        (email, hash_password(password))
    ).fetchone()
    if user:
        conn.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user["id"],))
        conn.commit()
    conn.close()
    return user


def update_user_status(user_id, status):
    """Admin: activate, suspend a member."""
    conn = get_db()
    conn.execute("UPDATE users SET status=? WHERE id=?", (status, user_id))
    conn.commit()
    conn.close()


def add_points(user_id, points):
    conn = get_db()
    conn.execute("UPDATE users SET points = points + ? WHERE id=?", (points, user_id))
    conn.commit()
    conn.close()


def get_leaderboard(limit=10):
    conn = get_db()
    rows = conn.execute("""
        SELECT id, full_name, establishment, points, avatar_url
        FROM users
        WHERE status='active' AND role='member'
        ORDER BY points DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def get_all_users(status=None):
    """Admin: get all users, optionally filtered by status."""
    conn = get_db()
    if status:
        rows = conn.execute("SELECT * FROM users WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


# ─────────────────────────────────────────
# MODULES & LESSONS
# ─────────────────────────────────────────

def get_all_modules():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM modules WHERE is_published=1 ORDER BY order_index"
    ).fetchall()
    conn.close()
    return rows


def get_module_by_slug(slug):
    conn = get_db()
    row = conn.execute("SELECT * FROM modules WHERE slug=?", (slug,)).fetchone()
    conn.close()
    return row


def get_lessons_by_module(module_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM lessons WHERE module_id=? AND is_published=1 ORDER BY order_index",
        (module_id,)
    ).fetchall()
    conn.close()
    return rows


def get_quiz_questions(lesson_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM quiz_questions WHERE lesson_id=? ORDER BY order_index",
        (lesson_id,)
    ).fetchall()
    conn.close()
    return rows


# ─────────────────────────────────────────
# PROGRESSION
# ─────────────────────────────────────────

def get_user_progress(user_id, lesson_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM user_progress WHERE user_id=? AND lesson_id=?",
        (user_id, lesson_id)
    ).fetchone()
    conn.close()
    return row


def mark_lesson_started(user_id, lesson_id):
    conn = get_db()
    conn.execute("""
        INSERT INTO user_progress (user_id, lesson_id, status, started_at)
        VALUES (?, ?, 'in_progress', datetime('now'))
        ON CONFLICT(user_id, lesson_id) DO UPDATE SET
            status='in_progress',
            started_at=COALESCE(started_at, datetime('now'))
    """, (user_id, lesson_id))
    conn.commit()
    conn.close()


def mark_lesson_completed(user_id, lesson_id, score=None):
    conn = get_db()
    conn.execute("""
        INSERT INTO user_progress (user_id, lesson_id, status, score, attempts, completed_at)
        VALUES (?, ?, 'completed', ?, 1, datetime('now'))
        ON CONFLICT(user_id, lesson_id) DO UPDATE SET
            status='completed',
            score=COALESCE(?, score),
            attempts=attempts+1,
            completed_at=datetime('now')
    """, (user_id, lesson_id, score, score))
    conn.commit()
    conn.close()


def get_module_completion_rate(user_id, module_id):
    """Returns (completed_lessons, total_lessons, percentage)."""
    conn = get_db()
    total = conn.execute(
        "SELECT COUNT(*) FROM lessons WHERE module_id=? AND is_published=1", (module_id,)
    ).fetchone()[0]
    completed = conn.execute("""
        SELECT COUNT(*) FROM user_progress up
        JOIN lessons l ON up.lesson_id = l.id
        WHERE up.user_id=? AND l.module_id=? AND up.status='completed'
    """, (user_id, module_id)).fetchone()[0]
    conn.close()
    pct = round((completed / total * 100) if total > 0 else 0)
    return completed, total, pct


def get_user_module_progress(user_id):
    """Returns progress for all modules."""
    conn = get_db()
    modules = conn.execute(
        "SELECT * FROM modules WHERE is_published=1 ORDER BY order_index"
    ).fetchall()
    result = []
    for m in modules:
        completed, total, pct = get_module_completion_rate(user_id, m["id"])
        result.append({
            "module": dict(m),
            "completed": completed,
            "total": total,
            "percent": pct,
        })
    conn.close()
    return result


# ─────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────

def get_all_badges():
    conn = get_db()
    rows = conn.execute("SELECT * FROM badges WHERE is_active=1").fetchall()
    conn.close()
    return rows


def get_user_badges(user_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT b.*, ub.awarded_at FROM badges b
        JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id=?
        ORDER BY ub.awarded_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return rows


def award_badge(user_id, badge_slug, awarded_by="system"):
    """Award a badge. Returns True if new, False if already had it."""
    conn = get_db()
    badge = conn.execute("SELECT * FROM badges WHERE slug=?", (badge_slug,)).fetchone()
    if not badge:
        conn.close()
        return False
    try:
        conn.execute("""
            INSERT INTO user_badges (user_id, badge_id, awarded_by)
            VALUES (?, ?, ?)
        """, (user_id, badge["id"], awarded_by))
        conn.execute(
            "UPDATE users SET points = points + ? WHERE id=?",
            (badge["points_reward"], user_id)
        )
        conn.commit()
        _create_notification(conn, user_id, "badge",
            f"🏅 Badge obtenu : {badge['name']}",
            badge["description"])
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Already awarded


def check_and_award_module_badge(user_id, module_slug):
    """Auto-award badge when module is completed."""
    badge_map = {
        "leadership": "transformateur",
        "project":    "architecte",
        "python":     "codeur_sahel",
        "english":    "voix_globale",
    }
    if module_slug in badge_map:
        award_badge(user_id, badge_map[module_slug])


# ─────────────────────────────────────────
# CERTIFICATES
# ─────────────────────────────────────────

def issue_certificate(user_id, module_id, final_score):
    """Generate a certificate record. Returns the uid."""
    uid = generate_certificate_uid()
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO certificates (certificate_uid, user_id, module_id, final_score)
            VALUES (?, ?, ?, ?)
        """, (uid, user_id, module_id, final_score))
        conn.execute("""
            INSERT INTO module_completions (user_id, module_id, final_score, certificate_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, module_id) DO UPDATE SET
                final_score=?, certificate_id=?, completed_at=datetime('now')
        """, (user_id, module_id, final_score, uid, final_score, uid))
        conn.commit()
        conn.close()
        return uid
    except Exception as e:
        conn.close()
        raise e


def verify_certificate(uid):
    """Public verification of a certificate by its UID."""
    conn = get_db()
    row = conn.execute("""
        SELECT c.*, u.full_name, m.title as module_title
        FROM certificates c
        JOIN users u ON c.user_id = u.id
        JOIN modules m ON c.module_id = m.id
        WHERE c.certificate_uid=? AND c.is_valid=1
    """, (uid,)).fetchone()
    conn.close()
    return row


def get_user_certificates(user_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT c.*, m.title as module_title, m.icon as module_icon, m.color as module_color
        FROM certificates c
        JOIN modules m ON c.module_id = m.id
        WHERE c.user_id=? AND c.is_valid=1
        ORDER BY c.issued_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return rows


# ─────────────────────────────────────────
# AI SESSIONS
# ─────────────────────────────────────────

def get_or_create_ai_session(user_id, module_slug):
    """Get today's AI session or create a new one."""
    today = date.today().isoformat()
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM ai_sessions WHERE user_id=? AND module_slug=? AND session_date=?",
        (user_id, module_slug, today)
    ).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO ai_sessions (user_id, module_slug, session_date) VALUES (?, ?, ?)",
            (user_id, module_slug, today)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM ai_sessions WHERE user_id=? AND module_slug=? AND session_date=?",
            (user_id, module_slug, today)
        ).fetchone()
    conn.close()
    return row


def update_ai_session(session_id, messages_json):
    conn = get_db()
    conn.execute("""
        UPDATE ai_sessions SET messages=?, session_count=session_count+1, updated_at=datetime('now')
        WHERE id=?
    """, (messages_json, session_id))
    conn.commit()
    conn.close()


MAX_AI_MESSAGES_PER_DAY = 20

def get_ai_message_count_today(user_id, module_slug):
    conn = get_db()
    row = conn.execute(
        "SELECT session_count FROM ai_sessions WHERE user_id=? AND module_slug=? AND session_date=?",
        (user_id, module_slug, date.today().isoformat())
    ).fetchone()
    conn.close()
    return row["session_count"] if row else 0


# ─────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────

def _create_notification(conn, user_id, notif_type, title, message):
    """Internal — use an existing connection."""
    conn.execute("""
        INSERT INTO notifications (user_id, type, title, message)
        VALUES (?, ?, ?, ?)
    """, (user_id, notif_type, title, message))


def get_user_notifications(user_id, unread_only=False):
    conn = get_db()
    if unread_only:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id=? AND is_read=0 ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
            (user_id,)
        ).fetchall()
    conn.close()
    return rows


def mark_notifications_read(user_id):
    conn = get_db()
    conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# ACTIVITY LOG
# ─────────────────────────────────────────

def log_activity(user_id, action, details=None, ip_address=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO activity_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
        (user_id, action, details, ip_address)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# ADMIN DASHBOARD STATS
# ─────────────────────────────────────────

def get_admin_stats():
    conn = get_db()
    stats = {}
    stats["total_members"]   = conn.execute("SELECT COUNT(*) FROM users WHERE role='member'").fetchone()[0]
    stats["active_members"]  = conn.execute("SELECT COUNT(*) FROM users WHERE status='active' AND role='member'").fetchone()[0]
    stats["pending_members"] = conn.execute("SELECT COUNT(*) FROM users WHERE status='pending'").fetchone()[0]
    stats["total_certs"]     = conn.execute("SELECT COUNT(*) FROM certificates WHERE is_valid=1").fetchone()[0]
    stats["total_badges"]    = conn.execute("SELECT COUNT(*) FROM user_badges").fetchone()[0]
    stats["ai_sessions"]     = conn.execute("SELECT COUNT(*) FROM ai_sessions").fetchone()[0]
    conn.close()
    return stats


def get_inactive_members(days=14):
    """Members who haven't logged in for X days."""
    conn = get_db()
    rows = conn.execute("""
        SELECT id, full_name, email, last_login, establishment
        FROM users
        WHERE role='member' AND status='active'
          AND (last_login IS NULL OR last_login < NOW() - INTERVAL '14 days')
        ORDER BY last_login ASC
    """).fetchall()
    conn.close()
    return rows
