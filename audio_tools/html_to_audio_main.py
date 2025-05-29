# tools/main.py
from fastapi import FastAPI
from routes import html_to_audio_api

app = FastAPI()
app.include_router(html_to_audio_api.router)
