"""驗證碼生成服務：產生格式化的驗證碼。"""

import uuid

from app.db.models import VerificationCode


def generate_verification_codes(
    prefix: str,
    count: int,
    teacher_id: uuid.UUID,
    exam_template_id: uuid.UUID,
    start_number: int = 1,
) -> list[VerificationCode]:
    """產生一批驗證碼。

    格式: {prefix}{001~999}，例如 APEX5A001, APEX5A002, ...

    Args:
        prefix: 英數前綴（6-12 字元）
        count: 要產生的數量（1-999）
        teacher_id: 教師 UUID
        exam_template_id: 試卷模板 UUID
        start_number: 起始編號（預設 1）

    Returns:
        VerificationCode ORM 物件列表
    """
    if not (1 <= len(prefix) <= 12):
        raise ValueError("前綴長度須為 1~12 個字元")
    if not prefix.isalnum():
        raise ValueError("前綴只能包含英文字母和數字")
    if not (1 <= count <= 999):
        raise ValueError("數量須為 1~999")
    if start_number + count - 1 > 999:
        raise ValueError("編號超出範圍（最大 999）")

    codes = []
    for i in range(count):
        num = start_number + i
        student_number = f"{num:03d}"
        code_str = f"{prefix}{student_number}"
        codes.append(
            VerificationCode(
                code=code_str,
                prefix=prefix,
                student_number=student_number,
                teacher_id=teacher_id,
                exam_template_id=exam_template_id,
            )
        )
    return codes
