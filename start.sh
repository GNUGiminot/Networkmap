#!/usr/bin/env bash
# NetworkMap — запуск на Linux/macOS
cd "$(dirname "$0")"
if [ ! -d venv ]; then
  echo "[NetworkMap] Создаю виртуальное окружение..."
  python3 -m venv venv
  venv/bin/pip install -r requirements.txt
fi
echo "[NetworkMap] Запуск на http://localhost:8790"
exec venv/bin/python -m uvicorn main:app --app-dir server --host 0.0.0.0 --port 8790
