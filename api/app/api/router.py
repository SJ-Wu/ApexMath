"""API 路由層：定義 RESTful 端點，銜接 HTTP 請求與領域邏輯。"""

from fastapi import APIRouter, Depends, HTTPException, Request

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


def _get_registry(request: Request) -> ExamRegistry:
    """從 app.state 取得 ExamRegistry 實例。"""
    return request.app.state.registry


def _get_llm_client(request: Request) -> LLMClient | None:
    """從 app.state 取得 LLM 客戶端實例（可能為 None）。"""
    return request.app.state.llm_client


@router.get("/exams", response_model=ExamListOut)
async def list_exams(registry: ExamRegistry = Depends(_get_registry)):
    """列出所有可用的測驗卷 ID。"""
    return ExamListOut(exam_ids=registry.list_ids())


@router.get("/exams/{exam_id}", response_model=ExamTemplate)
async def get_exam(exam_id: str, registry: ExamRegistry = Depends(_get_registry)):
    """取得指定測驗卷的完整模板，找不到時回傳 404。"""
    template = registry.get(exam_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Exam not found: {exam_id}")
    return template


@router.post("/exams/{exam_id}/assess", response_model=AssessmentResultOut)
async def assess(
    exam_id: str,
    body: ExamSubmissionIn,
    registry: ExamRegistry = Depends(_get_registry),
):
    """提交學生作答並取得評估結果。

    驗證 exam_id 存在且與 body 一致，無效的 question_id 回傳 422。
    """
    template = registry.get(exam_id)
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
async def assess_with_analysis(
    exam_id: str,
    body: ExamSubmissionIn,
    registry: ExamRegistry = Depends(_get_registry),
    llm_client: LLMClient | None = Depends(_get_llm_client),
):
    """提交學生作答並取得評估結果與 AI 分析報告。

    複用 assess 的驗證邏輯與評分引擎，額外呼叫 LLM 產出弱點分析與強化建議。
    LLM 未設定時回傳 503，LLM 呼叫失敗時回傳 502。
    """
    if llm_client is None:
        raise HTTPException(status_code=503, detail="AI 分析服務未啟用（未設定 LLM 客戶端）")

    template = registry.get(exam_id)
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
        analysis = await generate_ai_analysis(result, llm_client)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"AI 分析回應格式錯誤: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 分析服務呼叫失敗: {e}")

    return AssessmentWithAnalysisOut.model_validate(
        {**result.model_dump(), "ai_analysis": analysis.model_dump()}
    )
