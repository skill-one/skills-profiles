# 技能编写器

这个技能帮助你创建结构良好的 Agent 技能，用于 Claude 代码，并遵循最佳实践和验证要求。

## 何时使用此技能

当你需要：
- 创建新的 Agent 技能
- 编写或更新 SKILL.md 文件
- 设计技能结构和 frontmatter
- 排错技能发现问题
- 将现有提示或工作流转换为技能

## 指令

### 第 1 步：确定技能范围

首先，了解技能应该做什么：

1. **提出澄清问题**：
   - 这个技能应该提供什么具体功能？
   - Claude 何时应该使用这个技能？
   - 它需要哪些工具或资源？
   - 这是用于个人使用还是团队共享？

2. **保持专注**：一个技能 = 一个功能
   - 好："PDF 表单填写"、"Excel 数据分析"
   - 太宽泛："文档处理"、"数据工具"

### 第 2 步：选择技能位置

确定在哪里创建技能：

**个人技能** (`~/.claude/skills/`)：
- 个人工作流程和偏好
- 实验性技能
- 个人生产力工具

**项目技能** (`.claude/skills/`)：
- 团队工作流程和规范
- 项目特定专业知识
- 共享工具（提交到 git）

### 第 3 步：创建技能结构

创建目录和文件：

```bash
# 个人
mkdir -p ~/.claude/skills/skill-name

# 项目
mkdir -p .claude/skills/skill-name
```

对于多文件技能：
```
skill-name/
├── SKILL.md (必需)
├── reference.md (可选)
├── examples.md (可选)
├── scripts/
│   └── helper.py (可选)
└── templates/
    └── template.txt (可选)
```

### 第 4 步：编写 SKILL.md frontmatter

创建带有必需字段的 YAML frontmatter：

```yaml
---
name: skill-name
description: 简要描述这个技能的作用和何时使用
---
```

**字段要求**：

- **name**：
  - 仅限小写字母、数字、连字符
  - 最大 64 个字符
  - 必须与目录名称匹配
  - 好：`pdf-processor`，`git-commit-helper`
  - 不好：`PDF_Processor`，`Git Commits!`

- **description**：
  - 最大 1024 个字符
  - 包含 BOTH 它做什么 AND 何时使用
  - 使用用户会说的具体触发词
  - 提及文件类型、操作和上下文

**可选 frontmatter 字段**：

- **allowed-tools**：限制工具访问（逗号分隔列表）
  ```yaml
  allowed-tools: Read, Grep, Glob
  ```
  用于：
  - 只读技能
  - 安全敏感的工作流程
  - 范围有限的操作

### 第 5 步：编写有效的描述

描述对 Claude 发现你的技能至关重要。

**公式**：`[它做什么] + [何时使用它] + [关键触发词]`

**示例**：

✅ **好**：
```yaml
description: 从 PDF 文件中提取文本和表格，填写表单，合并文档。当处理 PDF 文件或用户提到 PDF、表单或文档提取时使用。
```

✅ **好**：
```yaml
description: 分析 Excel 电子表格，创建数据透视表，生成图表。当处理 Excel 文件、电子表格或分析 .xlsx 格式的表格数据时使用。
```

❌ **太模糊**：
```yaml
description: 帮助处理文档
description: 用于数据分析
```

**技巧**：
- 包含具体文件扩展名（.pdf，.xlsx，.json）
- 提及常用用户短语（"analyze"，"extract"，"generate"）
- 列出具体操作（而不是通用动词）
- 添加上下文线索（"Use when..."，"For..."）

### 第 6 步：组织技能内容

使用清晰的 Markdown 部分：

```markdown
# 技能名称

简要概述这个技能的作用。

## 快速入门

提供简单的示例，立即开始。

## 指令

为 Claude 提供分步指导：
1. 第一步，清晰的行动
2. 第二步，预期的结果
3. 处理边缘情况

## 示例

展示具体的代码或命令使用示例。

## 最佳实践

- 要遵循的关键规范
- 要避免的常见陷阱
- 何时使用与不使用

## 要求

列出任何依赖项或先决条件：
```bash
pip install package-name
```

## 高级用法

对于复杂场景，请参阅 [reference.md](reference.md)。

### 第 7 步：添加辅助文件（可选）

创建附加文件以进行渐进式披露：

**reference.md**：详细的 API 文档、高级选项
**examples.md**：扩展示例和使用案例
**scripts/**：辅助脚本和工具
**templates/**：文件模板或样板

从 SKILL.md 引用它们：
```markdown
对于高级用法，请参阅 [reference.md](reference.md)。

运行辅助脚本：
\`\`\`bash
python scripts/helper.py input.txt
\`\`\`
```

### 第 8 步：验证技能

检查这些要求：

✅ **文件结构**：
- [ ] SKILL.md 存在于正确位置
- [ ] 目录名称与 frontmatter `name` 匹配

✅ **YAML frontmatter**：
- [ ] 行 1 开头为 `---`
- [ ] 内容之前关闭 `---`
- [ ] 有效的 YAML（无制表符，正确的缩进）
- [ ] `name` 遵循命名规则
- [ ] `description` 是具体的且 < 1024 个字符

✅ **内容质量**：
- [ ] 为 Claude 提供清晰的指令
- [ ] 提供具体的示例
- [ ] 处理边缘情况
- [ ] 列出依赖项（如有）

✅ **测试**：
- [ ] 描述与用户问题匹配
- [ ] 技能在相关查询时自动激活
- [ ] 指令清晰且可执行

### 第 9 步：测试技能

1. **重启 Claude Code**（如果正在运行）以加载技能

2. **提出相关问题**，与描述匹配：
   ```
   你能帮我从 PDF 中提取文本吗？
   ```

3. **验证激活**：Claude 应该自动使用技能

4. **检查行为**：确认 Claude 正确遵循指令

### 第 10 步：如有需要，调试

如果 Claude 没有使用技能：

1. **使描述更具体**：
   - 添加触发词
   - 包含文件类型
   - 提及常用用户短语

2. **检查文件位置**：
   ```bash
   ls ~/.claude/skills/skill-name/SKILL.md
   ls .claude/skills/skill-name/SKILL.md
   ```

3. **验证 YAML**：
   ```bash
   cat SKILL.md | head -n 10
   ```

4. **运行调试模式**：
   ```bash
   claude --debug
   ```

## 常见模式

### 只读技能

```yaml
---
name: code-reader
description: 读取和分析代码而不进行更改。用于代码审查、理解代码库或文档。
allowed-tools: Read, Grep, Glob
---
```

### 基于脚本的技能

```yaml
---
name: data-processor
description: 使用 Python 脚本处理 CSV 和 JSON 数据文件。当分析数据文件或转换数据集时使用。
---

# 数据处理器

## 指令

1. 使用处理脚本：
\`\`\`bash
python scripts/process.py input.csv --output results.json
\`\`\`

2. 使用以下命令验证输出：
\`\`\`bash
python scripts/validate.py results.json
\`\`\`
```

### 多文件技能，渐进式披露

```yaml
---
name: api-designer
description: 遵循最佳实践设计 REST API。当创建 API 端点、设计路由或规划 API 架构时使用。
---

# API 设计器

快速入门：参见 [examples.md](examples.md)

详细参考：参见 [reference.md](reference.md)

## 指令

1. 收集需求
2. 设计端点（参见 examples.md）
3. 使用 OpenAPI 规范进行文档化
4. 对照最佳实践进行审查（参见 reference.md）
```

## 技能作者的最佳实践

1. **一个技能，一个目的**：不要创建巨型技能
2. **具体描述**：包含用户会说的触发词
3. **清晰指令**：为 Claude 而不是人类编写
4. **具体示例**：展示真实代码，而不是伪代码
5. **列出依赖项**：在描述中提及所需包
6. **与队友测试**：验证激活和清晰度
7. **版本控制技能**：在内容中记录更改
8. **使用渐进式披露**：将高级细节放在单独的文件中

## 验证清单

在最终确定技能之前，请验证：

- [ ] 名称是小写、仅连字符、最大 64 个字符
- [ ] 描述是具体的且 < 1024 个字符
- [ ] 描述包含 "什么" 和 "何时"
- [ ] YAML frontmatter 是有效的
- [ ] 指令是分步的
- [ ] 示例是具体且现实的
- [ ] 依赖项已记录
- [ ] 文件路径使用正斜杠
- [ ] 技能在相关查询时激活
- [ ] Claude 正确遵循指令

## 排错

**技能未激活**：
- 使描述更具体，添加触发词
- 在描述中包含文件类型和操作
- 添加 "Use when..." 子句，包含用户短语

**多个技能冲突**：
- 使描述更独特
- 使用不同的触发词
- 缩小每个技能的范围

**技能有错误**：
- 检查 YAML 语法（无制表符，正确缩进）
- 验证文件路径（使用正斜杠）
- 确保脚本具有执行权限
- 列出所有依赖项

## 示例

参见文档以获取完整示例：
- 简单的单文件技能（commit-helper）
- 具有工具权限的技能（code-reviewer）
- 多文件技能（pdf-processing）

## 输出格式

创建技能时，我将：

1. 提出关于范围和要求的澄清问题
2. 建议技能名称和位置
3. 创建带有正确 frontmatter 的 SKILL.md 文件
4. 包含清晰的指令和示例
5. 如有必要，添加辅助文件
6. 提供测试说明
7. 验证所有要求

结果将是一个完整的、可工作的技能，遵循所有最佳实践和验证规则。
