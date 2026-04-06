import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.publish_service import PublishService

logger = logging.getLogger(__name__)


class QueueService:
    def __init__(self, application):
        self.application = application
        self.scheduler = AsyncIOScheduler()
        self.publish_service = PublishService(application)
        self.is_running = True

    async def start(self):
        self.scheduler.add_job(
            self.process_queue,
            "interval",
            minutes=5,
            id="queue_processor",
        )
        self.scheduler.start()
        logger.info("Queue service started")

    async def stop(self):
        self.is_running = False
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def process_queue(self):
        if not self.is_running:
            return

        try:
            db = self.application.bot_data.get("db")
            if not db:
                return

            pending = await db.get_pending_queue()

            for item in pending[:5]:
                success, error = await self.publish_service.publish_quiz(
                    item["quiz_id"], item["channel_id"]
                )
                if success:
                    await db.update_queue_status(
                        item["queue_id"], "published"
                    )
                else:
                    await db.update_queue_status(
                        item["queue_id"], "failed"
                    )

        except Exception as e:
            logger.error(f"Queue processing error: {e}")

    async def pause(self):
        self.is_running = False

    async def resume(self):
        self.is_running = True