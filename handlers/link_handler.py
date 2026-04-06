import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard
from services.link_service import LinkService
from utils.helpers import generate_unique_code

logger = logging.getLogger(__name__)


class LinkHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def create_quiz_link(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        if not context.args:
            await update.message.reply_text(
                "🔗 استخدم: <code>/link QUIZ_ID</code>",
                parse_mode=ParseMode.HTML,
            )
            return

        try:
            quiz_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ ID غير صالح!")
            return

        quiz = await db.get_quiz(quiz_id)
        if not quiz or quiz["user_id"] != user.id:
            await update.message.reply_text("❌ الاختبار غير موجود!")
            return

        bot_info = await context.bot.get_me()
        link_service = LinkService(db, bot_info.username)
        link, code = await link_service.create_quiz_link(quiz_id)

        await update.message.reply_text(
            f"🔗 <b>رابط الاختبار</b>\n\n"
            f"📝 {quiz['title']}\n"
            f"🔗 {link}\n\n"
            f"شارك هذا الرابط مع الآخرين!",
            reply_markup=back_to_menu_keyboard(language),
            parse_mode=ParseMode.HTML,
        )

    async def link_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        action = query.data.replace("link_", "")

        if action.startswith("quiz_"):
            quiz_id = int(action.replace("quiz_", ""))
            quiz = await db.get_quiz(quiz_id)

            if not quiz:
                await query.edit_message_text("❌ الاختبار غير موجود!")
                return

            bot_info = await context.bot.get_me()
            link_service = LinkService(db, bot_info.username)
            link, code = await link_service.create_quiz_link(quiz_id)
            link_stats = await link_service.get_link_stats(quiz_id)

            await query.edit_message_text(
                f"🔗 <b>روابط الاختبار</b>\n\n"
                f"📝 {quiz['title']}\n"
                f"🔗 {link}\n"
                f"📊 إجمالي النقرات: {link_stats['total_clicks']}",
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )