from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from locales import get_text


def main_menu_keyboard(language="ar", is_admin=False):
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("create_quiz", language), callback_data="create_quiz"
            ),
            InlineKeyboardButton(
                get_text("my_quizzes", language), callback_data="quiz_menu"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text("publish", language), callback_data="publish_menu"
            ),
            InlineKeyboardButton(
                get_text("schedule", language), callback_data="schedule_quiz"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text("channels", language), callback_data="channel_menu"
            ),
            InlineKeyboardButton(
                get_text("analytics", language), callback_data="analytics_menu"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text("ai_tools", language), callback_data="ai_menu"
            ),
            InlineKeyboardButton(
                get_text("settings", language), callback_data="settings"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text("support", language), callback_data="support"
            ),
        ],
    ]

    if is_admin:
        keyboard.append(
            [
                InlineKeyboardButton(
                    get_text("admin_panel", language),
                    callback_data="admin_panel",
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard(language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ]
        ]
    )


def confirm_cancel_keyboard(
    confirm_callback, cancel_callback, language="ar"
):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    get_text("confirm", language),
                    callback_data=confirm_callback,
                ),
                InlineKeyboardButton(
                    get_text("cancel", language),
                    callback_data=cancel_callback,
                ),
            ]
        ]
    )