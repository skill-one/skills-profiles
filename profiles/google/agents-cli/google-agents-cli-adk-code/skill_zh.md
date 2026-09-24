# ADK 代码参考

首先激活 `/google-agents-cli-workflow`，以完成必要的开发阶段和脚手架搭建步骤。

## 1. 研读配方（无需项目）

**Python — 在回答“如何构建 X”之前，阅读 `references/samples.md` 中的主题索引。**
已实现的方案涵盖：沙箱/每用户代码执行、可加载至 Agent 的 `SKILL.md`
技能、跨会话记忆、对风险操作进行批准门控、工具护栏、每用户凭证，以及定时/事件驱动运行。

**Go — 阅读上游 [`examples/`](https://github.com/google/adk-go/tree/main/examples)。**
克隆仓库后，在实现之前阅读与所需能力匹配的实现。

## 2. 编写代码的先决条件

在项目完成脚手架搭建之前，切勿编写 Agent 代码。

1. 验证项目：运行 `agents-cli info`（若配置存在则继续）。
2. 新建项目：运行 `agents-cli scaffold create <name>` —— Go 项目添加 `--agent adk_go`。
3. 现有代码：运行 `agents-cli scaffold enhance .`。

## 快速参考 —— 最常见模式

请分别参考 `references/adk-python.md` 和 `references/adk-go.md` 获取 Python 和 Go 的代码示例。

---

## 参考资料

常见模式请参考速查表。对于深层知识，获取文档索引或检查已安装的包。

| 参考资料 | 语言 | 阅读时机 |
|------|------|-------------|
| `references/samples.md` | Python | **ADK 参考配方的主题索引目录。** 在流程第一阶段（脚手架搭建和编写代码之前）阅读 —— 它将能力映射到实现该能力的配方。 |
| `references/adk-python.md` | Python | 核心 ADK API：`Agent`、工具、回调、插件、状态、产物、多 Agent 系统、`SequentialAgent` / `ParallelAgent` / `LoopAgent`、自定义 `BaseAgent`、`ManagedAgent`（服务器托管的官方 Agent），A2A 协议，A2UI。大多数 Agent 的默认选择。 |
| `references/adk-python-workflows.md` | Python | 基于图的 Workflow API（ADK Python 2.0）：节点、边、扇出/扇入、HITL、并行处理。需要显式图拓扑结构时使用。 |
| `references/adk-go.md` | Go | 核心 ADK Go API：`llmagent`、工具、回调、插件、状态、产物、多 Agent 系统、顺序/并行/循环 Agent、自定义 Agent、运行器、HTTP 服务，A2A 协议，环境触发器。大多数 Agent 的默认选择。 |
| `references/adk-go-workflows.md` | Go | 基于图的 Workflow API：节点、边、扇出/扇入、HITL、并行处理。需要显式图拓扑结构时使用。 |
| [`examples/`](https://github.com/google/adk-go/tree/main/examples) | Go | 可运行的 upstream 程序 —— Go 的配方目录最接近的替代。 |
| `curl https://adk.dev/llms.txt` | Python | 文档索引（每个页面的标题 + URL）。获取后，使用 `WebFetch` 获取特定页面，处理速查表之外的内容。 |
| 已安装的 ADK 包 | Python | 确切的签名和符号 —— 检查源代码（参见 `references/adk-python.md` 中的“检查 ADK 源代码”）。 |

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流、编码规范与操作规则
- `/google-agents-cli-scaffold` — 使用 `agents-cli scaffold create` / `scaffold enhance` 创建和增强项目
- `/google-agents-cli-eval` — 评估方法、数据集模式与评估修复循环
- `/google-agents-cli-deploy` — 部署目标、CI/CD 流水线与生产工作流
