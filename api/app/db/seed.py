"""資料庫初始化種子資料：建立預設 admin 帳號與小五試卷。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.core.config import settings
from app.data.grade5_entrance import grade5_entrance_template
from app.db.models import ExamTemplateRecord, User


async def seed_admin(db: AsyncSession) -> None:
    """若 admin 帳號不存在，自動建立預設管理者。"""
    result = await db.execute(select(User).where(User.username == settings.admin_username))
    if result.scalar_one_or_none() is not None:
        return

    admin = User(
        username=settings.admin_username,
        hashed_password=hash_password(settings.admin_password),
        display_name="系統管理員",
        role="admin",
    )
    db.add(admin)
    await db.commit()


async def seed_exam_templates(db: AsyncSession) -> None:
    """若小五入班檢測試卷不存在，自動寫入 DB。"""
    template = grade5_entrance_template
    result = await db.execute(
        select(ExamTemplateRecord).where(ExamTemplateRecord.exam_id == template.exam_id)
    )
    if result.scalar_one_or_none() is not None:
        return

    record = ExamTemplateRecord(
        exam_id=template.exam_id,
        name=template.name,
        template_data=template.model_dump(),
    )
    db.add(record)
    await db.commit()


async def run_seed(db: AsyncSession) -> None:
    """執行所有種子資料初始化。"""
    await seed_admin(db)
    await seed_exam_templates(db)
