import logging
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from config import config
from locales import get_text
from keyboards.main_keyboards import (
    confirm_cancel_keyboard,
    back_to_menu_keyboard,
)

logger = logging.getLogger(__name__)


class BroadcastHandler:
    BROADCAST_MESSAGE = 1
    CONFIRM_BROADCAST = 2

    async def start_broadcast(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        if user.id not in config.ADMINS:
            await query.answer("⛔ ليس لديك صلاحية!", show_alert=True)
            return ConversationHandler.END

        db = context.bot_data.get("db")
        language = await db.get_user_language(user.id) if db else "ar"

        await query.edit_message_text(
            get_text("broadcast_enter", language),
            parse_mode=ParseMode.HTML,
        )
        return self.BROADCAST_MESSAGE

    async def receive_broadcast_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await db.get_user_language(user.id) if db else "ar"

        message = update.message.text
        context.user_data["broadcast_message"] = message

        user_count = await db.get_user_count()

        await update.message.reply_text(
            get_text("broadcast_confirm", language).format(
                message=message, count=user_count
            ),
            reply_markup=confirm_cancel_keyboard(
                "confirm_broadcast", "cancel_broadcast", language
            ),
            parse_mode=ParseMode.HTML,
        )
        return self.CONFIRM_BROADCAST

    async def confirm_broadcast(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await db.get_user_language(user.id) if db else "ar"

        message = context.user_data.get("broadcast_message", "")
        users = await db.get_all_users()

        await query.edit_message_text("📨 جاري الإرسال...")

        success = 0
        failed = 0

        for u in users:
            try:
                await context.bot.send_message(
                    chat_id=u["user_id"],
                    text=message,
                    parse_mode=ParseMode.HTML,
                )
                success += 1
                await asyncio.sleep(0.05)
            except Exception:
                failed += 1

        await query.edit_message_text(
            get_text("broadcast_done", language).format(
                success=success, failed=failed
            ),
            reply_markup=back_to_menu_keyboard(language),
            parse_mode=ParseMode.HTML,
        )

        context.user_data.pop("broadcast_message", None)
        return ConversationHandler.END

    async def cancel_broadcast(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await db.get_user_language(user.id) if db else "ar"

        context.user_data.pop("broadcast_message", None)

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