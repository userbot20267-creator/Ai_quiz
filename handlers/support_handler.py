import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from config import config
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard

logger = logging.getLogger(__name__)


class SupportHandler:
    SUPPORT_MESSAGE = 1

    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def start_support(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        await query.edit_message_text(
            get_text("support_enter", language),
            parse_mode=ParseMode.HTML,
        )
        return self.SUPPORT_MESSAGE

    async def receive_support_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        message = update.message.text
        await db.save_support_message(user.id, message)

        # Notify owner
        try:
            name = user.first_name or user.username or "Unknown"
            await context.bot.send_message(
                chat_id=config.OWNER_ID,
                text=f"💬 <b>رسالة دعم جديدة</b>\n\n"
                f"👤 من: {name} (ID: {user.id})\n"
                f"💬 الرسالة: {message}",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Failed to notify owner: {e}")

        await update.message.reply_text(
            get_text("support_sent", language),
            reply_markup=back_to_menu_keyboard(language),
        )
        return ConversationHandler.END

    async def cancel_support(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        if update.message:
            await update.message.reply_text(
                get_text("cancelled", language),
                reply_markup=back_to_menu_keyboard(language),
            )

        return ConversationHandler.END