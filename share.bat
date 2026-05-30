@echo off
chcp 65001 >nul
echo ========================================
echo   FinRate — публикация через ngrok
echo ========================================
echo.
echo 1. Убедитесь, что сайт уже запущен: python run.py
echo 2. Сейчас откроется публичная ссылка...
echo.

where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] ngrok не найден!
    echo Скачайте: https://ngrok.com/download
    echo После установки: ngrok config add-authtoken ВАШ_ТОКЕН
    pause
    exit /b 1
)

echo Запуск туннеля на порт 5000...
echo Скопируйте ссылку https://....ngrok-free.app и отправьте кому нужно.
echo.
ngrok http 5000
