"""小五入班檢測試卷定義：包含 10 個單元共 44 題的題目結構與權重配置。"""

from app.domain.models import (
    ExamTemplate,
    KnowledgePointCategory,
    MathLiteracyDimension,
    QuestionDefinition,
    SectionDefinition,
)
from app.domain.exam_registry import ExamRegistry

KP = KnowledgePointCategory
ML = MathLiteracyDimension


def _q(qid: str, kp: KP, dw: float, lw: dict[ML, float]) -> QuestionDefinition:
    """建立 QuestionDefinition 的快捷函式，簡化題目定義的重複程式碼。"""
    return QuestionDefinition(
        question_id=qid, knowledge_point=kp, difficulty_weight=dw, literacy_weights=lw,
    )


# --- Section 1: 正整數運算思維 (5題) ---
_sec1 = SectionDefinition(
    section_id="sec-1", name="正整數運算思維", knowledge_point=KP.INTEGER,
    questions=[
        _q("1-1", KP.INTEGER, 0.2, {ML.CONCEPTUAL_UNDERSTANDING: 1.0}),
        _q("1-2", KP.INTEGER, 0.4, {ML.CONCEPTUAL_UNDERSTANDING: 0.5, ML.COMPUTATIONAL_FLUENCY: 0.8}),
        _q("1-3", KP.INTEGER, 0.6, {ML.COMPUTATIONAL_FLUENCY: 1.0}),
        _q("1-4", KP.INTEGER, 0.8, {ML.CONCEPTUAL_UNDERSTANDING: 0.5, ML.LOGICAL_REASONING: 0.7}),
        _q("1-5", KP.INTEGER, 1.0, {ML.CONTEXTUAL_STRATEGY: 0.8, ML.COMPUTATIONAL_FLUENCY: 0.5}),
    ],
)

# --- Section 2: 小數思維 (5題) ---
_sec2 = SectionDefinition(
    section_id="sec-2", name="小數思維", knowledge_point=KP.DECIMAL,
    questions=[
        _q("2-1", KP.DECIMAL, 0.2, {ML.CONCEPTUAL_UNDERSTANDING: 1.0}),
        _q("2-2", KP.DECIMAL, 0.4, {ML.COMPUTATIONAL_FLUENCY: 1.0}),
        _q("2-3", KP.DECIMAL, 0.6, {ML.COMPUTATIONAL_FLUENCY: 0.8, ML.CONCEPTUAL_UNDERSTANDING: 0.4}),
        _q("2-4", KP.DECIMAL, 0.8, {ML.LOGICAL_REASONING: 0.6, ML.COMPUTATIONAL_FLUENCY: 0.5}),
        _q("2-5", KP.DECIMAL, 1.0, {ML.CONTEXTUAL_STRATEGY: 0.9, ML.COMPUTATIONAL_FLUENCY: 0.4}),
    ],
)

# --- Section 3: 分數思維 (5題) ---
_sec3 = SectionDefinition(
    section_id="sec-3", name="分數思維", knowledge_point=KP.FRACTION,
    questions=[
        _q("3-1", KP.FRACTION, 0.2, {ML.CONCEPTUAL_UNDERSTANDING: 1.0}),
        _q("3-2", KP.FRACTION, 0.4, {ML.CONCEPTUAL_UNDERSTANDING: 0.6, ML.COMPUTATIONAL_FLUENCY: 0.6}),
        _q("3-3", KP.FRACTION, 0.6, {ML.COMPUTATIONAL_FLUENCY: 1.0}),
        _q("3-4", KP.FRACTION, 0.8, {ML.COMPUTATIONAL_FLUENCY: 0.7, ML.LOGICAL_REASONING: 0.5}),
        _q("3-5", KP.FRACTION, 1.0, {ML.CONTEXTUAL_STRATEGY: 0.8, ML.COMPUTATIONAL_FLUENCY: 0.5}),
    ],
)

# --- Section 4: 容積與面積問題 (4題) ---
_sec4 = SectionDefinition(
    section_id="sec-4", name="容積與面積問題", knowledge_point=KP.VOLUME,
    questions=[
        _q("4-1", KP.VOLUME, 0.3, {ML.CONCEPTUAL_UNDERSTANDING: 0.8, ML.COMPUTATIONAL_FLUENCY: 0.4}),
        _q("4-2", KP.VOLUME, 0.5, {ML.COMPUTATIONAL_FLUENCY: 1.0}),
        _q("4-3", KP.VOLUME, 0.7, {ML.CONTEXTUAL_STRATEGY: 0.7, ML.COMPUTATIONAL_FLUENCY: 0.5}),
        _q("4-4", KP.VOLUME, 1.0, {ML.CONTEXTUAL_STRATEGY: 0.9, ML.LOGICAL_REASONING: 0.4}),
    ],
)

# --- Section 5: 距離問題與單位換算 (5題) ---
_sec5 = SectionDefinition(
    section_id="sec-5", name="距離問題與單位換算", knowledge_point=KP.DISTANCE,
    questions=[
        _q("5-1", KP.DISTANCE, 0.2, {ML.CONCEPTUAL_UNDERSTANDING: 1.0}),
        _q("5-2", KP.DISTANCE, 0.4, {ML.COMPUTATIONAL_FLUENCY: 0.8, ML.CONCEPTUAL_UNDERSTANDING: 0.3}),
        _q("5-3", KP.DISTANCE, 0.6, {ML.COMPUTATIONAL_FLUENCY: 0.7, ML.CONTEXTUAL_STRATEGY: 0.5}),
        _q("5-4", KP.DISTANCE, 0.8, {ML.CONTEXTUAL_STRATEGY: 0.8, ML.COMPUTATIONAL_FLUENCY: 0.4}),
        _q("5-5", KP.DISTANCE, 1.0, {ML.CONTEXTUAL_STRATEGY: 1.0, ML.LOGICAL_REASONING: 0.3}),
    ],
)

# --- Section 6: 時間問題 (5題) ---
_sec6 = SectionDefinition(
    section_id="sec-6", name="時間問題", knowledge_point=KP.TIME,
    questions=[
        _q("6-1", KP.TIME, 0.2, {ML.CONCEPTUAL_UNDERSTANDING: 1.0}),
        _q("6-2", KP.TIME, 0.4, {ML.COMPUTATIONAL_FLUENCY: 0.8, ML.CONCEPTUAL_UNDERSTANDING: 0.4}),
        _q("6-3", KP.TIME, 0.6, {ML.COMPUTATIONAL_FLUENCY: 0.6, ML.CONTEXTUAL_STRATEGY: 0.6}),
        _q("6-4", KP.TIME, 0.8, {ML.CONTEXTUAL_STRATEGY: 0.9, ML.LOGICAL_REASONING: 0.3}),
        _q("6-5", KP.TIME, 1.0, {ML.LOGICAL_REASONING: 0.7, ML.CONTEXTUAL_STRATEGY: 0.6}),
    ],
)

# --- Section 7: 應用問題解題策略 (5題) ---
_sec7 = SectionDefinition(
    section_id="sec-7", name="應用問題解題策略", knowledge_point=KP.PROBLEM_SOLVING,
    questions=[
        _q("7-1", KP.PROBLEM_SOLVING, 0.2, {ML.CONTEXTUAL_STRATEGY: 0.8, ML.CONCEPTUAL_UNDERSTANDING: 0.4}),
        _q("7-2", KP.PROBLEM_SOLVING, 0.4, {ML.CONTEXTUAL_STRATEGY: 0.9, ML.COMPUTATIONAL_FLUENCY: 0.3}),
        _q("7-3", KP.PROBLEM_SOLVING, 0.6, {ML.CONTEXTUAL_STRATEGY: 1.0, ML.LOGICAL_REASONING: 0.4}),
        _q("7-4", KP.PROBLEM_SOLVING, 0.8, {ML.CONTEXTUAL_STRATEGY: 0.8, ML.LOGICAL_REASONING: 0.6}),
        _q("7-5", KP.PROBLEM_SOLVING, 1.0, {ML.LOGICAL_REASONING: 0.8, ML.CONTEXTUAL_STRATEGY: 0.7}),
    ],
)

# --- Section 8: 規律推演 (5題) ---
_sec8 = SectionDefinition(
    section_id="sec-8", name="規律推演", knowledge_point=KP.PATTERN,
    questions=[
        _q("8-1", KP.PATTERN, 0.2, {ML.LOGICAL_REASONING: 0.8, ML.CONCEPTUAL_UNDERSTANDING: 0.4}),
        _q("8-2", KP.PATTERN, 0.4, {ML.LOGICAL_REASONING: 1.0}),
        _q("8-3", KP.PATTERN, 0.6, {ML.LOGICAL_REASONING: 0.9, ML.CONTEXTUAL_STRATEGY: 0.3}),
        _q("8-4", KP.PATTERN, 0.8, {ML.LOGICAL_REASONING: 1.0, ML.COMPUTATIONAL_FLUENCY: 0.3}),
        _q("8-5", KP.PATTERN, 1.0, {ML.LOGICAL_REASONING: 1.0, ML.CONTEXTUAL_STRATEGY: 0.5}),
    ],
)

# --- Section 9: 面積與立方體問題 (2大題) ---
_sec9 = SectionDefinition(
    section_id="sec-9", name="面積與立方體問題", knowledge_point=KP.AREA_CUBE,
    questions=[
        _q("9-1", KP.AREA_CUBE, 0.5, {ML.CONCEPTUAL_UNDERSTANDING: 0.6, ML.COMPUTATIONAL_FLUENCY: 0.7}),
        _q("9-2", KP.AREA_CUBE, 1.0, {ML.LOGICAL_REASONING: 0.7, ML.CONCEPTUAL_UNDERSTANDING: 0.5}),
    ],
)

# --- Section 10: 資優思維 (3題) ---
_sec10 = SectionDefinition(
    section_id="sec-10", name="資優思維", knowledge_point=KP.GIFTED,
    questions=[
        _q("10-1", KP.GIFTED, 0.6, {ML.COMPUTATIONAL_FLUENCY: 0.8, ML.LOGICAL_REASONING: 0.5}),
        _q("10-2", KP.GIFTED, 0.8, {ML.LOGICAL_REASONING: 0.9, ML.COMPUTATIONAL_FLUENCY: 0.4}),
        _q("10-3", KP.GIFTED, 1.0, {ML.LOGICAL_REASONING: 1.0, ML.CONTEXTUAL_STRATEGY: 0.6}),
    ],
)

# 組合 10 個單元共 44 題為完整測驗卷模板
grade5_entrance_template = ExamTemplate(
    exam_id="grade5_entrance",
    name="小五入班檢測",
    sections=[_sec1, _sec2, _sec3, _sec4, _sec5, _sec6, _sec7, _sec8, _sec9, _sec10],
)


def register_grade5_entrance(registry: ExamRegistry) -> None:
    """將小五入班檢測試卷模板註冊到指定的測驗卷註冊表中。"""
    registry.register(grade5_entrance_template)
