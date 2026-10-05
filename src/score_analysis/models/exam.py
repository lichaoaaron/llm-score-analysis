"""试卷与题目数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Question:
    """一道试题及其在各考生上的得分。"""

    question_id: str
    content: str
    full_score: float
    # 各考生在该题得分，顺序与考生列表一致。
    item_scores: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "content": self.content,
            "full_score": self.full_score,
        }


@dataclass
class QuestionStat:
    """一道题的统计分析结果。"""

    question_id: str
    content: str
    full_score: float
    mean_score: float
    difficulty: float       # 0~1，越大越简单（平均得分/满分）
    discrimination: float   # 区分度，-1~1
    quality: str            # 质量等级：good / acceptable / poor

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "content": self.content,
            "full_score": self.full_score,
            "mean_score": round(self.mean_score, 2),
            "difficulty": round(self.difficulty, 4),
            "discrimination": round(self.discrimination, 4),
            "quality": self.quality,
        }


@dataclass
class ExamPaper:
    """一份试卷。"""

    paper_id: str
    course: str
    questions: List[Question] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "course": self.course,
            "questions": [q.to_dict() for q in self.questions],
        }
