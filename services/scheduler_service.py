import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.publish_service import PublishService

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, application):
        self.application = application
        self.scheduler = AsyncIOScheduler()
        self.publish_service = PublishService(application)

    async def start(self):
        self.scheduler.add_job(
            self.check_schedules,
            "interval",
            minutes=1,
            id="schedule_checker",
        )
        self.scheduler.start()
        logger.info("Scheduler started")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    async def check_schedules(self):
        try:
            db = self.application.bot_data.get("db")
            if not db:
                return

            schedules = await db.get_active_schedules()
            now = datetime.now()

            for schedule in schedules:
                scheduled_time = datetime.fromisoformat(
                    schedule["scheduled_time"]
                )

                if scheduled_time <= now:
                    success, error = await self.publish_service.publish_quiz(
                        schedule["quiz_id"], schedule["channel_id"]
                    )

                    if success:
                        await db.update_schedule_last_published(
                            schedule["schedule_id"]
                        )
                        notification = self.application.bot_data.get(
                            "notification"
                        )
                        if notification:
                            await notification.notify_publish_success(
                                schedule["user_id"],
                                schedule["quiz_id"],
                                schedule["channel_id"],
                            )
                    else:
                        notification = self.application.bot_data.get(
                            "notification"
                        )
                        if notification:
                            await notification.notify_publish_failed(
                                schedule["user_id"],
                                schedule["quiz_id"],
                                error,
                            )

                    repeat = schedule.get("repeat_type", "none")
                    if repeat == "daily":
                        new_time = scheduled_time + timedelta(days=1)
                        await db.db.execute(
                            "UPDATE schedules SET scheduled_time=? WHERE schedule_id=?",
                            (new_time.isoformat(), schedule["schedule_id"]),
                        )
                        await db.db.commit()
                    elif repeat == "weekly":
                        new_time = scheduled_time + timedelta(weeks=1)
                        await db.db.execute(
                            "UPDATE schedules SET scheduled_time=? WHERE schedule_id=?",
                            (new_time.isoformat(), schedule["schedule_id"]),
                        )
                        await db.db.commit()
                    elif repeat == "monthly":
                        new_time = scheduled_time + timedelta(days=30)
                        await db.db.execute(
                            "UPDATE schedules SET scheduled_time=? WHERE schedule_id=?",
                            (new_time.isoformat(), schedule["schedule_id"]),
                        )
                        await db.db.commit()
                    else:
                        await db.deactivate_schedule(schedule["schedule_id"])

        except Exception as e:
            logger.error(f"Schedule check error: {e}")

    async def add_schedule_job(self, schedule_id, quiz_id, channel_id, run_time):
        self.scheduler.add_job(
            self.publish_service.publish_quiz,
            "date",
            run_date=run_time,
            args=[quiz_id, channel_id],
            id=f"schedule_{schedule_id}",
            replace_existing=True,
        )