import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard

logger = logging.getLogger(__name__)


class CalendarHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def show_calendar(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        schedules = await db.get_user_schedules(user.id)

        if not schedules:
            text = get_text("no_schedule", language)
            if update.message:
                await update.message.reply_text(
                    text, reply_markup=back_to_menu_keyboard(language)
                )
            return

        text = "📅 <b>جدول النشر</b>\n\n" if language == "ar" else "📅 <b>Publishing Schedule</b>\n\n"

        now = datetime.now()
        week_end = now + timedelta(days=7)

        text += "📌 <b>هذا الأسبوع:</b>\n" if language == "ar" else "📌 <b>This Week:</b>\n"

        for schedule in schedules:
            try:
                sch_time = datetime.fromisoformat(schedule["scheduled_time"])
                if now <= sch_time <= week_end:
                    text += (
                        f"  📝 {schedule['quiz_title']} → {schedule['channel_title']}\n"
                        f"  ⏰ {sch_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                    )
            except (ValueError, TypeError):
                pass

        text += "\n📋 <b>جميع الجداول:</b>\n" if language == "ar" else "\n📋 <b>All Schedules:</b>\n"

        for schedule in schedules:
            repeat_labels = {
                "none": "مرة واحدة",
                "daily": "يومي",
                "weekly": "أسبوعي",
                "monthly": "شهري",
            }
            repeat = repeat_labels.get(
                schedule.get("repeat_type", "none"), "مرة واحدة"
            )
            text += (
                f"  📝 {schedule['quiz_title']}\n"
                f"  📢 {schedule['channel_title']}\n"
                f"  ⏰ {schedule['scheduled_time'][:16]}\n"
                f"  🔄 {repeat}\n\n"
            )

        keyboard = [
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ]
        ]

        if update.message:
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
            )

    async def calendar_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        await self.show_calendar(update, context)