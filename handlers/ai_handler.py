import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import config
from locales import get_text
from keyboards.main_keyboards import back_to_menu_keyboard
from keyboards.quiz_keyboards import quiz_actions_keyboard
from services.ai_service import AIService
from utils.decorators import check_ban

logger = logging.getLogger(__name__)


class AIHandler:
    def __init__(self):
        self.ai_service = AIService()

    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def _check_ai_limit(self, user_id, context):
        """التحقق من حد استخدام AI"""
        db = context.bot_data.get("db")
        if db:
            return await db.check_ai_limit(user_id, config.MAX_AI_REQUESTS_PER_USER)
        return True

    @check_ban
    async def ai_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        # حالة الاتصال
        ai_status = "✅ متصل" if self.ai_service.is_configured else "❌ غير متصل"
        model_name = config.OPENROUTER_MODEL if self.ai_service.is_configured else "غير محدد"

        header = (
            f"🤖 <b>أدوات الذكاء الاصطناعي</b>\n\n"
            f"📡 الحالة: {ai_status}\n"
            f"🧠 النموذج: <code>{model_name}</code>\n"
            f"─────────────────────"
        ) if language == "ar" else (
            f"🤖 <b>AI Tools</b>\n\n"
            f"📡 Status: {ai_status}\n"
            f"🧠 Model: <code>{model_name}</code>\n"
            f"─────────────────────"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎯 توليد أسئلة اختيار" if language == "ar" else "🎯 Generate MCQ",
                    callback_data="ai_generate_mcq",
                ),
            ],
            [
                InlineKeyboardButton(
                    "✅❌ توليد صح/خطأ" if language == "ar" else "✅❌ Generate T/F",
                    callback_data="ai_generate_tf",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📄 استخراج من نص" if language == "ar" else "📄 From Text",
                    callback_data="ai_from_text",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔗 استخراج من رابط" if language == "ar" else "🔗 From URL",
                    callback_data="ai_from_url",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📝 إعادة صياغة" if language == "ar" else "📝 Rephrase",
                    callback_data="ai_rephrase",
                ),
            ],
            [
                InlineKeyboardButton(
                    "✨ تحسين المحتوى" if language == "ar" else "✨ Improve",
                    callback_data="ai_improve",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🤖 اختبار تلقائي كامل" if language == "ar" else "🤖 Full Auto Quiz",
                    callback_data="ai_auto_quiz",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ],
        ]

        await query.edit_message_text(
            header,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )

    async def ai_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)
        action = query.data.replace("ai_", "")

        # التحقق من الحد
        can_use = await self._check_ai_limit(user.id, context)
        if not can_use:
            await query.edit_message_text(
                get_text("ai_limit_reached", language).format(
                    limit=config.MAX_AI_REQUESTS_PER_USER
                ),
                reply_markup=back_to_menu_keyboard(language),
            )
            return

        if action == "generate_mcq":
            context.user_data["ai_action"] = "generate_mcq"
            text = (
                "🎯 <b>توليد أسئلة اختيار من متعدد</b>\n\n"
                "أرسل الموضوع بالصيغة التالية:\n"
                "<code>الموضوع | عدد الأسئلة | الصعوبة</code>\n\n"
                "أمثلة:\n"
                "• <code>الفيزياء</code> (5 أسئلة متوسطة)\n"
                "• <code>الرياضيات | 10</code> (10 أسئلة متوسطة)\n"
                "• <code>English Grammar | 7 | hard</code>\n\n"
                "الصعوبة: easy / medium / hard"
            ) if language == "ar" else (
                "🎯 <b>Generate Multiple Choice Questions</b>\n\n"
                "Send the topic in this format:\n"
                "<code>topic | number | difficulty</code>\n\n"
                "Examples:\n"
                "• <code>Physics</code> (5 medium questions)\n"
                "• <code>Math | 10</code>\n"
                "• <code>English Grammar | 7 | hard</code>\n\n"
                "Difficulty: easy / medium / hard"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "generate_tf":
            context.user_data["ai_action"] = "generate_tf"
            text = (
                "✅❌ <b>توليد أسئلة صح / خطأ</b>\n\n"
                "أرسل الموضوع:\n"
                "<code>الموضوع | عدد الأسئلة</code>\n\n"
                "مثال: <code>التاريخ الإسلامي | 8</code>"
            ) if language == "ar" else (
                "✅❌ <b>Generate True/False Questions</b>\n\n"
                "Send the topic:\n"
                "<code>topic | number</code>\n\n"
                "Example: <code>World History | 8</code>"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "from_text":
            context.user_data["ai_action"] = "from_text"
            text = (
                "📄 <b>استخراج أسئلة من نص</b>\n\n"
                "أرسل النص الذي تريد استخراج الأسئلة منه.\n"
                "يمكن أن يكون فقرة، مقال، درس، إلخ.\n\n"
                "سيتم إنشاء 5 أسئلة تلقائياً."
            ) if language == "ar" else (
                "📄 <b>Extract Questions from Text</b>\n\n"
                "Send the text to extract questions from.\n"
                "Can be a paragraph, article, lesson, etc.\n\n"
                "5 questions will be generated automatically."
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "from_url":
            context.user_data["ai_action"] = "from_url"
            text = (
                "🔗 <b>استخراج أسئلة من رابط</b>\n\n"
                "أرسل رابط الصفحة:\n"
                "<code>https://example.com/article</code>"
            ) if language == "ar" else (
                "🔗 <b>Extract Questions from URL</b>\n\n"
                "Send the page URL:\n"
                "<code>https://example.com/article</code>"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "rephrase":
            context.user_data["ai_action"] = "rephrase"
            text = (
                "📝 <b>إعادة صياغة سؤال</b>\n\n"
                "أرسل السؤال الذي تريد إعادة صياغته:"
            ) if language == "ar" else (
                "📝 <b>Rephrase Question</b>\n\n"
                "Send the question to rephrase:"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "improve":
            context.user_data["ai_action"] = "improve"
            text = (
                "✨ <b>تحسين المحتوى</b>\n\n"
                "أرسل المحتوى الذي تريد تحسينه:"
            ) if language == "ar" else (
                "✨ <b>Improve Content</b>\n\n"
                "Send the content to improve:"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "auto_quiz":
            context.user_data["ai_action"] = "auto_quiz"
            text = (
                "🤖 <b>إنشاء اختبار تلقائي كامل</b>\n\n"
                "أرسل الموضوع وعدد الأسئلة:\n"
                "<code>الموضوع | عدد الأسئلة</code>\n\n"
                "مثال: <code>البرمجة بلغة Python | 15</code>\n\n"
                "سيتم إنشاء اختبار كامل وحفظه تلقائياً!"
            ) if language == "ar" else (
                "🤖 <b>Auto Generate Full Quiz</b>\n\n"
                "Send topic and number:\n"
                "<code>topic | number</code>\n\n"
                "Example: <code>Python Programming | 15</code>\n\n"
                "A complete quiz will be created and saved!"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

    @check_ban
    async def generate_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """أمر /generate"""
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        if not context.args:
            await update.message.reply_text(
                get_text("ai_generate_prompt", language),
                parse_mode=ParseMode.HTML,
            )
            context.user_data["ai_action"] = "generate_mcq"
            return

        # التحقق من الحد
        can_use = await self._check_ai_limit(user.id, context)
        if not can_use:
            await update.message.reply_text(
                get_text("ai_limit_reached", language).format(
                    limit=config.MAX_AI_REQUESTS_PER_USER
                )
            )
            return

        input_text = " ".join(context.args)
        topic, num_questions, difficulty = self._parse_generate_input(input_text)

        msg = await update.message.reply_text(
            get_text("ai_generating", language)
        )

        questions = await self.ai_service.generate_questions(
            topic, num_questions, difficulty, language
        )

        await db.increment_ai_requests(user.id)

        quiz_id = await self._save_generated_quiz(
            db, user.id, topic, questions, language
        )

        await msg.edit_text(
            self._format_generation_result(topic, questions, quiz_id, language),
            reply_markup=quiz_actions_keyboard(quiz_id, language),
            parse_mode=ParseMode.HTML,
        )

    async def handle_ai_text_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة النصوص المرسلة لأوامر AI"""
        ai_action = context.user_data.get("ai_action")
        if not ai_action:
            return False  # ليس طلب AI

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)
        input_text = update.message.text.strip()

        # مسح الحالة
        context.user_data.pop("ai_action", None)

        # التحقق من الحد
        can_use = await self._check_ai_limit(user.id, context)
        if not can_use:
            await update.message.reply_text(
                get_text("ai_limit_reached", language).format(
                    limit=config.MAX_AI_REQUESTS_PER_USER
                )
            )
            return True

        msg = await update.message.reply_text(
            get_text("ai_generating", language)
        )

        try:
            if ai_action == "generate_mcq":
                topic, num_q, difficulty = self._parse_generate_input(input_text)
                questions = await self.ai_service.generate_questions(
                    topic, num_q, difficulty, language
                )
                await db.increment_ai_requests(user.id)
                quiz_id = await self._save_generated_quiz(
                    db, user.id, topic, questions, language
                )
                await msg.edit_text(
                    self._format_generation_result(topic, questions, quiz_id, language),
                    reply_markup=quiz_actions_keyboard(quiz_id, language),
                    parse_mode=ParseMode.HTML,
                )

            elif ai_action == "generate_tf":
                topic, num_q, _ = self._parse_generate_input(input_text)
                questions = await self.ai_service.generate_true_false_questions(
                    topic, num_q, language
                )
                await db.increment_ai_requests(user.id)
                quiz_id = await self._save_generated_quiz(
                    db, user.id, topic, questions, language
                )
                await msg.edit_text(
                    self._format_generation_result(topic, questions, quiz_id, language),
                    reply_markup=quiz_actions_keyboard(quiz_id, language),
                    parse_mode=ParseMode.HTML,
                )

            elif ai_action == "from_text":
                questions = await self.ai_service.extract_from_text(
                    input_text, 5, language
                )
                await db.increment_ai_requests(user.id)
                quiz_id = await self._save_generated_quiz(
                    db, user.id, "Text Extract", questions, language
                )
                await msg.edit_text(
                    self._format_generation_result("Text", questions, quiz_id, language),
                    reply_markup=quiz_actions_keyboard(quiz_id, language),
                    parse_mode=ParseMode.HTML,
                )

            elif ai_action == "from_url":
                questions = await self.ai_service.extract_from_url(
                    input_text, 5, language
                )
                await db.increment_ai_requests(user.id)
                quiz_id = await self._save_generated_quiz(
                    db, user.id, "URL Extract", questions, language
                )
                await msg.edit_text(
                    self._format_generation_result("URL", questions, quiz_id, language),
                    reply_markup=quiz_actions_keyboard(quiz_id, language),
                    parse_mode=ParseMode.HTML,
                )

            elif ai_action == "rephrase":
                result = await self.ai_service.rephrase_question(
                    input_text, language
                )
                await db.increment_ai_requests(user.id)
                text = (
                    f"📝 <b>إعادة الصياغة</b>\n\n"
                    f"<b>الأصلي:</b>\n{input_text}\n\n"
                    f"<b>المعاد صياغته:</b>\n{result}"
                ) if language == "ar" else (
                    f"📝 <b>Rephrased</b>\n\n"
                    f"<b>Original:</b>\n{input_text}\n\n"
                    f"<b>Rephrased:</b>\n{result}"
                )
                await msg.edit_text(
                    text,
                    reply_markup=back_to_menu_keyboard(language),
                    parse_mode=ParseMode.HTML,
                )

            elif ai_action == "improve":
                result = await self.ai_service.improve_content(
                    input_text, language
                )
                await db.increment_ai_requests(user.id)
                text = (
                    f"✨ <b>المحتوى المحسّن</b>\n\n{result}"
                ) if language == "ar" else (
                    f"✨ <b>Improved Content</b>\n\n{result}"
                )
                await msg.edit_text(
                    text,
                    reply_markup=back_to_menu_keyboard(language),
                    parse_mode=ParseMode.HTML,
                )

            elif ai_action == "auto_quiz":
                topic, num_q, _ = self._parse_generate_input(input_text)
                quiz_data = await self.ai_service.auto_generate_quiz(
                    topic, num_q, "medium", language
                )
                await db.increment_ai_requests(user.id)
                quiz_id = await self._save_generated_quiz(
                    db,
                    user.id,
                    quiz_data["title"],
                    quiz_data["questions"],
                    language,
                    quiz_data.get("description", ""),
                )
                await msg.edit_text(
                    self._format_generation_result(
                        topic, quiz_data["questions"], quiz_id, language
                    ),
                    reply_markup=quiz_actions_keyboard(quiz_id, language),
                    parse_mode=ParseMode.HTML,
                )

        except Exception as e:
            logger.error(f"AI handler error: {e}")
            await msg.edit_text(
                get_text("error_occurred", language),
                reply_markup=back_to_menu_keyboard(language),
            )

        return True

    def _parse_generate_input(self, text):
        """تحليل المدخلات: الموضوع | عدد | صعوبة"""
        parts = [p.strip() for p in text.split("|")]

        topic = parts[0] if parts else "General"

        num_questions = 5
        if len(parts) > 1:
            try:
                num_questions = int(parts[1])
                num_questions = max(1, min(num_questions, 30))
            except ValueError:
                pass

        difficulty = "medium"
        if len(parts) > 2:
            d = parts[2].lower().strip()
            if d in ("easy", "medium", "hard", "سهل", "متوسط", "صعب"):
                difficulty_map = {"سهل": "easy", "متوسط": "medium", "صعب": "hard"}
                difficulty = difficulty_map.get(d, d)

        return topic, num_questions, difficulty

    async def _save_generated_quiz(
        self, db, user_id, topic, questions, language, description=""
    ):
        """حفظ الاختبار المولّد"""
        title = topic if len(topic) <= 50 else topic[:47] + "..."

        if not description:
            description = (
                f"اختبار تم إنشاؤه بالذكاء الاصطناعي عن: {topic}"
                if language == "ar"
                else f"AI-generated quiz about: {topic}"
            )

        quiz_id = await db.create_quiz(
            user_id, title, description, "general"
        )

        for i, q in enumerate(questions):
            correct = q.get("correct", "a").lower()
            if correct not in ("a", "b", "c", "d"):
                correct = "a"

            await db.add_question(
                quiz_id=quiz_id,
                question_text=q.get("question", ""),
                question_type=q.get("type", "multiple_choice"),
                option_a=q.get("option_a", ""),
                option_b=q.get("option_b", ""),
                correct_answer=correct,
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                explanation=q.get("explanation"),
                order_num=i,
            )

        return quiz_id

    
    def _format_generation_result(self, topic, questions, quiz_id, language):
        """تنسيق نتيجة التوليد"""
        if language == "ar":
            text = (
                f"✅ <b>تم إنشاء الاختبار بنجاح!</b>\n\n"
                f"🤖 النموذج: <code>{config.OPENROUTER_MODEL}</code>\n"
                f"📝 الموضوع: {topic}\n"
                f"❓ عدد الأسئلة: {len(questions)}\n"
                f"🆔 رقم الاختبار: {quiz_id}\n\n"
                f"<b>معاينة الأسئلة:</b>\n"
            )
        else:
            text = (
                f"✅ <b>Quiz Generated Successfully!</b>\n\n"
                f"🤖 Model: <code>{config.OPENROUTER_MODEL}</code>\n"
                f"📝 Topic: {topic}\n"
                f"❓ Questions: {len(questions)}\n"
                f"🆔 Quiz ID: {quiz_id}\n\n"
                f"<b>Question Preview:</b>\n"
            )

        for i, q in enumerate(questions[:5]):
            q_text = q.get("question", "")
            if len(q_text) > 80:
                q_text = q_text[:77] + "..."
            text += f"  {i + 1}. {q_text}\n"

        if len(questions) > 5:
            remaining = len(questions) - 5
            text += (
                f"\n  ... و {remaining} أسئلة أخرى"
                if language == "ar"
                else f"\n  ... and {remaining} more questions"
            )

        return text