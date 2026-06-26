from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin


class Bloqueio(Base, TimestampMixin):
    __tablename__ = "bloqueios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trabalhador_id = Column(Integer, ForeignKey("trabalhadores.id"), nullable=False)
    tipo = Column(String(20), nullable=False)  # "automatico" ou "manual"
    ativo = Column(Boolean, default=True)

    # Motivos manual
    doc_incompleta = Column(Boolean, default=False)
    sem_epi = Column(Boolean, default=False)
    comportamento = Column(Boolean, default=False)
    determinacao_gestao = Column(Boolean, default=False)
    outro = Column(Boolean, default=False)
    justificativa = Column(Text, nullable=True)

    # Quem registrou
    registrado_por = Column(String(100), nullable=True)
    desbloqueado_em = Column(DateTime, nullable=True)
    motivo_desbloqueio = Column(Text, nullable=True)

    trabalhador = relationship("Trabalhador")

    def __repr__(self):
        return f"<Bloqueio {self.trabalhador_id} — {self.tipo}>"