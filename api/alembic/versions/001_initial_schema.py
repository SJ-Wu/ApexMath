"""初始資料庫架構：建立 users, exam_templates, teacher_exam_access, verification_codes, exam_sessions 表。

Revision ID: 001
Revises: None
Create Date: 2026-02-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="teacher"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # exam_templates
    op.create_table(
        "exam_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_id", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("template_data", JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # teacher_exam_access
    op.create_table(
        "teacher_exam_access",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("teacher_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exam_template_id", UUID(as_uuid=True), sa.ForeignKey("exam_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # verification_codes
    op.create_table(
        "verification_codes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("prefix", sa.String(12), nullable=False),
        sa.Column("student_number", sa.String(3), nullable=False),
        sa.Column("teacher_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exam_template_id", UUID(as_uuid=True), sa.ForeignKey("exam_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="unused"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # exam_sessions
    op.create_table(
        "exam_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("verification_code_id", UUID(as_uuid=True), sa.ForeignKey("verification_codes.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("student_name", sa.String(100), nullable=False),
        sa.Column("exam_id", sa.String(100), nullable=False),
        sa.Column("answers", JSONB, nullable=True),
        sa.Column("results", JSONB, nullable=True),
        sa.Column("assessment", JSONB, nullable=True),
        sa.Column("ai_analysis", JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("exam_sessions")
    op.drop_table("verification_codes")
    op.drop_table("teacher_exam_access")
    op.drop_table("exam_templates")
    op.drop_table("users")
