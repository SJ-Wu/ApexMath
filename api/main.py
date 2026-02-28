"""FastAPI 應用程式入口：負責組裝各元件並啟動 ApexMath 服務。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_router import router as admin_router
from app.api.router import router as exam_router
from app.api.student_router import router as student_router
from app.api.teacher_router import router as teacher_router
from app.auth.router import router as auth_router
from app.core.config import settings
from app.data.grade5_entrance import register_grade5_entrance
from app.db.engine import async_session_factory, engine
from app.db.models import Base
from app.db.seed import run_seed
from app.domain.exam_registry import ExamRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理：啟動時建表與 seed，關閉時清理連線池。"""
    # Startup: 建立資料庫表（開發用，正式環境改用 alembic migrate）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed 預設資料
    async with async_session_factory() as session:
        await run_seed(session)

    # 保留記憶體 ExamRegistry 以相容既有 scoring 流程
    registry = ExamRegistry()
    register_grade5_entrance(registry)
    app.state.registry = registry

    # 若有設定 OPENAI_API_KEY，啟用 AI 分析功能
    if settings.openai_api_key:
        from app.services.llm_client import OpenAIClient
        app.state.llm_client = OpenAIClient(api_key=settings.openai_api_key)
    else:
        app.state.llm_client = None

    yield

    # Shutdown: 關閉連線池
    await engine.dispose()


app = FastAPI(title="ApexMath 峰數學能力檢測平台", lifespan=lifespan)

# CORS 設定
_cors_origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(auth_router)
app.include_router(exam_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "ApexMath 峰數學能力檢測平台"}
