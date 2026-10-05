"""班级 / 课程成绩聚合分析服务。

对多个班级或课程的成绩做分组统计与横向对比，识别薄弱班级。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from score_analysis.config import AppConfig
from score_analysis.utils.statistics import mean, stddev


@dataclass
class GroupSummary:
    """一个班级/课程的成绩汇总。"""

    group: str
    count: int
    mean: float
    stddev: float
    pass_rate: float
    minimum: float
    maximum: float

    def to_dict(self) -> dict:
        return {
            "group": self.group,
            "count": self.count,
            "mean": round(self.mean, 2),
            "stddev": round(self.stddev, 2),
            "pass_rate": round(self.pass_rate, 4),
            "minimum": round(self.minimum, 2),
            "maximum": round(self.maximum, 2),
        }


class GroupAnalysisService:
    """班级/课程聚合与对比。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def summarize(self, groups: Dict[str, Sequence[float]]) -> List[GroupSummary]:
        """按分组统计成绩，返回按平均分降序排列的汇总列表。"""
        results: List[GroupSummary] = []
        for group, scores in groups.items():
            if not scores:
                results.append(GroupSummary(group, 0, 0.0, 0.0, 0.0, 0.0, 0.0))
                continue
            passed = sum(1 for s in scores if s >= self.config.pass_line)
            results.append(
                GroupSummary(
                    group=group,
                    count=len(scores),
                    mean=mean(scores),
                    stddev=stddev(scores),
                    pass_rate=passed / len(scores),
                    minimum=min(scores),
                    maximum=max(scores),
                )
            )
        results.sort(key=lambda r: r.mean, reverse=True)
        return results

    def compare(self, groups: Dict[str, Sequence[float]]) -> Dict[str, GroupSummary]:
        """返回 {分组: 汇总} 的字典，便于索引。"""
        return {s.group: s for s in self.summarize(groups)}

    def weakest(self, groups: Dict[str, Sequence[float]], top_n: int = 3) -> List[GroupSummary]:
        """返回平均分最低的 top_n 个分组（薄弱班级）。"""
        return self.summarize(groups)[-top_n:][::-1]
