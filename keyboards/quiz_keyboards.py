from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from locales import get_text


def question_type_keyboard(language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    get_text("multiple_choice", language),
                    callback_data="qtype_multiple",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("true_false", language),
                    callback_data="qtype_truefalse",
                ),
            ],
        ]
    )


def correct_answer_keyboard(options, language="ar"):
    keyboard = []
    labels = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        if opt:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{labels[i]}: {opt}",
                        callback_data=f"answer_{labels[i].lower()}",
                    )
                ]
            )
    return InlineKeyboardMarkup(keyboard)


def add_question_keyboard(language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ إضافة وسائط" if language == "ar" else "➕ Add Media",
                    callback_data="add_media",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("finish", language),
                    callback_data="finish_quiz",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("cancel", language),
                    callback_data="cancel_quiz",
                ),
            ],
        ]
    )


def quiz_actions_keyboard(quiz_id, language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📤 نشر" if language == "ar" else "📤 Publish",
                    callback_data=f"publish_quiz_{quiz_id}",
                ),
                InlineKeyboardButton(
                    "✏️ تعديل" if language == "ar" else "✏️ Edit",
                    callback_data=f"edit_quiz_{quiz_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎯 حل الاختبار" if language == "ar" else "🎯 Take Quiz",
                    callback_data=f"take_quiz_{quiz_id}",
                ),
                InlineKeyboardButton(
                    "🔗 رابط" if language == "ar" else "🔗 Link",
                    callback_data=f"link_quiz_{quiz_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📊 إحصائيات" if language == "ar" else "📊 Stats",
                    callback_data=f"quiz_stats_{quiz_id}",
                ),
                InlineKeyboardButton(
                    "🗑️ حذف" if language == "ar" else "🗑️ Delete",
                    callback_data=f"delete_quiz_{quiz_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="quiz_menu"
                )
            ],
        ]
    )


def quiz_list_keyboard(quizzes, language="ar"):
    keyboard = []
    for quiz in quizzes[:20]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"📝 {quiz['title']}",
                    callback_data=f"view_quiz_{quiz['quiz_id']}",
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                get_text("create_quiz", language), callback_data="create_quiz"
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                get_text("back", language), callback_data="main_menu"
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def skip_keyboard(callback_data, language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    get_text("skip", language), callback_data=callback_data
                )
            ]
        ]
    )


def category_keyboard(language="ar"):
    categories = {
        "general": "📋 عام" if language == "ar" else "📋 General",
        "science": "🔬 علوم" if language == "ar" else "🔬 Science",
        "math": "🔢 رياضيات" if language == "ar" else "🔢 Math",
        "language": "📖 لغات" if language == "ar" else "📖 Language",
        "history": "🏛️ تاريخ" if language == "ar" else "🏛️ History",
        "geography": "🌍 جغرافيا" if language == "ar" else "🌍 Geography",
        "technology": "💻 تكنولوجيا" if language == "ar" else "💻 Technology",
        "religion": "🕌 دين" if language == "ar" else "🕌 Religion",
        "other": "📦 أخرى" if language == "ar" else "📦 Other",
    }

    keyboard = []
    row = []
    for key, label in categories.items():
        row.append(
            InlineKeyboardButton(label, callback_data=f"cat_{key}")
        )
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def answer_keyboard(question, quiz_id, question_idx, language="ar"):
    keyboard = []
    if question["question_type"] == "true_false":
        keyboard.append(
            [
                InlineKeyboardButton(
                    "✅ صح" if language == "ar" else "✅ True",
                    callback_data=f"ans_{quiz_id}_{question_idx}_true",
                ),
                InlineKeyboardButton(
                    "❌ خطأ" if language == "ar" else "❌ False",
                    callback_data=f"ans_{quiz_id}_{question_idx}_false",
                ),
            ]
        )
    else:
        labels = {"a": "A", "b": "B", "c": "C", "d": "D"}
        options = {
            "a": question["option_a"],
            "b": question["option_b"],
            "c": question["option_c"],
            "d": question["option_d"],
        }
        for key, opt in options.items():
            if opt:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{labels[key]}: {opt}",
                            callback_data=f"ans_{quiz_id}_{question_idx}_{key}",
                        )
                    ]
                )

    return InlineKeyboardMarkup(keyboard)