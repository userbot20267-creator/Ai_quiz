import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, application):
        self.application = application

    async def notify_publish_success(self, user_id, quiz_id, channel_id):
        try:
            db = self.application.bot_data.get("db")
            quiz = await db.get_quiz(quiz_id)
            channel = await db.get_channel(channel_id)

            quiz_title = quiz["title"] if quiz else "Unknown"
            channel_title = channel["title"] if channel else "Unknown"

            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"✅ تم نشر الاختبار '{quiz_title}' في '{channel_title}' بنجاح!",
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")

    async def notify_publish_failed(self, user_id, quiz_id, error):
        try:
            db = self.application.bot_data.get("db")
            quiz = await db.get_quiz(quiz_id)
            quiz_title = quiz["title"] if quiz else "Unknown"

            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"❌ فشل نشر الاختبار '{quiz_title}'!\n\nالسبب: {error}",
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")

    async def notify_schedule_complete(self, user_id, quiz_id):
        try:
            db = self.application.bot_data.get("db")
            quiz = await db.get_quiz(quiz_id)
            quiz_title = quiz["title"] if quiz else "Unknown"

            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"📅 انتهى جدول النشر للاختبار '{quiz_title}'.",
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")

    async def notify_before_publish(self, user_id, quiz_id, minutes=5):
        try:
            db = self.application.bot_data.get("db")
            quiz = await db.get_quiz(quiz_id)
            quiz_title = quiz["title"] if quiz else "Unknown"

            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"⏰ سيتم نشر الاختبار '{quiz_title}' خلال {minutes} دقائق.",
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")