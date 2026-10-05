"""标准分、回归、相关、排名服务单元测试。"""
from __future__ import annotations

import unittest

from score_analysis.services.correlation import CorrelationService
from score_analysis.services.ranking_service import RankingService
from score_analysis.services.regression import LinearRegressionService
from score_analysis.services.standard_score import StandardScoreService


class TestStandardScore(unittest.TestCase):
    def test_convert(self) -> None:
        service = StandardScoreService()
        service.fit([60, 70, 80, 90, 100])
        result = service.convert(80)
        self.assertAlmostEqual(result.z, 0.0, places=4)
        self.assertAlmostEqual(result.t, 50.0, places=2)

    def test_stanine_range(self) -> None:
        service = StandardScoreService()
        service.fit(list(range(50, 101)))
        for raw in [50, 60, 70, 80, 90, 100]:
            result = service.convert(raw)
            self.assertGreaterEqual(result.stanine, 1)
            self.assertLessEqual(result.stanine, 9)


class TestRegression(unittest.TestCase):
    def test_perfect_linear(self) -> None:
        result = LinearRegressionService().fit([1, 2, 3, 4], [2, 4, 6, 8])
        self.assertAlmostEqual(result.slope, 2.0)
        self.assertAlmostEqual(result.intercept, 0.0)
        self.assertAlmostEqual(result.r_squared, 1.0)

    def test_predict(self) -> None:
        result = LinearRegressionService().fit([1, 2, 3], [1, 2, 3])
        self.assertAlmostEqual(result.predict(5), 5.0)


class TestCorrelation(unittest.TestCase):
    def test_identity(self) -> None:
        result = CorrelationService().compute({"a": [1, 2, 3], "b": [2, 4, 6]})
        self.assertAlmostEqual(result.get(0, 0), 1.0)
        self.assertAlmostEqual(result.get(0, 1), 1.0)


class TestRanking(unittest.TestCase):
    def test_rank_desc(self) -> None:
        rows = [("S1", "甲", 80), ("S2", "乙", 90), ("S3", "丙", 85)]
        results = RankingService().rank(rows)
        self.assertEqual(results[0].student_id, "S2")
        self.assertEqual(results[0].rank, 1)

    def test_tie_rank(self) -> None:
        rows = [("S1", "甲", 90), ("S2", "乙", 90), ("S3", "丙", 80)]
        results = RankingService().rank(rows)
        self.assertEqual(results[0].rank, 1)
        self.assertEqual(results[1].rank, 1)
        self.assertEqual(results[2].rank, 3)


if __name__ == "__main__":
    unittest.main()
