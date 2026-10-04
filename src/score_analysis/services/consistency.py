"""成绩一致性校验服务。

校验分项得分之和是否与总分一致，识别录入错误或缺失的分项，
保证数据质量后再进入分析环节。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from score_analysis.models.score import StudentScore


@dataclass
class ConsistencyIssue:
    """一条一致性问题。"""

    student_id: str
    name: str
    total: float
    item_sum: float
    difference: float
    detail: str

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "total": self.total,
            "item_sum": round(self.item_sum, 2),
            "difference": round(self.difference, 2),
            "detail": self.detail,
        }


@dataclass
class ConsistencyResult:
    """一致性校验结果。"""

    checked: int
    consistent: int
    inconsistent: int
    issues: List[ConsistencyIssue] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "checked": self.checked,
            "consistent": self.consistent,
            "inconsistent": self.inconsistent,
            "issues": [i.to_dict() for i in self.issues],
        }


class ConsistencyService:
    """成绩分项一致性校验。"""

    def __init__(self, tolerance: float = 1.0) -> None:
        self.tolerance = tolerance

    def check(self, scores: List[StudentScore]) -> ConsistencyResult:
        """校验每条记录的分项之和是否与总分一致。"""
        checked = len(scores)
        issues: List[ConsistencyIssue] = []
        for s in scores:
            if not s.item_scores:
                continue
            item_sum = sum(s.item_scores.values())
            diff = item_sum - s.score
            if abs(diff) > self.tolerance:
                issues.append(
                    ConsistencyIssue(
                        student_id=s.student_id,
                        name=s.name,
                        total=s.score,
                        item_sum=item_sum,
                        difference=diff,
                        detail="分项得分之和与总分不一致",
                    )
                )
        return ConsistencyResult(
            checked=checked,
            consistent=checked - len(issues),
            inconsistent=len(issues),
            issues=issues,
        )
