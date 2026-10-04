"""相关矩阵分析服务。

计算多个成绩序列（如各题得分、总分）两两之间的皮尔逊相关系数，
输出相关矩阵，用于分析题目间及题目与总分的关系。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from score_analysis.utils.statistics import pearson_correlation


@dataclass
class CorrelationMatrix:
    """相关矩阵。"""

    labels: List[str]
    matrix: List[List[float]] = field(default_factory=list)

    def get(self, i: int, j: int) -> float:
        return self.matrix[i][j]

    def to_dict(self) -> dict:
        return {
            "labels": self.labels,
            "matrix": [[round(v, 4) for v in row] for row in self.matrix],
        }

    def to_table(self) -> List[Dict[str, float]]:
        """转为行式表格，便于报告输出。"""
        rows: List[Dict[str, float]] = []
        for i in range(len(self.labels)):
            row: Dict[str, float] = {"指标": self.labels[i]}  # type: ignore[assignment]
            for j, label in enumerate(self.labels):
                row[label] = self.matrix[i][j]  # type: ignore[index]
            rows.append(row)
        return rows


class CorrelationService:
    """相关矩阵分析。"""

    def compute(self, data: Dict[str, Sequence[float]]) -> CorrelationMatrix:
        """data 为 {名称: 序列}，返回两两相关系数矩阵。"""
        labels = list(data.keys())
        n = len(labels)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                elif j > i:
                    r = pearson_correlation(list(data[labels[i]]), list(data[labels[j]]))
                    matrix[i][j] = r
                    matrix[j][i] = r
        return CorrelationMatrix(labels=labels, matrix=matrix)
