"""命令行入口。

子命令：
- stats：描述统计与分布；
- quality：试卷质量评估；
- report：导出报告（json/csv/markdown/html）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from score_analysis.config import load_config
from score_analysis.data_loader import load_scores
from score_analysis.models.score import StudentScore
from score_analysis.services.analysis_engine import AnalysisEngine
from score_analysis.services.llm_client import MockLLMClient, OpenAICompatibleClient
from score_analysis.services.report_service import ReportService


def _build_llm(config):
    if config.llm_provider == "openai_compatible":
        return OpenAICompatibleClient(config.llm_api_base, config.llm_api_key, config.llm_model)
    return MockLLMClient()


def _load(data_path: Path) -> List[StudentScore]:
    if not data_path.exists():
        print(f"数据文件不存在：{data_path}", file=sys.stderr)
        sys.exit(1)
    return load_scores(data_path)


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_stats(args, config) -> None:
    scores = _load(args.data)
    report = AnalysisEngine(config, _build_llm(config)).run(scores)
    _print_json({"descriptive": report.descriptive, "distribution": report.distribution})


def cmd_quality(args, config) -> None:
    scores = _load(args.data)
    report = AnalysisEngine(config, _build_llm(config)).run(scores)
    _print_json({"paper_quality": report.paper_quality, "question_stats": report.question_stats})


def cmd_report(args, config) -> None:
    scores = _load(args.data)
    report = AnalysisEngine(config, _build_llm(config)).run(scores)
    payload = report.to_dict()
    service = ReportService()
    if args.format == "csv":
        print(service.to_csv([report.descriptive, report.paper_quality]))
    elif args.format == "markdown":
        print(service.to_markdown_table([report.descriptive, report.paper_quality]))
    elif args.format == "html":
        print(service.to_html_page("成绩分析报告", [
            {"heading": "描述统计", "rows": [report.descriptive]},
            {"heading": "试卷质量", "rows": [report.paper_quality]},
            {"heading": "逐题分析", "rows": report.question_stats},
        ]))
    else:
        _print_json(payload)


def main(argv: List[str] | None = None) -> None:
    config = load_config()
    parser = argparse.ArgumentParser(prog="score-analysis", description="成绩统计分析与试卷质量评估系统")
    parser.add_argument("--data", type=Path, default=config.data_dir / "sample_scores.json", help="成绩数据 JSON 路径")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stats", help="描述统计与分布").set_defaults(func=cmd_stats)
    sub.add_parser("quality", help="试卷质量评估").set_defaults(func=cmd_quality)

    report = sub.add_parser("report", help="导出报告")
    report.add_argument("--format", choices=["json", "csv", "markdown", "html"], default="json")
    report.set_defaults(func=cmd_report)

    args = parser.parse_args(argv)
    args.func(args, config)


if __name__ == "__main__":
    main()
