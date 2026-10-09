"""去重服务与命令行成绩列表解析单元测试。"""
from __future__ import annotations

import unittest

from score_analysis.cli import _parse_score_list
from score_analysis.models.score import StudentScore
from score_analysis.services.dedup import DedupService


class TestDedup(unittest.TestCase):
    def test_keep_max(self) -> None:
        scores = [
            StudentScore("S1", "甲", 80),
            StudentScore("S1", "甲", 90),
            StudentScore("S2", "乙", 70),
        ]
        result = DedupService().dedup(scores, strategy="max")
        self.assertEqual(len(result.records), 2)
        s1 = [r for r in result.records if r.student_id == "S1"][0]
        self.assertEqual(s1.score, 90)

    def test_avg_strategy(self) -> None:
        scores = [StudentScore("S1", "甲", 80), StudentScore("S1", "甲", 90)]
        result = DedupService().dedup(scores, strategy="avg")
        self.assertAlmostEqual(result.records[0].score, 85.0)


class TestScoreListParsing(unittest.TestCase):
    """命令行成绩列表解析与输入校验。"""

    def test_plain_number_list(self) -> None:
        self.assertEqual(_parse_score_list([85, 90.5, 77]), [85.0, 90.5, 77.0])

    def test_dict_score_list(self) -> None:
        self.assertEqual(_parse_score_list([{"score": 85}, {"score": 60}]), [85.0, 60.0])

    def test_wrapped_scores_object(self) -> None:
        self.assertEqual(_parse_score_list({"scores": [88, 92]}), [88.0, 92.0])

    def test_empty_data_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _parse_score_list([])

    def test_non_numeric_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _parse_score_list([85, {"name": "甲"}])

    def test_non_list_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _parse_score_list(85)


if __name__ == "__main__":
    unittest.main()
