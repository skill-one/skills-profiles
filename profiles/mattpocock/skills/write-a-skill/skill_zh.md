# 技能编写

## 编写流程

1. **收集需求** - 向用户询问：
   - 技能涵盖的任务/领域是什么？
   - 应处理哪些具体的使用场景？
   - 是否需要可执行的脚本，还是只需指令？
   - 是否需要包含参考材料？

2. **草拟技能** - 创建：
   - 包含简洁说明的 SKILL.md
   - 若内容超过 500 行，则添加额外的参考文件
   - 若需要确定性操作，则添加实用脚本

3. **与用户审阅** - 呈现草稿并询问：
   - 此内容是否涵盖了您的使用场景？
   - 是否有遗漏或不明确之处？
   - 是否有章节需要更加或更少的详细说明？

## 技能结构

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── REFERENCE.md       # Detailed docs (if needed)
├── EXAMPLES.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md 模板

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [REFERENCE.md](REFERENCE.md)]
```

## 描述要求

描述是 **您的代理（agent）在决定加载哪个技能时唯一看到的内容**。它在系统提示词中与其他已安装技能一同展示。您的代理读取这些描述，并根据用户请求选择合适的技能。

**目标**：为您的代理提供足够的信息，使其能够：

1. 该技能提供何种能力
2. 在何时及为何触发它（特定关键词、场景、文件类型）

**格式**：

- 最多 1024 字符
- 以第三人称撰写
- 第一句：说明其功能
- 第二句："当 [特定触发条件] 时使用"

**示例（佳）**：

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**示例（劣）**：

```
Helps with documents.
```

## 何时添加脚本

在以下情况添加实用脚本：

- 操作为确定性操作（验证、格式化）
- 相同代码会被重复生成
- 错误需要明确处理

脚本可节省令牌，并在可靠性方面优于生成代码。

## 何时拆分文件

在以下情况下拆分为独立文件：

- SKILL.md 超过 100 行
- 内容包含不同领域（如金融与销售模式）
- 高级功能很少需要

## 审阅检查清单

撰写草稿后，进行以下检查：

- [ ] 描述包含触发条件（"当...时使用"）
- [ ] SKILL.md 不超过 100 行
- [ ] 不包含时效性信息
- [ ] 术语一致
- [ ] 包含具体示例
- [ ] 引用仅一层深度
