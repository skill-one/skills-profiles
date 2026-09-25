# Cross-Linker — 自动化维基交叉引用

您正在通过查找并插入页面之间缺失的 `[[wikilinks]]` 来编织维基的知识图谱，这些页面应该相互引用但目前没有引用。

**请遵循 `llm-wiki/SKILL.md` 中的检索原语表。** 通过步骤 1 使用仅 grep 前置内容的构建注册表（而不是完整页面）。为未链接提及的检测过程保留完整的 `Read`，即使在这种情况下，也只读取那些其摘要/标题使其成为合理链接目标的页面。盲法完整仓库读取是此框架存在的原因。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 上行查找 `.env` → 全局配置 → 提示设置）。这提供了 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_LINK_FORMAT`（默认：`wikilink`）。
2. 阅读 `index.md` 以获取页面及其单行描述的完整清单
3. 快速浏览 `log.md` 以查看最近已摄入的内容（将链接工作重点放在新页面上）

在步骤 4 中插入链接时，使用 `llm-wiki/SKILL.md`（链接格式部分）中的 `OBSIDIAN_LINK_FORMAT` 值应用链接格式。当 `OBSIDIAN_LINK_FORMAT=markdown` 时，从**正在编辑的文件**到目标页面的相对 `.md` 路径。

## 步骤 1：构建页面注册表

在仓库中 glob 所有 `.md` 文件（排除 `_archives/`、`_readouts/`、`.obsidian/`）。对于每个页面，提取：

- **文件名**（不带 `.md`）— 这是维基链接目标
- 从前置内容提取**标题**
- 从前置内容提取**别名**（如果有）
- 从前置内容提取**标签**
- 从前置内容或目录推断**类别**
- **单行摘要** — 第一句话或 `title` 字段

构建一个查找表：

```
page_name → { path, title, aliases, tags, summary }
```

这是您的“词汇表”——此表中的每个条目都是有效的维基链接目标。

## 步骤 2：扫描缺失链接

对于仓库中的每个页面：

1. **读取完整内容**
2. **提取现有维基链接** — 查找所有已存在的 `[[...]]` 引用
3. **搜索未链接提及** — 检查页面的文本是否包含这些内容，但不包含在 `[[...]]` 中：
   - 页面文件名（例如，单词 "MyProject" 出现，但 `[[projects/my-project/my-project]]` 缺失）
   - 从前置内容提取的页面标题
   - 从前置内容提取的别名
   - 注册表中的实体名称、项目名称、概念名称
4. **检查语义连接** — 共享多个标签的页面或位于同一项目目录但彼此不链接的页面

### 匹配规则

- **不区分大小写匹配**名称（例如，"my-project" 匹配页面 `MyProject`）
- **不区分变音符号匹配** — 使用 Unicode NFKD 规范化页面名称和正文文本（将变音字符分解为基础字符 + 结合标记，删除结合标记）进行比较。这确保正文文本 "Muller" 匹配页面 `[[entities/müller]]` 以及反之。
- **跳过自我引用** — 页面不应链接到自身
- **跳过常用词** — 不要链接 "the"、"and"、"通用术语"。仅匹配独特名称
- **优先使用最短的不含糊维基链接路径** — 当名称在仓库中唯一时，使用 `[[page-name]]` 而不是 `[[full/path/to/page-name]]`
- **不要在代码块内链接** 或前置内容
- **不要重复链接** — 如果页面已出现 `[[foo]]`，则不要添加另一个

## 步骤 3：评分和排名建议

并非每个可能的链接都值得添加。使用复合信号对每个候选进行评分，然后使用置信度标签进行标记。

### 评分

| 信号 | 分数 | 示例 |
|---|---|---|
| **文本中名称完全匹配** | +4 | "MyProject" 出现在正文文本中 → 链接到 my-project.md |
| **共享标签（2+）** | +2 | 两者都标记为 `#ai #agent` 但它们之间没有链接 |
| **同一项目，无链接** | +2 | 两者都在 `projects/my-project/` 下但彼此不引用 |
| **提及实体/概念** | +2 | 页面提及 "知识图谱" → 链接到 `[[concepts/knowledge-graphs]]` |
| **跨类别连接** | +2 | 源页面在 `concepts/`，目标页面在 `entities/`（或 `skills/` ↔ `synthesis/`）— 不同知识层级的连接在架构上更有价值 |
| **外围→中心连接** | +2 | 源页面总链接 ≤ 2（外围），但目标 ≥ 8（中心）— 将松散页面连接到承重概念 |
| **部分名称匹配** | +1 | "graph" 出现，但页面是 `knowledge-graphs` — 可能但模糊 |

### 置信度标签

根据其分数为每个候选添加置信度标签：

| 分数 | 标签 | 操作 |
|---|---|---|
| ≥ 6 | **EXTRACTED** | 链接实际上很确定 — 完全提及或非常强的匹配。应用内联。 |
| 3–5 | **INFERRED** | 链接是合理的推断 — 共享上下文、跨类别、外围→中心。内联或作为 Related 部分。 |
| 1–2 | **AMBIGUOUS** | 弱或部分匹配。除非用户明确要求连接松散页面，否则跳过。 |

仅对 **EXTRACTED** 和 **INFERRED** 候选采取行动。在 Cross-Link Report 中包含置信度标签，以便用户可以在信任它们之前审查 INFERRED 链接。

## 步骤 4：应用链接

**预写快照** — 在第一个文件写入之前，检查仓库本身是否是 Git 仓库的根。仅仅是较大仓库的子目录并不符合资格：在 đó 运行 `git add -A` 可能会捕获不相关的文件。如果仓库不是独立的 Git 仓库，则静默跳过此步骤 — 不提示，不建议 `git init`。

```bash
VAULT_REAL_PATH=$(cd "$OBSIDIAN_VAULT_PATH" && pwd -P)
VAULT_GIT_ROOT=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse --show-toplevel 2>/dev/null || true)
SNAPSHOT_SHA=""

if [ -n "$VAULT_GIT_ROOT" ] && [ "$VAULT_GIT_ROOT" = "$VAULT_REAL_PATH" ]; then
  if git -C "$OBSIDIAN_VAULT_PATH" diff --quiet \
    && git -C "$OBSIDIAN_VAULT_PATH" diff --cached --quiet \
    && [ -z "$(git -C "$OBSIDIAN_VAULT_PATH" ls-files --others --exclude-standard)" ]; then
    SNAPSHOT_SHA=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse HEAD)
  else
    if ! git -C "$OBSIDIAN_VAULT_PATH" add -A; then
      echo "Pre-write snapshot failed; abort the skill without writing any vault files." >&2
      exit 1
    fi
    if ! git -C "$OBSIDIAN_VAULT_PATH" commit -m "pre-cross-linker snapshot" --quiet; then
      echo "Pre-write snapshot failed; abort the skill without writing any vault files." >&2
      exit 1
    fi
    SNAPSHOT_SHA=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse HEAD)
  fi
fi
```

干净仓库分支故意避免调用 `git commit`，因此“没有可提交的”不被视为错误。如果 `git add` 或 `git commit` 失败，则在编辑仓库之前停止；永远不要在没有承诺的快照的情况下继续。

如果 `SNAPSHOT_SHA` 非空并且技能写入文件，则在最终报告中包含 SHA。要丢弃整个运行，在确认没有值得保留的后续更改后，用户可以运行：

```bash
git -C "$OBSIDIAN_VAULT_PATH" reset --hard "$SNAPSHOT_SHA"
git -C "$OBSIDIAN_VAULT_PATH" clean -fd
```

对于每个有缺失链接的页面：

### 4a：内联链接（首选）

在正文文本中找到术语的第一个自然提及并将其包裹在维基链接中：

**之前：**
```markdown
This project uses knowledge graphs to connect entities.
```

**之后：**
```markdown
This project uses [[concepts/knowledge-graphs|knowledge graphs]] to connect entities.
```

当维基链接路径与显示文本不同时，使用 `[[path|display text]]` 格式。

### 4b：相关部分（后备）

如果术语在正文文本中不是自然提及，但页面在语义上是相关的（共享标签、同一项目），在页面底部添加 `## Related` 部分：

```markdown
## Related

- [[projects/my-project/my-project]] — Also uses AI agents for research automation
- [[concepts/knowledge-graphs]] — Core technique used in this project
```

如果 `## Related` 部分已存在，则追加到其中。不要重复现有条目。

### 4c：推断并写入关系类型

对于添加的每个 EXTRACTED 或 INFERRED 链接（内联或相关部分），从包含提及的句子上下文中推断语义关系类型，并将其写入页面的 `relationships:` 前置内容块。跳过 AMBIGUOUS 链接。

**类型推断规则** — 扫描包含提及的句子（或对于相关部分链接，页面标题和共享标签上下文）：

| 句子模式 | 推断类型 |
|---|---|
| "X extends / builds on / generalises Y" | `extends` |
| "X implements / is an implementation of Y" | `implements` |
| "X contradicts / opposes / refutes / is at odds with Y" | `contradicts` |
| "X is derived from / based on / adapted from Y" | `derived_from` |
| "X uses / relies on / depends on / requires Y" | `uses` |
| "X replaces / supersedes / deprecates Y" | `replaces` |
| 共享标签或跨类别推断，无方向提示 | `related_to` |

如果周围上下文模糊或链接来自共享标签匹配（正文内无提及），默认为 `related_to`。

**写入块：**

读取页面的 YAML 前置内容。如果 `relationships:` 块已存在，则在不重复现有目标的情况下追加新条目。如果块不存在，则在 `aliases:`（或 `aliases:` 缺失时在 `tags:` 之后）之后添加它。

```yaml
relationships:
  - target: "[[concepts/knowledge-graphs]]"
    type: uses
```

`relationships:` YAML 块中的 `target` 值始终使用维基链接格式（`[[path/to/page]]`）— 无论 `OBSIDIAN_LINK_FORMAT`。`OBSIDIAN_LINK_FORMAT` 设置控制正文内容；前置内容属性始终使用维基链接语法，以便 `wiki-export` 可以可靠地解析它们。

仅添加在此交叉链接器运行中添加的条目 — 不要触摸已存在的类型条目。

## 步骤 5：评分杂项页面亲和度

在主要链接过程之后，更新 `misc/` 中所有页面的亲和度分数（这些页面的 `promotion_status: misc` 在其前置内容中，或位于 `misc/` 目录下）。

对于每个杂项页面：

1. **收集出站链接** — 页面正文中的所有 `[[wikilinks]]`
2. **收集入站链接** — 在仓库中 grep `[[misc/<slug>]]` 和 `[[<slug>]]` 引用
3. 对于每个链接页面（双向），检查它是否属于项目：
   - 位于 `projects/<project-name>/`
   - `project:` 前置内容字段匹配项目名称
4. 按项目名称分组并求和：`outgoing_links + incoming_links`
5. 更新杂项页面的 `affinity` 前置内容块：

```yaml
affinity:
  obsidian-wiki: 3
  another-project: 1
```

6. 如果任何项目的分数 ≥ 3：将此页面标记为 **晋升候选** 并记录它以供报告

**效率说明：** 仅读取杂项页面的完整正文 — 其他页面只需 grep 前置内容即可确定其项目成员资格。

## 步骤 6：报告

提供摘要：

```markdown
## Cross-Link Report

### 添加的链接：23 个跨 12 个页面

| 页面 | 添加的链接 | 置信度 | 位置 | 关系类型 |
|---|---|---|---|---|
| `projects/my-project/my-project.md` | 3 | EXTRACTED | 2 内联，1 相关 | uses ×2, related_to ×1 |
| `entities/jane-doe.md` | 5 | INFERRED | 3 内联，2 相关 | extends ×1, uses ×3, related_to ×1 |
| ... | | | | |

### 剩余的孤儿页面：2
- `references/foo.md` — 未找到入站或出站链接
- `concepts/bar.md` — 无法找到相关页面

### 杂项晋升候选：N
位于 `misc/` 且与单个项目有 ≥ 3 个连接的页面 — 准备晋升：

| 页面 | 顶级项目 | 分数 |
|---|---|---|
| `misc/web-martinfowler-articles-microservices.md` | `obsidian-wiki` | 4 |

要晋升：将页面移动到 `projects/<project-name>/references/` 并更新所有反向链接。

### 跳过的页面：3
- `index.md`, `log.md` — 特殊文件
- `_archives/*` — 归档内容
- `_readouts/*` — 派生阅读输出（wiki-narrate 输出）

## 步骤 7：更新日志和热缓存

一个锁定调用更新日志和热缓存（索引不受影响 — 没有创建页面）：

```bash
obsidian-wiki memory sync CROSS_LINK \
  pages_scanned=<N> links_added=<M> typed_relations_written=<T> \
  pages_modified=<P> orphans_remaining=<Q> \
  misc_affinity_updated=<R> promotion_candidates=<S> \
  --takeaways "Cross-linked 23 mentions across 12 pages; 2 orphans remain."
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令获取锁定，以防止并行写入者丢弃您的更新。

参见 `.skills/llm-wiki/references/MEMORY.md` 了解完整过程。

## 小贴士

- **每次摄入后运行。** 新页面几乎总是连接不良。这是修复方法。
- **保守地使用内联链接。** 仅链接第一个自然提及，而不是每个出现。
- **不要触摸 `_archives/` 或 `_readouts/` 中的页面。** 归档是冻结的快照；阅读输出是来自 `wiki-narrate` 的派生输出，不是知识页面。
- **尊重现有结构。** 如果页面在 `## Key Concepts` 部分仔细管理其链接，则添加到该部分，而不是创建单独的 `## Related`。
- **实体页面是链接磁铁。** 像 `jane-doe` 这样的实体应该从几乎每个项目页面链接。优先考虑这些。

## QMD 摘要更新后仓库写入

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在此技能写入或重写仓库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚仓库更改；单独报告 QMD 状态。

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

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录一个：

- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <short error summary>`
