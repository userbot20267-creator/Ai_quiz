from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from locales import get_text


def admin_panel_keyboard(language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📊 الإحصائيات" if language == "ar" else "📊 Statistics",
                    callback_data="admin_stats",
                ),
                InlineKeyboardButton(
                    "👥 المستخدمين" if language == "ar" else "👥 Users",
                    callback_data="admin_users",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📨 إرسال جماعي"
                    if language == "ar"
                    else "📨 Broadcast",
                    callback_data="admin_broadcast",
                ),
                InlineKeyboardButton(
                    "📢 قنوات الاشتراك"
                    if language == "ar"
                    else "📢 Force Channels",
                    callback_data="admin_force_channels",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🤖 إعدادات AI"
                    if language == "ar"
                    else "🤖 AI Settings",
                    callback_data="admin_ai_settings",
                ),
                InlineKeyboardButton(
                    "👮 المشرفين" if language == "ar" else "👮 Admins",
                    callback_data="admin_manage_admins",
                ),
            ],
            [
                InlineKeyboardButton(
                    "💬 رسائل الدعم"
                    if language == "ar"
                    else "💬 Support Messages",
                    callback_data="admin_support_messages",
                ),
                InlineKeyboardButton(
                    "📝 جميع الاختبارات"
                    if language == "ar"
                    else "📝 All Quizzes",
                    callback_data="admin_all_quizzes",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_text("back", language), callback_data="main_menu"
                )
            ],
        ]
    )