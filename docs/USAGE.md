# 使用说明

本项目仅依赖 Python 3.10+ 标准库，无需安装任何第三方包。

## 运行方式

```bash
cd score-analysis-system
PYTHONPATH=src python -m score_analysis --data data/sample_scores.json <命令>
```

其中 `--data` 指定成绩数据 JSON 文件，默认 `data/sample_scores.json`。

## 命令总览

| 命令 | 说明 |
| --- | --- |
| `stats` | 描述统计与等级分布 |
| `quality` | 试卷质量评估（难度/区分度/信度） |
| `clean` | 成绩清洗（缺失值与离群值） |
| `grade` | 等级与绩点换算 |
| `rank` | 成绩排名 |
| `normal` | 正态性检验（Jarque-Bera） |
| `standard` | 标准分换算（Z/T/标准九分） |
| `histogram` | 成绩直方图分箱 |
| `report` | 导出报告（json/csv/markdown/html） |
| `full-report` | 综合报表 |
| `export` | 导出报告到文件 |
| `ttest` | 两组成绩独立样本 t 检验 |
| `anova` | 多组成绩方差分析 |
| `progress` | 前后测进步追踪 |
| `forecast` | 成绩趋势预测 |

## 各命令示例

### stats —— 描述统计与分布

```bash
python -m score_analysis --data data/sample_scores.json stats
```

输出均值、中位数、标准差、四分位数、偏度、峰度、等级人数与及格率。

### quality —— 试卷质量评估

```bash
python -m score_analysis --data data/sample_scores.json quality --questions data/questions.json
```

输出整卷难度系数、区分度、克朗巴赫 α 信度，以及逐题难度与区分度。

### ttest —— 两组成绩 t 检验

```bash
python -m score_analysis ttest --group-a data/group_a.json --group-b data/group_b.json
```

输出 t 统计量、p 值、自由度、两组均值差与显著性判定。

### anova —— 多组成绩方差分析

```bash
python -m score_analysis anova --groups data/class1.json data/class2.json data/class3.json
```

输出 F 统计量、p 值、组间/组内平方和与显著性判定。

### progress —— 前后测进步追踪

```bash
python -m score_analysis progress --pre data/pre.json --post data/post.json
```

输出每名学生的进步幅度与进步率，以及全班的进步/退步/持平汇总。

### forecast —— 成绩趋势预测

```bash
python -m score_analysis --data data/sample_scores.json forecast
```

基于历次成绩做线性回归，预测下一次成绩并给出趋势斜率与 R²。

### export —— 导出报告到文件

```bash
python -m score_analysis --data data/sample_scores.json export --format html --output report.html
```

## 数据格式

成绩数据为 JSON 数组，每个元素包含 `student_id`、`name`、`score`，可选 `item_scores` 分项得分：

```json
[
  {"student_id": "2026001", "name": "张伟", "score": 88, "item_scores": {"q1": 9, "q2": 8}}
]
```

分组数据支持两种形式：分数数组 `[85, 90, ...]`，或对象数组 `[{"score": 85}, ...]`。
