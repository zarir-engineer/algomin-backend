from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path


app = FastAPI()

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    # allow scripts/images from same origin, and WS on port 46630
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "connect-src 'self' ws://127.0.0.1:46630; "
        "script-src 'self'; "
        "img-src 'self';"
    )
    return response

# serve your frontend (if you have a `static/` folder)
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    html = (Path(__file__).parent / "templates/index.html").read_text()
    return HTMLResponse(html)

# include your API router after the CSP middleware!
from src.algomin.api import router
app.include_router(router)
