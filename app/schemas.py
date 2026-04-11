from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LeadCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    telefono: str = Field(..., min_length=6, max_length=20)
    correo: Optional[EmailStr] = None
    rut: Optional[str] = Field(default=None, max_length=20)
    servicio: str = Field(..., min_length=2, max_length=100)
    nota: str = Field(..., min_length=3, max_length=1000)
    origen: Optional[str] = Field(default="web", max_length=50)
    presupuesto: Optional[str] = Field(default=None, max_length=50)
    comuna: Optional[str] = Field(default=None, max_length=100)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    urgencia: Optional[str] = Field(default=None, max_length=50)
    empresa: Optional[str] = Field(default=None, max_length=150)


class LeadUpdateEstado(BaseModel):
    estado: str = Field(..., min_length=2, max_length=50)


class LeadUpdateRut(BaseModel):
    rut: Optional[str] = Field(default=None, max_length=20)


class LeadUpdateNotaInterna(BaseModel):
    nota_interna: Optional[str] = Field(default=None, max_length=1000)


class LeadUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(default=None, min_length=6, max_length=20)
    correo: Optional[EmailStr] = None
    rut: Optional[str] = Field(default=None, max_length=20)
    servicio: Optional[str] = Field(default=None, min_length=2, max_length=100)
    nota: Optional[str] = Field(default=None, min_length=3, max_length=1000)
    estado: Optional[str] = Field(default=None, max_length=50)
    temperatura: Optional[str] = Field(default=None, max_length=50)
    origen: Optional[str] = Field(default=None, max_length=50)
    fecha_creacion: Optional[str] = Field(default=None, max_length=100)
    nota_interna: Optional[str] = Field(default=None, max_length=1000)
    presupuesto: Optional[str] = Field(default=None, max_length=50)
    comuna: Optional[str] = Field(default=None, max_length=100)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    urgencia: Optional[str] = Field(default=None, max_length=50)
    empresa: Optional[str] = Field(default=None, max_length=150)


class LeadHistorialAction(BaseModel):
    accion: str = Field(..., min_length=2, max_length=500)


class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    rol: str = Field(default="usuario", max_length=20)
    puede_crear_usuarios: bool = False


class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: str
    puede_crear_usuarios: bool

    class Config:
        from_attributes = True