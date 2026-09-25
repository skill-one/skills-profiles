# Wiki Dashboard — 动态 Vault 视图

提供两种工具：**Obsidian Bases**（原生，GUI 驱动，无需插件）和 **Dataview**（社区插件，SQL 类似，功能更强大）。检查用户使用的是哪种工具，并优先选择 Bases，除非他们要求使用 Dataview 或需要 GROUP BY / 计算列。

## 开始前

**撰写配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
仅将 `WRITING.md` 偏好应用于可选的 Markdown 仪表板文本；`.base` 语法保持不变。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 往上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会给出 `OBSIDIAN_VAULT_PATH`。
2. 阅读 `$OBSIDIAN_VAULT_PATH/index.md` 以了解现有的分类和页面。
3. 如果未指定要查看的内容，请询问用户他们想查看什么 — 文件夹、标签、分类、日期范围？
4. 如果不确定使用哪种工具，请询问用户是否安装了 Dataview。

---

## 选项 A — Obsidian Bases (`.base` 文件)

Bases 是定义 Vault 笔记动态视图的 YAML 文件。Obsidian 1.8+ 原生支持，无需插件。

### 官方规范模式

顶级键：

```yaml
filters:      # 应用于所有视图的全局过滤器（在 and/or/not 下方的表达式字符串）
formulas:     # 命名的计算属性 — 引用为 formula.<name>
properties:   # 每个属性的显示配置 — 设置列标题的 displayName
summaries:    # 聚合公式（例如 mean、sum）
views:        # 视图定义数组（必需）
```

`views:` 中的每个项目：

```yaml
views:
  - type: table          # table | list | cards | map
    name: "View Name"    # 显示标签
    limit: 50            # 可选的最大行数
    order:               # 列显示顺序（属性/公式名称列表）
      - file.name
      - note.updated
    groupBy:             # 分组 — 位于视图内部，而不是顶级
      property: note.tags
      direction: ASC     # ASC | DESC
    filters:             # 视图特定过滤器（与全局过滤器合并）
      and:
        - 'note.status != "done"'
    summaries:
      formula.myFormula: Average
```

### 过滤器语法 — 关键

**过滤器使用表达式字符串，而不是类型化对象。** 始终用 `and:`, `or:`, 或 `not:` 包围 — 空列表会导致解析错误 "may only have one of and/or/not keys"。

```yaml
# 正确
filters:
  and:
    - file.inFolder("concepts")

# 错误 — 类型化对象（解析错误）
filters:
  - type: folder
    folder: concepts
```

过滤器支持嵌套：

```yaml
filters:
  or:
    - file.hasTag("book")
    - and:
        - file.inFolder("concepts")
        - file.hasTag("research")
    - not:
        - file.hasTag("archived")
```

### 属性名称规范

不同上下文使用不同的命名 — 从 Obsidian 的自动格式化行为中确认：

| 上下文 | Frontmatter 字段 `tags` | 文件名 | 公式 |
|---|---|---|---|
| `properties:` 键 | `note.tags` | `file.name` | `formula.<name>` |
| `order:` 值 | `tags`（裸） | `file.name` | `formula.<name>` |
| `groupBy.property:` | `tags`（裸） | `file.name` | — |
| `filters:` 表达式 | `file.hasTag(...)` / `note.tags` | `file.name` | `formula.<name>` |
| `formulas:` 表达式 | `note.tags`, `note.updated` | `file.name` | — |

### 基本表格 — 文件夹过滤器

```yaml
filters:
  and:
    - file.inFolder("concepts")
properties:
  file.name:
    displayName: Page
  note.tags:
    displayName: Tags
  note.summary:
    displayName: Summary
  note.updated:
    displayName: Updated
views:
  - type: table
    name: Table
    order:
      - file.name
      - tags
      - summary
      - updated
```

### 卡片视图 — 文件夹过滤器

```yaml
filters:
  and:
    - file.inFolder("entities")
properties:
  file.name:
    displayName: Entity
  note.title:
    displayName: Full Name
  note.tags:
    displayName: Tags
  note.summary:
    displayName: Summary
views:
  - type: cards
    name: Cards
    order:
      - file.name
      - title
      - tags
      - summary
```

### 分组属性 — `groupBy` 位于视图内部

当 `groupBy` 设置时，**从 `order:` 中省略该属性** — 它成为分组标题行，同时将其作为列添加会导致重复。

```yaml
filters:
  and:
    - file.inFolder("concepts")
properties:
  file.name:
    displayName: Concept
  note.summary:
    displayName: Summary
  note.updated:
    displayName: Updated
views:
  - type: table
    name: By Domain
    groupBy:
      property: tags        # 裸属性名称，无 note. 前缀
      direction: ASC
    order:
      - file.name           # 不要在此处包含 tags — 它已经是分组标题
      - summary
      - updated
```

### 标签过滤器

```yaml
filters:
  and:
    - file.hasTag("machine-learning")
properties:
  file.name:
    displayName: Page
  note.category:
    displayName: Category
  note.summary:
    displayName: Summary
views:
  - type: table
    name: Table
    order:
      - file.name
      - category
      - summary
```

### 多过滤器（文件夹 AND 标签）

```yaml
filters:
  and:
    - file.inFolder("projects")
    - file.hasTag("active")
properties:
  file.name:
    displayName: Project
  note.summary:
    displayName: Summary
  note.updated:
    displayName: Last Updated
views:
  - type: cards
    name: Cards
    order:
      - file.name
      - summary
      - updated
```

### OR 过滤器（两个文件夹）

```yaml
filters:
  or:
    - file.inFolder("concepts")
    - file.inFolder("entities")
properties:
  file.name:
    displayName: Page
  note.category:
    displayName: Category
  note.updated:
    displayName: Updated
views:
  - type: table
    name: Table
    order:
      - file.name
      - category
      - updated
```

### 通过公式计算列

```yaml
filters:
  and:
    - file.inFolder("concepts")
formulas:
  days_stale: "floor((now() - note.updated) / 86400000)"
properties:
  file.name:
    displayName: Page
  note.updated:
    displayName: Updated
  formula.days_stale:
    displayName: Days Stale
views:
  - type: table
    name: Stale
    order:
      - file.name
      - updated
      - formula.days_stale
```

### 过滤器表达式参考

| 表达式 | 它的作用 |
|---|---|
| `file.inFolder("path")` | 该文件夹中的页面 |
| `file.hasTag("tag")` | 带有该标签的页面（无 `#` 前缀） |
| `file.hasLink("Note Name")` | 链接到笔记的页面 |
| `file.name == "note-name"` | 完全匹配文件名 |
| `file.ext == "md"` | 按扩展名过滤 |
| `note.propertyName` | 任何 frontmatter 属性 |
| `formula.formulaName` | 命名公式结果 |
| `now()` | 毫秒级当前时间戳 |

> **关于 Obsidian UI 生成的格式：** 当 Obsidian 的 GUI 写入或重新格式化 `.base` 文件时，它可能会输出一个简化的简写格式，其中包含顶级 `columns:`, `sort:`, 和 `view:` 键，而不是规范模式。该格式也能工作 — Obsidian 接受两者。手动编写的文件应使用上述规范模式。

---

## 选项 B — Dataview (社区插件)

Dataview 在任何笔记的 ` ```dataview ``` ` 代码块中使用类似 SQL 的查询语言。对于计算列、GROUP BY 和跨文件夹查询，比 Bases 更强大。

### 基本表格 — 文件夹

````markdown
```dataview
TABLE
  tags AS "Tags",
  summary AS "Summary",
  file.mtime AS "Last Modified"
FROM "concepts"
SORT file.mtime DESC
```
````

### 带有可点击链接的表格（TABLE WITHOUT ID）

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Entity",
  tags AS "Tags",
  summary AS "Summary"
FROM "entities"
SORT file.name ASC
```
````

### GROUP BY — 分组后使用 `rows.` 前缀

在 `GROUP BY` 之后，必须用 `rows.` 前缀引用单个文件属性 — 否则列将为空或出错。

````markdown
```dataview
TABLE WITHOUT ID
  rows.file.link AS "Concept",
  rows.summary AS "Summary"
FROM "concepts"
GROUP BY tags[0] AS "Domain"
```
````

### 过期页面 — 使用 `file.mtime` 进行日期计算

避免 `choice(updated, date(updated), file.mtime)` — `updated` frontmatter 中的混合日期格式会导致算术错误。`file.mtime` 始终是有效的 DateTime。

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Page",
  category AS "Type",
  file.mtime AS "Last Modified",
  (date(today) - file.mtime).days + " days" AS "Age"
FROM "concepts" OR "entities" OR "projects"
WHERE file.name != file.folder
WHERE (date(today) - file.mtime).days > 30
SORT (date(today) - file.mtime).days DESC
```
````

### 多文件夹查询

````markdown
```dataview
TABLE
  summary AS "Summary",
  file.mtime AS "Last Modified"
FROM "projects"
WHERE file.name != file.folder
SORT file.mtime DESC
```
````

### Dataview 参考

| 子句 | 使用 |
|---|---|
| `FROM "folder"` | 文件夹中的所有笔记 |
| `FROM #tag` | 带有标签的所有笔记 |
| `FROM "a" OR "b"` | 两个文件夹的并集 |
| `WHERE file.name != file.folder` | 排除文件夹索引页面 |
| `GROUP BY field AS "Label"` | 分组行 — 此后使用 `rows.` 引用属性 |
| `SORT field DESC` | 排序方向 |
| `file.link` | 可点击的 wikilink |
| `file.mtime` | 最后修改时间（始终是有效的 DateTime） |
| `(date(today) - file.mtime).days` | 最后修改以来的天数 |

---

## 第 3 步：写入文件

**Bases：** 目标路径 `$OBSIDIAN_VAULT_PATH/_meta/<dashboard-name>.base`

**Dataview：** 直接将查询写入任何 `.md` 笔记。在 `$OBSIDIAN_VAULT_PATH/_meta/dashboard.md` 中创建一个专用仪表板笔记，用于多部分视图，效果很好。

Slug 示例：
- "All concepts" → `_meta/concepts-index.base`
- "Recent ingests" → `_meta/recent-ingests.base`
- "Project overview" → `_meta/projects-overview.base`
- "Stale pages" → `_meta/stale-pages.base`
- "Full dashboard" → `_meta/dashboard.md`

如果 `_meta/` 不存在，请创建它。

## 第 4 步：嵌入 Bases（可选）

要在笔记中嵌入 `.base`：

```markdown
## Entities
![[_meta/entities-tracker.base]]
```

修改现有笔记前请询问。

## 第 5 步：更新跟踪

追加到 `$OBSIDIAN_VAULT_PATH/log.md`：
```
- [TIMESTAMP] WIKI_DASHBOARD name="<slug>" tool=bases|dataview view=<type> filter="<description>"
```

无需清单或索引更新 — 仪表板是动态查询，不是静态页面。

## 常见仪表板配方

| 仪表板 | 最佳工具 | 它显示的内容 |
|---|---|---|
| **内容索引** | Bases 或 Dataview | 按分类分组的所有页面，按更新排序 |
| **实体追踪器** | Bases（卡片） | 实体页面作为视觉卡片画廊 |
| **按领域分类的概念** | Dataview | 使用 GROUP BY 按第一个标签分组的概念 |
| **摄取日志** | 任意 | 按 `created` 日期排序的页面 |
| **过期内容** | Dataview | 30 天以上未修改的页面及天数 |
| **项目概述** | 任意 | 带最后同步日期的项目页面 |
| **研究追踪器** | Dataview | 标记为 `research` 的综合页面 |

## 质量检查清单

- [ ] Bases：过滤器使用 `and:`/`or:`/`not:` 下方的表达式字符串，从不使用类型化对象
- [ ] Bases：`groupBy` 位于视图定义内部 — 不是顶级键
- [ ] Bases：列标题通过 `properties: <name>: displayName: "..."` 设置，不是 `columns: [{title}]`
- [ ] Bases：`formulas:` 用于计算列，在 `order/properties` 中引用为 `formula.<name>`
- [ ] Dataview：GROUP BY 查询使用 `rows.property` 而不是裸 `property`
- [ ] Dataview：日期计算使用 `file.mtime`，而不是 `choice(updated, ...)`
- [ ] 文件写入到 `_meta/`，具有描述性 slug
- [ ] `log.md` 更新
- [ ] 告知用户如何嵌入 Bases (`![[_meta/<name>.base]]`) 或打开仪表板笔记

## QMD 在 Vault 写入后刷新

QMD 是搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写 Vault Markdown 后运行它。如果 QMD 刷新失败，不要回滚 Vault 更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`
