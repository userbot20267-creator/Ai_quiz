import logging
from utils.helpers import generate_unique_code

logger = logging.getLogger(__name__)


class LinkService:
    def __init__(self, db, bot_username):
        self.db = db
        self.bot_username = bot_username

    async def create_quiz_link(self, quiz_id):
        code = generate_unique_code(quiz_id)
        await self.db.create_quiz_link(quiz_id, code)
        link = f"https://t.me/{self.bot_username}?start=quiz_{code}"
        return link, code

    async def get_quiz_from_link(self, code):
        link_data = await self.db.get_quiz_link(code)
        if link_data:
            await self.db.increment_link_clicks(code)
            return link_data["quiz_id"]
        return None

    async def get_link_stats(self, quiz_id):
        links = await self.db.get_quiz_links(quiz_id)
        total_clicks = sum(l["clicks"] for l in links)
        return {
            "links": links,
            "total_clicks": total_clicks,
        }