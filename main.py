import logging
import asyncio
import sys

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from config import config
from database.db_manager import DatabaseManager
from handlers.start_handler import StartHandler
from handlers.quiz_handler import QuizHandler
from handlers.publish_handler import PublishHandler
from handlers.schedule_handler import ScheduleHandler
from handlers.queue_handler import QueueHandler
from handlers.admin_handler import AdminHandler
from handlers.ai_handler import AIHandler
from handlers.analytics_handler import AnalyticsHandler
from handlers.settings_handler import SettingsHandler
from handlers.broadcast_handler import BroadcastHandler
from handlers.import_export_handler import ImportExportHandler
from handlers.channel_handler import ChannelHandler
from handlers.calendar_handler import CalendarHandler
from handlers.link_handler import LinkHandler
from handlers.ab_test_handler import ABTestHandler
from handlers.support_handler import SupportHandler
from services.scheduler_service import SchedulerService
from services.queue_service import QueueService
from services.notification_service import NotificationService
from services.protection_service import ProtectionService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application):
    db = DatabaseManager()
    await db.initialize()
    application.bot_data["db"] = db

    scheduler_service = SchedulerService(application)
    await scheduler_service.start()
    application.bot_data["scheduler"] = scheduler_service

    queue_service = QueueService(application)
    await queue_service.start()
    application.bot_data["queue_service"] = queue_service

    notification_service = NotificationService(application)
    application.bot_data["notification"] = notification_service

    protection_service = ProtectionService()
    application.bot_data["protection"] = protection_service

    logger.info("Bot initialized successfully!")
    logger.info(f"OpenRouter Model: {config.OPENROUTER_MODEL}")
    logger.info(f"OpenRouter API: {'Connected' if config.OPENROUTER_API_KEY else 'Not configured'}")


async def post_shutdown(application):
    db = application.bot_data.get("db")
    if db:
        await db.close()
    scheduler = application.bot_data.get("scheduler")
    if scheduler:
        await scheduler.stop()
    logger.info("Bot shut down successfully!")


# ─── معالج النصوص العام لـ AI ──────────────────
ai_handler_instance = AIHandler()


async def handle_text_message(update, context):
    """معالج النصوص العامة - يتحقق إذا كان المستخدم ينتظر إدخال AI"""
    if not update.message or not update.message.text:
        return

    # التحقق من حالة AI
    ai_action = context.user_data.get("ai_action")
    if ai_action:
        handled = await ai_handler_instance.handle_ai_text_input(update, context)
        if handled:
            return


def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        sys.exit(1)

    if not config.OWNER_ID:
        logger.error("OWNER_ID is not set!")
        sys.exit(1)

    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    start_handler = StartHandler()
    quiz_handler = QuizHandler()
    publish_handler = PublishHandler()
    schedule_handler = ScheduleHandler()
    queue_handler_inst = QueueHandler()
    admin_handler = AdminHandler()
    ai_handler = AIHandler()
    analytics_handler = AnalyticsHandler()
    settings_handler = SettingsHandler()
    broadcast_handler = BroadcastHandler()
    import_export_handler = ImportExportHandler()
    channel_handler = ChannelHandler()
    calendar_handler = CalendarHandler()
    link_handler = LinkHandler()
    ab_test_handler = ABTestHandler()
    support_handler = SupportHandler()

    # ─── Conversation Handlers ─────────────────────

    quiz_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                quiz_handler.start_create_quiz, pattern="^create_quiz$"
            ),
        ],
        states={
            quiz_handler.QUIZ_TITLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    quiz_handler.receive_quiz_title,
                )
            ],
            quiz_handler.QUIZ_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    quiz_handler.receive_quiz_description,
                ),
                CallbackQueryHandler(
                    quiz_handler.skip_description, pattern="^skip_description$"
                ),
            ],
            quiz_handler.QUIZ_CATEGORY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    quiz_handler.receive_quiz_category,
                ),
                CallbackQueryHandler(
                    quiz_handler.select_category, pattern="^cat_"
                ),
            ],
            quiz_handler.ADD_QUESTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    quiz_handler.receive_question,
                ),
                CallbackQueryHandler(
                    quiz_handler.finish_quiz, pattern="^finish_quiz$"
                ),
                CallbackQueryHandler(
                    quiz_handler.add_media, pattern="^add_media$"
                ),
            ],
            quiz_handler.QUESTION_OPTIONS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    quiz_handler.receive_options,
                )
            ],
            quiz_handler.CORRECT_ANSWER: [
                CallbackQueryHandler(
                    quiz_handler.receive_correct_answer, pattern="^answer_"
                )
            ],
            quiz_handler.QUESTION_MEDIA: [
                MessageHandler(
                    filters.PHOTO
                    | filters.VIDEO
                    | filters.AUDIO
                    | filters.VOICE
                    | filters.Document.ALL,
                    quiz_handler.receive_media,
                ),
                CallbackQueryHandler(
                    quiz_handler.skip_media, pattern="^skip_media$"
                ),
            ],
            quiz_handler.QUESTION_TYPE: [
                CallbackQueryHandler(
                    quiz_handler.select_question_type, pattern="^qtype_"
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", quiz_handler.cancel_quiz),
            CallbackQueryHandler(
                quiz_handler.cancel_quiz, pattern="^cancel_quiz$"
            ),
        ],
        per_message=False,
    )

    publish_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                publish_handler.start_publish, pattern="^publish_quiz_"
            ),
            CallbackQueryHandler(
                publish_handler.start_publish_menu, pattern="^publish_menu$"
            ),
        ],
        states={
            publish_handler.SELECT_QUIZ: [
                CallbackQueryHandler(
                    publish_handler.select_quiz, pattern="^pub_quiz_"
                )
            ],
            publish_handler.SELECT_CHANNEL: [
                CallbackQueryHandler(
                    publish_handler.select_channel, pattern="^pub_ch_"
                ),
                CallbackQueryHandler(
                    publish_handler.select_all_channels,
                    pattern="^pub_all_channels$",
                ),
            ],
            publish_handler.CONFIRM_PUBLISH: [
                CallbackQueryHandler(
                    publish_handler.confirm_publish, pattern="^confirm_pub$"
                ),
                CallbackQueryHandler(
                    publish_handler.cancel_publish, pattern="^cancel_pub$"
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", publish_handler.cancel_publish),
        ],
        per_message=False,
    )

    schedule_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                schedule_handler.start_schedule, pattern="^schedule_quiz$"
            ),
        ],
        states={
            schedule_handler.SELECT_QUIZ: [
                CallbackQueryHandler(
                    schedule_handler.select_quiz, pattern="^sch_quiz_"
                )
            ],
            schedule_handler.SELECT_CHANNEL: [
                CallbackQueryHandler(
                    schedule_handler.select_channel, pattern="^sch_ch_"
                )
            ],
            schedule_handler.SET_DATETIME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    schedule_handler.set_datetime,
                )
            ],
            schedule_handler.SET_REPEAT: [
                CallbackQueryHandler(
                    schedule_handler.set_repeat, pattern="^repeat_"
                )
            ],
            schedule_handler.CONFIRM_SCHEDULE: [
                CallbackQueryHandler(
                    schedule_handler.confirm_schedule,
                    pattern="^confirm_sch$",
                ),
                CallbackQueryHandler(
                    schedule_handler.cancel_schedule,
                    pattern="^cancel_sch$",
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", schedule_handler.cancel_schedule),
        ],
        per_message=False,
    )

    broadcast_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                broadcast_handler.start_broadcast, pattern="^admin_broadcast$"
            ),
        ],
        states={
            broadcast_handler.BROADCAST_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    broadcast_handler.receive_broadcast_message,
                )
            ],
            broadcast_handler.CONFIRM_BROADCAST: [
                CallbackQueryHandler(
                    broadcast_handler.confirm_broadcast,
                    pattern="^confirm_broadcast$",
                ),
                CallbackQueryHandler(
                    broadcast_handler.cancel_broadcast,
                    pattern="^cancel_broadcast$",
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", broadcast_handler.cancel_broadcast),
        ],
        per_message=False,
    )

    support_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                support_handler.start_support, pattern="^support$"
            ),
        ],
        states={
            support_handler.SUPPORT_MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    support_handler.receive_support_message,
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", support_handler.cancel_support),
        ],
        per_message=False,
    )

    # ─── Register Handlers ─────────────────────────

    # Commands
    application.add_handler(CommandHandler("start", start_handler.start))
    application.add_handler(CommandHandler("help", start_handler.help_command))
    application.add_handler(
        CommandHandler("add_quiz", quiz_handler.quick_add_quiz)
    )
    application.add_handler(
        CommandHandler("add_quiz_bulk", quiz_handler.add_quiz_bulk)
    )
    application.add_handler(
        CommandHandler("my_quizzes", quiz_handler.my_quizzes)
    )
    application.add_handler(
        CommandHandler("add_channel", channel_handler.add_channel)
    )
    application.add_handler(
        CommandHandler("add_force", channel_handler.add_force)
    )
    application.add_handler(
        CommandHandler("my_channels", channel_handler.my_channels)
    )
    application.add_handler(
        CommandHandler("stats", analytics_handler.user_stats)
    )
    application.add_handler(
        CommandHandler("admin", admin_handler.admin_panel)
    )
    application.add_handler(
        CommandHandler("all_users", admin_handler.all_users)
    )
    application.add_handler(
        CommandHandler("all_quizzes", admin_handler.all_quizzes)
    )
    application.add_handler(
        CommandHandler("del_quiz", admin_handler.del_quiz)
    )
    application.add_handler(
        CommandHandler("ban", admin_handler.ban)
    )
    application.add_handler(
        CommandHandler("unban", admin_handler.unban)
    )
    application.add_handler(
        CommandHandler("language", settings_handler.change_language)
    )
    application.add_handler(
        CommandHandler("calendar", calendar_handler.show_calendar)
    )
    application.add_handler(
        CommandHandler("queue", queue_handler_inst.show_queue)
    )
    application.add_handler(
        CommandHandler("export", import_export_handler.export_quizzes)
    )
    application.add_handler(
        CommandHandler("import", import_export_handler.start_import)
    )
    application.add_handler(
        CommandHandler("generate", ai_handler.generate_quiz)
    )
    application.add_handler(
        CommandHandler("link", link_handler.create_quiz_link)
    )

    # Conversation Handlers
    application.add_handler(quiz_conv_handler)
    application.add_handler(publish_conv_handler)
    application.add_handler(schedule_conv_handler)
    application.add_handler(broadcast_conv_handler)
    application.add_handler(support_conv_handler)

    # Callback Query Handlers
    application.add_handler(
        CallbackQueryHandler(start_handler.main_menu, pattern="^main_menu$")
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.quiz_menu, pattern="^quiz_menu$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.view_quiz, pattern="^view_quiz_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.delete_quiz, pattern="^delete_quiz_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.edit_quiz, pattern="^edit_quiz_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.take_quiz, pattern="^take_quiz_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.answer_question, pattern="^ans_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            quiz_handler.handle_inline_answer, pattern="^inline_ans_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            channel_handler.channel_menu, pattern="^channel_menu$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            channel_handler.remove_channel, pattern="^remove_ch_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            analytics_handler.analytics_menu, pattern="^analytics_menu$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            analytics_handler.quiz_analytics, pattern="^quiz_stats_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            admin_handler.admin_callback, pattern="^admin_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            settings_handler.settings_menu, pattern="^settings$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            settings_handler.set_language, pattern="^lang_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            settings_handler.change_language, pattern="^change_language$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            queue_handler_inst.queue_callback, pattern="^queue_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            ai_handler.ai_menu, pattern="^ai_menu$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            ai_handler.ai_callback, pattern="^ai_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            calendar_handler.calendar_callback, pattern="^cal_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            ab_test_handler.ab_callback, pattern="^ab_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            link_handler.link_callback, pattern="^link_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            import_export_handler.import_callback, pattern="^import_"
        )
    )

    # ─── AI Text Handler (يجب أن يكون قبل معالجات الملفات) ───
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message,
        ),
        group=1,
    )

    # Document Handler
    application.add_handler(
        MessageHandler(
            filters.Document.ALL, import_export_handler.receive_import_file
        )
    )

    # Bot added to chat
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            channel_handler.bot_added_to_chat,
        )
    )

    logger.info("Starting bot...")
    logger.info(f"Owner ID: {config.OWNER_ID}")
    logger.info(f"AI Model: {config.OPENROUTER_MODEL}")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
