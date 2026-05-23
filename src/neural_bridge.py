#!/usr/bin/env python3
"""Neural Chan Web Bridge — serves web UI + WebSocket API for iPhone access."""
import asyncio, json, os, sys, subprocess, threading, time
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    import uvicorn
except ImportError:
    print("Installing fastapi + uvicorn...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "websockets"])
    from fastapi import FastAPI, WebSocket
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from neural_conversation_v2 import NeuralConversationV2
    from system_monitor import SystemMonitor
    from web_learner import WebLearner
    from memory_exporter import MemoryExporter
except Exception as e:
    print(f"[WARN] Could not import Neural Chan modules: {e}")
    NeuralConversationV2 = None
    SystemMonitor = None
    WebLearner = None
    MemoryExporter = None

app = FastAPI(title="Neural Chan Bridge")
BRAIN = None
MONITOR = None
LEARNER = None
EXPORTER = None

def init_brain():
    global BRAIN, MONITOR, LEARNER, EXPORTER
    if NeuralConversationV2:
        MONITOR = SystemMonitor() if SystemMonitor else None
        LEARNER = WebLearner() if WebLearner else None
        BRAIN = NeuralConversationV2(system_monitor=MONITOR, web_learner=LEARNER)
        if MONITOR:
            MONITOR.start()
    if MemoryExporter:
        EXPORTER = MemoryExporter()

@app.on_event("startup")
async def startup():
    init_brain()

@app.get("/")
async def root():
    html_path = Path(__file__).parent / "neural_web.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return {"status": "Neural Chan Bridge running", "brain": BRAIN is not None}

@app.get("/api/status")
async def status():
    if not BRAIN:
        return {"brain": False, "uptime": "0s"}
    stats = BRAIN.get_stats()
    latest = MONITOR.get_latest() if MONITOR else {}
    return {
        "brain": True,
        "proficiency": stats.get("proficiency", 0),
        "words": stats.get("words_learned", 0),
        "conversations": stats.get("conversations", 0),
        "mood": stats.get("mood", "Calm"),
        "cpu_pct": latest.get("cpu_percent", 0),
        "mem_pct": latest.get("mem_percent", 0),
        "uptime": "active"
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "connected", "msg": "Neural Chan Web Bridge active"})
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except:
                msg = {"cmd": "chat", "text": raw}
            cmd = msg.get("cmd", "chat")
            if cmd == "chat":
                text = msg.get("text", "")
                if BRAIN:
                    result = BRAIN.respond(text)
                    await ws.send_json({
                        "type": "response",
                        "text": result["response"],
                        "intent": result["intent"],
                        "mood": result["mood"],
                        "proficiency": result["proficiency"],
                        "words_learned": result["total_words"],
                        "new_words": result.get("new_words_learned", [])
                    })
                else:
                    await ws.send_json({"type": "response", "text": f"Echo: {text}", "mood": "Calm"})
            elif cmd == "detect":
                await ws.send_json({"type": "event", "msg": "Detection scan triggered", "mood": "Working"})
            elif cmd == "auto":
                await ws.send_json({"type": "event", "msg": "Auto mode toggled", "mood": "Working"})
            elif cmd == "stop":
                await ws.send_json({"type": "event", "msg": "Emergency stop", "mood": "Concerned"})
            elif cmd == "stats":
                if BRAIN:
                    s = BRAIN.get_stats()
                    await ws.send_json({"type": "stats", "data": s})
                else:
                    await ws.send_json({"type": "stats", "data": {}})
            elif cmd == "sysinfo":
                if MONITOR:
                    latest = MONITOR.get_latest()
                    await ws.send_json({"type": "sysinfo", "data": latest or {}})
                else:
                    await ws.send_json({"type": "sysinfo", "data": {}})
            elif cmd == "export":
                if EXPORTER:
                    files = EXPORTER.export_all()
                    await ws.send_json({"type": "export", "files": files})
                else:
                    await ws.send_json({"type": "export", "files": []})
            elif cmd == "search":
                query = msg.get("query", "")
                if LEARNER:
                    result = LEARNER.search_and_learn(query)
                    await ws.send_json({"type": "search", "result": result})
                else:
                    await ws.send_json({"type": "search", "result": {"query": query, "summary": "Web learner offline"}})
            else:
                await ws.send_json({"type": "error", "msg": f"Unknown cmd: {cmd}"})
    except Exception as e:
        print(f"[WS] Client disconnected: {e}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5757
    print(f"[Neural Chan Bridge] http://0.0.0.0:{port}")
    print(f"[Neural Chan Bridge] Place neural_web.html in same folder")
    uvicorn.run(app, host="0.0.0.0", port=port)
