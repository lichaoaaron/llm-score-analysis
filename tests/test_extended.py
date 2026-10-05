"""等级/绩点、加权成绩、组卷、直方图、示例数据单元测试。"""
from __future__ import annotations

import unittest

from score_analysis.models.question_bank import BankQuestion, QuestionBank
from score_analysis.sample_data import SampleScoreGenerator
from score_analysis.services.grade_scale import GradeScaleService
from score_analysis.services.histogram import HistogramService
from score_analysis.services.paper_generator import PaperGenerator, PaperSpec
from score_analysis.services.weighted_score import WeightedScoreService


class TestGradeScale(unittest.TestCase):
    def test_grade(self) -> None:
        service = GradeScaleService()
        self.assertEqual(service.grade(95), "优秀")
        self.assertEqual(service.grade(75), "中等")
        self.assertEqual(service.grade(55), "不及格")

    def test_gpa(self) -> None:
        service = GradeScaleService()
        self.assertEqual(service.gpa(95), 4.0)
        self.assertEqual(service.gpa(85), 3.0)

    def test_weighted_gpa(self) -> None:
        service = GradeScaleService()
        gpa = service.weighted_gpa([90, 80], [3.0, 2.0])
        # (4.0*3 + 3.0*2) / 5 = 3.6
        self.assertAlmostEqual(gpa, 3.6)


class TestWeightedScore(unittest.TestCase):
    def test_compute(self) -> None:
        service = WeightedScoreService()
        service.add_component("平时", 0.3)
        service.add_component("期中", 0.3)
        service.add_component("期末", 0.4)
        result = service.compute("S1", {"平时": 90, "期中": 80, "期末": 85})
        self.assertAlmostEqual(result.total_score, 85.0)

    def test_invalid_weight(self) -> None:
        service = WeightedScoreService()
        service.add_component("平时", 0.5)
        service.add_component("期末", 0.4)
        with self.assertRaises(ValueError):
            service.compute("S1", {"平时": 90, "期末": 85})


class TestPaperGenerator(unittest.TestCase):
    def _bank(self) -> QuestionBank:
        bank = QuestionBank(bank_id="B1", subject="数据结构")
        for i in range(20):
            bank.add(
                BankQuestion(
                    question_id=f"Q{i}",
                    content=f"题目 {i}",
                    question_type="选择题" if i % 2 == 0 else "简答题",
                    difficulty=0.3 + (i % 7) * 0.1,
                    knowledge_point=f"知识点{i % 5}",
                    full_score=5.0,
                )
            )
        return bank

    def test_generate_covers_points(self) -> None:
        generator = PaperGenerator()
        spec = PaperSpec(
            target_difficulty=0.6,
            type_counts={"选择题": 5, "简答题": 3},
            knowledge_points=["知识点0", "知识点1"],
        )
        paper = generator.generate(self._bank(), spec)
        self.assertIn("知识点0", paper.covered_points)
        self.assertIn("知识点1", paper.covered_points)

    def test_type_counts(self) -> None:
        generator = PaperGenerator()
        spec = PaperSpec(type_counts={"选择题": 4, "简答题": 2}, knowledge_points=[])
        paper = generator.generate(self._bank(), spec)
        choice_count = sum(1 for q in paper.questions if q.question_type == "选择题")
        self.assertEqual(choice_count, 4)


class TestHistogram(unittest.TestCase):
    def test_bin_counts(self) -> None:
        service = HistogramService()
        bins = service.build([55, 65, 75, 85, 95], bin_width=10)
        self.assertEqual(len(bins), 10)
        self.assertEqual(sum(b.count for b in bins), 5)


class TestSampleData(unittest.TestCase):
    def test_generate_count(self) -> None:
        records = SampleScoreGenerator(seed=42).generate(30, item_names=["选择题", "简答题"])
        self.assertEqual(len(records), 30)
        self.assertIn("选择题", records[0].item_scores)

    def test_deterministic(self) -> None:
        a = SampleScoreGenerator(seed=1).generate(10)
        b = SampleScoreGenerator(seed=1).generate(10)
        self.assertEqual([r.score for r in a], [r.score for r in b])


if __name__ == "__main__":
    unittest.main()
