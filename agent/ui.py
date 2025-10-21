import flet as ft
import asyncio, json, websockets, threading, subprocess, sys

BACKEND_WS = "ws://localhost:8000/ws/lease"

def run_agent_loop(log):
    async def loop():
        try:
            async with websockets.connect(BACKEND_WS) as ws:
                msg = await ws.recv()
                job = json.loads(msg)
                if job.get("kind") == "python":
                    code = job["code"]
                    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    out, err = p.communicate(timeout=30)
                    result = {"job_id": job["job_id"], "result": {"stdout": out, "stderr": err, "rc": p.returncode}}
                else:
                    result = {"job_id": job["job_id"], "result": {"stderr": "unsupported", "rc": 1}}
                await ws.send(json.dumps(result))
                log.value += f"Sent result for {job['job_id']}\n"
                log.update()
        except Exception as e:
            log.value += f"Agent error: {e}\n"; log.update()
    asyncio.run(loop())

def main(page: ft.Page):
    page.title = "GreenGrid Agent"
    log = ft.Text(value="Agent log...\n", selectable=True)
    start_btn = ft.ElevatedButton("Start", on_click=lambda e: threading.Thread(target=run_agent_loop, args=(log,), daemon=True).start())
    page.add(start_btn, log)

ft.app(target=main)
