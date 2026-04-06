import logging
import json
import re
import aiohttp
from config import config

logger = logging.getLogger(__name__)


class AIService:
    """خدمة الذكاء الاصطناعي باستخدام OpenRouter API"""

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model = config.OPENROUTER_MODEL
        self.base_url = config.OPENROUTER_BASE_URL
        self.app_name = config.OPENROUTER_APP_NAME
        self.is_configured = bool(self.api_key)

        if self.is_configured:
            logger.info(f"AI Service configured with model: {self.model}")
        else:
            logger.warning("AI Service: No OPENROUTER_API_KEY set - using fallback mode")

    async def _make_request(self, messages, temperature=0.7, max_tokens=2000):
        """إرسال طلب إلى OpenRouter API"""
        if not self.is_configured:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ai-quiz-bot",
            "X-Title": self.app_name,
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return content.strip()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"OpenRouter API error {response.status}: {error_text}"
                        )
                        return None

        except aiohttp.ClientError as e:
            logger.error(f"OpenRouter connection error: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error("OpenRouter request timeout")
            return None
        except Exception as e:
            logger.error(f"OpenRouter unexpected error: {e}")
            return None

    def _extract_json(self, text):
        """استخراج JSON من النص"""
        if not text:
            return None

        # محاولة 1: البحث عن مصفوفة JSON
        json_match = re.search(r'\[[\s\S]*?\]', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # محاولة 2: البحث عن كود JSON بين ```
        code_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if code_match:
            try:
                return json.loads(code_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # محاولة 3: تحليل النص كاملاً
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # محاولة 4: إصلاح JSON شائع الأخطاء
        try:
            # إزالة الفواصل الزائدة قبل ]
            cleaned = re.sub(r',\s*]', ']', text)
            cleaned = re.sub(r',\s*}', '}', cleaned)
            json_match = re.search(r'\[[\s\S]*\]', cleaned)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        logger.warning(f"Could not extract JSON from response: {text[:200]}")
        return None

    async def generate_questions(
        self, topic, num_questions=5, difficulty="medium", language="ar"
    ):
        """توليد أسئلة اختبار من موضوع"""
        if not self.is_configured:
            return self._generate_fallback_questions(topic, num_questions, language)

        lang_text = "Arabic" if language == "ar" else "English"
        difficulty_map = {
            "easy": "سهل / Easy",
            "medium": "متوسط / Medium",
            "hard": "صعب / Hard",
        }
        diff_text = difficulty_map.get(difficulty, "Medium")

        system_prompt = (
            "You are an expert quiz question generator. "
            "You MUST return ONLY a valid JSON array. "
            "No explanations, no markdown, no extra text. "
            "Just the JSON array."
        )

        user_prompt = f"""Generate exactly {num_questions} quiz questions about "{topic}" in {lang_text}.
Difficulty level: {diff_text}

Return ONLY a valid JSON array. Each object must have exactly these keys:
- "question": the question text in {lang_text}
- "type": "multiple_choice"
- "option_a": first option
- "option_b": second option
- "option_c": third option
- "option_d": fourth option
- "correct": letter of correct answer (only "a", "b", "c", or "d")
- "explanation": brief explanation in {lang_text}

Example:
[
  {{
    "question": "What is 2+2?",
    "type": "multiple_choice",
    "option_a": "3",
    "option_b": "4",
    "option_c": "5",
    "option_d": "6",
    "correct": "b",
    "explanation": "2+2 equals 4"
  }}
]

Generate {num_questions} questions now. Return ONLY the JSON array:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        content = await self._make_request(messages, temperature=0.7, max_tokens=3000)
        questions = self._extract_json(content)

        if questions and isinstance(questions, list) and len(questions) > 0:
            # التحقق من صحة البيانات
            validated = []
            for q in questions:
                validated_q = self._validate_question(q)
                if validated_q:
                    validated.append(validated_q)

            if validated:
                logger.info(f"Generated {len(validated)} questions about '{topic}'")
                return validated

        logger.warning(f"AI generation failed for topic '{topic}', using fallback")
        return self._generate_fallback_questions(topic, num_questions, language)

    async def generate_true_false_questions(
        self, topic, num_questions=5, language="ar"
    ):
        """توليد أسئلة صح/خطأ"""
        if not self.is_configured:
            return self._generate_fallback_tf_questions(topic, num_questions, language)

        lang_text = "Arabic" if language == "ar" else "English"
        true_text = "صح" if language == "ar" else "True"
        false_text = "خطأ" if language == "ar" else "False"

        system_prompt = (
            "You are an expert quiz generator. "
            "Return ONLY a valid JSON array. No extra text."
        )

        user_prompt = f"""Generate exactly {num_questions} True/False questions about "{topic}" in {lang_text}.

Return ONLY a JSON array. Each object:
- "question": statement text in {lang_text}
- "type": "true_false"
- "option_a": "{true_text}"
- "option_b": "{false_text}"
- "option_c": null
- "option_d": null
- "correct": "a" if true, "b" if false
- "explanation": brief explanation in {lang_text}

Return ONLY the JSON array:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        content = await self._make_request(messages, temperature=0.7, max_tokens=2000)
        questions = self._extract_json(content)

        if questions and isinstance(questions, list):
            validated = [self._validate_question(q) for q in questions if self._validate_question(q)]
            if validated:
                return validated

        return self._generate_fallback_tf_questions(topic, num_questions, language)

    async def extract_from_text(self, text, num_questions=5, language="ar"):
        """استخراج أسئلة من نص"""
        if not self.is_configured:
            return self._generate_fallback_questions("text", num_questions, language)

        lang_text = "Arabic" if language == "ar" else "English"
        # اقتطاع النص إذا كان طويلاً جداً
        truncated_text = text[:4000]

        system_prompt = (
            "You are an expert at creating quiz questions from educational text. "
            "Return ONLY a valid JSON array."
        )

        user_prompt = f"""Based on the following text, create exactly {num_questions} quiz questions in {lang_text}.

TEXT:
\"\"\"
{truncated_text}
\"\"\"

Return ONLY a valid JSON array. Each object must have:
- "question": question based on the text
- "type": "multiple_choice"
- "option_a": first option
- "option_b": second option
- "option_c": third option
- "option_d": fourth option
- "correct": "a", "b", "c", or "d"
- "explanation": brief explanation

Return ONLY the JSON array:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        content = await self._make_request(messages, temperature=0.7, max_tokens=3000)
        questions = self._extract_json(content)

        if questions and isinstance(questions, list):
            validated = [self._validate_question(q) for q in questions if self._validate_question(q)]
            if validated:
                logger.info(f"Extracted {len(validated)} questions from text")
                return validated

        return self._generate_fallback_questions("text", num_questions, language)

    async def extract_from_url(self, url, num_questions=5, language="ar"):
        """استخراج أسئلة من رابط"""
        try:
            from bs4 import BeautifulSoup

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # إزالة العناصر غير المرغوبة
                        for tag in soup(["script", "style", "nav", "footer", "header"]):
                            tag.decompose()

                        text = soup.get_text(separator="\n", strip=True)
                        # اقتطاع النص
                        text = text[:5000]

                        return await self.extract_from_text(text, num_questions, language)
                    else:
                        logger.error(f"URL fetch failed: {response.status}")
                        return self._generate_fallback_questions(url, num_questions, language)

        except Exception as e:
            logger.error(f"URL extraction error: {e}")
            return self._generate_fallback_questions(url, num_questions, language)

    async def extract_from_pdf(self, file_bytes, num_questions=5, language="ar"):
        """استخراج أسئلة من ملف PDF"""
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO

            reader = PdfReader(BytesIO(file_bytes))
            text = ""
            for page in reader.pages[:20]:  # أول 20 صفحة فقط
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            if text.strip():
                return await self.extract_from_text(text, num_questions, language)
            else:
                logger.warning("PDF has no extractable text")
                return self._generate_fallback_questions("PDF", num_questions, language)

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return self._generate_fallback_questions("PDF", num_questions, language)

    async def rephrase_question(self, question_text, language="ar"):
        """إعادة صياغة سؤال"""
        if not self.is_configured:
            return question_text

        lang_text = "Arabic" if language == "ar" else "English"

        messages = [
            {
                "role": "system",
                "content": f"You are a language expert. Rephrase the given question in {lang_text}. "
                           f"Keep the same meaning but use different words. Return ONLY the rephrased question.",
            },
            {"role": "user", "content": question_text},
        ]

        result = await self._make_request(messages, temperature=0.8, max_tokens=300)
        if result:
            # تنظيف النتيجة
            result = result.strip().strip('"').strip("'")
            if len(result) > 5:
                return result

        return question_text

    async def improve_content(self, text, language="ar"):
        """تحسين جودة المحتوى"""
        if not self.is_configured:
            return text

        lang_text = "Arabic" if language == "ar" else "English"

        messages = [
            {
                "role": "system",
                "content": f"You are an educational content expert. "
                           f"Improve the following content in {lang_text}. "
                           f"Make it clearer, more engaging, and educational. "
                           f"Return ONLY the improved text.",
            },
            {"role": "user", "content": text},
        ]

        result = await self._make_request(messages, temperature=0.5, max_tokens=1000)
        if result and len(result) > 10:
            return result

        return text

    async def remove_duplicates(self, questions, language="ar"):
        """إزالة الأسئلة المتكررة باستخدام AI"""
        if not self.is_configured or len(questions) < 2:
            return questions

        questions_text = "\n".join(
            [f"{i+1}. {q.get('question_text', q.get('question', ''))}"
             for i, q in enumerate(questions)]
        )

        messages = [
            {
                "role": "system",
                "content": "Identify duplicate or very similar questions. "
                           "Return ONLY a JSON array of indices (0-based) to KEEP. "
                           "Remove duplicates.",
            },
            {"role": "user", "content": f"Questions:\n{questions_text}"},
        ]

        result = await self._make_request(messages, temperature=0.3, max_tokens=200)
        indices = self._extract_json(result)

        if indices and isinstance(indices, list):
            try:
                return [questions[i] for i in indices if i < len(questions)]
            except (IndexError, TypeError):
                pass

        return questions

    async def auto_generate_quiz(self, topic, num_questions=10, difficulty="medium", language="ar"):
        """الوضع التلقائي - إنشاء اختبار كامل"""
        questions = await self.generate_questions(
            topic, num_questions, difficulty, language
        )

        # إزالة التكرار
        if len(questions) > 3:
            questions = await self.remove_duplicates(questions, language)

        return {
            "title": f"{'اختبار' if language == 'ar' else 'Quiz'}: {topic[:50]}",
            "description": f"{'اختبار تم إنشاؤه تلقائياً عن' if language == 'ar' else 'Auto-generated quiz about'} {topic}",
            "category": "general",
            "questions": questions,
        }

    async def get_available_models(self):
        """الحصول على قائمة النماذج المتاحة"""
        if not self.is_configured:
            return []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    return []
        except Exception as e:
            logger.error(f"Get models error: {e}")
            return []

    def _validate_question(self, q):
        """التحقق من صحة بيانات السؤال"""
        if not isinstance(q, dict):
            return None

        question = q.get("question", "").strip()
        if not question or len(question) < 3:
            return None

        correct = q.get("correct", "a").lower().strip()
        if correct not in ("a", "b", "c", "d"):
            # محاولة إصلاح الإجابة
            option_a = q.get("option_a", "")
            for letter, key in [("a", "option_a"), ("b", "option_b"), ("c", "option_c"), ("d", "option_d")]:
                if q.get(key, "").lower().strip() == correct:
                    correct = letter
                    break
            else:
                correct = "a"

        return {
            "question": question,
            "type": q.get("type", "multiple_choice"),
            "option_a": q.get("option_a", "A") or "A",
            "option_b": q.get("option_b", "B") or "B",
            "option_c": q.get("option_c"),
            "option_d": q.get("option_d"),
            "correct": correct,
            "explanation": q.get("explanation", ""),
        }

    def _generate_fallback_questions(self, topic, num_questions, language):
        """أسئلة احتياطية عند عدم توفر AI"""
        questions = []
        for i in range(num_questions):
            if language == "ar":
                q = {
                    "question": f"سؤال {i + 1} عن {topic}",
                    "type": "multiple_choice",
                    "option_a": "الخيار أ",
                    "option_b": "الخيار ب",
                    "option_c": "الخيار ج",
                    "option_d": "الخيار د",
                    "correct": "a",
                    "explanation": f"هذا سؤال تجريبي عن {topic}. قم بإعداد OPENROUTER_API_KEY لتوليد أسئلة حقيقية.",
                }
            else:
                q = {
                    "question": f"Question {i + 1} about {topic}",
                    "type": "multiple_choice",
                    "option_a": "Option A",
                    "option_b": "Option B",
                    "option_c": "Option C",
                    "option_d": "Option D",
                    "correct": "a",
                    "explanation": f"Sample question about {topic}. Set OPENROUTER_API_KEY for real AI questions.",
                }
            questions.append(q)
        return questions

    def _generate_fallback_tf_questions(self, topic, num_questions, language):
        """أسئلة صح/خطأ احتياطية"""
        questions = []
        for i in range(num_questions):
            if language == "ar":
                q = {
                    "question": f"عبارة {i + 1} عن {topic}",
                    "type": "true_false",
                    "option_a": "صح",
                    "option_b": "خطأ",
                    "option_c": None,
                    "option_d": None,
                    "correct": "a",
                    "explanation": f"هذه عبارة تجريبية عن {topic}.",
                }
            else:
                q = {
                    "question": f"Statement {i + 1} about {topic}",
                    "type": "true_false",
                    "option_a": "True",
                    "option_b": "False",
                    "option_c": None,
                    "option_d": None,
                    "correct": "a",
                    "explanation": f"Sample statement about {topic}.",
                }
            questions.append(q)
        return questions