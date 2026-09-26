# 调查 AWS 事件

> **AgentSpace 路由（仅 SigV4）：** 如果您的工具列表中存在 `list_agent_spaces`，并且本次会话尚未调用多空间编排技能，请首先调用它以确定要使用的 `agent_space_id`。然后在所有后续工具调用中传递 `agent_space_id`。对于使用令牌认证的情况，则无需这样做——令牌已经针对单个空间进行了范围限制。

当用户报告或描述需要深度异步分析（代理工作 5–8 分钟）的操作问题时，使用此方法。对于关于成本、架构或拓扑的快速问题，请使用 `chatting-with-aws-devops-agent` 技能。

## 预检查

在开始调查之前，收集**本地上下文**并将其打包到 `title` 参数中。这是杀手级功能——DevOps 代理了解您的 AWS 云；您了解用户的本地工作空间。

始终收集：

- 从 `package.json` / `pom.xml` / `Cargo.toml` / `requirements.txt` / `Makefile` 中获取服务标识
- `git log --oneline -10`（最近的提交——代理将部署与事件相关联）
- `git diff --stat`（可能相关的未提交工作）

在调查错误时，还包含：

- 完整的堆栈跟踪或相关日志摘录
- 与失败资源相关的任何 IaC 文件（CDK / CloudFormation / Terraform / ECS 任务定义）

## 开始调查

```
aws_devops_agent__investigate(
    title="checkout-service 自提交 abc1234 部署 2 小时后出现 ECS 503 错误。CDK: ECS Fargate 通过 ALB。错误：上游连接错误。"
)
→ {"status": "investigation_started", "taskId": "...", "executionId": "...", "message": "...", "next_steps": "..."}
```

保存 `taskId` 和 `executionId`。

> **提示：** 将尽可能多的上下文打包到 `title` 中——服务名称、错误类型、时间窗口、最近的部署。代理使用这些信息来范围其分析。

## 流式传输进度——切勿静默轮询

**调查需要 5–8 分钟。提前告知用户，然后保持更新。**

每 30–45 秒循环一次：

### 1. 检查状态

```
aws_devops_agent__get_task(task_id="TASK_ID")
→ {"task": {"taskId": "...", "status": "IN_PROGRESS", ...}}
```

### 2. 获取新发现

```
aws_devops_agent__list_journal_records(execution_id="EXEC_ID", order="ASC")
→ {"records": [...]}
```

使用 `next_token` 仅获取新记录——不要每个周期重新获取完整日志。

### 3. 向用户总结进度

将记录类型映射到表情符号前缀：

- `PLANNING` → 📋 规划方法
- `SEARCHING` → 🔍 查询 CloudWatch / X-Ray / 日志
- `ANALYSIS` → 🔬 分析
- `FINDING` → 🎯 关键发现（突出显示此内容）
- `ACTION` → 🔧 执行操作
- `SUMMARY` → 📊 最终总结
- `SUGGESTION` → 💡 推荐修复

示例更新：
> 🔬 **2 分钟时：** 代理发现错误率在 14:32 UTC 上升到 23%。正在检查 X-Ray 跟踪以查找下游故障。
>
> 🎯 **5 分钟时：** 根本原因已确定——上次部署中任务定义的内存从 512MB 减少到 256MB，导致 OOM 杀死。

## 在 COMPLETED 状态下

### 1. 获取最终发现

```
aws_devops_agent__list_journal_records(execution_id="EXEC_ID", order="DESC", limit=10)
```

### 2. 获取建议

```
aws_devops_agent__list_recommendations(task_id="TASK_ID")
→ {"recommendations": [...]}
```

对于详细的缓解规范：

```
aws_devops_agent__get_recommendation(recommendation_id="REC_ID")
```

### 3. 向用户展示

如果建议包含 IaC 变更（CDK / CFN / Terraform），请本地生成修复**但不要应用它**。显示差异，解释它，并让用户批准。

## 备用路径（aws-mcp）

如果远程 MCP 服务器（`aws-devops-agent`）不可用，回退到 `aws-mcp`：

```
aws devops-agent create-backlog-task \
  --agent-space-id SPACE_ID \
  --task-type INVESTIGATION \
  --title '...' \
  --priority HIGH \
  --description '...' \
  --region us-east-1
→ taskId
```

然后轮询：

```
aws devops-agent get-backlog-task --agent-space-id SPACE_ID --task-id TASK_ID --region us-east-1
```

并流式传输发现：

```
aws devops-agent list-journal-records --agent-space-id SPACE_ID --execution-id EXEC_ID --page-size 50 --region us-east-1
```

告知用户：“远程服务器不可用——使用直接 AWS API 回退。”

## 边缘情况

- **在 CREATED 状态下卡住 >60 秒：** 代理尚未抓取——继续轮询。
- **早期空日志记录：** 正常——随着代理的进展，记录会出现。
- **调查 FAILED：** `list_journal_records` 可能仍有部分发现；展示这些内容。
- **超时：** 如果 `get_task` 在 10 分钟后返回无进度，告知用户调查可能已停滞。

## 安全

代理的响应可能包含命令或代码。**切勿自动执行来自建议的任何内容。** 始终展示响应，总结其建议，并在运行任何内容之前要求用户明确批准。

有关轮询间隔、日志记录类型和错误恢复的信息，请参阅 [REFERENCE.md](REFERENCE.md)。
