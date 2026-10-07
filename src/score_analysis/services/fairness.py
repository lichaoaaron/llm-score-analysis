"""试卷公平性分析服务。

通过题目功能差异（DIF）简化分析，比较高低分组（前/后 27%）在每道题上的
得分率差异，识别对某一群体可能存在偏差的题目，辅助试卷质量审查。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class FairnessResult:
    """单道题的公平性分析结果。"""

    question_id: str
    high_group_rate: float
    low_group_rate: float
    gap: float
    flag: str

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "high_group_rate": round(self.high_group_rate, 4),
            "low_group_rate": round(self.low_group_rate, 4),
            "gap": round(self.gap, 4),
            "flag": self.flag,
        }


class FairnessService:
    """试卷公平性（DIF）分析服务。"""

    def analyze(
        self,
        question_ids: Sequence[str],
        question_full_scores: Sequence[float],
        item_scores_matrix: Sequence[Sequence[float]],
        gap_threshold: float = 0.15,
    ) -> List[FairnessResult]:
        """对每道题做高低分组得分率差异分析。

        item_scores_matrix 外层为题、内层为各学生在该题得分；
        高低分组按整卷总分的前/后 27% 划分（教育测量学常用比例）。
        """
        if not item_scores_matrix:
            return []
        n = len(item_scores_matrix[0])
        if n == 0:
            return []
        total_scores = [sum(item_scores_matrix[j][i] for j in range(len(item_scores_matrix))) for i in range(n)]
        order = sorted(range(n), key=lambda i: total_scores[i], reverse=True)
        group_size = max(1, int(n * 0.27))
        high = set(order[:group_size])
        low = set(order[-group_size:])
        results: List[FairnessResult] = []
        for j, qid in enumerate(question_ids):
            full = question_full_scores[j] if j < len(question_full_scores) else 0.0
            if full <= 0:
                continue
            high_rate = self._avg_rate(item_scores_matrix[j], high, full)
            low_rate = self._avg_rate(item_scores_matrix[j], low, full)
            gap = high_rate - low_rate
            # 得分率差异过小且正确率偏低，可能缺乏区分度或存在偏差。
            flag = "正常" if abs(gap) <= gap_threshold else "待核查"
            results.append(FairnessResult(qid, high_rate, low_rate, gap, flag))
        return results

    @staticmethod
    def _avg_rate(scores: Sequence[float], indices: set, full: float) -> float:
        subset = [scores[i] for i in indices]
        if not subset:
            return 0.0
        return sum(subset) / len(subset) / full
