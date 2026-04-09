import functools
import logging
from config import config

logger = logging.getLogger(__name__)


def admin_only(func):
    @functools.wraps(func)
    async def wrapper(self, update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.ADMINS:
            if update.callback_query:
                await update.callback_query.answer(
                    "⛔ ليس لديك صلاحية!", show_alert=True
                )
            else:
                await update.message.reply_text("⛔ ليس لديك صلاحية!")
            return
        return await func(self, update, context, *args, **kwargs)

    return wrapper


def rate_limit(func):
    @functools.wraps(func)
    async def wrapper(self_or_update, update_or_context=None, context=None, *args, **kwargs):
        if context is None:
            update = self_or_update
            ctx = update_or_context
            self = None
        else:
            self = self_or_update
            update = update_or_context
            ctx = context

        user_id = update.effective_user.id
        protection = ctx.bot_data.get("protection")
        
        if protection:
            if not protection.check_rate_limit(user_id):
                msg = "❌ لقد تجاوزت الحد المسموح، حاول لاحقًا"
                if update.callback_query:
                    await update.callback_query.answer(msg, show_alert=True)
                elif update.message:
                    await update.message.reply_text(msg)
                return

        if self is not None:
            return await func(self, update, ctx, *args, **kwargs)
        else:
            return await func(self_or_update, update_or_context, *args, **kwargs)

    return wrapper


def owner_only(func):
    @functools.wraps(func)
    async def wrapper(self, update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != config.OWNER_ID:
            if update.callback_query:
                await update.callback_query.answer(
                    "⛔ هذا الأمر لمالك البوت فقط!", show_alert=True
                )
            else:
                await update.message.reply_text(
                    "⛔ هذا الأمر لمالك البوت فقط!"
                )
            return
        return await func(self, update, context, *args, **kwargs)

    return wrapper


def check_ban(func):
    @functools.wraps(func)
    async def wrapper(self_or_update, update_or_context=None, context=None, *args, **kwargs):
        if context is None:
            update = self_or_update
            ctx = update_or_context
            self = None
        else:
            self = self_or_update
            update = update_or_context
            ctx = context

        db = ctx.bot_data.get("db")
        if db:
            user_id = update.effective_user.id
            if await db.is_banned(user_id):
                if update.callback_query:
                    await update.callback_query.answer(
                        "⛔ تم حظرك من استخدام البوت!", show_alert=True
                    )
                elif update.message:
                    await update.message.reply_text(
                        "⛔ تم حظرك من استخدام البوت!"
                    )
                return

        if self is not None:
            return await func(self, update, ctx, *args, **kwargs)
        else:
            return await func(self_or_update, update_or_context, *args, **kwargs)

    return wrapper