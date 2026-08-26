@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist venv (
    echo [NetworkMap] Создаю виртуальное окружение...
    python -m venv venv || (echo ОШИБКА: Python не найден. Установите Python 3.10+ и добавьте в PATH. & pause & exit /b 1)
    if exist wheels\ (
        echo [NetworkMap] Устанавливаю зависимости офлайн из wheels\...
        venv\Scripts\python -m pip install --no-index --find-links wheels -r requirements.txt
    ) else (
        echo [NetworkMap] Устанавливаю зависимости из интернета...
        venv\Scripts\python -m pip install -r requirements.txt
    )
)

echo [NetworkMap] Запуск сервера на http://localhost:8790
echo [NetworkMap] Браузер откроется автоматически, как только сервер будет готов.
echo [NetworkMap] Не закрывайте это окно — в нём работает сервер. Для остановки нажмите Ctrl+C.
echo.

rem Ждём готовности порта и открываем браузер (фоновый процесс, пока сервер запускается)
start "" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0open-when-ready.ps1"

venv\Scripts\python -m uvicorn main:app --app-dir server --host 0.0.0.0 --port 8790

echo.
echo [NetworkMap] Сервер остановлен.
pause
