"""加权总评成绩计算服务。

按平时成绩、期中成绩、期末成绩等分项按权重计算课程总评成绩，支持
权重归一化校验。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Component:
    """一个成绩构成项。"""

    name: str
    weight: float
    scores: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "weight": self.weight}


@dataclass
class WeightedResult:
    """加权总评结果。"""

    student_id: str
    total_score: float
    components: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "total_score": round(self.total_score, 2),
            "components": {k: round(v, 2) for k, v in self.components.items()},
        }


class WeightedScoreService:
    """加权成绩计算。"""

    def __init__(self) -> None:
        self._components: List[Component] = []

    def add_component(self, name: str, weight: float) -> None:
        """登记一个成绩构成项及其权重。"""
        self._components.append(Component(name=name, weight=weight))

    def _validate_weights(self) -> None:
        total = sum(c.weight for c in self._components)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"权重之和必须为 1，当前为 {total}")

    def compute(self, student_id: str, component_scores: Dict[str, float]) -> WeightedResult:
        """计算某学生的加权总评成绩。"""
        self._validate_weights()
        total = 0.0
        detail: Dict[str, float] = {}
        for component in self._components:
            score = component_scores.get(component.name, 0.0)
            weighted = score * component.weight
            detail[component.name] = weighted
            total += weighted
        return WeightedResult(student_id=student_id, total_score=total, components=detail)

    def compute_all(self, rows: List[Dict[str, float]]) -> List[WeightedResult]:
        """批量计算，rows 中每条需含 student_id 与各分项成绩。"""
        results: List[WeightedResult] = []
        for row in rows:
            student_id = str(row.get("student_id", ""))
            results.append(self.compute(student_id, row))
        results.sort(key=lambda r: r.total_score, reverse=True)
        return results
