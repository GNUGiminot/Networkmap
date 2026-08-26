"""
NetworkMap — панель организации сетей.
Backend: FastAPI + SQLite + реальный ping-мониторинг + WebSocket.
Кроссплатформенно: Windows / Linux / macOS (ping через системную команду).
"""
import asyncio
import json
import platform
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
STATIC = BASE.parent / "static"
DATA = BASE.parent / "data"
CONFIGS = DATA / "configs"
DATA.mkdir(exist_ok=True)
CONFIGS.mkdir(exist_ok=True)
DB_PATH = DATA / "netmap.db"

PING_INTERVAL = 5          # секунд между циклами опроса
PING_TIMEOUT_MS = 1500     # таймаут одного ping
PING_CONCURRENCY = 25      # одновременных ping

IS_WINDOWS = platform.system() == "Windows"

# ----------------------------------------------------------------- база
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS kv (
            k TEXT PRIMARY KEY,
            v TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            comment TEXT DEFAULT '',
            path TEXT NOT NULL
        );
        """)


def get_state() -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT v FROM kv WHERE k='state'").fetchone()
    return json.loads(row["v"]) if row else None


def put_state(state: dict) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO kv(k, v) VALUES('state', ?) "
            "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            (json.dumps(state, ensure_ascii=False),),
        )


# ------------------------------------------------------------- мониторинг
# id устройства -> {"online": bool|None, "rtt": float|None, "ts": float}
STATUS: dict[str, dict] = {}
WS_CLIENTS: set[WebSocket] = set()


async def ping_host(ip: str) -> tuple[bool, float | None]:
    """Один ICMP-ping через системную команду. Без прав администратора."""
    if IS_WINDOWS:
        args = ["ping", "-n", "1", "-w", str(PING_TIMEOUT_MS), ip]
    else:
        args = ["ping", "-c", "1", "-W", str(max(1, PING_TIMEOUT_MS // 1000)), ip]
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=PING_TIMEOUT_MS / 1000 + 3)
    except (asyncio.TimeoutError, OSError):
        return False, None
    ok = proc.returncode == 0
    # Windows может вернуть 0 при "Destination host unreachable" — проверяем TTL
    if ok and IS_WINDOWS and b"TTL=" not in out.upper():
        ok = False
    rtt = None
    if ok:
        m = re.search(rb"[=<]\s*(\d+(?:[.,]\d+)?)\s*m", out, re.IGNORECASE)
        if m:
            rtt = float(m.group(1).replace(b",", b"."))
        else:  # локализованный вывод (например, "время=3мс" в cp866)
            m = re.search(rb"[=<]\s*(\d+)", out)
            rtt = float(m.group(1)) if m else None
    return ok, rtt


def monitored_devices(state: dict) -> list[dict]:
    devices = []
    for org in state.get("orgs", []):
        for d in org.get("devices", []):
            if d.get("monitored") and d.get("ip"):
                devices.append(d)
    return devices


async def monitor_loop() -> None:
    sem = asyncio.Semaphore(PING_CONCURRENCY)

    async def check(dev: dict) -> None:
        async with sem:
            ok, rtt = await ping_host(dev["ip"])
        STATUS[dev["id"]] = {"online": ok, "rtt": rtt, "ts": time.time()}

    while True:
        state = get_state()
        if state:
            devs = monitored_devices(state)
            alive_ids = {d["id"] for d in devs}
            for gone in set(STATUS) - alive_ids:
                STATUS.pop(gone, None)
            if devs:
                await asyncio.gather(*(check(d) for d in devs))
            await broadcast_status()
        await asyncio.sleep(PING_INTERVAL)


async def broadcast_status() -> None:
    if not WS_CLIENTS:
        return
    msg = json.dumps({"type": "status", "data": STATUS})
    dead = set()
    for ws in WS_CLIENTS:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.add(ws)
    WS_CLIENTS.difference_update(dead)


# ------------------------------------------------------------------- app
app = FastAPI(title="NetworkMap")


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    asyncio.create_task(monitor_loop())


@app.get("/api/state")
def api_get_state():
    return get_state() or {}


@app.put("/api/state")
async def api_put_state(payload: dict):
    if "orgs" not in payload:
        raise HTTPException(400, "Некорректное состояние: нет поля orgs")
    put_state(payload)
    return {"ok": True}


@app.get("/api/status")
def api_status():
    return STATUS


# --------- конфигурации устройств (файлы на диске, с версионированием)
@app.post("/api/devices/{device_id}/configs")
async def upload_config(device_id: str, file: UploadFile = File(...), comment: str = ""):
    safe_name = re.sub(r"[^\w.\-]+", "_", file.filename or "config.txt")
    folder = CONFIGS / re.sub(r"[^\w\-]+", "_", device_id)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = folder / f"{stamp}_{safe_name}"
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "Файл больше 10 МБ")
    path.write_bytes(content)
    uploaded_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO configs(device_id, filename, uploaded_at, comment, path) "
            "VALUES(?,?,?,?,?)",
            (device_id, safe_name, uploaded_at, comment, str(path)),
        )
        cfg_id = cur.lastrowid
    return {"id": cfg_id, "name": safe_name, "date": uploaded_at}


@app.get("/api/devices/{device_id}/configs")
def list_configs(device_id: str):
    with db() as conn:
        rows = conn.execute(
            "SELECT id, filename AS name, uploaded_at AS date, comment "
            "FROM configs WHERE device_id=? ORDER BY id DESC",
            (device_id,),
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/configs/{cfg_id}/download")
def download_config(cfg_id: int):
    with db() as conn:
        row = conn.execute("SELECT filename, path FROM configs WHERE id=?", (cfg_id,)).fetchone()
    if not row or not Path(row["path"]).exists():
        raise HTTPException(404, "Файл не найден")
    return FileResponse(row["path"], filename=row["filename"])


@app.delete("/api/configs/{cfg_id}")
def delete_config(cfg_id: int):
    with db() as conn:
        row = conn.execute("SELECT path FROM configs WHERE id=?", (cfg_id,)).fetchone()
        conn.execute("DELETE FROM configs WHERE id=?", (cfg_id,))
    if row:
        Path(row["path"]).unlink(missing_ok=True)
    return {"ok": True}


# ------------------------------------------------------------- WebSocket
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    WS_CLIENTS.add(ws)
    try:
        await ws.send_text(json.dumps({"type": "status", "data": STATUS}))
        while True:
            await ws.receive_text()  # держим соединение; клиент шлёт ping-кадры
    except WebSocketDisconnect:
        pass
    finally:
        WS_CLIENTS.discard(ws)


# статика — в самом конце, чтобы не перехватывала /api и /ws
app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8790)
