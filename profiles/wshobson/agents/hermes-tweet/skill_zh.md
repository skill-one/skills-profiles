# Hermes Tweet

Hermes Tweet 为 Hermes Agent 添加了 X/Twitter 工具集。它适用于社交聆听、账号研究、发布监控、支持分派、抽奖审核以及需要控制流程的工作流，其中私密操作或状态变更操作保持明确。

## 何时使用此技能

当用户需要执行以下操作时，请使用此技能：

- 将 Hermes Tweet 安装到 Hermes Agent 运行时
- 发现可用的 X/Twitter 读取和操作路由
- 读取 X/Twitter 账号、推文、趋势、监控或搜索数据
- 在起草回复或活动前总结公开信号
- 将私密操作和状态变更操作限制在明确的操作员意图之后

## 安装

通过 Hermes 安装并启用插件：

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

Hermes 在安装和更新插件时会扫描插件。请检查每个警告。
危险的判断会阻止安装或禁用更新。

在 Hermes 运行时主机上设置 API 密钥：

```bash
export XQUIK_API_KEY="<your-key>"
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

对于以读取为主的会话，请保持 `HERMES_TWEET_ENABLE_ACTIONS` 为 `false`。仅当获得批准的私密读取、写入、监控、webhook、提取、绘制或媒体操作时，将其设置为 `true`。

## 输入

在选择路由前，请询问以下输入：

- 目标：研究、监控、支持分派、抽奖审核或操作准备
- 目标：账号标识符、推文 URL、关键词、列表、监控或趋势
- 时间窗口和新鲜度需求
- 是否包含任何私密或状态变更操作
- 确认 Hermes 运行时具有 `XQUIK_API_KEY`

## 工作流

1. 使用 `tweet_explore` 搜索捆绑的端点目录，以找到匹配的路由。
2. 选择目录路由后，通过 `tweet_read` 读取公开的 X/Twitter 数据。
3. 仅在明确批准后，使用 `tweet_action` 执行私密或状态变更路由。
4. 将 API 密钥保存在环境变量或 Hermes 运行时环境文件中。
5. 不要将凭证粘贴到提示、问题、PR 评论或工具输入中。
6. 当用户需要活动、监控、支持或抽奖工作流，而不是单个读取时，加载 [工作流模式](references/workflows.md)。

## 工具模型

| 工具 | 目的 |
| --- | --- |
| `tweet_explore` | 不使用 API 密钥搜索捆绑的端点目录。 |
| `tweet_read` | 当 `XQUIK_API_KEY` 设置时，调用目录列出的公开只读端点。 |
| `tweet_action` | 仅在启用操作门禁时，调用私密读取、写入、监控、webhook、提取、绘制和媒体操作。 |

## 输出格式

返回简洁的操作输出：

```text
摘要：
- 检查了什么以及原因

读取路由：
- 目录路径、输入和结果摘要

操作计划：
- 提议的私密或状态变更操作，每个操作都需要明确批准

下一步检查：
- 当有用时的后续路由或监控频率
```

## 使用示例

在起草回复前研究账号：

```text
使用 Hermes Tweet 检查 @example 的最新公开上下文，然后再起草回复。
保持操作禁用。
```

监控发布关键词：

```text
跟踪今天 X/Twitter 中关于 "Example Launch" 的提及。
总结主题和值得注意的账号。不要发布。
```

准备受保护的发布：

```text
起草发布推文，并列出您将使用的确切 `tweet_action` 调用。
在执行任何操作路由前等待批准。
```

捕获结构化路由笔记：

```json
{
  "objective": "support-triage",
  "route": "/api/v1/x/search",
  "action_gate": "disabled",
  "approval_required": true
}
```

## 故障排除

- 如果仅出现 `tweet_explore`，请在 Hermes 运行时主机上配置 `XQUIK_API_KEY` 并重新加载或重启活动 Hermes 会话。
- 如果操作路由不可用，请将公开读取与操作分开。仅当获得批准的私密或状态变更操作时，设置 `HERMES_TWEET_ENABLE_ACTIONS=true`。
- 如果路由不匹配，请再次使用 `tweet_explore` 并选择目录列出的路径，而不是猜测端点。

## 最佳实践

- 将 Hermes Tweet 视为 Hermes 原生的 X/Twitter 层，而不是通用的 API 封装。
- 默认情况下将研究设置为只读。在创建或更改监控前需要批准。
- 在执行私密或状态变更调用前，使用桌面或网关操作员进行审查。
- 在调用 `tweet_read` 或 `tweet_action` 前验证确切的目录路径。
- 在环境变更后重启网关、cron 或长时间运行的 Hermes 会话。

## 参考文档

社交发布插件与 Hermes Tweet 配合使用，适用于跨平台广泛发布。Hermes Tweet 专注于 Hermes Agent 的 X/Twitter 工具集及其以读取为主、需要批准的操作模型。

当路由边界不明确时，请参阅 [端点和批准合同](references/endpoint-contract.md)。有关官方指南，请参阅 https://github.com/Xquik-dev/hermes-tweet#readme。
