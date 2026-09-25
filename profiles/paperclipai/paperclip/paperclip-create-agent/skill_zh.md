# Paperclip 创建代理技能

当被要求雇佣/创建代理时，使用此技能。

## 前置条件

你需要以下权限之一：

- 板块访问权限，或
- 公司中的代理权限 `can_create_agents=true`

如果你没有这些权限，请升级至你的CEO或董事会。

## 工作流程

### 选择API传输方式

在 **Paperclip Runner** 上，使用宣传的 Paperclip 工具。使用 `get_task_context`
和 `list_agents` 获取身份和团队上下文，然后使用 `search_api` 发现下文使用的
配置、指令模板、图标和 `agent-hires` 端点。使用 `call_api` 调用发现的操作；
服务器提供公司和身份验证上下文。在起草雇佣前，先阅读返回的架构。

下方的 Shell 示例适用于接收 `PAPERCLIP_API_URL` 和
`PAPERCLIP_API_KEY` 的适配器。Paperclip Runner 不提供这些变量。不要搜索工作区文件以重新创建服务器地址或凭证路径。
如果 `search_api` / `call_api` 不可用，报告雇佣需要操作员为此公司启用 Runner API 工具。在对话中保留拟议的雇佣；不要声称已创建代理，也不要用临时代理替代请求的永久雇佣。

### 1. 确认身份和公司上下文

```sh
curl -sS "$PAPERCLIP_API_URL/api/agents/me" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"
```

### 2. 发现此 Paperclip 实例的适配器配置

```sh
curl -sS "$PAPERCLIP_API_URL/llms/agent-configuration.txt" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"

# 然后是计划使用的特定适配器，例如 claude_local：
curl -sS "$PAPERCLIP_API_URL/llms/agent-configuration/claude_local.txt" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"
```

### 3. 比较现有代理配置

```sh
curl -sS "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/agent-configurations" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"
```

注意公司已经遵循的命名、图标、汇报线和适配器约定。

### 4. 选择指令来源（必需）

这是决定雇佣质量的最重要决策。选择以下路径之一：

- **精确模板** — 角色与模板索引中的条目匹配。使用 `references/agents/` 下匹配的文件作为起点。
- **邻近模板** — 没有精确匹配，但现有模板接近（例如，从 `coder.md` 修改的“后端工程师”雇佣，或从 `uxdesigner.md` 修改的“内容设计师”）。复制最接近的模板并有意修改：重命名角色、重写角色章程、交换领域透镜，并删除不合适的部分。
- **通用后备** — 没有接近的模板。使用基线角色指南从零构建新的 `AGENTS.md`，填写每个推荐部分以适应特定角色。

模板索引和使用指南：
`skills/paperclip-create-agent/references/agent-instruction-templates.md`

无模板雇佣的通用后备：
`skills/paperclip-create-agent/references/baseline-role-guide.md`

在雇佣请求评论中说明你选择的路径，以便董事会了解理由。

### 5. 发现允许的代理图标

```sh
curl -sS "$PAPERCLIP_API_URL/llms/agent-icons.txt" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"
```

### 6. 起草新的雇佣配置

- 角色 / 标题 / 名称
- 图标（实践中必需；从 `/llms/agent-icons.txt` 选择）
- 汇报线 (`reportsTo`)
- 适配器类型
- 当此角色需要在第一天安装技能时，从公司技能库获取 `desiredSkills`
- 如果任何 `desiredSkills` 或适配器设置扩展浏览器访问、外部系统访问、文件系统范围或密钥处理能力，请在雇佣评论中说明每个扩展的理由
- 适配器和运行时配置与当前环境对齐
- 默认情况下关闭计时器心跳；只有在角色确实需要计划定期工作或用户明确要求时，才设置 `runtimeConfig.heartbeat.enabled=true`
- 如果角色可能处理私人建议或敏感披露，请先确认存在机密工作流程（专用技能或记录的手动流程）
- 能力
- 适配器支持的管理指令包 (`AGENTS.md`)；避免使用持久的 `promptTemplate` 配置
- 对于编码或执行代理，包括 Paperclip 执行合同：在同一心跳中启动可执行工作；除非请求规划，否则不要在计划处停止；将持久进度与清晰的下一步操作保留；使用子问题处理长时间或并行委托工作，而不是轮询；用所有者/操作标记阻塞工作；尊重预算、暂停/取消、审批门禁和公司边界
- 指令文本，如 `AGENTS.md`（来自步骤4）；对于本地管理包适配器，将此作为顶级 `instructionsBundle.files["AGENTS.md"]` 发送。不要为新代理设置 `adapterConfig.promptTemplate` 或 `bootstrapPromptTemplate`。
- 当此雇佣来自问题时，提供源问题链接 (`sourceIssueId` 或 `sourceIssueIds`)

### 7. 对照质量检查清单审查草稿

提交前，端到端走一遍草稿审查检查清单，并修复任何未通过的项：
`skills/paperclip-create-agent/references/draft-review-checklist.md`

### 8. 提交雇佣请求

```sh
curl -sS -X POST "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/agent-hires" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CTO",
    "role": "cto",
    "title": "Chief Technology Officer",
    "icon": "crown",
    "reportsTo": "<ceo-agent-id>",
    "capabilities": "Owns technical roadmap, architecture, staffing, execution",
    "desiredSkills": ["vercel-labs/agent-browser/agent-browser"],
    "adapterType": "codex_local",
    "adapterConfig": {"cwd": "/abs/path/to/repo", "model": "o4-mini"},
    "instructionsBundle": {"files": {"AGENTS.md": "You are the CTO..."}},
    "runtimeConfig": {"heartbeat": {"enabled": false, "wakeOnDemand": true}},
    "sourceIssueId": "<issue-id>"
  }'
```

### 9. 处理治理状态

- 如果响应有 `approval`，雇佣状态为 `pending_approval`
- 监控并在审批线程上讨论
- 当董事会批准时，你将被唤醒并带有 `PAPERCLIP_APPROVAL_ID`；阅读相关问题和关闭/评论后续事项

```sh
curl -sS "$PAPERCLIP_API_URL/api/approvals/<approval-id>" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"

curl -sS -X POST "$PAPERCLIP_API_URL/api/approvals/<approval-id>/comments" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"body":"## CTO 雇佣请求已提交\n\n- 审批: [<approval-id>](/approvals/<approval-id>)\n- 待处理的代理: [<agent-ref>](/agents/<agent-url-key-or-id>)\n- 源问题: [<issue-ref>](/issues/<issue-identifier-or-id>)\n\n根据董事会反馈更新了提示和适配器配置。"}'
```

如果审批已存在且需要手动链接到问题：

```sh
curl -sS -X POST "$PAPERCLIP_API_URL/api/issues/<issue-id>/approvals" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"approvalId":"<approval-id>"}'
```

批准后，运行此后续循环：

```sh
curl -sS "$PAPERCLIP_API_URL/api/approvals/$PAPERCLIP_APPROVAL_ID" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"

curl -sS "$PAPERCLIP_API_URL/api/approvals/$PAPERCLIP_APPROVAL_ID/issues" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY"
```

对于每个链接的问题，执行以下操作之一：
- 如果审批解决了请求，则关闭它，或
- 用 Markdown 评论，链接到审批和下一步行动。

## 参考资料

- 模板索引和使用模板指南：`skills/paperclip-create-agent/references/agent-instruction-templates.md`
- 单个角色模板：`skills/paperclip-create-agent/references/agents/`
- 无模板雇佣的通用基线角色指南：`skills/paperclip-create-agent/references/baseline-role-guide.md`
- 提交前草稿审查检查清单：`skills/paperclip-create-agent/references/draft-review-checklist.md`
- 端点有效负载形状和完整示例：`skills/paperclip-create-agent/references/api-reference.md`
