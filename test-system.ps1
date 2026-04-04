# Тестирование CrewAI системы

Write-Host "🧪 Тестирование CrewAI системы..." -ForegroundColor Cyan
Write-Host ""

# 1. Проверка Docker контейнеров
Write-Host "1️⃣  Проверка контейнеров:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 2. Проверка PostgreSQL
Write-Host "2️⃣  Проверка PostgreSQL:" -ForegroundColor Yellow
docker exec crewai-postgres pg_isready
Write-Host ""

# 3. Проверка gRPC портов
Write-Host "3️⃣  Проверка портов:" -ForegroundColor Yellow
$ports = @(
    @("Boss", "50051"),
    @("Manager", "50052"),
    @("Agents", "50053"),
    @("Merger", "50054"),
    @("ApiGateway", "3111")
)

foreach ($port in $ports) {
    $name = $port[0]
    $num = $port[1]
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", [int]$num)
        Write-Host "  ✅ $name (порт $num) - доступен" -ForegroundColor Green
        $tcp.Close()
    } catch {
        Write-Host "  ❌ $name (порт $num) - НЕ доступен" -ForegroundColor Red
    }
}
Write-Host ""

# 4. Проверка HTTP API
Write-Host "4️⃣  Проверка Apigateway (HTTP):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3111/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  ✅ Apigateway отвечает: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Apigateway: $_" -ForegroundColor Yellow
}
Write-Host ""

# 5. Логи Agents (Python)
Write-Host "5️⃣  Статус Python Agents:" -ForegroundColor Yellow
docker logs crewai-agents --tail 5 2>&1 | ForEach-Object {
    if ($_ -match "✅") { Write-Host "  $_" -ForegroundColor Green }
    elseif ($_ -match "ERROR|error") { Write-Host "  $_" -ForegroundColor Red }
    else { Write-Host "  $_" -ForegroundColor Gray }
}
Write-Host ""

# 6. Логи Boss
Write-Host "6️⃣  Статус Boss:" -ForegroundColor Yellow
docker logs crewai-boss --tail 3 2>&1 | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
}
Write-Host ""

Write-Host "✅ Тестирование завершено!" -ForegroundColor Green
