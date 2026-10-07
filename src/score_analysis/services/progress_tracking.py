"""学业进步追踪服务。

对比同一批学生前后两次（或多次）考试的成绩，识别进步、退步与持平学生，
并给出个体进步幅度与进步率，用于学情跟踪与教学干预。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class ProgressResult:
    """单个学生的前后测对比结果。"""

    student_id: str
    name: str
    pre_score: float
    post_score: float
    delta: float
    delta_rate: float
    status: str

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "pre_score": round(self.pre_score, 2),
            "post_score": round(self.post_score, 2),
            "delta": round(self.delta, 2),
            "delta_rate": round(self.delta_rate, 4),
            "status": self.status,
        }


@dataclass
class ProgressSummary:
    """全班的进步情况汇总。"""

    total: int
    improved: int
    declined: int
    unchanged: int
    avg_delta: float
    max_improvement: float
    max_decline: float

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "improved": self.improved,
            "declined": self.declined,
            "unchanged": self.unchanged,
            "avg_delta": round(self.avg_delta, 2),
            "max_improvement": round(self.max_improvement, 2),
            "max_decline": round(self.max_decline, 2),
        }


class ProgressTrackingService:
    """进步追踪服务。"""

    def compare(
        self,
        pre_scores: Sequence[float],
        post_scores: Sequence[float],
        ids: Sequence[str],
        names: Sequence[str],
        threshold: float = 0.5,
    ) -> tuple[List[ProgressResult], ProgressSummary]:
        """比较前后测成绩，threshold 为判定"持平"的浮动阈值。"""
        if not (len(pre_scores) == len(post_scores) == len(ids) == len(names)):
            raise ValueError("pre/post/ids/names 长度必须一致")
        results: List[ProgressResult] = []
        improved = declined = unchanged = 0
        deltas: List[float] = []
        for i in range(len(pre_scores)):
            pre, post = pre_scores[i], post_scores[i]
            delta = post - pre
            delta_rate = delta / pre if pre != 0 else 0.0
            if delta > threshold:
                status = "进步"
                improved += 1
            elif delta < -threshold:
                status = "退步"
                declined += 1
            else:
                status = "持平"
                unchanged += 1
            deltas.append(delta)
            results.append(
                ProgressResult(ids[i], names[i], pre, post, delta, delta_rate, status)
            )
        avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
        summary = ProgressSummary(
            total=len(results),
            improved=improved,
            declined=declined,
            unchanged=unchanged,
            avg_delta=avg_delta,
            max_improvement=max(deltas, default=0.0),
            max_decline=min(deltas, default=0.0),
        )
        return results, summary
