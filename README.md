# NetworkMap — панель организации сетей

Визуальный редактор и монитор сетей организации: интерактивное полотно
(в стиле n8n), устройства с полными карточками (IP, инвентарные и серийные
номера), несколько организаций, пользователи с правами, разграничение
доступа, валидация правил построения сетей, **реальный ping-мониторинг**
с живыми статусами и печать отчётов на A4.

<img width="1906" height="900" alt="image" src="https://github.com/user-attachments/assets/394e225d-d63d-4a24-876e-e95eb52c0187" />

<img width="1910" height="905" alt="image" src="https://github.com/user-attachments/assets/3f2a8a73-d26b-401b-bc60-bd19354ba5bf" />

<img width="1904" height="630" alt="image" src="https://github.com/user-attachments/assets/cde48c62-584b-4c91-9974-2b7f1e5e7558" />

## Возможности

- 🗺 Полотно: drag-and-drop устройств, связи (медь/оптика/Wi-Fi/VPN),
  сети и вложенные сегменты с CIDR/VLAN, зум и панорамирование.
- 🏢 Несколько организаций, у каждой свои сети, устройства и пользователи.
- 🖥 20+ типов устройств (АРМ, серверы, CRM, СУБД, камеры, ИБП…) +
  создание собственных типов; фильтры и поиск в палитре.
- 📋 Карточка устройства: сеть (IP/маска/шлюз/DNS/VLAN/MAC/порты),
  инвентаризация (вендор, модель, серийный №, инвентарный №, МОЛ, статус),
  пользователи и уровень доступа, конфигурации.
- 👥 Справочник пользователей: должность, роль, доступ в интернет;
  привязка к АРМ/серверам/принтерам.
- 🔒 Разграничение доступа на устройство и на сегмент.
- ✅ Валидация: конфликты IP, IP вне подсети, два DHCP, петли L2,
  вложенность CIDR, устройство напрямую в интернете и др.
- 📡 Реальный мониторинг: сервер пингует устройства каждые 5 секунд,
  статусы приходят в браузер по WebSocket; упавшие узлы подсвечиваются.
- 📎 Конфигурации устройств хранятся на сервере с версионированием
  (каждая загрузка — новый файл с меткой времени).
- 🖨 Печать A4: схема сети, инвентаризация, матрица доступов,
  сводка по устройству. Экспорт/импорт JSON.

## Запуск

Требуется Python 3.10+.

**Windows:** двойной клик по `start.bat`
**Linux/macOS:** `chmod +x start.sh && ./start.sh`

### Офлайн-установка (без интернета)

Все зависимости уже скачаны в папку `wheels/` (под Windows x64 / Python 3.13).
На машине без интернета достаточно Python 3.13 (64-bit):

1. Скопируйте папку проекта целиком (включая `wheels/`, `venv/` копировать не нужно).
2. Запустите `install-offline.bat` — окружение будет создано и зависимости
   установятся локально из `wheels/` (`pip --no-index --find-links wheels`).
3. Запуск как обычно: `start.bat` (он тоже умеет ставить офлайн, если
   `venv/` ещё нет, а `wheels/` рядом).

Для Linux/macOS: скачайте wheels на машине с той же ОС и версией Python
(`pip download -r requirements.txt -d wheels`), затем `install-offline.sh`.
Скрипты сохранены в UTF-8 (`chcp 65001`), кириллица в консоли отображается корректно.

Откройте http://localhost:8790 — при первом запуске будет создана
стартовая карта. Данные хранятся в `data/netmap.db` (SQLite),
файлы конфигураций — в `data/configs/`.

Для доступа с других компьютеров сети: сервер слушает `0.0.0.0`,
достаточно открыть `http://<ip-сервера>:8790` (разрешите порт в брандмауэре).

## Структура

```
networkmap/
├─ server/main.py      # FastAPI: REST API, WebSocket, ping-монитор
├─ static/index.html   # весь клиент (SVG-полотно, без сборки)
├─ data/               # создаётся автоматически: netmap.db, configs/
├─ requirements.txt
├─ start.bat / start.sh
└─ README.md
```

## API (кратко)

| Метод | Путь | Назначение |
|---|---|---|
| GET/PUT | `/api/state` | вся карта (все организации) |
| GET | `/api/status` | текущие статусы ping |
| POST | `/api/devices/{id}/configs` | загрузить конфиг (multipart) |
| GET | `/api/configs/{id}/download` | скачать конфиг |
| DELETE | `/api/configs/{id}` | удалить конфиг |
| WS | `/ws` | пуш статусов мониторинга |

## Примечания

- Ping выполняется системной командой — права администратора не нужны.
- Мониторинг видит только те устройства, у которых заполнен IP и включён
  флажок «Мониторить»; узел «Интернет/WAN» по умолчанию не пингуется.
- Прототип-предшественник (без сервера) лежит в
  `../панель управления ссылками/network-map/demo.html`.
  
 by Krainev and AI
# Networkmap

ENG

# NetworkMap — Network Organization Panel

Visual editor and network monitor for the organization: interactive canvas (n8n style), devices with full cards (IP, inventory and serial numbers), multiple organizations, users with permissions, access control, validation of network building rules, real ping monitoring with live statuses, and A4 report printing.

## Features
🗺 **Canvas**: drag-and-drop devices, connections (copper/fiber/Wi-Fi/VPN), networks and nested segments with CIDR/VLAN, zoom and pan.
🏢 **Multiple organizations**: each has its own networks, devices, and users.
🖥 **20+ device types** (Workstations, servers, CRM, DBMS, cameras, UPS, etc.) + creation of custom types; filters and search in the palette.
📋 **Device card**: network (IP/mask/gateway/DNS/VLAN/MAC/ports), inventory (vendor, model, serial #, inventory #, responsible person, status), users and access level, configurations.
👥 **User directory**: position, role, internet access; linked to workstations/servers/printers.
🔒 **Access control**: per device and per segment.
✅ **Validation**: IP conflicts, IP outside subnet, dual DHCP, L2 loops, CIDR nesting, device directly on the internet, etc.
📡 **Real monitoring**: server pings devices every 5 seconds, statuses are pushed to the browser via WebSocket; failed nodes are highlighted.
📎 **Device configurations** are stored on the server with versioning (each upload creates a new file with a timestamp).
🖨 **A4 Printing**: network diagram, inventory, access matrix, device summary. JSON export/import.

## Launch
Requires Python 3.10+.
Windows: double-click `start.bat`
Linux/macOS: `chmod +x start.sh && ./start.sh`

## Offline Installation (no internet)
All dependencies are already downloaded to the `wheels/` folder (for Windows x64 / Python 3.13).
On an offline machine, Python 3.13 (64-bit) is sufficient:
1. Copy the entire project folder (including `wheels/`, no need to copy `venv/`).
2. Run `install-offline.bat` — the environment will be created and dependencies installed locally from `wheels/` (`pip --no-index --find-links wheels`).
3. Launch as usual: `start.bat` (it also handles offline installation if `venv/` is missing but `wheels/` is nearby).

For Linux/macOS: download wheels on a machine with the same OS and Python version (`pip download -r requirements.txt -d wheels`), then run `install-offline.sh`.

Scripts are saved in UTF-8 (`chcp 65001`), Cyrillic displays correctly in the console.

Open `http://localhost:8790` — on the first run, a starter map will be created. Data is stored in `data/netmap.db` (SQLite), configuration files in `data/configs/`.

For access from other computers on the network: the server listens on `0.0.0.0`, just open `http://<server-ip>:8790` (allow the port in the firewall).

## Structure
```text
networkmap/
├─ server/main.py      # FastAPI: REST API, WebSocket, ping monitor
├─ static/index.html   # entire client (SVG canvas, no build)
├─ data/               # created automatically: netmap.db, configs/
├─ requirements.txt
├─ start.bat / start.sh
└─ README.md
```

## API (briefly)
| Method | Path | Purpose |
| --- | --- | --- |
| GET/PUT | `/api/state` | entire map (all organizations) |
| GET | `/api/status` | current ping statuses |
| POST | `/api/devices/{id}/configs` | upload config (multipart) |
| GET | `/api/configs/{id}/download` | download config |
| DELETE | `/api/configs/{id}` | delete config |
| WS | `/ws` | push monitoring statuses |

## Notes
* Ping is executed via system command — administrator rights are not required.
* Monitoring only sees devices that have an IP filled in and the "Monitor" flag enabled; the "Internet/WAN" node is not pinged by default.
* The predecessor prototype (without a server) is located at `../link-management-panel/network-map/demo.html`.

*by Krainev and AI*
