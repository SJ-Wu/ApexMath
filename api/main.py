"""FastAPI 應用程式入口：負責組裝各元件並啟動 ApexMath 服務。"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router, set_llm_client, set_registry
from app.data.grade5_entrance import register_grade5_entrance
from app.domain.exam_registry import ExamRegistry

app = FastAPI(title="ApexMath 峰數學能力檢測平台")

# CORS 設定：允許前端跨域呼叫（Render 部署時 API 與前端在不同域名）
_cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 啟動流程：建立註冊表 → 註冊試卷 → 注入路由
registry = ExamRegistry()
register_grade5_entrance(registry)
set_registry(registry)

# 若有設定 OPENAI_API_KEY，啟用 AI 分析功能
_openai_api_key = os.environ.get("OPENAI_API_KEY")
if _openai_api_key:
    from app.services.llm_client import OpenAIClient

    set_llm_client(OpenAIClient(api_key=_openai_api_key))

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "ApexMath 峰數學能力檢測平台"}
