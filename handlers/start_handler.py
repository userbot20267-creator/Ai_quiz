import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import config
from locales import get_text
from keyboards.main_keyboards import main_menu_keyboard
from keyboards.inline_keyboards import force_subscribe_keyboard

logger = logging.getLogger(__name__)


class StartHandler:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db = context.bot_data.get("db")

        if db:
            await db.add_user(
                user.id,
                user.username or "",
                user.first_name or "",
                user.last_name or "",
            )

            if await db.is_banned(user.id):
                await update.message.reply_text(
                    "⛔ تم حظرك من استخدام البوت!"
                )
                return

        # Check force subscribe
        force_channels = []
        if db:
            force_channels = await db.get_force_channels()

        if force_channels:
            not_subscribed = []
            for ch in force_channels:
                try:
                    member = await context.bot.get_chat_member(
                        chat_id=ch["channel_id"], user_id=user.id
                    )
                    if member.status in ("left", "kicked"):
                        not_subscribed.append(ch)
                except Exception:
                    not_subscribed.append(ch)

            if not_subscribed:
                language = "ar"
                if db:
                    language = await db.get_user_language(user.id)

                await update.message.reply_text(
                    get_text("force_subscribe", language),
                    reply_markup=force_subscribe_keyboard(not_subscribed),
                    parse_mode=ParseMode.HTML,
                )
                return

        # Handle deep link
        if context.args:
            arg = context.args[0]
            if arg.startswith("quiz_"):
                code = arg[5:]
                if db:
                    link_data = await db.get_quiz_link(code)
                    if link_data:
                        await db.increment_link_clicks(code)
                        context.user_data["take_quiz_id"] = link_data[
                            "quiz_id"
                        ]
                        # Will be handled by quiz handler
                        await update.message.reply_text(
                            "🎯 جاري تحميل الاختبار..."
                        )
                        return

        language = "ar"
        if db:
            language = await db.get_user_language(user.id)

        is_admin = user.id in config.ADMINS

        await update.message.reply_text(
            get_text("welcome", language),
            reply_markup=main_menu_keyboard(language, is_admin),
            parse_mode=ParseMode.HTML,
        )

    async def main_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")

        language = "ar"
        if db:
            language = await db.get_user_language(user.id)

        is_admin = user.id in config.ADMINS

        await query.edit_message_text(
            get_text("main_menu", language),
            reply_markup=main_menu_keyboard(language, is_admin),
            parse_mode=ParseMode.HTML,
        )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")

        language = "ar"
        if db:
            language = await db.get_user_language(user.id)

        await update.message.reply_text(
            get_text("help_text", language),
            parse_mode=ParseMode.HTML,
        )