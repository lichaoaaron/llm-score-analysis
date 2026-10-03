"""成绩 CSV 导入服务。"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from score_analysis.models.score import StudentScore


@dataclass
class ImportResult:
    """CSV 导入结果。"""

    records: List[StudentScore] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_rows: int = 0

    def to_dict(self) -> dict:
        return {
            "imported": len(self.records),
            "errors": self.errors,
            "total_rows": self.total_rows,
        }


class ScoreImporter:
    """成绩 CSV 导入器，支持中英文表头。"""

    _COLUMN_MAP: Dict[str, str] = {
        "学号": "student_id",
        "姓名": "name",
        "成绩": "score",
        "student_id": "student_id",
        "name": "name",
        "score": "score",
    }

    def import_csv(self, text: str) -> ImportResult:
        result = ImportResult()
        reader = csv.DictReader(self._lines(text))
        if not reader.fieldnames:
            result.errors.append("CSV 缺少表头")
            return result

        # 确定分项得分列（除学号/姓名/成绩外的列都视为题目得分）。
        mapped_columns = {self._COLUMN_MAP.get(f, "") for f in reader.fieldnames}
        item_columns = [f for f in reader.fieldnames if f not in self._COLUMN_MAP]

        for row_index, raw_row in enumerate(reader, start=2):
            result.total_rows += 1
            student_id = raw_row.get("学号") or raw_row.get("student_id") or ""
            name = raw_row.get("姓名") or raw_row.get("name") or ""
            score_raw = raw_row.get("成绩") or raw_row.get("score") or ""

            if not student_id or not score_raw:
                result.errors.append(f"第 {row_index} 行缺少学号或成绩")
                continue
            try:
                score = float(score_raw)
            except ValueError:
                result.errors.append(f"第 {row_index} 行成绩非法：{score_raw}")
                continue

            item_scores: Dict[str, float] = {}
            for col in item_columns:
                val = (raw_row.get(col) or "").strip()
                if val:
                    try:
                        item_scores[col] = float(val)
                    except ValueError:
                        result.errors.append(f"第 {row_index} 行题目得分非法：{col}={val}")

            result.records.append(
                StudentScore(student_id=student_id, name=name, score=score, item_scores=item_scores)
            )
        return result

    @staticmethod
    def _lines(text: str) -> List[str]:
        return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
