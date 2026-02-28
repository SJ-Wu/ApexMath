import pytest
from httpx import AsyncClient, ASGITransport

from tests.conftest import create_test_app


@pytest.fixture()
def client():
    app = create_test_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestListExams:
    async def test_list_exams(self, client):
        resp = await client.get("/api/exams")
        assert resp.status_code == 200
        data = resp.json()
        assert "grade5_entrance" in data["exam_ids"]

    async def test_list_exams_returns_list(self, client):
        resp = await client.get("/api/exams")
        assert isinstance(resp.json()["exam_ids"], list)


class TestGetExam:
    async def test_get_existing_exam(self, client):
        resp = await client.get("/api/exams/grade5_entrance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["exam_id"] == "grade5_entrance"
        assert len(data["sections"]) == 10

    async def test_get_nonexistent_exam_404(self, client):
        resp = await client.get("/api/exams/nonexistent")
        assert resp.status_code == 404


class TestAssess:
    async def test_assess_success(self, client):
        payload = {
            "student_name": "小明",
            "exam_id": "grade5_entrance",
            "results": [{"question_id": "1-1", "score": 1.0}],
        }
        resp = await client.post("/api/exams/grade5_entrance/assess", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_name"] == "小明"
        assert len(data["knowledge_point_scores"]) == 10
        assert len(data["math_literacy_scores"]) == 4

    async def test_assess_empty_results_all_zeros(self, client):
        payload = {
            "student_name": "小明",
            "exam_id": "grade5_entrance",
            "results": [],
        }
        resp = await client.post("/api/exams/grade5_entrance/assess", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        for kp in data["knowledge_point_scores"]:
            assert kp["score"] == 0.0
        for ml in data["math_literacy_scores"]:
            assert ml["score"] == 0.0

    async def test_assess_nonexistent_exam_404(self, client):
        payload = {
            "student_name": "小明",
            "exam_id": "nonexistent",
            "results": [],
        }
        resp = await client.post("/api/exams/nonexistent/assess", json=payload)
        assert resp.status_code == 404

    async def test_assess_invalid_question_id_422(self, client):
        payload = {
            "student_name": "小明",
            "exam_id": "grade5_entrance",
            "results": [{"question_id": "INVALID", "score": 1.0}],
        }
        resp = await client.post("/api/exams/grade5_entrance/assess", json=payload)
        assert resp.status_code == 422

    async def test_assess_invalid_score_422(self, client):
        payload = {
            "student_name": "小明",
            "exam_id": "grade5_entrance",
            "results": [{"question_id": "1-1", "score": 2.0}],
        }
        resp = await client.post("/api/exams/grade5_entrance/assess", json=payload)
        assert resp.status_code == 422

    async def test_assess_exam_id_mismatch_422(self, client):
        payload = {
            "student_name": "小明",
            "exam_id": "wrong_id",
            "results": [],
        }
        resp = await client.post("/api/exams/grade5_entrance/assess", json=payload)
        assert resp.status_code == 422
