"""去重服务与 CLI 综合报表单元测试。"""
from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
