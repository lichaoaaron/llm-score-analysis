"""配置加载器单元测试。"""
from __future__ import annotations

import unittest
from pathlib import Path

from score_analysis.config_loader import ConfigLoader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TestConfigLoader(unittest.TestCase):
    def test_load_grade_scale(self) -> None:
        scale = ConfigLoader().load_grade_scale(DATA_DIR / "grade_scale.json")
        self.assertEqual(len(scale.bands), 5)
        self.assertEqual(scale.grade_of(95), "优秀")

    def test_load_question_bank(self) -> None:
        bank = ConfigLoader().load_question_bank(DATA_DIR / "question_bank.json")
        self.assertEqual(bank.subject, "数据结构")
        self.assertEqual(bank.count(), 6)
        self.assertTrue(bank.by_knowledge_point("栈与队列"))


if __name__ == "__main__":
    unittest.main()
