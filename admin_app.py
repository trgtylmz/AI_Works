import json
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

CONFIG_FILE = Path("config.json")

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    config = load_config()
    return templates.TemplateResponse("admin.html", {"request": request, "config": config})


@app.post("/update")
async def update(instructions: str = Form(...), samples: str = Form("[]")):
    config = {
        "instructions": instructions,
        "samples": json.loads(samples),
    }
    save_config(config)
    return RedirectResponse("/", status_code=303)
