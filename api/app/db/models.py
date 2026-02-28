"""SQLAlchemy ORM 模型：定義所有資料庫表結構。"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有 ORM model 的基底類別。"""
    pass


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"


class User(Base):
    """統一使用者表：admin 與 teacher 共用。"""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="teacher")  # admin / teacher
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 關聯
    exam_access: Mapped[list["TeacherExamAccess"]] = relationship(back_populates="teacher", cascade="all, delete-orphan")
    verification_codes: Mapped[list["VerificationCode"]] = relationship(back_populates="teacher", cascade="all, delete-orphan")


class ExamTemplateRecord(Base):
    """試卷模板表：template_data 以 JSONB 存放完整 ExamTemplate。"""

    __tablename__ = "exam_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    template_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    teacher_access: Mapped[list["TeacherExamAccess"]] = relationship(back_populates="exam_template")
    verification_codes: Mapped[list["VerificationCode"]] = relationship(back_populates="exam_template")


class TeacherExamAccess(Base):
    """教師試卷存取權限表。"""

    __tablename__ = "teacher_exam_access"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_templates.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    teacher: Mapped["User"] = relationship(back_populates="exam_access")
    exam_template: Mapped["ExamTemplateRecord"] = relationship(back_populates="teacher_access")


class VerificationCode(Base):
    """驗證碼表：記錄每個驗證碼的狀態與歸屬。"""

    __tablename__ = "verification_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    prefix: Mapped[str] = mapped_column(String(12), nullable=False)
    student_number: Mapped[str] = mapped_column(String(3), nullable=False)  # 001~999
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_templates.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unused")  # unused / in_progress / completed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    teacher: Mapped["User"] = relationship(back_populates="verification_codes")
    exam_template: Mapped["ExamTemplateRecord"] = relationship(back_populates="verification_codes")
    exam_session: Mapped["ExamSession | None"] = relationship(back_populates="verification_code", uselist=False)


class ExamSession(Base):
    """學生測驗紀錄表：儲存作答過程與評分結果。"""

    __tablename__ = "exam_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_code_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("verification_codes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    student_name: Mapped[str] = mapped_column(String(100), nullable=False)
    exam_id: Mapped[str] = mapped_column(String(100), nullable=False)
    answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # 學生作答資料
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # 評分結果 (question_id -> score)
    assessment: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # 完整 AssessmentResult
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # AI 分析結果
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")  # in_progress / completed
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 關聯
    verification_code: Mapped["VerificationCode"] = relationship(back_populates="exam_session")
