# LLM 评估

掌握 LLM 应用的全面评估策略，从自动化指标到人工评估和 A/B 测试。

## 使用此技能的场景

- 系统地衡量 LLM 应用性能
- 比较不同的模型或提示
- 在部署前检测性能退化
- 验证提示变更带来的改进
- 建立生产系统的信心
- 建立基线并跟踪随时间推移的进展
- 调试意外模型行为

## 核心评估类型

### 1. 自动化指标

使用计算分数进行快速、可重复、可扩展的评估。

**文本生成：**

- **BLEU**：N-gram 重叠（翻译）
- **ROUGE**：基于召回（摘要）
- **METEOR**：语义相似度
- **BERTScore**：基于嵌入的相似度
- **困惑度**：语言模型置信度

**分类：**

- **准确率**：正确百分比
- **精确率/召回率/F1**：特定类别性能
- **混淆矩阵**：错误模式
- **AUC-ROC**：排序质量

**检索（RAG）：**

- **MRR**：平均倒数排名
- **NDCG**：归一化折扣累积增益
- **Precision@K**：前 K 项的相关性
- **Recall@K**：前 K 项的覆盖率

### 2. 人工评估

对难以自动化的质量方面进行手动评估。

**维度：**

- **准确率**：事实正确性
- **连贯性**：逻辑流畅性
- **相关性**：是否回答了问题
- **流畅性**：自然语言质量
- **安全性**：无有害内容
- **帮助性**：对用户是否有用

### 3. 以 LLM 评判 LLM

使用更强的 LLM 评估较弱的模型输出。

**方法：**

- **逐点评估**：评分单个响应
- **成对比较**：比较两个响应
- **基于参考**：与黄金标准比较
- **无参考**：无需真实标准进行评判

## 快速入门

```python
from dataclasses import dataclass
from typing import Callable
import numpy as np

@dataclass
class Metric:
    name: str
    fn: Callable

    @staticmethod
    def accuracy():
        return Metric("accuracy", calculate_accuracy)

    @staticmethod
    def bleu():
        return Metric("bleu", calculate_bleu)

    @staticmethod
    def bertscore():
        return Metric("bertscore", calculate_bertscore)

    @staticmethod
    def custom(name: str, fn: Callable):
        return Metric(name, fn)

class EvaluationSuite:
    def __init__(self, metrics: list[Metric]):
        self.metrics = metrics

    async def evaluate(self, model, test_cases: list[dict]) -> dict:
        results = {m.name: [] for m in self.metrics}

        for test in test_cases:
            prediction = await model.predict(test["input"])

            for metric in self.metrics:
                score = metric.fn(
                    prediction=prediction,
                    reference=test.get("expected"),
                    context=test.get("context")
                )
                results[metric.name].append(score)

        return {
            "metrics": {k: np.mean(v) for k, v in results.items()},
            "raw_scores": results
        }

# 使用示例
suite = EvaluationSuite([
    Metric.accuracy(),
    Metric.bleu(),
    Metric.bertscore(),
    Metric.custom("groundedness", check_groundedness)
])

test_cases = [
    {
        "input": "法国的首都是哪里？",
        "expected": "巴黎",
        "context": "法国是一个欧洲国家。巴黎是其首都。"
    },
]

results = await suite.evaluate(model=your_model, test_cases=test_cases)
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。
