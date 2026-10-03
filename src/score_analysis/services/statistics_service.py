"""描述统计与成绩分布服务。

对一组成绩计算均值、中位数、标准差、四分位数、偏度、峰度等描述统计量，
并按阈值划分等级、计算及格率与成绩频数分布。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from score_analysis.config import AppConfig
from score_analysis.models.score import GradeLevel
from score_analysis.utils.statistics import (
    frequency_distribution,
    kurtosis,
    mean,
    median,
    percentile,
    quartiles,
    skewness,
    stddev,
)


@dataclass
class DescriptiveStats:
    """一组成绩的描述统计量。"""

    count: int
    mean: float
    median: float
    stddev: float
    minimum: float
    maximum: float
    q1: float
    q3: float
    skewness: float
    kurtosis: float

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "mean": round(self.mean, 2),
            "median": round(self.median, 2),
            "stddev": round(self.stddev, 2),
            "minimum": round(self.minimum, 2),
            "maximum": round(self.maximum, 2),
            "q1": round(self.q1, 2),
            "q3": round(self.q3, 2),
            "skewness": round(self.skewness, 4),
            "kurtosis": round(self.kurtosis, 4),
        }


@dataclass
class ScoreDistribution:
    """成绩分布结果。"""

    stats: DescriptiveStats
    grade_levels: List[GradeLevel]
    pass_rate: float
    frequency: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "stats": self.stats.to_dict(),
            "grade_levels": [g.to_dict() for g in self.grade_levels],
            "pass_rate": round(self.pass_rate, 4),
            "frequency": self.frequency,
        }


class StatisticsService:
    """描述统计与分布分析。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def describe(self, scores: Sequence[float]) -> DescriptiveStats:
        """计算一组成绩的描述统计量。"""
        if not scores:
            return DescriptiveStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        q1, _, q3 = quartiles(scores)
        return DescriptiveStats(
            count=len(scores),
            mean=mean(scores),
            median=median(scores),
            stddev=stddev(scores),
            minimum=min(scores),
            maximum=max(scores),
            q1=q1,
            q3=q3,
            skewness=skewness(scores),
            kurtosis=kurtosis(scores),
        )

    def grade_levels(self, scores: Sequence[float]) -> List[GradeLevel]:
        """按阈值划分等级并统计人数与占比。"""
        cfg = self.config
        levels = [
            GradeLevel("优秀", cfg.excellent_line, cfg.full_score),
            GradeLevel("良好", cfg.good_line, cfg.excellent_line - 0.01),
            GradeLevel("中等", cfg.medium_line, cfg.good_line - 0.01),
            GradeLevel("及格", cfg.pass_line, cfg.medium_line - 0.01),
            GradeLevel("不及格", 0.0, cfg.pass_line - 0.01),
        ]
        total = len(scores)
        for level in levels:
            level.count = sum(1 for s in scores if level.min_score <= s <= level.max_score)
            level.ratio = level.count / total if total else 0.0
        return levels

    def pass_rate(self, scores: Sequence[float]) -> float:
        """及格率。"""
        if not scores:
            return 0.0
        passed = sum(1 for s in scores if s >= self.config.pass_line)
        return passed / len(scores)

    def distribute(self, scores: Sequence[float]) -> ScoreDistribution:
        """完整分布分析：描述统计 + 等级 + 及格率 + 频数。"""
        # 频数按 10 分一段归并（0-9、10-19……90-100）。
        freq: Dict[str, int] = {}
        for s in scores:
            bucket = min(int(s // 10) * 10, 90)
            key = f"{bucket}-{bucket + 9}"
            freq[key] = freq.get(key, 0) + 1
        return ScoreDistribution(
            stats=self.describe(scores),
            grade_levels=self.grade_levels(scores),
            pass_rate=self.pass_rate(scores),
            frequency=dict(sorted(freq.items(), key=lambda kv: int(kv[0].split("-")[0]))),
        )
