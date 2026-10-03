"""全局配置模块。

集中管理系统运行参数，支持通过环境变量覆盖，便于在不同院系、不同
课程间切换评分标准与阈值。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _as_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw not in (None, "") else default


def _as_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw not in (None, "") else default


@dataclass(frozen=True)
class AppConfig:
    """成绩分析系统运行参数。"""

    # 满分（百分制默认 100）。
    full_score: float = field(default_factory=lambda: _as_float("SA_FULL_SCORE", 100.0))

    # 及格线。
    pass_line: float = field(default_factory=lambda: _as_float("SA_PASS_LINE", 60.0))

    # 等级划分阈值（优秀/良好/中等/及格，其余为不及格）。
    excellent_line: float = field(default_factory=lambda: _as_float("SA_EXCELLENT", 90.0))
    good_line: float = field(default_factory=lambda: _as_float("SA_GOOD", 80.0))
    medium_line: float = field(default_factory=lambda: _as_float("SA_MEDIUM", 70.0))

    # 区分度计算时高低分组的比例（默认前 27% 与后 27%）。
    group_ratio: float = field(default_factory=lambda: _as_float("SA_GROUP_RATIO", 0.27))

    # 大模型接入。
    llm_provider: str = os.getenv("SA_LLM_PROVIDER", "mock")
    llm_api_base: str = os.getenv("SA_LLM_API_BASE", "")
    llm_api_key: str = os.getenv("SA_LLM_API_KEY", "")
    llm_model: str = os.getenv("SA_LLM_MODEL", "gpt-4o-mini")

    data_dir: Path = Path(os.getenv("SA_DATA_DIR", "data"))


def load_config() -> AppConfig:
    return AppConfig()
