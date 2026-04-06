import logging
from services.quiz_service import QuizService

logger = logging.getLogger(__name__)


class PublishService:
    def __init__(self, application):
        self.application = application
        self.quiz_service = QuizService()

    async def publish_quiz(self, quiz_id, channel_id):
        db = self.application.bot_data.get("db")
        bot = self.application.bot

        quiz = await db.get_quiz(quiz_id)
        if not quiz:
            return False, "Quiz not found"

        questions = await db.get_quiz_questions(quiz_id)
        if not questions:
            return False, "No questions in quiz"

        is_duplicate = await db.check_duplicate_publish(quiz_id, channel_id)
        if is_duplicate:
            logger.warning(
                f"Duplicate publish attempt: quiz={quiz_id}, channel={channel_id}"
            )

        success, error = await self.quiz_service.publish_quiz_to_channel(
            bot, quiz, questions, channel_id
        )

        if success:
            await db.log_publish(quiz_id, channel_id, "success")
            await db.increment_quiz_participants(quiz_id)
            await db.save_analytics(quiz_id, channel_id)
        else:
            await db.log_publish(quiz_id, channel_id, "failed")

        return success, error

    async def publish_to_multiple_channels(self, quiz_id, channel_ids):
        results = {}
        for ch_id in channel_ids:
            success, error = await self.publish_quiz(quiz_id, ch_id)
            results[ch_id] = {"success": success, "error": error}
        return results