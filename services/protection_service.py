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
        key = f"rate_{user_id}"
        count = self.rate_limit_cache.get(key, 0)

        if count >= config.RATE_LIMIT_MESSAGES:
            return False

        self.rate_limit_cache[key] = count + 1
        return True

    def check_spam(self, user_id, text):
        key = f"spam_{user_id}"
        last_texts = self.rate_limit_cache.get(key, [])

        if text in last_texts:
            return True

        last_texts.append(text)
        if len(last_texts) > 5:
            last_texts = last_texts[-5:]
        self.rate_limit_cache[key] = last_texts

        return False