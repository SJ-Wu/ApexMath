import pytest

from app.domain.models import (
    KnowledgePointCategory,
    MathLiteracyDimension,
    QuestionDefinition,
    SectionDefinition,
    ExamTemplate,
    QuestionResult,
    ExamSubmission,
)
from app.domain.scoring import (
    calculate_knowledge_point_scores,
    calculate_math_literacy_scores,
    generate_assessment,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_question(qid: str, kp: KnowledgePointCategory, dw: float,
                   lw: dict[MathLiteracyDimension, float] | None = None) -> QuestionDefinition:
    if lw is None:
        lw = {MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 1.0}
    return QuestionDefinition(
        question_id=qid,
        knowledge_point=kp,
        difficulty_weight=dw,
        literacy_weights=lw,
    )


def _make_template(sections_data: list[tuple[str, str, KnowledgePointCategory, list[QuestionDefinition]]]) -> ExamTemplate:
    sections = [
        SectionDefinition(section_id=sid, name=name, knowledge_point=kp, questions=qs)
        for sid, name, kp, qs in sections_data
    ]
    return ExamTemplate(exam_id="test", name="測試", sections=sections)


def _simple_template() -> ExamTemplate:
    """Template with 2 INTEGER questions (easy=0.2, hard=1.0)."""
    q1 = _make_question("1-1", KnowledgePointCategory.INTEGER, 0.2)
    q2 = _make_question("1-2", KnowledgePointCategory.INTEGER, 1.0)
    return _make_template([("s1", "正整數", KnowledgePointCategory.INTEGER, [q1, q2])])


# ===========================================================================
# Phase 2: Knowledge Point Scoring
# ===========================================================================

class TestKnowledgePointScoring:
    def test_all_correct_gives_5(self):
        template = _simple_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=1.0),
                     QuestionResult(question_id="1-2", score=1.0)],
        )
        scores = calculate_knowledge_point_scores(template, submission)
        integer_score = next(s for s in scores if s.category == KnowledgePointCategory.INTEGER)
        assert integer_score.score == pytest.approx(5.0)

    def test_all_wrong_gives_0(self):
        template = _simple_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=0.0),
                     QuestionResult(question_id="1-2", score=0.0)],
        )
        scores = calculate_knowledge_point_scores(template, submission)
        integer_score = next(s for s in scores if s.category == KnowledgePointCategory.INTEGER)
        assert integer_score.score == pytest.approx(0.0)

    def test_hard_question_correct_scores_higher(self):
        template = _simple_template()
        # Only hard correct
        sub_hard = ExamSubmission(
            student_name="A", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=0.0),
                     QuestionResult(question_id="1-2", score=1.0)],
        )
        # Only easy correct
        sub_easy = ExamSubmission(
            student_name="B", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=1.0),
                     QuestionResult(question_id="1-2", score=0.0)],
        )
        scores_hard = calculate_knowledge_point_scores(template, sub_hard)
        scores_easy = calculate_knowledge_point_scores(template, sub_easy)
        hard_val = next(s for s in scores_hard if s.category == KnowledgePointCategory.INTEGER).score
        easy_val = next(s for s in scores_easy if s.category == KnowledgePointCategory.INTEGER).score
        assert hard_val > easy_val

    def test_partial_score(self):
        template = _simple_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=0.5),
                     QuestionResult(question_id="1-2", score=0.5)],
        )
        scores = calculate_knowledge_point_scores(template, submission)
        integer_score = next(s for s in scores if s.category == KnowledgePointCategory.INTEGER)
        assert integer_score.score == pytest.approx(2.5)

    def test_unanswered_questions_count_as_zero(self):
        template = _simple_template()
        # Only answer one question
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=1.0)],
        )
        scores = calculate_knowledge_point_scores(template, submission)
        integer_score = next(s for s in scores if s.category == KnowledgePointCategory.INTEGER)
        # score = (1.0*0.2 + 0*1.0) / (0.2+1.0) * 5 = 0.2/1.2 * 5 ≈ 0.833
        expected = (1.0 * 0.2) / (0.2 + 1.0) * 5
        assert integer_score.score == pytest.approx(expected, rel=1e-3)

    def test_output_contains_all_10_categories(self):
        template = _simple_template()
        submission = ExamSubmission(student_name="小明", exam_id="test", results=[])
        scores = calculate_knowledge_point_scores(template, submission)
        categories = {s.category for s in scores}
        assert categories == set(KnowledgePointCategory)

    def test_category_with_no_questions_gives_zero(self):
        template = _simple_template()
        submission = ExamSubmission(student_name="小明", exam_id="test", results=[])
        scores = calculate_knowledge_point_scores(template, submission)
        decimal_score = next(s for s in scores if s.category == KnowledgePointCategory.DECIMAL)
        assert decimal_score.score == pytest.approx(0.0)

    def test_invalid_question_id_raises(self):
        template = _simple_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="INVALID", score=1.0)],
        )
        with pytest.raises(ValueError, match="INVALID"):
            calculate_knowledge_point_scores(template, submission)


# ===========================================================================
# Phase 3: Math Literacy Scoring
# ===========================================================================

class TestMathLiteracyScoring:
    def _literacy_template(self) -> ExamTemplate:
        q1 = _make_question("1-1", KnowledgePointCategory.INTEGER, 0.5, {
            MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 0.8,
            MathLiteracyDimension.COMPUTATIONAL_FLUENCY: 0.5,
        })
        q2 = _make_question("1-2", KnowledgePointCategory.INTEGER, 0.5, {
            MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 0.3,
            MathLiteracyDimension.LOGICAL_REASONING: 1.0,
        })
        return _make_template([("s1", "正整數", KnowledgePointCategory.INTEGER, [q1, q2])])

    def test_all_correct_gives_5_per_dimension(self):
        template = self._literacy_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=1.0),
                     QuestionResult(question_id="1-2", score=1.0)],
        )
        scores = calculate_math_literacy_scores(template, submission)
        for s in scores:
            if s.dimension in (
                MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING,
                MathLiteracyDimension.COMPUTATIONAL_FLUENCY,
                MathLiteracyDimension.LOGICAL_REASONING,
            ):
                assert s.score == pytest.approx(5.0)

    def test_all_wrong_gives_zero(self):
        template = self._literacy_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=0.0),
                     QuestionResult(question_id="1-2", score=0.0)],
        )
        scores = calculate_math_literacy_scores(template, submission)
        for s in scores:
            assert s.score == pytest.approx(0.0)

    def test_output_contains_all_4_dimensions(self):
        template = self._literacy_template()
        submission = ExamSubmission(student_name="小明", exam_id="test", results=[])
        scores = calculate_math_literacy_scores(template, submission)
        dims = {s.dimension for s in scores}
        assert dims == set(MathLiteracyDimension)

    def test_dimension_with_no_weight_gives_zero(self):
        template = self._literacy_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=1.0),
                     QuestionResult(question_id="1-2", score=1.0)],
        )
        scores = calculate_math_literacy_scores(template, submission)
        ctx = next(s for s in scores if s.dimension == MathLiteracyDimension.CONTEXTUAL_STRATEGY)
        assert ctx.score == pytest.approx(0.0)

    def test_half_correct_gives_approximately_half(self):
        template = self._literacy_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=0.5),
                     QuestionResult(question_id="1-2", score=0.5)],
        )
        scores = calculate_math_literacy_scores(template, submission)
        for s in scores:
            if s.score > 0:
                assert s.score == pytest.approx(2.5)


# ===========================================================================
# Phase 4: Full Assessment
# ===========================================================================

class TestGenerateAssessment:
    def test_returns_complete_structure(self):
        template = _simple_template()
        submission = ExamSubmission(
            student_name="小明", exam_id="test",
            results=[QuestionResult(question_id="1-1", score=1.0),
                     QuestionResult(question_id="1-2", score=1.0)],
        )
        result = generate_assessment(template, submission)
        assert result.student_name == "小明"
        assert result.exam_id == "test"
        assert len(result.knowledge_point_scores) == 10
        assert len(result.math_literacy_scores) == 4

    def test_empty_submission_gives_all_zeros(self):
        template = _simple_template()
        submission = ExamSubmission(student_name="小明", exam_id="test", results=[])
        result = generate_assessment(template, submission)
        for kp in result.knowledge_point_scores:
            assert kp.score == pytest.approx(0.0)
        for ml in result.math_literacy_scores:
            assert ml.score == pytest.approx(0.0)
