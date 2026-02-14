"""測驗卷註冊表：提供記憶體內的測驗卷模板管理功能。"""

from app.domain.models import ExamTemplate


class ExamRegistry:
    """記憶體內測驗卷管理器，以 exam_id 為鍵存放測驗卷模板。"""

    def __init__(self) -> None:
        self._templates: dict[str, ExamTemplate] = {}

    def register(self, template: ExamTemplate) -> None:
        """註冊一份測驗卷模板，若 exam_id 已存在則拋出 ValueError。"""
        if template.exam_id in self._templates:
            raise ValueError(f"Exam already registered: {template.exam_id}")
        self._templates[template.exam_id] = template

    def get(self, exam_id: str) -> ExamTemplate | None:
        """依 exam_id 取得測驗卷模板，找不到時回傳 None。"""
        return self._templates.get(exam_id)

    def list_ids(self) -> list[str]:
        """列出所有已註冊的測驗卷 ID。"""
        return list(self._templates.keys())
