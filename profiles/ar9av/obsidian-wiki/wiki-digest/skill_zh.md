# Wiki Digest — 知识简报生成器

您正在生成一份人类可读的简报，总结最近的维基活动：学到了什么、更新了什么、出现了哪些主题，以及哪些内容值得回顾。这项技能总结的是*知识*，而非来源——将其视为每周回顾会议，而非摄入状态报告。

## 开始前

**写作配置文件**：在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 的偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_LINK_FORMAT`。
2. **解析用户请求中的时间段**：
   - "daily" / "today" / "yesterday" → 过去 24 小时
   - "weekly" / "this week" / 无参数（默认）→ 过去 7 天
   - "monthly" / "this month" → 过去 30 天
   - ISO 日期，如 "since 2026-05-01" → 自该日期起更新的页面
   - 明确数字，如 "last 14 days" → 那么多天
3. 读取 `$OBSIDIAN_VAULT_PATH/log.md` — 最后 200 行 — 期间内的条目（时间戳为 ISO-8601 前缀行）。
4. 读取 `$OBSIDIAN_VAULT_PATH/hot.md` 获取当前会话上下文。
5. 如果 `$OBSIDIAN_VAULT_PATH/_insights.md` 存在，读取其 **锚点页面** 表格——稍后您将使用它来识别哪些新页面成为了中心枢纽。

## 第 1 步：收集期间内活跃的页面

在 `$OBSIDIAN_VAULT_PATH` 下 Glob 所有 `.md` 文件。跳过特殊/系统文件：
- `index.md`, `log.md`, `hot.md`, `AGENTS.md`, `_insights.md`
- 在 `_meta/`, `_archives/`, `_raw/` 下面的任何文件
- 日志简报页面本身 (`journal/digest-*.md`)

对于每个剩余的页面，读取其 frontmatter：
- `created` — 页面首次写入时间
- `updated` — 最后修改时间

分类：
- **新页面**：`created` 在期间内
- **更新页面**：`updated` 在期间内，但 `created` 在之前
- **未更改**：两个日期都不在期间内 → 跳过

如果活跃页面少于 5 个，请记录并提议扩大范围：*"过去 7 天只有 3 个页面活跃——想要生成月度简报吗？"* 除非用户要求继续，否则在此停止。

对于每个活跃页面，收集：`title`, `category`, `tags`, `summary`（frontmatter 字段）, `lifecycle`, 正文中的任何 `^[ambiguous]` 或 `^[inferred]` 标记。

## 第 2 步：识别主题

从所有活跃页面的标签中统计主题频率：

```
对于新 + 更新页面的每个标签：
  统计有多少个活跃页面包含它
降序排序，取前 5
```

同时读取 `$OBSIDIAN_VAULT_PATH/_meta/taxonomy.md`（如果存在）。标记步骤 1 中未出现的任何标签——这些是新出现的词汇，本期出现的。

记录哪些类别增长最多（concepts/、entities/、skills/、synthesis/、references/ 等）。

## 第 3 步：查找显著的全新连接

扫描新和更新页面中的跨类别维基链接——连接不同知识层的链接。这是本期最具智力趣味的输出。

对于每个活跃页面，提取所有 `[[wikilink]]` 目标。按目标类别的前缀对每个链接进行分类。标记跨类别的链接（例如，一个 `concepts/` 页面链接到一个 `entities/` 页面，或一个 `synthesis/` 页面连接两个主题）。

按有趣程度对候选者进行排名：
- **+3** 如果链接是两个很少连接的类别之间（如果可用，使用 `_insights.md` 桥接数据）
- **+2** 如果目标页面是前 10 个中心枢纽（根据 `_insights.md` 锚点）
- **+2** 如果链接出现在 `synthesis/` 页面中（有意进行跨切）
- **+1** 如果源页面标记为 `^[inferred]`（合成连接，未直接说明）

取前 3–5 个连接。将每个连接写为一句平实的英语：不仅是 "A → B"，而是*为什么这个连接有趣*。

## 第 4 步：浮现未完成的任务

扫描活跃页面和 `_raw/` 以查找未完成的工作：

- **草稿**：具有 `lifecycle: draft` 或 `lifecycle: stub` 的页面
- **模糊主张**：统计所有活跃页面中的 `^[ambiguous]` 标记（不要列出每一个——只需统计数量和哪些页面最多）
- **未提交笔记**：统计 `$OBSIDIAN_VAULT_PATH/_raw/` 中的文件（这里的内容尚未被提升）
- **分类法差距**：步骤 2 中未在 `_meta/taxonomy.md` 中的标签

## 第 5 步：选择推荐的重读

从*现有*（期间前）页面中，根据本周的新上下文，找出 2–3 个值得回顾的页面。

启发式方法：找到与步骤 1 中的活跃页面共享最多标签的期间前页面。这些是基础页面，其主题在本期被扩展——新页面基于它们，但用户可能没有回顾基础。

还包括任何期间前页面，现在有来自活跃页面的 2+ 个新入站链接（它刚刚变得更连接——一个承重迹象）。

为每个推荐提供具体理由：*"[[concepts/attention-mechanism]] — 您的基础页面；本周摄入的三个新论文都扩展了它"*, 而不是仅仅页面标题。

## 第 6 步：生成简报

生成结构化、可扫描的 markdown 报告。标题部分是最重要的——它应该像一份优秀简报的开头，综合实际见解，而不是列出页面名称。

使用 `llm-wiki/SKILL.md` 中的链接格式（链接格式部分）并使用 `OBSIDIAN_LINK_FORMAT`。默认是 `[[wikilink]]`。

```markdown
# Wiki Digest — [时间段标签]
> [N 个新页面 · M 个更新页面 · 时间段：YYYY-MM-DD 至 YYYY-MM-DD]

## 标题

- [具体见解 #1 — 综合实际知识，而不仅仅是“学习了 X”]
- [具体见解 #2]
- [具体见解 #3]

## 新知识

### 新页面 ([数量])
| 页面 | 类别 | 摘要 |
|---|---|---|
| [[concepts/foo]] | 概念 | 来自 frontmatter 的单句摘要 |
| [[entities/bar]] | 实体 | 来自 frontmatter 的单句摘要 |

### 显著更新 ([数量])
| 页面 | 更改内容 |
|---|---|
| [[skills/react-hooks]] | 添加了 useCallback 与异步效果的模式 |

*(如果没有更新，省略此子部分。)*

## 新兴主题

- **#[tag]** ([N 个页面]) — [一句话说明为什么这个主题活跃]
- **#[tag]** ([N 个页面]) — [...]
- **#[NEW TAG]** ([N 个页面]) ⭐ *新词汇——尚未在分类法中*

最活跃的类别：**[category/]** ([N 个页面添加或更新])

## 关键连接

- [[concepts/A]] → [[entities/B]] — [平实的英语解释为什么这个连接有趣]
- [[synthesis/X]] 创建 — 首次连接 [[concepts/Y]] 和 [[concepts/Z]]
- *(最多 5 个连接)*

## 未完成的任务

- **待整理的草稿** ([数量])：[[concepts/foo]], [[concepts/bar]] — 仍处于草稿生命周期
- **模糊主张**：[N] 个 `^[ambiguous]` 标记跨越 [M] 个页面 — 运行 `/wiki-synthesize` 来解决
- **未提交笔记**：[N] 个 `_raw/` 中的文件 — 运行 `/wiki-ingest _raw/` 来提升它们
- **分类法差距**：标签 `#newtag1`, `#newtag2` 已使用但未在分类法中 — 运行 `/tag-taxonomy`

*(省略任何数量为 0 的子部分。)*

## 推荐重读

- [[concepts/X]] — [具体理由：“本周摄入的三个论文都引用了此页面中的同一主张”]
- [[synthesis/Y]] — [具体理由：“本周创建的两个页面引用了它”]
- [[skills/Z]] — [具体理由：“现在有 4 个新入站链接——它已成为一个枢纽”]

---
*由 wiki-digest 生成 · [时间戳] · [N 个页面扫描在 [VAULT_PATH]]*
```

**可见性**：如果页面标记为 `visibility/pii`，则将其从所有表格和连接列表中排除（但在总数中计算，并注明“+ N 私有”）。如果用户明确表示“包含私有页面”或“完整简报”，则正常包含。

## 第 7 步：输出并可选保存

**默认（聊天输出）**：直接打印简报。在末尾，询问：
*"想要我将其保存为 `journal/digest-YYYY-MM-DD.md` 吗？)*

**如果用户以“保存”或“写入”为前缀**（例如，`/wiki-digest save` 或“生成并保存我的每周简报”）：
- 写入 `$OBSIDIAN_VAULT_PATH/journal/digest-YYYY-MM-DD.md`（每周/每月）或 `journal/digest-YYYY-MM-DD-daily.md`（每日）
- 添加 frontmatter：
  ```yaml
  ---
  title: "Wiki Digest — [时间段标签]"
  category: journal
  tags: [digest, meta/review]
  sources: []
  created: TIMESTAMP
  updated: TIMESTAMP
  summary: "每周知识简报：[N 新，M 更新页面]。主要主题：[tag1], [tag2]."
  ---
  ```
- 在 Journal 下更新 `index.md` 中的新条目
- **不要**添加到 `.manifest.json`（简报不是源摄入）

无论哪种方式，都追加到 `log.md`：
```
- [TIMESTAMP] DIGEST period="7d" new_pages=N updated_pages=M themes=T connections=C saved=false
```

## 边缘情况

| 情况 | 处理 |
|---|---|
| 活跃页面少于 5 个 | 提议扩大时间段；仅当用户确认时继续 |
| 空的维库（没有任何页面） | 告知用户先运行摄入；停止 |
| 没有 `_meta/taxonomy.md` | 跳过分类法差距检查；省略 Open Threads 中的该行 |
| 没有 `_insights.md` | 跳过基于枢纽的评分（第 3 步）；仍然生成连接部分 |
| 所有页面都是 `visibility/pii` | 报告“本期 N 个私有页面活跃”且无细节；提供完整模式 |
| 时间段跨越维库重建 | 在简报中注明：“本期维库重建——页面日期反映重建后状态” |

## 备注

- **标题是关键。** 不要列出页面标题——综合实际学习。如果有人本周学习了注意力机制，标题应捕捉见解，而不仅仅是说“添加了 3 个 transformer 页面”。
- **具体说明重读。** “此页面相关”是无用的。 “本周摄入的三个论文都引用了此页面中的同一主张” 是可操作的。
- **这项技能只读取。** 唯一写入是可选的期刊页面和 `log.md` 追加。它不会修改现有的维库页面。
- **不要重复维库状态。** 如果用户问“什么需要摄入”或“有什么差异”，请路由到 `wiki-status`。这项技能回答的是“我学到了什么”，而不是“有什么待办”。
