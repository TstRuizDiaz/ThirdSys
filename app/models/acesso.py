from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin


class Acesso(Base, TimestampMixin):
    __tablename__ = "acessos"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    trabalhador_id = Column(Integer, ForeignKey("trabalhadores.id"), nullable=False)
    tipo           = Column(String(10), nullable=False)   # "entrada" | "saida"
    horario        = Column(DateTime, default=datetime.now, nullable=False)
    operador       = Column(String(100), nullable=True)   # usuário que liberou

    trabalhador = relationship("Trabalhador")

    def __repr__(self):
        return f"<Acesso {self.tipo} — trabalhador {self.trabalhador_id} @ {self.horario}>"