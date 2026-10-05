"""试卷质量评估服务。

对整张试卷计算难度、区分度、信度（克朗巴赫 α），并对每道题做逐题分析，
判断题目质量。采用教育测量学中的经典测量理论（CTT）方法。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from score_analysis.config import AppConfig
from score_analysis.models.exam import Question, QuestionStat
from score_analysis.utils.statistics import cronbach_alpha, mean


@dataclass
class PaperQuality:
    """整张试卷的质量指标。"""

    question_count: int
    full_score: float
    avg_score: float
    difficulty: float       # 0~1，越大越简单
    reliability: float      # 信度 α
    avg_discrimination: float

    def to_dict(self) -> dict:
        return {
            "question_count": self.question_count,
            "full_score": self.full_score,
            "avg_score": round(self.avg_score, 2),
            "difficulty": round(self.difficulty, 4),
            "reliability": round(self.reliability, 4),
            "avg_discrimination": round(self.avg_discrimination, 4),
        }


class ItemAnalysisService:
    """试卷质量与逐题分析。"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def paper_quality(
        self,
        total_scores: Sequence[float],
        item_matrix: List[Sequence[float]],
    ) -> PaperQuality:
        """整张试卷质量：难度 = 平均分/满分，信度 = Cronbach's α。"""
        n = len(total_scores)
        if n == 0:
            return PaperQuality(0, self.config.full_score, 0.0, 0.0, 0.0, 0.0)

        avg = mean(total_scores)
        difficulty = avg / self.config.full_score if self.config.full_score else 0.0
        reliability = cronbach_alpha(item_matrix) if item_matrix else 0.0

        discriminations = [self._discrimination(item, total_scores) for item in item_matrix]
        avg_discrimination = mean(discriminations) if discriminations else 0.0

        return PaperQuality(
            question_count=len(item_matrix),
            full_score=self.config.full_score,
            avg_score=avg,
            difficulty=min(1.0, max(0.0, difficulty)),
            reliability=reliability,
            avg_discrimination=avg_discrimination,
        )

    def analyze_questions(
        self,
        questions: List[Question],
        total_scores: Sequence[float],
    ) -> List[QuestionStat]:
        """逐题分析：难度、区分度、质量等级。"""
        result: List[QuestionStat] = []
        for q in questions:
            if not q.item_scores:
                continue
            mean_score = mean(q.item_scores)
            difficulty = mean_score / q.full_score if q.full_score else 0.0
            discrimination = self._discrimination(q.item_scores, total_scores)
            result.append(
                QuestionStat(
                    question_id=q.question_id,
                    content=q.content,
                    full_score=q.full_score,
                    mean_score=mean_score,
                    difficulty=min(1.0, max(0.0, difficulty)),
                    discrimination=discrimination,
                    quality=self._quality(difficulty, discrimination),
                )
            )
        return result

    def _discrimination(self, item_scores: Sequence[float], total_scores: Sequence[float]) -> float:
        """区分度：高低分组法（前 27% 与后 27%）。"""
        n = len(total_scores)
        if n < 4:
            return 0.0
        ratio = self.config.group_ratio
        group_size = max(1, int(round(n * ratio)))

        # 按总分排序，取高分组与低分组。
        order = sorted(range(n), key=lambda i: total_scores[i])
        low_group = order[:group_size]
        high_group = order[-group_size:]

        full = self.config.full_score
        high_mean = mean([item_scores[i] for i in high_group])
        low_mean = mean([item_scores[i] for i in low_group])
        return (high_mean - low_mean) / full if full else 0.0

    @staticmethod
    def _quality(difficulty: float, discrimination: float) -> str:
        """按难度与区分度判定题目质量。"""
        if 0.3 <= difficulty <= 0.8 and discrimination >= 0.3:
            return "good"
        if discrimination >= 0.2:
            return "acceptable"
        return "poor"
