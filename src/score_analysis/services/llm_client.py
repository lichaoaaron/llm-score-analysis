"""大模型客户端：用于生成学情分析自然语言报告。

规则模板离线兜底，OpenAI 兼容接口可选接入，未配置密钥时功能不受影响。
"""
from __future__ import annotations

import json
import urllib.request
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """大模型客户端抽象接口。"""

    @abstractmethod
    def summarize(self, stats: dict) -> str:
        """基于统计结果生成一段学情分析报告。"""


class MockLLMClient(LLMClient):
    """规则模板客户端：离线按统计指标拼装学情报告。"""

    def summarize(self, stats: dict) -> str:
        count = stats.get("count", 0)
        mean_score = stats.get("mean", 0)
        pass_rate = stats.get("pass_rate", 0)
        stddev = stats.get("stddev", 0)

        if mean_score >= 85:
            level = "整体成绩优秀，知识掌握扎实"
        elif mean_score >= 70:
            level = "整体成绩良好，大部分知识点掌握到位"
        elif mean_score >= 60:
            level = "整体成绩中等，存在一定提升空间"
        else:
            level = "整体成绩偏低，需要加强薄弱环节的复习"

        dispersion = "成绩分布较集中" if stddev <= 10 else "成绩分化较明显"
        return (
            f"本次共 {count} 人参加，平均分 {mean_score:.1f}，及格率 {pass_rate:.1%}。"
            f"{level}；标准差 {stddev:.1f}，{dispersion}。"
        )


class OpenAICompatibleClient(LLMClient):
    """通过标准库直连 OpenAI 兼容接口生成报告。"""

    def __init__(self, api_base: str, api_key: str, model: str) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._fallback = MockLLMClient()

    def summarize(self, stats: dict) -> str:
        if not self.api_base or not self.api_key:
            return self._fallback.summarize(stats)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是教学助手，根据成绩统计生成一段简明的学情分析。"},
                {"role": "user", "content": json.dumps(stats, ensure_ascii=False)},
            ],
        }
        req = urllib.request.Request(
            f"{self.api_base}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return self._fallback.summarize(stats)
