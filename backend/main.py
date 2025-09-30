from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import items, mentions
from backend.init_db import init_db

app = FastAPI(title="AI Matome API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(mentions.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
