# app/routers/salas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/salas", tags=["salas"])

def _recount_salas(db: Session, cine_id: int):
    total = db.query(func.count(models.Sala.id)).filter(models.Sala.cine_id == cine_id).scalar()
    cine = db.query(models.Cinema).filter(models.Cinema.id == cine_id).first()
    if cine:
        cine.nro_salas = total or 0
        db.commit()
        db.refresh(cine)

@router.get("/", response_model=list[schemas.SalaOut])
def list_salas(db: Session = Depends(get_db)):
    return db.query(models.Sala).order_by(models.Sala.id.desc()).all()

@router.get("/{sala_id}", response_model=schemas.SalaOut)
def get_sala(sala_id: int, db: Session = Depends(get_db)):
    sala = db.query(models.Sala).filter(models.Sala.id == sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return sala

@router.post("/", response_model=schemas.SalaOut, status_code=201)
def create_sala(payload: schemas.SalaCreate, db: Session = Depends(get_db)):
    # Verifica cine
    cine = db.query(models.Cinema).filter(models.Cinema.id == payload.cine_id).first()
    if not cine:
        raise HTTPException(status_code=400, detail="cine_id no existe")

    sala = models.Sala(
        cine_id=payload.cine_id,
        numero=payload.numero,
        capacidad=payload.capacidad,
        tipo_sala=payload.tipo_sala
    )
    db.add(sala)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Violación de UNIQUE(cine_id, numero)
        raise HTTPException(status_code=409, detail="Ya existe una sala con ese número en este cine")
    db.refresh(sala)

    # Recalcular nro_salas
    _recount_salas(db, payload.cine_id)
    return sala

@router.patch("/{sala_id}", response_model=schemas.SalaOut)
def update_sala(sala_id: int, payload: schemas.SalaUpdate, db: Session = Depends(get_db)):
    sala = db.query(models.Sala).filter(models.Sala.id == sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

    old_cine_id = sala.cine_id

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(sala, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una sala con ese número en este cine")
    db.refresh(sala)

    # Si cambió el número o cine, recalculamos conteos
    _recount_salas(db, sala.cine_id)
    if sala.cine_id != old_cine_id:
        _recount_salas(db, old_cine_id)

    return sala

@router.delete("/{sala_id}")
def delete_sala(sala_id: int, db: Session = Depends(get_db)):
    sala = db.query(models.Sala).filter(models.Sala.id == sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

    cine_id = sala.cine_id
    db.delete(sala)
    db.commit()

    _recount_salas(db, cine_id)
    return {"message": "Sala eliminada"}
