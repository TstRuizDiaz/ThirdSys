
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base          # ajuste se seu Base vem de outro lugar


class Atividade(Base):
    __tablename__ = "atividades"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    descricao    = Column(Text,    nullable=False)
    setor        = Column(String(200), nullable=True)   # razao_social da empresa do responsável
    data_inicio  = Column(DateTime, default=datetime.now, nullable=False)
    data_fim     = Column(DateTime, nullable=True)       # preenchido ao encerrar
    encerrada    = Column(Boolean,  default=False)
    operador     = Column(String(120), nullable=True)   # usuário da portaria que registrou

    participantes = relationship(
        "AtividadeParticipante",
        back_populates="atividade",
        cascade="all, delete-orphan",
    )


class AtividadeParticipante(Base):
    __tablename__ = "atividade_participantes"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    atividade_id  = Column(Integer, ForeignKey("atividades.id"), nullable=False)
    trabalhador_id= Column(Integer, ForeignKey("trabalhadores.id"), nullable=False)

    atividade   = relationship("Atividade",   back_populates="participantes")
    trabalhador = relationship("Trabalhador")