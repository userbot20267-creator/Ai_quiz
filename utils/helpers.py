import hashlib
import time
import json
from datetime import datetime


def generate_unique_code(quiz_id):
    data = f"{quiz_id}_{time.time()}"
    return hashlib.md5(data.encode()).hexdigest()[:10]


def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(dt_str)


def parse_quick_quiz(text):
    """Parse quick quiz format: /add_quiz answer; question; opt1; opt2; opt3; opt4"""
    parts = text.split(";")
    if len(parts) < 4:
        return None

    parts = [p.strip() for p in parts]
    correct_answer = parts[0]
    question_text = parts[1]
    options = parts[2:]

    while len(options) < 4:
        options.append(None)

    return {
        "correct_answer": correct_answer,
        "question_text": question_text,
        "option_a": options[0],
        "option_b": options[1] if len(options) > 1 else None,
        "option_c": options[2] if len(options) > 2 else None,
        "option_d": options[3] if len(options) > 3 else None,
    }


def calculate_score(correct, total):
    if total == 0:
        return 0
    return round((correct / total) * 100, 1)


def truncate_text(text, max_length=50):
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def quiz_to_json(quiz, questions):
    return json.dumps(
        {
            "title": quiz.get("title", ""),
            "description": quiz.get("description", ""),
            "category": quiz.get("category", "general"),
            "questions": [
                {
                    "text": q["question_text"],
                    "type": q["question_type"],
                    "option_a": q["option_a"],
                    "option_b": q["option_b"],
                    "option_c": q["option_c"],
                    "option_d": q["option_d"],
                    "correct": q["correct_answer"],
                    "explanation": q.get("explanation", ""),
                }
                for q in questions
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def json_to_quiz(json_str):
    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError:
        return None