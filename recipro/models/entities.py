from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Crush(Base):
    __tablename__ = "crushes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analyses = relationship("Analysis", back_populates="crush", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    crush_id = Column(Integer, ForeignKey("crushes.id"), nullable=False, index=True)
    data_analise = Column(DateTime, default=datetime.utcnow, nullable=False)

    total_mensagens = Column(Integer, nullable=False)
    score_reciprocidade = Column(Float, nullable=False)
    score_investimento = Column(Float, nullable=False)
    score_profundidade = Column(Float, nullable=False)
    tempo_medio_resposta = Column(Float, nullable=False)
    percentual_mensagens_usuario = Column(Float, nullable=False)
    tendencia_semana_json = Column(Text, nullable=False)
    insights_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    crush = relationship("Crush", back_populates="analyses")
