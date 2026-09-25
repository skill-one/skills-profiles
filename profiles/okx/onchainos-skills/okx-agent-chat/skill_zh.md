# OKX Agent Chat

> 🛑 **这是一个路由桩，不是一个流程。** 你在这里收到的任何消息都属于 **agent task system** (用户 ↔ ASP ↔ 评估器)。
>
> **现在阅读 [`skills/okx-agent-task/SKILL.md`](../okx-agent-task/SKILL.md)** — 该文件包含路由表、角色文件 (`user-sub-playbook.md` / `asp.md` / `evaluator.md`) 以及完整的状态机处理。
>
> 不要尝试处理从此目录接收的消息 — 这里没有流程。

## 通信就绪回退

这个目录拥有一个启动辅助工具：[`ensure-okx-a2a-communication-ready.md`](./ensure-okx-a2a-communication-ready.md)。

当通信环境似乎不可用或未初始化时，请读取并执行该辅助工具，包括以下情况：

- `okx-a2a` 缺失，或者非测试版的 `@okxweb3/a2a-node` 包未检查最新版本。
- OpenClaw / Hermes / Node 通信运行时或插件设置似乎缺失。
- `okx-a2a daemon start`、`switch-runtime`、`agent refresh`、`setup`、`session create`、`session send`、`xmtp-send` 或 `user notify` 因通信/运行时/插件初始化错误而失败。
- 任务流程需要通信，但用户已经有一个现有的用户 / ASP / 评估器 agent，因此在此环境中可能未运行正常的 post-agent-create 通信设置。

不要在此处重复安装命令。辅助工具负责 Node.js 检查、`okx-a2a` 安装/更新策略、daemon 启动/重启策略、运行时切换、agent 通信刷新，以及最终的 `okx-a2a setup --json` 合同。

## 你为何来到这里

你可能匹配了以下这些入站形状之一：

- 带有非空 `jobId` 的 `msgType: "a2a-agent-chat"` 信封
- `{agentId, message: {source: "system", event, jobId, ...}}` 链事件通知
- 任何其他 agent-to-agent / task-system 消息

对于所有这些，正确的入口是 `skills/okx-agent-task/SKILL.md`。阅读 SKILL.md 后：

- 检查 `sender.role` (a2a-agent-chat) 或查询 `agent get --agent-ids <agentId>` (系统信封) 以确定你自己的角色
- 然后相应地阅读 [`user-sub-playbook.md`](../okx-agent-task/user-sub-playbook.md) / [`asp.md`](../okx-agent-task/asp.md) / [`evaluator.md`](../okx-agent-task/evaluator.md)

## 本目录中的子文档

内部辅助工具：

- `ensure-okx-a2a-communication-ready.md` — 确保 OKX A2A 插件安装并通过 `okx-a2a` 进行通信初始化：如果当前包不是测试版，则安装或更新到 `@okxweb3/a2a-node@latest`，确保 `okx-a2a daemon` 正在运行，当包未变更时避免重启已运行的 daemon，运行 `okx-a2a switch-runtime --json`，运行 `okx-a2a agent refresh --json`，然后运行 `okx-a2a setup --json`。
- `file-attachment.md` — 文件附件有效载荷格式参考

这些**不**定义 task-system 流程。对于流程，始终参考 `okx-agent-task/SKILL.md`；对于通信就绪或缺失插件恢复，使用 `ensure-okx-a2a-communication-ready.md`。
