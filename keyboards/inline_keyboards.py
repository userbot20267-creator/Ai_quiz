from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def force_subscribe_keyboard(channels):
    keyboard = []
    for ch in channels:
        username = ch.get("channel_username", "")
        title = ch.get("channel_title", "قناة")
        if username:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📢 {title}",
                        url=f"https://t.me/{username.lstrip('@')}",
                    )
                ]
            )
    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ تحقق من الاشتراك", callback_data="check_subscription"
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def channel_list_keyboard(channels, language="ar"):
    keyboard = []
    for ch in channels:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"📢 {ch['title']}",
                    callback_data=f"ch_info_{ch['channel_id']}",
                ),
                InlineKeyboardButton(
                    "🗑️", callback_data=f"remove_ch_{ch['channel_id']}"
                ),
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                "➕ إضافة قناة" if language == "ar" else "➕ Add Channel",
                callback_data="add_channel_prompt",
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                "🔙 رجوع" if language == "ar" else "🔙 Back",
                callback_data="main_menu",
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def publish_channel_keyboard(channels, language="ar"):
    keyboard = []
    for ch in channels:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"📢 {ch['title']}",
                    callback_data=f"pub_ch_{ch['channel_id']}",
                )
            ]
        )
    if len(channels) > 1:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "📢 جميع القنوات"
                    if language == "ar"
                    else "📢 All Channels",
                    callback_data="pub_all_channels",
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                "❌ إلغاء" if language == "ar" else "❌ Cancel",
                callback_data="cancel_pub",
            )
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def language_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            ]
        ]
    )


def repeat_keyboard(language="ar"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ بدون" if language == "ar" else "❌ None",
                    callback_data="repeat_none",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📅 يومي" if language == "ar" else "📅 Daily",
                    callback_data="repeat_daily",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📆 أسبوعي" if language == "ar" else "📆 Weekly",
                    callback_data="repeat_weekly",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗓️ شهري" if language == "ar" else "🗓️ Monthly",
                    callback_data="repeat_monthly",
                ),
            ],
        ]
    )