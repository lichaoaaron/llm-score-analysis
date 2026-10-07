"""假设检验服务。

提供教育测量中常用的三组显著性检验：
- 独立样本 t 检验（Welch 校正）：比较两个班级/组别的平均成绩差异；
- 单因素方差分析（one-way ANOVA）：比较多组平均成绩差异；
- 卡方独立性检验：检验等级分布与班级/性别等分类变量是否独立。

p 值基于手写的 Student-t / F / 卡方分布累积分布函数计算。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence

from score_analysis.utils.distributions import chi2_p_value, f_p_value, t_p_value
from score_analysis.utils.statistics import mean, variance


@dataclass
class TTestResult:
    """独立样本 t 检验结果。"""

    t_stat: float
    p_value: float
    df: float
    mean_a: float
    mean_b: float
    mean_diff: float
    alpha: float
    significant: bool

    def to_dict(self) -> dict:
        return {
            "t_stat": round(self.t_stat, 4),
            "p_value": round(self.p_value, 4),
            "df": round(self.df, 2),
            "mean_a": round(self.mean_a, 2),
            "mean_b": round(self.mean_b, 2),
            "mean_diff": round(self.mean_diff, 2),
            "alpha": self.alpha,
            "significant": self.significant,
        }


@dataclass
class AnovaResult:
    """单因素方差分析结果。"""

    f_stat: float
    p_value: float
    df_between: int
    df_within: int
    ss_between: float
    ss_within: float
    group_means: List[float]
    alpha: float
    significant: bool

    def to_dict(self) -> dict:
        return {
            "f_stat": round(self.f_stat, 4),
            "p_value": round(self.p_value, 4),
            "df_between": self.df_between,
            "df_within": self.df_within,
            "ss_between": round(self.ss_between, 2),
            "ss_within": round(self.ss_within, 2),
            "group_means": [round(m, 2) for m in self.group_means],
            "alpha": self.alpha,
            "significant": self.significant,
        }


@dataclass
class ChiSquareResult:
    """卡方独立性检验结果。"""

    chi2: float
    p_value: float
    df: int
    alpha: float
    significant: bool

    def to_dict(self) -> dict:
        return {
            "chi2": round(self.chi2, 4),
            "p_value": round(self.p_value, 4),
            "df": self.df,
            "alpha": self.alpha,
            "significant": self.significant,
        }


class HypothesisTestingService:
    """显著性检验服务。"""

    def independent_t_test(
        self, group_a: Sequence[float], group_b: Sequence[float], alpha: float = 0.05
    ) -> TTestResult:
        """Welch 独立样本 t 检验（不假设方差齐性）。"""
        if len(group_a) < 2 or len(group_b) < 2:
            raise ValueError("两组样本量均需不小于 2")
        ma, mb = mean(group_a), mean(group_b)
        va, vb = variance(group_a), variance(group_b)
        na, nb = len(group_a), len(group_b)
        se = math_sqrt(va / na + vb / nb)
        if se == 0:
            # 方差与均值均相同，无法区分。
            return TTestResult(0.0, 1.0, float(na + nb - 2), ma, mb, 0.0, alpha, False)
        t_stat = (ma - mb) / se
        # Welch-Satterthwaite 自由度。
        num = (va / na + vb / nb) ** 2
        den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
        df = num / den
        p = t_p_value(t_stat, df, two_sided=True)
        return TTestResult(t_stat, p, df, ma, mb, ma - mb, alpha, p < alpha)

    def one_way_anova(
        self, groups: Sequence[Sequence[float]], alpha: float = 0.05
    ) -> AnovaResult:
        """单因素方差分析（one-way ANOVA）。"""
        groups = [list(g) for g in groups if len(g) > 0]
        if len(groups) < 2:
            raise ValueError("至少需要两组数据")
        group_means = [mean(g) for g in groups]
        grand_mean = mean([x for g in groups for x in g])
        n_total = sum(len(g) for g in groups)
        # 组间平方和。
        ss_between = sum(len(g) * (m - grand_mean) ** 2 for g, m in zip(groups, group_means))
        # 组内平方和。
        ss_within = sum((x - m) ** 2 for g, m in zip(groups, group_means) for x in g)
        df_between = len(groups) - 1
        df_within = n_total - len(groups)
        if df_within <= 0 or ss_within == 0:
            return AnovaResult(0.0, 1.0, df_between, df_within, ss_between, ss_within, group_means, alpha, False)
        ms_between = ss_between / df_between
        ms_within = ss_within / df_within
        f_stat = ms_between / ms_within
        p = f_p_value(f_stat, df_between, df_within)
        return AnovaResult(f_stat, p, df_between, df_within, ss_between, ss_within, group_means, alpha, p < alpha)

    def chi_square_independence(
        self, observed: Sequence[Sequence[float]], alpha: float = 0.05
    ) -> ChiSquareResult:
        """卡方独立性检验。

        参数 observed 为列联表（二维数组），行、列分别代表两个分类变量。
        """
        rows = len(observed)
        if rows == 0:
            raise ValueError("列联表不能为空")
        cols = len(observed[0])
        if cols == 0:
            raise ValueError("列联表不能为空")
        row_totals = [sum(r) for r in observed]
        col_totals = [sum(observed[i][j] for i in range(rows)) for j in range(cols)]
        total = sum(row_totals)
        if total == 0:
            return ChiSquareResult(0.0, 1.0, (rows - 1) * (cols - 1), alpha, False)
        chi2 = 0.0
        for i in range(rows):
            for j in range(cols):
                expected = row_totals[i] * col_totals[j] / total
                if expected > 0:
                    chi2 += (observed[i][j] - expected) ** 2 / expected
        df = (rows - 1) * (cols - 1)
        p = chi2_p_value(chi2, df)
        return ChiSquareResult(chi2, p, df, alpha, p < alpha)


def math_sqrt(x: float) -> float:
    """平方根，避免在模块顶部重复导入 math。"""
    import math

    return math.sqrt(x)
