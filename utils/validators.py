import re


def validate_quiz_title(title):
    if not title or len(title) < 2:
        return False, "العنوان قصير جداً (أقل من حرفين)"
    if len(title) > 200:
        return False, "العنوان طويل جداً (أكثر من 200 حرف)"
    return True, ""


def validate_question_text(text):
    if not text or len(text) < 3:
        return False, "السؤال قصير جداً"
    if len(text) > 1000:
        return False, "السؤال طويل جداً"
    return True, ""


def validate_option(option):
    if not option or len(option) < 1:
        return False, "الخيار فارغ"
    if len(option) > 200:
        return False, "الخيار طويل جداً"
    return True, ""


def validate_datetime_format(dt_str):
    pattern = r"^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$"
    if re.match(pattern, dt_str):
        return True
    return False


def validate_channel_id(channel_id):
    try:
        cid = int(channel_id)
        return cid < 0
    except (ValueError, TypeError):
        if isinstance(channel_id, str) and channel_id.startswith("@"):
            return True
        return False