import aiosqlite
import logging
from datetime import datetime, date
from database.models import TABLES

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path="bot_database.db"):
        self.db_path = db_path
        self.db = None

    async def initialize(self):
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        await self.db.execute("PRAGMA journal_mode=WAL")
        await self.db.execute("PRAGMA foreign_keys=ON")
        for table_name, create_sql in TABLES.items():
            await self.db.execute(create_sql)
        await self.db.commit()
        logger.info("Database initialized successfully")

    async def close(self):
        if self.db:
            await self.db.close()

    # ─── User Operations ──────────────────────────────────

    async def add_user(self, user_id, username, first_name, last_name=""):
        await self.db.execute(
            """INSERT OR IGNORE INTO users 
               (user_id, username, first_name, last_name) 
               VALUES (?, ?, ?, ?)""",
            (user_id, username, first_name, last_name),
        )
        await self.db.execute(
            """UPDATE users SET username=?, first_name=?, last_name=?, 
               updated_at=CURRENT_TIMESTAMP WHERE user_id=?""",
            (username, first_name, last_name, user_id),
        )
        await self.db.commit()

    async def get_user(self, user_id):
        async with self.db.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def get_all_users(self):
        async with self.db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_user_count(self):
        async with self.db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0]

    async def ban_user(self, user_id):
        await self.db.execute(
            "UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,)
        )
        await self.db.commit()

    async def unban_user(self, user_id):
        await self.db.execute(
            "UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,)
        )
        await self.db.commit()

    async def is_banned(self, user_id):
        async with self.db.execute(
            "SELECT is_banned FROM users WHERE user_id=?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return bool(row[0])
            return False

    async def set_user_language(self, user_id, language):
        await self.db.execute(
            "UPDATE users SET language=? WHERE user_id=?", (language, user_id)
        )
        await self.db.commit()

    async def get_user_language(self, user_id):
        async with self.db.execute(
            "SELECT language FROM users WHERE user_id=?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return "ar"

    async def set_user_role(self, user_id, role):
        is_admin = 1 if role in ("admin", "editor") else 0
        await self.db.execute(
            "UPDATE users SET role=?, is_admin=? WHERE user_id=?",
            (role, is_admin, user_id),
        )
        await self.db.commit()

    async def check_ai_limit(self, user_id, max_requests):
        today = date.today().isoformat()
        async with self.db.execute(
            "SELECT ai_requests_today, ai_requests_date FROM users WHERE user_id=?",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                if row[1] != today:
                    await self.db.execute(
                        "UPDATE users SET ai_requests_today=0, ai_requests_date=? WHERE user_id=?",
                        (today, user_id),
                    )
                    await self.db.commit()
                    return True
                return row[0] < max_requests
            return True

    async def increment_ai_requests(self, user_id):
        today = date.today().isoformat()
        await self.db.execute(
            """UPDATE users SET ai_requests_today = ai_requests_today + 1, 
               ai_requests_date=? WHERE user_id=?""",
            (today, user_id),
        )
        await self.db.commit()

    # ─── Quiz Operations ──────────────────────────────────

    async def create_quiz(self, user_id, title, description="", category="general"):
        cursor = await self.db.execute(
            """INSERT INTO quizzes (user_id, title, description, category) 
               VALUES (?, ?, ?, ?)""",
            (user_id, title, description, category),
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_quiz(self, quiz_id):
        async with self.db.execute(
            "SELECT * FROM quizzes WHERE quiz_id=?", (quiz_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def get_user_quizzes(self, user_id):
        async with self.db.execute(
            "SELECT * FROM quizzes WHERE user_id=? ORDER BY created_at DESC",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_all_quizzes_count(self):
        async with self.db.execute("SELECT COUNT(*) FROM quizzes") as cursor:
            row = await cursor.fetchone()
            return row[0]

    async def delete_quiz(self, quiz_id):
        await self.db.execute(
            "DELETE FROM questions WHERE quiz_id=?", (quiz_id,)
        )
        await self.db.execute(
            "DELETE FROM quizzes WHERE quiz_id=?", (quiz_id,)
        )
        await self.db.commit()

    async def update_quiz(self, quiz_id, **kwargs):
        set_clause = ", ".join(f"{k}=?" for k in kwargs.keys())
        values = list(kwargs.values())
        values.append(quiz_id)
        await self.db.execute(
            f"UPDATE quizzes SET {set_clause}, updated_at=CURRENT_TIMESTAMP WHERE quiz_id=?",
            values,
        )
        await self.db.commit()

    async def increment_quiz_participants(self, quiz_id):
        await self.db.execute(
            "UPDATE quizzes SET total_participants = total_participants + 1 WHERE quiz_id=?",
            (quiz_id,),
        )
        await self.db.commit()

    # ─── Question Operations ──────────────────────────────

    async def add_question(
        self,
        quiz_id,
        question_text,
        question_type,
        option_a,
        option_b,
        correct_answer,
        option_c=None,
        option_d=None,
        explanation=None,
        media_type=None,
        media_file_id=None,
        order_num=0,
    ):
        cursor = await self.db.execute(
            """INSERT INTO questions 
               (quiz_id, question_text, question_type, option_a, option_b, 
                option_c, option_d, correct_answer, explanation, 
                media_type, media_file_id, order_num) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                quiz_id,
                question_text,
                question_type,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                explanation,
                media_type,
                media_file_id,
                order_num,
            ),
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_quiz_questions(self, quiz_id):
        async with self.db.execute(
            "SELECT * FROM questions WHERE quiz_id=? ORDER BY order_num",
            (quiz_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_question(self, question_id):
        async with self.db.execute(
            "SELECT * FROM questions WHERE question_id=?", (question_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def delete_question(self, question_id):
        await self.db.execute(
            "DELETE FROM questions WHERE question_id=?", (question_id,)
        )
        await self.db.commit()

    async def get_question_count(self, quiz_id):
        async with self.db.execute(
            "SELECT COUNT(*) FROM questions WHERE quiz_id=?", (quiz_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]

    # ─── Channel Operations ──────────────────────────────

    async def add_channel(self, channel_id, user_id, title, username="", channel_type="channel"):
        await self.db.execute(
            """INSERT OR REPLACE INTO channels 
               (channel_id, user_id, title, username, channel_type) 
               VALUES (?, ?, ?, ?, ?)""",
            (channel_id, user_id, title, username, channel_type),
        )
        await self.db.commit()

    async def get_user_channels(self, user_id):
        async with self.db.execute(
            "SELECT * FROM channels WHERE user_id=?", (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_channel(self, channel_id):
        async with self.db.execute(
            "SELECT * FROM channels WHERE channel_id=?", (channel_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def remove_channel(self, channel_id):
        await self.db.execute(
            "DELETE FROM channels WHERE channel_id=?", (channel_id,)
        )
        await self.db.commit()

    async def add_force_channel(self, channel_id, title, username=""):
        await self.db.execute(
            """INSERT INTO force_channels (channel_id, channel_title, channel_username) 
               VALUES (?, ?, ?)""",
            (str(channel_id), title, username),
        )
        await self.db.commit()

    async def get_all_channels(self):
        async with self.db.execute("SELECT * FROM channels") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── Schedule Operations ──────────────────────────────

    async def add_schedule(
        self, quiz_id, channel_id, user_id, scheduled_time, repeat_type="none"
    ):
        cursor = await self.db.execute(
            """INSERT INTO schedules 
               (quiz_id, channel_id, user_id, scheduled_time, repeat_type) 
               VALUES (?, ?, ?, ?, ?)""",
            (quiz_id, channel_id, user_id, scheduled_time, repeat_type),
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_active_schedules(self):
        async with self.db.execute(
            "SELECT * FROM schedules WHERE is_active=1"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_user_schedules(self, user_id):
        async with self.db.execute(
            "SELECT s.*, q.title as quiz_title, c.title as channel_title "
            "FROM schedules s "
            "JOIN quizzes q ON s.quiz_id = q.quiz_id "
            "JOIN channels c ON s.channel_id = c.channel_id "
            "WHERE s.user_id=? AND s.is_active=1",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def deactivate_schedule(self, schedule_id):
        await self.db.execute(
            "UPDATE schedules SET is_active=0 WHERE schedule_id=?",
            (schedule_id,),
        )
        await self.db.commit()

    async def update_schedule_last_published(self, schedule_id):
        await self.db.execute(
            "UPDATE schedules SET last_published=CURRENT_TIMESTAMP WHERE schedule_id=?",
            (schedule_id,),
        )
        await self.db.commit()

    # ─── Queue Operations ──────────────────────────────────

    async def add_to_queue(self, quiz_id, channel_id, user_id, position=0, scheduled_time=None):
        cursor = await self.db.execute(
            """INSERT INTO queue 
               (quiz_id, channel_id, user_id, position, scheduled_time) 
               VALUES (?, ?, ?, ?, ?)""",
            (quiz_id, channel_id, user_id, position, scheduled_time),
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_user_queue(self, user_id):
        async with self.db.execute(
            """SELECT q.*, qz.title as quiz_title, c.title as channel_title 
               FROM queue q 
               JOIN quizzes qz ON q.quiz_id = qz.quiz_id 
               JOIN channels c ON q.channel_id = c.channel_id 
               WHERE q.user_id=? AND q.status='pending' 
               ORDER BY q.position""",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_pending_queue(self):
        async with self.db.execute(
            """SELECT q.*, qz.title as quiz_title, c.title as channel_title 
               FROM queue q 
               JOIN quizzes qz ON q.quiz_id = qz.quiz_id 
               JOIN channels c ON q.channel_id = c.channel_id 
               WHERE q.status='pending' 
               ORDER BY q.position"""
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_queue_status(self, queue_id, status):
        await self.db.execute(
            "UPDATE queue SET status=? WHERE queue_id=?", (status, queue_id)
        )
        await self.db.commit()

    async def remove_from_queue(self, queue_id):
        await self.db.execute(
            "DELETE FROM queue WHERE queue_id=?", (queue_id,)
        )
        await self.db.commit()

    # ─── Quiz Results ─────────────────────────────────────

    async def save_quiz_result(self, quiz_id, user_id, score, total_questions):
        await self.db.execute(
            """INSERT INTO quiz_results 
               (quiz_id, user_id, score, total_questions) 
               VALUES (?, ?, ?, ?)""",
            (quiz_id, user_id, score, total_questions),
        )
        await self.db.commit()

    async def get_quiz_results(self, quiz_id):
        async with self.db.execute(
            "SELECT * FROM quiz_results WHERE quiz_id=? ORDER BY completed_at DESC",
            (quiz_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_user_results(self, user_id):
        async with self.db.execute(
            """SELECT qr.*, q.title as quiz_title 
               FROM quiz_results qr 
               JOIN quizzes q ON qr.quiz_id = q.quiz_id 
               WHERE qr.user_id=? 
               ORDER BY qr.completed_at DESC""",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── Analytics ────────────────────────────────────────

    async def save_analytics(self, quiz_id, channel_id, participants=0, avg_score=0):
        await self.db.execute(
            """INSERT INTO analytics 
               (quiz_id, channel_id, published_at, participants, avg_score) 
               VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)""",
            (quiz_id, channel_id, participants, avg_score),
        )
        await self.db.commit()

    async def get_quiz_analytics(self, quiz_id):
        async with self.db.execute(
            "SELECT * FROM analytics WHERE quiz_id=? ORDER BY published_at DESC",
            (quiz_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_user_analytics(self, user_id):
        async with self.db.execute(
            """SELECT a.*, q.title as quiz_title 
               FROM analytics a 
               JOIN quizzes q ON a.quiz_id = q.quiz_id 
               WHERE q.user_id=? 
               ORDER BY a.published_at DESC""",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── Force Channels ──────────────────────────────────

    async def add_force_channel(self, channel_id, title="", username=""):
        await self.db.execute(
            """INSERT OR REPLACE INTO force_channels 
               (channel_id, channel_title, channel_username) 
               VALUES (?, ?, ?)""",
            (channel_id, title, username),
        )
        await self.db.commit()

    async def remove_force_channel(self, channel_id):
        await self.db.execute(
            "DELETE FROM force_channels WHERE channel_id=?", (channel_id,)
        )
        await self.db.commit()

    async def get_force_channels(self):
        async with self.db.execute(
            "SELECT * FROM force_channels"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── Quiz Links ──────────────────────────────────────

    async def create_quiz_link(self, quiz_id, unique_code):
        await self.db.execute(
            "INSERT INTO quiz_links (quiz_id, unique_code) VALUES (?, ?)",
            (quiz_id, unique_code),
        )
        await self.db.commit()

    async def get_quiz_link(self, unique_code):
        async with self.db.execute(
            "SELECT * FROM quiz_links WHERE unique_code=?", (unique_code,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def increment_link_clicks(self, unique_code):
        await self.db.execute(
            "UPDATE quiz_links SET clicks = clicks + 1 WHERE unique_code=?",
            (unique_code,),
        )
        await self.db.commit()

    async def get_quiz_links(self, quiz_id):
        async with self.db.execute(
            "SELECT * FROM quiz_links WHERE quiz_id=?", (quiz_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── AB Tests ─────────────────────────────────────────

    async def create_ab_test(self, quiz_a_id, quiz_b_id, channel_id, user_id):
        cursor = await self.db.execute(
            """INSERT INTO ab_tests 
               (quiz_a_id, quiz_b_id, channel_id, user_id) 
               VALUES (?, ?, ?, ?)""",
            (quiz_a_id, quiz_b_id, channel_id, user_id),
        )
        await self.db.commit()
        return cursor.lastrowid

    async def get_ab_tests(self, user_id):
        async with self.db.execute(
            """SELECT t.*, qa.title as quiz_a_title, qb.title as quiz_b_title, 
                      c.title as channel_title
               FROM ab_tests t 
               JOIN quizzes qa ON t.quiz_a_id = qa.quiz_id 
               JOIN quizzes qb ON t.quiz_b_id = qb.quiz_id 
               JOIN channels c ON t.channel_id = c.channel_id
               WHERE t.user_id=? 
               ORDER BY t.created_at DESC""",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── Support Messages ────────────────────────────────

    async def save_support_message(self, user_id, message):
        await self.db.execute(
            "INSERT INTO support_messages (user_id, message) VALUES (?, ?)",
            (user_id, message),
        )
        await self.db.commit()

    async def get_unread_support_messages(self):
        async with self.db.execute(
            """SELECT sm.*, u.username, u.first_name 
               FROM support_messages sm 
               JOIN users u ON sm.user_id = u.user_id 
               WHERE sm.is_read=0 
               ORDER BY sm.created_at DESC"""
        ) as cursor:
      
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ─── Publish Log ─────────────────────────────────────

    async def log_publish(self, quiz_id, channel_id, status="success"):
        await self.db.execute(
            "INSERT INTO publish_log (quiz_id, channel_id, status) VALUES (?, ?, ?)",
            (quiz_id, channel_id, status),
        )
        await self.db.commit()

    async def check_duplicate_publish(self, quiz_id, channel_id, hours=24):
        async with self.db.execute(
            """SELECT COUNT(*) FROM publish_log 
               WHERE quiz_id=? AND channel_id=? 
               AND published_at > datetime('now', ?)""",
            (quiz_id, channel_id, f"-{hours} hours"),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] > 0