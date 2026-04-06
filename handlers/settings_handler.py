import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.inline_keyboards import language_keyboard
from keyboards.main_keyboards import back_to_menu_keyboard

logger = logging.getLogger(__name__)


class SettingsHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def settings_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [
                InlineKeyboardButton(
                    "🌍 اللغة / Language",
                    callback_data="change_language",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ],
        ]

        await query.edit_message_text(
            get_text("settings", language),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )

    async def change_language(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if update.message:
            await update.message.reply_text(
                "🌍 اختر اللغة / Choose Language:",
                reply_markup=language_keyboard(),
            )
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                "🌍 اختر اللغة / Choose Language:",
                reply_markup=language_keyboard(),
            )

    async def set_language(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")

        language = query.data.replace("lang_", "")
        if db:
            await db.set_user_language(user.id, language)

        await query.edit_message_text(
            get_text("language_changed", language),
            reply_markup=back_to_menu_keyboard(language),
        )