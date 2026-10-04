"""分析结果导出到文件服务。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from score_analysis.services.report_service import ReportService


class Exporter:
    """把分析结果写入文件。"""

    def __init__(self) -> None:
        self._report = ReportService()

    def export(self, payload: Any, output: Path, fmt: str = "json") -> str:
        """把分析结果写入指定文件，返回写入内容。"""
        if fmt == "csv" and isinstance(payload, list):
            content = self._report.to_csv(payload)
        elif fmt == "markdown" and isinstance(payload, list):
            content = self._report.to_markdown_table(payload)
        elif fmt == "html":
            content = self._report.to_html_page("成绩分析报告", payload)
        else:
            content = json.dumps(payload, ensure_ascii=False, indent=2)
        output.write_text(content, encoding="utf-8")
        return content
