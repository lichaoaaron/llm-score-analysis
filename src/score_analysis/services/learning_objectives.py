"""课程目标达成度服务（OBE 成果导向）。

将试卷中各题目映射到课程教学目标，通过学生在对应题目上的得分率
计算每个目标的达成度，用于判断教学目标的达成情况，支撑持续改进。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass
class ObjectiveResult:
    """单个课程目标的达成度。"""

    objective_id: str
    name: str
    total_possible: float
    total_obtained: float
    achievement: float
    level: str

    def to_dict(self) -> dict:
        return {
            "objective_id": self.objective_id,
            "name": self.name,
            "total_possible": round(self.total_possible, 2),
            "total_obtained": round(self.total_obtained, 2),
            "achievement": round(self.achievement, 4),
            "level": self.level,
        }


class LearningObjectivesService:
    """课程目标达成度评估服务。"""

    def evaluate(
        self,
        objective_names: Dict[str, str],
        question_objectives: Dict[str, str],
        question_full_scores: Dict[str, float],
        student_item_scores: Sequence[Dict[str, float]],
    ) -> List[ObjectiveResult]:
        """评估各课程目标的达成度。

        参数说明：
        - objective_names：目标 id -> 目标名称；
        - question_objectives：题目 id -> 所属目标 id；
        - question_full_scores：题目 id -> 该题满分；
        - student_item_scores：每名学生的 {题目 id: 得分}。
        """
        # 汇总每个目标在所有学生上的总分与实得分。
        possibles: Dict[str, float] = {oid: 0.0 for oid in objective_names}
        obtained: Dict[str, float] = {oid: 0.0 for oid in objective_names}
        for qid, oid in question_objectives.items():
            if oid not in possibles:
                continue
            full = question_full_scores.get(qid, 0.0)
            possibles[oid] += full * len(student_item_scores)
            for student in student_item_scores:
                obtained[oid] += student.get(qid, 0.0)
        results: List[ObjectiveResult] = []
        for oid in objective_names:
            total_possible = possibles[oid]
            total_obtained = obtained[oid]
            achievement = total_obtained / total_possible if total_possible > 0 else 0.0
            results.append(
                ObjectiveResult(
                    objective_id=oid,
                    name=objective_names[oid],
                    total_possible=total_possible,
                    total_obtained=total_obtained,
                    achievement=achievement,
                    level=self._level(achievement),
                )
            )
        return results

    @staticmethod
    def _level(achievement: float) -> str:
        if achievement >= 0.85:
            return "达成良好"
        if achievement >= 0.70:
            return "基本达成"
        if achievement >= 0.60:
            return "接近达成"
        return "未达成"
