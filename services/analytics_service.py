import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db):
        self.db = db

    async def get_user_stats(self, user_id):
        quizzes = await self.db.get_user_quizzes(user_id)
        channels = await self.db.get_user_channels(user_id)
        schedules = await self.db.get_user_schedules(user_id)

        total_questions = 0
        for quiz in quizzes:
            count = await self.db.get_question_count(quiz["quiz_id"])
            total_questions += count

        return {
            "total_quizzes": len(quizzes),
            "total_questions": total_questions,
            "total_channels": len(channels),
            "active_schedules": len(schedules),
        }

    async def get_quiz_stats(self, quiz_id):
        quiz = await self.db.get_quiz(quiz_id)
        questions = await self.db.get_quiz_questions(quiz_id)
        results = await self.db.get_quiz_results(quiz_id)
        analytics = await self.db.get_quiz_analytics(quiz_id)

        avg_score = 0
        if results:
            total_scores = sum(r["score"] for r in results)
            total_possible = sum(r["total_questions"] for r in results)
            if total_possible > 0:
                avg_score = round((total_scores / total_possible) * 100, 1)

        return {
            "quiz": quiz,
            "question_count": len(questions),
            "participant_count": len(results),
            "avg_score": avg_score,
            "publish_count": len(analytics),
        }

    async def get_global_stats(self):
        user_count = await self.db.get_user_count()
        quiz_count = await self.db.get_all_quizzes_count()
        channels = await self.db.get_all_channels()

        return {
            "total_users": user_count,
            "total_quizzes": quiz_count,
            "total_channels": len(channels),
        }

    async def get_best_publish_time(self, user_id):
        # Simple heuristic: suggest peak hours
        return {
            "weekday": "14:00 - 16:00",
            "weekend": "10:00 - 12:00",
            "best_day": "Sunday",
        }