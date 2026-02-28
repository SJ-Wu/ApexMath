"""學生測驗路由：驗證碼驗證後的作答與結果查詢。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_student_session_payload
from app.db.engine import get_db
from app.db.models import ExamSession, ExamTemplateRecord, VerificationCode
from app.domain.models import ExamSubmission, ExamTemplate, QuestionResult
from app.domain.scoring import generate_assessment
from app.services.analysis_service import generate_ai_analysis

router = APIRouter(prefix="/api/student", tags=["student"])


# === Schemas ===

class ExamContentOut(BaseModel):
    exam_id: str
    name: str
    session_id: str
    student_name: str
    template: dict  # 完整 ExamTemplate JSON


class SubmitAnswersRequest(BaseModel):
    results: list[dict]  # [{"question_id": str, "score": float}]


class ExamResultOut(BaseModel):
    student_name: str
    exam_id: str
    status: str
    assessment: dict | None
    ai_analysis: dict | None


# === Endpoints ===

@router.get("/exam/{session_id}", response_model=ExamContentOut)
async def get_exam_content(
    session_id: str,
    payload: dict = Depends(get_student_session_payload),
    db: AsyncSession = Depends(get_db),
):
    """取得測驗內容（題目）。"""
    import uuid

    # 驗證 session 歸屬
    if payload.get("session_id") != session_id:
        raise HTTPException(status_code=403, detail="無權存取此測驗")

    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的 session ID")

    result = await db.execute(select(ExamSession).where(ExamSession.id == sid))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="找不到測驗紀錄")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="此測驗已完成，請查看結果")

    # 取得試卷模板
    result = await db.execute(
        select(ExamTemplateRecord).where(ExamTemplateRecord.exam_id == session.exam_id)
    )
    template_record = result.scalar_one_or_none()
    if template_record is None:
        raise HTTPException(status_code=404, detail="找不到試卷")

    return ExamContentOut(
        exam_id=session.exam_id,
        name=template_record.name,
        session_id=str(session.id),
        student_name=session.student_name,
        template=template_record.template_data,
    )


@router.post("/exam/{session_id}/submit", response_model=ExamResultOut)
async def submit_answers(
    session_id: str,
    body: SubmitAnswersRequest,
    request: Request,
    payload: dict = Depends(get_student_session_payload),
    db: AsyncSession = Depends(get_db),
):
    """提交學生作答，計算評分。"""
    import uuid

    if payload.get("session_id") != session_id:
        raise HTTPException(status_code=403, detail="無權存取此測驗")

    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的 session ID")

    result = await db.execute(select(ExamSession).where(ExamSession.id == sid))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="找不到測驗紀錄")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="此測驗已完成，不可重複提交")

    # 取得 ExamTemplate（從 registry）
    registry = request.app.state.registry
    template = registry.get(session.exam_id)
    if template is None:
        raise HTTPException(status_code=404, detail="找不到試卷")

    # 評分
    submission = ExamSubmission(
        student_name=session.student_name,
        exam_id=session.exam_id,
        results=[QuestionResult(question_id=r["question_id"], score=r["score"]) for r in body.results],
    )

    try:
        assessment = generate_assessment(template, submission)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # AI 分析
    ai_analysis_data = None
    llm_client = request.app.state.llm_client
    if llm_client:
        try:
            ai_result = await generate_ai_analysis(assessment, llm_client)
            ai_analysis_data = ai_result.model_dump()
        except Exception:
            pass

    # 更新 session
    session.answers = {r["question_id"]: r["score"] for r in body.results}
    session.results = {r["question_id"]: r["score"] for r in body.results}
    session.assessment = assessment.model_dump()
    session.ai_analysis = ai_analysis_data
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)

    # 更新驗證碼狀態
    vc_result = await db.execute(
        select(VerificationCode).where(VerificationCode.id == session.verification_code_id)
    )
    vc = vc_result.scalar_one_or_none()
    if vc:
        vc.status = "completed"

    await db.commit()

    return ExamResultOut(
        student_name=session.student_name,
        exam_id=session.exam_id,
        status=session.status,
        assessment=session.assessment,
        ai_analysis=session.ai_analysis,
    )


@router.get("/result/{session_id}", response_model=ExamResultOut)
async def get_exam_result(
    session_id: str,
    payload: dict = Depends(get_student_session_payload),
    db: AsyncSession = Depends(get_db),
):
    """取得測驗結果。"""
    import uuid

    if payload.get("session_id") != session_id:
        raise HTTPException(status_code=403, detail="無權存取此結果")

    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="無效的 session ID")

    result = await db.execute(select(ExamSession).where(ExamSession.id == sid))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="找不到測驗紀錄")

    return ExamResultOut(
        student_name=session.student_name,
        exam_id=session.exam_id,
        status=session.status,
        assessment=session.assessment,
        ai_analysis=session.ai_analysis,
    )
