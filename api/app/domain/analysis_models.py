"""AI 分析結果的領域模型。"""

from pydantic import BaseModel


class AIAnalysis(BaseModel):
    """AI 產出的弱點分析與強化建議。"""

    weakness_analysis: str
    enhancement_suggestions: str
