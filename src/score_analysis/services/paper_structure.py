"""试卷结构分析服务。

分析一张试卷的题型构成、分值分布与知识点覆盖情况，帮助教师检视
试卷命题结构是否合理。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from score_analysis.models.question_bank import BankQuestion


@dataclass
class StructureSummary:
    """试卷结构汇总。"""

    question_count: int
    total_score: float
    type_distribution: Dict[str, Dict[str, float]] = field(default_factory=dict)
    knowledge_distribution: Dict[str, float] = field(default_factory=dict)
    avg_difficulty: float = 0.0

    def to_dict(self) -> dict:
        return {
            "question_count": self.question_count,
            "total_score": self.total_score,
            "type_distribution": self.type_distribution,
            "knowledge_distribution": self.knowledge_distribution,
            "avg_difficulty": round(self.avg_difficulty, 4),
        }


class PaperStructureService:
    """试卷结构分析。"""

    def analyze(self, questions: List[BankQuestion]) -> StructureSummary:
        """按题型与知识点统计题目数量、分值与难度。"""
        type_dist: Dict[str, Dict[str, float]] = {}
        knowledge_dist: Dict[str, float] = {}
        total_score = sum(q.full_score for q in questions)
        difficulty_sum = sum(q.difficulty for q in questions)

        for q in questions:
            # 题型分布：数量 + 分值。
            t = type_dist.setdefault(q.question_type, {"count": 0, "score": 0.0})
            t["count"] += 1
            t["score"] += q.full_score
            # 知识点分值分布。
            knowledge_dist[q.knowledge_point] = knowledge_dist.get(q.knowledge_point, 0.0) + q.full_score

        return StructureSummary(
            question_count=len(questions),
            total_score=total_score,
            type_distribution=type_dist,
            knowledge_distribution=knowledge_dist,
            avg_difficulty=difficulty_sum / len(questions) if questions else 0.0,
        )
