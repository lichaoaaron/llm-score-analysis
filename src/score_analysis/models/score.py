"""成绩数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StudentScore:
    """一名学生的单科成绩记录。"""

    student_id: str
    name: str
    score: float
    # 可选：分项得分，用于试卷信度与逐题分析。
    item_scores: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.score < 0:
            raise ValueError("score 不能为负")


@dataclass
class ScoreEntry:
    """清洗后的成绩条目，带班级/课程上下文。"""

    course: str
    class_name: str
    student_id: str
    name: str
    score: float

    def to_dict(self) -> dict:
        return {
            "course": self.course,
            "class_name": self.class_name,
            "student_id": self.student_id,
            "name": self.name,
            "score": self.score,
        }


@dataclass
class GradeLevel:
    """一个等级区间。"""

    name: str
    min_score: float
    max_score: float
    count: int = 0
    ratio: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "count": self.count,
            "ratio": round(self.ratio, 4),
        }
