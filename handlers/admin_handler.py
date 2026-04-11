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

    @admin_only
    async def all_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = context.bot_data.get("db")
        users = await db.get_all_users()
        text = f"👥 <b>قائمة جميع المستخدمين ({len(users)})</b>\n\n"
        for u in users[:50]:
            status = "🚫" if u["is_banned"] else "✅"
            name = u.get("first_name", "") or u.get("username", "Unknown")
            text += f"{status} {name} (ID: <code>{u['user_id']}</code>)\n"
        
        if len(users) > 50:
            text += f"\n... و {len(users) - 50} مستخدم آخر"
            
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    @admin_only
    async def all_quizzes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = context.bot_data.get("db")
        quizzes = await db.get_all_quizzes()
        text = f"📝 <b>قائمة جميع الاختبارات ({len(quizzes)})</b>\n\n"
        for q in quizzes[:50]:
            text += f"• {q['title']} (ID: <code>{q['quiz_id']}</code>) - بواسطة: {q['user_id']}\n"
            
        if len(quizzes) > 50:
            text += f"\n... و {len(quizzes) - 50} اختبار آخر"
            
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    @admin_only
    async def ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("⚠️ يرجى إرسال ID المستخدم: <code>/ban 123456</code>", parse_mode=ParseMode.HTML)
            return
        
        try:
            user_id = int(context.args[0])
            db = context.bot_data.get("db")
            await db.ban_user(user_id)
            await update.message.reply_text(f"✅ تم حظر المستخدم {user_id} بنجاح.")
        except ValueError:
            await update.message.reply_text("❌ ID غير صالح.")

    @admin_only
    async def unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("⚠️ يرجى إرسال ID المستخدم: <code>/unban 123456</code>", parse_mode=ParseMode.HTML)
            return
        
        try:
            user_id = int(context.args[0])
            db = context.bot_data.get("db")
            await db.unban_user(user_id)
            await update.message.reply_text(f"✅ تم إلغاء حظر المستخدم {user_id} بنجاح.")
        except ValueError:
            await update.message.reply_text("❌ ID غير صالح.")

    @admin_only
    async def del_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("⚠️ يرجى إرسال ID الاختبار: <code>/del_quiz 123</code>", parse_mode=ParseMode.HTML)
            return
        
        quiz_id = int(context.args[0])
        db = context.bot_data.get("db")
        quiz = await db.get_quiz(quiz_id)
        
        if quiz:
            await db.delete_quiz(quiz_id)
            await update.message.reply_text(f"✅ تم حذف الاختبار '{quiz['title']}' بنجاح.")
        else:
            await update.message.reply_text("❌ لم يتم العثور على الاختبار.")

    async def admin_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        if user.id not in config.ADMINS and user.id != config.OWNER_ID:
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

            keyboard = []
            if force_channels:
                for ch in force_channels:
                    text += f"📢 {ch['channel_title']} (<code>{ch['channel_id']}</code>)\n"
                    keyboard.append([InlineKeyboardButton(f"❌ حذف {ch['channel_title']}", callback_data=f"admin_del_force_{ch['channel_id']}")])
            else:
                text += "لا توجد قنوات مضافة.\n"

            text += "\n💡 لإضافة قناة، أرسل:\n<code>/add_force @channel_username</code>"

            keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
            )

        elif action.startswith("del_force_"):
            channel_id = query.data.replace("admin_del_force_", "")
            await db.remove_force_channel(channel_id)
            await query.answer("✅ تم حذف القناة من الاشتراك الإجباري")
            # إعادة تحميل القائمة
            query.data = "admin_force_channels"
            await self.admin_callback(update, context)
            return

        elif action == "all_quizzes":
            quizzes = await db.get_all_quizzes()
            text = f"📝 <b>إدارة جميع الاختبارات ({len(quizzes)})</b>\n\n"
            text += "هنا يمكنك عرض وحذف أي اختبار موجود في البوت:\n\n"
            
            keyboard = []
            for q in quizzes[:15]:
                # جلب معلومات المستخدم صاحب الاختبار
                owner = await db.get_user(q['user_id'])
                owner_name = owner.get('first_name', 'Unknown') if owner else "Unknown"
                
                text += f"🔹 <b>{q['title']}</b>\n"
                text += f"👤 المالك: {owner_name} (<code>{q['user_id']}</code>)\n"
                text += f"🆔 ID: <code>{q['quiz_id']}</code>\n"
                text += "──────────────────\n"
                
                keyboard.append([
                    InlineKeyboardButton(f"🗑 حذف: {q['title'][:15]}...", callback_data=f"admin_del_quiz_{q['quiz_id']}")
                ])
            
            if len(quizzes) > 15:
                text += f"\n... و {len(quizzes) - 15} اختبار آخر"
            
            keyboard.append([InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
            )

        elif action.startswith("del_quiz_"):
            quiz_id = int(query.data.replace("admin_del_quiz_", ""))
            quiz = await db.get_quiz(quiz_id)
            if quiz:
                # حذف الاختبار من قاعدة البيانات
                await db.delete_quiz(quiz_id)
                await query.answer(f"✅ تم حذف '{quiz['title']}' بنجاح", show_alert=True)
                
                # تحديث القائمة فوراً
                quizzes = await db.get_all_quizzes()
                text = f"📝 <b>إدارة جميع الاختبارات ({len(quizzes)})</b>\n\n"
                keyboard = []
                for q in quizzes[:15]:
                    owner = await db.get_user(q['user_id'])
                    owner_name = owner.get('first_name', 'Unknown') if owner else "Unknown"
                    text += f"🔹 <b>{q['title']}</b>\n👤 المالك: {owner_name}\n🆔 ID: <code>{q['quiz_id']}</code>\n──────────────────\n"
                    keyboard.append([InlineKeyboardButton(f"🗑 حذف: {q['title'][:15]}...", callback_data=f"admin_del_quiz_{q['quiz_id']}")])
                
                keyboard.append([InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel")])
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
            else:
                await query.answer("❌ الاختبار غير موجود")
            return

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