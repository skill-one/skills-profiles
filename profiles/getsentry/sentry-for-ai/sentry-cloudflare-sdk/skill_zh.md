> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Cloudflare SDK

# Sentry Cloudflare SDK

一个有主见的向导，它会扫描您的 Cloudflare 项目，并指导您完成 Sentry 在 Workers、Pages、Durable Objects、Queues、Workflows 和 Hono 上的完整设置。

## 在何时调用此技能

- 用户询问在 Cloudflare 项目中“将 Sentry 添加到 Cloudflare Workers”或“设置 Sentry”
- 用户想要安装或配置 `@sentry/cloudflare`
- 用户想要为 Cloudflare Workers 或 Pages 添加错误监控、跟踪、日志记录、计划任务或 AI 监控
- 用户询问关于 `withSentry`、`sentryPagesPlugin`、`instrumentDurableObjectWithSentry` 或 `instrumentD1WithSentry`
- 用户想要监控 Cloudflare 上的 Durable Objects、Queues、Workflows、计划处理程序或电子邮件处理程序

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的当前状态（`@sentry/cloudflare` v10.61.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/javascript/guides/cloudflare/](https://docs.sentry.io/platforms/javascript/guides/cloudflare/) 进行验证。

---

## 第一阶段：检测

在做出任何建议之前，运行这些命令以了解项目：

```bash
# 检测 Cloudflare 项目
ls wrangler.toml wrangler.jsonc wrangler.json 2>/dev/null

# 检测现有 Sentry
cat package.json 2>/dev/null | grep -E '"@sentry/'

# 检测项目类型（Workers vs Pages）
ls functions/ functions/_middleware.js functions/_middleware.ts 2>/dev/null && echo "检测到 Pages"
cat wrangler.toml 2>/dev/null | grep -E 'main|pages_build_output_dir'

# 检测框架
cat package.json 2>/dev/null | grep -E '"hono"|"remix"|"astro"|"svelte"'

# 检测 Durable Objects
cat wrangler.toml 2>/dev/null | grep -i 'durable_objects'

# 检测 D1 数据库
cat wrangler.toml 2>/dev/null | grep -i 'd1_databases'

# 检测 Queues
cat wrangler.toml 2>/dev/null | grep -i 'queues'

# 检测 Workflows
cat wrangler.toml 2>/dev/null | grep -i 'workflows'

# 检测计划处理程序（cron 触发器）
cat wrangler.toml 2>/dev/null | grep -i 'crons\|triggers'

# 检测兼容性标志
cat wrangler.toml 2>/dev/null | grep -i 'compatibility_flags'
cat wrangler.jsonc 2>/dev/null | grep -i 'compatibility_flags'

# 检测 AI/LLM 库
cat package.json 2>/dev/null | grep -E '"openai"|"@anthropic-ai"|"ai"|"@google/generative-ai"|"@langchain"'

# 检测日志记录库
cat package.json 2>/dev/null | grep -E '"pino"|"winston"'

# 检查配套前端
ls frontend/ web/ client/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"vue"|"svelte"|"next"'
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| Workers 或 Pages？ | 确定包装器：`withSentry` vs `sentryPagesPlugin` |
| Hono 框架？ | 推荐使用独立的 `@sentry/hono` 包（v10.55.0+）以实现更干净的集成 |
| `@sentry/cloudflare` 已安装？ | 跳过安装，进入功能配置 |
| Durable Objects 已配置？ | 推荐使用 `instrumentDurableObjectWithSentry` |
| D1 数据库已绑定？ | `withSentry` 自动注入 D1 绑定（v10.57.0+）；无需手动包装 |
| Queues 已配置？ | `withSentry` 自动注入队列处理程序 |
| Workflows 已配置？ | 推荐使用 `instrumentWorkflowWithSentry` |
| Cron 触发器已配置？ | `withSentry` 自动注入计划处理程序；推荐使用 Crons 监控 |
| `nodejs_als` 或 `nodejs_compat` 标志已设置？ | **必需** — SDK 需要 `AsyncLocalStorage` |
| AI/LLM 库？ | 推荐使用 AI 监控集成 |
| 配套前端？ | 触发第四阶段的跨链接 |

---

## 第二阶段：推荐

根据您发现的内容提出具体的建议，不要提出开放式问题——直接提出建议：

**核心覆盖（推荐）：**
- ✅ **错误监控** — 始终；捕获 fetch、scheduled、queue、email 和 Durable Object 处理程序中的未处理异常
- ✅ **跟踪** — 自动 HTTP 请求跨度、出站 fetch 跟踪、D1 查询跨度

**可选（增强可观察性）：**
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 进行结构化日志；当需要日志搜索时推荐
- ⚡ **Crons** — 检测遗漏/失败的计划任务；当配置了 cron 触发器时推荐
- ⚡ **D1 注入** — 自动查询跨度和面包屑；当 D1 绑定时推荐
- ⚡ **Durable Objects** — 自动捕获 DO 方法的错误和跨度；当配置了 DO 时推荐
- ⚡ **Workflows** — 自动为 workflow 步骤创建跨度；当配置了 Workflows 时推荐
- ⚡ **AI 监控** — Vercel AI SDK、OpenAI、Anthropic、LangChain；当检测到 AI 库时推荐

**推荐逻辑：**

| 功能 | 当...推荐 |
|---------|------------------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终** — HTTP 请求跟踪和出站 fetch 具有高价值 |
| 日志记录 | 应用需要结构化日志搜索或日志到跟踪关联 |
| Crons | 在 `wrangler.toml` 中配置了 cron 触发器 |
| D1 注入 | 存在 D1 数据库绑定 |
| Durable Objects | 配置了 Durable Object 绑定 |
| Workflows | 配置了 Workflow 绑定 |
| AI 监控 | 应用使用 Vercel AI SDK、OpenAI、Anthropic 或 LangChain |
| 指标 | 应用需要自定义计数器、仪表板或分布 |

提议：*"我建议设置错误监控 + 跟踪。您还需要我添加 D1 注入和 Crons 监控吗？"*
