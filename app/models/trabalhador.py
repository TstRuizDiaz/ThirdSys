from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


OPCAO_SIM = "sim"
OPCAO_NAO = "nao"
OPCAO_NA  = "na"


class Trabalhador(Base, TimestampMixin):
    __tablename__ = "trabalhadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nome = Column(String(200), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    funcao = Column(String(100))
    data_nascimento = Column(Date, nullable=True)
    data_admissao = Column(Date, nullable=True)
    ativo = Column(Boolean, default=True)

    # ASO com validade
    aso_data_inicial = Column(Date, nullable=True)
    aso_validade = Column(Date, nullable=True)

    # Checkboxes (sim / nao / na)
    ordem_servico = Column(String(10), default=OPCAO_NAO)
    ficha_registro = Column(String(10), default=OPCAO_NAO)
    ficha_epi = Column(String(10), default=OPCAO_NAO)
    cnh = Column(String(10), default=OPCAO_NA)

    empresa = relationship("Empresa", back_populates="trabalhadores")
    treinamentos = relationship("Treinamento", back_populates="trabalhador",
                                 cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trabalhador {self.nome}>"