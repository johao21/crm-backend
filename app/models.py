from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Index
from app.database import Base
import uuid


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(String, default="usuario", nullable=False)
    puede_crear_usuarios = Column(Boolean, default=False, nullable=False)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    public_id = Column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, nullable=True)
    rut = Column(String, nullable=True)

    servicio = Column(String, nullable=False)
    nota = Column(String, nullable=False)

    estado = Column(String, default="nuevo", index=True)
    temperatura = Column(String, default="frio")

    origen = Column(String, default="web")
    fecha_creacion = Column(String, nullable=True)

    assigned_user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)

    nota_interna = Column(String, nullable=True)
    historial_contacto = Column(String, nullable=True)

    presupuesto = Column(String, nullable=True)
    comuna = Column(String, nullable=True)
    ciudad = Column(String, nullable=True)
    urgencia = Column(String, nullable=True)
    empresa = Column(String, nullable=True)


Index("ix_leads_assigned_estado", Lead.assigned_user_id, Lead.estado)