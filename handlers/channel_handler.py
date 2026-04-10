import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from locales import get_text
from keyboards.inline_keyboards import channel_list_keyboard
from keyboards.main_keyboards import back_to_menu_keyboard

logger = logging.getLogger(__name__)


class ChannelHandler:
    async def _get_language(self, user_id, context):
        db = context.bot_data.get("db")
        if db:
            return await db.get_user_language(user_id)
        return "ar"

    async def add_channel(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        if not context.args:
            await update.message.reply_text(
                "📢 أرسل معرف القناة أو المجموعة:\n"
                "<code>/add_channel @channel_username</code>\n"
                "أو\n"
                "<code>/add_channel -100123456789</code>",
                parse_mode=ParseMode.HTML,
            )
            return

        channel_id = context.args[0]

        try:
            chat = await context.bot.get_chat(channel_id)
            bot_member = await context.bot.get_chat_member(
                chat.id, context.bot.id
            )

            if bot_member.status not in ("administrator", "creator"):
                await update.message.reply_text(
                    get_text("bot_not_admin", language)
                )
                return

            channel_type = "group" if chat.type in ("group", "supergroup") else "channel"

            await db.add_channel(
                chat.id,
                user.id,
                chat.title or "Unknown",
                chat.username or "",
                channel_type,
            )

            await update.message.reply_text(
                get_text("channel_added", language).format(
                    title=chat.title or "Unknown"
                ),
                reply_markup=back_to_menu_keyboard(language),
            )

        except Exception as e:
            logger.error(f"Add channel error: {e}")
            await update.message.reply_text(
                f"❌ خطأ: {str(e)}\n\nتأكد من:\n"
                "1. المعرف صحيح\n"
                "2. البوت مشرف في القناة/المجموعة",
                reply_markup=back_to_menu_keyboard(language),
            )

    async def my_channels(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        channels = await db.get_user_channels(user.id)

        if not channels:
            await update.message.reply_text(
                get_text("no_channels", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return

        await update.message.reply_text(
            f"📢 <b>قنواتك ({len(channels)})</b>"
            if language == "ar"
            else f"📢 <b>Your Channels ({len(channels)})</b>",
            reply_markup=channel_list_keyboard(channels, language),
            parse_mode=ParseMode.HTML,
        )

    async def channel_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        channels = await db.get_user_channels(user.id)

        if not channels:
            await query.edit_message_text(
                get_text("no_channels", language),
                reply_markup=back_to_menu_keyboard(language),
            )
            return

        await query.edit_message_text(
            f"📢 <b>قنواتك ({len(channels)})</b>"
            if language == "ar"
            else f"📢 <b>Your Channels ({len(channels)})</b>",
            reply_markup=channel_list_keyboard(channels, language),
            parse_mode=ParseMode.HTML,
        )

    async def remove_channel(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        channel_id = int(query.data.replace("remove_ch_", ""))
        await db.remove_channel(channel_id)

        await query.edit_message_text(
            get_text("channel_removed", language),
            reply_markup=back_to_menu_keyboard(language),
        )

    async def add_force(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        db = context.bot_data.get("db")
        language = await self._get_language(user.id, context)

        # التحقق من أن المستخدم أدمن أو المالك
        if user.id not in config.ADMINS and user.id != config.OWNER_ID:
            return

        if not context.args:
            await update.message.reply_text(
                "📢 أرسل معرف القناة للاشتراك الإجباري:\n"
                "<code>/add_force @channel_username</code>",
                parse_mode=ParseMode.HTML,
            )
            return

        channel_id = context.args[0]

        try:
            chat = await context.bot.get_chat(channel_id)
            
            # التحقق من أن البوت مشرف في القناة
            try:
                bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
                if bot_member.status not in ("administrator", "creator"):
                    await update.message.reply_text(
                        "⚠️ البوت ليس مشرفاً في هذه القناة. يرجى رفعه لرتبة مشرف أولاً."
                    )
                    return
            except Exception:
                await update.message.reply_text(
                    "⚠️ تعذر التحقق من صلاحيات البوت. تأكد من إضافة البوت للقناة كـ مشرف."
                )
                return

            await db.add_force_channel(
                str(chat.id),
                chat.title or "Unknown",
                chat.username or "",
            )

            await update.message.reply_text(
                f"✅ تم إضافة القناة للاشتراك الإجباري: {chat.title or 'Unknown'}",
                reply_markup=back_to_menu_keyboard(language),
            )

        except Exception as e:
            logger.error(f"Add force channel error: {e}")
            await update.message.reply_text(
                f"❌ خطأ: {str(e)}\nتأكد من أن المعرف صحيح وأن البوت مضاف للقناة.",
                reply_markup=back_to_menu_keyboard(language),
            )

    async def bot_added_to_chat(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle when bot is added to a group/channel"""
        if update.message and update.message.new_chat_members:
            for member in update.message.new_chat_members:
                if member.id == context.bot.id:
                    chat = update.message.chat
                    logger.info(
                        f"Bot added to: {chat.title} ({chat.id})"
                    )