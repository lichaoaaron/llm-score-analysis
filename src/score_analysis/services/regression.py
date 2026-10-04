"""线性回归与成绩预测服务。

用最小二乘法拟合一元线性回归，支持基于期中成绩预测期末成绩。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from score_analysis.utils.statistics import mean, pearson_correlation, stddev


@dataclass
class RegressionResult:
    """一元线性回归结果。"""

    slope: float
    intercept: float
    r: float          # 相关系数
    r_squared: float  # 决定系数

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept

    def to_dict(self) -> dict:
        return {
            "slope": round(self.slope, 4),
            "intercept": round(self.intercept, 4),
            "r": round(self.r, 4),
            "r_squared": round(self.r_squared, 4),
        }


class LinearRegressionService:
    """最小二乘一元线性回归。"""

    def fit(self, xs: Sequence[float], ys: Sequence[float]) -> RegressionResult:
        """拟合 y = slope * x + intercept。"""
        n = len(xs)
        if n < 2 or n != len(ys):
            return RegressionResult(0.0, 0.0, 0.0, 0.0)

        mx = mean(xs)
        my = mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        if sxx == 0:
            return RegressionResult(0.0, my, 0.0, 0.0)

        slope = sxy / sxx
        intercept = my - slope * mx
        r = pearson_correlation(xs, ys)
        return RegressionResult(slope=slope, intercept=intercept, r=r, r_squared=r ** 2)
