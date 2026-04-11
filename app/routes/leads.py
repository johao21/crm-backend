from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas
from app.security import get_current_user, require_admin
from app.rate_limiter import limiter

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/")
@limiter.limit("5/minute")
def create_lead(
    request: Request,
    lead: schemas.LeadCreate,
    db: Session = Depends(get_db)
):
    nuevo_lead = crud.create_lead(db, lead)

    return {
        "message": "Lead recibido correctamente",
        "tracking_id": nuevo_lead.public_id
    }


@router.get("/all")
def read_all_leads(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return crud.get_all_leads(db)


@router.get("/mine")
def read_my_leads(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_my_leads(db, current_user["user_id"])


@router.get("/unassigned")
def read_unassigned_leads(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return crud.get_unassigned_leads(db)


@router.put("/{lead_id}/assign/{assigned_user_id}")
def assign_lead(
    lead_id: int,
    assigned_user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    lead = crud.assign_lead(db, lead_id, assigned_user_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.put("/{lead_id}/assign-auto")
def reassign_lead_auto(
    lead_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    lead = crud.reassign_lead_automatically(db, lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.put("/{lead_id}/estado")
def cambiar_estado(
    lead_id: int,
    data: schemas.LeadUpdateEstado,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user["rol"] in ["admin", "superadmin"]

    lead = crud.update_estado(
        db,
        lead_id,
        data.estado,
        current_user["user_id"],
        is_admin
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.put("/{lead_id}/rut")
def cambiar_rut(
    lead_id: int,
    data: schemas.LeadUpdateRut,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user["rol"] in ["admin", "superadmin"]

    lead = crud.update_rut(
        db,
        lead_id,
        data.rut,
        current_user["user_id"],
        is_admin
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.put("/{lead_id}/nota-interna")
def cambiar_nota_interna(
    lead_id: int,
    data: schemas.LeadUpdateNotaInterna,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user["rol"] in ["admin", "superadmin"]

    lead = crud.update_nota_interna(
        db,
        lead_id,
        data.nota_interna,
        current_user["user_id"],
        is_admin
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.put("/{lead_id}")
def actualizar_lead(
    lead_id: int,
    data: schemas.LeadUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user["rol"] in ["admin", "superadmin"]

    lead = crud.update_lead(
        db,
        lead_id,
        data,
        current_user["user_id"],
        is_admin
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.post("/{lead_id}/historial-contacto")
def registrar_historial(
    lead_id: int,
    data: schemas.LeadHistorialAction,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user["rol"] in ["admin", "superadmin"]

    lead = crud.registrar_historial_contacto(
        db,
        lead_id,
        data.accion,
        current_user["user_id"],
        is_admin
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return lead


@router.delete("/{lead_id}")
def eliminar_lead(
    lead_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    lead = crud.delete_lead(db, lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return {"message": "Lead eliminado correctamente"}