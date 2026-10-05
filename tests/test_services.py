"""清洗、导入、正态性、聚合、趋势服务单元测试。"""
from __future__ import annotations

import unittest

from score_analysis.config import AppConfig
from score_analysis.services.group_analysis import GroupAnalysisService
from score_analysis.services.importer import ScoreImporter
from score_analysis.services.normality import NormalityService
from score_analysis.services.score_cleaner import ScoreCleaner
from score_analysis.services.statistics_service import StatisticsService
from score_analysis.services.trend_analysis import TrendAnalysisService


class TestScoreCleaner(unittest.TestCase):
    def test_remove_invalid(self) -> None:
        cleaner = ScoreCleaner(AppConfig())
        result = cleaner.clean([88, None, -5, 200, 75, 92])
        self.assertEqual(result.scores, [88, 75, 92])
        self.assertEqual(result.report.removed_invalid, 3)

    def test_outlier_detection(self) -> None:
        cleaner = ScoreCleaner(AppConfig())
        # 95 是明显离群值，会被 IQR 法剔除。
        result = cleaner.clean([60, 62, 61, 63, 62, 61, 95])
        self.assertNotIn(95, result.scores)


class TestImporter(unittest.TestCase):
    def test_import_csv(self) -> None:
        text = "学号,姓名,成绩,选择题,填空题\n2026001,张伟,88,18,16\n2026002,李娜,92,20,18\n"
        result = ScoreImporter().import_csv(text)
        self.assertEqual(len(result.records), 2)
        self.assertEqual(result.records[0].item_scores["选择题"], 18.0)

    def test_invalid_score(self) -> None:
        text = "学号,姓名,成绩\n2026001,张伟,abc\n"
        result = ScoreImporter().import_csv(text)
        self.assertEqual(len(result.records), 0)
        self.assertTrue(any("成绩非法" in e for e in result.errors))


class TestNormality(unittest.TestCase):
    def test_normal_data(self) -> None:
        # 近似正态的数据。
        values = [55, 60, 65, 70, 75, 80, 85, 90, 95, 72, 78, 82]
        result = NormalityService().test(values)
        self.assertIsInstance(result.is_normal, bool)
        self.assertGreater(result.jarque_bera, 0)

    def test_skewed_data(self) -> None:
        # 明显右偏的数据。
        values = [95, 96, 97, 98, 99, 100, 100, 100, 55, 60]
        result = NormalityService().test(values)
        self.assertLess(result.skewness, 0)


class TestGroupAnalysis(unittest.TestCase):
    def test_summarize_sorted(self) -> None:
        service = GroupAnalysisService(AppConfig())
        groups = {"一班": [80, 85, 90], "二班": [60, 65, 70]}
        results = service.summarize(groups)
        self.assertEqual(results[0].group, "一班")
        self.assertAlmostEqual(results[0].mean, 85.0)

    def test_weakest(self) -> None:
        service = GroupAnalysisService(AppConfig())
        groups = {"一班": [80, 85, 90], "二班": [60, 65, 70], "三班": [50, 55, 60]}
        weakest = service.weakest(groups, top_n=1)
        self.assertEqual(weakest[0].group, "三班")


class TestTrendAnalysis(unittest.TestCase):
    def test_rising_trend(self) -> None:
        service = TrendAnalysisService(AppConfig())
        report = service.analyze([("期中", [60, 65, 70]), ("期末", [80, 85, 90])])
        self.assertEqual(report.direction, "rising")
        self.assertGreater(report.mean_change, 0)

    def test_stable_trend(self) -> None:
        service = TrendAnalysisService(AppConfig())
        report = service.analyze([("期中", [70, 72, 71]), ("期末", [71, 73, 72])])
        self.assertEqual(report.direction, "stable")


class TestStatisticsService(unittest.TestCase):
    def test_distribute(self) -> None:
        service = StatisticsService(AppConfig())
        dist = service.distribute([88, 92, 75, 95, 60])
        self.assertEqual(dist.stats.count, 5)
        self.assertEqual(len(dist.grade_levels), 5)
        self.assertAlmostEqual(dist.pass_rate, 1.0)

    def test_grade_levels(self) -> None:
        service = StatisticsService(AppConfig())
        levels = service.grade_levels([55, 65, 75, 85, 95])
        by_name = {g.name: g.count for g in levels}
        self.assertEqual(by_name["优秀"], 1)
        self.assertEqual(by_name["不及格"], 1)


if __name__ == "__main__":
    unittest.main()
