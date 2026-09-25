# Firecrawl 开发者索引

从主要来源回答开发者问题：报告错误的 issue、修复错误的合并 pull request、声明契约的 README 或文档页面。描述行为的博客文章不如定义它的段落有力，因此应首先使用索引，其次才是公开网络。索引的存储库部分仅涵盖公共存储库。私有或内部存储库不包含在内，因此关于私有代码的问题需要不同的途径：直接阅读该代码。

没有**固定的配方**。阅读问题，判断问题的类型，然后选择以下方法之一。字面错误字符串需要不同的处理方式，而“如何做 X”则不同。不要运行问题未要求使用的机器。

## 工具及其独特优势

- HTTP: **`GET|POST https://api.firecrawl.dev/v2/search/developer`**
  MCP: **`firecrawl_developer_search(query, k?, skills?)`**
  CLI: **`firecrawl developer <query> [--limit <n>]`**
  在整个索引中提供排序结果。每个结果都包含 `id` (`issue:owner/repo#123`)、`url` 以及**Markdown 格式的匹配段落**，因此表格和代码块得以保留。结果类型由 `id` 前缀指示：`doc:`、`issue:`、`pull_request:` 或 `readme:`。
  开发者问题的默认首选方法。它是唯一返回段落的界面，这是让你能够直接回答而不是指向页面的原因。
  `k` / `--limit` 的范围是 1–100，默认值为 10。`skills="only"` (HTTP/MCP 仅限) 将搜索限制为 agent-skill 文件。
  无需密钥；为获得更高的速率限制，请发送 `Authorization: Bearer $FIRECRAWL_API_KEY`。

- MCP: **`firecrawl_search(query, categories: ["developer"])`**
  CLI: **`firecrawl search <query> --categories developer`**
  开发者结果在 `developer` 组中与 `web` 结果并列，每个结果包含 `url`、`title`、`description` (匹配的段落)、`position` 和 `category: "developer"` — web 结果不包含 `category`，因此合并时以此字段为依据。
  当你已经运行 web 搜索并希望开发源在相同调用中加权时使用。它不暴露任何过滤器，也不提供段落控制。

- MCP: **`firecrawl_scrape(url)` / `firecrawl_search(query)`**
  CLI: **`firecrawl scrape <url>` / `firecrawl search <query>`**
  通用 web 获取和搜索，用于主要来源未声明的内容：两个库的比较、停机事件、迁移说明、没有公共存储库或索引文档的项目。
  当命中是正确的页面但你需要全部内容时，也是后续操作 — `scrape` 结果的 `url`。

## 过滤器及其成本

仅 HTTP 界面采用这些。在 `GET` 中，传递 `types=issue,pull_request` 或重复参数；在 `POST` 中，传递数组。所有过滤器都是可选的。

- `types` — 搜索 `doc`、`issue`、`pull_request`、`readme` 中的哪一种。默认为全部四种。在此处缩小范围是使查询精确的最经济方式。
- `repos` (`owner/name`) 范围化存储库部分，即 `issue`、`pull_request` 和 `readme`；`sources` (文档源 ID，最多 20 个) 范围化文档部分，即 `doc`。传递两者会**联合**两半而不是交集。两者都在响应中回显 `indexed: true|false` — 这就是如何区分“不在索引中”和“未找到任何内容”。
- 无法匹配任何请求的 `type` 的过滤器会返回 `400`，而不是空列表：`types` 中没有存储库类型的 `repos`，或没有 `doc` 的 `sources`。
- `passages` (1–5, 默认 1) 是每个结果的**最大**段落数，不是保证。当一页显然是正确的页面，但第一个段落是它错误的部分时，提高它。
- `language`、`topic`、`license`、`min_stars`、`max_stars`、`archived`、`fork` 描述一个**存储库**。索引中的大多数文档页面没有存储库支持，因此没有存储库事实可以接纳或排除一个。发送任何这些过滤器而不带 `sources` 范围，响应将仅包含存储库证据 — `issue`、`pull_request`、`readme`。这是设计，不是索引的缺陷：不要重试，也不要报告索引损坏。要保留文档，请删除存储库过滤器，或使用 `sources` 范围化文档部分，并读取 `sources` 回显以确认 ID 已被索引。

## 将方法与问题匹配

- **字面错误消息或堆栈跟踪字符串** → 搜索字符串本身加上库名，并使用 `types=["issue","pull_request"]`。有人已经报告了它。如果没有任何匹配项，请剥离易变部分（路径、行号、ID、地址）并重试 — 消息的不变中间部分是索引的。
- **概念性的“如何做 X”** → 自然语言的完整问题，所有四种类型。答案通常是 `doc` 或 `readme`；在提高 `k` 之前先提高 `passages`。
- **已知错误** → issue 报告了它，合并的 pull request 修复了它，而你想要的是修复内容。搜索 `types=["issue","pull_request"]`，然后使用 `types=["pull_request"]` 将 issue 的自身术语范围化到其存储库中重新查询。合并的 PR 的段落告诉你发生了什么以及方向。
- **API 契约**（“X 返回什么”、“Y 是否必需”、“默认值是什么”）→ `readme` 和 `doc` 是权威的，博客文章不是。使用 `types=["readme","doc"]`。如果契约看起来已经移动，请使用 `pull_request` 跟踪移动它的更改。
- **特定版本的行行为** → issue 的开启报告描述了损坏的版本；其解决方案会覆盖它。提高 `passages` 以查看线程的更多内容，并在回答前阅读解决方案和链接的 pull request。永远不要仅凭开启报告回答。
- **限定于一个库** → 当你知道 slug 时使用 `repos=["owner/name"]`，如果你希望其文档在相同调用中返回，请加上 `sources`。如果限定搜索返回为空，请首先读取回显的 `indexed` 标志：`false` 表示来自该存储库或源的任何内容永远无法匹配，并且没有重写能帮助 — 删除范围并搜索整个索引，或转到网络。
- **生态系统范围**（“哪些库做 X”、“其他人是否也遇到了这个问题”）→ 无范围。使用 `language` / `topic` / `min_stars` 保持在维护的存储库中，接受这会放弃所有 `doc` 结果。
- **agent 技能和工具约定** → `skills="only"` (HTTP/MCP 仅限)。
- **比较、观点、新闻或未索引的项目** → 公开网络。`firecrawl_search`，然后 `firecrawl_scrape` 值得完整阅读的内容。组合通常是正确的：从索引中获取契约，从网络中获取权衡。

## 原则

- **引用段落，引用 `url`。** 段落是证据；将它们交给读者而不是将它们改写为读者无法检查的声明。`title` 在 `doc` 结果中经常不存在 — 回退到 `url`。
- **合并优先于报告。** 当 issue 和 pull request 互相矛盾时，合并的 pull request 是当前行为。说明你读了哪个。
- **最后范围，而不是首先。** 搜索整个索引，然后在使用 `types`、`repos` 或 `sources` 缩小范围之前，知道命中结果的样子。首先范围会隐藏会告诉你在哪里查找的结果。
- **当索引无话可说时，转到网络。** 权衡、生态系统观点以及任何关于未索引项目的内容都是网络问题。不要强迫它们通过索引，也不要将一般网络页面打扮成主要来源。

## 参见

- [firecrawl-build-search](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-search) — 将开发者索引构建到应用程序中而不是在这里查询
