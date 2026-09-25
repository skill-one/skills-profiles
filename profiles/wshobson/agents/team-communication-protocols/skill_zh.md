# 团队沟通协议

团队代理成员之间有效沟通的协议，包括消息类型选择、计划审批工作流、关闭程序以及常见的反模式以避免。

## 何时使用此技能

- 为新团队建立沟通规范
- 在消息类型（message、broadcast、shutdown_request）之间进行选择
- 处理计划审批工作流
- 管理团队优雅关闭
- 发现团队成员身份和能力

## 消息类型选择

### `message`（直接消息）— 默认选择

发送给单个特定团队成员：

```json
{
  "type": "message",
  "recipient": "implementer-1",
  "content": "您的 API 端点已准备就绪。现在可以构建前端表单了。",
  "summary": "API 端点已就绪，可用于前端"
}
```

**用于**：任务更新、协调、提问、集成通知。

### `broadcast` — 限制使用

同时发送给所有团队成员：

```json
{
  "type": "broadcast",
  "content": "关键：共享类型文件已更新。继续前请拉取最新版本。",
  "summary": "共享类型已更新"
}
```

**仅用于**：影响所有人的关键阻塞、共享资源的重大变更。

**为何限制使用**？每个广播会发送 N 条独立消息（每条对应一个团队成员），消耗与团队规模成正比的 API 资源。

### `shutdown_request` — 优雅终止

请求团队成员关闭：

```json
{
  "type": "shutdown_request",
  "recipient": "reviewer-1",
  "content": "审核完成，关闭团队。"
}
```

团队成员以 `shutdown_response` 响应（批准或附带原因拒绝）。

## 沟通反模式

| 反模式                          | 问题                                  | 更好的方法                        |
| -------------------------------- | ---------------------------------------- | -------------------------------------- |
| 广播常规更新                    | 浪费资源、噪音                  | 直接消息给受影响的团队成员    |
| 发送 JSON 状态消息            | 非为结构化数据设计         | 使用 TaskUpdate 更新任务状态   |
| 在集成点不沟通                 | 团队成员针对过时的接口构建       | 当您的接口就绪时发送消息   |
| 通过消息进行微观管理              | 让团队成员不堪重负、减慢工作         | 在里程碑处检查，而不是每一步 |
| 使用 UUID 而不是名称            | 难以阅读、易出错                | 始终使用团队成员名称              |
| 忽略空闲的团队成员                 | 浪费容量                          | 分配新工作或关闭           |

## 计划审批工作流

当团队成员以 `plan_mode_required` 被生成时：

1. 团队成员使用只读探索工具创建计划
2. 团队成员调用 `ExitPlanMode`，发送 `plan_approval_request` 给负责人
3. 负责人审核计划
4. 负责人以 `plan_approval_response` 响应：

**批准**：

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "implementer-1",
  "approve": true
}
```

**拒绝并附带反馈**：

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "implementer-1",
  "approve": false,
  "content": "请添加 API 调用的错误处理"
}
```

## 关闭协议

### 优雅关闭序列

1. **负责人发送 shutdown_request** 给每个团队成员
2. **团队成员接收请求** 作为带有 `type: "shutdown_request"` 的 JSON 消息
3. **团队成员响应** 以 `shutdown_response`：
   - `approve: true` — 团队成员保存状态并退出
   - `approve: false` + 原因 — 团队成员继续工作
4. **负责人处理拒绝** — 等待团队成员完成，然后重试
5. **所有团队成员关闭后** — 调用 `TeamDelete` 删除团队资源

### 处理拒绝

如果团队成员拒绝关闭：

- 检查他们的原因（通常是“仍在处理任务”）
- 等待他们当前任务完成
- 重试关闭请求
- 如果紧急，用户可以强制关闭

## 团队成员发现

通过读取配置文件查找团队成员：

**位置**：`~/.claude/teams/{team-name}/config.json`

**结构**：

```json
{
  "members": [
    {
      "name": "security-reviewer",
      "agentId": "uuid-here",
      "agentType": "team-reviewer"
    },
    {
      "name": "perf-reviewer",
      "agentId": "uuid-here",
      "agentType": "team-reviewer"
    }
  ]
}
```

**始终使用 `name`** 进行消息发送和任务分配。绝不要直接使用 `agentId`、角色名称或未加后缀的别名。如果团队成员以 `team-lead-2` 被生成，发送给 `team-lead-2`，而不是 `team-lead`。

## 故障排除

**团队成员不响应消息。**
检查团队成员的任务状态。如果它处于空闲状态，可能已完成任务并等待分配新工作或关闭。如果它仍处于活动状态，可能正在执行当前操作，一旦操作完成就会处理消息。

**团队成员说它看不到 SendMessage。**
检查团队成员代理的 `tools:` 前置符。当代理使用受限工具允许列表时，必须明确列出 Agent Teams 沟通工具，如 `SendMessage`、`TaskList`、`TaskGet` 和 `TaskUpdate`。

**负责人为每个状态更新发送广播。**
这是一种常见的反模式。广播很昂贵——每条广播发送 N 条消息。使用直接消息（`type: "message"`）进行点对点更新。保留广播用于关键共享资源变更，如接口合约更新。

**团队成员意外拒绝了关闭请求。**
团队成员仍在工作。检查拒绝原因（在 `shutdown_response` 的 `content` 字段中），等待工作完成，然后重试。绝不要强制终止有未保存工作的团队成员。

**收到的 plan_approval_request 缺少 request_id。**
团队成员在进入计划模式时未提供必要的请求上下文。让团队成员重新进入计划模式，完成探索，然后再次调用 `ExitPlanMode`。`request_id` 由计划模式系统自动生成。

**两个团队成员互相等待，双方都没有进展。**
这是一个死锁：双方都在等待对方先完成。负责人应向其中一个团队成员发送带有桩或部分结果的直接消息，以便它能够解除阻塞并继续。

## 相关技能

- [team-composition-patterns](../team-composition-patterns/SKILL.md) — 在建立沟通规范之前选择代理类型和团队规模
- [parallel-feature-development](../parallel-feature-development/SKILL.md) — 使用沟通协议协调并行实现者之间的集成交接
