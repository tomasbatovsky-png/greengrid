from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    stats = {"nodes_online": 0, "jobs_running": 0}
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})

@app.websocket("/ws/lease")
async def lease(ws: WebSocket):
    await ws.accept()
    job = {"job_id": "demo1", "kind": "python", "code": "print(sum(range(1000)))"}
    await ws.send_json(job)
    result = await ws.receive_json()
    print("Received result:", result)
    await ws.close()
