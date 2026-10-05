"""统计工具模块。

实现描述统计、分位数、偏度、峰度、频数分布、信度系数等基础统计函数，
全部基于 Python 标准库手写，不依赖 numpy/pandas 等第三方包。
"""
from __future__ import annotations

import math
from collections import Counter
from typing import List, Sequence


def mean(values: Sequence[float]) -> float:
    """算术平均值。"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """中位数。"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 1:
        return sorted_values[n // 2]
    return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0


def variance(values: Sequence[float], sample: bool = True) -> float:
    """方差。sample=True 时为样本方差（除以 n-1），否则为总体方差（除以 n）。"""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    ss = sum((x - m) ** 2 for x in values)
    divisor = (len(values) - 1) if sample else len(values)
    return ss / divisor


def stddev(values: Sequence[float], sample: bool = True) -> float:
    """标准差。"""
    return math.sqrt(variance(values, sample))


def percentile(values: Sequence[float], p: float) -> float:
    """百分位数（线性插值法，p 取值 0~100）。"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    rank = (p / 100.0) * (n - 1)
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    if lower == upper:
        return sorted_values[lower]
    frac = rank - lower
    return sorted_values[lower] * (1 - frac) + sorted_values[upper] * frac


def quartiles(values: Sequence[float]) -> tuple[float, float, float]:
    """返回 (Q1, Q2, Q3)。"""
    return percentile(values, 25), percentile(values, 50), percentile(values, 75)


def skewness(values: Sequence[float]) -> float:
    """样本偏度（Fisher-Pearson 修正系数），衡量分布不对称程度。"""
    n = len(values)
    if n < 3:
        return 0.0
    m = mean(values)
    s = stddev(values)
    if s == 0:
        return 0.0
    m3 = sum(((x - m) / s) ** 3 for x in values)
    return (n / ((n - 1) * (n - 2))) * m3


def kurtosis(values: Sequence[float]) -> float:
    """样本超额峰度，衡量分布尖峭程度（正态分布约为 0）。"""
    n = len(values)
    if n < 4:
        return 0.0
    m = mean(values)
    s = stddev(values)
    if s == 0:
        return 0.0
    m4 = sum(((x - m) / s) ** 4 for x in values)
    term1 = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3)) * m4
    term2 = (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return term1 - term2


def frequency_distribution(values: Sequence[object]) -> dict:
    """频数分布，返回 {取值: 频数}。"""
    return dict(Counter(values))


def cronbach_alpha(item_scores: Sequence[Sequence[float]]) -> float:
    """克朗巴赫 α 信度系数。

    参数 item_scores 为逐题得分矩阵：外层是题目，内层是各考生在该题的得分。
    α = (k/(k-1)) * (1 - Σσ²_题 / σ²_总分)，k 为题数。
    """
    k = len(item_scores)
    if k < 2:
        return 0.0
    n = len(item_scores[0]) if item_scores else 0
    if n < 2:
        return 0.0
    # 每个考生的总分。
    total_scores = [sum(item_scores[j][i] for j in range(k)) for i in range(n)]
    var_total = variance(total_scores)
    if var_total == 0:
        return 0.0
    var_sum = sum(variance(item_scores[j]) for j in range(k))
    return (k / (k - 1)) * (1 - var_sum / var_total)


def pearson_correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    """皮尔逊相关系数。"""
    n = len(xs)
    if n < 2 or n != len(ys):
        return 0.0
    mx, my = mean(xs), mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)
