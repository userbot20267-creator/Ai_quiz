QUIZ_STATES = {
    "DRAFT": "draft",
    "ACTIVE": "active",
    "PUBLISHED": "published",
    "ARCHIVED": "archived",
}

QUESTION_TYPES = {
    "MULTIPLE_CHOICE": "multiple_choice",
    "TRUE_FALSE": "true_false",
}

REPEAT_TYPES = {
    "NONE": "none",
    "DAILY": "daily",
    "WEEKLY": "weekly",
    "MONTHLY": "monthly",
}

QUEUE_STATUS = {
    "PENDING": "pending",
    "PUBLISHED": "published",
    "FAILED": "failed",
    "PAUSED": "paused",
}

USER_ROLES = {
    "USER": "user",
    "EDITOR": "editor",
    "ADMIN": "admin",
}

CATEGORIES = [
    "general",
    "science",
    "math",
    "language",
    "history",
    "geography",
    "technology",
    "sports",
    "entertainment",
    "religion",
    "other",
]

MAX_QUESTIONS_PER_QUIZ = 50
MAX_OPTIONS = 4
MAX_QUIZZES_PER_USER = 100
MAX_CHANNELS_PER_USER = 20