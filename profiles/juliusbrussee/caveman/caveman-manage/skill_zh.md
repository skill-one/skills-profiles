# 管理受评估门控的实验

将每一次生命周期变更都视为生产控制操作。读取当前状态和结果，然后报告一项受支持的建议或阻断。

当前的 agent MCP 有意采用只读模式：`control-api` 尚无法原子化地强制完整生命周期转换表与证据门控。

## 不可协商的门控

1. 审查、检查、解释或建议的请求仅授权读取操作。
2. 绝不批准结果处于待处理状态、缺少所需护栏、或证据报告存在违规的实验。
3. 绝不将实验提升转化为 `verified_savings`。唯有活跃真实流量加上提供者因果、提供者完整账本证据，才能做到这一点。
4. 绝不提供组织 id。项目与租户范围来自登录的 Caveman 身份以及服务器 RBAC。
5. 绝不执行生命周期变更，即使用户已批准。确切的 `<action>:<experiment_id>` 字符串可由 agent 生成，并非人类意图的证明。
6. 未知状态和服务器错误一律失败关闭。报告确切的 `cave_snake_code`。

## 第 1 步 — 加载项目与实验

优先使用 MCP：

```text
caveman_context {}
caveman_experiment_get {"action":"get","experiment_id":"<id>"}
caveman_experiment_get {"action":"results","experiment_id":"<id>"}
```

当用户未指定 id 时，使用 `{"action":"list"}`。

CLI 回退方案：

```bash
caveman cloud experiments list
caveman cloud experiments show <id>
caveman cloud experiments results <id>
```

如果登录、项目、实验或结果不可用，立即停止。

## 第 2 步 — 评估证据

报告：

- 当前生命周期状态与安全类别；
- 控制组与候选组的样本量；
- 质量或评估结果；
- 存在的延迟、错误、成本、重试、丢弃与升级护栏；
- 证据成本；
- 回滚或暂停原因；
- 结果是否处于待处理、失败、可提升或活跃状态。

缺失并不代表通过。如果缺少必需字段，说明 `evidence incomplete`，不得提出批准建议。

## 第 3 步 — 提出一项操作

允许的操作：

- `start` — 仅从可启动的草稿或已排队状态，且已配置分诊器时执行；
- `approve` — 仅具备完整通过的证据，且当前角色可批准的安全类别时执行；
- `cancel` — 终止用户不再希望运行的活跃实验；
- `rollback` — 通过服务器关联的策略路径回滚活跃或有害变更。当前部署可能诚实拒绝该操作，并返回 `cave_not_implemented`；切勿将该响应描述为回滚。

展示建议与 id：

```text
Proposed action: approve experiment 7f...
Reason: candidate passed quality and every configured guardrail.
Execution: blocked until server-authoritative lifecycle and evidence gates ship.
```

不要将“管理它”或“做最优选择”等早期一般性表述视为变更批准。

## 第 4 步 — 阻断不安全执行

不得生成或执行可执行的生命周期命令。说明当前服务器尚未原子化强制执行所有证据/状态转换。因此，CLI 和 MCP agent 界面目前仅暴露实验读取操作。

## 第 5 步 — 在外部操作员操作后重新读取

如果操作员表示其已执行命令，重新读取详情与结果。报告服务器观察到的操作后状态、审计或结果响应，以及任何返回的策略交付状态。切勿仅凭操作员意图推断成功。

使用以下结束语：

```text
Action: <action> <experiment-id>
Before: <state>
Server response: <status and cave_snake_code if any>
After: <re-read state>
Basis: experiment evidence only. Verified savings unchanged unless the signed
ledger independently records active, provider-causal real-traffic savings.
```
