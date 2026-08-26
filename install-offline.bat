@echo off
chcp 65001 >nul
rem ============================================================
rem  NetworkMap — офлайн-установка (без интернета)
rem  Все зависимости берутся из локальной папки wheels\
rem  Требуется только установленный Python 3.10+ (64-bit)
rem ============================================================
cd /d "%~dp0"

echo.
echo [NetworkMap] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден в PATH.
    echo Установите Python 3.10+ с python.org и поставьте галочку "Add to PATH".
    pause
    exit /b 1
)
python --version

if not exist wheels\ (
    echo ОШИБКА: папка wheels\ не найдена рядом со скриптом.
    echo Скопируйте проект целиком, включая папку wheels.
    pause
    exit /b 1
)

echo.
echo [NetworkMap] Создаю виртуальное окружение venv...
if exist venv\ (
    echo Окружение уже существует — пропускаю создание.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ОШИБКА: не удалось создать виртуальное окружение.
        pause
        exit /b 1
    )
)

echo.
echo [NetworkMap] Устанавливаю зависимости из wheels\ (без интернета)...
venv\Scripts\python -m pip install --no-index --find-links wheels -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: установка зависимостей не удалась.
    echo Проверьте, что версия Python совместима (wheels собраны под Python 3.13, 64-bit Windows).
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Установка завершена успешно!
echo  Запуск сервера: start.bat  (адрес: http://localhost:8790)
echo ============================================================
pause
