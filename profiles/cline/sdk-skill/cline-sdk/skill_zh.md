# Cline SDK 技能

Cline SDK 用于构建 AI 代理的集成技能。使用下面的决策树找到合适的入口点和 API 表面，然后加载详细参考。

## 关键规则

在所有 Cline SDK 代码中遵循以下规则：

1. 使用 `npm install @cline/sdk` 安装。`@cline/sdk` 包重新导出 `@cline/core`，而不是直接重新导出每个子包。核心重新导出公共 SDK 表面，例如 `ClineCore`、`Agent`、`createAgentRuntime`、`createTool`、内置工具助手、提供者助手以及 `Llms` 命名空间。仅在您需要核心未重新导出的 API 时，才从 `@cline/agents`、`@cline/llms` 或 `@cline/shared` 导入，例如 `AgentRuntime`、`createAgent` 或某些低级类型。
2. 需要 Node.js 22 或更高版本。
3. 使用 `@cline/sdk`（或 `@cline/shared`）中的 `createTool()` 定义工具。工具名称必须为 `snake_case`。
4. 当代理可以恢复时，优先从工具 `execute` 函数返回结构化错误数据。直接 `Agent` 将抛出的工具错误转换为错误工具结果；ClineCore 也可以计算重复失败的工具回合数，用于其错误限制处理。
5. 对于应结束代理循环的工具（例如“提交答案”工具），使用 `lifecycle: { completesRun: true }`。
6. 使用 `ClineCore` 时，完成操作后始终调用 `dispose()` 以清理资源。
7. 直接 `Agent` 和 `ClineCore` 具有不同的事件系统。对于 `Agent`：使用 `agent.subscribe()` 获取 `AgentRuntimeEvent` 类型，文本流是 `"assistant-text-delta"`，结果文本是 `result.outputText`。对于 `ClineCore`：使用 `cline.subscribe()` 获取 `CoreSessionEvent` 类型。从 `"agent_event"` 有效负载（`content_start`、`content_update`、`content_end`、`done`）中渲染面向用户文本、推理和工具活动。将 `"chunk"` 事件视为原始传输块 `{ stream, chunk, ts }`，而不是类型化的文本增量。`ClineCore` 结果文本是 `result.text`。`AgentRuntimeConfig` 没有顶层的 `onEvent` 字段；使用 `agent.subscribe()` 或 `hooks.onEvent`。不要使用 `"content_update"` 或 `"content_start"` 与 `agent.subscribe()`；这些是宿主面的 `AgentEvent` 类型，包含在 ClineCore `agent_event` 事件内部。
8. 对于直接 `Agent`，`plugins` 是简单的运行时插件，`setup(context)` 返回 `{ tools, hooks }`。对于 `ClineCore`，`extensions` 是 `AgentPlugin` 对象，具有 `manifest`、`setup(api, ctx)` 和可选的 `hooks`。不要在直接 `Agent.plugins` 中使用 ClineCore 插件示例。
9. 插件技能是 **基于文件** 的，不是注册的。没有 `registerSkill()` 和 `api.registerSkill`。插件将技能作为 `SKILL.md` 文件打包在 `<package>/skills/<name>/SKILL.md`（需要包结构）；宿主自动发现它们并作为 `/slash-commands` 显示——不要调用 `registerCommand` 用于技能。插件 MCP 服务器使用 `api.registerMcpServer()` 并带有 `"mcp"` 功能。配置的代理（代理配置文件）是 `.cline/agents/` 中的 YAML 文件，当 `enableSpawnAgent` 为 true 时，作为 `subagent_<name>` 工具加载。

## 如何使用此技能

### 参考文件结构

两个主要 API 表面（`Agent` 和 `ClineCore`）遵循 4 文件模式。跨领域概念是单文件指南。

`./references/<api>/` 中的每个主要 API 表面包含：

| 文件 | 目的 | 何时阅读 |
|------|---------|--------------|
| `REFERENCE.md` | 概述、何时使用、快速入门 | 首先总是阅读 |
| `api.md` | 完整 API：类、方法、配置、类型 | 编写代码 |
| `patterns.md` | 常见模式、最佳实践 | 实现指导 |
| `gotchas.md` | 陷阱、限制、调试 | 故障排除 |

`./references/<concept>/` 中的跨领域概念以 `REFERENCE.md` 作为入口点。

### 阅读顺序

1. 从您选择的 API 表面的 `REFERENCE.md` 开始
2. 然后阅读与您的任务相关的附加文件：
   - 编写代理代码 -> `api.md`
   - 常见模式 -> `patterns.md`
   - 创建工具 -> `tools/REFERENCE.md`
   - 添加插件/钩子 -> `plugins/REFERENCE.md`
   - 配置 LLM 提供者 -> `providers/REFERENCE.md`
   - 流式传输事件 -> `events/REFERENCE.md`
   - 部署到生产环境 -> `production/REFERENCE.md`
   - 调度代理 -> `scheduling/REFERENCE.md`
   - 多代理编排 -> `multi-agent/REFERENCE.md`
   - 调试 -> `gotchas.md`

### 示例路径

```
./references/agent/REFERENCE.md           # 轻量级代理从这里开始
./references/clinecore/REFERENCE.md       # 全功能运行时从这里开始
./references/agent/api.md                 # Agent 类、配置、方法
./references/tools/REFERENCE.md           # 创建和使用工具
./references/plugins/REFERENCE.md         # 插件系统
./references/providers/REFERENCE.md       # LLM 提供者配置
```

## 快速决策树

### “我应该使用哪个 API 表面？”

```
选择哪个 API？
+-- 我需要一个简单的、内存中的代理，带有自定义工具
|   +-- agent/ (来自 @cline/agents 的 Agent 类，由 @cline/sdk 重新导出)
+-- 我需要会话持久化、内置工具、配置发现
|   +-- clinecore/ (来自 @cline/core 的 ClineCore)
+-- 我需要内置的文件/Shell/搜索/网络工具
|   +-- clinecore/ (具有内置工具；Agent 没有)
+-- 我需要计划或定期执行的代理
|   +-- clinecore/ (自动化 API)
+-- 我需要多进程或多客户端会话共享
|   +-- clinecore/ (中心化运行时)
+-- 我正在构建一个浏览器兼容的代理
|   +-- agent/ (无 Node.js 依赖)
```

### “我需要创建工具”

```
工具？
+-- 使用模式定义自定义工具 -> tools/REFERENCE.md
+-- 使用内置工具（read_files、search_codebase、run_commands 等）-> tools/REFERENCE.md (内置部分)
+-- 控制工具审批/策略 -> tools/REFERENCE.md (策略部分)
+-- 结束代理循环的工具 -> tools/REFERENCE.md (完成工具)
+-- 将工具打包为可重用的插件 -> plugins/REFERENCE.md
```

### “我需要处理事件”

```
事件？
+-- 实时流式传输文本/推理 -> events/REFERENCE.md
+-- 跟踪令牌使用和成本 -> events/REFERENCE.md
+-- 监控工具调用 -> events/REFERENCE.md
+-- 检测完成/错误 -> events/REFERENCE.md
+-- 钩入生命周期阶段 -> plugins/REFERENCE.md
```

### “我需要配置模型提供者”

```
提供者？
+-- Anthropic (Claude) -> providers/REFERENCE.md
+-- OpenAI (GPT) -> providers/REFERENCE.md
+-- Google (Gemini/Vertex) -> providers/REFERENCE.md
+-- AWS Bedrock -> providers/REFERENCE.md
+-- Mistral -> providers/REFERENCE.md
+-- OpenAI 兼容 (vLLM、Together 等) -> providers/REFERENCE.md
+-- 自定义/自托管提供者 -> providers/REFERENCE.md
```

### “我需要插件或钩子”

```
插件？
+-- 将工具 + 钩子打包在一起 -> plugins/REFERENCE.md
+-- 观察工具调用（日志记录、指标）-> plugins/REFERENCE.md
+-- 截断生命周期事件 -> plugins/REFERENCE.md
+-- 添加系统提示规则 -> plugins/REFERENCE.md
+-- 暴露 MCP 服务器的工具 -> plugins/REFERENCE.md (MCP 服务器)
+-- 打包可重用的技能 (SKILL.md, 自动 slash 命令) -> plugins/REFERENCE.md (打包技能)
+-- 通过 npm/git 分发 -> plugins/REFERENCE.md
```

### “我需要多代理协调”

```
多代理？
+-- 运行一次性委托子代理 -> multi-agent/REFERENCE.md (子代理)
+-- 从文件中预定义的命名子代理 -> multi-agent/REFERENCE.md (配置的代理)
+-- 持久化跨会话团队 -> multi-agent/REFERENCE.md (团队)
+-- 父子委托 -> multi-agent/REFERENCE.md (子代理)
+-- 对等任务板 -> multi-agent/REFERENCE.md (团队)
```

### “我需要计划或自动化”

```
计划？
+-- 定期 cron 任务 -> scheduling/REFERENCE.md
+-- 一次性计划任务 -> scheduling/REFERENCE.md
+-- 事件驱动触发器 -> scheduling/REFERENCE.md
+-- CLI 计划管理 -> scheduling/REFERENCE.md
```

### “我需要部署到生产环境”

```
生产？
+-- 错误处理和状态检查 -> production/REFERENCE.md
+-- 成本控制和令牌限制 -> production/REFERENCE.md
+-- 可观察性 (OpenTelemetry) -> production/REFERENCE.md
+-- 安全和沙盒 -> production/REFERENCE.md
+-- 部署模式 -> production/REFERENCE.md
```

### 故障排除索引

- 代理循环未停止 -> `tools/REFERENCE.md` (完成工具)
- 工具错误导致代理崩溃 -> `agent/gotchas.md` 或 `clinecore/gotchas.md`
- 提供者认证失败 -> `providers/REFERENCE.md`
- 会话未持久化 -> `clinecore/gotchas.md`
- 令牌使用过高 -> `production/REFERENCE.md` (成本控制)
- 中心连接问题 -> `clinecore/gotchas.md`
- 插件未加载 -> `plugins/REFERENCE.md`
- 事件未触发 -> `events/REFERENCE.md`
```

## 产品索引

### API 表面
| API | 入口文件 | 描述 |
|-----|------------|-------------|
| Agent | `./references/agent/REFERENCE.md` | 轻量级内存代理循环 |
| ClineCore | `./references/clinecore/REFERENCE.md` | 具有会话、持久化、内置工具的完整运行时 |

### 跨领域概念
| 概念 | 入口文件 | 描述 |
|---------|------------|-------------|
| Tools | `./references/tools/REFERENCE.md` | 内置和自定义工具创建 |
| Plugins | `./references/plugins/REFERENCE.md` | 具有钩子、MCP 服务器和打包技能的扩展系统 |
| Events | `./references/events/REFERENCE.md` | 实时流式事件 |
| Providers | `./references/providers/REFERENCE.md` | LLM 提供者配置 |
| Production | `./references/production/REFERENCE.md` | 部署、安全、可观察性 |
| Scheduling | `./references/scheduling/REFERENCE.md` | Cron 任务和自动化 |
| Multi-Agent | `./references/multi-agent/REFERENCE.md` | 团队、子代理和配置的代理配置文件 |

### 包映射
| 包 | 目的 |
|---------|---------|
| `@cline/sdk` | 用户面别名，首先安装这个包 |
| `@cline/core` | 会话、持久化、内置工具、配置、中心、以及选择的重新导出 |
| `@cline/agents` | 浏览器兼容的 AgentRuntime 类和低级工厂 |
| `@cline/llms` | LLM 提供者网关 |
| `@cline/shared` | 类型、工具助手、钩子引擎 |

## 资源

仓库：https://github.com/cline/cline
SDK 源代码：https://github.com/cline/cline/tree/main/sdk
文档：https://docs.cline.bot/sdk/overview
Discord：https://discord.gg/cline
