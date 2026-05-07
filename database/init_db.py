"""
FOCUS Leadership Platform — Database Initialization
====================================================
Run this file ONCE to create the entire database.
Command: python init_db.py
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "focus_platform.db"


def get_connection():
    """Returns a database connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables(conn):
    cursor = conn.cursor()

    # ─────────────────────────────────────────
    # TABLE : users
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT    NOT NULL,
            email           TEXT    NOT NULL UNIQUE,
            password_hash   TEXT    NOT NULL,
            role            TEXT    NOT NULL DEFAULT 'member'
                                    CHECK(role IN ('member', 'admin')),
            establishment   TEXT,
            city            TEXT,
            bio             TEXT,
            avatar_url      TEXT,
            status          TEXT    NOT NULL DEFAULT 'pending'
                                    CHECK(status IN ('pending', 'active', 'suspended')),
            points          INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            last_login      TEXT,
            email_verified  INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : modules
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            slug            TEXT    NOT NULL UNIQUE,
            title           TEXT    NOT NULL,
            description     TEXT,
            icon            TEXT,
            color           TEXT    NOT NULL DEFAULT '#1A7A6E',
            order_index     INTEGER NOT NULL DEFAULT 0,
            is_published    INTEGER NOT NULL DEFAULT 1,
            passing_score   INTEGER NOT NULL DEFAULT 70,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : lessons
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id       INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
            title           TEXT    NOT NULL,
            content         TEXT,
            lesson_type     TEXT    NOT NULL DEFAULT 'text'
                                    CHECK(lesson_type IN ('text', 'video', 'quiz')),
            video_url       TEXT,
            order_index     INTEGER NOT NULL DEFAULT 0,
            duration_min    INTEGER NOT NULL DEFAULT 10,
            is_published    INTEGER NOT NULL DEFAULT 1,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : quiz_questions
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id       INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            question_text   TEXT    NOT NULL,
            option_a        TEXT    NOT NULL,
            option_b        TEXT    NOT NULL,
            option_c        TEXT    NOT NULL,
            option_d        TEXT    NOT NULL,
            correct_option  TEXT    NOT NULL CHECK(correct_option IN ('a','b','c','d')),
            explanation     TEXT,
            points          INTEGER NOT NULL DEFAULT 10,
            order_index     INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : user_progress
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            lesson_id       INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            status          TEXT    NOT NULL DEFAULT 'not_started'
                                    CHECK(status IN ('not_started','in_progress','completed')),
            score           INTEGER,
            attempts        INTEGER NOT NULL DEFAULT 0,
            started_at      TEXT,
            completed_at    TEXT,
            UNIQUE(user_id, lesson_id)
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : module_completions
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS module_completions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            module_id       INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
            final_score     INTEGER NOT NULL DEFAULT 0,
            completed_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            certificate_id  TEXT    UNIQUE,
            UNIQUE(user_id, module_id)
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : badges
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            slug            TEXT    NOT NULL UNIQUE,
            name            TEXT    NOT NULL,
            description     TEXT    NOT NULL,
            icon            TEXT    NOT NULL,
            color           TEXT    NOT NULL DEFAULT '#C8A84B',
            trigger_type    TEXT    NOT NULL
                                    CHECK(trigger_type IN (
                                        'registration',
                                        'module_complete',
                                        'helped_member',
                                        'perfect_score',
                                        'streak',
                                        'manual'
                                    )),
            trigger_value   TEXT,
            points_reward   INTEGER NOT NULL DEFAULT 50,
            is_active       INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : user_badges
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_badges (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            badge_id        INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
            awarded_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            awarded_by      TEXT    NOT NULL DEFAULT 'system',
            UNIQUE(user_id, badge_id)
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : certificates
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_uid TEXT    NOT NULL UNIQUE,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            module_id       INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
            issued_at       TEXT    NOT NULL DEFAULT (datetime('now')),
            final_score     INTEGER NOT NULL,
            pdf_path        TEXT,
            is_valid        INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : ai_sessions
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            module_slug     TEXT    NOT NULL,
            session_date    TEXT    NOT NULL DEFAULT (date('now')),
            messages        TEXT    NOT NULL DEFAULT '[]',
            session_count   INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : community_posts
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_posts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            module_id       INTEGER REFERENCES modules(id) ON DELETE SET NULL,
            title           TEXT    NOT NULL,
            content         TEXT    NOT NULL,
            post_type       TEXT    NOT NULL DEFAULT 'question'
                                    CHECK(post_type IN ('question','resource','announcement')),
            likes           INTEGER NOT NULL DEFAULT 0,
            is_pinned       INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : notifications
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type            TEXT    NOT NULL,
            title           TEXT    NOT NULL,
            message         TEXT    NOT NULL,
            is_read         INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ─────────────────────────────────────────
    # TABLE : activity_log
    # ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
            action          TEXT    NOT NULL,
            details         TEXT,
            ip_address      TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    print("✅  Toutes les tables créées avec succès.")


def seed_modules(conn):
    """Insert the 4 training modules."""
    modules = [
        ("leadership",   "Leadership Transformationnel", "Inspirer, motiver et transformer ceux qui t'entourent grâce aux principes du modèle de Bass.", "🔥", "#1A7A6E", 1),
        ("project",      "Gestion de Projet",            "Maîtriser le cycle de vie d'un projet, de l'idée à la livraison.",                            "⚙️", "#2980B9", 2),
        ("python",       "Python pour Leaders",          "S'initier à la logique de programmation pour comprendre et façonner le monde numérique.",        "🐍", "#16A085", 3),
        ("english",      "English for Global Leaders",   "Pratiquer l'anglais pour t'ouvrir aux opportunités internationales.",                           "🌍", "#8E44AD", 4),
    ]
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR IGNORE INTO modules (slug, title, description, icon, color, order_index)
        VALUES (?, ?, ?, ?, ?, ?)
    """, modules)
    conn.commit()
    print("✅  4 modules insérés.")


def seed_badges(conn):
    """Insert the 6 official FOCUS badges."""
    badges = [
        ("eveille",       "L'Éveillé",       "Inscription validée. Ton voyage commence.",                       "🌱", "#27AE60", "registration",    None,         50),
        ("architecte",    "Architecte",       "Module Gestion de Projet terminé. Tu bâtis désormais.",           "⚙️", "#2980B9", "module_complete",  "project",    100),
        ("codeur_sahel",  "Codeur du Sahel",  "Module Python terminé. Le code n'a plus de secrets pour toi.",   "🐍", "#16A085", "module_complete",  "python",     100),
        ("voix_globale",  "Voix Globale",     "Module Anglais terminé. Le monde t'appartient.",                  "🌍", "#8E44AD", "module_complete",  "english",    100),
        ("transformateur","Transformateur",   "Module Leadership terminé. Tu inspires désormais les autres.",    "🔥", "#E74C3C", "module_complete",  "leadership", 100),
        ("pilier",        "Pilier",           "Tu as aidé un autre membre. C'est ça, le vrai leadership.",       "🤝", "#C8A84B", "helped_member",    None,         75),
    ]
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR IGNORE INTO badges
            (slug, name, description, icon, color, trigger_type, trigger_value, points_reward)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, badges)
    conn.commit()
    print("✅  6 badges insérés.")


def seed_admin(conn):
    """Create the default admin account."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users
            (full_name, email, password_hash, role, status, email_verified, establishment, city)
        VALUES (?, ?, ?, 'admin', 'active', 1, 'Centrale-2iE', 'Ouagadougou')
    """, (
        "Coordinateur FOCUS",
        "admin@focus-bf.org",
        hash_password("Focus@Admin2025!"),
    ))
    conn.commit()
    print("✅  Compte admin créé  →  admin@focus-bf.org  /  Focus@Admin2025!")


def seed_sample_lessons(conn):
    """Insert sample lessons for the Leadership module."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modules WHERE slug='leadership'")
    mod = cursor.fetchone()
    if not mod:
        return
    mid = mod["id"]

    lessons = [
        (mid, "Introduction au Leadership Transformationnel",
         """Le leadership transformationnel, tel que défini par Bass (1985), repose sur quatre piliers :

1. **Influence Idéalisée** — Tu sers de modèle moral.
2. **Motivation Inspirante** — Tu donnes une vision claire.
3. **Stimulation Intellectuelle** — Tu challenges tes pairs à penser.
4. **Considération Individuelle** — Tu vois chaque personne dans sa singularité.

Dans ce module, tu vas apprendre à incarner ces quatre piliers dans ta vie quotidienne au Burkina Faso.""",
         "text", None, 1, 15),

        (mid, "La Boussole Morale du Leader",
         """Avant de diriger les autres, tu dois te diriger toi-même.

La boussole morale FOCUS repose sur 5 valeurs :
- **Patriotisme** : Agir pour le bien collectif.
- **Intégrité** : Être cohérent entre tes paroles et tes actes.
- **Excellence** : Viser toujours plus haut.
- **Service** : Mettre tes compétences au service des autres.
- **Relève** : Former ceux qui viennent après toi.""",
         "text", None, 2, 20),

        (mid, "Quiz — Fondements du Leadership", "", "quiz", None, 3, 10),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO lessons
            (module_id, title, content, lesson_type, video_url, order_index, duration_min)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, lessons)
    conn.commit()

    # Sample quiz questions
    cursor.execute("SELECT id FROM lessons WHERE module_id=? AND lesson_type='quiz'", (mid,))
    quiz = cursor.fetchone()
    if quiz:
        qid = quiz["id"]
        questions = [
            (qid, "Selon Bass, combien de piliers compose le leadership transformationnel ?",
             "3", "4", "5", "6", "b",
             "Le modèle de Bass (1985) définit 4 piliers : Influence Idéalisée, Motivation Inspirante, Stimulation Intellectuelle, Considération Individuelle.", 10, 1),

            (qid, "Qu'est-ce que la 'Considération Individuelle' dans le modèle de Bass ?",
             "Donner des ordres individuellement",
             "Voir et accompagner chaque membre dans sa singularité",
             "Faire du favoritisme",
             "Ignorer les besoins du groupe", "b",
             "La Considération Individuelle signifie que le leader porte une attention particulière aux besoins et potentiels de chaque membre.", 10, 2),

            (qid, "Laquelle de ces valeurs NE fait PAS partie de la boussole morale FOCUS ?",
             "Intégrité", "Patriotisme", "Compétitivité", "Service", "c",
             "La boussole FOCUS repose sur : Patriotisme, Intégrité, Excellence, Service et Relève. La compétitivité n'en fait pas partie.", 10, 3),
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO quiz_questions
                (lesson_id, question_text, option_a, option_b, option_c, option_d,
                 correct_option, explanation, points, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, questions)
        conn.commit()
    print("✅  Leçons et quiz de démonstration insérés (module Leadership).")


def create_indexes(conn):
    """Create indexes for frequently queried columns."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email         ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_status        ON users(status)",
        "CREATE INDEX IF NOT EXISTS idx_progress_user       ON user_progress(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_progress_lesson     ON user_progress(lesson_id)",
        "CREATE INDEX IF NOT EXISTS idx_badges_user         ON user_badges(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_notif_user          ON notifications(user_id, is_read)",
        "CREATE INDEX IF NOT EXISTS idx_activity_user       ON activity_log(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_certificates_uid    ON certificates(certificate_uid)",
        "CREATE INDEX IF NOT EXISTS idx_ai_sessions_user    ON ai_sessions(user_id, module_slug)",
    ]
    cursor = conn.cursor()
    for idx in indexes:
        cursor.execute(idx)
    conn.commit()
    print("✅  Index de performance créés.")


def print_summary(conn):
    cursor = conn.cursor()
    print("\n" + "="*50)
    print("   FOCUS PLATFORM — BASE DE DONNÉES INITIALISÉE")
    print("="*50)
    tables = ["users","modules","lessons","quiz_questions","badges",
              "certificates","ai_sessions","community_posts","notifications","activity_log"]
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"   📋  {t:<25} {count} enregistrement(s)")
    print("="*50)
    print(f"   📁  Fichier : {DB_PATH}")
    print("="*50 + "\n")


if __name__ == "__main__":
    print("\n🚀  Initialisation de la base de données FOCUS Platform...\n")

    if os.path.exists(DB_PATH):
        print(f"⚠️   Base existante détectée ({DB_PATH}). Les données existantes sont préservées.\n")

    conn = get_connection()
    try:
        create_tables(conn)
        seed_modules(conn)
        seed_badges(conn)
        seed_admin(conn)
        seed_sample_lessons(conn)
        create_indexes(conn)
        print_summary(conn)
    finally:
        conn.close()
