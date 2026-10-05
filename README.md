# 基于大模型的成绩统计分析与试卷质量评估系统

面向高校课程成绩分析与试卷质量评估的命令行工具与 Python 库。读取学生成绩数据，计算描述统计量与成绩分布，评估试卷的难度、区分度与信度，并生成学情分析报告。

## 功能

- 成绩导入与清洗（JSON / CSV）
- 描述性统计（均值、中位数、标准差、四分位数、偏度、峰度）
- 成绩分布与等级划分（优秀/良好/中等/及格/不及格）、及格率
- 试卷质量评估（难度系数、区分度、信度 Cronbach's α）
- 逐题分析（每题难度、区分度、质量等级）
- 学情报告生成（规则模板，可选接入大模型）
- 多格式报告导出（JSON / CSV / Markdown / HTML）

## 运行

```bash
PYTHONPATH=src python -m score_analysis --data data/sample_scores.json stats
PYTHONPATH=src python -m score_analysis --data data/sample_scores.json quality
PYTHONPATH=src python -m score_analysis --data data/sample_scores.json report --format html
```

## 数据格式

```json
[
  {"student_id": "2026001", "name": "张伟", "score": 88,
   "item_scores": {"选择题": 18, "填空题": 16, "简答题": 24, "计算题": 20, "综合题": 10}}
]
```

`item_scores` 为可选的分项得分，用于试卷信度与逐题分析。
