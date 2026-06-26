from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)