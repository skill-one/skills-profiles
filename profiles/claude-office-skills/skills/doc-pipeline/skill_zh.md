# 文档处理流程技能

## 概述

该技能能够构建文档处理流程 - 将多个操作（提取、转换、转换）链式组合成可重用的工作流，并在各阶段之间流动数据。

## 如何使用

1. 描述您想要完成的目标
2. 提供所需的输入数据或文件
3. 我将执行相应的操作

**示例提示：**
- "PDF → 提取文本 → 翻译 → 生成DOCX"
- "图像 → OCR → 摘要 → 创建报告"
- "Excel → 分析 → 生成图表 → 创建PPT"
- "多个输入 → 合并 → 格式化 → 输出"

## 领域知识


### 流程架构

```
阶段1      阶段2      阶段3      阶段4
┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│提取│ → │转换│ → │ AI   │ → │输出│
│ PDF  │    │  数据│    │分析│   │ DOCX │
└──────┘    └──────┘    └──────┘    └──────┘
     │           │           │           │
     └───────────┴───────────┴───────────┘
                 数据流
```

### 流程领域特定语言（DSL）

```yaml
# pipeline.yaml
name: 合同审核流程
description: 提取、分析和报告合同

stages:
  - name: extract
    operation: pdf-extraction
    input: $input_file
    output: $extracted_text
    
  - name: analyze
    operation: ai-analyze
    input: $extracted_text
    prompt: "审核此合同中的风险..."
    output: $analysis
    
  - name: report
    operation: docx-generation
    input: $analysis
    template: templates/review_report.docx
    output: $output_file
```

### Python实现

```python
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class Stage:
    name: str
    operation: Callable
    
class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.stages: list[Stage] = []
    
    def add_stage(self, name: str, operation: Callable):
        self.stages.append(Stage(name, operation))
        return self  # 流畅API
    
    def run(self, input_data: Any) -> Any:
        data = input_data
        for stage in self.stages:
            print(f"运行阶段: {stage.name}")
            data = stage.operation(data)
        return data

# 示例用法
pipeline = Pipeline("合同审核")
pipeline.add_stage("extract", extract_pdf_text)
pipeline.add_stage("analyze", analyze_with_ai)
pipeline.add_stage("generate", create_docx_report)

result = pipeline.run("/path/to/contract.pdf")
```

### 高级：条件流程

```python
class ConditionalPipeline(Pipeline):
    def add_conditional_stage(self, name: str, condition: Callable, 
                               if_true: Callable, if_false: Callable):
        def conditional_op(data):
            if condition(data):
                return if_true(data)
            return if_false(data)
        return self.add_stage(name, conditional_op)

# 使用示例
pipeline.add_conditional_stage(
    "ocr_if_needed",
    condition=lambda d: d.get("has_images"),
    if_true=run_ocr,
    if_false=lambda d: d
)
```

## 最佳实践

1. **保持阶段专注（单一职责）**
2. **使用中间输出进行调试**
3. **实现阶段级错误处理**
4. **通过YAML/JSON使流程可配置**

## 安装

```bash
# 安装所需依赖
pip install python-docx openpyxl python-pptx reportlab jinja2
```

## 资源

- [自定义仓库](https://github.com/claude-office-skills/skills)
- [Claude Office技能中心](https://github.com/claude-office-skills/skills)
