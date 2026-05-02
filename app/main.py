import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.database import Base, engine
from app import models
from app.routes import auth, leads
from app.rate_limiter import limiter

# =========================================================
# CARGA DE VARIABLES DE ENTORNO
# =========================================================
load_dotenv()

# Crea las tablas si no existen.
# En producción sirve para mantener el despliegue simple.
Base.metadata.create_all(bind=engine)

# Configuración de entorno.
APP_ENV = os.getenv("APP_ENV", "development")
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "true").lower() == "true"

# =========================================================
# CREACIÓN DE APP FASTAPI
# =========================================================
# En producción puedes desactivar Swagger usando:
# APP_ENV=production
# ENABLE_DOCS=false
if APP_ENV == "production" and not ENABLE_DOCS:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
else:
    app = FastAPI()

# =========================================================
# CORS
# =========================================================
# Esto permite que tu web pública pueda enviar formularios al backend.
#
# Importante:
# - http://127.0.0.1:5500 y http://localhost:5500 son para Live Server local.
# - https://factorysoftware.cl y https://www.factorysoftware.cl son producción.
# - El endpoint correcto de leads es: POST /leads/
ALLOWED_ORIGINS = [
    "https://factorysoftware.cl",
    "https://www.factorysoftware.cl",

    # Angular local
    "http://localhost:4200",
    "http://127.0.0.1:4200",

    # Web estática local con Live Server
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# RATE LIMITER
# =========================================================
# Protege la API contra demasiadas solicitudes desde una misma IP.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # Respuesta personalizada cuando se supera el límite de solicitudes.
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intenta más tarde."}
    )


# =========================================================
# HEADERS DE SEGURIDAD
# =========================================================
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Agrega headers básicos de seguridad a las respuestas de la API.
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # CSP conservadora para la API.
    # Ojo: esta CSP aplica a respuestas del backend, no a tu web estática.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "frame-ancestors 'none';"
    )

    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# =========================================================
# RUTAS
# =========================================================
app.include_router(auth.router)
app.include_router(leads.router)


@app.get("/")
def root():
    # Ruta simple para verificar que la API está funcionando.
    return {"message": "API funcionando"}


@app.get("/health")
def health():
    # Ruta de salud para probar rápido desde navegador o Render.
    return {
        "status": "ok",
        "environment": APP_ENV,
        "docs_enabled": ENABLE_DOCS,
        "lead_endpoint": "/leads/"
    }
