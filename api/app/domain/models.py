"""領域模型定義：定義峰數學能力檢測平台的所有核心實體與值物件。"""

from enum import Enum

from pydantic import BaseModel, Field


class KnowledgePointCategory(str, Enum):
    """十大知識點類別，涵蓋九大基礎單元與資優挑戰。"""

    INTEGER = "正整數"
    DECIMAL = "小數"
    FRACTION = "分數"
    VOLUME = "容積"
    DISTANCE = "距離問題"
    TIME = "時間問題"
    PROBLEM_SOLVING = "解題策略"
    PATTERN = "規律推演"
    AREA_CUBE = "面積/立方體"
    GIFTED = "資優挑戰"


class MathLiteracyDimension(str, Enum):
    """四大數學素養維度，用於雷達圖評估。"""

    CONCEPTUAL_UNDERSTANDING = "概念理解"
    COMPUTATIONAL_FLUENCY = "計算流暢度"
    CONTEXTUAL_STRATEGY = "情境策略與脈絡素養"
    LOGICAL_REASONING = "邏輯推理"


class QuestionDefinition(BaseModel):
    """單題定義，描述一道題目所評量的知識點與數學素養權重。"""

    question_id: str
    knowledge_point: KnowledgePointCategory
    difficulty_weight: float = Field(gt=0)  # 難度權重，值越大代表越難
    literacy_weights: dict[MathLiteracyDimension, float] = Field(min_length=1)  # 各素養維度的權重分配


class SectionDefinition(BaseModel):
    """單元定義，將同一知識點類別的題目組成一個測驗單元。"""

    section_id: str
    name: str
    knowledge_point: KnowledgePointCategory
    questions: list[QuestionDefinition]


class ExamTemplate(BaseModel):
    """測驗卷模板，包含多個單元，定義一份完整測驗的結構。"""

    exam_id: str
    name: str
    sections: list[SectionDefinition]

    def get_all_questions(self) -> list[QuestionDefinition]:
        """取得測驗卷中所有單元的全部題目，攤平為一維清單。"""
        return [q for s in self.sections for q in s.questions]


class QuestionResult(BaseModel):
    """學生單題作答結果，score 為 0.0～1.0 的得分率。"""

    question_id: str
    score: float = Field(ge=0.0, le=1.0)


class ExamSubmission(BaseModel):
    """學生整份測驗的作答提交，包含學生姓名與各題作答結果。"""

    student_name: str
    exam_id: str
    results: list[QuestionResult] = Field(default_factory=list)


class KnowledgePointScore(BaseModel):
    """單一知識點類別的評分結果，分數範圍 0～5。"""

    category: KnowledgePointCategory
    score: float = Field(ge=0.0, le=5.0)


class MathLiteracyScore(BaseModel):
    """單一數學素養維度的評分結果，分數範圍 0～5。"""

    dimension: MathLiteracyDimension
    score: float = Field(ge=0.0, le=5.0)


class AssessmentResult(BaseModel):
    """完整評估結果，整合知識點分數與數學素養分數。"""

    student_name: str
    exam_id: str
    knowledge_point_scores: list[KnowledgePointScore]
    math_literacy_scores: list[MathLiteracyScore]
