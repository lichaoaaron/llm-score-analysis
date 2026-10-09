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
from score_analysis.data_loader import fill_item_scores, load_questions, load_scores
from score_analysis.models.score import StudentScore
from score_analysis.services.analysis_engine import AnalysisEngine
from score_analysis.services.grade_scale import GradeScaleService
from score_analysis.services.histogram import HistogramService
from score_analysis.services.llm_client import MockLLMClient, OpenAICompatibleClient
from score_analysis.services.normality import NormalityService
from score_analysis.services.ranking_service import RankingService
from score_analysis.services.report_service import ReportService
from score_analysis.services.score_cleaner import ScoreCleaner
from score_analysis.services.standard_score import StandardScoreService
from score_analysis.services.dedup import DedupService
from score_analysis.services.exporter import Exporter
from score_analysis.services.report_builder import ReportBuilder
from score_analysis.services.hypothesis_testing import HypothesisTestingService
from score_analysis.services.progress_tracking import ProgressTrackingService
from score_analysis.services.forecast import ForecastService


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
    questions_path = args.questions or config.data_dir / "questions.json"
    questions = load_questions(Path(questions_path)) if Path(questions_path).exists() else None
    if questions:
        fill_item_scores(questions, scores)
    report = AnalysisEngine(config, _build_llm(config)).run(scores, questions)
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


def cmd_clean(args, config) -> None:
    scores = _load(args.data)
    result = ScoreCleaner(config).clean([s.score for s in scores])
    _print_json(result.to_dict())


def cmd_grade(args, config) -> None:
    scores = _load(args.data)
    service = GradeScaleService()
    output = [
        {"student_id": s.student_id, "name": s.name, "score": s.score,
         "grade": service.grade(s.score), "gpa": service.gpa(s.score)}
        for s in scores
    ]
    _print_json(output)


def cmd_rank(args, config) -> None:
    scores = _load(args.data)
    results = RankingService(GradeScaleService()).rank(
        [(s.student_id, s.name, s.score) for s in scores]
    )
    _print_json([r.to_dict() for r in results])


def cmd_normal(args, config) -> None:
    scores = _load(args.data)
    result = NormalityService().test([s.score for s in scores])
    _print_json(result.to_dict())


def cmd_histogram(args, config) -> None:
    scores = _load(args.data)
    bins = HistogramService().build([s.score for s in scores], bin_width=args.bin_width)
    _print_json([b.to_dict() for b in bins])


def cmd_standard(args, config) -> None:
    scores = _load(args.data)
    values = [s.score for s in scores]
    service = StandardScoreService()
    service.fit(values)
    output = [service.convert(s.score).to_dict() for s in scores]
    _print_json(output)


def cmd_full_report(args, config) -> None:
    scores = _load(args.data)
    engine = AnalysisEngine(config, _build_llm(config))
    report = ReportBuilder(config, engine).build("成绩统计分析与试卷质量评估报告", scores)
    _print_json(report.to_dict())


def cmd_export(args, config) -> None:
    scores = _load(args.data)
    engine = AnalysisEngine(config, _build_llm(config))
    report = ReportBuilder(config, engine).build("成绩统计分析与试卷质量评估报告", scores)
    payload = report.to_dict()
    if not args.output:
        print("请通过 --output 指定输出文件路径", file=sys.stderr)
        sys.exit(1)
    Exporter().export(payload, Path(args.output), fmt=args.format)
    print(f"已导出到 {args.output}")


def _parse_score_list(raw) -> List[float]:
    """把 JSON 解析结果规整为一组分数。

    支持 ``[85, 90, ...]``、``[{"score": 85}, ...]`` 与 ``{"scores": [...]}`` 三种写法。
    空数据或无法解析为数值时抛出 ``ValueError``，由调用方转为友好提示。
    """
    if isinstance(raw, dict):
        raw = raw.get("scores", [])
    if not isinstance(raw, list):
        raise ValueError("应为数组，或包含 scores 数组的对象")
    if not raw:
        raise ValueError("成绩数据为空，无法进行统计检验")

    values: List[float] = []
    for index, item in enumerate(raw, start=1):
        try:
            values.append(float(item) if isinstance(item, (int, float)) else float(item["score"]))
        except (TypeError, KeyError, ValueError):
            raise ValueError(f"第 {index} 条成绩无法解析为数值") from None
    return values


def _load_score_list(path: Path) -> List[float]:
    """从 JSON 文件加载一组分数（支持 [85, 90, ...] 或 [{...\"score\": 85}, ...]）。"""
    if not path.exists():
        print(f"数据文件不存在：{path}", file=sys.stderr)
        sys.exit(1)
    raw = json.loads(path.read_text(encoding="utf-8"))
    try:
        return _parse_score_list(raw)
    except ValueError as exc:
        print(f"数据文件格式有误：{path}（{exc}）", file=sys.stderr)
        sys.exit(1)


def cmd_ttest(args, config) -> None:
    a = _load_score_list(Path(args.group_a))
    b = _load_score_list(Path(args.group_b))
    result = HypothesisTestingService().independent_t_test(a, b, alpha=args.alpha)
    _print_json(result.to_dict())


def cmd_anova(args, config) -> None:
    groups = [_load_score_list(Path(p)) for p in args.groups]
    result = HypothesisTestingService().one_way_anova(groups, alpha=args.alpha)
    _print_json(result.to_dict())


def cmd_progress(args, config) -> None:
    pre = _load_score_list(Path(args.pre))
    post = _load_score_list(Path(args.post))
    ids = [str(i + 1) for i in range(len(pre))]
    names = [f"学生{i + 1}" for i in range(len(pre))]
    results, summary = ProgressTrackingService().compare(pre, post, ids, names)
    _print_json({"summary": summary.to_dict(), "details": [r.to_dict() for r in results]})


def cmd_dedup(args, config) -> None:
    scores = _load(args.data)
    result = DedupService().dedup(scores, strategy=args.strategy)
    _print_json(result.to_dict())


def cmd_forecast(args, config) -> None:
    scores = _load(args.data)
    history: dict = {}
    names: dict = {}
    for s in scores:
        history.setdefault(s.student_id, []).append(s.score)
        names[s.student_id] = s.name
    results = ForecastService().predict_next(history, names)
    _print_json([r.to_dict() for r in results])


def main(argv: List[str] | None = None) -> None:
    config = load_config()
    parser = argparse.ArgumentParser(prog="score-analysis", description="成绩统计分析与试卷质量评估系统")
    parser.add_argument("--data", type=Path, default=config.data_dir / "sample_scores.json", help="成绩数据 JSON 路径")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stats", help="描述统计与分布").set_defaults(func=cmd_stats)
    quality = sub.add_parser("quality", help="试卷质量评估")
    quality.add_argument("--questions", help="试卷题目结构 JSON 路径（默认 data/questions.json）")
    quality.set_defaults(func=cmd_quality)
    sub.add_parser("clean", help="成绩清洗").set_defaults(func=cmd_clean)
    sub.add_parser("grade", help="等级与绩点").set_defaults(func=cmd_grade)
    sub.add_parser("rank", help="成绩排名").set_defaults(func=cmd_rank)
    sub.add_parser("normal", help="正态性检验").set_defaults(func=cmd_normal)
    sub.add_parser("standard", help="标准分换算").set_defaults(func=cmd_standard)

    histogram = sub.add_parser("histogram", help="成绩直方图分箱")
    histogram.add_argument("--bin-width", type=float, default=10.0, help="分箱宽度")
    histogram.set_defaults(func=cmd_histogram)

    report = sub.add_parser("report", help="导出报告")
    report.add_argument("--format", choices=["json", "csv", "markdown", "html"], default="json")
    report.set_defaults(func=cmd_report)

    sub.add_parser("full-report", help="综合报表").set_defaults(func=cmd_full_report)

    export = sub.add_parser("export", help="导出报告到文件")
    export.add_argument("--format", choices=["json", "csv", "markdown", "html"], default="json")
    export.add_argument("--output", required=True, help="输出文件路径")
    export.set_defaults(func=cmd_export)

    ttest = sub.add_parser("ttest", help="两组成绩独立样本 t 检验")
    ttest.add_argument("--group-a", required=True, help="第一组成绩 JSON 文件")
    ttest.add_argument("--group-b", required=True, help="第二组成绩 JSON 文件")
    ttest.add_argument("--alpha", type=float, default=0.05, help="显著性水平")
    ttest.set_defaults(func=cmd_ttest)

    anova = sub.add_parser("anova", help="多组成绩方差分析")
    anova.add_argument("--groups", nargs="+", required=True, help="多组成绩 JSON 文件（空格分隔）")
    anova.add_argument("--alpha", type=float, default=0.05, help="显著性水平")
    anova.set_defaults(func=cmd_anova)

    progress = sub.add_parser("progress", help="前后测进步追踪")
    progress.add_argument("--pre", required=True, help="前测成绩 JSON 文件")
    progress.add_argument("--post", required=True, help="后测成绩 JSON 文件")
    progress.set_defaults(func=cmd_progress)

    dedup = sub.add_parser("dedup", help="成绩记录去重")
    dedup.add_argument("--strategy", choices=["max", "avg"], default="max",
                       help="同一学号存在多条记录时的处理策略（默认 max 取最高分）")
    dedup.set_defaults(func=cmd_dedup)

    sub.add_parser("forecast", help="成绩趋势预测").set_defaults(func=cmd_forecast)

    args = parser.parse_args(argv)
    args.func(args, config)


if __name__ == "__main__":
    main()
