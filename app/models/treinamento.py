from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from .base import Base, TimestampMixin


NRS_BRASIL = [
    "NR-01 — Disposições Gerais e Gerenciamento de Riscos (Integração)",
    "NR-02 — Inspeção Prévia",
    "NR-03 — Embargo e Interdição",
    "NR-04 — Serviços Especializados em Eng. de Segurança (SESMT)",
    "NR-05 — Comissão Interna de Prevenção de Acidentes (CIPA)",
    "NR-06 — Equipamentos de Proteção Individual (EPI)",
    "NR-07 — Programa de Controle Médico de Saúde Ocupacional (PCMSO)",
    "NR-08 — Edificações",
    "NR-09 — Avaliação e Controle das Exposições Ocupacionais",
    "NR-10 — Segurança em Instalações e Serviços em Eletricidade",
    "NR-11 — Transporte, Movimentação, Armazenagem e Manuseio de Materiais",
    "NR-12 — Segurança no Trabalho em Máquinas e Equipamentos",
    "NR-13 — Caldeiras, Vasos de Pressão e Tubulações",
    "NR-14 — Fornos",
    "NR-15 — Atividades e Operações Insalubres",
    "NR-16 — Atividades e Operações Perigosas",
    "NR-17 — Ergonomia",
    "NR-18 — Segurança e Saúde no Trabalho na Indústria da Construção",
    "NR-19 — Explosivos",
    "NR-20 — Segurança e Saúde no Trabalho com Inflamáveis e Combustíveis",
    "NR-21 — Trabalho a Céu Aberto",
    "NR-22 — Segurança e Saúde Ocupacional na Mineração",
    "NR-23 — Proteção Contra Incêndios",
    "NR-24 — Condições Sanitárias e de Conforto nos Locais de Trabalho",
    "NR-25 — Resíduos Industriais",
    "NR-26 — Sinalização de Segurança",
    "NR-27 — Registro Profissional do Técnico de Segurança do Trabalho",
    "NR-28 — Fiscalização e Penalidades",
    "NR-29 — Segurança e Saúde no Trabalho Portuário",
    "NR-30 — Segurança e Saúde no Trabalho Aquaviário",
    "NR-31 — Segurança e Saúde no Trabalho na Agricultura",
    "NR-32 — Segurança e Saúde no Trabalho em Serviços de Saúde",
    "NR-33 — Segurança e Saúde nos Trabalhos em Espaços Confinados",
    "NR-34 — Condições e Meio Ambiente de Trabalho na Indústria da Construção Naval",
    "NR-35 — Trabalho em Altura",
    "NR-36 — Segurança e Saúde no Trabalho em Empresas de Abate",
    "NR-37 — Segurança e Saúde em Plataformas de Petróleo",
    "NR-38 — Segurança e Saúde no Trabalho nas Atividades de Limpeza",
    "NR-39 — Segurança e Saúde no Trabalho em Salões de Beleza",
    "NR-40 — Segurança e Saúde no Trabalho em Serviços de Lavanderia",
]


class Treinamento(Base, TimestampMixin):
    __tablename__ = "treinamentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trabalhador_id = Column(Integer, ForeignKey("trabalhadores.id"), nullable=False)
    nr_nome = Column(String(200), nullable=False)
    data_realizacao = Column(Date, nullable=True)
    data_validade = Column(Date, nullable=True)
    certificado_path = Column(String(500), nullable=True)

    trabalhador = relationship("Trabalhador", back_populates="treinamentos")

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

    @property
    def is_integracao(self) -> bool:
        return "NR-01" in self.nr_nome

    def __repr__(self):
        return f"<Treinamento {self.nr_nome}>"