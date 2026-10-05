"""成绩正态性检验服务。

用 Jarque-Bera 检验判断成绩是否近似服从正态分布，供试卷质量评估与
教学分析参考。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from score_analysis.utils.statistics import kurtosis, skewness


@dataclass
class NormalityResult:
    """正态性检验结果。"""

    skewness: float
    kurtosis: float
    jarque_bera: float
    is_normal: bool

    def to_dict(self) -> dict:
        return {
            "skewness": round(self.skewness, 4),
            "kurtosis": round(self.kurtosis, 4),
            "jarque_bera": round(self.jarque_bera, 4),
            "is_normal": self.is_normal,
        }


class NormalityService:
    """Jarque-Bera 正态性检验。"""

    # χ²(2) 分布在显著性水平 0.05 下的临界值。
    _CRITICAL_VALUE = 5.991

    def test(self, values: Sequence[float]) -> NormalityResult:
        """检验一组成绩是否近似正态分布。"""
        n = len(values)
        if n < 8:
            # 样本过小，不进行检验，默认视为正态。
            return NormalityResult(0.0, 0.0, 0.0, True)

        s = skewness(values)
        k = kurtosis(values)  # 超额峰度
        jb = (n / 6.0) * (s ** 2 + (k ** 2) / 4.0)

        return NormalityResult(
            skewness=s,
            kurtosis=k,
            jarque_bera=jb,
            is_normal=jb <= self._CRITICAL_VALUE,
        )
