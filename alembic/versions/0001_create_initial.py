"""create initial tables

Revision ID: 0001_create_initial
Revises:
Create Date: 2026-04-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001_create_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # create pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "models",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
    )

    op.create_table(
        "fine_tunes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "model_id", sa.UUID(as_uuid=True), sa.ForeignKey("models.id"), nullable=True
        ),
        sa.Column("base_model", sa.String(255), nullable=False),
        sa.Column("params", JSONB, nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("metrics", JSONB, nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True)),
    )

    op.create_table(
        "records",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "model_id", sa.UUID(as_uuid=True), sa.ForeignKey("models.id"), nullable=True
        ),
        sa.Column("input", JSONB, nullable=False),
        sa.Column("output", JSONB, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")
        ),
    )

    # embeddings table using pgvector vector type (1536 dims example)
    op.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id uuid PRIMARY KEY,
        record_id uuid REFERENCES records(id),
        vector vector(1536),
        created_at timestamptz DEFAULT now()
    );
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS embeddings;")
    op.drop_table("records")
    op.drop_table("fine_tunes")
    op.drop_table("models")
    op.execute("DROP EXTENSION IF EXISTS vector;")
