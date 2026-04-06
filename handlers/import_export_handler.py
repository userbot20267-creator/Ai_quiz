import logging
import json
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard
from utils.helpers import quiz_to_json, json_to_quiz

logger = logging.getLogger(__name__)


class ImportExportHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def export_quizzes(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quizzes = await db.get_user_quizzes(user.id)

        if not quizzes:
            await update.message.reply_text(
                get_text("no_quizzes", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return

        export_data = []
        for quiz in quizzes:
            questions = await db.get_quiz_questions(quiz["quiz_id"])
            quiz_json = quiz_to_json(quiz, questions)
            export_data.append(json.loads(quiz_json))

        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

        from io import BytesIO

        file = BytesIO(json_str.encode("utf-8"))
        file.name = "quizzes_export.json"

        await update.message.reply_document(
            document=file,
            caption=get_text("export_success", language),
        )

    async def start_import(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["waiting_import"] = True

        await update.message.reply_text(
            get_text("import_prompt", language),
            reply_markup=back_to_menu_keyboard(language),
            parse_mode=ParseMode.HTML,
        )

    async def receive_import_file(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not context.user_data.get("waiting_import"):
            return

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        try:
            document = update.message.document
            file = await context.bot.get_file(document.file_id)
            file_bytes = await file.download_as_bytearray()
            content = file_bytes.decode("utf-8")

            data = json.loads(content)

            if not isinstance(data, list):
                data = [data]

            count = 0
            for quiz_data in data:
                quiz_id = await db.create_quiz(
                    user.id,
                    quiz_data.get("title", "Imported Quiz"),
                    quiz_data.get("description", ""),
                    quiz_data.get("category", "general"),
                )

                for i, q in enumerate(quiz_data.get("questions", [])):
                    await db.add_question(
                        quiz_id=quiz_id,
                        question_text=q.get("text", q.get("question", "")),
                        question_type=q.get("type", "multiple_choice"),
                        option_a=q.get("option_a", ""),
                        option_b=q.get("option_b", ""),
                        correct_answer=q.get("correct", "a"),
                        option_c=q.get("option_c"),
                        option_d=q.get("option_d"),
                        explanation=q.get("explanation"),
                        order_num=i,
                    )
                count += 1

            context.user_data.pop("waiting_import", None)

            await update.message.reply_text(
                get_text("import_success", language).format(count=count),
                reply_markup=back_to_menu_keyboard(language),
            )

        except Exception as e:
            logger.error(f"Import error: {e}")
            await update.message.reply_text(
                get_text("import_failed", language),
                reply_markup=back_to_menu_keyboard(language),
            )

    async def import_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["waiting_import"] = True
        await query.edit_message_text(
            get_text("import_prompt", language),
            parse_mode=ParseMode.HTML,
        )