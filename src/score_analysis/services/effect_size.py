"""效应量服务。

显著性检验只能回答"差异是否存在"，效应量则回答"差异有多大"。
本模块实现 Cohen's d（两独立组均值差）、η²（方差分析解释比例），
并给出教育测量领域常用的效应量解释阈值。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from score_analysis.utils.statistics import mean, variance


@dataclass
class EffectSizeResult:
    """效应量计算结果与解释。"""

    value: float
    kind: str
    interpretation: str

    def to_dict(self) -> dict:
        return {
            "value": round(self.value, 4),
            "kind": self.kind,
            "interpretation": self.interpretation,
        }


class EffectSizeService:
    """效应量计算服务。"""

    def cohens_d(self, group_a: Sequence[float], group_b: Sequence[float]) -> EffectSizeResult:
        """Cohen's d：两独立组均值差除以合并标准差。"""
        na, nb = len(group_a), len(group_b)
        if na < 2 or nb < 2:
            raise ValueError("两组样本量均需不小于 2")
        va, vb = variance(group_a), variance(group_b)
        pooled = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
        pooled_sd = pooled ** 0.5
        if pooled_sd == 0:
            return EffectSizeResult(0.0, "cohens_d", "无差异（两组完全一致）")
        d = abs(mean(group_a) - mean(group_b)) / pooled_sd
        return EffectSizeResult(d, "cohens_d", self._interpret_d(d))

    def eta_squared(self, ss_between: float, ss_total: float) -> EffectSizeResult:
        """η² = 组间平方和 / 总平方和，表示自变量解释的方差比例。"""
        if ss_total == 0:
            return EffectSizeResult(0.0, "eta_squared", "无差异")
        eta = ss_between / ss_total
        return EffectSizeResult(eta, "eta_squared", self._interpret_eta(eta))

    @staticmethod
    def _interpret_d(d: float) -> str:
        # Cohen (1988) 建议阈值。
        if d < 0.2:
            return "小（差异微弱）"
        if d < 0.5:
            return "小到中"
        if d < 0.8:
            return "中（差异明显）"
        return "大（差异显著）"

    @staticmethod
    def _interpret_eta(eta: float) -> str:
        if eta < 0.01:
            return "小（解释力微弱）"
        if eta < 0.06:
            return "小到中"
        if eta < 0.14:
            return "中（解释力中等）"
        return "大（解释力强）"
