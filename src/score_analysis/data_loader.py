"""成绩数据加载器。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

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
