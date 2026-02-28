"""測試 AI 分析 API 端點。"""

import json

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import create_test_app


class FakeLLMClient:
    """測試用假 LLM 客戶端。"""

    def __init__(self, response: str):
        self.response = response

    async def generate(self, system_prompt: str, user_message: str) -> str:
        return self.response


class ErrorLLMClient:
    """模擬 LLM 呼叫失敗的客戶端。"""

    async def generate(self, system_prompt: str, user_message: str) -> str:
        raise RuntimeError("API connection failed")


@pytest.fixture()
def _valid_payload():
    return {
        "student_name": "小明",
        "exam_id": "grade5_entrance",
        "results": [{"question_id": "1-1", "score": 1.0}],
    }


def _make_client(llm_client=None):
    app = create_test_app(llm_client=llm_client)
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestAssessWithAnalysis:
    async def test_success(self, _valid_payload):
        fake_response = json.dumps({
            "weakness_analysis": "小數和分數基礎需要加強",
            "enhancement_suggestions": "建議從正整數四則運算開始複習",
        })
        client = _make_client(FakeLLMClient(fake_response))
        resp = await client.post(
            "/api/exams/grade5_entrance/assess-with-analysis",
            json=_valid_payload,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_name"] == "小明"
        assert len(data["knowledge_point_scores"]) == 10
        assert len(data["math_literacy_scores"]) == 4
        assert data["ai_analysis"]["weakness_analysis"] == "小數和分數基礎需要加強"
        assert data["ai_analysis"]["enhancement_suggestions"] == "建議從正整數四則運算開始複習"

    async def test_no_llm_client_returns_503(self, _valid_payload):
        client = _make_client(None)
        resp = await client.post(
            "/api/exams/grade5_entrance/assess-with-analysis",
            json=_valid_payload,
        )
        assert resp.status_code == 503

    async def test_llm_error_returns_502(self, _valid_payload):
        client = _make_client(ErrorLLMClient())
        resp = await client.post(
            "/api/exams/grade5_entrance/assess-with-analysis",
            json=_valid_payload,
        )
        assert resp.status_code == 502

    async def test_invalid_json_from_llm_returns_502(self, _valid_payload):
        client = _make_client(FakeLLMClient("not valid json"))
        resp = await client.post(
            "/api/exams/grade5_entrance/assess-with-analysis",
            json=_valid_payload,
        )
        assert resp.status_code == 502

    async def test_nonexistent_exam_returns_404(self):
        client = _make_client(FakeLLMClient("{}"))
        payload = {
            "student_name": "小明",
            "exam_id": "nonexistent",
            "results": [],
        }
        resp = await client.post(
            "/api/exams/nonexistent/assess-with-analysis",
            json=payload,
        )
        assert resp.status_code == 404

    async def test_exam_id_mismatch_returns_422(self):
        client = _make_client(FakeLLMClient("{}"))
        payload = {
            "student_name": "小明",
            "exam_id": "wrong_id",
            "results": [],
        }
        resp = await client.post(
            "/api/exams/grade5_entrance/assess-with-analysis",
            json=payload,
        )
        assert resp.status_code == 422
