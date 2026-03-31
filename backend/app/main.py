from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .database import engine, Base
from .routers import rsvp, admin, auth
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea tabelle se non esistono
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Wedding RSVP API",
    description="API per la gestione delle conferme di partecipazione al matrimonio",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mauvale-wedding-frontend.onrender.com",
        "http://localhost",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(rsvp.router, prefix="/api/rsvp", tags=["RSVP"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "couple": settings.COUPLE_NAME}
