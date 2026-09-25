你正在为 Caveman Cloud 标记此仓库的 LLM 工作流。

*工作流*是指代码执行的一个任务——“回复支持工单”、“构建夜间摘要”、“运行评估套件”——而非一项技术。每个网关请求都可以携带工作流标签；未标记的流量将全部落入一个 `unlabeled-workflow` 桶中。你的任务是：找出这些工作流、为其命名、关联标签，并确认一切未出现问题。

这涉及代码变更，因此需经过用户的常规审查：**先提出表格方案，待用户同意后再应用。** 在已标记的仓库上重复执行必须不产生任何变化（即具备幂等性）。

本技能由操作员调用。`unlabeled-traffic` Cave Plan 观测仅为审查用途，不会创建建议文件、提案或草稿 PR。不得推断遥测数据已选择某个调用点或授权了编辑操作。请独立盘点仓库、展示标记表格，并在更改代码前等待用户批准。

## 步骤 1 — 盘点工作流

从仓库的入口点（而非导入）开始遍历：

- 调用 LLM 的 HTTP/RPC 处理器（直接调用或通过中间层调用）
- 定时任务：cron 定义、队列消费者、工作进程、调用 LLM 代码的 GitHub Actions
- CLI 命令和脚本（`scripts/`、`bin/`、`package.json` 脚本）
- 消耗真实 token 的评估/测试框架
- 框架内的独立 Agent 或链（每个 LangGraph 图、每个 crew、每个 Agent 定义通常都是独立的工作流）

一个工作流 = 人类会给其命名的一个任务。同一请求处理器内部的十个调用点属于一个工作流；由三个任务共享的同一个 `llm.ts` 辅助函数则属于三个工作流（在调用处标记，而非在共享辅助函数处标记）。

## 步骤 2 — 命名

Slug 语法（网关会强制执行）：小写 `[a-z0-9_-]`，长度为 1–96 个字符。命名任务是其目的，而非技术：

- 推荐：`support-reply`、`nightly-digest`、`pr-review`、`eval-suite`、`onboarding-email`
- 不推荐：`openai-calls`（技术名）、`main`（无意义）、`SupportReply`（不符合规范）、`johns-test-3`（不便于长期维护）

名称一经确定，基本具有长期性——后续重命名会割裂花费记录。当任务目的无法从代码中明确时，应从文件名推导出 slug，并在表格中将其标记为 `review`，而非随意臆造目的。

## 步骤 3 — 先提出，后应用

展示以下表格并请求继续执行：

```
| workflow | job | where | how it gets labeled |
|---|---|---|---|
| support-reply | answers inbound tickets | src/bot/reply.ts:41 | defaultHeaders on the reply client |
| nightly-digest | 02:00 summary job | jobs/digest.ts:12 | header on the digest client |
| eval-suite (review) | scripts/eval.ts:8 — purpose inferred from filename | scripts/eval.ts:8 | env override at invocation |
```

随后在调用点使用最轻量的机制为每个标签接入：

- **@caveman-ai/sdk / caveman_cloud SDK**：使用单次调用 per-trace `workflow` 选项，或在单个任务服务构建的客户端上设置 `defaultWorkflow`。
- **原始提供商 SDK**（OpenAI/Anthropic/LangChain/LiteLLM/Vercel）：在已包含 `x-cave-api-key` 的 `defaultHeaders` / `default_headers` / `extra_headers` 代码块中，添加 `"x-cave-workflow": "<slug`。多个任务共享同一客户端时，请按调用传递该请求头（上述所有 SDK 均接受单请求请求头覆盖），或为每个任务配置独立的轻量客户端。
- **包装编程 Agent**（`caveman wrap`）：在调用位置（cron 行、CI 步骤）使用 `--workflow <slug>` 参数或 `CAVE_WORKFLOW= <slug>` 环境变量。
- **原始 HTTP**：将 `x-cave-workflow` 请求头添加到请求中。

在调用处标记，保持差异最小，并符合仓库风格。如果某个调用点完全未通过 Caveman 网关路由，则不要为其标记——在报告中将其列入“未接入”部分（标签仅在网关流量中传输；接入工作由 caveman-setup 技能负责）。

## 步骤 4 — 验证

运行仓库中已有用以测试某条已标记路径的方法（测试、开发脚本、一次 curl）。随后确认：请求仍能成功（网关会对无效标签返回 400 `cave_invalid_request_header`——若如此，请修正 slug）。每次工作流运行后，已标记的花费会出现在 `/activity?tab=workflows` 的仪表板上；定时任务会在计划触发时显示，在报告中说明这一点比假装它们在线更有价值。

## 步骤 5 — 汇报

```
## 已标记工作流

| workflow | job | where |
|---|---|---|
| support-reply | answers inbound tickets | src/bot/reply.ts:41 |
| nightly-digest | 02:00 summary job | jobs/digest.ts:12 |

已验证： <你实际测试的已标记路径及其观察结果)
显示位置： <DASHBOARD>/activity?tab=workflows — 每行会在该工作流下次运行时显示。任何仍未标记的项将显示为 `unlabeled-workflow`。
未接入（无网关路由，故无标签）： <列表或“无”）
标记为审查： <因文件名推导出目的而标记的 slug，或“无”）
```

如果你完全没有找到 LLM 入口点，请确切说明这一点，并指向设置技能（` <docs origin>/docs/agent-setup.md`），而不是编造一张表格。
