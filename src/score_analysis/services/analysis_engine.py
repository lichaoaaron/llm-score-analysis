"""成绩分析编排引擎。

把成绩清洗、描述统计、分布分析、试卷质量评估、学情报告生成编排为一次
完整分析，输出统一的结构化结果。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from score_analysis.config import AppConfig
from score_analysis.models.exam import Question
from score_analysis.models.score import StudentScore
from score_analysis.services.item_analysis import ItemAnalysisService
from score_analysis.services.llm_client import LLMClient
from score_analysis.services.statistics_service import StatisticsService


@dataclass
class ScoreReport:
    """一次完整分析产出。"""

    descriptive: Dict[str, Any]
    distribution: Dict[str, Any]
    paper_quality: Dict[str, Any]
    question_stats: List[Dict[str, Any]] = field(default_factory=list)
    narrative: str = ""

    def to_dict(self) -> dict:
        return {
            "descriptive": self.descriptive,
            "distribution": self.distribution,
            "paper_quality": self.paper_quality,
            "question_stats": self.question_stats,
            "narrative": self.narrative,
        }


class AnalysisEngine:
    """成绩分析编排引擎。"""

    def __init__(self, config: AppConfig, llm: LLMClient) -> None:
        self.config = config
        self.statistics = StatisticsService(config)
        self.item_analysis = ItemAnalysisService(config)
        self.llm = llm

    def run(
        self,
        scores: List[StudentScore],
        questions: List[Question] | None = None,
    ) -> ScoreReport:
        """执行完整分析流程。"""
        values = [s.score for s in scores]
        distribution = self.statistics.distribute(values)
        stats = distribution.stats

        total_scores = values

        paper_quality = self.item_analysis.paper_quality(total_scores, questions or [])
        question_stats = (
            self.item_analysis.analyze_questions(questions, total_scores) if questions else []
        )

        narrative = self.llm.summarize(
            {
                "count": stats.count,
                "mean": stats.mean,
                "stddev": stats.stddev,
                "pass_rate": distribution.pass_rate,
                "reliability": paper_quality.reliability,
            }
        )

        return ScoreReport(
            descriptive=stats.to_dict(),
            distribution=distribution.to_dict(),
            paper_quality=paper_quality.to_dict(),
            question_stats=[q.to_dict() for q in question_stats],
            narrative=narrative,
        )
