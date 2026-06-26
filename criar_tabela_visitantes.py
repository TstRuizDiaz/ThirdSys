"""
Script avulso — roda uma vez só para criar a tabela 'visitantes'
sem precisar esperar o próximo restart completo do app.

Uso:
    python criar_tabela_visitantes.py

Pode ser executado e descartado depois.
"""
from app.core.database import engine
from app.models.base import Base
from app.models.visitante import Visitante

Base.metadata.create_all(engine, tables=[Visitante.__table__])
print("Tabela 'visitantes' criada (ou já existia). OK.")