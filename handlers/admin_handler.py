import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import config
from locales import get_text
from keyboards.admin_keyboards import admin_panel_keyboard
from keyboards.main_keyboards import back_to_menu_keyboard
from utils.decorators import admin_only
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class AdminHandler:
    @admin_only
    async def admin_panel(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await db.get_user_language(user.id) if db else "ar"

        if update.message:
            await update.message.reply_text(
                get_text("admin_panel", language),
                reply_markup=admin_panel_keyboard(language),
                parse_mode=ParseMode.HTML,
            )
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                get_text("admin_panel", language),
                reply_markup=admin_panel_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

    async def admin_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        if user.id not in config.ADMINS:
            await query.answer("⛔ ليس لديك صلاحية!", show_alert=True)
            return

        db = context.bot_data.get("db")
        language = await db.get_user_language(user.id) if db else "ar"
        action = query.data.replace("admin_", "")

        if action == "stats":
            analytics = AnalyticsService(db)
            stats = await analytics.get_global_stats()

            text = (
                f"📊 <b>إحصائيات البوت</b>\n\n"
                f"👥 المستخدمين: {stats['total_users']}\n"
                f"📝 الاختبارات: {stats['total_quizzes']}\n"
                f"📢 القنوات: {stats['total_channels']}\n"
            )

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_panel"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

        elif action == "users":
            users = await db.get_all_users()
            text = f"👥 <b>المستخدمين ({len(users)})</b>\n\n"

            for u in users[:20]:
                status = "🚫" if u["is_banned"] else "✅"
                role = "👑" if u["is_admin"] else "👤"
                name = u.get("first_name", "") or u.get("username", "Unknown")
                text += f"{status} {role} {name} (ID: {u['user_id']})\n"

            if len(users) > 20:
                text += f"\n... و {len(users) - 20} مستخدم آخر"

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🚫 حظر مستخدم", callback_data="admin_ban_prompt"
                    ),
                    InlineKeyboardButton(
                        "✅ إلغاء حظر", callback_data="admin_unban_prompt"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🔙 رجوع", callback_data="admin_panel"
                    )
                ],
            ]

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
            )

        elif action == "force_channels":
            force_channels = await db.get_force_channels()
            text = "📢 <b>قنوات الاشتراك الإجباري</b>\n\n"

            if force_channels:
                for ch in force_channels:
                    text += f"📢 {ch['channel_title']} ({ch['channel_id']})\n"
            else:
                text += "لا توجد قنوات مضافة.\n"

            text += "\n💡 لإضافة قناة، أرسل:\n<code>/add_force @channel_username</code>"

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_panel"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

        elif action == "ai_settings":
            # عرض إعدادات OpenRouter
            ai_connected = "✅ متصل" if config.OPENROUTER_API_KEY else "❌ غير متصل"
            model = config.OPENROUTER_MODEL

            text = (
                f"🤖 <b>إعدادات الذكاء الاصطناعي (OpenRouter)</b>\n\n"
                f"📡 حالة الاتصال: {ai_connected}\n"
                f"🧠 النموذج: <code>{model}</code>\n"
                f"📊 الحد اليومي لكل مستخدم: {config.MAX_AI_REQUESTS_PER_USER} طلب\n"
                f"🌐 الخادم: <code>{config.OPENROUTER_BASE_URL}</code>\n\n"
                f"<b>نماذج مقترحة:</b>\n"
                f"• <code>google/gemini-2.0-flash-001</code> (سريع ومجاني)\n"
                f"• <code>google/gemini-pro</code>\n"
                f"• <code>meta-llama/llama-3-8b-instruct</code>\n"
                f"• <code>mistralai/mistral-7b-instruct</code>\n"
                f"• <code>openai/gpt-3.5-turbo</code>\n"
                f"• <code>anthropic/claude-3-haiku</code>\n\n"
                f"لتغيير النموذج، عدّل متغير <code>OPENROUTER_MODEL</code>"
            )

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_panel"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

        elif action == "manage_admins":
            text = "👮 <b>المشرفين</b>\n\n"
            for admin_id in config.ADMINS:
                admin_user = await db.get_user(admin_id)
                if admin_user:
                    name = admin_user.get("first_name", "") or admin_user.get(
                        "username", "Unknown"
                    )
                    role = admin_user.get("role", "admin")
                    text += f"👑 {name} (ID: {admin_id}) - {role}\n"
                else:
                    text += f"👑 ID: {admin_id}\n"

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_panel"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

        elif action == "support_messages":
            messages = await db.get_unread_support_messages()
            text = "💬 <b>رسائل الدعم</b>\n\n"

            if messages:
                for msg in messages[:10]:
                    name = msg.get("first_name", "") or msg.get(
                        "username", "Unknown"
                    )
                    text += (
                        f"👤 {name} (ID: {msg['user_id']}):\n"
                        f"💬 {msg['message'][:100]}\n"
                        f"📅 {msg['created_at'][:16]}\n\n"
                    )
            else:
                text += "لا توجد رسائل جديدة."

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_panel"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

        elif action == "panel":
            await query.edit_message_text(
                get_text("admin_panel", language),
                reply_markup=admin_panel_keyboard(language),
                parse_mode=ParseMode.HTML,
            )

        elif action == "ban_prompt":
            await query.edit_message_text(
                "🚫 أرسل ID المستخدم لحظره:\n<code>/ban USER_ID</code>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_users"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

        elif action == "unban_prompt":
            await query.edit_message_text(
                "✅ أرسل ID المستخدم لإلغاء حظره:\n<code>/unban USER_ID</code>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 رجوع", callback_data="admin_users"
                            )
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )