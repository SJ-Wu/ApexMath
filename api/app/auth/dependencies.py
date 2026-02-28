"""認證依賴注入：提供 FastAPI 路由用的使用者驗證函式。"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_access_token
from app.db.engine import get_db
from app.db.models import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """從 Bearer token 解析當前使用者，驗證失敗時拋出 401。"""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無效的認證 token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 缺少使用者資訊")

    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在或已停用")

    return user


def require_role(*roles: str):
    """建立角色檢查依賴，限定指定角色才能存取。

    用法: Depends(require_role("admin")) 或 Depends(require_role("admin", "teacher"))
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="權限不足")
        return user

    return role_checker


async def get_student_session_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """從 Bearer token 解析學生 session 資訊（不需要使用者帳號）。"""
    payload = decode_access_token(credentials.credentials)
    if payload is None or payload.get("type") != "student_session":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無效的學生 session token")
    return payload
