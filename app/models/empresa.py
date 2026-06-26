from sqlalchemy import Column, Integer, String, Text, Date, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Empresa(Base, TimestampMixin):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    razao_social = Column(String(200), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    email = Column(String(150))
    telefone = Column(String(20))
    responsavel = Column(String(150))
    setor = Column(String(100), nullable=True)
    status = Column(String(20), default="ativo")

    # ── Tipo de empresa: "fixa" ou "flutuante" ──────────────────────────────
    # Empresa fixa = presta serviço contínuo na unidade (já tem rotina
    # conhecida, não precisa descrever a atividade a cada entrada).
    # Empresa flutuante = visita esporádica, precisa descrever o motivo
    # da atividade a cada liberação de entrada na portaria.
    tipo_empresa = Column(String(20), nullable=False, default="fixa")

    # Checkboxes
    tem_contrato_social = Column(Boolean, default=False)
    tem_manual_qsma = Column(Boolean, default=False)

    # PGR
    pgr_data_inicial = Column(Date, nullable=True)
    pgr_validade = Column(Date, nullable=True)

    # PCMSO
    pcmso_data_inicial = Column(Date, nullable=True)
    pcmso_validade = Column(Date, nullable=True)

    # Apólice de Seguro
    apolice_data_inicial = Column(Date, nullable=True)
    apolice_validade = Column(Date, nullable=True)

    trabalhadores = relationship("Trabalhador", back_populates="empresa",
                                  cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Empresa {self.razao_social}>"