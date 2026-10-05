"""标准分换算服务。

实现 Z 分数、T 分数、标准九分（Stanine）等教育测量中常用的标准分
转换，用于不同难度考试间的成绩比较。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from score_analysis.utils.statistics import mean, stddev


@dataclass
class StandardScore:
    """标准分换算结果。"""

    raw: float
    z: float
    t: float
    stanine: int

    def to_dict(self) -> dict:
        return {"raw": self.raw, "z": round(self.z, 4), "t": round(self.t, 2), "stanine": self.stanine}


class StandardScoreService:
    """标准分换算。"""

    def __init__(self) -> None:
        self._mean = 0.0
        self._stddev = 0.0

    def fit(self, scores: Sequence[float]) -> None:
        """以一组成绩为基准估计均值与标准差。"""
        self._mean = mean(scores)
        self._stddev = stddev(scores)

    def convert(self, raw: float) -> StandardScore:
        """把原始分换算为标准分。"""
        if self._stddev == 0:
            z = 0.0
        else:
            z = (raw - self._mean) / self._stddev
        t = 50 + 10 * z
        stanine = self._to_stanine(z)
        return StandardScore(raw=raw, z=z, t=t, stanine=stanine)

    @staticmethod
    def _to_stanine(z: float) -> int:
        """Z 分数转标准九分（1~9）。"""
        if z >= 1.75:
            return 9
        if z >= 1.25:
            return 8
        if z >= 0.75:
            return 7
        if z >= 0.25:
            return 6
        if z >= -0.25:
            return 5
        if z >= -0.75:
            return 4
        if z >= -1.25:
            return 3
        if z >= -1.75:
            return 2
        return 1
