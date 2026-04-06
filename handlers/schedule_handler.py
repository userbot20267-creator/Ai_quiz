import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from locales import get_text
from keyboards.inline_keyboards import repeat_keyboard, publish_channel_keyboard
from keyboards.main_keyboards import (
    confirm_cancel_keyboard,
    back_to_menu_keyboard,
)
from utils.validators import validate_datetime_format

logger = logging.getLogger(__name__)


class ScheduleHandler:
    SELECT_QUIZ = 1
    SELECT_CHANNEL = 2
    SET_DATETIME = 3
    SET_REPEAT = 4
    CONFIRM_SCHEDULE = 5

    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def start_schedule(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quizzes = await db.get_user_quizzes(user.id)

        if not quizzes:
            await query.edit_message_text(
                get_text("no_quizzes", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return ConversationHandler.END

        keyboard = []
        for quiz in quizzes[:20]:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📝 {quiz['title']}",
                        callback_data=f"sch_quiz_{quiz['quiz_id']}",
                    )
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    get_text("cancel", language),
                    callback_data="cancel_sch",
                )
            ]
        )

        await query.edit_message_text(
            get_text("select_quiz_to_publish", language),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )
        return self.SELECT_QUIZ

    async def select_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("sch_quiz_", ""))
        context.user_data["schedule_quiz_id"] = quiz_id

        channels = await db.get_user_channels(user.id)

        if not channels:
            await query.edit_message_text(
                get_text("no_channels", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return ConversationHandler.END

        keyboard = []
        for ch in channels:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📢 {ch['title']}",
                        callback_data=f"sch_ch_{ch['channel_id']}",
                    )
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    get_text("cancel", language),
                    callback_data="cancel_sch",
                )
            ]
        )

        await query.edit_message_text(
            get_text("select_channel", language),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )
        return self.SELECT_CHANNEL

    async def select_channel(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        channel_id = int(query.data.replace("sch_ch_", ""))
        context.user_data["schedule_channel_id"] = channel_id

        await query.edit_message_text(
            get_text("enter_schedule_time", language),
            parse_mode=ParseMode.HTML,
        )
        return self.SET_DATETIME

    async def set_datetime(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        dt_str = update.message.text.strip()

        if not validate_datetime_format(dt_str):
            await update.message.reply_text(
                "⚠️ صيغة خاطئة! استخدم: <code>YYYY-MM-DD HH:MM</code>\nمثال: <code>2024-03-20 14:00</code>",
                parse_mode=ParseMode.HTML,
            )
            return self.SET_DATETIME

        try:
            scheduled_time = datetime.fromisoformat(dt_str)
            if scheduled_time <= datetime.now():
                await update.message.reply_text(
                    "⚠️ الموعد يجب أن يكون في المستقبل!"
                )
                return self.SET_DATETIME
        except ValueError:
            await update.message.reply_text("⚠️ تاريخ غير صالح!")
            return self.SET_DATETIME

        context.user_data["schedule_time"] = dt_str

        await update.message.reply_text(
            get_text("select_repeat", language),
            reply_markup=repeat_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.SET_REPEAT

    async def set_repeat(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        repeat_type = query.data.replace("repeat_", "")
        context.user_data["schedule_repeat"] = repeat_type

        repeat_labels = {
            "none": get_text("none_repeat", language),
            "daily": get_text("daily", language),
            "weekly": get_text("weekly", language),
            "monthly": get_text("monthly", language),
        }

        text = (
            f"📅 <b>تأكيد الجدولة</b>\n\n"
            f"⏰ الموعد: {context.user_data.get('schedule_time')}\n"
            f"🔄 التكرار: {repeat_labels.get(repeat_type, repeat_type)}\n\n"
            f"هل تريد المتابعة؟"
        )

        await query.edit_message_text(
            text,
            reply_markup=confirm_cancel_keyboard(
                "confirm_sch", "cancel_sch", language
            ),
            parse_mode=ParseMode.HTML,
        )
        return self.CONFIRM_SCHEDULE

    async def confirm_schedule(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = context.user_data.get("schedule_quiz_id")
        channel_id = context.user_data.get("schedule_channel_id")
        scheduled_time = context.user_data.get("schedule_time")
        repeat_type = context.user_data.get("schedule_repeat", "none")

        schedule_id = await db.add_schedule(
            quiz_id, channel_id, user.id, scheduled_time, repeat_type
        )

        scheduler = context.bot_data.get("scheduler")
        if scheduler:
            run_time = datetime.fromisoformat(scheduled_time)
            await scheduler.add_schedule_job(
                schedule_id, quiz_id, channel_id, run_time
            )

        repeat_labels = {
            "none": get_text("none_repeat", language),
            "daily": get_text("daily", language),
            "weekly": get_text("weekly", language),
            "monthly": get_text("monthly", language),
        }

        await query.edit_message_text(
            get_text("schedule_set", language).format(
                time=scheduled_time,
                repeat=repeat_labels.get(repeat_type, repeat_type),
            ),
            reply_markup=back_to_menu_keyboard(language),
            parse_mode=ParseMode.HTML,
        )

        context.user_data.pop("schedule_quiz_id", None)
        context.user_data.pop("schedule_channel_id", None)
        context.user_data.pop("schedule_time", None)
        context.user_data.pop("schedule_repeat", None)

        return ConversationHandler.END

    async def cancel_schedule(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data.pop("schedule_quiz_id", None)
        context.user_data.pop("schedule_channel_id", None)
        context.user_data.pop("schedule_time", None)
        context.user_data.pop("schedule_repeat", None)

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                get_text("cancelled", language),
                reply_markup=back_to_menu_keyboard(language),
            )
        else:
            await update.message.reply_text(
                get_text("cancelled", language),
                reply_markup=back_to_menu_keyboard(language),
            )

        return ConversationHandler.END