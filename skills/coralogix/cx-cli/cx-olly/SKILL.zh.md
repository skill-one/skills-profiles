---
name: cx-olly
description: 当用户要求“与AI聊天”、“询问Olly”、“询问代理”、“向AI发送消息”、“继续聊天”、“跟进聊天”、“获取工件”、“下载工件”、“列出工件”、“检索生成内容”、“AI生成的图表”、“AI分析”、“对话可观察性”、“自然语言查询”，或使用cx CLI与Coralogix可观察性代理（Olly）交互时，应使用此技能。
---

# Olly 可观察性代理技能

使用此技能通过 `cx olly` CLI 命令与 Coralogix 的可观察性代理（Olly）进行交互。Olly 可以分析您的可观察性数据，回答有关告警、指标、日志的问题，并生成图表和报告等工件。

`cx olly ask` 默认 `--agent-to-agent-mode` 为 **false**。**如果您是 LLM/代理，请传递 `--agent-to-agent-mode`** - 详见下文“代理间模式”。

## CLI 命令

| 命令 | 目的 | 关键标志 |
|---|---|---|
| `cx olly ask "消息"` | 向可观察性代理发送消息 | `--chat-id`, `--model`, `--timeout`, `--agent-to-agent-mode` |
| `cx olly artifacts list` | 列出所有生成的工件 | - |
| `cx olly artifacts get <id>` | 通过 ID 获取工件内容 | - |

**输出格式：** 添加 `-o json` 或 `-o toon` 以获取机器可读输出。

**仅单配置：** `cx olly` 命令不支持多配置分叉。使用 `-p <配置>` 指定单个配置。

## 运行 Olly（默认异步）

**默认以异步方式运行 `cx olly ask`：** 启动它作为 **后台进程并轮询其完成**，而不是阻塞它。Olly 的调查通常需要几分钟，因此这是 `cx olly ask` 的正常模式。

仅以行内（前台、阻塞）方式运行 `cx olly ask`，用于您期望 Olly 快速回答的简短问题——快速查找或单行后续问题。如有疑问，请在后台运行。

## 聊天命令

### 开始新的对话

```bash
cx olly ask "今天触发了哪些告警？" --agent-to-agent-mode
```

这将创建一个新的聊天，并返回一个 **聊天 ID**，您可以使用它进行后续问题。
如果您没有要共享的上下文（例如快速访问源文件）或创建的聊天仅用于人类使用，请移除 `--agent-to-agent-mode`。

### 继续现有聊天

```bash
cx olly ask "告诉我更多关于错误率的信息" --chat-id <聊天-id> --agent-to-agent-mode
```

使用 `--chat-id` 以继续对话并保持先前消息的上下文。当启动另一个调查时，也将后续问题置于后台。

### 模型选择

可用模型包括 `gpt-5.2`（默认）、`claude-sonnet-4-5`、`sonnet-4.6`、`gpt-5.4`、`claude-haiku-4-5`。

```bash
cx olly ask "解释这个错误" --model claude-sonnet-4-5 --agent-to-agent-mode
```

### 超时

对于可能需要更长时间的复杂查询，增加 Olly 的响应超时
（默认：900 秒）：

```bash
cx olly ask "深入分析上周的事件" --timeout 1800 --agent-to-agent-mode
```

`--http-timeout <秒>`（或 `CX_HTTP_TIMEOUT`）为所有 CLI 命令（包括 Olly）设置 HTTP 请求截止日期。它与 Olly 的响应超时是分开的。

### 代理间模式

`--agent-to-agent-mode` 默认为 `false`，因为 `cx olly ask` 既被人类直接使用，也被代理使用。**如果您是 LLM/代理，请传递 `--agent-to-agent-mode`** 以选择更短的、子代理风格的响应：不生成图表/表格，用澄清问题代替猜测，并依赖您的更广泛的上下文。

```bash
cx olly ask "分析一下这个" --agent-to-agent-mode
```

**它是按调用而不是按聊天设置的。** `--chat-id` 不会记住它 - 在每个后续回合中重新传递 `--agent-to-agent-mode`，或者模式在对话中后期无声地切换回面向人类。

## 工件

Olly 可以生成查询结果、预览和引用等工件。工件 ID 出现在代理的响应文本中的链接中。

### 列出所有工件

```bash
cx olly artifacts list
cx olly artifacts list -o json
```

### 获取工件内容

```bash
cx olly artifacts get <工件-id>
cx olly artifacts get <工件-id> -o json
```

`artifacts get` 命令自动：
1. 获取工件元数据
2. 从预签名 URL 下载内容
3. **解压缩 gzip** 内容
4. **解析 JSON** 并对大内容使用 spill 逻辑
5. 将非 JSON 文本保存到临时文件

输出行为：
- **JSON 内容**：直接显示，或如果内容较大则保存到文件
- **文本内容**：保存到临时文件（例如 `/tmp/cx_results_artifact_<id>_<hash>.txt`）

## 工作流示例

### 调查问题

```bash
# 开始调查——在后台运行并轮询完成
cx olly ask "为什么结账服务显示高延迟？检查包含 'checkout:' 字符串的日志和 aws 相关指标" --agent-to-agent-mode

# 使用响应中的聊天 ID 进行后续——也置于后台并轮询
cx olly ask "过去一小时发生了什么变化？" --chat-id abc-123-def --agent-to-agent-mode

# 交互完成后，获取任何生成的图表
cx olly artifacts list -o json | jq '.[0].id'
cx olly artifacts get <工件-id>
```

### 获取 JSON 输出用于脚本

```bash
# 获取 JSON 格式的响应
cx olly ask "列出前 5 个错误消息" -o json --agent-to-agent-mode | jq '.response'

# 解析工件
cx olly artifacts list -o json | jq '.[] | {id, filename, created_at}'
```

### 使用特定模型进行详细分析

```bash
cx olly ask "对 2024-01-15 的停机事件进行根本原因分析" \
  --model claude-sonnet-4-5 \
  --timeout 1800 \
  --agent-to-agent-mode
```

## 关键原则

- **默认异步** - 将 `cx olly ask` 作为后台进程运行并轮询其完成；仅对您期望 Olly 快速回答的简短问题以行内（阻塞）方式运行
- **聊天 ID 启用上下文** - 从响应中保存聊天 ID 以继续对话
- **使用 `-o json` 用于脚本** - 管道到 `jq` 以进行过滤和提取
- **工件 ID 出现在响应文本中** - 查找类似 `[图表](https://...artifact_view/<id>)` 的 Markdown 链接
- **仅单配置** - `cx olly` 不支持多配置查询
- **大工件自动溢出** - 超过配置限制的 JSON 内容保存到临时文件
- **在提问前检查源代码** - 如果有，在调用它之前向 Olly 提供来自源代码的具体上下文，例如从哪个指标开始调查
- **限制调查范围** - 指导 Olly 到正确的有限范围，例如仅限于日志或特定时间范围
- **作为 LLM/代理调用时传递 `--agent-to-agent-mode`** - 它默认为 `false`（面向人类）；代理应选择更短的、子代理风格的响应

## 相关技能

- **`cx-telemetry-querying`** - 用于无需 AI 代理协助的直接 DataPrime/PromQL 查询（涵盖日志、跨度、指标、RUM）
- **`cx-alerts`** - 用于管理告警定义
