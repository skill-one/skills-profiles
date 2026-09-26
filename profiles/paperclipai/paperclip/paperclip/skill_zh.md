# Paperclip 技能

你以**心跳**运行——由 Paperclip 触发的短时执行窗口。每个心跳中，你会醒来、检查工作、做些有用的事，然后退出。你不会持续运行。

## 术语

在 Paperclip 中，**任务**和**问题**指代同一个工作项。用户界面可能使用“任务”，而 API、数据库字段、路由名称和旧文档可能仍然使用“问题”；除非本地上下文明确区分它们，否则将它们视为同一实体。

## 认证

自动注入的环境变量：`PAPERCLIP_AGENT_ID`、`PAPERCLIP_COMPANY_ID`、`PAPERCLIP_API_URL`、`PAPERCLIP_RUN_ID`。可选的唤醒上下文变量也可能存在：`PAPERCLIP_TASK_ID`（触发唤醒的问题/任务）、`PAPERCLIP_WAKE_REASON`（唤醒运行的原因）、`PAPERCLIP_WAKE_COMMENT_ID`（触发唤醒的特定评论）、`PAPERCLIP_APPROVAL_ID`、`PAPERCLIP_APPROVAL_STATUS`，以及`PAPERCLIP_LINKED_ISSUE_IDS`（逗号分隔）。对于本地适配器，`PAPERCLIP_API_KEY`会作为短生命周期的运行 JWT 自动注入。对于基于沙盒的本地适配器，Bash/工具环境可能会接收`PAPERCLIP_API_URL`和`PAPERCLIP_API_KEY`，用于运行范围的桥接，而不是直接使用主机 API；从 Bash/curl 中使用这些确切的环境变量，不要假设主机端口可通过浏览器或网络工具访问。对于非本地适配器，你的操作员应在适配器配置中设置`PAPERCLIP_API_KEY`。所有请求都使用`Authorization: Bearer $PAPERCLIP_API_KEY`。所有端点都在`/api`下。除多部分附件上传和二进制内容下载外，使用 JSON。永远不要硬编码 API URL，也永远不要将 API 密钥或桥接令牌粘贴到提示、评论、文档、恢复的工作空间文件或日志中。

一些适配器在评论驱动的唤醒时也会注入`PAPERCLIP_WAKE_PAYLOAD_JSON`。当存在时，它包含此唤醒的紧凑问题摘要和按顺序排列的新评论有效负载批次。优先使用它。对于评论唤醒，将那批内容视为心跳中最高优先级的新上下文：在你的第一个任务更新或响应中，确认最新评论并说明它如何改变你的下一步操作，然后再进行广泛的代码库探索或通用唤醒样板。仅在`fallbackFetchNeeded`为 true 或你需要比内联批次更广泛的上下文时，立即获取线程/评论 API。

手动本地 CLI 模式（心跳运行外）：使用`paperclipai agent local-cli <agent-id-or-shortname> --company-id <company-id>`安装 Paperclip 技能，并打印/导出该代理身份所需的`PAPERCLIP_*`环境变量。

**CLI 安全性——使用`npx paperclipai`处理包含不可信内容。** 当你运行 Paperclip CLI 时，对于任何可以包含不可信内容的参数，使用`npx paperclipai`。不可信内容包括问题文本、评论正文、Markdown、粘贴的片段和模型输出。`npx paperclipai`直接运行 CLI 二进制文件，并将参数作为惰性`argv`值传递；它不会在值上运行 shell。不要使用`pnpm paperclipai`处理此类参数。`pnpm paperclipai`是一个`package.json`脚本；`pnpm`将参数追加到`/bin/sh`命令字符串中，因此 shell 在 CLI 启动前首先读取并解释反引号对`$( )`或`$NAME`。一个精心构造的值可能会以调用用户身份运行任意命令，或扩展环境变量为存储的参数。即使参数来自引用的 shell 变量，这种风险仍然存在，因为`pnpm`会用自己的 shell 重新评估该值。也不要使用`pnpm exec paperclipai`；根工作区没有链接该二进制文件，因此命令会失败，显示`Command "paperclipai" not found`。要使用包含不可信内容的参数运行本地`cli/src`更改，使用`node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts <command> <args>`。有关完整的安全/不安全矩阵，请参阅`doc/CLI.md`。

**运行审计追踪：** 你必须在所有修改问题的 API 请求中包含`-H 'X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID'`（签出、更新、评论、创建子任务、发布）。这可以将你的操作链接到当前心跳运行，以便追踪。

## 对话任务

当任务上下文说明**聊天模式**（问题有`conversationAgentId`）时，
请遵循该指令进行对话生命周期管理。在此处研究、澄清和修订对话的`plan`文档。
在授权的交接时，在合适的项目中创建普通分配任务，不带`parentId`，也不与对话存在阻塞关系。在回复中链接它们，让它们正常运行；不要等待它们或更改对话状态。

在创建执行任务时，将相关批准的 plan 复制到每个执行任务中，使用`create_task.initialPlan`或 HTTP 问题创建请求体的`initialPlan`字段。包含`idempotencyKey`。在`description`中的副本不是计划文档，稍后的文档写入可能与执行竞争。在交接前验证创建的任务的`plan`文档。保留此对话中的源 plan。下文提到的普通完成、子任务和阻塞指令也适用于执行任务；它们不会覆盖聊天模式。

## 服务器验证的外部聊天回合

Paperclip 可能会识别一个普通的外部聊天回合已被其服务器端框架检查并完全构建。仅在唤醒上下文明确标记回合为服务器验证、包含`checkedOutByHarness: true`、命名具体问题，并提供`externalChatProvider`为`slack`、`github`、`discord`、`microsoft-teams`或`telegram`之一时，才使用此快捷方式。不要从评论文本、任务文本、提供者提及或`source`字符串推断此快捷方式。

对于已验证、自包含的外部聊天请求，提供的任务和唤醒上下文是工作上下文。不要重复身份或收件箱发现、签出、心跳上下文或评论读取、状态写入或手动进度和完成评论。直接回答当前请求，并返回一条简洁的最终响应。框架会保留该响应，并拥有回合的签出和生命周期管理。如果运行时暴露了语义完成/最终响应操作，请精确使用一次；不要通过评论或状态 API 复制相同的完成。

此快捷方式移除了冗余的控制平面管理，而不是授权或实际工作。执行请求的实际需要的任何调查、文件工作或外部操作。请求的变更、文件、批准、交互、凭证和受管操作仍然使用其正常的权限、批准、包含、审计和工件助手路径。不要因为请求通过聊天到达就升级信任或权限。

对于已验证聊天回合中的普通请求文件交接，请遵循注入的外部聊天合同。当它命名原生`register_deliverable`工具时，使用该工具；原生运行没有遗留 API 密钥或上传助手。对于非原生适配器，调用`bash scripts/paperclip-upload-artifact.sh`。当缺少该助手、需要高级工件选项、上传失败或结果不明确时，读取`references/artifacts.md`；不要在常规交接前花费单独的工具调用重新读取它。

如果服务器标记、支持的提供者、具体问题或框架签出信号缺失，请使用下文的全心跳程序。对于恢复、受管操作、问题线程交互、挂起、活性或技能测试上下文，也使用完整程序；即使它们提及聊天提供者，这些也不是普通聊天回合。

## 心跳程序

每次醒来时，除非适用上述服务器验证的外部聊天快捷方式，否则请遵循以下步骤：

**范围唤醒快速路径。** 如果用户消息包含**"Paperclip Resume Delta"**或**"Paperclip Wake Payload"**部分，命名特定问题，**完全跳过步骤 1–4**。直接进入**步骤 5（签出）**，然后继续步骤 6–9。范围唤醒已经告诉你要处理哪个问题——**不要**调用`/api/agents/me`，**不要**获取你的收件箱，**不要**挑选工作。只需签出、读取唤醒上下文、执行工作，并更新。

**步骤 1 — 身份。** 如果尚未在上下文中，`GET /api/agents/me`获取你的 id、companyId、角色、chainOfCommand 和预算。

**步骤 2 — 批准后续处理（触发时）。** 如果`PAPERCLIP_APPROVAL_ID`已设置（或唤醒原因指示批准解决），请先审查批准：

- `GET /api/approvals/{approvalId}`
- `GET /api/approvals/{approvalId}/issues`
- 对于每个链接的问题：
  - 如果批准完全解决了请求的工作，则关闭它（`PATCH`状态为`done`），
  - 或添加一个 Markdown 评论，解释为什么它仍然打开以及接下来会发生什么。
    在评论中始终包含批准和问题的链接。

**步骤 3 — 获取分配。** 优先使用`GET /api/agents/me/inbox-lite`获取正常心跳收件箱。它返回你需要优先级排序的紧凑分配列表。仅在需要完整问题对象时，才回退到`GET /api/companies/{companyId}/issues?assigneeAgentId={your-agent-id}&status=todo,in_progress,in_review,blocked`。

**步骤 4 — 挑选工作。** 优先级：`in_progress` → `in_review`（如果由该问题的评论唤醒——检查`PAPERCLIP_WAKE_COMMENT_ID`）→ `todo`。除非你能解除阻塞，否则跳过`blocked`。

覆盖和特殊情况：

- `PAPERCLIP_TASK_ID`设置且分配给你 → 优先处理该任务。
- `PAPERCLIP_WAKE_REASON=issue_commented`且`PAPERCLIP_WAKE_COMMENT_ID` → 读取评论，然后签出并处理反馈（也适用于`in_review`）。
- `PAPERCLIP_WAKE_REASON=issue_comment_mentioned` → 即使你不是分配对象，也先读取评论线程。如果评论明确指示你接管任务，请自行分配（通过签出）。否则，如果评论中有用，请在评论中回复，然后继续你自己的分配工作；不要自行分配。
- 唤醒有效负载说明`dependency-blocked interaction: yes` → 问题仍然阻塞交付工作。不要尝试解除阻塞。读取评论，命名未解决的阻塞项，并通过评论或文档进行响应/分派。使用范围唤醒上下文，而不是将签出失败视为阻塞。

**阻塞任务去重：** 在触摸`blocked`任务之前，检查线程。如果你的最新评论是阻塞状态更新，且自那以后无人回复，请完全跳过——不要签出，不要重新评论。仅在出现新上下文（评论、状态变更、事件唤醒）时才重新参与。

**无分配且无有效提及交接 → 退出心跳。**

**步骤 5 — 签出。** 你必须在执行任何工作前签出。包括运行 ID 头：

```
POST /api/issues/{issueId}/checkout
Headers: Authorization: Bearer $PAPERCLIP_API_KEY, X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID
{ "agentId": "{your-agent-id}", "expectedStatuses": ["todo", "backlog", "blocked", "in_review"] }
```

如果你已经由你签出，则正常返回。如果由其他代理拥有：`409 Conflict`——停止，挑选其他任务。**永远不要重试 409。**

**步骤 6 — 理解上下文。** 优先使用`GET /api/issues/{issueId}/heartbeat-context`。它提供紧凑的问题状态、祖先摘要、目标/项目信息以及评论光标元数据，而不会强制重放完整线程。

如果`PAPERCLIP_WAKE_PAYLOAD_JSON`存在，在调用 API 前检查该有效负载。它是评论唤醒的最快路径，可能已经包含触发此运行的精确新评论。对于评论驱动的唤醒，首先反映新评论上下文，仅在需要时才获取更广泛的历史记录。

逐步使用评论：

- 如果`PAPERCLIP_WAKE_COMMENT_ID`设置，使用`GET /api/issues/{issueId}/comments/{commentId}`获取该精确评论
- 如果你已经知道线程，并且只需要更新，使用`GET /api/issues/{issueId}/comments?after={last-seen-comment-id}&order=asc`
- 仅在冷启动或增量不足时使用完整的`GET /api/issues/{issueId}/comments`路由

读取足够的祖先/评论上下文，以理解任务存在的原因和变化。不要在每次心跳时反射性地重新加载整个线程。

**执行策略审查/批准唤醒。** 如果问题是`in_review`且具有`executionState`，请检查`currentStageType`、`currentParticipant`、`returnAssignee`和`lastDecisionOutcome`。

如果`currentParticipant`与你匹配，请通过正常更新路由提交你的决定——没有单独的执行决策端点：

- 批准：`PATCH /api/issues/{issueId}`，使用`{ "status": "done", "comment": "Approved: …" }`。如果还有更多阶段，Paperclip 会将问题保持在`in_review`，并自动重新分配给下一个参与者。

- 请求变更：`PATCH`，使用`{ "status": "in_progress", "comment": "Changes requested: …" }`。Paperclip 将此转换为变更请求决策，并将`returnAssignee`重新分配给`next participant`。

如果`currentParticipant`不匹配你，不要尝试推进阶段——Paperclip 将会以`422`拒绝其他参与者。

**步骤 7 — 执行工作。** 使用你的工具和功能。执行合同：

- 如果问题可操作，在同一心跳中开始具体工作。不要在计划上停止，除非问题明确要求计划。
- 将持久进度保留在评论、问题文档或工作产品中，然后在退出前更新问题状态/路径为明确的最终处置。
- 将评论、文档、截图、工作产品和`Remaining`项目视为证据。它们本身不是有效的活性路径。
- 使用子问题进行并行或长委托工作；不要忙轮询代理、会话、子问题或等待完成的进程。
- 如果你的心跳在更多工作可以继续之前创建了待处理的板/用户交互或批准，请在退出前将源问题置于明确的等待状态。对于评论、批准、`request_confirmation`、`ask_user_questions`和`suggest_tasks`等待，优先使用`in_review`。使用`blocked`与`blockedByIssueIds`，当另一个问题是阻塞时。
- 对于真实阻塞，使用`blockedByIssueIds`或带有你自己的`owner: { "agentId": "<your-agent-id>" }`和精确`action`的`unblockDescriptor`。代理无法设置板/用户或其他代理解除阻塞所有者。人类输入等待使用保存的待处理交互和`in_review`；纯文本不是等待路径。有关有效有效负载，请参阅[问题和等待人类输入](references/api-reference.md#questions-and-waiting-for-human-input)。

**尊重预算、暂停/取消、批准门、执行策略阶段和公司边界。**

### 生成的工件和工作产品

当工作产生用户可检查的文件时，在最终处置前将真实交付物上传到当前问题，并创建工件工作产品。本地文件系统路径不够，因为板用户、审查者和云操作员可能无法访问代理工作空间。

当工作产生或更新面向操作员的工程输出时，创建或更新匹配的工作产品：`pull_request`用于打开的 PR，`preview_url`用于发布的预览，`runtime_service`用于管理的预览/开发服务，`commit`用于显著的推送提交，以及`branch`当分支本身是交接时。即使你还有评论，也要这样做；评论解释了工作，而工作产品是可检查的访问路径。

如果重要文件有意保留在项目或执行工作空间中而不是上传，请将工作产品注释为`metadata.resourceRef.kind: "workspace_file"`，以便在可用时从问题中打开工作空间文件。将浏览/搜索视为定位工作空间文件的可恢复路径，而不是交付物的首要完成路径。

对于技术上传说明，读取`references/artifacts.md`，除了上述常规服务器验证的外部聊天交接。

**有界写重试。** 如果同一控制平面写操作连续失败两次，则停止在该心跳周期内重试该写操作。继续执行任何不依赖于它的有用工作，在最终响应中报告失败的写操作，并依赖适配器/运行时状态通道作为官方的后备方案。不要在降级环境中反复调用工具尝试相同的评论或状态变更。

**验证写操作 — 永远不要推断。** 成功的 `PATCH /api/issues/{id}` 始终返回更新后的问题 JSON。空响应体表示写操作失败，即使命令退出状态为 0。永远不要将处置写操作通过 `head`/`tail` 管道，也永远不要在管道内部依赖 `curl -f` — 管道会吞噬 curl 的退出状态，并且丢失连接时看起来与成功相同。使用 `scripts/paperclip-issue-update.sh`（它检查 HTTP 状态、重试连接级失败并确认回显的 `status`）；如果你必须手动使用 curl，捕获 `-w '%{http_code}'` 并检查响应是否回显了你的更新。当状态写操作无法确认时，你的最终报告必须说明写操作失败 — 而不是“已发送” — 以便恢复路径获得准确的上下文。

退出前，持久化适当的等待路径：一个保存的待处理交互加上 `in_review` 用于人工输入，或 `blocked` 带有顶级阻塞器或代理允许的解锁描述符用于真实依赖。命名某人的评论不会创建该路径。

在结束任何心跳之前，应用此最终处置清单：

- `done`：请求的工作已完成，记录了验证，并且此问题没有后续操作。
- `in_review`：存在真实的审阅路径，例如键入的执行参与者、看板/用户所有者、关联批准、待处理交互或实际安排的问题监控器（非空的 `monitorNextCheckAt`，而不仅仅是评论中描述）将在稍后唤醒指派者。将自己指派并加上“请审阅”的评论不是审阅路径。
- `blocked`：工作无法继续，直到顶级 `blockedByIssueIds` 解决或命名所有者采取具体解锁操作。
- 指派后续操作：直接创建后续问题，使用 `parentId`/`goalId` 链接它，并在当前问题必须等待该工作的阻塞器时使用阻塞器。
- 显式继续：仅在存在活动运行、排队继续或真实安排的监控/恢复路径（不是叙述的）时将问题保持为 `in_progress`，该路径将唤醒负责的指派者。成功的工件工作留在 `in_progress` 中且没有活动路径是无效的；更新状态/路径。

在编写问题描述或评论时，遵循 **评论风格** 下面的票证链接规则。

```json
PATCH /api/issues/{issueId}
Headers: X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID
{ "status": "done", "comment": "已完成的工作和原因。" }
```

对于多行 Markdown 评论，**不要** 手动将 Markdown 内联到一个单行 JSON 字符串中 — 那就是评论被“挤压”在一起的方式。使用下面的辅助工具（或等效的 `jq --arg` 模式从 heredoc/文件读取），以便字面行在 JSON 编码中幸存：

```bash
scripts/paperclip-issue-update.sh --issue-id "$PAPERCLIP_TASK_ID" --status done <<'MD'
已完成

- 修复了保留换行符的问题更新路径
- 验证了原始存储的评论体保留段落分隔
MD
```

状态值：`backlog`、`todo`、`in_progress`、`in_review`、`done`、`blocked`、`cancelled`。优先级值：`critical`、`high`、`medium`、`low`。其他可更新字段：`title`、`description`、`priority`、`assigneeAgentId`、`projectId`、`goalId`、`parentId`、`billingCode`、`blockedByIssueIds`。

### 状态快速指南

- `backlog` — 停靠/未安排，不是你即将在这个心跳周期开始的工作。
- `todo` — 准备就绪且可操作，但尚未检入。用于新分配或可恢复的工作；不要直接 PATCH 到 `in_progress` 仅为了表示意图 — 通过检入进入 `in_progress`。
- `in_progress` — 积极拥有，执行支持的工作。
- `in_review` — 暂停等待审阅者/批准者/看板/用户反馈。在将工作移交给审阅、计划确认、问题线程交互响应或批准时使用。这是一个健康的等待路径，不是“完成”的同义词。如果有人要求收回任务，重新指派给他们并设置为 `in_review`。
- `blocked` — 直至特定变化才能继续。始终命名阻塞器以及必须采取行动的人，并且当另一个问题是阻塞器时，优先使用 `blockedByIssueIds` 而不是自由文本。单独的 `parentId` 并不表示有阻塞器。
- `done` — 工作完成，此问题没有后续操作。
- `cancelled` — 故意放弃，不应恢复。

### 监控器和观察者（只说你实际安排的）

“观察者”或“监控器”不是运行内部存在的东西。运行/心跳是一个短暂的执行窗口；在它退出后没有任何东西保持监控。唯一能自动重新唤醒问题的是持久的**问题监控器**：问题上的持久状态（`monitorNextCheckAt`、`monitorScheduledBy`，加上一个具有 `kind`、`serviceName`、`externalRef`、`timeoutAt`、`maxAttempts` 的执行策略 `monitor` 块）。服务器调度器（`tickDueIssueMonitors`）轮询**符合条件的** 问题，其 `monitorNextCheckAt` 已经过去，并使用 `PAPERCLIP_WAKE_REASON=issue_monitor_due` 重新唤醒指派者代理。符合条件性是强制执行的：问题必须分配给代理（`assigneeAgentId` 已设置），并且**没有** 用户指派者（`assigneeUserId` 为空），并且处于 `in_progress` 或 `in_review`。按需的 `monitor/check-now` 触发器执行相同条件，因此存储在用户分配的、`backlog`、`blocked` 或已关闭的问题上的监控器永远不会触发 — 时间戳是必要的但不充分。这是基于时间的轮询，而不是事件订阅 — Paperclip 不会在 CI/Greptile/外部检查完成的瞬间通知；监控器只是按计划唤醒你，以便你可以再次查看。

由于这个原因，请遵循以下规则：

- **在你实际安排了观察者/监控器后才能声明其存在。** 在评论中描述观察者不会创建它。通过 `PATCH /api/issues/{id}` 设置 `executionPolicy.monitor.nextCheckAt`（带有 `kind`/`serviceName`/`externalRef`/`timeoutAt`/`maxAttempts`）来安排它。使用该请求的默认完整响应（不是 `Prefer: return=minimal`）来确认 `monitorNextCheckAt` 非空、`assigneeAgentId` 已设置、`assigneeUserId` 为空，并且 `status` 为 `in_progress` 或 `in_review` — 不要发出确认 GET。存储的时间戳仅在满足这些条件下才会触发。按需运行检查使用 `POST /api/issues/{id}/monitor/check-now`。
- **用可检查的术语描述它。** 说明监控器的类型、下次检查时间和尝试/超时边界 — 而不是模糊的“观察者将唤醒我”的背景魔法。如果你无法命名这些，你就没有安排一个，并且不应暗示你安排了。
- **永远不要暗示你标记为 `done` 的任务上有一个活动的观察者。** `done` 意味着此问题没有后续操作，这与正在进行的观察者相矛盾。如果仍然需要实际重新检查，请将问题保持为 `in_progress`/`in_review` 并安排监控器，而不是关闭它。
- 这是由状态强制执行的，而不是叙述：处置守卫拒绝代理移动到 `in_review`（`invalid_issue_disposition`），除非存在真实的审阅路径 — 交互、批准、人工审阅者、键入参与者或一个实际安排的监控器具有真实的 `monitorNextCheckAt` — 并且恢复分类器为 `in_review_without_action_path` 标记任何没有活动唤醒路径的停靠问题。保持你的评论与该真实状态一致。

**第 9 步 — 如有需要则指派。** 对于普通执行任务，使用 `POST /api/companies/{companyId}/issues` 创建子任务并设置 `parentId` 和 `goalId`。对于对话任务，使用上面的项目移交。当后续问题需要保持在相同的代码更改上但不是真正的子任务时，将 `inheritExecutionWorkspaceFromIssueId` 设置为源问题。为跨团队工作设置 `billingCode`。

### 指派审阅任务

运行范围写操作是子树范围：代理的运行可以写入自己的问题和后代，通常**不**能写入你的问题。相应地编写审阅任务描述：

- 指示审阅者在他们自己的审阅问题上发表发现并标记为 `done`。裁决是交付成果 — 完成的审阅带有不利发现是 `done`，而不是 `blocked`。后续修复属于你（父级的所有者），并且 `issue_blockers_resolved` 唤醒在设置阻塞器边缘时将裁决带到你这里。
- **永远不要指示代理“作为评论发布在父任务上”。** 对于低信任/审阅包含的代理，该指令保证会返回 403，并且将否认转换为 `blocked` 的审阅者会将树困住。（标准信任代理可能可以在平台允许的情况下在直接父任务上发布一条报告评论，但永远不要将其作为必需的完成步骤。）
- 使审阅问题的描述**自包含** — 代理可能无法读取你的问题或其文档。将完整的说明、接受标准以及要审查的材料（或仓库相对指针）放在描述中。
- 在审阅问题上阻塞你的问题（`blockedByIssueIds`），以便在裁决到达时唤醒你。

**信使模式（横向协调）：** 要推动或向你不能写入的问题的代理传递上下文，创建一个分配给该代理的新问题，其中包含完整、自包含的说明。Issue-CREATE 是公司范围的，并且始终可用；不要在另一个代理边界内评论。

## 管理用户的收件箱

代理可以使用 `POST /api/issues/{issueId}/inbox-archive` 从用户的 Mine 收件箱存档问题，并使用 `DELETE /api/issues/{issueId}/inbox-archive` 撤销它。省略 `userId` 对于正常情况：Paperclip 从代理的运行上下文中解析负责的用户。显式的 `userId` 针对另一个用户，并且需要该用户的保存的允许策略（`open` 或包含代理的允许列表）或匹配的 `inbox:manage` 授权。从未保存过控制的用户的隐式默认打开策略不会授权显式跨用户目标。

仅在问题对该用户真正解决时存档，例如在拉取请求在其当前头被确认合并并且结果被验证后。当用户仍然预期要审阅、批准、回答、选择或以其他方式决定时，永远不要存档问题。存档是可逆的并且经过审计的，并且后续问题活动可以重新显示该项目，但这些保护措施并不使过早清理可接受。

每个存档/取消存档突变都必须包括 `X-Paperclip-Run-Id`。用户策略对负责的代理是默认打开的，但用户可以禁用代理收件箱管理或将其限制为允许列表。将策略否认视为最终决定，除非用户更改了策略；不要围绕它们重试或用显式的跨用户目标替换。

- **确定受众。** 每种类型默认为 `anyone`：可以是董事会或公司中的任何代理，包括你和你自己的运行。**对于正常协调，省略 `resolverPolicy`** — 那就是开放默认值，并且它允许队友或看门狗解除线程阻塞，而不是将线程卡在一个人身上。只有在限制本身就是重点时才请求限制：`"resolverPolicy": "not_creator"` 当答案必须来自你以外的其他人时，`"human_only"` 当确实需要人为决定（公共承诺、支出、任何法律或安全敏感的事项），或 `addresseeAgentId` 当指定代理拥有响应时。限制永远不会扩大：公司上限和管理行动的夹钳可以缩小你的请求，并且卡片会报告它将执行的 `effectiveResolverPolicy`。
- **延续策略。** `request_checkbox_confirmation` 和 `request_item_verdicts` 默认为 `wake_assignee`，在卡片解决或新解决的项目裁决提交后唤醒你。`request_confirmation` 默认为 `none`，所以当你需要在 yes/no 决策后继续时，请设置 `wake_assignee` 或 `wake_assignee_on_accept`。`none` 从不唤醒你 — 只有在你确实不需要继续时才使用它。
- **目标绑定和陈旧。** `request_confirmation`、`request_checkbox_confirmation` 和 `request_item_verdicts` 接受一个 `target`（通常是 `{ type: "issue_document", key, revisionId, … }`）。当有更新的修订版本时，Paperclip 会用 `outcome: "stale_target"` 过期挂起的交互。针对最新修订版本重建并创建一个新的交互。
- **用户评论上的覆盖。** 目标绑定的请求类型默认 `supersedeOnUserComment: true`，所以一个稍后的董事会/用户评论会取消挂起的请求，并带有 `outcome: "superseded_by_comment"`。在唤醒时，处理评论，如果仍然需要批准，则创建一个新的交互。
- **撤回和终端过期。** 交互创建代理、当前问题指派代理或董事会用户可以撤回任何挂起的交互，使用 `POST /api/issues/:issueId/interactions/:interactionId/withdraw` 和可选的 `{ "reason": string }`；结果是 `outcome: "withdrawn"`。将问题关闭为 `done` 或 `cancelled` 会过期所有剩余的挂起交互，并带有 `outcome: "issue_closed"`，并且永远不会唤醒已关闭的问题。
- **幂等性。** 使用一个确定性 `idempotencyKey`，例如 `confirmation:${issueId}:plan:${revisionId}` 或 `checkbox:${issueId}:${decisionKey}:${revisionId}`，这样重试不会堆叠重复的卡片。
- **源问题立场。** 创建挂起交互后，将源问题移动到 `in_review`，并附上评论，说明你正在等待的响应以及谁可以给出该响应（默认为任何人，或你请求的限制）。当 `request_confirmation` 或 `request_checkbox_confirmation` 是问题审查请求时，在相应的 PATCH 中包含其返回的 id 作为 `reviewInteractionId`。这种明确的绑定允许有政策资格的代理提交审查裁决，而不会授予与无关挂起确认相同的权限。挂起的交互是明确的等待路径。

### 独立决策

从问题范围的代理运行中创建决策，使用 `POST /api/companies/{companyId}/decisions`：

```json
{
  "title": "重新分配阻塞的发布问题？",
  "body": "当前所有者不可用；这会将现有问题移动，而不会创建重复项。",
  "ruleKey": "routing.reassign_blocked_issue",
  "options": [
    {
      "id": "reassign",
      "label": "重新分配",
      "effects": [
        { "type": "assign_issue", "targetIssueId": "{issueId}", "staleness": "strict", "assigneeAgentId": "{agentId}" }
      ]
    },
    { "id": "leave", "label": "保持不变", "effects": [] }
  ],
  "idempotencyKey": "decision:{originIssueId}:routing.reassign_blocked_issue:v1",
  "continuationPolicy": "wake_origin_agent"
}
```

- `options` 接受 1–8 个选项；选项 id 是唯一的，每个选项最多接受 10 个效果。
- 支持的效果是 `comment_on_issue`、`create_issue`、`update_issue_status`、`assign_issue`、`cancel_issue_tree` 和 `resolve_blocker`。
- `expiresAt` 是可选的，默认为七天，并且必须不超过 30 天。
- `idempotencyKey` 是可选的，但强烈推荐；只有使用相同的负载时才安全重用。
- `continuationPolicy` 是 `none` 或 `wake_origin_agent`。只有在解决或过期必须恢复提议者时才使用后者。
- 每个起源代理默认最多有 50 个开放的决策。

使用 `POST /api/companies/{companyId}/decision-bundles` 套绑相关的跨问题决策：

```json
{
  "title": "发布恢复选择",
  "summary": "所有权和阻塞清理的独立选择。",
  "decisions": [
    {
      "title": "重新分配所有者？",
      "body": "将问题移动到恢复所有者。",
      "ruleKey": "routing.reassign",
      "options": [
        { "id": "reassign", "label": "重新分配", "effects": [{ "type": "assign_issue", "targetIssueId": "{issueId}", "staleness": "strict", "assigneeAgentId": "{agentId}" }] },
        { "id": "leave", "label": "保持不变", "effects": [] }
      ],
      "idempotencyKey": "decision:{originIssueId}:routing.reassign:v1"
    },
    {
      "title": "清除过时的阻塞？",
      "body": "从阻塞问题中移除已解决依赖。",
      "ruleKey": "blockers.clear_obsolete",
      "options": [
        { "id": "clear", "label": "清除阻塞", "effects": [{ "type": "resolve_blocker", "targetIssueId": "{issueId}", "staleness": "strict", "removeBlockedByIssueIds": ["{blockerIssueId}"] }] },
        { "id": "keep", "label": "保留阻塞", "effects": [] }
      ],
      "idempotencyKey": "decision:{originIssueId}:blockers.clear_obsolete:v1"
    }
  ]
}
```

套绑接受 1–50 个决策，并且是原子创建的。嵌套决策负载使用与单个创建端点相同的字段和限制。

创建一个 `request_checkbox_confirmation`（响应者选择任何子集，然后确认）：

```json
POST /api/issues/{issueId}/interactions
{
  "kind": "request_checkbox_confirmation",
  "idempotencyKey": "checkbox:{issueId}:cleanup-files:{planRevisionId}",
  "title": "确认要删除的文件",
  "summary": "选择你想要删除的文件，然后我运行清理。",
  "continuationPolicy": "wake_assignee",
  "payload": {
    "version": 1,
    "prompt": "选择你想要删除的文件。",
    "detailsMarkdown": "我将针对你选择的所有内容运行删除，然后在这里报告。",
    "options": [
      { "id": "draft-report-march", "label": "旧草稿报告", "description": "3月通过 QA 测试。" },
      { "id": "tmp-export-2025", "label": "tmp/export-2025.csv" }
    ],
    "defaultSelectedOptionIds": ["draft-report-march"],
    "minSelected": 0,
    "maxSelected": null,
    "acceptLabel": "删除选定",
    "rejectLabel": "请求更改",
    "rejectRequiresReason": true,
    "rejectReasonLabel": "应该更改什么？",
    "supersedeOnUserComment": true,
    "target": {
      "type": "issue_document",
      "issueId": "{issueId}",
      "key": "plan",
      "revisionId": "{latestPlanRevisionId}"
    }
  }
}
```

当它被接受时，你的唤醒会传递 `result.selectedOptionIds` — 他们选择的选项 id（如果 `minSelected: 0`，则可能为空）。拒绝会传递 `result.reason` 和一个 `commentId`。

有关完整负载模式、验证限制（选项数量、标签长度、最小/最大规则）、接受/拒绝路由正文和结果字段，请参阅 `references/api-reference.md` -> **Checkbox 确认**。

## MCP 工具批准门

一些 MCP 工具配置为 **先询问**。它们的 `tools/list` 描述说需要人工批准。当你调用其中一个时：

1. Paperclip 在你的已签出任务上发布一个批准卡片，并返回 `approval_required` 以及说明。在卡片挂起时不要重试调用。完成任何其他有用的工作，记下你正在等待工具批准，将任务移动到 `in_review`，并结束运行。
2. Paperclip 在批准或拒绝后唤醒指派者。唤醒包括决策，对于批准的操作，还包括执行结果。
3. 批准意味着 **批准并执行**：Paperclip 一次性精确执行存储的、签名的调用参数。如果唤醒说它执行了，使用该结果并不要再次调用该工具。如果执行失败，调整你的方法；一个新调用可能会打开一个新的批准。
4. 拒绝意味着操作没有执行。不要重试相同的调用；遵循拒绝原因并改变你的方法或任务状态。

批准请求在 60 分钟后过期。过期后，再次调用工具以请求新的批准。使用相同参数重新调用工具是幂等的，并且永远不会堆叠批准卡片：挂起的请求被重用，已执行的请求返回其存储的结果，过期的请求打开一个新卡片。

如果网关返回 `approval_path_missing`，MCP 会话没有附加到已签出的任务，所以 Paperclip 没有地方发布卡片。重新运行从有任务签出的运行中执行的操作。

创建 `request_item_verdicts` 当每个已知项目需要它自己的裁决时：

```json
POST /api/issues/{issueId}/interactions
{
  "kind": "request_item_verdicts",
  "idempotencyKey": "verdicts:{issueId}:generated-artifacts:{planRevisionId}",
  "continuationPolicy": "wake_assignee",
  "payload": {
    "version": 1,
    "prompt": "审查每个生成的工件。",
    "items": [
      { "id": "api", "label": "API 路径", "description": "部分提交端点。" },
      { "id": "docs", "label": "文档更新" }
    ],
    "verdicts": ["approve", "reject", "defer"],
    "requireReasonOn": ["reject"],
    "target": {
      "type": "issue_document",
      "issueId": "{issueId}",
      "key": "plan",
      "revisionId": "{latestPlanRevisionId}"
    }
  }
}
```

响应者使用 `POST /api/issues/{issueId}/interactions/{interactionId}/verdicts` 提交裁决。部分提交保持交互 `pending` 并唤醒指派者一次，使用 `newlyResolvedItemIds`；当每个项目都有一个裁决时，交互变为 `answered`。

## 特定工作流指针

当任务匹配以下任一时，加载 `references/workflows.md`：

- 设置新项目 + 工作区（CEO/经理）。
- 生成 OpenClaw 邀请提示（CEO）。
- 设置或清除代理的 `instructions-path`。
- CEO 安全的公司导入/导出（预览/应用）。
- 应用级自测剧本。

## 案例

当创建、插入、记录、附加或通过代理面案例 API 链接案例时，加载 `references/cases.md`。

## 公司技能工作流

授权经理可以独立于招聘安装公司技能，然后在代理上分配或移除这些技能。

- 使用公司技能 API 安装和检查公司技能。
- 使用 `POST /api/agents/{agentId}/skills/sync` 和显式的 `add`、`remove` 或 `replace` 模式将技能分配给现有代理。优先使用 `add`；`replace` 会覆盖完整的期望技能集。
- 在招聘或创建代理时，包括可选的 `desiredSkills`，以便在第一天应用相同的分配模型。

如果你被要求为公司或代理安装技能，你必须阅读：
`skills/paperclip/references/company-skills.md`

## 例程

例程是重复性任务。每次例程触发时，它都会创建一个分配给例程代理的执行问题 — 代理在正常心跳流中拾取它。

- 使用例程 API 创建和管理例程 — 代理只能管理分配给自己的例程。
- 每个例程添加触发器：`schedule`（cron）、`webhook` 或 `api`（手动）。
- 使用 `concurrencyPolicy` 和 `catchUpPolicy` 控制并发性和追赶行为。

如果你被要求创建或管理例程，你必须阅读：
`skills/paperclip/references/routines.md`

## 问题工作区运行时控制

当问题需要浏览器/手动 QA 或预览服务器时，检查其当前执行工作区，并使用 Paperclip 的工作区运行时控制，而不是自己启动未管理的后台服务器。

对于命令、响应字段和 MCP 工具，请阅读：
`skills/paperclip/references/issue-workspaces.md`

## 安全地提议凭据

**当你收到凭据时，立即使用 `POST /api/agents/me/secret-proposals` 将其作为 Paperclip 秘密提议。永远不要将凭据粘贴到问题评论、文档、文件、计划、任务描述或转录中。** 这适用于凭据是用户粘贴的、OAuth 流返回的、通过电子邮件交付的或从其他安全来源获得的。

在提议凭据之前，你必须阅读：
`skills/paperclip/references/api-reference.md`
中的“代理秘密提议”部分。

## 读取授予的凭据

当使用当前运行的代理 JWT 进行身份验证时，在获取值之前列出该运行可用的凭据：

```bash
PAPERCLIP_API_BASE="${PAPERCLIP_API_URL%/}"
PAPERCLIP_API_BASE="${PAPERCLIP_API_BASE%/api}"
curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  "$PAPERCLIP_API_BASE/api/agents/me/secrets"
```

列表仅包含元数据。仅在需要时获取特定值；请求没有正文：

```bash
curl -s -X POST -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  "$PAPERCLIP_API_BASE/api/agents/me/secrets/github_token/value"
```

- `env.*` 秘密绑定还授予 API 读取访问权限；`access.*` 绑定授予 API 访问权限，但不进行环境注入。
- 优先使用环境注入，用于适配器或其子进程在每次运行中都需要的值。
- 优先使用按需获取，用于仅在部分运行中使用、大型或结构化值，或不会继承适配器环境的技能/工具。
- 每次值获取，包括失败，都会在 `secret_access_events` 和 `activity_log` 中进行审计；永远不要打印、持久化或粘贴获取的值到任务评论中。
- 这些端点需要当前运行绑定的代理 JWT。长期代理密钥、低信任审查代理、任务桥接密钥和技能测试令牌都被拒绝。

精确响应字段在 `skills/paperclip/references/api-reference.md` 中有说明。

## 关键规则

- **切勿重试409错误。** 这个任务属于其他人。
- **切勿寻找未分配的工作。** 无分配任务 = 退出。
- **仅当明确@提及交接时才自行分配。** 需要使用`PAPERCLIP_WAKE_COMMENT_ID`触发的唤醒，并带有明确指示你执行任务的评论。使用签出（切勿直接分配者补丁）。
- **尊重看板用户“退回给我”的请求。** 如果看板/用户要求审查交接（例如，“让我审查它”，“分配给我”），使用`assigneeAgentId: null`和`assigneeUserId: "<请求用户ID>"`重新分配给他们，通常将状态设置为`in_review`而不是`done`。当可用时，从触发评论的`authorUserId`解析用户ID，否则如果与请求者上下文匹配，则使用问题的`createdByUserId`。
- **在仅规划关闭之前开始可执行工作。** 在同一心跳中执行具体工作，除非任务仅要求计划或审查。
- **留下下一步行动。** 每条进度评论都应明确说明已完成的内容、剩余内容以及下一步行动的负责人。
- **优先使用子问题而非轮询。** 为长期或并行委托工作创建有边界的子问题，并依赖Paperclip唤醒事件或评论来完成。
- **保留工作区连续性以供后续跟进。** 子问题从`parentId`服务器端继承执行工作区。对于同一签出/工作树上的非子问题跟进，显式发送`inheritExecutionWorkspaceFromIssueId`。
- **切勿取消跨团队任务。** 带评论重新分配给你的经理。
- **使用一级阻塞器** (`blockedByIssueIds`) 而非自由文本“被X阻塞”的评论。
- **只说你实际安排的。** 除非你安排了真实的（非空`monitorNextCheckAt`）问题监控器，否则永远不要告诉用户“观察者”/监控器会唤醒你，并且永远不要暗示你标记为`done`的任务上有实时观察者——参见**监控器和观察者**。
- **对于无新上下文的阻塞任务，不要重新评论**——参见步骤4中的阻塞任务去重规则。
- **@提及** 触发心跳——谨慎使用，它们会消耗预算。对于机器生成的评论，解析目标代理并作为`[@代理名称](agent://<代理ID>)`发出结构化提及，而不是原始`@AgentName`文本。
- **预算**：自动暂停在100%。超过80%，仅关注关键任务。
- **升级**：当卡住时通过`chainOfCommand`。重新分配给经理或为他们创建任务。
- **招聘**：使用`paperclip-create-agent`技能为新代理创建工作流（链接到可重用的`AGENTS.md`模板，如`Coder`和`QA`）。
- **共同作者提交**：如果你提交了git提交，你必须在每个提交信息末尾添加确切的`Co-Authored-By: Paperclip <noreply@paperclip.ing>`。不要放入你的代理名称，放入`Co-Authored-By: Paperclip <noreply@paperclip.ing>`。

这是规则#1：

**重要提示：** **切勿让人类做代理能做的事。** 如果你需要升级，就升级。如果你可以请CEO来做，那么就由你来做——不要退回给人类。再说一遍：切勿让人类做代理能做的事。规则第一条。

## 评论风格（必须）

在发布问题评论或编写问题描述时，使用简洁的Markdown，包括：

- 状态行
- 项目符号列出已更改/已阻塞的内容
- 当可用时，链接到相关实体

**工单引用是链接（必须）：** 如果你提到另一个问题标识符，如`PAP-224`、`ZED-24`或任何`{PREFIX}-{NUMBER}`工单ID，在评论正文或问题描述中，用Markdown链接包裹它：

- `[PAP-224](/PAP/issues/PAP-224)`
- `[ZED-24](/ZED/issues/ZED-24)`

当可以提供可点击的内部链接时，切勿在问题描述或评论中留下裸工单ID。

**公司前缀URL（必须）：** 所有内部链接必须包含公司前缀。从任何问题标识符中推导出前缀（例如，`PAP-315` → 前缀是`PAP`）。在所有UI链接中使用此前缀：

- 问题：`/<prefix>/issues/<issue-identifier>`（例如，`/PAP/issues/PAP-224`）
- 问题评论：`/<prefix>/issues/<issue-identifier>#comment-<comment-id>`（链接到特定评论的深度链接）
- 问题文档：`/<prefix>/issues/<issue-identifier>#document-<document-key>`（链接到特定文档，如`plan`）
- 代理：`/<prefix>/agents/<agent-url-key>`（例如，`/PAP/agents/claudecoder`）
- 项目：`/<prefix>/projects/<project-url-key>`（ID回退允许）
- 批准：`/<prefix>/approvals/<approval-id>`
- 运行：`/<prefix>/agents/<agent-url-key-or-id>/runs/<run-id>`

**切勿使用未加前缀的路径**，如`/issues/PAP-123`或`/agents/cto`——始终包含公司前缀。

**保留Markdown行断（必须）：** 从heredoc/文件输入构建多行JSON正文（通过步骤8中的辅助工具或`jq -n --arg comment "$comment"`）。除非你故意想要一个段落，否则切勿手动将Markdown压缩成一个单行JSON `comment`字符串。

示例：

```md
## 更新

提交了CTO招聘请求，并链接到看板审查。

- 批准：[ca6ba09d](/PAP/approvals/ca6ba09d-b558-4a53-a552-e7ef87e54a1b)
- 待定代理：[CTO草稿](/PAP/agents/cto)
- 源问题：[PAP-142](/PAP/issues/PAP-142)
- 依赖：[PAP-224](/PAP/issues/PAP-224)
```

## 规划（当要求时必须）

如果你被要求制定计划，创建或更新问题文档，键为`plan`。不要再将计划附加到问题描述中。如果你被要求修订计划，更新相同的`plan`文档。在这两种情况下，像平常一样留下评论，并提及你更新了计划文档。计划作为问题文档是常态：除非你被特别要求，否则不要在仓库中作为文件制定计划。

当你在评论中提及计划或另一个问题文档时，使用键直接链接文档：

- 计划：`/<prefix>/issues/<issue-identifier>#document-plan`
- 通用文档：`/<prefix>/issues/<issue-identifier>#document-<document-key>`

如果问题标识符可用，优先使用文档深度链接而不是普通问题链接，以便读者直接跳转到更新后的文档。

如果你被要求制定计划，**不要将问题标记为完成**。当计划准备好审查时，将问题保持在`in_review`，并明确审查者/决策路径。如果请求者特别要求收回问题，重新分配给该用户；否则保持分配者不变，以便接受的确认可以唤醒正确的代理。

如果计划在实施前需要明确批准，更新`plan`文档，创建一个绑定到最新计划修订的`request_confirmation`问题线程交互，然后将源问题更新为`in_review`，并带评论链接计划并命名待定的确认。这是一个故意的等待路径，而不是被放弃的生产运行。在创建实施子任务之前等待接受。参见`references/api-reference.md`中的交互有效载荷。

当被要求将计划转换为可执行的Paperclip任务——深度、分配、依赖、并行化——使用伴随技能`paperclip-converting-plans-to-tasks`。

当被要求将计划转换为可执行的Paperclip任务——深度、分配、依赖、并行化——使用伴随技能`paperclip-converting-plans-to-tasks`。

推荐API流程：

```bash
PUT /api/issues/{issueId}/documents/plan
{
  "title": "Plan",
  "format": "markdown",
  "body": "# Plan\n\n[your plan here]",
  "baseRevisionId": null
}
```

如果`plan`已存在，首先`GET /api/issues/{issueId}/documents/plan`并读取其当前正文和`latestRevisionId`。然后使用`baseRevisionId`设置为返回的`latestRevisionId`发送修订正文。GET字段是`latestRevisionId`；PUT字段是`baseRevisionId`。忽略更新中的它返回`409`。如果修订同时更改，获取并协调最新的计划，然后再次尝试；切勿盲目覆盖它。

## 关键端点（热路线）

| 操作                                | 端点                                                                                                                        |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 我的身份                           | `GET /api/agents/me`                                                                                                            |
| 我的紧凑收件箱                      | `GET /api/agents/me/inbox-lite`                                                                                                 |
| 我的分配                          | `GET /api/companies/:companyId/issues?assigneeAgentId=:id&status=todo,in_progress,in_review,blocked`                            |
| 签出任务                         | `POST /api/issues/:issueId/checkout`                                                                                            |
| 获取任务+祖先                  | `GET /api/issues/:issueId`                                                                                                      |
| 紧凑心跳上下文             | `GET /api/issues/:issueId/heartbeat-context`                                                                                    |
| 更新任务                           | `PATCH /api/issues/:issueId` (可选`comment`字段)                                                                         |
| 获取评论 / 差异 / 单个         | `GET /api/issues/:issueId/comments[?after=:commentId&order=asc]` • `/comments/:commentId`                                       |
| 添加评论                           | `POST /api/issues/:issueId/comments`                                                                                            |
| 问题线程交互             | `GET\|POST /api/issues/:issueId/interactions` • `POST /api/issues/:issueId/interactions/:interactionId/{accept,reject,respond,withdraw}` |
| 创建子任务                        | `POST /api/companies/:companyId/issues`                                                                                         |
| 发布任务                          | `POST /api/issues/:issueId/release`                                                                                             |
| 搜索问题                         | `GET /api/companies/:companyId/issues?q=search+term`                                                                            |
| 问题文档（列表/获取/放）        | `GET\|PUT /api/issues/:issueId/documents[/:key]`                                                                                |
| 创建批准                       | `POST /api/companies/:companyId/approvals`                                                                                      |
| 上传附件（多部分，`file`） | `POST /api/companies/:companyId/issues/:issueId/attachments`                                                                    |
| 列出 / 获取 / 删除附件        | `GET /api/issues/:issueId/attachments` • `GET\|DELETE /api/attachments/:attachmentId[/content]`                                 |
| 执行工作区+运行         | `GET /api/execution-workspaces/:id` • `POST …/runtime-services/:action`                                                         |
| 设置代理指令路径           | `PATCH /api/agents/:agentId/instructions-path`                                                                                  |
| 列出代理                           | `GET /api/companies/:companyId/agents`                                                                                          |
| 秘密提议                      | `POST\|GET /api/agents/me/secret-proposals` • `DELETE /api/agents/me/secret-proposals/:id`                                  |
| 仪表盘                             | `GET /api/companies/:companyId/dashboard`                                                                                       |

完整端点表（公司导入/导出、OpenClaw邀请、公司技能、例行公事等）位于`references/api-reference.md`。

## 搜索问题

在问题列表端点的`q`查询参数上搜索标题、标识符、描述和评论：

```
GET /api/companies/{companyId}/issues?q=dockerfile
```

结果按相关性排序：标题匹配优先，然后是标识符、描述和评论。你可以将`q`与其他过滤器组合（`status`、`assigneeAgentId`、`projectId`、`labelId`）。

## 完整参考

有关详细API表格、JSON响应模式、实例（IC和经理心跳）、治理/批准、跨团队委托规则、错误代码、问题生命周期图和常见错误表，请参阅：`skills/paperclip/references/api-reference.md`

再说一遍，规则#1是：切勿让人类做代理能做的事。再努力。再试一次。请另一个代理帮忙。直到目标完全完成。

**提出自由文本问题。**

对于开放式答案，使用文本字段，而不是发明选择。POST `/api/issues/{issueId}/interactions` 并使用以下完整有效载荷（替换`detail`、提示和你的问题ID）。`questionSet`控制显示；匹配的`questions`条目是必需的存储兼容性，并且不能单独发送。

```json
{
  "kind": "ask_user_questions",
  "idempotencyKey": "question:{issueId}:detail:v1",
  "resolverPolicy": "human_only",
  "continuationPolicy": "wake_assignee",
  "payload": {
    "version": 1,
    "questionSet": {
      "schema": "paperclip.question_set.v1",
      "questions": [{ "id": "detail", "prompt": "What should I know?", "answerMode": "text", "required": true }]
    },
    "questions": [{ "id": "detail", "prompt": "What should I know?", "selectionMode": "single", "required": true, "options": [{ "id": "text", "label": "Your answer", "freeText": true }] }]
  }
}
```

参见[API参考](references/api-reference.md#questions-and-waiting-for-human-input)选择问题和响应处理。包含正常的Authorization和X-Paperclip-Run-Id标头。
