---
name: iris-development
description: Iris 是 Redis 针对 AI 产品提供的集成解决方案。在将 Iris Redis Agent Memory (RAM) 数据平面与 Redis Cloud 集成时，可使用此技能来记录 AI 代理的会话事件、创建或搜索长期记忆、配置记忆存储或调整后台记忆提升。代码示例使用官方的 `redis-agent-memory` (Python) 和 `@redis-iris/agent-memory` (TypeScript) SDK。
---

# Iris：Redis 代理内存

**Iris** 是 Redis AI 相关产品的总品牌。此技能目前涵盖该系列中的一个产品：**Redis Agent Memory (RAM)** — AI 代理的持久化内存层，作为 Redis Cloud 上的托管服务提供。当其他 Iris 产品推出时，它们将作为单独的部分进行介绍。

Redis Agent Memory 提供了一个 REST/JSON 数据平面 API，具有两个内存层级：

- **会话内存** — 每个会话的仅追加式对话历史记录（工作内存）。
- **长期内存** — 从会话中提取的语义可搜索记录（或直接创建）。

一个后台的 **推广** 工作人员 — 由 Redis Cloud 管理 — 从会话事件中提取持久事实，并将它们写入长期内存。

## 官方 SDK

所有代码示例都使用官方 SDK：

| 语言     | 包名                    | 类         | 安装                          |
| -------- | ----------------------- | ---------- | ----------------------------- |
| Python   | `redis-agent-memory`    | `AgentMemory` | `pip install redis-agent-memory` |
| TypeScript | `@redis-iris/agent-memory` | `AgentMemory` | `npm add @redis-iris/agent-memory` |

这两个 SDK 都从 `AGENT_MEMORY_API_KEY` 读取访问令牌，并从 `AGENT_MEMORY_STORE_ID` 读取默认存储 ID。生产数据平面 URL 是 `https://gcp-us-east4.memory.redis.io`；在配置后，您的服务的确切 URL 也显示在云控制台中。

## 何时应用

参考这些指南：

- 在 Redis Cloud 上创建内存服务 ([https://cloud.redis.io/#/agent-memory](https://cloud.redis.io/#/agent-memory))
- 将代理连接到调用 `AgentMemory.add_session_event(...)` / `addSessionEvent(...)`
- 使用 `search_long_term_memory(...)` / `searchLongTermMemory(...)` 搜索长期内存
- 在会话事件和直接长期内存写入之间进行选择

## 按优先级分类的规则类别

| 优先级 | 类别                | 影响 | 前缀       |
| ------ | ----------------------- | ------ | ------------ |
| 1      | 设置和云服务   | 高   | `setup-`     |
| 2      | 会话内存 / 事件 | 高   | `session-`   |
| 3      | 长期内存        | 高   | `ltm-`       |
| 4      | 内存推广        | 中   | `promotion-` |

## 快速参考

### 1. 设置和云服务 (高)

- [`setup-cloud-service`](references/setup-cloud-service.md) - 在 Redis Cloud 上创建内存服务
- [`setup-auth-token`](references/setup-auth-token.md) - 使用存储 API 密钥对 SDK 进行身份验证

### 2. 会话内存 / 事件 (高)

- [`session-when-to-use`](references/session-when-to-use.md) - 选择会话事件与直接长期内存
- [`session-add-event`](references/session-add-event.md) - 正确追加会话事件
- [`session-retrieval`](references/session-retrieval.md) - 检索会话内存和单个事件

### 3. 长期内存 (高)

- [`ltm-bulk-create`](references/ltm-bulk-create.md) - 使用幂等 ID 批量创建长期记忆
- [`ltm-search`](references/ltm-search.md) - 使用过滤器对长期内存进行语义搜索
- [`ltm-organize`](references/ltm-organize.md) - 使用命名空间、ownerId、主题和memoryType组织记录

### 4. 内存推广 (中)

- [`promotion-overview`](references/promotion-overview.md) - 背景推广的工作原理

## 如何使用

在 `references/` 下阅读单个规则文件以获取详细说明和代码示例：

```
references/setup-cloud-service.md
references/session-add-event.md
references/promotion-overview.md
```

每个规则文件包含：

- 它为什么重要的简要说明
- 带有 Python 和 TypeScript SDK 代码的正确示例
- 要么一个“不正确”的示例，要么“何时使用 / 何时不需要”的指导
- 额外的上下文和参考
