from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import traceback

from database import get_db
from schemas import UsuarioCreate, UsuarioLogin, Token
import crud
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/usuarios")
def create_internal_user(
    user: UsuarioCreate,
    db: Session = Depends(get_db)
):
    try:
        db_user = crud.get_user_by_email(db, user.correo)
        if db_user:
            raise HTTPException(status_code=400, detail="Correo ya registrado")

        rol_solicitado = user.rol.strip().lower()
        if rol_solicitado not in ["usuario", "admin", "superadmin"]:
            raise HTTPException(status_code=400, detail="Rol no válido")

        hashed_password = hash_password(user.password)

        nuevo_usuario = crud.create_user(
            db=db,
            nombre=user.nombre,
            correo=user.correo,
            password=hashed_password,
            rol=rol_solicitado,
            puede_crear_usuarios=user.puede_crear_usuarios
        )

        return {
            "mensaje": "Usuario creado correctamente",
            "usuario": {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre,
                "correo": nuevo_usuario.correo,
                "rol": nuevo_usuario.rol,
                "puede_crear_usuarios": nuevo_usuario.puede_crear_usuarios
            }
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print("SQLAlchemyError en /auth/usuarios:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        print("Error general en /auth/usuarios:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/login", response_model=Token)
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.correo)

    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({
        "user_id": db_user.id,
        "rol": db_user.rol
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, current_user["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": user.id,
        "nombre": user.nombre,
        "correo": user.correo,
        "rol": user.rol,
        "puede_crear_usuarios": user.puede_crear_usuarios
    }