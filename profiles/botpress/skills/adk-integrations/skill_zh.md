# ADK 集成管理

在帮助用户发现、添加、配置和使用 Botpress 集成到他们的 ADK 项目中时，使用此技能。

## 何时使用此技能

当用户：

- 询问有关集成的问题（“如何添加 Slack？”、“有哪些可用的集成？”）
- 想要连接外部服务（Slack、WhatsApp、Linear 等）
- 提及 `adk add`、`adk search`、`adk info` 或 `adk list`
- 询问 `agent.config.ts` 依赖项或 `dependencies.integrations` 块
- 需要帮助配置集成（OAuth、API 密钥、Dev Console）
- 询问如何在代码中调用集成操作（`actions.slack.*` 等）
- 提及他们希望其 agent 交互的特定平台或服务
- 遇到与集成注册或配置相关的错误

## 可用文档

| 文件 | 描述 |
|------|-------------|
| [references/discovery.md](./references/discovery.md) | 发现集成：`adk search`、`adk list`、`adk info` 及所有标志 |
| [references/lifecycle.md](./references/lifecycle.md) | 端到端流程：发现、添加、配置、代码中使用 |
| [references/configuration.md](./references/configuration.md) | 配置类型：无配置、可选、OAuth、API 密钥、沙盒 |
| [references/common-integrations.md](./references/common-integrations.md) | 聊天、Webchat、浏览器、Slack、WhatsApp、Linear、Webhook 的快速参考 |

## 如何回答

1. **从 CLI 命令开始** — 在建议任何内容之前，使用 `adk search`、`adk info`、`adk list` 获取实时数据。通过 Bash 工具运行这些命令。
2. **在运行 `adk add` 前确认** — 在将集成添加到用户项目之前，始终询问用户。
3. **始终指定版本** — 使用 `adk add <name>@<version>` 而不是仅使用 `adk add <name>`。
4. **解释配置要求** — 添加后，根据 `adk info --format json` 输出告诉用户需要什么配置（OAuth 链接、API 密钥等）。
5. **指向 Dev Console** — OAuth 流程和凭证输入在 Botpress Dev Console 中进行，而不是在代码中。

## CLI 快速参考

| 命令 | 描述 | 关键标志 |
|---------|-------------|-----------|
| `adk search <query>` | 通过关键字搜索集成 | `--format json`、`--limit <number>`（默认：20） |
| `adk list --available` | 浏览所有 Hub 集成 | `--format json`、`--limit <number>`（默认：50） |
| `adk list` | 显示已安装的依赖项 | `--format json`、`--limit <number>`（默认：50） |
| `adk info <name>` | 集成详细信息（仅集成，不包括插件） | `--actions`、`--channels`、`--events`、`--full`、`--format json` |
| `adk add <name>@<version>` | 将集成添加到项目 | `--alias <name>`、`--format json` |
| `adk add plugin:<name>@<version>` | 将插件添加到项目 | `--alias <name>`、`--format json` |
| `adk remove <name>` | 删除集成、插件或接口 | `--format json` |
| `adk upgrade [name]` | 升级依赖项（或交互式升级所有） | `--format json` |

使用 `--format json` 进行 CLI 检查。

## 关键模式

### 始终使用 CLI

```bash
# 正确 - 使用 adk add
adk add slack@3.0.0
adk add plugin:desk-hitl@1.0.0
adk add interface:translator@1.0.0

# 错误 - 永远不要手动编辑 agent.config.ts 依赖项
# 不要在 dependencies 块中手动编写条目
```

### 版本固定

```bash
# 正确 - 固定到特定版本
adk add browser@0.8.6

# 有风险 - 解析到最新版本，可能会意外更改
adk add browser
```

### 访问集成操作

```typescript
// 正确 - 从 @botpress/runtime 导入，使用 agent.config.ts 中的别名
import { actions } from '@botpress/runtime'
await actions.slack.sendMessage({ channel: '#general', text: 'Hello' })

// agent.config.ts 中的别名决定了访问器名称
// { browser: { version: 'browser@0.8.6', enabled: true } }
await actions.browser.webSearch({ query: 'search term' })
```

### 检查配置要求

```bash
# 使用 --format json 检查集成需要什么配置
adk info slack --format json

# 查看 configuration.schema 以获取必需字段
# 查看 configuration.identifier 以获取 OAuth
# 查看 configurations 以获取替代配置模式
```

## 此技能回答的问题示例

### 初学者

- "有哪些可用的集成？"
- "如何将 Slack 添加到我的 agent？"
- "浏览器集成是什么？"

### 中级

- "如何在沙盒模式下配置 WhatsApp？"
- "Webchat 集成提供哪些操作？"
- "如何从工作流中调用 Linear 操作？"
- "聊天和 Webchat 的区别是什么？"

### 高级

- "如何使用私有工作区集成？"
- "`registration_pending` 状态是什么意思？"
- "如何为更干净的代码别名集成？"
- "如何以编程方式检查集成的 config schema？"
