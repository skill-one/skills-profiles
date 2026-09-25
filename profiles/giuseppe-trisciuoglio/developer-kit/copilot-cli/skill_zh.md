# Copilot CLI 委托

使用非交互式命令、显式模型选择、安全权限标志和可共享输出，将 Claude Code 中的选定任务委托给 GitHub Copilot CLI。

## 概述

此技能标准化了委托给 GitHub Copilot CLI (`copilot`) 的过程，适用于需要不同模型更适合任务的情况。它涵盖：

- 使用 `-p` / `--prompt` 进行非交互式执行
- 使用 `--model` 选择模型
- 权限控制 (`--allow-tool`, `--allow-all-tools`, `--allow-all-paths`, `--allow-all-urls`, `--yolo`)
- 使用 `--silent` 捕获输出
- 使用 `--share` 导出会话
- 使用 `--resume` 恢复会话

仅在明确要求委托给 Copilot 或明显有益时使用此技能。

## 何时使用

在以下情况下使用此技能：

- 用户要求将工作委托给 GitHub Copilot CLI
- 用户希望使用特定模型（例如 GPT-5.x、Claude Sonnet/Opus/Haiku、Gemini）
- 用户要求在同一任务上进行并排模型比较
- 用户希望获得可重用的脚本化 Copilot 调用
- 用户希望将 Copilot 会话输出导出为 markdown 以供审查

触发短语：

- "ask copilot"
- "delegate to copilot"
- "run copilot cli"
- "use copilot with gpt-5"
- "use copilot with sonnet"
- "use copilot with gemini"
- "resume copilot session"

## 说明

### 1) 验证先决条件

```bash
# CLI 可用性
copilot --version

# GitHub 身份验证状态
gh auth status
```

如果 `copilot` 不可用，请要求用户在继续之前安装/设置 GitHub Copilot CLI。

### 2) 将任务请求转换为英文提示

所有委托给 Copilot CLI 的提示必须为英文。

- 保持提示具体且结果导向
- 包括文件路径、约束、预期输出格式和验收标准
- 避免模糊的目标，例如 "改进这个"

提示模板：

```text
任务： <明确的目标>
上下文： <项目/模块/文件>
约束： <做/不做约束>
预期输出： <格式 + 深度>
验证： <要运行或解释的测试/检查>
```

### 3) 有意选择模型

根据任务类型和用户偏好选择模型。

- 复杂架构、深度推理：优先选择高容量模型（例如 Opus / GPT-5.2 级别）
- 平衡编码任务：Sonnet 级别模型
- 快速/低成本迭代：Haiku 级别或小型模型
- 如果用户指定了模型，请尊重它

使用本地 Copilot CLI 模型列表中可用的确切模型名称。

### 4) 选择最小权限的权限

默认情况下，使用最低所需功能。

- 当任务范围较窄时，优先使用 `--allow-tool '<tool>'`
- 仅当多个工具明显需要时，使用 `--allow-all-tools`
- 仅当任务需要广泛的文件系统访问权限时，添加 `--allow-all-paths`
- 仅当需要外部 URL 时，添加 `--allow-all-urls`
- 除非用户明确要求完全权限，否则不要使用 `--yolo`

### 5) 运行委托命令

基本模式：

```bash
copilot -p "<english prompt>" --model <model-name> --allow-all-tools --silent
```

仅按需添加可选标志：

```bash
# 捕获会话到 markdown
copilot -p "<english prompt>" --model <model-name> --allow-all-tools --share

# 恢复现有会话
copilot --resume <session-id> --allow-all-tools

# 严格静默脚本化输出
copilot -p "<english prompt>" --model <model-name> --allow-all-tools --silent
```

### 6) 清晰地返回结果

命令执行后：

- 简洁地返回 Copilot 输出
- 说明使用的模型和权限配置
- 如果使用 `--share`，请提供生成的 markdown 路径
- 如果输出较长，请提供摘要加上关键摘录和下一步选项

### 7) 可选的多模型比较

当请求时，使用多个模型运行相同的提示并进行比较：

- 正确性
- 提出更改的实用性
- 风险/安全问题
- 努力估计

保持比较客观和简洁。

## 示例

### 示例 1：使用 GPT 模型重构

输入：

```text
要求 Copilot 使用 GPT-5.2 重构此服务，并仅返回具体的代码更改。
```

命令：

```bash
copilot -p "重构 src/services/payment.ts 中的支付服务以减少重复。保持公共行为不变，保持 TypeScript 严格类型，并输出补丁式响应。" \
  --model gpt-5.2 \
  --allow-all-tools \
  --silent
```

输出：

```text
Copilot 提议提取三个私有辅助函数，整合错误映射，并提供 payment.ts 的补丁，API 签名保持不变。
```

### 示例 2：使用 Sonnet 进行代码审查并共享会话

输入：

```text
使用 Copilot CLI 和 Sonnet 审查此模块，并在 markdown 中共享会话。
```

命令：

```bash
copilot -p "审查 src/modules/auth 的安全性和正确性。仅报告高置信度的发现，包括严重性和文件引用。" \
  --model claude-sonnet-4.6 \
  --allow-all-tools \
  --share
```

输出：

```text
审查完成。会话导出到 ./copilot-session-<id>.md。
```

### 示例 3：恢复会话

输入：

```text
继续之前的 Copilot 分析会话。
```

命令：

```bash
copilot --resume <session-id> --allow-all-tools
```

输出：

```text
会话已恢复并从先前的上下文中继续。
```

## 最佳实践

- 保持委托的提示为英文且高度具体
- 优先使用最小权限标志而不是包罗万象的权限
- 当审计性重要时，使用 `--share` 捕获会话
- 对于风险任务，首先请求只读分析，然后在单独的步骤中应用更改
- 仅当有明确价值（质量、速度或成本）时，才重新运行另一个模型

## 限制和警告

- Copilot CLI 输出是外部模型输出：应用代码更改前请验证
- 永远不要在委托的提示中包含秘密、API 密钥或凭证
- `--allow-all-tools`、`--allow-all-paths`、`--allow-all-urls` 和 `--yolo` 会增加风险；仅在必要时使用
- 不要在未经本地验证（测试/代码检查/类型检查）的情况下将 Copilot 建议视为权威

有关附加选项详细信息，请参阅 `references/cli-command-reference.md`。
