# 自主评估模式

通过迭代评估和改进实现自我提升的模式。

## 概述

评估模式使智能体能够评估并改进自身的输出，从单次生成转向迭代优化循环。

```
生成 → 评估 → 批评 → 改进 → 输出
    ↑                              │
    └──────────────────────────────┘
```

## 使用场景

- **质量关键生成**：需要高精度的代码、报告、分析
- **具有明确评估标准的任务**：存在定义的成功指标
- **需要特定标准的任务**：风格指南、合规性、格式化

---

## 模式1：基本反思

智能体通过自我批评来评估和改进自身的输出。

```python
def reflect_and_refine(task: str, criteria: list[str], max_iterations: int = 3) -> str:
    """带反思循环的生成。"""
    output = llm(f"完成这个任务：\n{task}")
    
    for i in range(max_iterations):
        # 自我批评
        critique = llm(f"""
        根据标准评估这个输出：{criteria}
        输出：{output}
        以JSON格式给出每个标准的评分：PASS/FAIL及反馈。
        """)
        
        critique_data = json.loads(critique)
        all_pass = all(c["status"] == "PASS" for c in critique_data.values())
        if all_pass:
            return output
        
        # 根据批评改进
        failed = {k: v["feedback"] for k, v in critique_data.items() if v["status"] == "FAIL"}
        output = llm(f"针对以下问题改进：{failed}\n原始输出：{output}")
    
    return output
```

**关键洞察**：使用结构化的JSON输出以可靠地解析批评结果。

---

## 模式2：评估器-优化器

将生成和评估分离为不同的组件，以更清晰的职责划分。

```python
class EvaluatorOptimizer:
    def __init__(self, score_threshold: float = 0.8):
        self.score_threshold = score_threshold
    
    def generate(self, task: str) -> str:
        return llm(f"完成：{task}")
    
    def evaluate(self, output: str, task: str) -> dict:
        return json.loads(llm(f"""
        评估任务：{task}的输出
        输出：{output}
        返回JSON：{{"整体评分": 0-1, "维度": {{"准确性": ..., "清晰度": ...}}}}
        """))
    
    def optimize(self, output: str, feedback: dict) -> str:
        return llm(f"根据反馈改进：{feedback}\n输出：{output}")
    
    def run(self, task: str, max_iterations: int = 3) -> str:
        output = self.generate(task)
        for _ in range(max_iterations):
            evaluation = self.evaluate(output, task)
            if evaluation["整体评分"] >= self.score_threshold:
                break
            output = self.optimize(output, evaluation)
        return output
```

---

## 模式3：代码特定反思

用于代码生成的测试驱动优化循环。

```python
class CodeReflector:
    def reflect_and_fix(self, spec: str, max_iterations: int = 3) -> str:
        code = llm(f"为以下需求编写Python代码：{spec}")
        tests = llm(f"为以下需求生成pytest测试：{spec}\n代码：{code}")
        
        for _ in range(max_iterations):
            result = run_tests(code, tests)
            if result["success"]:
                return code
            code = llm(f"修复错误：{result['error']}\n代码：{code}")
        return code
```

---

## 评估策略

### 结果导向

评估输出是否达到预期结果。

```python
def evaluate_outcome(task: str, output: str, expected: str) -> str:
    return llm(f"输出是否达到预期结果？任务：{task}, 预期：{expected}, 输出：{output}")
```

### LLM作为裁判

使用LLM比较和排序输出。

```python
def llm_judge(output_a: str, output_b: str, criteria: str) -> str:
    return llm(f"比较A和B的输出，根据{criteria}判断哪个更好并说明原因。")
```

### 评分标准

根据加权维度对输出进行评分。

```python
RUBRIC = {
    "准确性": {"权重": 0.4},
    "清晰度": {"权重": 0.3},
    "完整性": {"权重": 0.3}
}

def evaluate_with_rubric(output: str, rubric: dict) -> float:
    scores = json.loads(llm(f"对每个维度1-5评分：{list(rubric.keys())}\n输出：{output}"))
    return sum(scores[d] * rubric[d]["权重"] for d in rubric) / 5
```

---

## 最佳实践

| 实践 | 理由 |
|------|------|
| **明确标准** | 提前定义具体、可衡量的评估标准 |
| **迭代限制** | 设置最大迭代次数（3-5次）以防止无限循环 |
| **收敛检查** | 如果输出评分在迭代间未改善则停止 |
| **记录历史** | 保留完整轨迹以供调试和分析 |
| **结构化输出** | 使用JSON以可靠地解析评估结果 |

---

## 快速入门清单

```markdown
## 评估实现清单

### 配置
- [ ] 定义评估标准/评分标准
- [ ] 设置"足够好"的评分阈值
- [ ] 配置最大迭代次数（默认：3）

### 实现
- [ ] 实现generate()函数
- [ ] 实现evaluate()函数并使用结构化输出
- [ ] 实现optimize()函数
- [ ] 连接优化循环

### 安全
- [ ] 添加收敛检测
- [ ] 记录所有迭代以供调试
- [ ] 优雅处理评估解析失败
```
