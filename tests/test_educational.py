"""教育测量类服务测试：百分位排名、达成度、进步追踪、公平性、预测。"""
from __future__ import annotations

import unittest

from score_analysis.services.percentile_rank import PercentileRankService
from score_analysis.services.learning_objectives import LearningObjectivesService
from score_analysis.services.progress_tracking import ProgressTrackingService
from score_analysis.services.fairness import FairnessService
from score_analysis.services.forecast import ForecastService


class TestPercentileRank(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PercentileRankService()

    def test_rank_order(self) -> None:
        scores = [90, 80, 70]
        ids = ["a", "b", "c"]
        names = ["甲", "乙", "丙"]
        results = self.service.rank(scores, ids, names)
        self.assertEqual(results[0].student_id, "a")
        self.assertEqual(results[0].rank, 1)
        self.assertGreater(results[0].percentile_rank, results[-1].percentile_rank)

    def test_tie_rank(self) -> None:
        scores = [90, 90, 70]
        ids = ["a", "b", "c"]
        names = ["甲", "乙", "丙"]
        results = self.service.rank(scores, ids, names)
        # 同分并列第 1。
        self.assertEqual(results[0].rank, 1)
        self.assertEqual(results[1].rank, 1)
        self.assertEqual(results[2].rank, 3)


class TestLearningObjectives(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LearningObjectivesService()

    def test_full_achievement(self) -> None:
        obj_names = {"o1": "知识掌握"}
        q_obj = {"q1": "o1", "q2": "o1"}
        q_full = {"q1": 10.0, "q2": 10.0}
        students = [{"q1": 10, "q2": 10}, {"q1": 10, "q2": 10}]
        results = self.service.evaluate(obj_names, q_obj, q_full, students)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].achievement, 1.0, places=4)
        self.assertEqual(results[0].level, "达成良好")

    def test_partial_achievement(self) -> None:
        obj_names = {"o1": "知识掌握"}
        q_obj = {"q1": "o1"}
        q_full = {"q1": 10.0}
        students = [{"q1": 5}]
        results = self.service.evaluate(obj_names, q_obj, q_full, students)
        self.assertAlmostEqual(results[0].achievement, 0.5, places=4)
        self.assertEqual(results[0].level, "未达成")


class TestProgressTracking(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProgressTrackingService()

    def test_progress(self) -> None:
        pre = [60, 80, 90]
        post = [75, 80, 85]
        ids = ["a", "b", "c"]
        names = ["甲", "乙", "丙"]
        results, summary = self.service.compare(pre, post, ids, names)
        self.assertEqual(summary.total, 3)
        self.assertEqual(summary.improved, 1)
        self.assertEqual(summary.declined, 1)
        self.assertEqual(summary.unchanged, 1)
        # 甲进步 +15。
        self.assertEqual(results[0].status, "进步")
        self.assertAlmostEqual(results[0].delta, 15.0)


class TestFairness(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FairnessService()

    def test_analyze(self) -> None:
        qids = ["q1", "q2"]
        qfull = [10.0, 10.0]
        # 4 名学生，q1 高分者得分高、低分者得分低；q2 人人满分。
        matrix = [
            [10, 2, 9, 1],   # q1
            [10, 10, 10, 10],  # q2
        ]
        results = self.service.analyze(qids, qfull, matrix)
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0].gap, 0.5)
        self.assertAlmostEqual(results[1].gap, 0.0)


class TestForecast(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ForecastService()

    def test_linear_trend(self) -> None:
        history = {"a": [60, 65, 70, 75]}
        names = {"a": "甲"}
        results = self.service.predict_next(history, names)
        self.assertEqual(len(results), 1)
        # 稳定上升趋势，斜率约 5。
        self.assertAlmostEqual(results[0].slope, 5.0, places=1)
        self.assertAlmostEqual(results[0].predicted, 80.0, places=1)
        self.assertAlmostEqual(results[0].r_squared, 1.0, places=4)

    def test_insufficient_samples(self) -> None:
        history = {"a": [80]}
        names = {"a": "甲"}
        results = self.service.predict_next(history, names)
        self.assertEqual(results[0].predicted, 80.0)


if __name__ == "__main__":
    unittest.main()
