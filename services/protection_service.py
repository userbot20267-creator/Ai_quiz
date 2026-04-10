import time
import logging
from cachetools import TTLCache
from config import config

logger = logging.getLogger(__name__)


class ProtectionService:
    def __init__(self):
        self.rate_limit_cache = TTLCache(
            maxsize=10000, ttl=config.RATE_LIMIT_PERIOD
        )

    def check_rate_limit(self, user_id):
        """التحقق من عدد الطلبات في الدقيقة"""
        key = f"rate_{user_id}"
        count = self.rate_limit_cache.get(key, 0)

        if count >= config.RATE_LIMIT_MESSAGES:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False

        self.rate_limit_cache[key] = count + 1
        return True

    def check_spam(self, user_id, text):
        """التحقق من تكرار النصوص (Spam)"""
        if not text or len(text) < 2:
            return False
            
        key = f"spam_{user_id}"
        last_texts = self.rate_limit_cache.get(key, [])

        if text in last_texts:
            logger.warning(f"Spam detected from user {user_id}")
            return True

        last_texts.append(text)
        if len(last_texts) > 5:
            last_texts = last_texts[-5:]
        self.rate_limit_cache[key] = last_texts

        return False

    def validate_input(self, text, max_length=1000):
        """التحقق من سلامة المدخلات"""
        if not text:
            return False
        if len(text) > max_length:
            return False
        # يمكن إضافة المزيد من التحققات هنا (مثل الكلمات النابية أو الروابط المشبوهة)
        return True