from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Usuario, Lead
import bleach


# =========================
# HELPERS DE SANITIZACIÓN
# =========================
def _clean_text(value: str | None, max_len: int | None = None) -> str | None:
    """
    Limpia texto para reducir riesgo de XSS almacenado.
    El frontend igual debe escapar al renderizar.
    """
    if value is None:
        return None

    cleaned = bleach.clean(value.strip(), tags=[], attributes={}, protocols=[], strip=True)

    if max_len is not None:
        cleaned = cleaned[:max_len]

    return cleaned


# =========================
# USUARIOS
# =========================
def get_user_by_email(db: Session, correo: str):
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id == user_id).first()


def create_user(
    db: Session,
    nombre: str,
    correo: str,
    password: str,
    rol: str = "usuario",
    puede_crear_usuarios: bool = False
):
    """
    Crea usuario interno.
    La seguridad de quién puede crearlo se valida en la ruta.
    """
    user = Usuario(
        nombre=_clean_text(nombre, 100),
        correo=correo.strip().lower(),
        password=password,
        rol=rol,
        puede_crear_usuarios=puede_crear_usuarios
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_creation_permission(db: Session, user_id: int, puede_crear_usuarios: bool):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.puede_crear_usuarios = puede_crear_usuarios
    db.commit()
    db.refresh(user)
    return user


def get_vendedores(db: Session):
    return db.query(Usuario).filter(Usuario.rol == "usuario").all()


def get_admin_fallback(db: Session):
    admin = db.query(Usuario).filter(Usuario.rol == "admin").first()
    if admin:
        return admin

    return db.query(Usuario).filter(Usuario.rol == "superadmin").first()


# =========================
# ASIGNACIÓN AUTOMÁTICA
# =========================
def get_user_with_less_workload(db: Session):
    vendedores = get_vendedores(db)

    if not vendedores:
        return get_admin_fallback(db)

    conteo = (
        db.query(
            Usuario.id,
            func.count(Lead.id).label("total")
        )
        .outerjoin(
            Lead,
            (Lead.assigned_user_id == Usuario.id) &
            (Lead.estado.notin_(["cerrado", "perdido"]))
        )
        .filter(Usuario.rol == "usuario")
        .group_by(Usuario.id)
        .order_by(func.count(Lead.id).asc(), Usuario.id.asc())
        .all()
    )

    if conteo:
        user_id = conteo[0].id
        return db.query(Usuario).filter(Usuario.id == user_id).first()

    return vendedores[0]


# =========================
# LEADS
# =========================
def create_lead(db: Session, lead):
    """
    Crea un lead público y lo asigna automáticamente.
    """
    usuario_asignado = get_user_with_less_workload(db)

    nuevo = Lead(
        nombre=_clean_text(lead.nombre, 100),
        telefono=_clean_text(lead.telefono, 20),
        correo=str(lead.correo).strip().lower() if getattr(lead, "correo", None) else None,
        rut=_clean_text(getattr(lead, "rut", None), 20),
        servicio=_clean_text(lead.servicio, 100),
        nota=_clean_text(lead.nota, 1000),
        estado="nuevo",
        temperatura="frio",
        origen=_clean_text(getattr(lead, "origen", "web"), 50),
        fecha_creacion=getattr(lead, "fecha_creacion", None),
        assigned_user_id=usuario_asignado.id if usuario_asignado else None,
        nota_interna=None,
        historial_contacto=None,
        presupuesto=_clean_text(getattr(lead, "presupuesto", None), 50),
        comuna=_clean_text(getattr(lead, "comuna", None), 100),
        ciudad=_clean_text(getattr(lead, "ciudad", None), 100),
        urgencia=_clean_text(getattr(lead, "urgencia", None), 50),
        empresa=_clean_text(getattr(lead, "empresa", None), 150)
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def get_all_leads(db: Session):
    return db.query(Lead).all()


def get_my_leads(db: Session, user_id: int):
    return db.query(Lead).filter(Lead.assigned_user_id == user_id).all()


def get_unassigned_leads(db: Session):
    return db.query(Lead).filter(Lead.assigned_user_id == None).all()


def get_lead_by_id(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_my_lead_by_id(db: Session, lead_id: int, user_id: int):
    return db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.assigned_user_id == user_id
    ).first()


def assign_lead(db: Session, lead_id: int, assigned_user_id: int):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None

    usuario = get_user_by_id(db, assigned_user_id)
    if not usuario:
        return None

    lead.assigned_user_id = assigned_user_id
    db.commit()
    db.refresh(lead)
    return lead


def reassign_lead_automatically(db: Session, lead_id: int):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None

    usuario_asignado = get_user_with_less_workload(db)
    if not usuario_asignado:
        return None

    lead.assigned_user_id = usuario_asignado.id
    db.commit()
    db.refresh(lead)
    return lead


def update_estado(db: Session, lead_id: int, estado: str, user_id: int, is_admin: bool = False):
    lead = get_lead_by_id(db, lead_id) if is_admin else get_my_lead_by_id(db, lead_id, user_id)
    if not lead:
        return None

    lead.estado = _clean_text(estado, 50)
    db.commit()
    db.refresh(lead)
    return lead


def update_rut(db: Session, lead_id: int, rut: str, user_id: int, is_admin: bool = False):
    lead = get_lead_by_id(db, lead_id) if is_admin else get_my_lead_by_id(db, lead_id, user_id)
    if not lead:
        return None

    lead.rut = _clean_text(rut, 20)
    db.commit()
    db.refresh(lead)
    return lead


def update_nota_interna(db: Session, lead_id: int, nota_interna: str, user_id: int, is_admin: bool = False):
    lead = get_lead_by_id(db, lead_id) if is_admin else get_my_lead_by_id(db, lead_id, user_id)
    if not lead:
        return None

    lead.nota_interna = _clean_text(nota_interna, 1000)
    db.commit()
    db.refresh(lead)
    return lead


def update_lead(db: Session, lead_id: int, data, user_id: int, is_admin: bool = False):
    lead = get_lead_by_id(db, lead_id) if is_admin else get_my_lead_by_id(db, lead_id, user_id)
    if not lead:
        return None

    if hasattr(data, "nombre") and data.nombre is not None:
        lead.nombre = _clean_text(data.nombre, 100)

    if hasattr(data, "telefono") and data.telefono is not None:
        lead.telefono = _clean_text(data.telefono, 20)

    if hasattr(data, "correo") and data.correo is not None:
        lead.correo = str(data.correo).strip().lower()

    if hasattr(data, "rut") and data.rut is not None:
        lead.rut = _clean_text(data.rut, 20)

    if hasattr(data, "servicio") and data.servicio is not None:
        lead.servicio = _clean_text(data.servicio, 100)

    if hasattr(data, "nota") and data.nota is not None:
        lead.nota = _clean_text(data.nota, 1000)

    if hasattr(data, "estado") and data.estado is not None:
        lead.estado = _clean_text(data.estado, 50)

    if hasattr(data, "temperatura") and data.temperatura is not None:
        lead.temperatura = _clean_text(data.temperatura, 50)

    if hasattr(data, "origen") and data.origen is not None:
        lead.origen = _clean_text(data.origen, 50)

    if hasattr(data, "fecha_creacion") and data.fecha_creacion is not None:
        lead.fecha_creacion = _clean_text(data.fecha_creacion, 100)

    if hasattr(data, "nota_interna") and data.nota_interna is not None:
        lead.nota_interna = _clean_text(data.nota_interna, 1000)

    if hasattr(data, "presupuesto") and data.presupuesto is not None:
        lead.presupuesto = _clean_text(data.presupuesto, 50)

    if hasattr(data, "comuna") and data.comuna is not None:
        lead.comuna = _clean_text(data.comuna, 100)

    if hasattr(data, "ciudad") and data.ciudad is not None:
        lead.ciudad = _clean_text(data.ciudad, 100)

    if hasattr(data, "urgencia") and data.urgencia is not None:
        lead.urgencia = _clean_text(data.urgencia, 50)

    if hasattr(data, "empresa") and data.empresa is not None:
        lead.empresa = _clean_text(data.empresa, 150)

    db.commit()
    db.refresh(lead)
    return lead


def registrar_historial_contacto(db: Session, lead_id: int, accion: str, user_id: int, is_admin: bool = False):
    lead = get_lead_by_id(db, lead_id) if is_admin else get_my_lead_by_id(db, lead_id, user_id)
    if not lead:
        return None

    nueva_accion = _clean_text(accion, 500)
    historial_actual = lead.historial_contacto or ""

    if historial_actual.strip():
        lead.historial_contacto = f"{historial_actual}\n{nueva_accion}"
    else:
        lead.historial_contacto = nueva_accion

    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None

    db.delete(lead)
    db.commit()
    return lead