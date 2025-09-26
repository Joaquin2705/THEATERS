# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import models
from .routers import cinemas, salas

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Theaters Service", version="1.0.0")

# CORS (ajusta orígenes según necesites)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, específica tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(cinemas.router)
app.include_router(salas.router)

@app.get("/")
def health():
    return {"ok": True, "service": "theaters"}
