"""成绩直方图分箱服务。

把成绩按区间分箱，输出用于绘制直方图的频数与频率数据。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class HistogramBin:
    """一个直方图区间。"""

    lower: float
    upper: float
    count: int
    ratio: float

    def to_dict(self) -> dict:
        return {
            "range": f"{self.lower:.0f}-{self.upper:.0f}",
            "count": self.count,
            "ratio": round(self.ratio, 4),
        }


class HistogramService:
    """成绩直方图分箱。"""

    def build(self, scores: Sequence[float], bin_width: float = 10.0, full_score: float = 100.0) -> List[HistogramBin]:
        """按固定宽度分箱，返回各区间频数。"""
        n = len(scores)
        bins: List[HistogramBin] = []
        lower = 0.0
        while lower < full_score:
            upper = min(lower + bin_width - 0.01, full_score)
            count = sum(1 for s in scores if lower <= s <= upper)
            bins.append(
                HistogramBin(lower=lower, upper=upper, count=count, ratio=count / n if n else 0.0)
            )
            lower += bin_width
        return bins

    def build_adaptive(self, scores: Sequence[float], bin_count: int = 10, full_score: float = 100.0) -> List[HistogramBin]:
        """按指定区间数自适应分箱。"""
        width = full_score / bin_count
        return self.build(scores, bin_width=width, full_score=full_score)
