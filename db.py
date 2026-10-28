"""
Acceso a la base de datos MySQL (librería: PyMySQL).

Funciones de ayuda:
  query(sql, args)      -> lista de filas (diccionarios)
  query_one(sql, args)  -> una fila o None
  execute(sql, args)    -> id insertado (lastrowid)
  init_db()             -> crea la base y las tablas si no existen
"""
import pymysql
from pymysql.cursors import DictCursor

import config

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(80) NOT NULL,
        username VARCHAR(40) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id INT NOT NULL,
        name VARCHAR(60) NOT NULL,
        course VARCHAR(30) NOT NULL DEFAULT '',
        username VARCHAR(40) NOT NULL UNIQUE,
        pin CHAR(4) NOT NULL,
        avatar TEXT,
        coins INT NOT NULL DEFAULT 0,
        last_seen DATETIME NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS topics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id INT NOT NULL,
        title VARCHAR(80) NOT NULL,
        title_es VARCHAR(80) NOT NULL DEFAULT '',
        emoji VARCHAR(16) NOT NULL DEFAULT '📚',
        color VARCHAR(9) NOT NULL DEFAULT '#5b2bd6',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS words (
        id INT AUTO_INCREMENT PRIMARY KEY,
        topic_id INT NOT NULL,
        word VARCHAR(40) NOT NULL,
        translation VARCHAR(60) NOT NULL,
        emoji VARCHAR(16) NOT NULL DEFAULT '',
        sentence VARCHAR(200) NOT NULL DEFAULT '',
        position INT NOT NULL DEFAULT 0,
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS lessons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id INT NOT NULL,
        title VARCHAR(100) NOT NULL,
        description VARCHAR(255) NOT NULL DEFAULT '',
        scene VARCHAR(20) NOT NULL DEFAULT 'house',
        activities VARCHAR(120) NOT NULL DEFAULT 'explore,read,write,quiz',
        course VARCHAR(30) NOT NULL DEFAULT '',
        published TINYINT(1) NOT NULL DEFAULT 1,
        position INT NOT NULL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS lesson_topics (
        lesson_id INT NOT NULL,
        topic_id INT NOT NULL,
        PRIMARY KEY (lesson_id, topic_id),
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS lesson_progress (
        student_id INT NOT NULL,
        lesson_id INT NOT NULL,
        activity VARCHAR(20) NOT NULL,
        best_score INT NOT NULL DEFAULT 0,
        total INT NOT NULL DEFAULT 0,
        passed TINYINT(1) NOT NULL DEFAULT 0,
        attempts INT NOT NULL DEFAULT 0,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (student_id, lesson_id, activity),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS quick_games (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id INT NOT NULL,
        title VARCHAR(100) NOT NULL,
        emoji VARCHAR(16) NOT NULL DEFAULT '⚡',
        time_limit INT NOT NULL DEFAULT 20,
        course VARCHAR(120) NOT NULL DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS quick_questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        game_id INT NOT NULL,
        position INT NOT NULL DEFAULT 0,
        text VARCHAR(255) NOT NULL,
        emoji VARCHAR(16) NOT NULL DEFAULT '',
        opt1 VARCHAR(120) NOT NULL,
        opt2 VARCHAR(120) NOT NULL,
        opt3 VARCHAR(120) NOT NULL DEFAULT '',
        opt4 VARCHAR(120) NOT NULL DEFAULT '',
        correct TINYINT NOT NULL DEFAULT 0,
        FOREIGN KEY (game_id) REFERENCES quick_games(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS game_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        game_id INT NOT NULL,
        code CHAR(6) NOT NULL,
        players INT NOT NULL DEFAULT 0,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ended_at DATETIME NULL,
        FOREIGN KEY (game_id) REFERENCES quick_games(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS game_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL,
        student_id INT NOT NULL,
        score INT NOT NULL DEFAULT 0,
        correct INT NOT NULL DEFAULT 0,
        total INT NOT NULL DEFAULT 0,
        rank_pos INT NOT NULL DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS game_answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL,
        student_id INT NOT NULL,
        qnum INT NOT NULL DEFAULT 0,
        question VARCHAR(255) NOT NULL,
        emoji VARCHAR(16) NOT NULL DEFAULT '',
        chosen VARCHAR(120) NULL,
        correct_answer VARCHAR(120) NOT NULL,
        is_correct TINYINT NOT NULL DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )""",
]

TABLE_OPTIONS = " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"


def get_conn(with_db=True):
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME if with_db else None,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


def query(sql, args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, args=None):
    rows = query(sql, args)
    return rows[0] if rows else None


def execute(sql, args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.lastrowid
    finally:
        conn.close()


def execute_many(sql, rows):
    if not rows:
        return
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
    finally:
        conn.close()


def init_db():
    """Crea la base de datos y las tablas si todavía no existen."""
    conn = get_conn(with_db=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            for table_sql in SCHEMA:
                cur.execute(table_sql + TABLE_OPTIONS)
            # Bases creadas antes de que los juegos tuvieran curso: agregar la columna
            cur.execute("SELECT COUNT(*) n FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s "
                        "AND TABLE_NAME='quick_games' AND COLUMN_NAME='course'", (config.DB_NAME,))
            if not cur.fetchone()["n"]:
                cur.execute("ALTER TABLE quick_games ADD COLUMN course VARCHAR(120) NOT NULL DEFAULT '' AFTER time_limit")
    finally:
        conn.close()


def schema_sql():
    """Devuelve el script SQL completo (se usa para generar database.sql)."""
    parts = [f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
             f"USE `{config.DB_NAME}`;"]
    parts += [s.strip() + TABLE_OPTIONS + ";" for s in SCHEMA]
    return "\n\n".join(parts) + "\n"
