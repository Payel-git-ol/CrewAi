# Agents Service (Python Version)

Единый интерфейс ко всем LLM-провайдерам в системе CrewAI.

## 📖 Обзор

Agents Service — это **централизованный маршрутизатор** запросов к ИИ-провайдерам. Вместо того чтобы каждый сервис (Boss, Manager, Worker) самостоятельно подключался к OpenAI, Gemini и другим, они все обращаются к Agents через gRPC.

### Преимущества

- ✅ **Все провайдеры в одном месте** — легко добавить новый
- ✅ **Централизованная retry-логика** (особенно для OpenRouter)
- ✅ **Per-request токены** — API-ключи не хранятся на сервере
- ✅ **Единый интерфейс** независимо от провайдера
- ✅ **Асинхронная архитектура** на Python 3.12+
- ✅ **Lazy client creation** — клиенты создаются только при первом запросе

## 🏗️ Архитектура

```
Boss/Manager/Worker → gRPC → Agents Service → Provider SDK → LLM API
                            (Python)
```

### Поддерживаемые провайдеры

| Провайдер | SDK | Модель по умолчанию | Извлечение ключа |
|-----------|-----|---------------------|------------------|
| **OpenRouter** | `openai` (совместимый) | `qwen/qwen3.6-plus:free` | `openrouter`, `api_key`, `apiKey` |
| **Gemini** | `google-genai` | `gemini-2.5-flash` | `gemini`, `google` |
| **OpenAI** | `openai` | `gpt-4o` | `openai`, `api_key` |
| **Claude** | `anthropic` | `claude-opus-4-6` | `claude`, `anthropic` |
| **DeepSeek** | `openai` (совместимый) | `deepseek-chat` | `deepseek`, `api_key` |
| **Grok** | `openai` (совместимый) | `grok-3` | `grok`, `xai` |

## 📁 Структура проекта

```
agents/
├── app/
│   ├── core/
│   │   ├── models.py              # Pydantic модели и базовый класс провайдера
│   │   ├── helpers.py             # Утилиты (извлечение API ключей)
│   │   └── agent_service.py       # Роутер запросов к провайдерам
│   ├── providers/
│   │   ├── openrouter.py          # OpenRouter с retry-логикой
│   │   ├── gemini.py              # Google Gemini
│   │   ├── openai_provider.py     # OpenAI
│   │   ├── claude.py              # Anthropic Claude
│   │   ├── deepseek.py            # DeepSeek
│   │   └── grok.py                # xAI Grok
│   ├── grpc/
│   │   ├── server.py              # gRPC сервер (AgentsGRPCServicer)
│   │   └── client.py              # gRPC клиент для других сервисов
│   └── proto/
│       ├── agents.proto           # Proto-контракт
│       ├── agents_pb2.py          # Сгенерированный код
│       └── agents_pb2_grpc.py     # Сгенерированный gRPC код
├── main.py                        # Точка входа
├── requirements.txt               # Python зависимости
├── Dockerfile                     # Docker образ
├── .env.example                   # Пример переменных окружения
└── README.md                      # Этот файл
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Генерация gRPC кода (если изменили proto)

```bash
python -m grpc_tools.protoc -I app/proto --python_out=app/proto --grpc_python_out=app/proto app/proto/agents.proto
```

### 3. Запуск сервиса

```bash
# С настройками по умолчанию
python main.py

# Или с переменными окружения
export AGENTS_PORT=50053
python main.py
```

### 4. Использование Docker

```bash
docker build -t crewai-agents .
docker run -p 50053:50053 --env-file .env crewai-agents
```

## 🔌 Использование из других сервисов

### Python клиент

```python
from app.grpc.client import AgentsClient

client = AgentsClient(host="localhost", port=50053)

response = await client.generate(
    provider="openrouter",
    model="qwen/qwen3.6-plus:free",
    prompt="Напиши функцию для сортировки массива",
    tokens={"openrouter": "sk-or-v1-..."},
    max_tokens=2048,
    temperature=0.7,
)

print(response.content)
await client.close()
```

### Streaming

```python
async for chunk in client.generate_stream(
    provider="gemini",
    model="gemini-2.5-flash",
    prompt="Расскажи о Python",
    tokens={"gemini": "AIza..."},
):
    if chunk.done:
        break
    print(chunk.content, end="")
```

## 📋 Proto-контракт

```protobuf
service AgentService {
  rpc Generate(GenerateRequest) returns (GenerateResponse) {}
  rpc GenerateStream(GenerateRequest) returns (stream GenerateStreamChunk) {}
}

message GenerateRequest {
  string provider = 1;           // openrouter, gemini, openai, claude, deepseek, grok
  string model = 2;              // модель
  string prompt = 3;             // текст промпта
  map<string, string> tokens = 4; // API-ключи per-request
  int32 max_tokens = 5;
  float temperature = 6;
}

message GenerateResponse {
  string provider = 1;
  string model = 2;
  string content = 3;
  int32 tokens_used = 4;
  string error = 5;
  string error_code = 6;
}
```

## 🔑 Per-request токены

Все провайдеры принимают API-ключ **в каждом запросе** через поле `tokens`, а не при инициализации:

```python
tokens = {
    "openrouter": "sk-or-v1-...",  # для OpenRouter
    "gemini": "AIza...",            # для Gemini
    "openai": "sk-...",             # для OpenAI
    "claude": "sk-ant-...",         # для Claude
    "deepseek": "sk-...",           # для DeepSeek
    "grok": "xai-...",              # для Grok
}
```

Это позволяет:
- ✅ Не хранить API-ключи на сервере
- ✅ Переключать пользователей с разными ключами
- ✅ Безопасно работать в multi-tenant среде

## 🔄 Retry-логика (OpenRouter)

OpenRouter провайдер имеет встроенную retry-логику для transient-ошибков:

```python
MAX_RETRIES = 3
# Retry при: EOF, connection reset, timeout, 502, 503, 504
# НЕ retry при: auth error, rate limit, invalid request
```

## ➕ Добавление нового провайдера

1. Создайте файл: `app/providers/newprovider.py`

```python
from app.core.models import BaseAIProvider, ProviderConfig

class NewProvider(BaseAIProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
    
    async def generate(self, prompt, tokens, max_tokens, temperature):
        # Реализация
        pass
    
    def name(self):
        return "newprovider"
```

2. Зарегистрируйте в `main.py`:

```python
from app.providers.newprovider import NewProvider

newprovider = NewProvider(providers_config["newprovider"])
agent_service.register_provider("newprovider", newprovider)
```

## 🐛 Логирование

Логи пишутся в:
- **stderr** — уровень INFO+
- **logs/agents_YYYY-MM-DD.log** — уровень DEBUG+ с ротацией

## 🐳 Docker Compose

В корневом `docker-compose.yml`:

```yaml
services:
  agents:
    build: ./agents
    ports:
      - "50053:50053"
    env_file:
      - .env
    restart: unless-stopped
```

## 📝 Лицензия

MIT
