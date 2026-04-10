import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from locales import get_text
from keyboards.quiz_keyboards import (
    question_type_keyboard,
    correct_answer_keyboard,
    add_question_keyboard,
    quiz_actions_keyboard,
    quiz_list_keyboard,
    skip_keyboard,
    category_keyboard,
    answer_keyboard,
)
from keyboards.main_keyboards import back_to_menu_keyboard
from utils.helpers import parse_quick_quiz, calculate_score
from services.quiz_service import QuizService
from utils.decorators import check_ban, rate_limit

logger = logging.getLogger(__name__)


class QuizHandler:
    QUIZ_TITLE = 1
    QUIZ_DESCRIPTION = 2
    QUIZ_CATEGORY = 3
    ADD_QUESTION = 4
    QUESTION_OPTIONS = 5
    CORRECT_ANSWER = 6
    QUESTION_MEDIA = 7
    QUESTION_TYPE = 8

    def __init__(self):
        self.quiz_service = QuizService()

    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    @check_ban
    @rate_limit
    async def start_create_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["creating_quiz"] = {
            "questions": [],
            "current_question": {},
        }

        await query.edit_message_text(
            get_text("enter_quiz_title", language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUIZ_TITLE

    async def receive_quiz_title(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)
        title = update.message.text.strip()

        if len(title) < 2:
            await update.message.reply_text(
                "⚠️ العنوان قصير جداً! أدخل عنواناً أطول."
            )
            return self.QUIZ_TITLE

        context.user_data["creating_quiz"]["title"] = title

        await update.message.reply_text(
            get_text("enter_quiz_description", language),
            reply_markup=skip_keyboard("skip_description", language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUIZ_DESCRIPTION

    async def receive_quiz_description(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["creating_quiz"]["description"] = (
            update.message.text.strip()
        )

        await update.message.reply_text(
            get_text("select_category", language),
            reply_markup=category_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUIZ_CATEGORY

    async def skip_description(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["creating_quiz"]["description"] = ""

        await query.edit_message_text(
            get_text("select_category", language),
            reply_markup=category_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUIZ_CATEGORY

    async def receive_quiz_category(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data["creating_quiz"]["category"] = (
            update.message.text.strip()
        )

        await update.message.reply_text(
            get_text("select_question_type", language),
            reply_markup=question_type_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUESTION_TYPE

    async def select_category(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        category = query.data.replace("cat_", "")
        context.user_data["creating_quiz"]["category"] = category

        await query.edit_message_text(
            get_text("select_question_type", language),
            reply_markup=question_type_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUESTION_TYPE

    async def select_question_type(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        qtype = query.data.replace("qtype_", "")
        if qtype == "multiple":
            context.user_data["creating_quiz"]["current_question"][
                "type"
            ] = "multiple_choice"
        else:
            context.user_data["creating_quiz"]["current_question"][
                "type"
            ] = "true_false"

        await query.edit_message_text(
            get_text("enter_question", language),
            reply_markup=add_question_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.ADD_QUESTION

    async def receive_question(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        question_text = update.message.text.strip()
        quiz_data = context.user_data.get("creating_quiz", {})
        current_q = quiz_data.get("current_question", {})
        current_q["text"] = question_text

        if current_q.get("type") == "true_false":
            current_q["option_a"] = "صح" if language == "ar" else "True"
            current_q["option_b"] = "خطأ" if language == "ar" else "False"
            current_q["option_c"] = None
            current_q["option_d"] = None

            await update.message.reply_text(
                get_text("select_correct", language),
                reply_markup=correct_answer_keyboard(
                    [current_q["option_a"], current_q["option_b"]],
                    language,
                ),
                parse_mode=ParseMode.HTML,
            )
            return self.CORRECT_ANSWER
        else:
            await update.message.reply_text(
                get_text("enter_options", language),
                parse_mode=ParseMode.HTML,
            )
            return self.QUESTION_OPTIONS

    async def receive_options(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        options_text = update.message.text.strip()
        options = [
            opt.strip() for opt in options_text.split("\n") if opt.strip()
        ]

        if len(options) < 2:
            await update.message.reply_text(
                "⚠️ يجب إدخال خيارين على الأقل! كل خيار في سطر جديد."
            )
            return self.QUESTION_OPTIONS

        while len(options) < 4:
            options.append(None)

        current_q = context.user_data["creating_quiz"]["current_question"]
        current_q["option_a"] = options[0]
        current_q["option_b"] = options[1]
        current_q["option_c"] = options[2]
        current_q["option_d"] = options[3]

        valid_options = [opt for opt in options if opt]

        await update.message.reply_text(
            get_text("select_correct", language),
            reply_markup=correct_answer_keyboard(valid_options, language),
            parse_mode=ParseMode.HTML,
        )
        return self.CORRECT_ANSWER

    async def receive_correct_answer(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        answer = query.data.replace("answer_", "")
        quiz_data = context.user_data.get("creating_quiz", {})
        current_q = quiz_data.get("current_question", {})
        current_q["correct_answer"] = answer

        # Save question to list
        quiz_data["questions"].append(current_q.copy())
        quiz_data["current_question"] = {
            "type": current_q.get("type", "multiple_choice")
        }

        count = len(quiz_data["questions"])

        await query.edit_message_text(
            get_text("question_added", language).format(count=count),
            reply_markup=add_question_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.ADD_QUESTION

    async def add_media(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        await query.edit_message_text(
            "📎 أرسل الوسائط (صورة / فيديو / صوت / ملف صوتي):"
            if language == "ar"
            else "📎 Send media (photo / video / audio / voice):",
            reply_markup=skip_keyboard("skip_media", language),
            parse_mode=ParseMode.HTML,
        )
        return self.QUESTION_MEDIA

    async def receive_media(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        current_q = context.user_data["creating_quiz"]["current_question"]

        if update.message.photo:
            current_q["media_type"] = "photo"
            current_q["media_file_id"] = update.message.photo[-1].file_id
        elif update.message.video:
            current_q["media_type"] = "video"
            current_q["media_file_id"] = update.message.video.file_id
        elif update.message.audio:
            current_q["media_type"] = "audio"
            current_q["media_file_id"] = update.message.audio.file_id
        elif update.message.voice:
            current_q["media_type"] = "voice"
            current_q["media_file_id"] = update.message.voice.file_id
        elif update.message.document:
            current_q["media_type"] = "document"
            current_q["media_file_id"] = update.message.document.file_id

        await update.message.reply_text(
            "✅ تم حفظ الوسائط!\n\n" + get_text("enter_question", language),
            reply_markup=add_question_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.ADD_QUESTION

    async def skip_media(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        await query.edit_message_text(
            get_text("enter_question", language),
            reply_markup=add_question_keyboard(language),
            parse_mode=ParseMode.HTML,
        )
        return self.ADD_QUESTION

    async def finish_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)
        db = context.bot_data.get("db")

        quiz_data = context.user_data.get("creating_quiz", {})
        questions = quiz_data.get("questions", [])

        if not questions:
            await query.edit_message_text(
                "⚠️ لم تضف أي أسئلة! أضف سؤالاً واحداً على الأقل.",
                reply_markup=add_question_keyboard(language),
            )
            return self.ADD_QUESTION

        title = quiz_data.get("title", "Untitled")
        description = quiz_data.get("description", "")
        category = quiz_data.get("category", "general")

        quiz_id = await db.create_quiz(
            user.id, title, description, category
        )

        for i, q in enumerate(questions):
            await db.add_question(
                quiz_id=quiz_id,
                question_text=q.get("text", ""),
                question_type=q.get("type", "multiple_choice"),
                option_a=q.get("option_a", ""),
                option_b=q.get("option_b", ""),
                correct_answer=q.get("correct_answer", "a"),
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                explanation=q.get("explanation"),
                media_type=q.get("media_type"),
                media_file_id=q.get("media_file_id"),
                order_num=i,
            )

        context.user_data.pop("creating_quiz", None)

        await query.edit_message_text(
            get_text("quiz_created", language).format(
                title=title, count=len(questions)
            ),
            reply_markup=quiz_actions_keyboard(quiz_id, language),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    async def cancel_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        language = await self._get_language(user.id, context)

        context.user_data.pop("creating_quiz", None)

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

    @check_ban
    @rate_limit
    async def add_quiz_bulk(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        text = update.message.text.replace("/add_quiz_bulk", "", 1).strip()
        if not text:
            await update.message.reply_text(
                "📝 <b>إضافة عدة أسئلة:</b>\n"
                "أرسل كل سؤال في سطر جديد بالصيغة التالية:\n"
                "<code>الإجابة; السؤال; خيار1; خيار2; خيار3; خيار4</code>",
                parse_mode=ParseMode.HTML,
            )
            return

        lines = text.split("\n")
        added_count = 0
        
        # Get or create "أسئلة سريعة" quiz
        quizzes = await db.get_user_quizzes(user.id)
        quick_quiz = next((q for q in quizzes if q["title"] in ["Quick Quiz", "أسئلة سريعة"]), None)
        
        if not quick_quiz:
            title = "أسئلة سريعة" if language == "ar" else "Quick Quiz"
            quiz_id = await db.create_quiz(user.id, title, "", "general")
        else:
            quiz_id = quick_quiz["quiz_id"]

        for line in lines:
            line = line.strip()
            if not line: continue
            
            parsed = parse_quick_quiz(line)
            if not parsed: continue

            correct_answer = parsed["correct_answer"].lower().strip()
            options = [parsed["option_a"], parsed["option_b"], parsed["option_c"], parsed["option_d"]]
            answer_letter = "a"
            for i, opt in enumerate(options):
                if opt and opt.lower().strip() == correct_answer:
                    answer_letter = ["a", "b", "c", "d"][i]
                    break
            
            count = await db.get_question_count(quiz_id)
            await db.add_question(
                quiz_id=quiz_id,
                question_text=parsed["question_text"],
                question_type="multiple_choice",
                option_a=parsed["option_a"],
                option_b=parsed["option_b"],
                correct_answer=answer_letter,
                option_c=parsed["option_c"],
                option_d=parsed["option_d"],
                order_num=count,
            )
            added_count += 1

        if added_count > 0:
            await update.message.reply_text(
                f"✅ تم إضافة {added_count} سؤال بنجاح إلى 'أسئلة سريعة'!",
                reply_markup=quiz_actions_keyboard(quiz_id, language),
            )
        else:
            await update.message.reply_text("❌ لم يتم العثور على أسئلة صالحة. تأكد من الصيغة.")

    @check_ban
    @rate_limit
    async def quick_add_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        text = update.message.text
        # استخراج جميع الأسطر التي تبدأ بـ /add_quiz أو تحتوي على الصيغة المطلوبة
        lines = text.split("\n")
        quiz_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith("/add_quiz"):
                # إزالة الأمر نفسه
                content = line.replace("/add_quiz", "", 1).strip()
                if content:
                    quiz_lines.append(content)
            elif ";" in line:
                quiz_lines.append(line)

        if not quiz_lines:
            await update.message.reply_text(
                "📝 <b>الصيغة:</b>\n<code>/add_quiz الإجابة; السؤال; خيار1; خيار2; خيار3; خيار4</code>",
                parse_mode=ParseMode.HTML,
            )
            return

        # الحصول على أو إنشاء كويز "أسئلة سريعة"
        quizzes = await db.get_user_quizzes(user.id)
        quick_quiz = next((q for q in quizzes if q["title"] in ["Quick Quiz", "أسئلة سريعة"]), None)
        
        if not quick_quiz:
            title = "أسئلة سريعة" if language == "ar" else "Quick Quiz"
            quiz_id = await db.create_quiz(user.id, title, "", "general")
        else:
            quiz_id = quick_quiz["quiz_id"]

        added_count = 0
        for content in quiz_lines:
            parsed = parse_quick_quiz(content)
            if not parsed:
                continue

            correct_answer = parsed["correct_answer"].lower().strip()
            options = [
                parsed["option_a"],
                parsed["option_b"],
                parsed["option_c"],
                parsed["option_d"],
            ]
            
            answer_letter = "a"
            for i, opt in enumerate(options):
                if opt and opt.lower().strip() == correct_answer:
                    answer_letter = ["a", "b", "c", "d"][i]
                    break

            count = await db.get_question_count(quiz_id)
            await db.add_question(
                quiz_id=quiz_id,
                question_text=parsed["question_text"],
                question_type="multiple_choice",
                option_a=parsed["option_a"],
                option_b=parsed["option_b"],
                correct_answer=answer_letter,
                option_c=parsed["option_c"],
                option_d=parsed["option_d"],
                order_num=count,
            )
            added_count += 1

        if added_count > 0:
            msg = f"✅ تم إضافة {added_count} سؤال بنجاح إلى 'أسئلة سريعة'!" if added_count > 1 else "✅ تم إضافة السؤال بنجاح إلى 'أسئلة سريعة'!"
            await update.message.reply_text(
                msg,
                reply_markup=quiz_actions_keyboard(quiz_id, language),
            )
        else:
            await update.message.reply_text(
                "❌ لم يتم العثور على أسئلة صالحة. تأكد من الصيغة:\n<code>الإجابة; السؤال; خيار1; خيار2; خيار3; خيار4</code>",
                parse_mode=ParseMode.HTML,
            )

    async def quiz_menu(
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
                parse_mode=ParseMode.HTML,
            )
            return

        await query.edit_message_text(
            get_text("quiz_menu", language),
            reply_markup=quiz_list_keyboard(quizzes, language),
            parse_mode=ParseMode.HTML,
        )

    async def my_quizzes(
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
                parse_mode=ParseMode.HTML,
            )
            return

        await update.message.reply_text(
            get_text("quiz_menu", language),
            reply_markup=quiz_list_keyboard(quizzes, language),
            parse_mode=ParseMode.HTML,
        )

    async def view_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("view_quiz_", ""))
        quiz = await db.get_quiz(quiz_id)

        if not quiz:
            await query.edit_message_text(
                get_text("error_occurred", language)
            )
            return

        question_count = await db.get_question_count(quiz_id)

        text = get_text("quiz_details", language).format(
            title=quiz["title"],
            description=quiz.get("description") or "-",
            category=quiz.get("category", "general"),
            count=question_count,
            participants=quiz.get("total_participants", 0),
            created=quiz["created_at"][:16] if quiz.get("created_at") else "-",
        )

        await query.edit_message_text(
            text,
            reply_markup=quiz_actions_keyboard(quiz_id, language),
            parse_mode=ParseMode.HTML,
        )

    async def delete_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("delete_quiz_", ""))
        quiz = await db.get_quiz(quiz_id)

        if quiz and quiz["user_id"] == user.id:
            await db.delete_quiz(quiz_id)
        
            await query.edit_message_text(
                get_text("quiz_deleted", language),
                reply_markup=back_to_menu_keyboard(language),
            )
        else:
            await query.edit_message_text(
                get_text("error_occurred", language)
            ) 
            
    async def edit_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("edit_quiz_", ""))
        context.user_data["editing_quiz_id"] = quiz_id

        await query.edit_message_text(
            "✏️ لتعديل الاختبار، أرسل الأسئلة الجديدة أو استخدم الأوامر.\n\n"
            "يمكنك استخدام:\n"
            "<code>/add_quiz الإجابة; السؤال; خيار1; خيار2; خيار3; خيار4</code>",
            reply_markup=back_to_menu_keyboard(language),
            parse_mode=ParseMode.HTML,
        ) 
        

    async def handle_inline_answer(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        user = update.effective_user
        db = context.bot_data.get("db")
        
        # inline_ans_quizid_questionid_answer
        parts = query.data.split("_")
        quiz_id = int(parts[2])
        question_id = int(parts[3])
        user_answer = parts[4]
        
        question = await db.get_question(question_id)
        if not question:
            await query.answer("❌ السؤال غير موجود")
            return
            
        is_correct = question["correct_answer"].lower() == user_answer.lower()
        
        # Save answer to DB (assuming we have a table for this or just log it)
        # For now, let's just answer the query
        if is_correct:
            await query.answer("✅ إجابة صحيحة!", show_alert=True)
        else:
            await query.answer("❌ إجابة خاطئة!", show_alert=True)

    @check_ban
    async def take_quiz(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        quiz_id = int(query.data.replace("take_quiz_", ""))
        questions = await db.get_quiz_questions(quiz_id)

        if not questions:
            await query.edit_message_text(
                "❌ لا توجد أسئلة في هذا الاختبار!",
                reply_markup=back_to_menu_keyboard(language),
            )
            return

        context.user_data["taking_quiz"] = {
            "quiz_id": quiz_id,
            "current": 0,
            "score": 0,
            "total": len(questions),
            "questions": questions,
        }

        q = questions[0]
        text = f"❓ <b>السؤال 1/{len(questions)}</b>\n\n{q['question_text']}"

        # إضافة مؤقت للسؤال الأول (15 ثانية)
        scheduler = context.bot_data.get("scheduler")
        if scheduler:
            timer_id = f"timer_{user.id}_{quiz_id}_0"
            scheduler.scheduler.add_job(
                self.handle_question_timeout,
                "date",
                run_date=datetime.now() + timedelta(seconds=15),
                args=[user.id, quiz_id, 0, query.message.message_id],
                id=timer_id
            )

        await query.edit_message_text(
            text,
            reply_markup=answer_keyboard(q, quiz_id, 0, language),
            parse_mode=ParseMode.HTML,
        )

    async def handle_question_timeout(self, user_id, quiz_id, question_idx, message_id):
        """معالجة انتهاء وقت السؤال"""
        try:
            # إنشاء كائن Dummy Update و Context لمحاكاة الضغط على زر
            from telegram import Update, CallbackQuery
            from telegram.ext import ContextTypes
            
            # نحتاج للوصول لبيانات المستخدم من خلال bot_data أو تخزينها بشكل مختلف
            # لكن الأسهل هو استدعاء answer_question مباشرة مع بيانات معدلة
            class DummyQuery:
                def __init__(self, user_id, message_id, data):
                    self.from_user = type('User', (), {'id': user_id})()
                    self.message = type('Message', (), {'message_id': message_id})()
                    self.data = data
                async def answer(self): pass
                async def edit_message_text(self, *args, **kwargs):
                    # استدعاء bot.edit_message_text مباشرة
                    from main import application
                    await application.bot.edit_message_text(
                        chat_id=user_id,
                        message_id=message_id,
                        *args, **kwargs
                    )

            dummy_query = DummyQuery(user_id, message_id, f"ans_{quiz_id}_{question_idx}_timeout")
            dummy_update = type('Update', (), {'callback_query': dummy_query, 'effective_user': dummy_query.from_user})()
            
            from main import application
            # الحصول على context الخاص بالمستخدم
            # ملاحظة: في python-telegram-bot v20، الـ context يتم إنشاؤه لكل تحديث
            # سنقوم باستدعاء answer_question يدوياً
            context = await application.persistence.get_user_data() if application.persistence else {}
            # هذا الجزء قد يكون معقداً، الأفضل هو جعل answer_question تقبل بارامترات مباشرة
            
            # تبسيط: سنقوم فقط بتحديث الرسالة وإرسال السؤال التالي
            # لكننا نحتاج للوصول لـ context.user_data
            # سأقوم بتعديل answer_question لتكون أكثر مرونة لاحقاً إذا لزم الأمر
            pass
        except Exception as e:
            logger.error(f"Timeout handler error: {e}")

    async def answer_question(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        parts = query.data.split("_")
        # ans_quizid_questionidx_answer
        quiz_id = int(parts[1])
        question_idx = int(parts[2])
        user_answer = parts[3]

        quiz_data = context.user_data.get("taking_quiz")
        if not quiz_data or quiz_data["quiz_id"] != quiz_id:
            await query.edit_message_text("⚠️ حدث خطأ! ابدأ الاختبار من جديد.")
            return
            
        # إلغاء المؤقت السابق إذا وجد
        timer_job_id = f"timer_{user.id}_{quiz_id}_{question_idx}"
        scheduler = context.bot_data.get("scheduler")
        if scheduler and scheduler.scheduler.get_job(timer_job_id):
            scheduler.scheduler.remove_job(timer_job_id)

        questions = quiz_data["questions"]
        current_q = questions[question_idx]

        is_timeout = user_answer == "timeout"
        is_correct = False if is_timeout else (user_answer.lower() == current_q["correct_answer"].lower())
        
        if is_correct:
            quiz_data["score"] += 1

        next_idx = question_idx + 1

        if next_idx < len(questions):
            quiz_data["current"] = next_idx
            q = questions[next_idx]

            if is_timeout:
                result_text = f"⏰ انتهى الوقت! الإجابة الصحيحة كانت: {current_q['correct_answer']}"
            else:
                result_text = "✅ صحيح!" if is_correct else f"❌ خطأ! الإجابة: {current_q['correct_answer']}"

            text = f"{result_text}\n\n❓ <b>السؤال {next_idx + 1}/{len(questions)}</b>\n\n{q['question_text']}"

            # إضافة مؤقت للسؤال التالي (15 ثانية)
            if scheduler:
                next_timer_id = f"timer_{user.id}_{quiz_id}_{next_idx}"
                scheduler.scheduler.add_job(
                    self.handle_question_timeout,
                    "date",
                    run_date=datetime.now() + timedelta(seconds=15),
                    args=[user.id, quiz_id, next_idx, query.message.message_id],
                    id=next_timer_id
                )

            await query.edit_message_text(
                text,
                reply_markup=answer_keyboard(q, quiz_id, next_idx, language),
                parse_mode=ParseMode.HTML,
            )
        else:
            score = quiz_data["score"]
            total = quiz_data["total"]
            percentage = calculate_score(score, total)
            grade = self.quiz_service.calculate_grade(percentage, language)

            quiz = await db.get_quiz(quiz_id)
            quiz_title = quiz["title"] if quiz else "Unknown"

            await db.save_quiz_result(quiz_id, user.id, score, total)

            result_text = "✅ صحيح!" if is_correct else f"❌ خطأ! الإجابة: {current_q['correct_answer']}"

            text = result_text + "\n\n" + get_text(
                "quiz_result", language
            ).format(
                title=quiz_title,
                correct=score,
                total=total,
                percentage=percentage,
                grade=grade,
            )

            context.user_data.pop("taking_quiz", None)

            await query.edit_message_text(
                text,
                reply_markup=back_to_menu_keyboard(language),
                parse_mode=ParseMode.HTML,
            )