"""百分位排名服务。

将原始分数转换为百分位等级（Percentile Rank），反映某学生在全体中的相对位置。
PR = (低于该分数的人数 + 0.5 × 同分人数) / 总人数 × 100。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class PercentileRankResult:
    """单个学生的百分位排名。"""

    student_id: str
    name: str
    score: float
    rank: int
    percentile_rank: float

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "score": round(self.score, 2),
            "rank": self.rank,
            "percentile_rank": round(self.percentile_rank, 2),
        }


class PercentileRankService:
    """百分位排名计算服务。"""

    def rank(
        self, scores: Sequence[float], ids: Sequence[str], names: Sequence[str]
    ) -> List[PercentileRankResult]:
        """按分数计算百分位等级，分数越高排名越靠前（rank=1 为最高分）。

        scores / ids / names 需一一对应、长度相同。
        """
        if not (len(scores) == len(ids) == len(names)):
            raise ValueError("scores/ids/names 长度必须一致")
        n = len(scores)
        if n == 0:
            return []
        # 按分数降序排序，同分并列取相同名次（竞赛排名法）。
        order = sorted(range(n), key=lambda i: scores[i], reverse=True)
        ranks = [0] * n
        current_rank = 1
        i = 0
        while i < n:
            j = i
            while j < n and scores[order[j]] == scores[order[i]]:
                j += 1
            for k in range(i, j):
                ranks[order[k]] = current_rank
            current_rank += j - i
            i = j
        results: List[PercentileRankResult] = []
        for idx in range(n):
            lower = sum(1 for s in scores if s < scores[idx])
            equal = sum(1 for s in scores if s == scores[idx])
            pr = (lower + 0.5 * equal) / n * 100
            results.append(
                PercentileRankResult(ids[idx], names[idx], scores[idx], ranks[idx], pr)
            )
        results.sort(key=lambda r: r.rank)
        return results
