TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT DEFAULT 'ar',
            is_banned INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user',
            ai_requests_today INTEGER DEFAULT 0,
            ai_requests_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "quizzes": """
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'general',
            is_published INTEGER DEFAULT 0,
            total_participants INTEGER DEFAULT 0,
            total_correct INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "questions": """
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'multiple_choice',
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            media_type TEXT,
            media_file_id TEXT,
            order_num INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
        )
    """,
    "channels": """
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            username TEXT,
            channel_type TEXT DEFAULT 'channel',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "schedules": """
        CREATE TABLE IF NOT EXISTS schedules (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            channel_id INTEGER,
            user_id INTEGER,
            scheduled_time TIMESTAMP,
            repeat_type TEXT DEFAULT 'none',
            is_active INTEGER DEFAULT 1,
            last_published TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "queue": """
        CREATE TABLE IF NOT EXISTS queue (
            queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            channel_id INTEGER,
            user_id INTEGER,
            position INTEGER,
            status TEXT DEFAULT 'pending',
            scheduled_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "quiz_results": """
        CREATE TABLE IF NOT EXISTS quiz_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            user_id INTEGER,
            score INTEGER,
            total_questions INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "analytics": """
        CREATE TABLE IF NOT EXISTS analytics (
            analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            channel_id INTEGER,
            published_at TIMESTAMP,
            participants INTEGER DEFAULT 0,
            avg_score REAL DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        )
    """,
    "force_channels": """
        CREATE TABLE IF NOT EXISTS force_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            channel_title TEXT,
            channel_username TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "quiz_links": """
        CREATE TABLE IF NOT EXISTS quiz_links (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            unique_code TEXT UNIQUE,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id)
        )
    """,
    "ab_tests": """
        CREATE TABLE IF NOT EXISTS ab_tests (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_a_id INTEGER,
            quiz_b_id INTEGER,
            channel_id INTEGER,
            user_id INTEGER,
            status TEXT DEFAULT 'active',
            winner TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_a_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (quiz_b_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "support_messages": """
        CREATE TABLE IF NOT EXISTS support_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            reply TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """,
    "publish_log": """
        CREATE TABLE IF NOT EXISTS publish_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            channel_id INTEGER,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        )
    """,
}