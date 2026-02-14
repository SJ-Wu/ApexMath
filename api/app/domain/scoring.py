"""純函式評分引擎：根據測驗卷模板與學生作答，計算知識點與數學素養分數。"""

from collections import defaultdict

from app.domain.models import (
    AssessmentResult,
    ExamSubmission,
    ExamTemplate,
    KnowledgePointCategory,
    KnowledgePointScore,
    MathLiteracyDimension,
    MathLiteracyScore,
)


def _build_score_map(template: ExamTemplate, submission: ExamSubmission) -> dict[str, float]:
    """建立 question_id → 得分率 的映射表。

    驗證提交的每一題 ID 皆存在於測驗卷模板中，
    若遇到無效 ID 則拋出 ValueError。
    未作答的題目不會出現在映射表中（後續計算視為 0 分）。
    """
    valid_ids = {q.question_id for q in template.get_all_questions()}
    score_map: dict[str, float] = {}
    for r in submission.results:
        if r.question_id not in valid_ids:
            raise ValueError(f"Invalid question_id: {r.question_id}")
        score_map[r.question_id] = r.score
    return score_map


def calculate_knowledge_point_scores(
    template: ExamTemplate, submission: ExamSubmission,
) -> list[KnowledgePointScore]:
    """計算各知識點類別的加權分數。

    公式：score = (Σ(答題得分率 × difficulty_weight) / Σ(difficulty_weight)) × 5
    結果為 0～5 分，涵蓋全部十大知識點類別。
    """
    score_map = _build_score_map(template, submission)

    weighted_num: dict[KnowledgePointCategory, float] = defaultdict(float)  # 加權分子
    weighted_den: dict[KnowledgePointCategory, float] = defaultdict(float)  # 加權分母

    for q in template.get_all_questions():
        student_score = score_map.get(q.question_id, 0.0)
        weighted_num[q.knowledge_point] += student_score * q.difficulty_weight  # 累加加權得分
        weighted_den[q.knowledge_point] += q.difficulty_weight  # 累加難度權重

    results = []
    for cat in KnowledgePointCategory:
        den = weighted_den.get(cat, 0.0)
        score = (weighted_num.get(cat, 0.0) / den * 5.0) if den > 0 else 0.0  # 加權平均再乘以滿分 5
        results.append(KnowledgePointScore(category=cat, score=round(score, 4)))
    return results


def calculate_math_literacy_scores(
    template: ExamTemplate, submission: ExamSubmission,
) -> list[MathLiteracyScore]:
    """計算各數學素養維度的加權分數。

    公式：score = (Σ(答題得分率 × literacy_weight) / Σ(literacy_weight)) × 5
    每題可同時貢獻多個素養維度，結果為 0～5 分。
    """
    score_map = _build_score_map(template, submission)

    weighted_num: dict[MathLiteracyDimension, float] = defaultdict(float)  # 加權分子
    weighted_den: dict[MathLiteracyDimension, float] = defaultdict(float)  # 加權分母

    for q in template.get_all_questions():
        student_score = score_map.get(q.question_id, 0.0)
        for dim, weight in q.literacy_weights.items():
            weighted_num[dim] += student_score * weight  # 累加加權得分
            weighted_den[dim] += weight  # 累加素養權重

    results = []
    for dim in MathLiteracyDimension:
        den = weighted_den.get(dim, 0.0)
        score = (weighted_num.get(dim, 0.0) / den * 5.0) if den > 0 else 0.0  # 加權平均再乘以滿分 5
        results.append(MathLiteracyScore(dimension=dim, score=round(score, 4)))
    return results


def generate_assessment(
    template: ExamTemplate, submission: ExamSubmission,
) -> AssessmentResult:
    """整合知識點分數與數學素養分數，產生完整的評估結果。"""
    return AssessmentResult(
        student_name=submission.student_name,
        exam_id=submission.exam_id,
        knowledge_point_scores=calculate_knowledge_point_scores(template, submission),
        math_literacy_scores=calculate_math_literacy_scores(template, submission),
    )
