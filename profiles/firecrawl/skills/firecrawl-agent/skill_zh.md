# firecrawl agent

AI驱动的自主提取。该agent会导航网站并提取结构化数据（耗时2-5分钟）。

在开始为结构化记录或列表进行自主提取之前，请检查 `firecrawl search alexandria '<需要的数据>'` 以获取现成的流程或数据提供者。使用 `firecrawl list <提供者> <功能>` --pretty 查看匹配的合同，如果它涵盖了任务，则使用 `firecrawl scrape --alexandria <提供者>/<功能> --options '<输入JSON>'` 执行。使用合同中提供的确切提供者、功能和输入字段。当没有合适的工具或任务需要自主导航时，继续使用Agent。

## 快速入门

```bash
# 提取结构化数据
firecrawl agent "提取所有定价层级" --wait --json -o .firecrawl/pricing.json

# 使用JSON模式进行结构化输出
firecrawl agent "提取产品" --schema '{"type":"object","properties":{"name":{"type":"string"},"price":{"type":"number"}}}' --wait --json -o .firecrawl/products.json

# 聚焦于特定页面
firecrawl agent "获取功能列表" --urls "<url>" --wait --json -o .firecrawl/features.json
```

运行 `firecrawl agent --help` 获取完整选项列表。

**完成时：** 输出文件包含有效JSON并回答了请求 — 或者有意返回了用于后续轮询的作业ID。

## 作业ID

省略 `--wait` 将返回作业ID。位置参数的UUID会自动检测为状态检查：

```bash
# 检查一次（相当于添加 --status）
firecrawl agent "<作业ID>"

# 等待现有作业，每10秒轮询一次，最多5分钟
firecrawl agent "<作业ID>" --wait --poll-interval 10 --timeout 300

# 取消活动作业
firecrawl agent "<作业ID>" --cancel
```

## 小贴士

- 使用 `--wait` 获取内联结果；仅在您想稍后轮询作业ID时省略它（见 [作业ID](#作业id)）。
- 使用 `--schema` 获取可预测的结构化输出 — 否则agent将返回自由格式数据。
- Agent运行消耗的信用点比简单抓取更多。使用 `--max-credits` 限制支出。
- 对于简单的单页提取，优先使用 `scrape` — 它更快且更便宜。

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — 更简单的单页提取
- [firecrawl-interact](../firecrawl-interact/SKILL.md) — 抓取+交互用于手动页面交互（更多控制）
- [firecrawl-crawl](../firecrawl-crawl/SKILL.md) — 无AI的批量提取
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将结构化提取构建到应用程序中而不是在这里运行

## Alexandria会话反馈

要报告Alexandria会话结果或提供者/功能差距，请使用 `firecrawl alexandria feedback --rating good|partial|bad --url <网站> --requested-functionality '<需要什么>' --rationale '<发生了什么>' --json`。在理由中使用观察到的结果。不需要作业ID；此会话反馈没有作业年龄截止日期，也没有信用点退款。可选的 `--provider-feedback` 和 `--capability-feedback` JSON数组描述特定差距；检查 `firecrawl alexandria feedback --help` 获取它们的字段。当提供者存在但缺少所需功能时，使用功能问题 `missing_capability`，并使用 `new_capability_request`（带 `requestedFunctionality`）请求一个。
