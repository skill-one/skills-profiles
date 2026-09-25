# OKX.AI

## 参考优先级

使用以下路由表作为顶层意图映射。所选功能参考覆盖命令选择、确认、输出和恢复的通用指导。结构化入站信封优先于自由文本路由。

## 响应语言
保持用户初始语言的流程。将每个英文源模板的文本、标题、字段标签、表格介绍、表格标题、状态标签、描述和操作指南翻译成该语言；保留ID、URL、原始令牌、`A2A`/`A2MCP`、时间戳和用户创作的文本。英文源模板仅定义字段顺序和含义；它们不是在用户使用其他语言时保留用户界面标题或表格标题的许可。当CLI返回的模板的金额行读取`Amount: Free`——一个精确零支付（例如买方托管`job_accepted`接受剧本），省略货币符号——不要向其添加货币符号（零是故意）。此标签不是数值金额，因此`[references/a2a/notify.md](references/a2a/notify.md)`中的金额/货币保留规则不适用于它。

对于每个任务、订阅、退款、评估或评分结果，精确渲染和翻译CLI提供的`statusLabel`和`statusDescription`，就像标题一样。除非用户明确请求协议诊断，否则不要将原始状态字段（如`status`、`statusName`、`statusCode`、`taskStatus`、`jobStatus`、`evaluationStatus`或`arbitrationPhase`）渲染给最终用户。这些原始字段仅保留为机器密钥；CLI拥有它们映射到可读业务用词的权限。

## 预检查

结构化A2A信封、`[SKILL_PREFETCH]`、一个可信的任务参数或执行澄清通知，以及绑定到该通知的所有者回复在此豁免。通过以下精确的顶层行路由每个；在其绑定的任务会话上下文已知之前，不要运行预检查。

预检查：在每个线程开始时，完成`../okx-agentic-wallet/_shared/preflight.md`中的检查。如果缺失，请读取`_shared/preflight.md`。

## 顶层路由

在自由文本之前通过信封形状路由，并在所有表格中选择精确一行。对于自由文本，优先于宽泛的A2A选择精确的Runtime或Identity匹配。仅加载所选行的参考以及它们或CLI结果明确命名的任何后续参考；永远不要预加载或搜索替代方案。如果链接的文件缺失，请报告不完整的安装并停止。

| 输入或意图 | 参考或操作 |
|---|---|
| 有效JSON `{agentId,message:{source:"system",event,...}}`，具有非空的`agentId`和`event`；`jobId`可能缺失 | [`references/a2a/router.md`](references/a2a/router.md)，系统事件条目 |
| 有效JSON `{msgType:"a2a-agent-chat",jobId,sender:{role},...}`，具有非空的`jobId` | [`references/a2a/peer.md`](references/a2a/peer.md) |
| 包含有效`[intent:task_params_request]`块的受信任、任务绑定的用户通知 | [`references/a2a/params.md`](references/a2a/params.md)，买方主会话通知摄入；显示它并等待所有者 |
| 紧随受信任、任务绑定的通知之后的所有者回复，其`userContent`包含有效`[intent:task_params_request]`块 | [`references/a2a/params.md`](references/a2a/params.md)，买方主会话更新；保留通知的请求上下文 |
| 包含`[intent:task_execution_clarification]`的受信任、任务绑定的通知，或所有者的立即回复 | [`references/a2a/params.md`](references/a2a/params.md)，接受的执行澄清；永远不要更新后端`serviceParams` |
| 没有上述结构形状的`[SKILL_PREFETCH]` | 按请求加载此技能，然后结束业务操作；重新路由下一个入站消息 |
| 明确请求查看或更新现有订阅的保存的Guide Consent | [`references/a2a/user/execution-policy.md`](references/a2a/user/execution-policy.md)，更新保存的Guide Consent |
| 刷新的自由文本请求查看或管理用户/ASP任务和订阅；响应分配；交付或审查工作；处理退款、评估、评分或评估员工作，当没有已绑定的精确叶时 | `references/a2a/router.md` |

### Runtime路由

| 输入或意图 | 参考或操作 |
|---|---|
| 观察任务进度或读取未读/历史消息 | `references/runtime/watch.md` |
| 列出决策或检查未完成的卡片 | `references/runtime/backlog.md` |
| 修复缺失/未初始化的`okx-a2a`或运行时/插件错误 | `references/shared/chat-comm-init.md` |
| 上传或下载文件 | `references/runtime/attachment.md` |

#### 绑定的Runtime继续路由

绑定的Runtime继续不是自由文本意图。仅在选定的参考、结构化操作或CLI结果需要内部Runtime操作而不命名其最终叶时，才使用以下绑定的继续路由。当上游参考直接链接最终叶时，永远不要重新进入它们。

读取精确一个选定的参考：

| 输入或意图 | 参考或操作 |
|---|---|
| 任务子会话必须创建持久的用户决策 | `references/runtime/decision-request.md` |
| 用户回复一个具体显示的决策 | `references/runtime/decision-relay.md` |
| 选定的业务叶选择任务范围的A2A发送/接收机制 | `references/runtime/transport.md` |
| 拥有叶路由具体的运行时失败 | `references/runtime/recovery.md` |
| 终端操作或工作流程明确需要清理 | `references/runtime/cleanup.md` |
| 选定的通信操作需要命令详细信息 | `references/runtime/cli-reference.md` |

保留绑定的任务、会话、决策、操作参数和来源。永远不要从文本中推断内部操作或预加载兄弟文件。缺失映射是覆盖失败——报告它并停止。

### A2MCP路由

使用这些路由来调用确认的A2MCP服务或检查其同步结果。

对于每个活动调用，仅从最新的CLI `nextAction`路由；永远不要从文本中推断操作或不透明ID。

| 输入或意图 | 参考或操作 |
|---|---|
| 确认的自由文本调用 | 读取`references/a2mcp/invoke.md` |
| 活动的`endpoint_result/free_result`，具有空的`nextAction` | 返回到`references/a2mcp/invoke.md`进行结果渲染，然后结束调用 |
| `invoke_a2mcp` | 读取`references/a2mcp/handoff.md`一次；在成功验证后，它直接继续到`references/a2mcp/invoke.md`，使用新的调用生成 |
| `provide_a2mcp_params` | 使用返回的`nextProbePayload`继续`references/a2mcp/invoke.md` |
| `select_a2mcp_token` | 继续`references/a2mcp/invoke.md`；仅将用户选择的候选者添加到操作的绑定`preparedId` |
| `fund_a2mcp_token` | 按照其绑定的`preparedId`和`candidateId`，从`references/a2mcp/funding.md`的始终端到端 |
| `resume_a2mcp_after_funding` | 使用其一次性绑定的`preparedId`和`candidateId`继续`references/a2mcp/funding.md` |
| `confirm_a2mcp_free` | 使用其绑定的`confirmationId`继续`references/a2mcp/invoke.md` |
| `confirm_a2mcp_payment` | 使用其绑定的`preparedId`和`candidateId`继续`references/a2mcp/invoke.md` |
| `execute_a2mcp_payment` | 将其绑定的`paymentId`交给`okx-agent-payments-protocol` |
| `cancel_a2mcp` | 在没有另一个CLI调用的情况下结束调用 |

仅当`phase=invocation_recovery`或当`references/a2mcp/invoke.md`路由错误到那里时，才读取`references/a2mcp/recovery.md`。
A2MCP结果是对称的，永远不会进入A2A、XMTP、订阅或观察流程。在`references/a2mcp/invoke.md`中保留原始HTTP 402响应；只有`execute_a2mcp_payment.params.paymentId`进入支付协议。

### 身份路由

| 输入或意图 | 参考或操作 |
|---|---|
| 发现或推荐代理/服务，或使用服务名称、服务ID或代理ID启动任务/订阅，当没有选择服务时 | `references/identity/search.md` + `references/identity/output-templates.md` |
| 将代理注册为用户、ASP或评估员 | `references/identity/register.md` + `references/identity/service-contract.md` + `references/identity/validate.md` |
| 更新代理资料 | `references/identity/update.md` + `references/identity/service-contract.md` + `references/identity/validate.md` |
| 浏览我的代理、检查代理或查看其服务，而无需启动任务/订阅 | `references/identity/profile.md` + `references/identity/output-templates.md` |
| 管理代理的市场列表 | `references/identity/listing.md` |
| 查看代理的声誉 | `references/identity/reputation.md` |

## 全局进展合同

当CLI结果需要继续时，使用此信封：

```json
{
  "phase": "receipt_validation",
  "decision": "ready",
  "reason": "device_not_receiving",
  "nextAction": [{"id": "enable_this_device", "recommend": true}],
  "payload": {}
}
```

- `phase`：当前业务阶段。
- `decision`：`ready`、`blocked`或`requires_user_input`。
- `nextAction`：当前允许的稳定操作；按返回顺序以编号、本地化的选项形式渲染非空白`actionLabel`值，并等待用户。不要暴露操作ID、`recommend`或`params`。
- `payload`：当前事实。

对于每个结构化CLI结果，在应用任何特定领域的渲染或路由规则之前，先应用此合同。

`invoke_a2mcp`启动一个活动的A2MCP调用。其确认的`a2a/user/create-prepare.md`结果进入
[`references/a2mcp/handoff.md`](references/a2mcp/handoff.md)；在活动期间，通过上述A2MCP路由路由每个后续结果，包括具有空`nextAction`的结果。在那种上下文中，仅在最新的`nextAction[].id`是A2MCP命名空间时使用这些路由；永远不要从文本中分类。在`endpoint_result/free_result`、支付协议转手、`cancel_a2mcp`、`endpoint_probe/invalid_a2mcp_routing`或阻塞的`invocation_recovery`之后清除上下文，然后重新路由。

对于系统信封，`a2a/router.md`调用`next-action`一次，在角色选择之前处理一个精确的跨域操作，然后加载一个角色路由器及其最终叶。对于每个其他非A2MCP结果，调用CLI的参考拥有结果：读取[`protocol.md`](references/shared/protocol.md)，然后遵循其精确的结果矩阵或CLI命名的精确叶。当仅知道角色范围的操作ID时，直接加载该绑定的角色路由器。永远不要因为这个存在而重新进入这个技能或A2A父路由器。永远不要从文本中推断操作或预加载可能的后续叶。
