"""
Пример из урока "API: как обращаться к модели напрямую",
переделанный под подключение к OpenRouter.

OpenRouter — это агрегатор, совместимый с OpenAI SDK, поэтому мы
используем ту же библиотеку `openai`, но с другим `base_url`.
Главное отличие от урока: OpenRouter работает через Chat Completions
(`client.chat.completions.create`), а не через Responses API.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# --- Настройки (правь под себя) -------------------------------------------------

# Загружаем .env до чтения переменных ниже. override=True — чтобы значения из
# .env имели приоритет над уже заданными переменными окружения.
load_dotenv(override=True)

# Модель. Можно задать в .env (OPENROUTER_MODEL) или прямо здесь.
# Полный список slug-ов моделей: https://openrouter.ai/models
# Примеры:
#   "openai/gpt-4o-mini"
#   "anthropic/claude-3.5-sonnet"
#   "google/gemini-2.0-flash-exp:free"   (бесплатная модель, суффикс ":free")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# Системный промпт (аналог параметра `instructions` из урока).
SYSTEM_PROMPT = (
    "Ты — дружелюбный помощник. Отвечай на русском языке, "
    "объясняй просто, как преподаватель для новичков, "
    "и по возможности приводи короткие примеры."
)

TEMPERATURE = 0.7   # 0 — строго и предсказуемо, выше 1 — креативнее
MAX_TOKENS = 800    # ограничение длины ответа

# Отладочный режим: печатать полный JSON-ответ от API.
PRINT_FULL_JSON = False

# --- Подготовка клиента ---------------------------------------------------------

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit(
        "Не найден OPENROUTER_API_KEY.\n"
        "Создай файл .env по образцу .env.example и вставь свой ключ "
        "из https://openrouter.ai/settings/keys"
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    # Необязательные заголовки для статистики приложения на openrouter.ai.
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-OpenRouter-Title": "myFirstApi",
    },
)


def ask_model(messages):
    """Отправляет историю сообщений модели и возвращает объект ответа."""
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )


def print_usage(completion):
    """Печатает расход токенов и причину завершения генерации."""
    usage = completion.usage
    if usage is not None:
        print(
            f"[токены] запрос: {usage.prompt_tokens}, "
            f"ответ: {usage.completion_tokens}, "
            f"всего: {usage.total_tokens}"
        )
    finish_reason = completion.choices[0].finish_reason
    if finish_reason == "length":
        print("[!] Ответ оборвался: достигнут лимит max_tokens.")
    print(f"[finish_reason] {finish_reason}")


def main():
    print(f"Модель: {MODEL}")
    print("Введите 'выход' или 'exit', чтобы завершить диалог.\n")

    # История диалога: системная инструкция + реплики (user / assistant).
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            question = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"выход", "exit", "quit"}:
            break
        if not question:
            continue

        messages.append({"role": "user", "content": question})

        try:
            completion = ask_model(messages)
        except Exception as error:  # noqa: BLE001 — учебный пример
            print(f"\n[ошибка] Не удалось получить ответ: {error}\n")
            # Убираем неудачную реплику, чтобы не ломать историю.
            messages.pop()
            continue

        answer = completion.choices[0].message.content
        print(f"\nМодель: {answer}\n")

        # Сохраняем ответ в историю, чтобы модель помнила контекст.
        messages.append({"role": "assistant", "content": answer})

        print_usage(completion)

        if PRINT_FULL_JSON:
            print("\n--- Полный JSON-ответ ---")
            print(json.dumps(completion.model_dump(), indent=2, ensure_ascii=False))

        print()

    print("Диалог завершён.")


if __name__ == "__main__":
    main()
