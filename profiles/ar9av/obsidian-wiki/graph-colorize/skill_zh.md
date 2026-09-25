# 图形着色 — 为 Obsidian 图形视图添加颜色编码

您正在重写 `$OBSIDIAN_VAULT_PATH/.obsidian/graph.json`，以便 Obsidian 的图形视图能够根据标签、文件夹或可见性对节点进行着色。

Obsidian 将图形设置存储在 `<vault>/.obsidian/graph.json` 中。`colorGroups` 数组是一个 `{query, color}` 对列表；每个节点按照第一个匹配的查询进行着色。查询使用 Obsidian 的搜索语法：`tag:#foo`、`path:"concepts"`、`file:foo` 等。颜色格式为 `{"a": 1, "rgb": <packed-int>}`，其中整数是 `(R << 16) | (G << 8) | B`。

## 开始前

1. **解析配置** — 按照 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这将提供 `OBSIDIAN_VAULT_PATH`。
2. 确认 `$OBSIDIAN_VAULT_PATH/.obsidian/` 存在。如果不存在，说明该 vault 从未在 Obsidian 中打开过 — 提示用户在 Obsidian 中打开 vault，然后重新运行。
3. **如果 Obsidian 可能正在运行，则警告用户**：Obsidian 在关闭时会覆盖 `graph.json`。告诉他们先关闭 vault，或者在重新加载（Cmd/Ctrl+R）时准备好重新加载（Cmd/Ctrl+R），并在重新加载前不要触碰图形设置。

## 第 1 步：选择模式

根据用户的措辞推断模式。如果存在歧义，则默认为 **按标签** 模式。

| 用户意图 | 模式 |
|---|---|
| "按标签着色"、"给我的图形上色"、"让它多彩"（默认） | `by-tag` |
| "按文件夹着色"、"按类别着色"、"按目录着色" | `by-category` |
| "高亮可见性"、"在图形中显示内部/PII"、"可见性颜色" | `by-visibility` |
| 用户提供明确的映射（`tag:#foo = red`，或 JSON 片段） | `custom` |
| "组合标签和可见性" / "两者" | `combined`（先按可见性，再按标签） |

## 第 2 步：构建 `colorGroups` 数组

### 调色板（10 种不同的、无障碍的颜色）

按顺序使用。如果组数多于颜色数，则循环并通过第二次遍历将亮度约降低 20% 来调整明度 — 或者直接限制为 10 个，并告知用户其余标签共享 "其他" 颜色。

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

每种颜色都包装为 `{"a": 1, "rgb": <int>}`。

### 模式：`by-tag`

1. 使用 glob 匹配 `$VAULT_PATH/**/*.md`，排除 `_archives/`、`_raw/`、`.obsidian/`、`node_modules/`、`index.md`、`log.md`、`_insights.md`。
2. 解析每个页面的 frontmatter 中的 `tags`。统计每个标签的使用频率。
3. **从频率列表中删除 `visibility/*` 标签** — 它们是保留的系统标签，仅在 `by-visibility` 或 `combined` 模式下处理。
4. 按使用频率取前 10 个标签。如果唯一标签少于 10 个，则使用所有标签。
5. 对于索引为 `i` 的每个标签 `T`：输出 `{"query": "tag:#T", "color": palette[i]}`。
6. 可选地，在末尾添加一个用于未标记页面的通配符条目：`{"query": "-[\"tag\":]", "color": palette[9]}` — **如果颜色槽 9 已被真实标签占用，则跳过**。

### 模式：`by-category`

使用七个 vault 顶级文件夹，按此固定顺序，以便颜色在多次运行中保持一致：

| 文件夹 | 颜色索引 |
|---|---|
| `concepts` | 0（蓝色） |
| `entities` | 1（橙色） |
| `skills` | 2（红色） |
| `references` | 3（青色） |
| `synthesis` | 4（绿色） |
| `projects` | 5（黄色） |
| `journal` | 6（紫色） |

为每个存在且至少包含一个 `.md` 文件的文件夹输出一个条目。每个条目为：

```json
{"query": "path:\"<folder>\"", "color": {"a": 1, "rgb": <int>}}
```

### 模式：`by-visibility`

输出三个条目，按此顺序（先匹配者胜出，因此最严格的优先）：

1. `visibility/pii` → `#E15759`（红色，rgb 14767961）
2. `visibility/internal` → `#F28E2B`（橙色，rgb 15896107）
3. `visibility/public` → `#59A14F`（绿色，rgb 5873999）

```json
{"query": "tag:#visibility/pii", "color": {"a": 1, "rgb": 14767961}}
```

没有 `visibility/` 标签的页面保持 Obsidian 的默认颜色 — 不要添加通配符。

### 模式：`combined`

先输出 `by-visibility` 条目，然后输出 `by-tag` 条目。可见性在冲突时优先，因为它在列表中先出现。

### 模式：`custom`

如果用户提供了明确的映射，则直接使用。将他们提供的任何十六进制值（例如 `#FF00FF`）转换为打包整数使用 `int(hex_without_hash, 16)`。每个条目包装为 `{"a": 1, "rgb": <int>}`。

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

2. **首先备份**：在写入前将现有文件复制到 `.obsidian/graph.json.backup-<YYYYMMDD-HHMM>`。如果存在同一分钟的备份，则复用它 — 不要堆叠重复的备份。

3. 仅替换 **`colorGroups` 字段** 为您的新数组。不要更改其他任何字段。这将保留用户的缩放、物理、过滤、搜索和显示偏好。

4. 使用与原始文件相同的 JSON 风格（通常是紧凑的单行或 2 空格缩进 — 保留现有格式）将文件写回。

## 第 4 步：报告和记录

打印类似以下摘要：

```
图形着色 → .obsidian/graph.json
  模式:    by-tag
  组数:    7 个颜色分配
  调色板:  蓝色、橙色、红色、青色、绿色、黄色、紫色
  备份:    .obsidian/graph.json.backup-20260424-1432

重新加载 Obsidian (Cmd/Ctrl+R) 以查看新颜色。
如果 Obsidian 当前正在运行，请先关闭它，或者立即重新加载 — Obsidian
在关闭时会覆盖 graph.json，并可能擦除这些更改。
```

追加到 `$VAULT_PATH/log.md`：

```
- [TIMESTAMP] GRAPH_COLORIZE mode=<mode> groups=<N> backup=graph.json.backup-<stamp>
```

## 边缘情况

- **在 `by-tag` 模式下 vault 中没有标签** → 回退到 `by-category` 并告知用户。
- **用户想要撤销** → 从最新的 `graph.json.backup-*` 恢复，并在 `log.md` 中记录。
- **用户想要清除所有颜色组** → 设置 `colorGroups: []`，备份，记录为 `GRAPH_COLORIZE mode=clear`。
- **`.obsidian/` 缺失** → vault 还未在 Obsidian 中打开过。告诉用户在 Obsidian 中打开一次，然后重新运行。不要自己创建 `.obsidian/` — Obsidian 在首次打开时会填充其中的许多文件。
- **查询语法陷阱**：文件夹路径中包含空格需要加引号（`path:"my folder"`）；嵌套斜杠的标签按字面值处理（`tag:#visibility/internal`）；不要 URL-编码。
- **编辑时 Obsidian 正在运行**：提示风险 — Obsidian 在启动时读取 `graph.json` 并在关闭时**重写它**。如果用户正在实时编辑，告诉他们先关闭 Obsidian 或立即运行重新加载（Cmd/Ctrl+R），并在重新加载前避免打开图形设置。

## 注意事项

- 这是一个纯配置编辑 — 不更改页面内容，不写入 frontmatter。
- 重新运行是安全的：每次运行都会创建一个新的备份，仅重写 `colorGroups`。
- 如果用户有手动策划的颜色组并希望保留，提供 `combined` 模式或询问是否覆盖。
- 此调色板与 `wiki-export` 的 `graph.html` 社区颜色匹配，因此 Obsidian 图形和导出的可视化看起来一致。
