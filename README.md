# myFirstApi — обращение к модели через OpenRouter

Учебный проект по мотивам занятия «API: как обращаться к модели напрямую».
Вместо прямого подключения к OpenAI здесь используется **OpenRouter** —
агрегатор, который даёт один ключ и один эндпоинт ко множеству моделей
(OpenAI, Anthropic, Google и др.).

## Чем отличается от урока

| В уроке (OpenAI Responses API) | В этом проекте (OpenRouter) |
|---|---|
| `client = OpenAI(api_key=...)` | `client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)` |
| `client.responses.create(...)` | `client.chat.completions.create(...)` |
| системный промпт через `instructions` | сообщение `{"role": "system", "content": ...}` |
| запрос через `input=` | сообщение `{"role": "user", "content": ...}` |
| ответ через `response.output_text` | `completion.choices[0].message.content` |
| токены `input_tokens` / `output_tokens` | `prompt_tokens` / `completion_tokens` / `total_tokens` |
| `model="gpt-5.2"` | slug с провайдером, например `openai/gpt-4o-mini` |

Клиентская библиотека остаётся той же — `openai`. OpenRouter совместим
с OpenAI SDK на уровне Chat Completions, поэтому меняется только способ
подключения и формат вызова.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка ключа

1. Зарегистрируйся на [openrouter.ai](https://openrouter.ai) и пополни баланс
   (либо используй бесплатные модели с суффиксом `:free` — они работают без оплаты).
2. Создай ключ: [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) → **Create Key**.
3. Скопируй файл `.env.example` в `.env` и вставь ключ:

```bash
cp .env.example .env
```

```env
OPENROUTER_API_KEY=скопированный_ключ
OPENROUTER_MODEL=openai/gpt-4o-mini
```

> Файл `.env` уже добавлен в `.gitignore` и не попадёт в репозиторий.

## Выбор модели

Модель задаётся в `.env` в переменной `OPENROUTER_MODEL` (или константой
`MODEL` в `main.py`). Slug-и моделей и цены смотри на
[openrouter.ai/models](https://openrouter.ai/models). Примеры:

- `openai/gpt-4o-mini` — недорогая и быстрая модель OpenAI;
- `anthropic/claude-3.5-sonnet` — сильна в коде и работе с текстом;
- `google/gemini-2.0-flash-exp:free` — бесплатный вариант для экспериментов.

## Запуск

```bash
python main.py
```

Программа запускает интерактивный чат в консоли: вводишь вопрос — получаешь
ответ. История диалога сохраняется, поэтому модель помнит контекст
(в массив `messages` добавляются роли `user` и `assistant`). Для выхода
введи `выход` или `exit`.

После каждого ответа выводится расход токенов и причина завершения
(`finish_reason`). Если хочется увидеть полную структуру ответа от API,
поставь в `main.py` флаг:

```python
PRINT_FULL_JSON = True
```

Тогда ответ будет печататься целиком через `json.dumps(completion.model_dump())`.

## Настройка поведения модели

В `main.py` можно менять:

- `SYSTEM_PROMPT` — системная инструкция (поведение и стиль модели);
- `TEMPERATURE` — 0 — строго и предсказуемо, выше 1 — креативнее;
- `MAX_TOKENS` — ограничение длины ответа.

## Структура проекта

```
myFirstApi/
├── main.py           # интерактивный чат с OpenRouter
├── .env              # твой ключ и модель (не попадает в git)
├── .env.example      # шаблон переменных
├── requirements.txt  # зависимости
├── .gitignore
└── README.md
```
