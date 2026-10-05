"""成绩清洗服务。

处理缺失值、非法值（负分、超满分），并用四分位距（IQR）法识别离群值，
输出清洗后的成绩与清洗报告。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from score_analysis.config import AppConfig
from score_analysis.utils.statistics import percentile


@dataclass
class CleaningReport:
    """清洗报告。"""

    total: int
    removed_invalid: int
    removed_outlier: int
    kept: int
    outlier_threshold_low: float
    outlier_threshold_high: float
    messages: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "removed_invalid": self.removed_invalid,
            "removed_outlier": self.removed_outlier,
            "kept": self.kept,
            "outlier_threshold_low": round(self.outlier_threshold_low, 2),
            "outlier_threshold_high": round(self.outlier_threshold_high, 2),
            "messages": self.messages,
        }


@dataclass
class CleaningResult:
    """清洗结果。"""

    scores: List[float]
    report: CleaningReport

    def to_dict(self) -> dict:
        return {"scores": self.scores, "report": self.report.to_dict()}


class ScoreCleaner:
    """成绩清洗器。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def clean(self, raw_scores: Sequence[Optional[float]]) -> CleaningResult:
        """清洗一组成绩，返回清洗后的成绩与报告。"""
        cfg = self.config
        total = len(raw_scores)
        messages: List[str] = []

        # 1. 过滤非法值（None、负分、超满分）。
        valid: List[float] = []
        removed_invalid = 0
        for s in raw_scores:
            if s is None or s < 0 or s > cfg.full_score:
                removed_invalid += 1
            else:
                valid.append(s)
        if removed_invalid:
            messages.append(f"剔除非法值 {removed_invalid} 条（缺失、负分或超满分）")

        # 2. IQR 离群值检测（仅当有足够数据时）。
        low, high = 0.0, cfg.full_score
        removed_outlier = 0
        if len(valid) >= 4:
            q1 = percentile(valid, 25)
            q3 = percentile(valid, 75)
            iqr = q3 - q1
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            kept: List[float] = []
            for s in valid:
                if s < low or s > high:
                    removed_outlier += 1
                else:
                    kept.append(s)
            valid = kept
            if removed_outlier:
                messages.append(f"按 IQR 法剔除离群值 {removed_outlier} 条")

        return CleaningResult(
            scores=valid,
            report=CleaningReport(
                total=total,
                removed_invalid=removed_invalid,
                removed_outlier=removed_outlier,
                kept=len(valid),
                outlier_threshold_low=low,
                outlier_threshold_high=high,
                messages=messages,
            ),
        )
