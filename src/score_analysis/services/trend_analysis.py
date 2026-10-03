"""多次考试趋势分析服务。

对同一批学生在多次考试（如期中、期末）中的成绩做纵向对比，识别
进步或退步趋势。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from score_analysis.config import AppConfig
from score_analysis.utils.statistics import mean


@dataclass
class TrendPoint:
    """一次考试的成绩指标点。"""

    exam_name: str
    count: int
    mean: float
    pass_rate: float

    def to_dict(self) -> dict:
        return {
            "exam_name": self.exam_name,
            "count": self.count,
            "mean": round(self.mean, 2),
            "pass_rate": round(self.pass_rate, 4),
        }


@dataclass
class TrendReport:
    """趋势分析报告。"""

    points: List[TrendPoint] = field(default_factory=list)
    direction: str = "stable"     # rising / falling / stable
    mean_change: float = 0.0      # 首末次考试的均值变化

    def to_dict(self) -> dict:
        return {
            "points": [p.to_dict() for p in self.points],
            "direction": self.direction,
            "mean_change": round(self.mean_change, 2),
        }


class TrendAnalysisService:
    """考试趋势分析。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def analyze(self, exams: Sequence[tuple[str, Sequence[float]]]) -> TrendReport:
        """按考试顺序（如 [("期中", scores), ("期末", scores)]）分析趋势。"""
        points: List[TrendPoint] = []
        for name, scores in exams:
            if not scores:
                points.append(TrendPoint(name, 0, 0.0, 0.0))
                continue
            passed = sum(1 for s in scores if s >= self.config.pass_line)
            points.append(
                TrendPoint(
                    exam_name=name,
                    count=len(scores),
                    mean=mean(scores),
                    pass_rate=passed / len(scores),
                )
            )

        report = TrendReport(points=points)
        if len(points) >= 2:
            first = points[0].mean
            last = points[-1].mean
            report.mean_change = last - first
            if report.mean_change > 2:
                report.direction = "rising"
            elif report.mean_change < -2:
                report.direction = "falling"
            else:
                report.direction = "stable"
        return report
