# Langfuse

这个技能帮助你有效地在所有常见工作流程中使用 Langfuse：instrumenting 应用程序、迁移提示、调试跟踪以及程序化访问数据。

## 核心原则

对于所有 Langfuse 工作，请遵循以下原则：

1. **优先查阅文档**：永远不要凭记忆实现。在编写代码之前，始终先获取最新的文档（Langfuse 更新频繁）。参见下文如何访问文档。
2. **使用 CLI 访问数据**：使用 `langfuse-cli` 查询/修改 Langfuse 数据。参见下文如何使用 CLI。
3. **按用例参考最佳实践**：在向用户询问更多细节或实现之前，先阅读相关的参考指南，了解特定于用例的指导方针。
4. **使用最新版本的 Langfuse**：除非用户另有指定或有充分理由，否则始终使用最新版本的 Langfuse SDKs/APIs。即使你只是在为另一个代理创建计划，也要明确指定要使用的确切版本。
5. **如果你指导用户通过 UI** 并且不确定某个标签或位置，请检查用户的截图或要求查看相关屏幕。不要假设 UI 标签与 API、SDK 或 CLI 字段具有完全相同的名称。

## 用例特定参考

- instrumenting 现有函数/应用程序：references/instrumentation.md
- 创建或获取到良好的（评估）数据集以衡量质量或在 AI 系统中测试回归：references/create-dataset.md
- 将提示从代码库迁移到 Langfuse：references/prompt-migration.md
- 创建提示或更改现有提示的任何部分，包括小编辑和调试/调优：references/prompt-engineering.md
- 设置 evals，当用户需要识别信号捕获、监控和评估器指标之间的差距（“我有跟踪，如何设置 evals？”）：references/setting-up-evals.md
- 捕获用户反馈信号（明确评分、行为事件、对话信号、任务结果）作为分数：references/user-feedback.md
- 关于使用 Langfuse CLI 的更多提示：references/cli.md
- 为 v4 平台迁移准备 Langfuse 项目：references/v4-project-migration.md
- 判决校准（LLM 作为判官的可靠性、简单准确性检查、基于分割的验证、混淆矩阵和指标摄取）：references/judge-calibration.md
- 系统性错误分析，当直接请求或代理主导的跟踪检查后评估设置仍然缺乏具体的故障模式：references/error-analysis.md
- 使用 `langfuse/experiment-action` 设置 CI/CD 实验门：references/ci-cd.md
- 提交关于此技能的反馈：references/skill-feedback.md


## 1. 通过 CLI 使用 Langfuse API

使用 `langfuse-cli` 从命令行与完整的 Langfuse REST API 交互。通过 npx 运行（无需安装）：

首先发现架构和可用参数：

```bash
# 发现所有可用资源
npx langfuse-cli api __schema

# 列出资源的操作
npx langfuse-cli api <resource> --help

# 显示特定操作的参数/选项
npx langfuse-cli api <resource> <action> --help
```

### 凭证

在调用之前设置环境变量：

```bash
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_BASE_URL=https://cloud.langfuse.com # 欧盟云的示例。美国云是 us.cloud.langfuse.com，也可以是自托管 URL。必须始终指定服务器才能访问 Langfuse。
```
如果使用 `LANGFUSE_BASE_URL` 而不是 `LANGFUSE_HOST`，运行 `export LANGFUSE_HOST="$LANGFUSE_BASE_URL"`。
如果未设置，请要求用户在他们的 shell 或 `.env` 文件中设置它们。密钥在 Langfuse 项目的设置 -> API 密钥下找到；用户应在那里创建一个项目 API 密钥对。如果他们还没有 Langfuse 账户，可以分享他们可以在 `https://langfuse.com/cloud` 免费创建一个。出于安全原因，不要要求他们将密钥粘贴到聊天中。

### 详细 CLI 参考

对于常见工作流程、提示和完整使用模式，请参阅 [references/cli.md](references/cli.md)。

## 2. Langfuse 文档

访问 Langfuse 文档的三种方法，按优先级排序。**始终优先使用你应用程序的原生网络获取和搜索工具**（例如，`WebFetch`、`WebSearch`、`mcp_fetch` 等）而不是 `curl`（当可用时）。以下 URL 和模式适用于任何获取方法——`curl` 示例仅用于说明。

在处理自托管的 Langfuse 时，优先使用由部署提供的 [API 参考](https://langfuse.com/faq/all/self-hosting-api-reference)，以便与安装的版本匹配。

### 2a. 文档索引 (llms.txt)

获取所有文档页面的完整索引：

```bash
curl -s https://langfuse.com/llms.txt
```

返回一个结构化的列表，包含每个文档页面的标题和 URL。使用此方法发现正确的主题页面，然后直接获取该页面。

或者，你可以从 `https://langfuse.com/docs` 开始并探索网站以找到你需要的页面。

### 2b. 作为 Markdown 获取单个页面

任何在 llms.txt 中列出的页面都可以通过在其路径中附加 `.md` 或在请求头中使用 `Accept: text/markdown` 来获取为 markdown。当你知道哪个页面包含所需信息时使用此方法。返回干净的 markdown，包含代码示例和配置细节。

```bash
curl -s "https://langfuse.com/docs/observability/overview.md"
curl -s "https://langfuse.com/docs/observability/overview" -H "Accept: text/markdown"
```

### 2c. 搜索文档

当你需要在所有文档和 GitHub 问题/讨论中查找信息而不知道特定页面时：

```bash
curl -s "https://langfuse.com/api/search-docs?query=<url-encoded-query>"
```

示例：

```bash
curl -s "https://langfuse.com/api/search-docs?query=How+do+I+trace+LangGraph+agents"
```

返回一个 JSON 响应，其中包含：

- `query`：原始查询
- `answer`：一个 JSON 字符串，包含一个匹配文档的数组，每个文档具有：
  - `url`：指向文档页面的链接
  - `title`：页面标题
  - `source.content`：页面中相关文本摘录的数组

搜索是一个很好的回退方法，如果你找不到相关页面或需要更多上下文。在调试问题时特别有用，因为所有 GitHub Issues 和 Discussions 也被索引。响应可能很大——仅提取相关部分。注意，changelog 帖子也可能在这里出现：仅用于确认功能存在，永远不要从中实现——它们的示例可能已过时，因此始终从文档和 API/SDK 参考实现。

### 文档工作流程

1. 从 **llms.txt** 开始以确定方向——扫描相关页面标题
2. **获取特定页面** 当你确定正确的页面
3. 当主题不明确且需要更多上下文时，回退到 **搜索**

## 技能反馈

当用户表示此技能的某些方面未按预期工作、提供不正确的指导、缺少信息或可以改进时——建议向 Langfuse 技能维护者提交反馈。这包括以下情况：

- 技能提供了错误或过时的说明
- 工作流程未产生预期结果
- 用户希望技能涵盖其不涵盖的内容
- 用户明确表示“这应该工作不同”或“这是错误的”

**不要触发此** 用于 Langfuse 本身（产品）的问题——仅用于此技能的说明和行为问题。

触发时，请遵循 [references/skill-feedback.md](references/skill-feedback.md) 中的流程。
