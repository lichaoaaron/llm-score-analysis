"""成绩排名与成绩单服务。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from score_analysis.services.grade_scale import GradeScaleService


@dataclass
class RankResult:
    """一名学生的排名。"""

    student_id: str
    name: str
    score: float
    rank: int           # 名次（并列同名次）
    grade: str
    gpa: float

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "score": self.score,
            "rank": self.rank,
            "grade": self.grade,
            "gpa": self.gpa,
        }


class RankingService:
    """成绩排名与成绩单生成。"""

    def __init__(self, grade_service: GradeScaleService | None = None) -> None:
        self.grade_service = grade_service or GradeScaleService()

    def rank(self, rows: List[tuple[str, str, float]]) -> List[RankResult]:
        """按成绩降序排名（并列同名次）。rows 为 (student_id, name, score)。"""
        ordered = sorted(rows, key=lambda r: r[2], reverse=True)
        results: List[RankResult] = []
        current_rank = 1
        for i, (sid, name, score) in enumerate(ordered):
            if i > 0 and score < ordered[i - 1][2]:
                current_rank = i + 1
            results.append(
                RankResult(
                    student_id=sid,
                    name=name,
                    score=score,
                    rank=current_rank,
                    grade=self.grade_service.grade(score),
                    gpa=self.grade_service.gpa(score),
                )
            )
        return results

    def transcript(self, rows: List[tuple[str, str, float]]) -> List[RankResult]:
        """成绩单（排名 + 等级 + 绩点）。"""
        return self.rank(rows)
