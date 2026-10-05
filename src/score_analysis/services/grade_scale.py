"""成绩等级与绩点转换服务。

实现百分制成绩与五级制（优秀/良好/中等/及格/不及格）、四级制 GPA（4.0 制）
之间的转换，支持自定义等级阈值。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class GradeBand:
    """一个绩点区间。"""

    name: str          # 等级名称
    min_score: float   # 最低分（含）
    max_score: float   # 最高分（含）
    gpa: float         # 对应绩点

    def contains(self, score: float) -> bool:
        return self.min_score <= score <= self.max_score


@dataclass
class GradeScale:
    """一套成绩等级标准。"""

    bands: List[GradeBand] = field(default_factory=list)

    def grade_of(self, score: float) -> str:
        """返回成绩对应的等级名称。"""
        for band in self.bands:
            if band.contains(score):
                return band.name
        return "未评级"

    def gpa_of(self, score: float) -> float:
        """返回成绩对应的绩点。"""
        for band in self.bands:
            if band.contains(score):
                return band.gpa
        return 0.0

    def to_dict(self) -> dict:
        return [
            {"name": b.name, "min_score": b.min_score, "max_score": b.max_score, "gpa": b.gpa}
            for b in self.bands
        ]


# 常见的百分制到五级制 + GPA(4.0) 映射。
DEFAULT_SCALE = GradeScale(
    [
        GradeBand("优秀", 90, 100, 4.0),
        GradeBand("良好", 80, 89.99, 3.0),
        GradeBand("中等", 70, 79.99, 2.0),
        GradeBand("及格", 60, 69.99, 1.0),
        GradeBand("不及格", 0, 59.99, 0.0),
    ]
)


class GradeScaleService:
    """等级与绩点换算。"""

    def __init__(self, scale: GradeScale | None = None) -> None:
        self.scale = scale or DEFAULT_SCALE

    def grade(self, score: float) -> str:
        return self.scale.grade_of(score)

    def gpa(self, score: float) -> float:
        return self.scale.gpa_of(score)

    def weighted_gpa(self, scores: List[float], credits: List[float]) -> float:
        """按学分加权的平均绩点。"""
        if len(scores) != len(credits) or not scores:
            return 0.0
        total_credit = sum(credits)
        if total_credit == 0:
            return 0.0
        total = sum(self.gpa(s) * c for s, c in zip(scores, credits))
        return total / total_credit
