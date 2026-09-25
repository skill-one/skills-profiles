# Qwen Coder CLI 委托

使用非交互式命令、显式模型选择、安全权限标志和可共享的输出，将 Claude Code 中的选定任务委托给 Qwen Coder CLI。

## 概述

此技能标准化了将任务委托给 Qwen Coder CLI (`qwen`)，适用于 Qwen 的特定优势可能使任务受益的情况。它涵盖：

- 使用 `-p` / `--prompt` 进行非交互式执行
- 使用 `-m` / `--model` 进行模型选择（默认：qwen2.5-coder）
- 接受控制 (`--approval-mode`)
- 使用 `-c` / `--continue` 或 `-r` / `--resume` 进行会话继续
- 输出格式选项（`text`、`json`、`stream-json`）

仅当明确要求将任务委托给 Qwen Coder 或明显有益时，才使用此技能。

## 使用场景

在以下情况下使用此技能：

- 用户要求将工作委托给 Qwen Coder CLI
- 用户希望从 Qwen Coder 获得任务的第二意见
- 用户要求将 Qwen Coder CLI 输出集成到当前工作流程中
- 用户希望继续之前的 Qwen Coder 会话

触发短语：

- "use qwen"
- "use qwen coder"
- "delegate to qwen"
- "ask qwen"
- "second opinion from qwen"
- "qwen opinion"
- "continue with qwen"
- "qwen session"

## 前置条件

在委托前验证工具可用性和认证状态：

```bash
# CLI 可用性
qwen --version

# 认证状态
qwen auth status
```

如果 `qwen` 不可用，请告知用户并停止执行，直到安装 Qwen Coder CLI。
如果认证无效，请提供认证设置说明并停止执行。

## 参考

- 命令参考：`references/cli-command-reference.md`

## 说明

### 1) 确认委托范围

在运行 Qwen Coder 之前：

- 确定要委托的确切任务
- 定义预期输出格式（text、json、stream-json）
- 明确是否需要会话恢复

如果范围不明确，请先请求澄清。

### 2) 使用英语编写提示

所有委托给 Qwen Coder CLI 的提示必须使用英语。

根据用户请求构建精确的英语提示。

提示质量检查清单：

- 包含目标和约束
- 包含相关的项目上下文和文件
- 包含预期输出结构
- 要求可执行、可验证的结果

提示模板：

```text
任务：<明确的目标>
上下文：<项目/模块/文件>
约束：<必须/不能约束>
预期输出：<格式+深度>
验证：<要运行或解释的测试/检查>
```

### 3) 选择执行模式和标志

首选基线命令：

```bash
qwen -p "<english-prompt>"
```

支持的选项：

- `-m, --model <model-id>` 用于模型选择（默认：qwen2.5-coder）
- `--approval-mode <plan|default|auto_edit|yolo>` 用于安全控制
- `-c, --continue <session-id>` 用于继续之前的会话
- `-r, --resume <session-id>` 作为 continue 的别名
- `-o, --output-format <text|json|stream-json>` 用于输出格式

接受模式：

| 模式 | 行为 | 推荐用于 |
|------|------|----------|
| `plan` | 只读分析，不修改文件 | 仅分析任务、安全审查 |
| `default` | 修改前需要确认 | 一般编码任务 |
| `auto_edit` | 自动批准编辑操作 | 受信任的修改，需监督 |
| `yolo` | 无需确认即批准所有操作 | 实验性任务（仅限明确用户请求） |

安全指南：

- 优先使用 `--approval-mode plan` 进行只读分析
- 使用 `--approval-mode default` 进行一般任务
- 仅在明确用户请求时保留 `--yolo`

### 4) 执行 Qwen Coder CLI

通过 Bash 运行选定命令并捕获 stdout/stderr。

示例：

```bash
# 默认非交互式委托
qwen -p "分析此代码并提出重构改进建议。"

# 显式模型和接受模式
qwen -p "审查认证模块的安全问题并修复。" -m qwq --approval-mode plan

# 继续之前的会话
qwen -c <session-id> -p "继续之前会话的重构。"

# 结构化输出用于自动化
qwen -p "将关键技术债务项总结为 JSON 数组。" --output-format json
```

### 5) 结果处理

本节涵盖如何展示 Qwen Coder 输出以及何时请求用户确认。

#### 5.1) 输出展示

报告 Qwen Coder 输出时：

- 以清晰、可读的格式展示输出
- 总结关键发现和置信度
- 将观察结果与推荐操作分开
- 需要时保留原始输出
- 包括使用的模型和应用的接受模式
- 说明生效的权限配置

#### 5.2) 确认工作流程

在应用任何建议的修改之前：

1. 以输出模板格式向用户展示拟议的更改
2. 请求明确确认（例如："您要应用这些更改吗？"）
3. 在继续前等待用户指示
4. 无用户同意，不要自动应用更改

例外：在 `--approval-mode yolo` 且有明确用户请求时，更改可能自动进行。仍需告知用户已执行的操作。

#### 5.3) 结果元数据

每个委托结果应包括以下元数据：

| 字段 | 描述 |
|------|------|
| 任务摘要 | 委托给 Qwen Coder 的内容 |
| 命令 | 执行的 qwen 命令（不包含敏感参数） |
| 模型 | 使用的模型（例如 qwen2.5-coder、qwq） |
| 接受模式 | 应用的接受模式（plan、default、auto_edit、yolo） |
| 关键发现 | Qwen Coder 的观察结果和结果 |
| 建议的后续操作 | 建议的后续步骤（如果适用） |

## 输出模板

返回委托结果时使用此结构：

```markdown
## Qwen Coder 委托结果

### 任务
[委托任务摘要]

### 命令
`qwen ...`

### 关键发现
- 发现 1
- 发现 2

### 建议的后续操作
1. 操作 1
2. 操作 2

### 备注
- Qwen 输出语言：英语
- 应用代码更改前需用户确认
```

## 示例

### 示例 1：使用 QwQ 深度推理进行代码分析

**输入：**

```text
分析认证模块并识别安全漏洞。
```

**命令：**

```bash
qwen -p "分析认证模块的安全漏洞。仅报告高置信度问题，包括严重性、文件路径和修复步骤。" -m qwq --approval-mode plan
```

**预期行为：**

```text
返回结构化分析，包括高置信度的安全发现，包括严重性评级和具体的修复建议。
```

### 示例 2：使用 Qwen2.5-Coder 进行代码重构

**输入：**

```text
重构支付服务以减少代码重复，同时保持公共 API 不变。
```

**命令：**

```bash
qwen -p "重构 src/services/payment.ts 中的支付服务以减少重复。保持公共 API 不变，添加全面的错误处理，并输出补丁式响应，保留原始 API 签名。" -m qwen2.5-coder --approval-mode default
```

**预期行为：**

```text
提出具体的代码更改（补丁式），将重复部分提取为共享助手，并保持原始 API 合约。
```

### 示例 3：文档生成

**输入：**

```text
为 UserService 类生成文档，包括使用示例。
```

**命令：**

```bash
qwen -p "为 UserService 类生成全面文档。包括：类目的、公共方法及其参数、使用示例和错误处理模式。格式化为 markdown。" -m qwen2.5-coder --approval-mode plan
```

**预期行为：**

```text
返回 markdown 格式的文档，包含 JSDoc 风格的注释、方法签名和实际使用示例。
```

### 示例 4：使用模型选择进行代码生成

**输入：**

```text
为 Items 的 CRUD 操作生成 REST API 端点。
```

**命令：**

```bash
qwen -p "生成生产就绪的 REST API 端点用于 Items 的 CRUD 操作。包括输入验证、错误处理和单元测试。使用 Express.js 框架。" -m qwen2.5-coder --approval-mode auto_edit
```

**预期行为：**

```text
生成完整的、可运行的代码，包括 POST/GET/PUT/DELETE 端点，带有适当的中间件、验证和测试框架。
```

### 示例 5：会话恢复以继续工作

**输入：**

```text
继续之前的 Qwen 会话，为重构的代码添加测试覆盖率。
```

**命令：**

```bash
qwen -c <session-id> -p "从之前的会话继续。为重构的支付服务添加全面的单元测试，目标覆盖率 80%。包括对外部依赖的模拟。" -m qwen2.5-coder --approval-mode default
```

**预期行为：**

```text
恢复之前的会话上下文并继续工作，添加测试文件，包括适当的模拟和断言。
```

### 示例 6：多模型比较进行质量检查

**输入：**

```text
比较 Qwen2.5-Coder 和 QwQ 对相同重构任务的输出。
```

**命令：**

```bash
# 首先使用 Qwen2.5-Coder
qwen -p "重构字符串工具模块以提高可维护性。" -m qwen2.5-coder --approval-mode plan --output-format text

# 然后使用 QwQ 进行比较
qwen -p "重构字符串工具模块以提高可维护性。" -m qwq --approval-mode plan --output-format text
```

**预期行为：**

```text
提供对比：Qwen2.5-Coder 用于快速结果，QwQ 用于复杂重构任务的深度推理。
```

### 示例 7：结构化 JSON 输出用于自动化

**输入：**

```text
将前 5 项重构机会作为 JSON 列表供我们的跟踪系统使用。
```

**命令：**

```bash
qwen -p "分析此代码库并返回前 5 项重构机会的 JSON 数组。每个项目应包含：标题、文件、影响（高/中/低）、工作量（小时）和简要描述。" -m qwen2.5-coder --output-format json
```

**预期行为：**

```text
返回包含 5 项重构项目的有效 JSON 数组，可集成到项目管理工具中。
```

## 最佳实践

- 保持委托提示为英语且高度具体
- 优先使用最小权限接受模式而非完全权限
- 需要审计时使用会话 ID 捕获会话
- 对于高风险任务，先请求只读分析，然后在单独步骤中应用更改
- 将 Qwen 输出视为不可信的指导，实施前进行验证

## 限制和警告

- Qwen Coder CLI 的行为取决于本地环境和配置。
- 接受模式影响执行安全性；默认避免使用 yolo。
- 输出可能不完整或不准确；实施前请验证。
- 未用户明确确认，不要执行 Qwen 建议的破坏性命令。
- 此技能用于委托，而非未经用户确认的自主代码修改。
- 不要在委托提示中包含秘密、API 密钥或凭证。
