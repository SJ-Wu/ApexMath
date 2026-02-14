"""API 路由層：定義 RESTful 端點，銜接 HTTP 請求與領域邏輯。"""

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    AssessmentResultOut,
    AssessmentWithAnalysisOut,
    ExamListOut,
    ExamSubmissionIn,
)
from app.domain.exam_registry import ExamRegistry
from app.domain.models import ExamSubmission, ExamTemplate, QuestionResult
from app.domain.scoring import generate_assessment
from app.services.analysis_service import generate_ai_analysis
from app.services.llm_client import LLMClient

router = APIRouter(prefix="/api")

_registry: ExamRegistry | None = None
_llm_client: LLMClient | None = None


def set_registry(registry: ExamRegistry) -> None:
    """注入測驗卷註冊表實例，供路由端點使用。"""
    global _registry
    _registry = registry


def set_llm_client(client: LLMClient) -> None:
    """注入 LLM 客戶端實例，供 AI 分析端點使用。"""
    global _llm_client
    _llm_client = client


def _get_registry() -> ExamRegistry:
    """取得已注入的註冊表，若尚未初始化則觸發 AssertionError。"""
    assert _registry is not None, "Registry not initialized"
    return _registry


@router.get("/exams", response_model=ExamListOut)
async def list_exams():
    """列出所有可用的測驗卷 ID。"""
    return ExamListOut(exam_ids=_get_registry().list_ids())


@router.get("/exams/{exam_id}", response_model=ExamTemplate)
async def get_exam(exam_id: str):
    """取得指定測驗卷的完整模板，找不到時回傳 404。"""
    template = _get_registry().get(exam_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Exam not found: {exam_id}")
    return template


@router.post("/exams/{exam_id}/assess", response_model=AssessmentResultOut)
async def assess(exam_id: str, body: ExamSubmissionIn):
    """提交學生作答並取得評估結果。

    驗證 exam_id 存在且與 body 一致，無效的 question_id 回傳 422。
    """
    template = _get_registry().get(exam_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Exam not found: {exam_id}")

    if body.exam_id != exam_id:
        raise HTTPException(status_code=422, detail="exam_id in body does not match URL")

    submission = ExamSubmission(
        student_name=body.student_name,
        exam_id=body.exam_id,
        results=[QuestionResult(question_id=r.question_id, score=r.score) for r in body.results],
    )

    try:
        result = generate_assessment(template, submission)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return result


@router.post("/exams/{exam_id}/assess-with-analysis", response_model=AssessmentWithAnalysisOut)
async def assess_with_analysis(exam_id: str, body: ExamSubmissionIn):
    """提交學生作答並取得評估結果與 AI 分析報告。

    複用 assess 的驗證邏輯與評分引擎，額外呼叫 LLM 產出弱點分析與強化建議。
    LLM 未設定時回傳 503，LLM 呼叫失敗時回傳 502。
    """
    if _llm_client is None:
        raise HTTPException(status_code=503, detail="AI 分析服務未啟用（未設定 LLM 客戶端）")

    template = _get_registry().get(exam_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Exam not found: {exam_id}")

    if body.exam_id != exam_id:
        raise HTTPException(status_code=422, detail="exam_id in body does not match URL")

    submission = ExamSubmission(
        student_name=body.student_name,
        exam_id=body.exam_id,
        results=[QuestionResult(question_id=r.question_id, score=r.score) for r in body.results],
    )

    try:
        result = generate_assessment(template, submission)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        analysis = await generate_ai_analysis(result, _llm_client)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"AI 分析回應格式錯誤: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 分析服務呼叫失敗: {e}")

    return AssessmentWithAnalysisOut.model_validate(
        {**result.model_dump(), "ai_analysis": analysis.model_dump()}
    )
