"""認證路由：登入與驗證碼驗證端點。"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, verify_password
from app.core.config import settings
from app.db.engine import get_db
from app.db.models import User, VerificationCode

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    display_name: str


class VerifyCodeRequest(BaseModel):
    code: str
    student_name: str


class VerifyCodeResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    exam_id: str
    session_id: str
    status: str  # "new" or "completed"


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Admin/Teacher 帳密登入，回傳 JWT token。"""
    result = await db.execute(
        select(User).where(User.username == body.username, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號或密碼錯誤")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return LoginResponse(access_token=token, role=user.role, display_name=user.display_name)


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(body: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    """學生輸入驗證碼，建立或取得測驗 session。"""
    from app.db.models import ExamSession, ExamTemplateRecord

    result = await db.execute(
        select(VerificationCode).where(VerificationCode.code == body.code)
    )
    vc = result.scalar_one_or_none()

    if vc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="驗證碼不存在")

    # 取得對應的 exam_id
    template_result = await db.execute(
        select(ExamTemplateRecord).where(ExamTemplateRecord.id == vc.exam_template_id)
    )
    template_record = template_result.scalar_one_or_none()
    if template_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="對應的試卷不存在")

    if vc.status == "completed":
        # 已完成的驗證碼 → 回傳結果 (唯讀)
        session_result = await db.execute(
            select(ExamSession).where(ExamSession.verification_code_id == vc.id)
        )
        session = session_result.scalar_one_or_none()
        if session is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="資料異常")

        token = create_access_token(
            {"type": "student_session", "session_id": str(session.id), "code_id": str(vc.id)},
            expires_minutes=settings.jwt_student_token_expire_minutes,
        )
        return VerifyCodeResponse(
            access_token=token,
            exam_id=template_record.exam_id,
            session_id=str(session.id),
            status="completed",
        )

    if vc.status == "in_progress":
        # 已開始但未完成 → 回傳現有 session
        session_result = await db.execute(
            select(ExamSession).where(ExamSession.verification_code_id == vc.id)
        )
        session = session_result.scalar_one_or_none()
        if session is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="資料異常")

        token = create_access_token(
            {"type": "student_session", "session_id": str(session.id), "code_id": str(vc.id)},
            expires_minutes=settings.jwt_student_token_expire_minutes,
        )
        return VerifyCodeResponse(
            access_token=token,
            exam_id=template_record.exam_id,
            session_id=str(session.id),
            status="in_progress",
        )

    # unused → 建立新 session
    vc.status = "in_progress"
    session = ExamSession(
        verification_code_id=vc.id,
        student_name=body.student_name,
        exam_id=template_record.exam_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    token = create_access_token(
        {"type": "student_session", "session_id": str(session.id), "code_id": str(vc.id)},
        expires_minutes=settings.jwt_student_token_expire_minutes,
    )
    return VerifyCodeResponse(
        access_token=token,
        exam_id=template_record.exam_id,
        session_id=str(session.id),
        status="new",
    )
