"""測驗 Session 資料存取層。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import ExamSession, VerificationCode


async def get_sessions_by_teacher(
    db: AsyncSession,
    teacher_id: uuid.UUID,
    exam_id: str | None = None,
) -> list[ExamSession]:
    """取得教師所轄驗證碼對應的測驗 session 列表。"""
    stmt = (
        select(ExamSession)
        .join(VerificationCode)
        .where(VerificationCode.teacher_id == teacher_id)
        .options(selectinload(ExamSession.verification_code))
        .order_by(ExamSession.started_at.desc())
    )
    if exam_id is not None:
        stmt = stmt.where(ExamSession.exam_id == exam_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_session_by_id(db: AsyncSession, session_id: uuid.UUID) -> ExamSession | None:
    """依 ID 取得測驗 session。"""
    result = await db.execute(
        select(ExamSession)
        .where(ExamSession.id == session_id)
        .options(selectinload(ExamSession.verification_code))
    )
    return result.scalar_one_or_none()
