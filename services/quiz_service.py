import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class QuizService:
    @staticmethod
    async def publish_quiz_to_channel(bot: Bot, quiz, questions, channel_id, use_inline=True):
        try:
            header = f"📝 <b>{quiz['title']}</b>\n"
            if quiz.get("description"):
                header += f"📄 {quiz['description']}\n"
            header += f"\n❓ عدد الأسئلة: {len(questions)}\n"
            header += "─" * 30

            await bot.send_message(
                chat_id=channel_id,
                text=header,
                parse_mode=ParseMode.HTML,
            )

            for i, q in enumerate(questions):
                text = f"❓ {i + 1}. {q['question_text']}"
                
                if not use_inline:
                    # Original Poll logic
                    if q["question_type"] == "true_false":
                        options = ["صح ✅", "خطأ ❌"]
                        correct_id = 0 if q["correct_answer"].lower() in ("true", "صح", "a") else 1
                    else:
                        options = []
                        for opt_key in ["option_a", "option_b", "option_c", "option_d"]:
                            if q.get(opt_key):
                                options.append(q[opt_key])
                        answer_map = {"a": 0, "b": 1, "c": 2, "d": 3}
                        correct_id = answer_map.get(q["correct_answer"].lower(), 0)
                        if correct_id >= len(options): correct_id = 0
                        for idx, opt in enumerate(options):
                            if opt.lower().strip() == q["correct_answer"].lower().strip():
                                correct_id = idx
                                break

                    await bot.send_poll(
                        chat_id=channel_id,
                        question=text,
                        options=options,
                        type="quiz",
                        correct_option_id=correct_id,
                        explanation=q.get("explanation", ""),
                        is_anonymous=True,
                    )
                else:
                    # New Inline logic
                    keyboard = []
                    if q["question_type"] == "true_false":
                        keyboard.append([
                            InlineKeyboardButton("صح ✅", callback_data=f"inline_ans_{quiz['quiz_id']}_{q['question_id']}_a"),
                            InlineKeyboardButton("خطأ ❌", callback_data=f"inline_ans_{quiz['quiz_id']}_{q['question_id']}_b")
                        ])
                    else:
                        for letter in ["a", "b", "c", "d"]:
                            opt_text = q.get(f"option_{letter}")
                            if opt_text:
                                keyboard.append([InlineKeyboardButton(opt_text, callback_data=f"inline_ans_{quiz['quiz_id']}_{q['question_id']}_{letter}")])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    if q.get("media_file_id") and q.get("media_type"):
                        media_type = q["media_type"]
                        file_id = q["media_file_id"]
                        if media_type == "photo":
                            await bot.send_photo(chat_id=channel_id, photo=file_id, caption=text, reply_markup=reply_markup)
                        elif media_type == "video":
                            await bot.send_video(chat_id=channel_id, video=file_id, caption=text, reply_markup=reply_markup)
                        else:
                            await bot.send_message(chat_id=channel_id, text=text, reply_markup=reply_markup)
                    else:
                        await bot.send_message(chat_id=channel_id, text=text, reply_markup=reply_markup)

            return True, ""
        except Exception as e:
            logger.error(f"Error publishing quiz: {e}")
            return False, str(e)

    @staticmethod
    def calculate_grade(percentage, language="ar"):
        if percentage >= 90:
            return "🏆 ممتاز!" if language == "ar" else "🏆 Excellent!"
        elif percentage >= 75:
            return "🌟 جيد جداً!" if language == "ar" else "🌟 Very Good!"
        elif percentage >= 60:
            return "👍 جيد" if language == "ar" else "👍 Good"
        elif percentage >= 50:
            return "📝 مقبول" if language == "ar" else "📝 Fair"
        else:
            return "📚 يحتاج مراجعة" if language == "ar" else "📚 Needs Review"