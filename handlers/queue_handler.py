import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard

logger = logging.getLogger(__name__)


class QueueHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def show_queue(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        queue_items = await db.get_user_queue(user.id)

        if not queue_items:
            text = get_text("queue_empty", language)
            if update.message:
                await update.message.reply_text(
                    text, reply_markup=back_to_menu_keyboard(language)
                )
            return

        text = "📦 <b>قائمة الانتظار</b>\n\n" if language == "ar" else "📦 <b>Publishing Queue</b>\n\n"

        for i, item in enumerate(queue_items):
            status_emoji = {
                "pending": "⏳",
                "published": "✅",
                "failed": "❌",
                "paused": "⏸️",
            }
            emoji = status_emoji.get(item["status"], "📋")
            text += f"{emoji} {i + 1}. {item['quiz_title']} → {item['channel_title']}\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    "⏸️ إيقاف" if language == "ar" else "⏸️ Pause",
                    callback_data="queue_pause",
                ),
                InlineKeyboardButton(
                    "▶️ استئناف" if language == "ar" else "▶️ Resume",
                    callback_data="queue_resume",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗑️ مسح الكل" if language == "ar" else "🗑️ Clear All",
                    callback_data="queue_clear",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ],
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

    async def queue_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)
        action = query.data.replace("queue_", "")

        queue_service = context.bot_data.get("queue_service")

        if action == "pause":
            if queue_service:
                await queue_service.pause()
            await query.edit_message_text(
                "⏸️ تم إيقاف قائمة الانتظار مؤقتاً.",
                reply_markup=back_to_menu_keyboard(language),
            )

        elif action == "resume":
            if queue_service:
                await queue_service.resume()
            await query.edit_message_text(
                "▶️ تم استئناف قائمة الانتظار.",
                reply_markup=back_to_menu_keyboard(language),
            )

        elif action == "clear":
            db = context.bot_data.get("db")
            queue_items = await db.get_user_queue(user.id)
            for item in queue_items:
                await db.remove_from_queue(item["queue_id"])
            await query.edit_message_text(
                "🗑️ تم مسح قائمة الانتظار.",
                reply_markup=back_to_menu_keyboard(language),
            )