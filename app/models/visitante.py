from sqlalchemy import Column, Integer, String, DateTime
from app.models.base import Base


class Visitante(Base):
    __tablename__ = "visitantes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=True)         # CPF/RG
    telefone = Column(String, nullable=True)
    empresa_visitada = Column(String, nullable=True)  # setor/empresa que ele vai visitar
    pessoa_visitada = Column(String, nullable=True)   # quem ele procura
    motivo = Column(String, nullable=True)
    entrada = Column(DateTime, nullable=True)
    saida = Column(DateTime, nullable=True)
    status = Column(String, default="Dentro")         # "Dentro" | "Saiu"
    operador = Column(String, nullable=True)