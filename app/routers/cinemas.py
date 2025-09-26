# app/routers/cinemas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/cinemas", tags=["cinemas"])

def _recount_salas(db: Session, cine_id: int):
    total = db.query(func.count(models.Sala.id)).filter(models.Sala.cine_id == cine_id).scalar()
    cine = db.query(models.Cinema).filter(models.Cinema.id == cine_id).first()
    if cine:
        cine.nro_salas = total or 0
        db.commit()
        db.refresh(cine)
    return total or 0

@router.get("/", response_model=list[schemas.CinemaOut])
def list_cinemas(db: Session = Depends(get_db)):
    return db.query(models.Cinema).order_by(models.Cinema.id.desc()).all()

@router.post("/", response_model=schemas.CinemaOut, status_code=201)
def create_cinema(payload: schemas.CinemaCreate, db: Session = Depends(get_db)):
    cine = models.Cinema(
        nombre=payload.nombre,
        ciudad=payload.ciudad,
        distrito=payload.distrito,
        nro_salas=payload.nro_salas or 0
    )
    db.add(cine)
    db.commit()
    db.refresh(cine)
    return cine

@router.get("/{cinema_id}", response_model=schemas.CinemaWithSalas)
def get_cinema(cinema_id: int, db: Session = Depends(get_db)):
    cine = db.query(models.Cinema).filter(models.Cinema.id == cinema_id).first()
    if not cine:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    return cine

@router.patch("/{cinema_id}", response_model=schemas.CinemaOut)
def update_cinema(cinema_id: int, payload: schemas.CinemaUpdate, db: Session = Depends(get_db)):
    cine = db.query(models.Cinema).filter(models.Cinema.id == cinema_id).first()
    if not cine:
        raise HTTPException(status_code=404, detail="Cine no encontrado")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(cine, k, v)

    db.commit()
    db.refresh(cine)
    return cine

@router.delete("/{cinema_id}")
def delete_cinema(cinema_id: int, db: Session = Depends(get_db)):
    cine = db.query(models.Cinema).filter(models.Cinema.id == cinema_id).first()
    if not cine:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    db.delete(cine)
    db.commit()
    return {"message": "Cine eliminado"}

@router.get("/{cinema_id}/salas", response_model=list[schemas.SalaOut])
def list_salas_by_cinema(cinema_id: int, db: Session = Depends(get_db)):
    # Verifica cine
    exists = db.query(models.Cinema.id).filter(models.Cinema.id == cinema_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    return db.query(models.Sala).filter(models.Sala.cine_id == cinema_id).order_by(models.Sala.numero.asc()).all()
