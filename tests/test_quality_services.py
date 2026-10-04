"""一致性校验、试卷结构、导出服务单元测试。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from score_analysis.models.question_bank import BankQuestion
from score_analysis.models.score import StudentScore
from score_analysis.services.consistency import ConsistencyService
from score_analysis.services.exporter import Exporter
from score_analysis.services.paper_structure import PaperStructureService


class TestConsistency(unittest.TestCase):
    def test_consistent(self) -> None:
        scores = [
            StudentScore("S1", "甲", 30, {"a": 10, "b": 20}),
            StudentScore("S2", "乙", 25, {"a": 10, "b": 15}),
        ]
        result = ConsistencyService().check(scores)
        self.assertEqual(result.inconsistent, 0)

    def test_inconsistent(self) -> None:
        scores = [StudentScore("S1", "甲", 30, {"a": 10, "b": 10})]  # 分项之和 20 ≠ 30
        result = ConsistencyService().check(scores)
        self.assertEqual(result.inconsistent, 1)
        self.assertEqual(result.issues[0].difference, -10.0)


class TestPaperStructure(unittest.TestCase):
    def test_analyze(self) -> None:
        questions = [
            BankQuestion("Q1", "题1", "选择题", 0.5, "知识点A", 10),
            BankQuestion("Q2", "题2", "简答题", 0.6, "知识点B", 20),
        ]
        summary = PaperStructureService().analyze(questions)
        self.assertEqual(summary.question_count, 2)
        self.assertEqual(summary.total_score, 30)
        self.assertEqual(summary.type_distribution["选择题"]["count"], 1)


class TestExporter(unittest.TestCase):
    def test_export_json(self) -> None:
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            Exporter().export({"a": 1}, out, fmt="json")
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["a"], 1)

    def test_export_markdown(self) -> None:
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.md"
            Exporter().export([{"name": "张伟", "score": 88}], out, fmt="markdown")
            content = out.read_text(encoding="utf-8")
            self.assertIn("张伟", content)


if __name__ == "__main__":
    unittest.main()
