"""測試設定：提供共用 fixtures。"""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient

from app.api.router import router as exam_router
from app.data.grade5_entrance import grade5_entrance_template, register_grade5_entrance
from app.domain.exam_registry import ExamRegistry


@pytest.fixture()
def registry():
    """提供一個已註冊小五試卷的 ExamRegistry。"""
    r = ExamRegistry()
    register_grade5_entrance(r)
    return r


@pytest.fixture()
def template():
    """提供小五入班檢測試卷模板。"""
    return grade5_entrance_template


def create_test_app(llm_client=None):
    """建立不依賴資料庫的測試用 FastAPI 應用程式。"""
    test_app = FastAPI()
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(exam_router)

    # 直接設定 state，不需要 lifespan
    registry = ExamRegistry()
    register_grade5_entrance(registry)
    test_app.state.registry = registry
    test_app.state.llm_client = llm_client

    @test_app.get("/")
    async def root():
        return {"message": "ApexMath 測試"}

    return test_app


@pytest.fixture()
def test_app():
    """提供測試用 FastAPI app（無 LLM client）。"""
    return create_test_app()


@pytest.fixture()
def client(test_app):
    """提供測試用 HTTP client。"""
    transport = ASGITransport(app=test_app)
    return AsyncClient(transport=transport, base_url="http://test")
