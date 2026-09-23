import json
from openai import AsyncOpenAI
from config import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)

async def generate_study_plan(raw_text: str, duration_days: int) -> dict:
    """Генерирует структурированный учебный план с тестами по материалу."""
    prompt = f"""
Ты — профессиональный ИИ-преподаватель и методолог.
На основе представленного ниже учебного материала составь четкий и структурированный план обучения на {duration_days} дней.

МАТЕРИАЛ:
{raw_text[:12000]}

Верни ответ СТРОГО в формате JSON со следующей структурой:
{{
  "title": "Название курса / темы",
  "days": [
    {{
      "day_number": 1,
      "title": "День 1. Название темы",
      "summary": "Краткая выжимка теории (3-4 понятных абзаца со всеми ключевыми понятиями)",
      "quiz": [
        {{
          "question": "Текст вопроса?",
          "options": ["Вариант 0", "Вариант 1", "Вариант 2"],
          "correct_option": 0,
          "explanation": "Почему этот вариант правильный"
        }}
      ]
    }}
  ]
}}

Для КАЖДОГО из {duration_days} дней сделай выжимку теории и ровно 2 вопроса для проверки знаний.
"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


async def ask_llm_question(day_summary: str, user_question: str) -> str:
    """Отвечает на вопрос пользователя по материалу конкретного дня."""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"Ты ИИ-репетитор. Ученик задает вопрос по теме со следующим материалом:\n\n{day_summary}\n\nОтвечай понятно, емко и по существу."
            },
            {"role": "user", "content": user_question}
        ]
    )
    return response.choices[0].message.content