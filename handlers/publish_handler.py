import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from locales import get_text
from keyboards.quiz_keyboards import quiz_list_keyboard
from keyboards.inline_keyboards import publish_channel_keyboard
from keyboards.main_keyboards import (
    confirm_cancel_keyboard,
    back_to_menu_keyboard,
)
from services.publish_service import PublishService

logger = logging.getLogger(__name__)


class PublishHandler:
    SELECT_QUIZ = 1
    SELECT_CHANNEL = 2
    CONFIRM_PUBLISH = 3

    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def start_publish_menu(
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
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        for quiz in quizzes[:20]:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📝 {quiz['title']}",
                        callback_data=f"pub_quiz_{quiz['quiz_id']}",
                    )
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    get_text("cancel", language),
                    callback_data="cancel_pub",
                )
            ]
        )

        await query.edit_message_text(
            get_text("select_quiz_to_publish", language),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )
        return self.SELECT_QUIZ

    async def start_publish(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("publish_quiz_", ""))
        context.user_data["publish_quiz_id"] = quiz_id

        channels = await db.get_user_channels(user.id)

        if not channels:
            await query.edit_message_text(
                get_text("no_channels", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return ConversationHandler.END

        await query.edit_message_text(
            get_text("select_channel", language),
            reply_markup=publish_channel_keyboard(channels, language),
            parse_mode=ParseMode.HTML,
        )
        return self.SELECT_CHANNEL

    async def select_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("pub_quiz_", ""))
        context.user_data["publish_quiz_id"] = quiz_id

        channels = await db.get_user_channels(user.id)

        if not channels:
            await query.edit_message_text(
                get_text("no_channels", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return ConversationHandler.END

        await query.edit_message_text(
            get_text("select_channel", language),
            reply_markup=publish_channel_keyboard(channels, language),
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

        channel_id = int(query.data.replace("pub_ch_", ""))
        context.user_data["publish_channel_id"] = channel_id

        await query.edit_message_text(
            "📤 <b>تأكيد النشر</b>\n\nهل تريد نشر الاختبار؟",
            reply_markup=confirm_cancel_keyboard(
                "confirm_pub", "cancel_pub", language
            ),
            parse_mode=ParseMode.HTML,
        )
        return self.CONFIRM_PUBLISH

    async def select_all_channels(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["publish_all_channels"] = True

        await query.edit_message_text(
            "📤 <b>تأكيد النشر في جميع القنوات</b>\n\nهل تريد المتابعة؟",
            reply_markup=confirm_cancel_keyboard(
                "confirm_pub", "cancel_pub", language
            ),
            parse_mode=ParseMode.HTML,
        )
        return self.CONFIRM_PUBLISH

    async def confirm_publish(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = context.user_data.get("publish_quiz_id")
        publish_service = PublishService(context.application)

        if context.user_data.get("publish_all_channels"):
            channels = await db.get_user_channels(user.id)
            channel_ids = [ch["channel_id"] for ch in channels]
            results = await publish_service.publish_to_multiple_channels(
                quiz_id, channel_ids
            )

            success_count = sum(
                1 for r in results.values() if r["success"]
            )
            failed_count = len(results) - success_count

            await query.edit_message_text(
                f"📤 <b>نتائج النشر:</b>\n\n✅ نجح: {success_count}\n❌ فشل: {failed_count}",
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )
        else:
            channel_id = context.user_data.get("publish_channel_id")
            success, error = await publish_service.publish_quiz(
                quiz_id, channel_id
            )

            if success:
                channel = await db.get_channel(channel_id)
                channel_title = channel["title"] if channel else "Unknown"
                await query.edit_message_text(
                    get_text("publish_success", language).format(
                        channel=channel_title
                    ),
                    reply_markup=back_to_menu_keyboard(language),
                    parse_mode=ParseMode.HTML,
                )
            else:
                await query.edit_message_text(
                    get_text("publish_failed", language).format(error=error),
                    reply_markup=back_to_menu_keyboard(language),
                    parse_mode=ParseMode.HTML,
                )

        context.user_data.pop("publish_quiz_id", None)
        context.user_data.pop("publish_channel_id", None)
        context.user_data.pop("publish_all_channels", None)

        return ConversationHandler.END

    async def cancel_publish(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if update.callback_query:
            await update.callback_query.answer()
            user = update.effective_user
            language = await self._get_language(user.id, context)
            await update.callback_query.edit_message_text(
                get_text("cancelled", language),
                reply_markup=back_to_menu_keyboard(language),
            )
        else:
            user = update.effective_user
            language = await self._get_language(user.id, context)
            await update.message.reply_text(
                get_text("cancelled", language),
                reply_markup=back_to_menu_keyboard(language),
            )

        context.user_data.pop("publish_quiz_id", None)
        context.user_data.pop("publish_channel_id", None)
        context.user_data.pop("publish_all_channels", None)

        return ConversationHandler.END