from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import DB_PATH
from app.models.base import Base
from app.models.user import Usuario
from app.models.empresa import Empresa
from app.models.trabalhador import Trabalhador
from app.models.treinamento import Treinamento
from app.models.documento import TipoDocumento, Documento
from app.models.bloqueio import Bloqueio
from app.models.acesso import Acesso
from app.models.atividade import Atividade, AtividadeParticipante
from app.models.veiculo import Veiculo  # CORREÇÃO: faltava esse import —
                                          # sem ele, create_all() nunca cria
                                          # a tabela 'veiculos'.
from app.models.visitante import Visitante  # CORREÇÃO: mesma situação —
                                              # sem esse import, create_all()
                                              # nunca cria a tabela 'visitantes'.

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def criar_tabelas():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()