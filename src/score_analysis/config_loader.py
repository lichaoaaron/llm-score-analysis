"""业务配置加载服务。

从 JSON 文件加载成绩等级标准、组卷规格等业务配置。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from score_analysis.models.question_bank import BankQuestion, QuestionBank
from score_analysis.services.grade_scale import GradeBand, GradeScale


class ConfigLoader:
    """业务配置加载器。"""

    @staticmethod
    def _read_json(path: Path) -> object:
        return json.loads(path.read_text(encoding="utf-8"))

    def load_grade_scale(self, path: Path) -> GradeScale:
        """从 JSON 加载成绩等级标准。"""
        raw = self._read_json(path)
        bands: List[GradeBand] = []
        for item in raw:  # type: ignore[union-attr]
            bands.append(
                GradeBand(
                    name=item["name"],
                    min_score=float(item["min_score"]),
                    max_score=float(item["max_score"]),
                    gpa=float(item["gpa"]),
                )
            )
        return GradeScale(bands)

    def load_question_bank(self, path: Path) -> QuestionBank:
        """从 JSON 加载试题库。"""
        raw = self._read_json(path)
        bank = QuestionBank(bank_id=raw["bank_id"], subject=raw["subject"])  # type: ignore[index]
        for item in raw["questions"]:  # type: ignore[index]
            bank.add(
                BankQuestion(
                    question_id=item["question_id"],
                    content=item["content"],
                    question_type=item["question_type"],
                    difficulty=float(item["difficulty"]),
                    knowledge_point=item["knowledge_point"],
                    full_score=float(item["full_score"]),
                    tags=list(item.get("tags") or []),
                )
            )
        return bank
