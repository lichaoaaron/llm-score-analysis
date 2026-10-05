"""重复成绩记录处理服务。

对同一学生出现多条成绩记录的情况进行去重与合并，支持保留最高分、
取平均或取最新等策略。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from score_analysis.models.score import StudentScore


@dataclass
class DedupResult:
    """去重结果。"""

    records: List[StudentScore]
    original_count: int
    removed_duplicates: int

    def to_dict(self) -> dict:
        return {
            "records": [
                {"student_id": s.student_id, "name": s.name, "score": s.score}
                for s in self.records
            ],
            "original_count": self.original_count,
            "removed_duplicates": self.removed_duplicates,
        }


class DedupService:
    """成绩记录去重。"""

    STRATEGY_MAX = "max"
    STRATEGY_AVG = "avg"

    def dedup(self, scores: Sequence[StudentScore], strategy: str = STRATEGY_MAX) -> DedupResult:
        """按学号去重，同一学生保留一条记录。"""
        grouped: Dict[str, List[StudentScore]] = {}
        for s in scores:
            grouped.setdefault(s.student_id, []).append(s)

        records: List[StudentScore] = []
        for student_id, items in grouped.items():
            if len(items) == 1:
                records.append(items[0])
            else:
                if strategy == self.STRATEGY_AVG:
                    avg = sum(i.score for i in items) / len(items)
                    items[0].score = avg
                else:
                    best = max(items, key=lambda i: i.score)
                    items[0].score = best.score
                records.append(items[0])

        return DedupResult(
            records=sorted(records, key=lambda r: r.student_id),
            original_count=len(scores),
            removed_duplicates=len(scores) - len(records),
        )
