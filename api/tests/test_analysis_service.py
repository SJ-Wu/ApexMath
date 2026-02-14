"""測試 AI 分析服務：prompt 建構與 LLM 回應解析。"""

import json

import pytest

from app.domain.models import (
    AssessmentResult,
    KnowledgePointCategory,
    KnowledgePointScore,
    MathLiteracyDimension,
    MathLiteracyScore,
)
from app.services.analysis_service import (
    WEAKNESS_THRESHOLD,
    _build_user_message,
    generate_ai_analysis,
)


def _make_result(
    kp_scores: dict[KnowledgePointCategory, float] | None = None,
    ml_scores: dict[MathLiteracyDimension, float] | None = None,
) -> AssessmentResult:
    """輔助函式：建立測試用的 AssessmentResult。"""
    if kp_scores is None:
        kp_scores = {cat: 4.0 for cat in KnowledgePointCategory}
    if ml_scores is None:
        ml_scores = {dim: 4.0 for dim in MathLiteracyDimension}

    return AssessmentResult(
        student_name="測試生",
        exam_id="test_exam",
        knowledge_point_scores=[
            KnowledgePointScore(category=cat, score=score) for cat, score in kp_scores.items()
        ],
        math_literacy_scores=[
            MathLiteracyScore(dimension=dim, score=score) for dim, score in ml_scores.items()
        ],
    )


class FakeLLMClient:
    """測試用的假 LLM 客戶端。"""

    def __init__(self, response: str):
        self.response = response
        self.calls: list[tuple[str, str]] = []

    async def generate(self, system_prompt: str, user_message: str) -> str:
        self.calls.append((system_prompt, user_message))
        return self.response


class TestBuildUserMessage:
    def test_contains_student_name(self):
        result = _make_result()
        msg = _build_user_message(result)
        assert "測試生" in msg

    def test_marks_weak_items(self):
        kp_scores = {cat: 4.0 for cat in KnowledgePointCategory}
        kp_scores[KnowledgePointCategory.FRACTION] = 2.0
        result = _make_result(kp_scores=kp_scores)
        msg = _build_user_message(result)
        assert "分數" in msg
        assert "⚠ 弱項" in msg

    def test_includes_dependency_info_for_weak_items(self):
        kp_scores = {cat: 4.0 for cat in KnowledgePointCategory}
        kp_scores[KnowledgePointCategory.FRACTION] = 2.0
        result = _make_result(kp_scores=kp_scores)
        msg = _build_user_message(result)
        assert "前置知識點" in msg
        assert "正整數" in msg
        assert "小數" in msg

    def test_no_dependency_section_when_no_weak_items(self):
        result = _make_result()
        msg = _build_user_message(result)
        assert "前置知識點依賴關係" not in msg

    def test_weak_item_without_dependencies(self):
        """正整數沒有前置依賴，弱項時不應顯示依賴資訊。"""
        kp_scores = {cat: 4.0 for cat in KnowledgePointCategory}
        kp_scores[KnowledgePointCategory.INTEGER] = 1.0
        result = _make_result(kp_scores=kp_scores)
        msg = _build_user_message(result)
        assert "⚠ 弱項" in msg
        # 依賴區段存在但正整數本身沒有前置依賴
        assert "正整數 的前置知識點" not in msg

    def test_math_literacy_weak_items(self):
        ml_scores = {dim: 4.0 for dim in MathLiteracyDimension}
        ml_scores[MathLiteracyDimension.COMPUTATIONAL_FLUENCY] = 1.5
        result = _make_result(ml_scores=ml_scores)
        msg = _build_user_message(result)
        assert "計算流暢度" in msg
        assert "⚠ 弱項" in msg


class TestGenerateAIAnalysis:
    async def test_valid_json_response(self):
        response = json.dumps({
            "weakness_analysis": "分數基礎不穩",
            "enhancement_suggestions": "建議從正整數開始複習",
        })
        fake_llm = FakeLLMClient(response)
        result = _make_result()
        analysis = await generate_ai_analysis(result, fake_llm)
        assert analysis.weakness_analysis == "分數基礎不穩"
        assert analysis.enhancement_suggestions == "建議從正整數開始複習"
        assert len(fake_llm.calls) == 1

    async def test_json_in_code_fence(self):
        inner = json.dumps({
            "weakness_analysis": "弱點",
            "enhancement_suggestions": "建議",
        })
        response = f"```json\n{inner}\n```"
        fake_llm = FakeLLMClient(response)
        result = _make_result()
        analysis = await generate_ai_analysis(result, fake_llm)
        assert analysis.weakness_analysis == "弱點"
        assert analysis.enhancement_suggestions == "建議"

    async def test_invalid_json_raises_value_error(self):
        fake_llm = FakeLLMClient("this is not json")
        result = _make_result()
        with pytest.raises(ValueError, match="LLM 回應格式無效"):
            await generate_ai_analysis(result, fake_llm)

    async def test_missing_key_raises_value_error(self):
        response = json.dumps({"weakness_analysis": "弱點"})
        fake_llm = FakeLLMClient(response)
        result = _make_result()
        with pytest.raises(ValueError, match="LLM 回應格式無效"):
            await generate_ai_analysis(result, fake_llm)
