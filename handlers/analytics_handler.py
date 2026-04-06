import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class AnalyticsHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def user_stats(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        analytics = AnalyticsService(db)
        stats = await analytics.get_user_stats(user.id)

        text = get_text("stats_user", language).format(
            quizzes=stats["total_quizzes"],
            questions=stats["total_questions"],
            channels=stats["total_channels"],
            schedules=stats["active_schedules"],
        )

        await update.message.reply_text(
            text,
            reply_markup=back_to_menu_keyboard(language),
            parse_mode=ParseMode.HTML,
        )

    async def analytics_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        analytics = AnalyticsService(db)
        stats = await analytics.get_user_stats(user.id)
        best_time = await analytics.get_best_publish_time(user.id)

        text = (
            f"📊 <b>التحليلات</b>\n\n"
            f"📝 اختبارات: {stats['total_quizzes']}\n"
            f"❓ أسئلة: {stats['total_questions']}\n"
            f"📢 قنوات: {stats['total_channels']}\n"
            f"📅 جداول نشطة: {stats['active_schedules']}\n\n"
            f"⏰ <b>أفضل وقت للنشر:</b>\n"
            f"📅 أيام العمل: {best_time['weekday']}\n"
            f"🏖️ عطلة نهاية الأسبوع: {best_time['weekend']}\n"
            f"🌟 أفضل يوم: {best_time['best_day']}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 تفاصيل الاختبارات"
                    if language == "ar"
                    else "📊 Quiz Details",
                    callback_data="analytics_quizzes",
                )
            ],
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ],
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )

    async def quiz_analytics(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("quiz_stats_", ""))
        analytics = AnalyticsService(db)
        stats = await analytics.get_quiz_stats(quiz_id)

        if not stats["quiz"]:
            await query.edit_message_text(
                get_text("error_occurred", language)
            )
            return

        text = (
            f"📊 <b>إحصائيات: {stats['quiz']['title']}</b>\n\n"
            f"❓ عدد الأسئلة: {stats['question_count']}\n"
            f"👥 المشاركين: {stats['participant_count']}\n"
            f"📈 متوسط النتيجة: {stats['avg_score']}%\n"
            f"📤 مرات النشر: {stats['publish_count']}"
        )

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            get_text("back", language),
                            callback_data="analytics_menu",
                        )
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )