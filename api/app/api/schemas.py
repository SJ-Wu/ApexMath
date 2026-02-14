"""API 請求與回應模型（Schema）：與領域模型分離，專責 HTTP 序列化與驗證。"""

from pydantic import BaseModel, Field

from app.domain.models import (
    KnowledgePointCategory,
    MathLiteracyDimension,
)


class QuestionResultIn(BaseModel):
    """請求用：單題作答結果，score 為 0.0～1.0 的得分率。"""

    question_id: str
    score: float = Field(ge=0.0, le=1.0)


class ExamSubmissionIn(BaseModel):
    """請求用：學生整份測驗的作答提交。"""

    student_name: str
    exam_id: str
    results: list[QuestionResultIn] = Field(default_factory=list)


class KnowledgePointScoreOut(BaseModel):
    """回應用：單一知識點類別的評分結果。"""

    category: KnowledgePointCategory
    score: float


class MathLiteracyScoreOut(BaseModel):
    """回應用：單一數學素養維度的評分結果。"""

    dimension: MathLiteracyDimension
    score: float


class AssessmentResultOut(BaseModel):
    """回應用：完整評估結果，包含知識點分數與數學素養分數。"""

    student_name: str
    exam_id: str
    knowledge_point_scores: list[KnowledgePointScoreOut]
    math_literacy_scores: list[MathLiteracyScoreOut]


class AIAnalysisOut(BaseModel):
    """回應用：AI 分析結果，包含弱點分析與強化建議。"""

    weakness_analysis: str
    enhancement_suggestions: str


class AssessmentWithAnalysisOut(BaseModel):
    """回應用：完整評估結果 + AI 分析。"""

    student_name: str
    exam_id: str
    knowledge_point_scores: list[KnowledgePointScoreOut]
    math_literacy_scores: list[MathLiteracyScoreOut]
    ai_analysis: AIAnalysisOut


class ExamListOut(BaseModel):
    """回應用：可用測驗卷 ID 清單。"""

    exam_ids: list[str]
