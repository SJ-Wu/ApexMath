"""驗證碼資料存取層。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import VerificationCode


async def create_codes(
    db: AsyncSession,
    codes: list[VerificationCode],
) -> list[VerificationCode]:
    """批次建立驗證碼。"""
    db.add_all(codes)
    await db.commit()
    for c in codes:
        await db.refresh(c)
    return codes


async def get_codes_by_teacher(
    db: AsyncSession,
    teacher_id: uuid.UUID,
    exam_id: str | None = None,
) -> list[VerificationCode]:
    """取得教師的驗證碼列表，可選依試卷篩選。"""
    stmt = (
        select(VerificationCode)
        .where(VerificationCode.teacher_id == teacher_id)
        .options(selectinload(VerificationCode.exam_template))
        .order_by(VerificationCode.created_at.desc())
    )
    if exam_id is not None:
        from app.db.models import ExamTemplateRecord
        stmt = stmt.join(ExamTemplateRecord).where(ExamTemplateRecord.exam_id == exam_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_code_by_value(db: AsyncSession, code: str) -> VerificationCode | None:
    """依驗證碼字串查詢。"""
    result = await db.execute(
        select(VerificationCode).where(VerificationCode.code == code)
    )
    return result.scalar_one_or_none()
