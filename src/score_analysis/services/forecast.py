"""成绩预测服务。

基于学生历次考试的成绩序列做一元线性回归，外推预测下一次成绩，
并给出成绩变化趋势（斜率）与拟合优度（R²），用于学业预警。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from score_analysis.utils.statistics import mean


@dataclass
class ForecastResult:
    """单个学生的成绩预测。"""

    student_id: str
    name: str
    history: List[float]
    predicted: float
    slope: float
    r_squared: float

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "history": [round(x, 2) for x in self.history],
            "predicted": round(self.predicted, 2),
            "slope": round(self.slope, 4),
            "r_squared": round(self.r_squared, 4),
        }


class ForecastService:
    """成绩预测服务。"""

    def predict_next(
        self,
        history_by_student: Dict[str, Sequence[float]],
        names: Dict[str, str],
    ) -> List[ForecastResult]:
        """对每名学生做线性回归并预测下一次成绩。

        history_by_student：学生 id -> 历次成绩（按时间升序）。
        """
        results: List[ForecastResult] = []
        for sid, history in history_by_student.items():
            hist = list(history)
            if len(hist) < 2:
                # 样本不足，无法可靠回归，用最近一次成绩兜底。
                pred = hist[-1] if hist else 0.0
                results.append(ForecastResult(sid, names.get(sid, ""), hist, pred, 0.0, 0.0))
                continue
            slope, intercept, r2 = self._linreg(list(range(len(hist))), hist)
            next_x = len(hist)
            pred = slope * next_x + intercept
            results.append(ForecastResult(sid, names.get(sid, ""), hist, pred, slope, r2))
        return results

    @staticmethod
    def _linreg(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float, float]:
        """一元线性回归，返回 (斜率, 截距, R²)。"""
        n = len(xs)
        mx, my = mean(xs), mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        syy = sum((y - my) ** 2 for y in ys)
        if sxx == 0:
            return 0.0, my, 0.0
        slope = sxy / sxx
        intercept = my - slope * mx
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
        r2 = 1.0 - ss_res / syy if syy != 0 else 0.0
        return slope, intercept, r2
