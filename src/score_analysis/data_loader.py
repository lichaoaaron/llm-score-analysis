"""成绩数据加载器。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from score_analysis.models.exam import Question
from score_analysis.models.score import StudentScore


def load_scores(data_path: Path) -> List[StudentScore]:
    """从 JSON 文件加载学生成绩。

    支持两种结构：
    - 纯总分：[{"student_id", "name", "score", ...}]
    - 含分项：[{"student_id", "name", "score", "item_scores": {"题1": 8, ...}}]
    """
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    result: List[StudentScore] = []
    for item in raw:
        result.append(
            StudentScore(
                student_id=item["student_id"],
                name=item.get("name", ""),
                score=float(item["score"]),
                item_scores={k: float(v) for k, v in (item.get("item_scores") or {}).items()},
            )
        )
    return result


def load_questions(data_path: Path) -> List[Question]:
    """从 JSON 文件加载试卷题目结构（不含考生得分）。"""
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    result: List[Question] = []
    for item in raw:
        result.append(
            Question(
                question_id=item["question_id"],
                content=item["content"],
                full_score=float(item["full_score"]),
            )
        )
    return result


def fill_item_scores(questions: List[Question], scores: List[StudentScore]) -> List[Question]:
    """把各考生的分项得分按题目名称回填到题目对象中。"""
    for q in questions:
        q.item_scores = [s.item_scores.get(q.content, 0.0) for s in scores]
    return questions
