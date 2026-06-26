"""
app/models/veiculo.py

Model SQLAlchemy para controle de veículos na portaria.

Após criar este arquivo, rode:
    alembic revision --autogenerate -m "add veiculos"
    alembic upgrade head
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
# Importe o Base do seu projeto (ajuste o caminho se necessário)
from app.core.database import Base


class Veiculo(Base):
    __tablename__ = "veiculos"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    placa      = Column(String(20),  nullable=False, index=True)
    modelo     = Column(String(100), nullable=True)
    tipo       = Column(String(40),  nullable=True,  default="Carro")
    cor        = Column(String(40),  nullable=True)
    motorista  = Column(String(120), nullable=True)
    empresa    = Column(String(120), nullable=True)
    observacao = Column(Text,        nullable=True)

    # "Dentro" | "Saiu"
    status     = Column(String(20),  nullable=False, default="Dentro", index=True)

    entrada    = Column(DateTime,    nullable=False)
    saida      = Column(DateTime,    nullable=True)
    operador   = Column(String(80),  nullable=True,  default="portaria")

    def __repr__(self):
        return f"<Veiculo id={self.id} placa={self.placa!r} status={self.status!r}>"