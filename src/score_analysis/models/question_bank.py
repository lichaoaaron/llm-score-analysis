"""试题库数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BankQuestion:
    """题库中的一道题。"""

    question_id: str
    content: str
    question_type: str       # 选择题 / 填空题 / 简答题 / 计算题 / 综合题
    difficulty: float        # 0~1，越大越难
    knowledge_point: str     # 所属知识点
    full_score: float
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "content": self.content,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "knowledge_point": self.knowledge_point,
            "full_score": self.full_score,
            "tags": self.tags,
        }


@dataclass
class QuestionBank:
    """试题库。"""

    bank_id: str
    subject: str
    questions: List[BankQuestion] = field(default_factory=list)

    def add(self, question: BankQuestion) -> None:
        self.questions.append(question)

    def by_knowledge_point(self, point: str) -> List[BankQuestion]:
        return [q for q in self.questions if q.knowledge_point == point]

    def by_type(self, question_type: str) -> List[BankQuestion]:
        return [q for q in self.questions if q.question_type == question_type]

    def count(self) -> int:
        return len(self.questions)
