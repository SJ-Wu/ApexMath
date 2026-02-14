"""AI 分析服務：建構 prompt、呼叫 LLM、解析回應，產出弱點分析與強化建議。"""

import json

from app.domain.analysis_models import AIAnalysis
from app.domain.models import AssessmentResult, KnowledgePointCategory
from app.services.llm_client import LLMClient

# 知識點前後置依賴對照表：key 的學習需要先具備 values 中的知識點
KNOWLEDGE_POINT_DEPENDENCIES: dict[KnowledgePointCategory, list[KnowledgePointCategory]] = {
    KnowledgePointCategory.DECIMAL: [KnowledgePointCategory.INTEGER],
    KnowledgePointCategory.FRACTION: [KnowledgePointCategory.INTEGER, KnowledgePointCategory.DECIMAL],
    KnowledgePointCategory.VOLUME: [KnowledgePointCategory.INTEGER, KnowledgePointCategory.DECIMAL],
    KnowledgePointCategory.DISTANCE: [KnowledgePointCategory.INTEGER, KnowledgePointCategory.DECIMAL],
    KnowledgePointCategory.TIME: [KnowledgePointCategory.INTEGER],
    KnowledgePointCategory.PROBLEM_SOLVING: [
        KnowledgePointCategory.INTEGER,
        KnowledgePointCategory.DECIMAL,
        KnowledgePointCategory.FRACTION,
    ],
    KnowledgePointCategory.AREA_CUBE: [KnowledgePointCategory.INTEGER, KnowledgePointCategory.DECIMAL],
    KnowledgePointCategory.GIFTED: [
        KnowledgePointCategory.INTEGER,
        KnowledgePointCategory.DECIMAL,
        KnowledgePointCategory.FRACTION,
        KnowledgePointCategory.PATTERN,
    ],
}

WEAKNESS_THRESHOLD = 3.0

SYSTEM_PROMPT = """\
你是一位資深的國小數學教育專家，專門為學生提供數學能力診斷分析。
請根據學生的知識點分數與數學素養分數，以繁體中文產出分析報告。

回應格式必須是純 JSON（不要包裹在 code fence 中）：
{"weakness_analysis": "弱點分析內容", "enhancement_suggestions": "強化建議內容"}

分析原則：
1. 指出低於 3.0 分的弱項，解釋可能的原因
2. 追溯前置知識點，找出根本問題（例如分數弱可能源於正整數基礎不穩）
3. 提供具體、可執行的分層練習建議，從基礎到進階
4. 語氣溫和鼓勵，肯定學生的優勢領域，再引導改善弱項
5. 若所有分數都在 3.0 以上，仍可指出相對弱項並提供精進建議"""


def _build_user_message(result: AssessmentResult) -> str:
    """將評估結果轉為結構化文字訊息，供 LLM 分析使用。"""
    lines = [f"學生：{result.student_name}", f"測驗卷：{result.exam_id}", ""]

    # 知識點分數
    lines.append("【知識點能力分數（滿分 5.0）】")
    weak_categories: list[KnowledgePointCategory] = []
    for kp in result.knowledge_point_scores:
        marker = " ⚠ 弱項" if kp.score < WEAKNESS_THRESHOLD else ""
        lines.append(f"  {kp.category.value}：{kp.score:.1f}{marker}")
        if kp.score < WEAKNESS_THRESHOLD:
            weak_categories.append(kp.category)
    lines.append("")

    # 數學素養分數
    lines.append("【數學素養分數（滿分 5.0）】")
    for ml in result.math_literacy_scores:
        marker = " ⚠ 弱項" if ml.score < WEAKNESS_THRESHOLD else ""
        lines.append(f"  {ml.dimension.value}：{ml.score:.1f}{marker}")
    lines.append("")

    # 弱項前置依賴資訊
    if weak_categories:
        lines.append("【弱項前置知識點依賴關係】")
        for cat in weak_categories:
            deps = KNOWLEDGE_POINT_DEPENDENCIES.get(cat)
            if deps:
                dep_names = "、".join(d.value for d in deps)
                lines.append(f"  {cat.value} 的前置知識點：{dep_names}")
        lines.append("")

    return "\n".join(lines)


def _parse_llm_response(raw: str) -> AIAnalysis:
    """解析 LLM 回應為 AIAnalysis，處理可能的 code fence 包裹。"""
    text = raw.strip()
    # 移除可能的 code fence
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[: -3]
        text = text.strip()

    data = json.loads(text)
    return AIAnalysis(
        weakness_analysis=data["weakness_analysis"],
        enhancement_suggestions=data["enhancement_suggestions"],
    )


async def generate_ai_analysis(result: AssessmentResult, llm: LLMClient) -> AIAnalysis:
    """呼叫 LLM 產生 AI 分析報告。

    Raises:
        ValueError: LLM 回應格式無效（JSON 解析失敗或缺少必要欄位）
        Exception: LLM 呼叫本身的錯誤（網路、API key 等）
    """
    user_message = _build_user_message(result)
    raw_response = await llm.generate(SYSTEM_PROMPT, user_message)
    try:
        return _parse_llm_response(raw_response)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"LLM 回應格式無效: {e}") from e
