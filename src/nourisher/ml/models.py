import importlib
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base

try:
    Vector = importlib.import_module("pgvector.sqlalchemy").Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    Vector = None
    PGVECTOR_AVAILABLE = False

Base = declarative_base()


class Model(Base):
    __tablename__ = "models"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String(255), nullable=False)
    path = sa.Column(sa.Text, nullable=False)
    meta = sa.Column("metadata", JSONB, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), server_default=sa.func.now())


class FineTune(Base):
    __tablename__ = "fine_tunes"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("models.id"), nullable=True)
    base_model = sa.Column(sa.String(255), nullable=False)
    params = sa.Column(JSONB, nullable=True)
    status = sa.Column(sa.String(50), nullable=False, default="pending")
    metrics = sa.Column(JSONB, nullable=True)
    started_at = sa.Column(sa.TIMESTAMP(timezone=True))
    finished_at = sa.Column(sa.TIMESTAMP(timezone=True))


class Record(Base):
    __tablename__ = "records"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("models.id"), nullable=True)
    input = sa.Column(JSONB, nullable=False)
    output = sa.Column(JSONB, nullable=True)
    meta = sa.Column("metadata", JSONB, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), server_default=sa.func.now())


class Embedding(Base):
    __tablename__ = "embeddings"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("records.id"), nullable=True)
    if PGVECTOR_AVAILABLE:
        vector = sa.Column(Vector, nullable=True)
    else:
        vector = sa.Column(JSONB, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
