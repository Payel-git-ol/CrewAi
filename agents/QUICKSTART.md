# 🚀 Быстрый старт - Agents Service (Python)

## 1️⃣ Установка зависимостей

```bash
cd agents
pip install -r requirements.txt
```

## 2️⃣ Настройка переменных окружения (опционально)

```bash
# Скопируйте .env.example в .env
copy .env.example .env

# Отредактируйте .env при необходимости
# По умолчанию все настроено на модели по умолчанию
```

## 3️⃣ Запуск сервиса

### Вариант A: Прямой запуск

```bash
python main.py
```

Ожидаемый вывод:
```
✅ Registered AI provider: openrouter
✅ Registered AI provider: gemini
✅ Registered AI provider: openai
✅ Registered AI provider: claude
✅ Registered AI provider: deepseek
✅ Registered AI provider: grok
✅ Available AI providers: ['openrouter', 'gemini', 'openai', 'claude', 'deepseek', 'grok']
🌐 Starting gRPC server on port 50053
✅ Agents gRPC server starting on port 50053
✅ Agents gRPC server is running on [::]:50053
```

### Вариант B: Docker

```bash
# Сборка
docker build -t crewai-agents .

# Запуск
docker run -p 50053:50053 --env-file .env crewai-agents
```

## 4️⃣ Тестирование (из других сервисов)

### Python клиент

```python
import sys
sys.path.insert(0, 'путь/к/agents')

from app.grpc.client import AgentsClient

async def test():
    client = AgentsClient(host="localhost", port=50053)
    
    response = await client.generate(
        provider="openrouter",
        model="qwen/qwen3.6-plus:free",
        prompt="Напиши hello world на Python",
        tokens={"openrouter": "ВАШ_OPENROUTER_KEY"},
        max_tokens=100,
        temperature=0.7,
    )
    
    print(response.content)
    await client.close()
```

## 5️⃣ Проверка работоспособности

```bash
# Запустить тесты
python test_agents.py
```

## 🔧 Перегенерация Proto файлов

Если изменили `app/proto/agents.proto`:

### PowerShell
```bash
.\generate-proto.ps1
```

### Ручной способ
```bash
python -m grpc_tools.protoc -I app/proto --python_out=app/proto --grpc_python_out=app/proto app/proto/agents.proto
```

**ВАЖНО:** После генерации исправить в `agents_pb2_grpc.py`:
```python
# Заменить
import agents_pb2 as agents__pb2
# На
from . import agents_pb2 as agents__pb2
```

## 📁 Структура проекта

```
agents/
├── app/
│   ├── core/           # Основные компоненты
│   │   ├── models.py
│   │   ├── helpers.py
│   │   └── agent_service.py
│   ├── providers/      # LLM провайдеры
│   │   ├── openrouter.py
│   │   ├── gemini.py
│   │   ├── openai_provider.py
│   │   ├── claude.py
│   │   ├── deepseek.py
│   │   └── grok.py
│   ├── grpc/           # gRPC сервер и клиент
│   │   ├── server.py
│   │   └── client.py
│   └── proto/          # Proto контракты
│       └── agents.proto
├── main.py             # Точка входа
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md           # Полная документация
└── MIGRATION.md        # Руководство по миграции
```

## 🎯 Поддерживаемые провайдеры

| Провайдер | Ключ в tokens | Модель по умолчанию |
|-----------|---------------|---------------------|
| OpenRouter | `openrouter` | qwen/qwen3.6-plus:free |
| Gemini | `gemini` | gemini-2.5-flash |
| OpenAI | `openai` | gpt-4o |
| Claude | `claude` | claude-opus-4-6 |
| DeepSeek | `deepseek` | deepseek-chat |
| Grok | `grok` | grok-3 |

## ⚡ Ключевые особенности

✅ **Per-request токены** - API-ключи передаются в каждом запросе, не хранятся на сервере
✅ **Lazy client creation** - клиенты создаются только при первом запросе
✅ **Retry-логика** - OpenRouter автоматически повторяет запросы при transient-ошибках
✅ **Асинхронность** - все операции асинхронные через asyncio
✅ **Валидация** - Pydantic автоматически валидирует все данные

## 🐛 Troubleshooting

### Ошибка импорта protobuf
```bash
# Перегенерировать proto файлы
python -m grpc_tools.protoc -I app/proto --python_out=app/proto --grpc_python_out=app/proto app/proto/agents.proto

# Исправить импорт в agents_pb2_grpc.py
# Заменить: import agents_pb2 as agents__pb2
# На: from . import agents_pb2 as agents__pb2
```

### Порт уже используется
```bash
# Изменить порт в .env
AGENTS_PORT=50054
```

### Missing API key
```
# Это нормально - ключи передаются per-request
# Ошибка появится только при реальном запросе без ключа
```

## 📚 Документация

- [README.md](./README.md) - Полная документация
- [MIGRATION.md](./MIGRATION.md) - Миграция с Go на Python
- [.env.example](./.env.example) - Все настройки

## 🤝 Интеграция с другими сервисами

Сервис полностью совместим с существующими Boss, Manager и Worker сервисами.
gRPC контракт остался неизменным - изменилась только внутренняя реализация.

Для интеграции обновите docker-compose.yml:

```yaml
services:
  agents:
    build: ./agents  # Теперь это Python проект
    ports:
      - "50053:50053"
    env_file:
      - .env
    restart: unless-stopped
```
