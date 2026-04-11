# ================================
# IMPORTACIONES
# ================================
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()


# ================================
# CONFIGURACIÓN GENERAL
# ================================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está definida")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


# ================================
# CONFIGURACIÓN DE HASH
# ================================
# bcrypt con costo explícito
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=int(os.getenv("BCRYPT_ROUNDS", "12"))
)


# ================================
# AUTENTICACIÓN BEARER
# ================================
security = HTTPBearer()


# ================================
# FUNCIONES DE PASSWORD
# ================================
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# ================================
# CREACIÓN DE TOKEN JWT
# ================================
def create_access_token(data: dict):
    """
    Genera un JWT firmado con expiración corta.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================================
# VALIDACIÓN DE TOKEN
# ================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")
        rol = payload.get("rol")
        token_type = payload.get("type")

        if user_id is None or rol is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        return {
            "user_id": user_id,
            "rol": rol
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    return current_user


def require_superadmin(current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") != "superadmin":
        raise HTTPException(status_code=403, detail="No autorizado")
    return current_user