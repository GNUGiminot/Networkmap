#!/usr/bin/env bash
# ============================================================
#  NetworkMap — офлайн-установка (без интернета) для Linux/macOS
#  ВНИМАНИЕ: wheels в комплекте собраны под Windows x64 / Python 3.13.
#  Для Linux скачайте их на машине с интернетом той же ОС/версии Python:
#     pip download -r requirements.txt -d wheels
#  и перенесите папку wheels сюда.
# ============================================================
set -e
cd "$(dirname "$0")"

command -v python3 >/dev/null || { echo "ОШИБКА: python3 не найден"; exit 1; }
[ -d wheels ] || { echo "ОШИБКА: папка wheels/ не найдена"; exit 1; }

if [ ! -d venv ]; then
  echo "[NetworkMap] Создаю виртуальное окружение..."
  python3 -m venv venv
fi

echo "[NetworkMap] Устанавливаю зависимости из wheels/ (без интернета)..."
venv/bin/python -m pip install --no-index --find-links wheels -r requirements.txt

echo "Установка завершена. Запуск: ./start.sh (http://localhost:8790)"
