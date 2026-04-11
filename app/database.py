# ================================
# IMPORTACIONES
# ================================
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


# ================================
# CONFIGURACIÓN DE BASE DE DATOS
# ================================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está definida")


# ================================
# ENGINE DE SQLALCHEMY
# ================================
# Hardening:
# - pool_pre_ping: detecta conexiones muertas
# - pool_size / max_overflow: mejor manejo concurrente
# - pool_recycle: evita conexiones viejas
# - pool_timeout: corta si el pool está saturado
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    Entrega una sesión por request y la cierra al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()