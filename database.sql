CREATE DATABASE IF NOT EXISTS `english_quest` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `english_quest`;

CREATE TABLE IF NOT EXISTS teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(80) NOT NULL,
        username VARCHAR(40) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS students (
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS topics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id INT NOT NULL,
        title VARCHAR(80) NOT NULL,
        title_es VARCHAR(80) NOT NULL DEFAULT '',
        emoji VARCHAR(16) NOT NULL DEFAULT '📚',
        color VARCHAR(9) NOT NULL DEFAULT '#5b2bd6',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS words (
        id INT AUTO_INCREMENT PRIMARY KEY,
        topic_id INT NOT NULL,
        word VARCHAR(40) NOT NULL,
        translation VARCHAR(60) NOT NULL,
        emoji VARCHAR(16) NOT NULL DEFAULT '',
        sentence VARCHAR(200) NOT NULL DEFAULT '',
        position INT NOT NULL DEFAULT 0,
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lessons (
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lesson_topics (
        lesson_id INT NOT NULL,
        topic_id INT NOT NULL,
        PRIMARY KEY (lesson_id, topic_id),
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lesson_progress (
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS quick_games (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id INT NOT NULL,
        title VARCHAR(100) NOT NULL,
        emoji VARCHAR(16) NOT NULL DEFAULT '⚡',
        time_limit INT NOT NULL DEFAULT 20,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS quick_questions (
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS game_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        game_id INT NOT NULL,
        code CHAR(6) NOT NULL,
        players INT NOT NULL DEFAULT 0,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ended_at DATETIME NULL,
        FOREIGN KEY (game_id) REFERENCES quick_games(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS game_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL,
        student_id INT NOT NULL,
        score INT NOT NULL DEFAULT 0,
        correct INT NOT NULL DEFAULT 0,
        total INT NOT NULL DEFAULT 0,
        rank_pos INT NOT NULL DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
