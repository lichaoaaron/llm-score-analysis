"""服务层。"""
from score_analysis.services.statistics_service import (
    DescriptiveStats,
    ScoreDistribution,
    StatisticsService,
)
from score_analysis.services.item_analysis import ItemAnalysisService, PaperQuality
from score_analysis.services.report_service import ReportService
from score_analysis.services.llm_client import LLMClient, MockLLMClient, OpenAICompatibleClient
from score_analysis.services.analysis_engine import AnalysisEngine, ScoreReport
from score_analysis.services.score_cleaner import CleaningReport, CleaningResult, ScoreCleaner
from score_analysis.services.importer import ImportResult, ScoreImporter
from score_analysis.services.normality import NormalityResult, NormalityService
from score_analysis.services.group_analysis import GroupAnalysisService, GroupSummary
from score_analysis.services.trend_analysis import TrendAnalysisService, TrendPoint, TrendReport
from score_analysis.services.grade_scale import GradeBand, GradeScale, GradeScaleService
from score_analysis.services.weighted_score import Component, WeightedResult, WeightedScoreService
from score_analysis.services.paper_generator import GeneratedPaper, PaperGenerator, PaperSpec
from score_analysis.services.histogram import HistogramBin, HistogramService
from score_analysis.services.standard_score import StandardScore, StandardScoreService
from score_analysis.services.regression import LinearRegressionService, RegressionResult
from score_analysis.services.correlation import CorrelationMatrix, CorrelationService
from score_analysis.services.ranking_service import RankResult, RankingService
from score_analysis.services.report_builder import FullReport, ReportBuilder
from score_analysis.services.consistency import ConsistencyIssue, ConsistencyResult, ConsistencyService
from score_analysis.services.paper_structure import PaperStructureService, StructureSummary
from score_analysis.services.exporter import Exporter

__all__ = [
    "DescriptiveStats",
    "ScoreDistribution",
    "StatisticsService",
    "ItemAnalysisService",
    "PaperQuality",
    "ReportService",
    "LLMClient",
    "MockLLMClient",
    "OpenAICompatibleClient",
    "AnalysisEngine",
    "ScoreReport",
    "ScoreCleaner",
    "CleaningReport",
    "CleaningResult",
    "ScoreImporter",
    "ImportResult",
    "NormalityService",
    "NormalityResult",
    "GroupAnalysisService",
    "GroupSummary",
    "TrendAnalysisService",
    "TrendPoint",
    "TrendReport",
    "GradeBand",
    "GradeScale",
    "GradeScaleService",
    "Component",
    "WeightedResult",
    "WeightedScoreService",
    "PaperGenerator",
    "PaperSpec",
    "GeneratedPaper",
    "HistogramBin",
    "HistogramService",
    "StandardScore",
    "StandardScoreService",
    "LinearRegressionService",
    "RegressionResult",
    "CorrelationMatrix",
    "CorrelationService",
    "RankResult",
    "RankingService",
    "FullReport",
    "ReportBuilder",
    "ConsistencyIssue",
    "ConsistencyResult",
    "ConsistencyService",
    "PaperStructureService",
    "StructureSummary",
    "Exporter",
]
