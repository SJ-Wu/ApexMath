import pytest

from app.domain.models import (
    ExamTemplate,
    KnowledgePointCategory,
    MathLiteracyDimension,
    QuestionDefinition,
    SectionDefinition,
)
from app.domain.exam_registry import ExamRegistry


# ===========================================================================
# Phase 5: Registry basics
# ===========================================================================

class TestExamRegistry:
    def _make_template(self, exam_id: str = "test") -> ExamTemplate:
        q = QuestionDefinition(
            question_id="1-1",
            knowledge_point=KnowledgePointCategory.INTEGER,
            difficulty_weight=0.5,
            literacy_weights={MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 1.0},
        )
        s = SectionDefinition(
            section_id="s1", name="Test", knowledge_point=KnowledgePointCategory.INTEGER, questions=[q],
        )
        return ExamTemplate(exam_id=exam_id, name="Test Exam", sections=[s])

    def test_register_and_get(self):
        reg = ExamRegistry()
        tmpl = self._make_template()
        reg.register(tmpl)
        assert reg.get("test") is tmpl

    def test_get_nonexistent_returns_none(self):
        reg = ExamRegistry()
        assert reg.get("nope") is None

    def test_list_ids_empty(self):
        reg = ExamRegistry()
        assert reg.list_ids() == []

    def test_list_ids(self):
        reg = ExamRegistry()
        reg.register(self._make_template("a"))
        reg.register(self._make_template("b"))
        assert sorted(reg.list_ids()) == ["a", "b"]

    def test_duplicate_register_raises(self):
        reg = ExamRegistry()
        reg.register(self._make_template("dup"))
        with pytest.raises(ValueError, match="dup"):
            reg.register(self._make_template("dup"))


# ===========================================================================
# Phase 6: Grade 5 entrance exam data
# ===========================================================================

class TestGrade5EntranceExam:
    @pytest.fixture()
    def template(self):
        from app.data.grade5_entrance import grade5_entrance_template
        return grade5_entrance_template

    def test_exam_id(self, template):
        assert template.exam_id == "grade5_entrance"

    def test_has_10_sections(self, template):
        assert len(template.sections) == 10

    def test_total_44_questions(self, template):
        assert len(template.get_all_questions()) == 44

    def test_section_question_counts(self, template):
        expected_counts = [5, 5, 5, 4, 5, 5, 5, 5, 2, 3]
        actual_counts = [len(s.questions) for s in template.sections]
        assert actual_counts == expected_counts

    def test_every_question_has_at_least_one_literacy_weight(self, template):
        for q in template.get_all_questions():
            assert len(q.literacy_weights) >= 1, f"{q.question_id} has no literacy weights"

    def test_difficulty_weights_non_decreasing_within_section(self, template):
        for section in template.sections:
            weights = [q.difficulty_weight for q in section.questions]
            for i in range(1, len(weights)):
                assert weights[i] >= weights[i - 1], (
                    f"Section {section.section_id}: difficulty not non-decreasing at index {i}"
                )

    def test_unique_question_ids(self, template):
        ids = [q.question_id for q in template.get_all_questions()]
        assert len(ids) == len(set(ids))

    def test_registered_in_default_registry(self):
        from app.data.grade5_entrance import register_grade5_entrance
        reg = ExamRegistry()
        register_grade5_entrance(reg)
        assert reg.get("grade5_entrance") is not None
