"""示例数据生成器。

按参数生成具有结构特征的示例成绩数据，用于功能演示与测试。
"""
from __future__ import annotations

import random
from typing import List, Optional

from score_analysis.models.score import StudentScore


class SampleScoreGenerator:
    """示例成绩生成器。"""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def generate(
        self,
        count: int,
        mean: float = 75.0,
        stddev: float = 12.0,
        item_names: Optional[List[str]] = None,
    ) -> List[StudentScore]:
        """生成 count 名学生的成绩，近似正态分布。"""
        item_names = item_names or []
        records: List[StudentScore] = []
        for i in range(count):
            # Box-Muller 法生成正态分布随机数。
            u1 = self._rng.random()
            u2 = self._rng.random()
            import math
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            score = mean + stddev * z
            score = max(0.0, min(100.0, score))

            item_scores = {}
            remaining = score
            for j, name in enumerate(item_names):
                if j == len(item_names) - 1:
                    item_scores[name] = round(remaining, 1)
                else:
                    part = round(remaining * (0.5 + self._rng.random() * 0.3), 1)
                    part = max(0.0, part)
                    item_scores[name] = part
                    remaining = max(0.0, remaining - part)

            records.append(
                StudentScore(
                    student_id=f"2026{i + 1:04d}",
                    name=f"学生{i + 1}",
                    score=round(score, 1),
                    item_scores=item_scores,
                )
            )
        return records
