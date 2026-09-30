---
name: graph-colorize
description: 为 Obsidian 图形视图按颜色编码，通过重写 `.obsidian/graph.json` 中的 `colorGroups`。当用户说“给我的图形上色”、“为 Obsidian 编色”、“给图形上色”、“按标签为图形上色”、“按类别上色”、“在图形中突出显示可见性”、“让图形变得多彩”、“在图形中区分标签”，或希望 Obsidian 图形视图中的节点按标签、文件夹或可见性着色时，使用此功能。从仓库的实际标签/类别生成 `colorGroups` 数组，并将其合并到现有的 graph.json 中，而不会覆盖其他图形设置。始终先进行备份。
---

# 图形着色 — 为 Obsidian 图形视图添加颜色编码

您正在重写 `$OBSIDIAN_VAULT_PATH/.obsidian/graph.json`，以便 Obsidian 的图形视图能够根据标签、文件夹或可见性对节点进行着色。

Obsidian 将图形设置存储在 `<vault>/.obsidian/graph.json` 中。`colorGroups` 数组是一个 `{query, color}` 对列表；每个节点将匹配第一个查询。查询使用 Obsidian 的搜索语法：`tag:#foo`、`path:"concepts"`、`file:foo` 等。颜色是 `{"a": 1, "rgb": <packed-int>}`，其中整数是 `(R << 16) | (G << 8) | B`。

## 开始前

1. **解析配置** — 按照 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这将提供 `OBSIDIAN_VAULT_PATH`。
2. 确认 `$OBSIDIAN_VAULT_PATH/.obsidian/` 存在。如果不存在，该仓库从未在 Obsidian 中打开过 — 请用户在 Obsidian 中打开仓库一次，然后重新运行。
3. **如果 Obsidian 可能正在运行，则警告用户**：Obsidian 在关闭时会覆盖 `graph.json`。告诉他们先关闭仓库，或者在重新加载（Cmd/Ctrl+R）时准备好重新加载（Cmd/Ctrl+R），并在重新加载之前不要触摸图形设置。

## 第 1 步：选择模式

根据用户的措辞推断模式。如果模糊不清，则默认为 **按标签**。

| 用户意图 | 模式 |
|---|---|
| "按标签着色"、"给我的图形着色"、"让它多彩"（默认） | `by-tag` |
| "按文件夹着色"、"按类别着色"、"按目录着色" | `by-category` |
| "突出显示可见性"、"在图形中显示内部/PII"、"可见性颜色" | `by-visibility` |
| 用户提供显式映射（`tag:#foo = red`，或 JSON 块） | `custom` |
| "组合标签和可见性" / "两者" | `combined`（可见性优先，然后是标签） |

## 第 2 步：构建 `colorGroups` 数组

### 调色板（10 种不同的、无障碍的颜色）

按顺序使用。如果组数多于颜色数，则循环并通过对亮度进行约 20% 的调整（通过第二次遍历）来增加明度 — 或者直接限制为 10 个并告诉用户其余的标签共享 "其他" 颜色。

| # | 十六进制 | rgb（打包整数） | 角色 |
|---|---|---|---|
| 0 | `#4E79A7` | `5142951` | 蓝色 |
| 1 | `#F28E2B` | `15896107` | 橙色 |
| 2 | `#E15759` | `14767961` | 红色 |
| 3 | `#76B7B2` | `7780786` | 青色 |
| 4 | `#59A14F` | `5873999` | 绿色 |
| 5 | `#EDC948` | `15583048` | 黄色 |
| 6 | `#B07AA1` | `11565217` | 紫色 |
| 7 | `#FF9DA7` | `16751527` | 粉色 |
| 8 | `#9C755F` | `10253663` | 棕色 |
| 9 | `#BAB0AC` | `12234924` | 灰色 |

每个颜色都包装为 `{"a": 1, "rgb": <int>}`。

### 模式：`by-tag`

1. 使用 glob `$VAULT_PATH/**/*.md` 排除 `_archives/`、`_raw/`、`.obsidian/`、`node_modules/`、`index.md`、`log.md`、`_insights.md`。
2. 解析每个页面的 frontmatter `tags`。统计每个标签的使用频率。
3. **从频率列表中删除 `visibility/*` 标签** — 它们是保留的系统标签，仅在 `by-visibility` 或 `combined` 模式下处理。
4. 取使用频率最高的前 10 个标签。如果有少于 10 个唯一标签，则使用所有标签。
5. 对于索引为 `i` 的每个标签 `T`：发出 `{"query": "tag:#T", "color": palette[i]}`。
6. 可选地，在末尾添加一个最终捕获项，用于未标记的页面：`{"query": "-[\"tag\":]", "color": palette[9]}` — **跳过**，如果颜色槽 9 已经被真实标签占用。

### 模式：`by-category`

使用七个仓库顶级文件夹，按此固定顺序，以便颜色在多次运行中保持稳定：

| 文件夹 | 颜色索引 |
|---|---|
| `concepts` | 0（蓝色） |
| `entities` | 1（橙色） |
| `skills` | 2（红色） |
| `references` | 3（青色） |
| `synthesis` | 4（绿色） |
| `projects` | 5（黄色） |
| `journal` | 6（紫色） |

为每个存在且至少包含一个 `.md` 文件的文件夹发出一个条目。每个条目是：

```json
{"query": "path:\"<folder>\"", "color": {"a": 1, "rgb": <int>}}
```

### 模式：`by-visibility`

按顺序发出三个条目（第一个匹配的获胜，因此最严格的优先）：

1. `visibility/pii` → `#E15759`（红色，rgb 14767961）
2. `visibility/internal` → `#F28E2B`（橙色，rgb 15896107）
3. `visibility/public` → `#59A14F`（绿色，rgb 5873999）

```json
{"query": "tag:#visibility/pii", "color": {"a": 1, "rgb": 14767961}}
```

没有 `visibility/` 标签的页面保持 Obsidian 的默认颜色 — 不要添加捕获项。

### 模式：`combined`

首先发出 `by-visibility` 条目，然后是 `by-tag` 条目。可见性在冲突时优先，因为它在列表中首先出现。

### 模式：`custom`

如果用户提供了显式映射，则直接使用它们。将他们提供的任何十六进制值（例如 `#FF00FF`）转换为使用 `int(hex_without_hash, 16)` 的打包整数。将每个包装为 `{"a": 1, "rgb": <int>}`。

## 第 3 步：合并到 graph.json（不要覆盖）

1. 读取现有的 `$VAULT_PATH/.obsidian/graph.json`。如果不存在，则从以下最小默认值开始：

   ```json
   {
     "collapse-filter": true,
     "search": "",
     "showTags": false,
     "showAttachments": false,
     "hideUnresolved": false,
     "showOrphans": true,
     "collapse-color-groups": false,
     "colorGroups": [],
     "collapse-display": true,
     "showArrow": false,
     "textFadeMultiplier": 0,
     "nodeSizeMultiplier": 1,
     "lineSizeMultiplier": 1,
     "collapse-forces": true,
     "centerStrength": 0.518713248970312,
     "repelStrength": 10,
     "linkStrength": 1,
     "linkDistance": 250,
     "scale": 1,
     "close": true
   }
   ```

2. **首先备份**：在写入之前将现有文件复制到 `.obsidian/graph.json.backup-<YYYYMMDD-HHMM>`。如果存在同一分钟的备份，则重用它 — 不要堆叠重复项。

3. 仅替换 **`colorGroups` 字段** 为您的新数组。不要更改其他任何字段。这将保留用户的缩放、物理、过滤、搜索和显示偏好。

4. 使用与原始文件相同的 JSON 风格（通常是紧凑的单行或 2 空格缩进 — 保留现有格式）将文件写回。

## 第 4 步：报告和记录

打印类似以下摘要：

```
Graph colorized → .obsidian/graph.json
  Mode:    by-tag
  Groups:  7 color assignments
  Palette: blue, orange, red, teal, green, yellow, purple
  Backup:  .obsidian/graph.json.backup-20260424-1432

Reload Obsidian (Cmd/Ctrl+R) to see the new colors.
If Obsidian is currently open, close it first OR reload immediately — Obsidian
overwrites graph.json on close and can erase these changes.
```

追加到 `$VAULT_PATH/log.md`：

```
- [TIMESTAMP] GRAPH_COLORIZE mode=<mode> groups=<N> backup=graph.json.backup-<stamp>
```

## 边缘情况

- **在 `by-tag` 模式下，仓库中没有标签** → 回退到 `by-category` 并告诉用户。
- **用户想要撤销** → 从最新的 `graph.json.backup-*` 恢复并记录在 `log.md` 中。
- **用户想要清除所有颜色组** → 设置 `colorGroups: []`，备份，记录为 `GRAPH_COLORIZE mode=clear`。
- **`.obsidian/` 缺失** → 该仓库尚未在 Obsidian 中打开过。告诉用户在 Obsidian 中打开一次，然后重新运行。不要自己创建 `.obsidian/` — Obsidian 在首次打开时会填充其中的许多文件。
- **查询语法陷阱**：文件夹路径中的空格需要引号（`path:"my folder"`）；嵌套斜杠的标签按字面意义工作（`tag:#visibility/internal`）；不要 URL-编码。
- **编辑时 Obsidian 打开**：提示风险 — Obsidian 在启动时读取 `graph.json` 并在关闭时**重写它**。如果用户正在实时编辑，告诉他们先关闭 Obsidian 或立即运行重新加载（Cmd/Ctrl+R），并在他们这样做之前避免打开图形设置。

## 注意事项

- 这是一个纯配置编辑 — 不更改页面内容，不写入 frontmatter。
- 重新运行是安全的：每次运行都会创建一个新的备份，仅 `colorGroups` 被重写。
- 如果用户有手动策划的颜色组并希望保留，请提供 `combined` 模式或询问是否覆盖。
- 此调色板与 `wiki-export` 的 `graph.html` 社区颜色匹配，因此 Obsidian 图形和导出的可视化看起来一致。
