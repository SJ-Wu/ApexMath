import pytest
from pydantic import ValidationError

from app.domain.models import (
    KnowledgePointCategory,
    MathLiteracyDimension,
    QuestionDefinition,
    SectionDefinition,
    ExamTemplate,
    QuestionResult,
    ExamSubmission,
    KnowledgePointScore,
    MathLiteracyScore,
    AssessmentResult,
)


class TestKnowledgePointCategory:
    def test_has_10_members(self):
        assert len(KnowledgePointCategory) == 10

    def test_contains_expected_members(self):
        expected = [
            "INTEGER", "DECIMAL", "FRACTION", "VOLUME",
            "DISTANCE", "TIME", "PROBLEM_SOLVING", "PATTERN",
            "AREA_CUBE", "GIFTED",
        ]
        for name in expected:
            assert name in KnowledgePointCategory.__members__


class TestMathLiteracyDimension:
    def test_has_4_members(self):
        assert len(MathLiteracyDimension) == 4

    def test_contains_expected_members(self):
        expected = [
            "CONCEPTUAL_UNDERSTANDING",
            "COMPUTATIONAL_FLUENCY",
            "CONTEXTUAL_STRATEGY",
            "LOGICAL_REASONING",
        ]
        for name in expected:
            assert name in MathLiteracyDimension.__members__


class TestQuestionDefinition:
    def test_create_valid(self):
        q = QuestionDefinition(
            question_id="1-1",
            knowledge_point=KnowledgePointCategory.INTEGER,
            difficulty_weight=0.2,
            literacy_weights={MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 1.0},
        )
        assert q.question_id == "1-1"
        assert q.difficulty_weight == 0.2

    def test_difficulty_weight_must_be_positive(self):
        with pytest.raises(ValidationError):
            QuestionDefinition(
                question_id="1-1",
                knowledge_point=KnowledgePointCategory.INTEGER,
                difficulty_weight=0.0,
                literacy_weights={MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 1.0},
            )

    def test_literacy_weights_must_not_be_empty(self):
        with pytest.raises(ValidationError):
            QuestionDefinition(
                question_id="1-1",
                knowledge_point=KnowledgePointCategory.INTEGER,
                difficulty_weight=0.5,
                literacy_weights={},
            )


class TestSectionDefinition:
    def test_create_section(self):
        q = QuestionDefinition(
            question_id="1-1",
            knowledge_point=KnowledgePointCategory.INTEGER,
            difficulty_weight=0.5,
            literacy_weights={MathLiteracyDimension.COMPUTATIONAL_FLUENCY: 1.0},
        )
        section = SectionDefinition(
            section_id="sec-1",
            name="正整數運算思維",
            knowledge_point=KnowledgePointCategory.INTEGER,
            questions=[q],
        )
        assert section.section_id == "sec-1"
        assert len(section.questions) == 1


class TestExamTemplate:
    def _make_template(self):
        q1 = QuestionDefinition(
            question_id="1-1",
            knowledge_point=KnowledgePointCategory.INTEGER,
            difficulty_weight=0.2,
            literacy_weights={MathLiteracyDimension.CONCEPTUAL_UNDERSTANDING: 1.0},
        )
        q2 = QuestionDefinition(
            question_id="2-1",
            knowledge_point=KnowledgePointCategory.DECIMAL,
            difficulty_weight=0.4,
            literacy_weights={MathLiteracyDimension.COMPUTATIONAL_FLUENCY: 1.0},
        )
        s1 = SectionDefinition(
            section_id="sec-1", name="正整數", knowledge_point=KnowledgePointCategory.INTEGER, questions=[q1],
        )
        s2 = SectionDefinition(
            section_id="sec-2", name="小數", knowledge_point=KnowledgePointCategory.DECIMAL, questions=[q2],
        )
        return ExamTemplate(exam_id="test-exam", name="測試", sections=[s1, s2])

    def test_get_all_questions_flattens(self):
        template = self._make_template()
        questions = template.get_all_questions()
        assert len(questions) == 2
        ids = {q.question_id for q in questions}
        assert ids == {"1-1", "2-1"}

    def test_get_all_questions_returns_list(self):
        template = self._make_template()
        assert isinstance(template.get_all_questions(), list)


class TestQuestionResult:
    def test_valid_score(self):
        r = QuestionResult(question_id="1-1", score=0.5)
        assert r.score == 0.5

    def test_score_min_zero(self):
        r = QuestionResult(question_id="1-1", score=0.0)
        assert r.score == 0.0

    def test_score_max_one(self):
        r = QuestionResult(question_id="1-1", score=1.0)
        assert r.score == 1.0

    def test_score_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            QuestionResult(question_id="1-1", score=-0.1)

    def test_score_above_one_rejected(self):
        with pytest.raises(ValidationError):
            QuestionResult(question_id="1-1", score=1.1)


class TestExamSubmission:
    def test_create_submission(self):
        sub = ExamSubmission(
            student_name="小明",
            exam_id="grade5_entrance",
            results=[QuestionResult(question_id="1-1", score=1.0)],
        )
        assert sub.student_name == "小明"
        assert len(sub.results) == 1


class TestScoreModels:
    def test_knowledge_point_score(self):
        s = KnowledgePointScore(
            category=KnowledgePointCategory.INTEGER, score=4.5,
        )
        assert s.score == 4.5

    def test_math_literacy_score(self):
        s = MathLiteracyScore(
            dimension=MathLiteracyDimension.LOGICAL_REASONING, score=3.0,
        )
        assert s.score == 3.0

    def test_assessment_result(self):
        kp = [KnowledgePointScore(category=KnowledgePointCategory.INTEGER, score=5.0)]
        ml = [MathLiteracyScore(dimension=MathLiteracyDimension.LOGICAL_REASONING, score=3.0)]
        result = AssessmentResult(
            student_name="小明",
            exam_id="test",
            knowledge_point_scores=kp,
            math_literacy_scores=ml,
        )
        assert result.student_name == "小明"
        assert len(result.knowledge_point_scores) == 1
        assert len(result.math_literacy_scores) == 1
