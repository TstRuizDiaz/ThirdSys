from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from .base import Base, TimestampMixin


class TipoDocumento(Base, TimestampMixin):
    __tablename__ = "tipo_documentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(20), nullable=False)  # "empresa" ou "colaborador"
    tem_validade = Column(Boolean, default=False)
    ordem = Column(Integer, default=0)

    def __repr__(self):
        return f"<TipoDocumento {self.nome}>"


class Documento(Base, TimestampMixin):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    trabalhador_id = Column(Integer, ForeignKey("trabalhadores.id"), nullable=True)
    tipo_documento_id = Column(Integer, ForeignKey("tipo_documentos.id"), nullable=False)

    possui = Column(Boolean, default=False)
    caminho_arquivo = Column(String(500), nullable=True)
    nome_arquivo = Column(String(255), nullable=True)
    data_inicial = Column(Date, nullable=True)
    data_validade = Column(Date, nullable=True)
    observacao = Column(Text, nullable=True)

    tipo_documento = relationship("TipoDocumento")
    empresa = relationship("Empresa")
    trabalhador = relationship("Trabalhador")

    @property
    def status(self) -> str:
        if not self.data_validade:
            return "sem_data"
        hoje = date.today()
        if self.data_validade < hoje:
            return "vencido"
        elif self.data_validade <= hoje + timedelta(days=30):
            return "a_vencer"
        return "valido"

    @property
    def dias_restantes(self):
        if not self.data_validade:
            return None
        return (self.data_validade - date.today()).days

    def __repr__(self):
        return f"<Documento {self.tipo_documento_id}>"