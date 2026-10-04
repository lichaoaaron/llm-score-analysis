"""自动组卷服务。

从试题库中按题型、知识点覆盖、难度约束自动抽取题目组成试卷，
采用贪心策略逼近目标难度与知识点覆盖。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from score_analysis.models.question_bank import BankQuestion, QuestionBank


@dataclass
class PaperSpec:
    """组卷规格。"""

    total_score: float = 100.0
    target_difficulty: float = 0.6     # 目标难度 0~1
    # 题型 -> 需要的题数。
    type_counts: Dict[str, int] = field(default_factory=dict)
    # 需要覆盖的知识点集合。
    knowledge_points: List[str] = field(default_factory=list)


@dataclass
class GeneratedPaper:
    """组卷结果。"""

    questions: List[BankQuestion] = field(default_factory=list)
    total_score: float = 0.0
    avg_difficulty: float = 0.0
    covered_points: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "questions": [q.to_dict() for q in self.questions],
            "total_score": self.total_score,
            "avg_difficulty": round(self.avg_difficulty, 4),
            "covered_points": self.covered_points,
        }


class PaperGenerator:
    """自动组卷器（贪心策略）。"""

    def generate(self, bank: QuestionBank, spec: PaperSpec) -> GeneratedPaper:
        selected: List[BankQuestion] = []
        used_ids: set = set()

        # 1. 优先覆盖知识点：每个知识点选一道最接近目标难度的题。
        for point in spec.knowledge_points:
            candidates = [q for q in bank.by_knowledge_point(point) if q.question_id not in used_ids]
            if not candidates:
                continue
            best = min(candidates, key=lambda q: abs(q.difficulty - spec.target_difficulty))
            selected.append(best)
            used_ids.add(best.question_id)

        # 2. 按题型补齐数量。
        for qtype, count in spec.type_counts.items():
            need = count
            already = sum(1 for q in selected if q.question_type == qtype)
            need -= already
            if need <= 0:
                continue
            candidates = [q for q in bank.by_type(qtype) if q.question_id not in used_ids]
            candidates.sort(key=lambda q: abs(q.difficulty - spec.target_difficulty))
            for q in candidates[:need]:
                selected.append(q)
                used_ids.add(q.question_id)

        total_score = sum(q.full_score for q in selected)
        avg_difficulty = (
            sum(q.difficulty for q in selected) / len(selected) if selected else 0.0
        )
        covered = sorted({q.knowledge_point for q in selected})

        return GeneratedPaper(
            questions=selected,
            total_score=total_score,
            avg_difficulty=avg_difficulty,
            covered_points=covered,
        )
