# Миграция Agents Service с Go на Python

## 📊 Сравнение

| Характеристика | Go версия | Python версия |
|----------------|-----------|---------------|
| **Язык** | Go 1.25 | Python 3.12+ |
| **Строк кода** | ~2000+ | ~800 |
| **Файлов** | 30+ | 15 |
| **Зависимости** | 40+ модулей | 10 модулей |
| **Время сборки** | Компиляция | Интерпретатор |
| **Асинхронность** | Горутины | asyncio |
| **gRPC** | grpc-go | grpcio |
| **Валидация** | Ручная | Pydantic |

## 🏗️ Архитектура

### Go версия (старая)
```
agents/
├── cmd/app/main.go
├── internal/
│   ├── service/agent_service.go
│   └── fetcher/
│       ├── grpc/
│       │   ├── server.go
│       │   └── client.go
│       └── providers/
│           ├── openrouter/openrouter.go
│           ├── gemini/gemini.go
│           ├── openai/openai.go
│           ├── claude/claude.go
│           ├── deepseek/deepseek.go
│           └── grok/grok.go
├── pkg/
│   ├── fetcher/grpc/
│   ├── models/agent.go
│   └── ...
├── proto/agents.proto
├── pb/
│   ├── agents.pb.go
│   └── agents_grpc.pb.go
├── go.mod
├── go.sum
└── Dockerfile
```

### Python версия (новая)
```
agents/
├── app/
│   ├── core/
│   │   ├── models.py              # Модели + базовый класс
│   │   ├── helpers.py             # Утилиты
│   │   └── agent_service.py       # Роутер запросов
│   ├── providers/
│   │   ├── openrouter.py          # OpenRouter с retry
│   │   ├── gemini.py              # Gemini
│   │   ├── openai_provider.py     # OpenAI
│   │   ├── claude.py              # Claude
│   │   ├── deepseek.py            # DeepSeek
│   │   └── grok.py                # Grok
│   ├── grpc/
│   │   ├── server.py              # gRPC сервер
│   │   └── client.py              # gRPC клиент
│   └── proto/
│       ├── agents.proto           # Proto-контракт
│       ├── agents_pb2.py          # Generated
│       └── agents_pb2_grpc.py     # Generated
├── main.py                        # Точка входа
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔄 Ключевые изменения

### 1. Модели данных

**Go:**
```go
type AgentRequest struct {
    Provider    string
    Model       string
    Prompt      string
    Tokens      map[string]interface{}
    MaxTokens   int
    Temperature float32
}
```

**Python:**
```python
class AgentRequest(BaseModel):
    provider: str
    model: str
    prompt: str
    tokens: Dict[str, str] = {}
    max_tokens: int = 4096
    temperature: float = 0.7
```

### 2. Интерфейс провайдера

**Go:**
```go
type AIProvider interface {
    Generate(ctx context.Context, prompt string, tokens map[string]interface{}) (string, error)
    Name() string
    IsConfigured() bool
}
```

**Python:**
```python
class BaseAIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt, tokens, max_tokens, temperature) -> str:
        pass
    
    @abstractmethod
    def name(self) -> str:
        pass
    
    def is_configured(self) -> bool:
        return True
```

### 3. Lazy Client Creation

**Go:**
```go
func (p *OpenAIProvider) getClient(tokens map[string]interface{}) (*openai.Client, error) {
    p.mu.Lock()
    defer p.mu.Unlock()
    if p.client != nil {
        return p.client, nil
    }
    apiKey := extractAPIKey(tokens)
    p.client = openai.NewClient(option.WithAPIKey(apiKey))
    return p.client, nil
}
```

**Python:**
```python
async def _get_client(self, tokens: Dict[str, Any]) -> AsyncOpenAI:
    async with self._lock:
        if self._client is not None:
            return self._client
        
        api_key = extract_api_key(tokens, self.KEY_NAMES)
        self._client = AsyncOpenAI(api_key=api_key)
        return self._client
```

### 4. Retry-логика (OpenRouter)

**Go:**
```go
for attempt := 0; attempt < 3; attempt++ {
    if attempt > 0 {
        time.Sleep(time.Duration(attempt) * 2 * time.Second)
    }
    response, err := client.Chat.Completions.New(ctx, params)
    if err == nil {
        return response.Choices[0].Message.Content, nil
    }
    if isTransient(err) {
        continue
    }
    return "", err
}
```

**Python:**
```python
for attempt in range(self.MAX_RETRIES):
    if attempt > 0:
        await asyncio.sleep(attempt * 2)
    
    try:
        response = await client.chat.completions.create(...)
        return response.choices[0].message.content
    except Exception as e:
        if self._is_transient_error(e):
            continue
        raise
```

### 5. gRPC Сервер

**Go:**
```go
func (s *Server) Generate(ctx context.Context, req *pb.GenerateRequest) (*pb.GenerateResponse, error) {
    resp, err := s.service.Generate(ctx, &models.AgentRequest{...})
    return &pb.GenerateResponse{...}, nil
}
```

**Python:**
```python
async def Generate(self, request, context):
    internal_request = AgentRequest(...)
    response = await self._agent_service.generate(internal_request)
    return agents_pb2.GenerateResponse(...)
```

## 🚀 Запуск

### Go версия
```bash
cd agents
go run cmd/app/main.go
```

### Python версия
```bash
cd agents
pip install -r requirements.txt
python main.py
```

## 🐳 Docker

### Go версия
```dockerfile
FROM golang:1.25-alpine
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o server cmd/app/main.go
CMD ["./server"]
```

### Python версия
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## ✅ Преимущества Python версии

1. **Меньше кода** — в 2.5 раза меньше строк
2. **Быстрее разработка** — не нужна компиляция
3. **Pydantic** — автоматическая валидация данных
4. **asyncio** — встроенная асинхронность
5. **Проще тестирование** — интерактивный режим
6. **Меньше зависимостей** — 10 вместо 40+
7. **Легче читать** — понятный синтаксис
8. **Быстрый старт** — не нужно знать Go

## ⚠️ Важно помнить

### API ключи per-request
Все провайдеры принимают API-ключ **в каждом запросе**, а не при инициализации:

```python
# Правильно ✅
response = await client.generate(
    provider="openrouter",
    prompt="...",
    tokens={"openrouter": "sk-or-v1-..."},  # Ключ здесь
)

# Неправильно ❌
# Ключи НЕ передаются в .env или конфиге провайдера
```

### Извлечение ключей
Каждый провайдер ищет ключ по своим именам:

| Провайдер | Имена ключей |
|-----------|--------------|
| OpenRouter | `openrouter`, `api_key`, `apiKey` |
| Gemini | `gemini`, `google` |
| OpenAI | `openai`, `api_key` |
| Claude | `claude`, `anthropic` |
| DeepSeek | `deepseek`, `api_key` |
| Grok | `grok`, `xai` |

### Proto файлы
После изменения `agents.proto` нужно перегенерировать код:

```bash
# PowerShell
.\generate-proto.ps1

# Или вручную
python -m grpc_tools.protoc -I app/proto --python_out=app/proto --grpc_python_out=app/proto app/proto/agents.proto
```

Затем исправить импорт в `agents_pb2_grpc.py`:
```python
# Было
import agents_pb2 as agents__pb2

# Стало
from . import agents_pb2 as agents__pb2
```

## 📚 Ссылки

- [README.md](./README.md) — полная документация
- [.env.example](./.env.example) — переменные окружения
- [Proto-контракт](./app/proto/agents.proto) — gRPC API
- [Dockerfile](./Dockerfile) — образ Docker

## 🎯 Следующие шаги

1. Обновить другие сервисы (Boss, Manager, Worker) для работы с Python Agents
2. Изменить docker-compose.yml для использования Python версии
3. Протестировать с реальными API ключами
4. Добавить unit-тесты
5. Настроить CI/CD
