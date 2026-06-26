from sqlalchemy import Column, Integer, String, Boolean
from .base import Base, TimestampMixin

class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(300), nullable=False)
    perfil = Column(String(20), default="operador")  # admin, tecnico, operador
    ativo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Usuario {self.username}>"