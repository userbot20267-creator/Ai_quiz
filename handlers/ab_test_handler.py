import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard

logger = logging.getLogger(__name__)


class ABTestHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def ab_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        action = query.data.replace("ab_", "")

        if action == "menu":
            tests = await db.get_ab_tests(user.id)

            text = "🔄 <b>اختبارات A/B</b>\n\n" if language == "ar" else "🔄 <b>A/B Tests</b>\n\n"

            if tests:
                for test in tests:
                    status = "✅ نشط" if test["status"] == "active" else "✅ منتهي"
                    text += (
                        f"📝 {test['quiz_a_title']} vs {test['quiz_b_title']}\n"
                        f"📢 {test['channel_title']}\n"
                        f"📊 الحالة: {status}\n\n"
                    )
            else:
                text += "لا توجد اختبارات A/B حالياً.\n" if language == "ar" else "No A/B tests currently.\n"

            keyboard = [
                [
                    InlineKeyboardButton(
                        "➕ إنشاء اختبار A/B"
                        if language == "ar"
                        else "➕ Create A/B Test",
                        callback_data="ab_create",
                    )
                ],
                [
                    InlineKeyboardButton(
                        get_text("back", language),
                        callback_data="main_menu",
                    )
                ],
            ]

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
            )

        elif action == "create":
            await query.edit_message_text(
                "🔄 <b>لإنشاء اختبار A/B:</b>\n\n"
                "1. أنشئ نسختين مختلفتين من الاختبار\n"
                "2. سيتم نشر كل نسخة وقياس التفاعل\n\n"
                "هذه الميزة قيد التطوير!"
                if language == "ar"
                else "🔄 <b>To create A/B test:</b>\n\n"
                "1. Create two versions of a quiz\n"
                "2. Each will be published and engagement measured\n\n"
                "This feature is under development!",
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )