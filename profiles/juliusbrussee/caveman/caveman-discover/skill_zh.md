您正在为Caveman Cloud标记此存储库的LLM工作流。  
*工作流*是指代码执行的任务——"回答支持工单"、"构建夜间摘要"、"运行评估套件"——而不是技术。每个网关请求都可以携带一个工作流标签；未标记的流量全部进入一个`unlabeled-workflow`桶。您的任务：找到工作流，命名清晰，连接标签，并验证没有出现故障。

这会修改代码，因此需要经过用户的正常审查：**先提出表格，用户同意后再应用**。在已经标记的存储库上重新运行时，必须不做任何改变（幂等性）。

这项技能由操作员触发。一个`unlabeled-traffic`的Cave Plan观察仅用于审查，不会创建建议文件、提案或Draft PR。不要推断遥测数据选择了调用点或授权了编辑。独立地清点存储库，展示标记表格，并在修改代码前等待用户的批准。

## 第1步——清点工作流

从存储库的入口点开始遍历，而不是从其导入开始：

- 调用LLM的HTTP/RPC处理器（直接或通过层）
- 定时任务：cron定义、队列消费者、工作程序、调用LLM代码的GitHub Actions
- CLI命令和脚本（`scripts/`、`bin/`、`package.json`脚本）
- 烧掉真实令牌的评估/测试框架
- 框架内的独立代理或链（每个LangGraph图、每个crew、每个代理定义通常是其自己的工作流）

一个工作流 = 一个人会命名的任务。同一个请求处理器内的十个调用点是一个工作流；三个任务使用的共享`llm.ts`辅助程序是三个工作流（在调用者处标记，而不是在共享辅助程序处）。

## 第2步——命名

短横线语法（网关强制执行此规则）：小写`[a-z0-9_-]`，1-96个字符。命名任务，而不是技术：

- 好：`support-reply`、`nightly-digest`、`pr-review`、`eval-suite`、`onboarding-email`
- 不好：`openai-calls`（技术）、`main`（无意义）、`SupportReply`（无效）、`johns-test-3`（不会随时间变化）

名称是永恒的——稍后重命名会分割支出历史。当任务的用途从代码中不明显时，从文件名派生短横线，并在表格中将其标记为`review`，而不是编造一个用途。

## 第3步——先提出，再应用

展示此表格并请求继续：

```
| 工作流 | 任务 | 位置 | 如何标记 |
|---|---|---|---|
| support-reply | 回答传入的工单 | src/bot/reply.ts:41 | reply客户端的defaultHeaders |
| nightly-digest | 02:00摘要任务 | jobs/digest.ts:12 | 摘要客户端的header |
| eval-suite (review) | scripts/eval.ts:8 — 从文件名推断用途 | scripts/eval.ts:8 | 调用时的环境覆盖 |
```

然后在每个调用点使用最轻的机制连接每个标签：

- **@caveman-ai/sdk / caveman_cloud SDK**：每个跟踪的`workflow`选项，或单任务服务构造的客户端上的`defaultWorkflow`。
- **原始提供者SDK**（OpenAI/Anthropic/LangChain/LiteLLM/Vercel）：在已经携带`x-cave-api-key`的`defaultHeaders` / `default_headers` / `extra_headers`块中添加`"x-cave-workflow": "<slug>"`。多个任务使用的共享客户端→逐调用传递头（上述所有SDK都接受逐请求头覆盖），或给每个任务自己的瘦客户端。
- **包装的编码代理**（`caveman wrap`）：`--workflow <slug>`标志或调用位置的`CAVE_WORKFLOW=<slug>`环境（cron行、CI步骤）。
- **原始HTTP**：在请求中添加`x-cave-workflow`头。

标记调用者，保持差异最小，匹配存储库的风格。如果一个调用点根本没有通过Caveman网关路由，就不要标记它——在报告中将其列为"未连接"（标签仅在网关流量中传递；连接是caveman-setup技能的工作）。

## 第4步——验证

运行存储库已经使用的任何用于执行一个标记路径的工具（测试、开发脚本、一个curl）。然后确认：请求仍然成功（网关会拒绝无效标签，返回400 `cave_invalid_request_header`——如果是这样，请修复短横线）。标记的支出会在每个工作流下次运行时出现在`/activity?tab=workflows`的仪表板上；定时任务会在任务触发时出现，这在报告中值得说明，而不是假装它们是活跃的。

## 第5步——报告

```
## 已标记的工作流

| 工作流 | 任务 | 位置 |
|---|---|---|
| support-reply | 回答传入的工单 | src/bot/reply.ts:41 |
| nightly-digest | 02:00摘要任务 | jobs/digest.ts:12 |

验证：您实际执行的标记路径以及观察到的内容
指向：<DASHBOARD>/activity?tab=workflows — 每行会在该工作流下次运行时出现。任何未标记的流量显示为`unlabeled-workflow`。
未连接（没有网关路由，因此没有标签）：<列出或"无">
标记为review：<从文件名推断用途的短横线，或"无">
```

如果您根本没有找到任何LLM入口点：明确说明这一点，并指向设置技能（`<docs origin>/docs/agent-setup.md`），而不是编造表格。
