# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Cinema(Base):
    __tablename__ = "cinemas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ciudad = Column(String, nullable=True)
    distrito = Column(String, nullable=True)
    nro_salas = Column(Integer, nullable=True, default=0)

    salas = relationship(
        "Sala",
        back_populates="cine",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Sala(Base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, index=True)
    cine_id = Column(Integer, ForeignKey("cinemas.id", ondelete="CASCADE"), nullable=False)
    numero = Column(Integer, nullable=False)
    capacidad = Column(Integer, nullable=True)
    tipo_sala = Column(String, nullable=True)

    cine = relationship("Cinema", back_populates="salas")

    __table_args__ = (
        UniqueConstraint("cine_id", "numero", name="uq_sala_cine_numero"),
    )
