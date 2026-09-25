# LLM Wiki 本地 API 功能

通过其内置的 HTTP API 与用户本地运行的 LLM Wiki 应用进行交互。这是一个标准的 JSON API — 可以使用您环境中已有的任何 HTTP 工具（`curl`、`fetch`、`requests`、`http` 中间件等）直接调用它。无需安装客户端库，无需学习 SDK。

将维基视为用户一直在整理的**私有、结构化知识库**：页面作为 `wiki/**.md` 存在，原始文档在 `raw/sources/` 下，维基链接形成图谱。

## 调用时机

**仅**在用户明确指向**LLM Wiki**时调用 — 通过应用名称、`wiki` 语境或 `知识库` 语境。具体来说：

- 以“我的**维基** / 我的**知识库** / 我的**知识库** / **LLM Wiki** 对 X 有什么说法”的语境提问
- 要求“搜索我的**维基** / **LLM Wiki** 项目 / 我的**知识库**中的 X”
- 引用维基页面（通过词干/标题）并希望阅读或交叉链接
- 要求获取**维基图谱 / 知识图谱 / 维基概览 / 维基结构**
- 刚刚添加或编辑了 LLM Wiki **源文件夹**下的文件，并希望重新运行摄取 / **重新索引**
- 说“使用我的**维基**作为上下文” / “以我的**维基**为依据” / “检查我的**LLM Wiki**”
- 指名维基项目（通过 ID、绝对路径或 `current`）

**在用户说以下情况时** **不要**调用：

- “搜索我的**笔记**”而无进一步说明 — 可能是 Obsidian / Apple Notes / Notion / Logseq / Bear / 等
- “在我的**笔记本**中查找” — 可能是 Jupyter / OneNote / Notability
- “检查我的**Obsidian / Notion / Roam / Logseq 库**” — 明确是不同的工具
- “查找我的**Anki / Readwise / Pocket**” — 不同的工具
- “搜索我的**文件 / 我的文档文件夹**” — 通用文件系统，不是维基
- 一般世界知识、时事或用户明显想从公开网络获取的内容

当不确定用户指的是哪个知识工具时，询问：“您是指您的 LLM Wiki，还是其他工具？” — 不要在可能是 Obsidian 库的情况下静默调用 LLM Wiki API。

## 快速入门

整个 API 是纯 HTTP + JSON。最快的方式：

```bash
BASE=http://127.0.0.1:19828
TOKEN="${LLM_WIKI_API_TOKEN:-<从设置中粘贴>}"

# 1. 探测状态 — 无需认证
curl -s $BASE/api/v1/health

# 2. 列出项目
curl -s -H "Authorization: Bearer $TOKEN" $BASE/api/v1/projects

# 3. 搜索
curl -s -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"query":"rope embedding","topK":5}' \
  $BASE/api/v1/projects/current/search

# 4. 读取页面
curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/projects/current/files/content?path=wiki/concepts/rope.md"
```

如果您正在编写 TypeScript / JavaScript：

```ts
const res = await fetch("http://127.0.0.1:19828/api/v1/projects/current/search", {
  method: "POST",
  headers: { "Authorization": `Bearer ${process.env.LLM_WIKI_API_TOKEN}`, "Content-Type": "application/json" },
  body: JSON.stringify({ query: "rope embedding", topK: 5 }),
})
const { results } = await res.json()
```

Python 形式相同 — `urllib.request`、`requests`、`httpx`，无论您已经有什么。**不要安装任何新东西。**

## 认证模型

API 是**仅限本地主机**的。令牌是：

1. `LLM_WIKI_API_TOKEN` 环境变量（如果设置，则覆盖 UI）
2. 通过设置 → API 服务器保存的用户 `apiConfig.token`
3. `allowUnauthenticated: true` 模式（无需令牌；罕见，仅用户选择）

始终先检查 `/api/v1/health` — 它返回 `{ enabled, authConfigured, allowUnauthenticated, tokenSource }`。**如果 `authConfigured: false && allowUnauthenticated: false`，请提示用户打开 `设置 → API 服务器 → 生成新令牌`**。未经认证设置，不要继续。

发送令牌的三种等效方式：

```
Authorization: Bearer <令牌>          # 推荐方式
X-LLM-Wiki-Token: <令牌>              # 替代请求头
?token=<URL编码的令牌>              # 查询参数 — 最后手段，会泄露到日志中
```

**永远不要记录或回显令牌。永远不要将令牌放在用户可以在您的输出中看到的任何 URL 中**（Referer / shell 历史记录 / 日志都会泄露它）。

## 标准工作流程

当用户要求“在我的维基中查找”时：

1. **解析项目**（见下文“项目解析”）。
2. **搜索**：`POST /api/v1/projects/{id}/search` 使用 `{ query, topK: 5..10 }` → 排名结果 (`path`, `title`, `snippet`, `score`, `titleMatch`, 可选 `vectorScore`, `images`)。检查 `response.mode` 以了解是否触发了混合检索。
3. **读取顶部命中**：对于每个有希望的命中，`GET /api/v1/projects/{id}/files/content?path=...` 获取完整的 markdown。或者将 `includeContent: true` 传递给搜索以避免往返。
4. **引用 + 回答**：综合基于已读页面的答案。**引用您使用的每个页面的 `path`**，以便用户可以验证并在应用内跳转。

### 读取分数

`score` 字段的尺度取决于 `mode`：

- **`mode: "keyword"`** — 加性关键词分数。文件名精确命中约为 200；标题中包含短语约为 50+；词袋落在个位数。将低于 ~5% 的顶部结果视为低置信度。
- **`mode: "hybrid"` 或 `"vector"`** — RRF（递归秩融合）分数，通常在 **0.015–0.035** 范围内。绝对数字很小；相对排序才重要。如果需要，可以使用每个结果的 `vectorScore`（余弦相似度 0–1）来“嵌入匹配强度如何”。

不要在模式之间应用固定的分数阈值。按 `score` 降序排序，并依赖相对差距。

### 项目解析

`{id}` 在每个项目范围端点中接受**四种形式**：

| 形式 | 使用时机 | 示例 |
|---|---|---|
| `current`（字面量） | 默认用于“我的维基 / 我的知识库 / 这个项目 / 这个维基”。用户指的是桌面 UI 中打开的内容。 | `/api/v1/projects/current/search` |
| UUID | 用户粘贴了项目 ID，或您之前将名称解析为 ID 并希望重用。 | `/api/v1/projects/a0e90b29-fcf3-4364-9502-8bd1272de820/files` |
| 绝对文件系统路径（URL 编码） | 用户命名了路径（例如 `~/notes/research`）。当用户有多个名称相似的项目时很有用。 | `/api/v1/projects/%2FUsers%2Fme%2Fwiki%2Fresearch/files` |
| 项目名称 | **不直接支持**。您必须首先 `GET /api/v1/projects`，通过 `name` 找到匹配项，然后使用该项目的 `id`。 |

**决策树**用户说了什么：

```
"我的维基" / "我的 知识库" / "这个维基" / "这个项目" / 未指定
    → 使用 `current`

"我的 Research 项目" / "在 Reading"
    → GET /api/v1/projects
    → 名称匹配（不区分大小写的子字符串 `name`）
    → 使用结果 `id`
    → 如果 0 个匹配：告诉用户，列出可用名称，只有在他们确认的情况下才回退到 `current`
    → 如果 2+ 个匹配：要求用户消除歧义，引用两个名称 + 路径

"位于 /Users/me/foo 的项目"
    → URL 编码路径，直接使用
    → 如果 API 返回 404，项目未注册 — 列出并让用户选择

"项目 a0e90b29-…"
    → 直接使用 UUID 字面量
```

缓存解析后的 `id` 以便整个对话 — 没有必要为每次调用都 `GET /projects`。但如果用户在对话中途切换上下文（“现在查看我的 Reading 项目”），则需要重新解析。

当用户对项目保持沉默时，**默认为 `current`** 并提及一次：*"正在查看您的活动项目（Research Notes）…"*。这可以避免跨项目意外。

对于图谱 / 交叉引用问题：

- `GET /api/v1/projects/{id}/graph?limit=200` → `{ nodes: [{id, label, nodeType, path, linkCount}], edges: [{source, target, weight}] }`
- 通过 `?q=term`（ID/标签的子字符串，不区分大小写）和 `?nodeType=entity|concept|...` 进行过滤

对于“我添加了新文档”请求：

- `POST /api/v1/projects/{id}/sources/rescan` → 返回 `{ queue: { tasks }, changedTasks: [...] }`。告诉用户有多少文件已更改。实际摄取通过桌面队列异步运行。

## 端点契约（v1）

| 方法 | 路径 | 备注 |
|---|---|---|
| GET | `/api/v1/health` | 无需认证。返回 `{ ok, status, version, enabled, authRequired, authConfigured, allowUnauthenticated, tokenSource }`。 |
| GET | `/api/v1/projects` | 列出项目。每个：`{ id, name, path, current }`。 |
| GET | `/api/v1/projects/{id}/files?root=wiki\|sources\|all&recursive=true&maxFiles=2000` | 文件树 `{ name, path, isDir, size, children }`。最多 10000 个节点（413）。 |
| GET | `/api/v1/projects/{id}/files/content?path=wiki/foo.md` | 仅限文本文件（md/mdx/txt/json/yaml/yml/csv/html/htm/xml/rtf/log）。最大 2 MB。二进制文件为 415，文件过大为 413，路径超出范围为 403。 |
| POST | `/api/v1/projects/{id}/search` | 正文：`{ "query": "...", "topK": 10, "includeContent": false }`。**混合（关键词 + 向量）** 当用户在设置中配置了嵌入时；否则回退到关键词仅。响应包含 `mode: "keyword" \| "vector" \| "hybrid"`，以及 `tokenHits` / `vectorHits` 和每个结果的 `vectorScore`。空查询 → 400。 |
| GET | `/api/v1/projects/{id}/graph?q=&nodeType=&limit=200` | 来自 `wiki/*.md` 的维基链接图谱。限制为 1000。 |
| POST | `/api/v1/projects/{id}/sources/rescan` | 触发使用用户源监视配置的后端重新扫描。返回重新扫描后的队列 + 实际更改的任务。 |
| POST | `/api/v1/projects/{id}/chat` | **501** — v1 中未实现。不要调用。 |

`{id}` 接受 UUID、绝对文件系统路径（URL 编码）或字面字符串 `current`。

## 错误处理

始终将状态码视为契约：

| 状态 | 含义 | 应该怎么办 |
|---|---|---|
| 200 | OK | 使用 `body.ok === true` 双保险；负载在同一对象中。 |
| 400 | 请求错误 | 显示 `body.error`。典型：空 `query`、无效 `?root=`、正文过大。 |
| 401 | 未授权 | 令牌缺失/错误。提示用户在设置 → API 服务器中设置/重新生成。 |
| 403 | 禁止 | 路径遍历或超出范围（例如 `../app-state.json`）。不要重试相同的路径。 |
| 404 | 未找到 | 未知项目 ID 或未知路由。对于未知项目，首先列出项目以恢复。 |
| 405 | 禁止方法 | 错误的 HTTP 请求方法。 |
| 413 | 负载过大 | 文件 > 2 MB，文件树 > maxFiles，或请求正文 > 1 MB。建议缩小范围。 |
| 415 | 不支持的媒体 | 二进制或非 UTF-8 文件内容。API 仅支持文本。 |
| 429 | 请求过多 | 速率限制（每秒 120 请求）。至少退避 1 秒。 |
| 500 | 内部错误 | 记录 + 报告；不要循环。 |
| 501 | 未实现 | `/chat` 桥接。不要重试。 |
| 503 | 服务不可用 | 两种类型：API 关闭（`error` 包含 "disabled"）；飞行中限制（64）达到（"忙碌"）。至少退避 2 秒。 |

如果 HTTP 调用本身失败（连接拒绝 / ENOTFOUND）：桌面应用**未运行**。提示用户："启动 LLM Wiki，然后重试。"

## 礼节

- **引用路径。** 当您使用维基内容回答时，命名页面：`(from wiki/concepts/rope.md)`。用户使用这些来验证并在应用内跳转。
- **默认为只读。** 只有 `sources/rescan` 修改状态；其他都是读取。不要发明写端点 — v1 中不存在。
- **除非要求，否则不要转储完整页面。** 提要 + 路径通常足够。仅在推理确实需要时才拉取完整内容。
- **尊重项目边界。** 当前项目是用户的活动上下文。不要静默切换项目。
- **尊重速率限制。** 每秒 120 请求对于顺序工作绰绰有余，但并行页面读取可能接近限制。在 API 允许的地方批量处理（搜索时 `includeContent: true` 可避免 N+1 读取）。
- **永远不要泄露令牌。** 请求头是安全的；查询参数和您自己的输出文本不安全。

## 参见

- `api-reference.md` — 完整端点形状，带请求 / 响应示例
- `examples.md` — 常见对话模式映射到直接的 `curl` / `fetch` 序列
- `README.md` — 人类设置说明（令牌生成、端口冲突、故障排除）
