# Проверка статуса сборки
Write-Host "📦 Проверка статуса сборки..." -ForegroundColor Cyan

if (Test-Path "build.log") {
    Write-Host "`n📄 Последние строки из build.log:" -ForegroundColor Yellow
    Get-Content build.log -Tail 20
    
    if (Select-String -Path build.log -Pattern "Successfully|Built" -Quiet) {
        Write-Host "`n✅ Сборка завершена!" -ForegroundColor Green
        Write-Host "`nЗапуск сервисов..." -ForegroundColor Cyan
        docker-compose up -d
    } elseif (Select-String -Path build.log -Pattern "error|failed" -Quiet) {
        Write-Host "`n❌ Ошибка сборки! Последние логи:" -ForegroundColor Red
        Get-Content build.log -Tail 50
    } else {
        Write-Host "`n⏳ Сборка еще идет..." -ForegroundColor Yellow
        Write-Host "Запустите этот скрипт снова через несколько минут" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ build.log не найден. Сборка не запущена." -ForegroundColor Red
    Write-Host "Запустите: docker-compose build > build.log 2>&1" -ForegroundColor Gray
}
