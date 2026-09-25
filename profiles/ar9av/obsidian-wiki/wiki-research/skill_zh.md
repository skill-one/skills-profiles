# Wiki Research — 自主多轮研究

你正在针对某个主题运行自主研究循环，综合你发现的内容，并将结果存入 Obsidian 知识库作为永久知识。

## 开始前

**写作配置：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 的偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_LINK_FORMAT`（默认：`wikilink`）。
2. 阅读 `$OBSIDIAN_VAULT_PATH/index.md` 以了解知识库中已有的内容 — 不要重新研究知识库已很好地涵盖的主题
3. 如果存在 `$OBSIDIAN_VAULT_PATH/hot.md`，请阅读它 — 它会展示最近的上下文
4. 如果存在 `$OBSIDIAN_VAULT_PATH/references/research-config.md`，请检查它 — 它可能定义了来源偏好、要跳过的域名或此知识库的置信度规则
5. 如果存在 `$OBSIDIAN_VAULT_PATH/references/research-backends.md`，请检查它 — 它注册了可选的 CLI 获取后端（社交媒体、视频文本、付费 API 等）。将可用的后端加载到本次会话的工作状态中。

在生成的页面中编写内部链接时，使用 `llm-wiki/SKILL.md`（链接格式部分）中的 `OBSIDIAN_LINK_FORMAT` 值应用链接格式。

如果研究主题不明确，请与用户确认。然后继续。

## 研究配置（可选）

如果知识库中存在 `references/research-config.md`，请阅读并应用其定义的任何规则：
- 来源偏好（例如，优先学术来源，避免某些域名）
- 要跳过的域名
- 置信度评分调整
- 主题特定约束

如果该文件不存在，则使用默认值。

## 研究后端（可选）

如果知识库中存在 `references/research-backends.md`，请在开始研究之前加载它。它定义了零个或多个作为 YAML 列表的 CLI 获取后端：

```yaml
backends:
  - name: yt-dlp-transcript      # 友好的标签
    binary: yt-dlp                # CLI 二进制文件（使用 `command -v` 检查）
    invoke: "yt-dlp --skip-download --write-auto-sub --sub-lang en --sub-format json3 -o /tmp/ytvid '{url}'"
    when_to_use: YouTube 视频URL、视频文本
    cost_tier: free               # free | paid
    env_key: ""                   # 付费层级所需的 env 变量（空 = 始终启用）
    output: text                  # json | text | markdown

  - name: perplexity-sonar
    binary: perplexity
    invoke: "perplexity search '{query}'"
    when_to_use: 需要跨来源聚合的深度合成查询
    cost_tier: paid
    env_key: PERPLEXITY_API_KEY   # 如果未设置则跳过
    output: text
```

**后端可用性检查（会话开始时运行一次）：**
- 对于每个后端：`command -v <binary> 2>/dev/null` — 如果未找到，则标记为不可用并在运行摘要中注明
- 对于 `paid` 后端：还检查 `$env_key` 是否非空 — 如果未设置，则标记为不可用并注明
- 构建一个 *活动后端* 列表（可用性 + 密钥门控检查通过）以用于第 1 轮和第 2 轮

**调用规则（研究期间每个角度/URL）：**
- 将 `{url}` 或 `{query}` 在 `invoke` 模板中替换为当前的 URL 或搜索查询
- 捕获标准输出；如果退出代码非零 → 跳过此后端，记录简短错误，继续
- 将后端输出折叠到相同的声明/概念/实体/矛盾提取中，引用后端返回的来源 URL（或查询模式的后端的查询字符串）
- 后端失败永远不会中止研究运行 — 始终回退到 `WebSearch`/`WebFetch`

**免费优先排序：** 对于每个角度，先评估 `free` 后端，然后再评估 `paid` 后端。如果一个免费后端返回了足够的内容，则可以跳过同一角度的付费后端。

**没有 `research-backends.md`** → 完全跳过本节；行为与今天相同。

### 启动器注册模板

如果用户要求示例注册，请提供 `$VAULT/references/research-backends.md` 中的此文件：

```yaml
# 可选的 CLI 后端用于 wiki-research。删除不需要的行。
# 技能文档：.skills/wiki-research/SKILL.md — Research Backends 部分
backends:
  # --- free / local ---
  - name: defuddle-fetch
    binary: defuddle
    invoke: "defuddle '{url}'"
    when_to_use: 任何 URL — 比单独使用 WebFetch 更干净的提取
    cost_tier: free
    env_key: ""
    output: markdown

  - name: yt-dlp-transcript
    binary: yt-dlp
    invoke: "yt-dlp --skip-download --write-auto-sub --sub-lang en --sub-format json3 -o /tmp/ytvid '{url}'"
    when_to_use: YouTube 视频URL用于文本提取
    cost_tier: free
    env_key: ""
    output: text

  # --- paid / gated (当 env key 未设置时跳过) ---
  - name: perplexity-sonar
    binary: perplexity
    invoke: "perplexity search '{query}'"
    when_to_use: 需要跨来源聚合的深度合成查询
    cost_tier: paid
    env_key: PERPLEXITY_API_KEY
    output: text
```

## 第 1 轮 — 广泛调查

**目标：** 获取主题的广泛地图。

1. 将主题分解为 **3-5 个不同的角度**（例如，对于“向量数据库”：它们是什么，何时使用它们，领先的实现，权衡，生产中的陷阱）
2. 对于每个角度，运行 **2-3 个 `WebSearch` 查询**，使用不同的措辞
3. 对于每个角度的前 2-3 个结果，使用 `WebFetch`（如果可用则使用 `defuddle <url>` — 更干净的提取）获取内容。对于每个 URL，还调用任何 *活动后端*，其 `when_to_use` 匹配（例如，一个 YouTube URL 触发 `yt-dlp-transcript`）；将它们的输出与 `WebFetch` 结果一起折叠到提取中，引用后端返回的来源 URL。
4. 从每个获取的页面中提取：
   - **关键声明** — 来源明确说明的内容
   - **概念** — 概念、术语、框架
   - **实体** — 提到的工具、人员、组织
   - **矛盾** — 来源相互矛盾的地方

跟踪已涵盖的内容和缺失的内容。

## 第 2 轮 — 填补空白

**目标：** 填补第 1 轮留下的空白。

回顾第 1 轮的产出：
- 来源提出了哪些问题但未回答？
- 来源在哪里相互矛盾？
- 哪些角度覆盖不足？

运行 **最多 5 个有针对性的搜索**，专门解决这些空白。优先考虑原始来源、官方文档和权威分析，而不是链接聚合器。对于填补空白查询，还调用任何 *活动查询模式后端*（例如，`perplexity-sonar`），通过将 `{query}` 替换到它们的 `invoke` 模板中 — 将结果折叠到提取中，并将后端名称作为引用上下文。
将发现结果添加到你的工作集中。更新矛盾列表。

## 第 3 轮 — 综合检查

**目标：** 解决矛盾；确认深度足够。

如果重大矛盾仍未解决：
- 运行一次最终的针对性遍历（2-3 个搜索）以找到权威的解决方案
- 如果无法解决，则在综合页面中明确标记矛盾

如果矛盾较小或主题在第 2 轮后感觉已充分覆盖，则跳过额外搜索并继续存档。

**停止条件：** 达到深度或完成 3 轮 — 不要无限循环。

## 存档 — 编写 Wiki 页面

将所有发现结果组织到四个输出区域中的 Wiki 页面中：

### 1. sources/ — 每个主要参考一个页面

对于每个重要来源（总共 4-8 个页面）：

```yaml
---
title: >-
  <来源标题>
category: references
tags: [<2-4 域标签>]
sources:
  - "<URL>"
source_url: "<URL>"
created: <ISO-8601 时间戳>
updated: <ISO-8601 时间戳>
summary: >-
  <1-2 句话描述此来源涵盖的内容，≤200 字符>
provenance:
  extracted: 0.X
  inferred: 0.X
  ambiguous: 0.X
base_confidence: <0.17 + 0.5 × classify(url) for a single source>
lifecycle: draft
lifecycle_changed: <ISO 日期今天>
---
```

正文：标题、URL、涵盖的内容、关键声明（带来源标记）、限制。

### 2. concepts/ — 每个实质性概念一个页面

对于每个来源中出现的重大概念：

标准概念前文 + 正文。将概念相互链接并链接到来源页面。

### 3. entities/ — 工具、组织、人员

对于遇到的每个重大实体（工具、库、公司、关键作者）：

标准实体前文。链接回使用该实体的概念和出现该实体的来源。

### 4. synthesis/Research: [主题].md — 主合成

主要输出：所有发现的结构的综合。

```yaml
---
title: >-
  Research: <主题>
category: synthesis
tags: [<3-5 域标签>, research]
sources: [<来源 URL 或页面路径列表>]
created: <ISO-8601 时间戳>
updated: <ISO-8601 时间戳>
summary: >-
  <主题的 N 轮研究综合。涵盖 ≤200 字符的核心发现>
provenance:
  extracted: 0.X
  inferred: 0.X
  ambiguous: 0.X
base_confidence: <min(N_unique_sources/3,1.0)×0.5 + avg_source_quality×0.5>
lifecycle: draft
lifecycle_changed: <ISO 日期今天>
---

# Research: <主题>

## 概述
<2-4 句话的执行摘要，概述研究发现了什么>

## 关键发现
<带 [[来源页面]] 引用的最重要声明列表>

## 核心概念
<创建的概念页面链接，带一句话描述>

## 实体和工具
<实体页面链接，带一句话描述>

## 矛盾和开放问题
<来源相互矛盾的地方或研究达到限制的地方>

## 参考的来源
<所有来源页面的链接列表>
```

## 交叉链接

存档所有页面后：
- 每个概念页面应至少链接到 2 个来源页面
- 每个来源页面应链接到它所提供信息的概念页面
- 综合页面应链接到所有生成的概念、实体和来源页面

检查 `index.md` 以查找相同主题的现有页面 — 合并到现有页面而不是创建重复页面。

## 更新跟踪文件

**`.manifest.json`** — 添加一个 `research` 条目：
```json
{
  "type": "research",
  "topic": "<主题>",
  "researched_at": "TIMESTAMP",
  "rounds_completed": 3,
  "sources_fetched": N,
  "pages_created": ["..."],
  "pages_updated": ["..."]
}
```

一次锁定调用更新索引、日志和热缓存：

```bash
obsidian-wiki memory sync WIKI_RESEARCH \
  topic="<主题>" rounds=<N> sources_fetched=<N> \
  pages_created=<M> backends_used="<name,...|none>" \
  --takeaways "<研究主题及其核心发现，一句话>"
```

**不要** 在日志字段中列出你创建的每个页面 — `memory sync` 从磁盘合并索引，而巨大的字段只会挤占热缓存。如果研究正在进行中，请记录它：`obsidian-wiki memory todo add "<开放问题>" --origin synthesis/<页面>.md`。

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令会获取锁，以防止并行写入者覆盖你的更新。

有关完整过程的详细信息，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 质量检查清单

- [ ] 完成 3 轮（或在足够深度处停止）
- [ ] 存在 `synthesis/Research: [主题].md` 综合页面
- [ ] 为主要参考编写了来源页面
- [ ] 为重要项目编写了概念和实体页面
- [ ] 在综合页面中标记了矛盾
- [ ] 所有页面都已交叉链接
- [ ] 更新了 `index.md`、`log.md`、`hot.md`、`.manifest.json`
- [ ] 报告后端摘要：哪些后端处于活动状态，哪些被跳过（不可用二进制文件 / 未设置密钥 / 错误），以及原因

## QMD 刷新存档写入后

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，请跳过此步骤。仅在技能写入或重写了知识库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚知识库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出说需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或者，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<页面>.md" -l 5
```

记录一个：
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION 未设置`
- `QMD skipped: qmd CLI 不可用`
- `QMD failed: <简短错误摘要>`
