"""综合报表构建服务。

把描述统计、分布、试卷质量、逐题分析、排名等结果汇总为一份结构化
报表，供多格式导出。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from score_analysis.config import AppConfig
from score_analysis.models.score import StudentScore
from score_analysis.services.analysis_engine import AnalysisEngine
from score_analysis.services.grade_scale import GradeScaleService
from score_analysis.services.normality import NormalityService
from score_analysis.services.ranking_service import RankingService


@dataclass
class FullReport:
    """综合报表。"""

    title: str
    sections: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"title": self.title, "sections": self.sections}


class ReportBuilder:
    """综合报表构建器。"""

    def __init__(self, config: AppConfig, engine: AnalysisEngine) -> None:
        self.config = config
        self.engine = engine
        self.normality = NormalityService()
        self.ranking = RankingService(GradeScaleService())

    def build(self, title: str, scores: List[StudentScore]) -> FullReport:
        """构建完整报表。"""
        report = self.engine.run(scores)
        values = [s.score for s in scores]
        normal = self.normality.test(values)
        ranking = self.ranking.rank([(s.student_id, s.name, s.score) for s in scores])

        sections = [
            {"heading": "一、描述统计", "rows": [report.descriptive]},
            {"heading": "二、成绩分布", "rows": [report.distribution]},
            {"heading": "三、正态性检验", "rows": [normal.to_dict()]},
            {"heading": "四、试卷质量", "rows": [report.paper_quality]},
            {"heading": "五、逐题分析", "rows": report.question_stats},
            {"heading": "六、排名与绩点", "rows": [r.to_dict() for r in ranking[:20]]},
        ]
        return FullReport(title=title, sections=sections)
