# app/schemas.py
from typing import Optional, List
from pydantic import BaseModel

# ----- SALAS -----
class SalaBase(BaseModel):
    cine_id: int
    numero: int
    capacidad: Optional[int] = None
    tipo_sala: Optional[str] = None

class SalaCreate(SalaBase):
    pass

class SalaUpdate(BaseModel):
    numero: Optional[int] = None
    capacidad: Optional[int] = None
    tipo_sala: Optional[str] = None

class SalaOut(SalaBase):
    id: int
    class Config:
        from_attributes = True

# ----- CINEMAS -----
class CinemaBase(BaseModel):
    nombre: str
    ciudad: Optional[str] = None
    distrito: Optional[str] = None
    nro_salas: Optional[int] = 0

class CinemaCreate(CinemaBase):
    pass

class CinemaUpdate(BaseModel):
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    distrito: Optional[str] = None
    nro_salas: Optional[int] = None

class CinemaOut(CinemaBase):
    id: int
    class Config:
        from_attributes = True

class CinemaWithSalas(CinemaOut):
    salas: List[SalaOut] = []
