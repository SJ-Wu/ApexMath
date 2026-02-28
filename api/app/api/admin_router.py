"""管理者後台路由：教師帳號 CRUD、試卷管理、學生紀錄查看。"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.auth.security import hash_password
from app.db.engine import get_db
from app.db.models import (
    ExamSession,
    ExamTemplateRecord,
    TeacherExamAccess,
    User,
    VerificationCode,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# === Schemas ===

class TeacherOut(BaseModel):
    id: str
    username: str
    display_name: str
    is_active: bool


class CreateTeacherRequest(BaseModel):
    username: str
    password: str
    display_name: str


class UpdateTeacherRequest(BaseModel):
    display_name: str | None = None
    password: str | None = None
    is_active: bool | None = None


class ExamTemplateOut(BaseModel):
    id: str
    exam_id: str
    name: str
    is_active: bool


class AssignExamRequest(BaseModel):
    teacher_id: str
    exam_template_id: str


class SessionSummaryOut(BaseModel):
    session_id: str
    student_name: str
    exam_id: str
    status: str
    code: str


class DashboardStatsOut(BaseModel):
    teacher_count: int
    exam_count: int
    session_count: int
    code_count: int


# === Endpoints ===

@router.get("/stats", response_model=DashboardStatsOut)
async def get_stats(
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """取得管理者儀表板統計。"""
    teacher_count = (await db.execute(
        select(func.count()).select_from(User).where(User.role == "teacher")
    )).scalar() or 0

    exam_count = (await db.execute(
        select(func.count()).select_from(ExamTemplateRecord).where(ExamTemplateRecord.is_active.is_(True))
    )).scalar() or 0

    session_count = (await db.execute(
        select(func.count()).select_from(ExamSession)
    )).scalar() or 0

    code_count = (await db.execute(
        select(func.count()).select_from(VerificationCode)
    )).scalar() or 0

    return DashboardStatsOut(
        teacher_count=teacher_count,
        exam_count=exam_count,
        session_count=session_count,
        code_count=code_count,
    )


# --- 教師管理 ---

@router.get("/teachers", response_model=list[TeacherOut])
async def list_teachers(
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """列出所有教師帳號。"""
    result = await db.execute(select(User).where(User.role == "teacher").order_by(User.created_at))
    teachers = result.scalars().all()
    return [
        TeacherOut(id=str(t.id), username=t.username, display_name=t.display_name, is_active=t.is_active)
        for t in teachers
    ]


@router.post("/teachers", response_model=TeacherOut)
async def create_teacher(
    body: CreateTeacherRequest,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """建立教師帳號。"""
    # 檢查 username 是否已存在
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="此帳號已存在")

    teacher = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        display_name=body.display_name,
        role="teacher",
    )
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)

    return TeacherOut(id=str(teacher.id), username=teacher.username, display_name=teacher.display_name, is_active=teacher.is_active)


@router.put("/teachers/{teacher_id}", response_model=TeacherOut)
async def update_teacher(
    teacher_id: str,
    body: UpdateTeacherRequest,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """更新教師帳號。"""
    try:
        tid = uuid.UUID(teacher_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的教師 ID")

    result = await db.execute(select(User).where(User.id == tid, User.role == "teacher"))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(status_code=404, detail="教師不存在")

    if body.display_name is not None:
        teacher.display_name = body.display_name
    if body.password is not None:
        teacher.hashed_password = hash_password(body.password)
    if body.is_active is not None:
        teacher.is_active = body.is_active

    await db.commit()
    await db.refresh(teacher)

    return TeacherOut(id=str(teacher.id), username=teacher.username, display_name=teacher.display_name, is_active=teacher.is_active)


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: str,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """停用教師帳號（軟刪除）。"""
    try:
        tid = uuid.UUID(teacher_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的教師 ID")

    result = await db.execute(select(User).where(User.id == tid, User.role == "teacher"))
    teacher = result.scalar_one_or_none()
    if teacher is None:
        raise HTTPException(status_code=404, detail="教師不存在")

    teacher.is_active = False
    await db.commit()
    return {"detail": "教師帳號已停用"}


# --- 試卷管理 ---

@router.get("/exams", response_model=list[ExamTemplateOut])
async def list_exams(
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """列出所有試卷模板。"""
    result = await db.execute(select(ExamTemplateRecord).order_by(ExamTemplateRecord.created_at))
    templates = result.scalars().all()
    return [
        ExamTemplateOut(id=str(t.id), exam_id=t.exam_id, name=t.name, is_active=t.is_active)
        for t in templates
    ]


@router.post("/exams/assign")
async def assign_exam_to_teacher(
    body: AssignExamRequest,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """將試卷授權給教師。"""
    try:
        tid = uuid.UUID(body.teacher_id)
        eid = uuid.UUID(body.exam_template_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的 ID 格式")

    # 檢查是否已存在
    existing = await db.execute(
        select(TeacherExamAccess).where(
            TeacherExamAccess.teacher_id == tid,
            TeacherExamAccess.exam_template_id == eid,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="此授權已存在")

    access = TeacherExamAccess(teacher_id=tid, exam_template_id=eid)
    db.add(access)
    await db.commit()
    return {"detail": "授權成功"}


# --- 學生紀錄 ---

@router.get("/sessions", response_model=list[SessionSummaryOut])
async def list_sessions(
    exam_id: str | None = None,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """列出所有學生測驗紀錄。"""
    from sqlalchemy.orm import selectinload

    stmt = (
        select(ExamSession)
        .options(selectinload(ExamSession.verification_code))
        .order_by(ExamSession.started_at.desc())
    )
    if exam_id:
        stmt = stmt.where(ExamSession.exam_id == exam_id)

    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return [
        SessionSummaryOut(
            session_id=str(s.id),
            student_name=s.student_name,
            exam_id=s.exam_id,
            status=s.status,
            code=s.verification_code.code if s.verification_code else "",
        )
        for s in sessions
    ]
