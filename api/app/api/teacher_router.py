"""教師後台路由：驗證碼管理、成績查看、手動評分。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db.engine import get_db
from app.db.models import (
    ExamSession,
    ExamTemplateRecord,
    TeacherExamAccess,
    User,
    VerificationCode,
)
from app.domain.models import ExamSubmission, ExamTemplate, QuestionResult
from app.domain.scoring import generate_assessment
from app.repositories.session_repo import get_session_by_id, get_sessions_by_teacher
from app.repositories.verification_repo import create_codes, get_codes_by_teacher
from app.services.analysis_service import generate_ai_analysis
from app.services.verification_service import generate_verification_codes

router = APIRouter(prefix="/api/teacher", tags=["teacher"])


# === Schemas ===

class ExamAccessOut(BaseModel):
    exam_id: str
    name: str


class GenerateCodesRequest(BaseModel):
    exam_id: str
    prefix: str
    count: int
    start_number: int = 1


class CodeOut(BaseModel):
    code: str
    prefix: str
    student_number: str
    status: str
    exam_id: str
    created_at: datetime


class SessionOut(BaseModel):
    session_id: str
    student_name: str
    exam_id: str
    code: str
    status: str
    started_at: datetime
    completed_at: datetime | None


class SessionDetailOut(SessionOut):
    assessment: dict | None
    ai_analysis: dict | None


class TeacherScoringRequest(BaseModel):
    verification_code: str
    student_name: str
    exam_id: str
    results: list[dict]  # [{"question_id": str, "score": float}]


# === Endpoints ===

@router.get("/exams", response_model=list[ExamAccessOut])
async def list_teacher_exams(
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """取得教師可用的試卷列表。Admin 可看到所有試卷。"""
    if user.role == "admin":
        result = await db.execute(
            select(ExamTemplateRecord).where(ExamTemplateRecord.is_active.is_(True))
        )
        templates = result.scalars().all()
    else:
        result = await db.execute(
            select(ExamTemplateRecord)
            .join(TeacherExamAccess)
            .where(
                TeacherExamAccess.teacher_id == user.id,
                ExamTemplateRecord.is_active.is_(True),
            )
        )
        templates = result.scalars().all()

    return [ExamAccessOut(exam_id=t.exam_id, name=t.name) for t in templates]


@router.post("/codes/generate", response_model=list[CodeOut])
async def generate_codes(
    body: GenerateCodesRequest,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """產生驗證碼（批次）。"""
    # 驗證試卷存在
    result = await db.execute(
        select(ExamTemplateRecord).where(ExamTemplateRecord.exam_id == body.exam_id)
    )
    template_record = result.scalar_one_or_none()
    if template_record is None:
        raise HTTPException(status_code=404, detail="試卷不存在")

    try:
        codes = generate_verification_codes(
            prefix=body.prefix,
            count=body.count,
            teacher_id=user.id,
            exam_template_id=template_record.id,
            start_number=body.start_number,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    created = await create_codes(db, codes)
    return [
        CodeOut(
            code=c.code,
            prefix=c.prefix,
            student_number=c.student_number,
            status=c.status,
            exam_id=body.exam_id,
            created_at=c.created_at,
        )
        for c in created
    ]


@router.get("/codes", response_model=list[CodeOut])
async def list_codes(
    exam_id: str | None = None,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """取得教師的驗證碼列表。"""
    codes = await get_codes_by_teacher(db, user.id, exam_id)
    return [
        CodeOut(
            code=c.code,
            prefix=c.prefix,
            student_number=c.student_number,
            status=c.status,
            exam_id=c.exam_template.exam_id if c.exam_template else "",
            created_at=c.created_at,
        )
        for c in codes
    ]


@router.get("/results", response_model=list[SessionOut])
async def list_results(
    exam_id: str | None = None,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """取得學生成績列表。"""
    sessions = await get_sessions_by_teacher(db, user.id, exam_id)
    return [
        SessionOut(
            session_id=str(s.id),
            student_name=s.student_name,
            exam_id=s.exam_id,
            code=s.verification_code.code if s.verification_code else "",
            status=s.status,
            started_at=s.started_at,
            completed_at=s.completed_at,
        )
        for s in sessions
    ]


@router.get("/results/{session_id}", response_model=SessionDetailOut)
async def get_result_detail(
    session_id: str,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """取得個別學生的詳細報告。"""
    import uuid as uuid_mod

    try:
        sid = uuid_mod.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的 session ID")

    session = await get_session_by_id(db, sid)
    if session is None:
        raise HTTPException(status_code=404, detail="找不到該測驗紀錄")

    # 確認是該教師的學生
    if session.verification_code and session.verification_code.teacher_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="無權查看此紀錄")

    return SessionDetailOut(
        session_id=str(session.id),
        student_name=session.student_name,
        exam_id=session.exam_id,
        code=session.verification_code.code if session.verification_code else "",
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        assessment=session.assessment,
        ai_analysis=session.ai_analysis,
    )


@router.post("/scoring", response_model=SessionDetailOut)
async def teacher_scoring(
    body: TeacherScoringRequest,
    request: Request,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """教師手動評分：輸入驗證碼的每題得分，系統計算評估結果。"""
    # 查詢驗證碼
    result = await db.execute(
        select(VerificationCode).where(VerificationCode.code == body.verification_code)
    )
    vc = result.scalar_one_or_none()
    if vc is None:
        raise HTTPException(status_code=404, detail="驗證碼不存在")

    if vc.teacher_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="無權操作此驗證碼")

    # 取得 ExamTemplate（從 registry）
    registry = request.app.state.registry
    template = registry.get(body.exam_id)
    if template is None:
        raise HTTPException(status_code=404, detail="找不到試卷")

    # 建立 submission 並評分
    submission = ExamSubmission(
        student_name=body.student_name,
        exam_id=body.exam_id,
        results=[QuestionResult(question_id=r["question_id"], score=r["score"]) for r in body.results],
    )

    try:
        assessment = generate_assessment(template, submission)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # AI 分析（可選）
    ai_analysis_data = None
    llm_client = request.app.state.llm_client
    if llm_client:
        try:
            ai_result = await generate_ai_analysis(assessment, llm_client)
            ai_analysis_data = ai_result.model_dump()
        except Exception:
            pass  # AI 失敗不阻擋評分

    # 建立或更新 session
    result = await db.execute(
        select(ExamSession).where(ExamSession.verification_code_id == vc.id)
    )
    session = result.scalar_one_or_none()

    if session is None:
        vc.status = "completed"
        session = ExamSession(
            verification_code_id=vc.id,
            student_name=body.student_name,
            exam_id=body.exam_id,
            results={r["question_id"]: r["score"] for r in body.results},
            assessment=assessment.model_dump(),
            ai_analysis=ai_analysis_data,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )
        db.add(session)
    else:
        session.results = {r["question_id"]: r["score"] for r in body.results}
        session.assessment = assessment.model_dump()
        session.ai_analysis = ai_analysis_data
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        vc.status = "completed"

    await db.commit()
    await db.refresh(session)

    return SessionDetailOut(
        session_id=str(session.id),
        student_name=session.student_name,
        exam_id=session.exam_id,
        code=vc.code,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        assessment=session.assessment,
        ai_analysis=session.ai_analysis,
    )
