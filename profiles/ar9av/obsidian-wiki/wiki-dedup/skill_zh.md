# Wiki Dedup — 身份解析和页面级去重

你正在查找并合并涵盖相同概念但名称不同的维基页面。这是一个写操作密集型、可能具有破坏性的技能——页面合并不能自动撤销。请小心操作并在合并模式下确认后再执行。

**请遵循 `llm-wiki/SKILL.md` 中的检索原语表格。** 候选检测阶段仅使用前导部分和标题（成本较低）。仅对确认的候选对打开完整页面正文。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。

`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 沿 CWD 向上查找 `.env` → 全局配置 → 提示设置）。这提供了 `OBSIDIAN_VAULT_PATH` 和 `OBSIDIAN_LINK_FORMAT`。
2. 阅读 `index.md` 获取包含单行描述和标签的完整页面清单。
3. 简要阅读 `log.md` — 如果刚刚进行了去重运行，请注意哪些内容已经被合并。

## 模式

| 模式 | 标志 | 行为 |
|---|---|---|
| **审计** | *(默认)* | 仅报告候选对 — 不进行写入 |
| **合并** | `--merge` | 显示每个确认对，合并前请求确认 |
| **自动合并** | `--auto` | 非交互式合并所有高置信度对 (`score ≥ 0.90`) |

如果用户未指定，则以 **审计** 模式运行，并在询问是否继续之前呈现结果。

## 第 1 步：构建页面注册表

在保险库中全局搜索所有 `.md` 文件（排除 `_archives/`、`_raw/`、`.obsidian/`、`index.md`、`log.md`、`hot.md`、`_insights.md` 以及其前导部分包含 `redirects_to:` 的任何文件 — 这些已经是合并的重定向占位符）。

对于每个剩余页面，从前导部分中提取：
- `node_id` — 从保险库根目录的相对路径，不包含 `.md`
- `title` — 前导部分的 `title` 字段
- `aliases` — 前导部分的 `aliases` 列表（可能不存在）
- `tags` — 前导部分的 `tags` 列表
- `category` — 目录前缀

构建一个查找表：`node_id → {title, aliases, tags, category, summary}`。

## 第 2 步：检测候选对

对于注册表中的每一对页面，使用以下信号计算 **相似度分数**：

### 2a. 标题相似度信号

| 信号 | 评估方法 | 最大贡献 |
|---|---|---|
| **词元重叠** | 小写标题词元的 Jaccard 相似度（按空格、连字符、下划线、标点符号分割） | 0.65 |
| **编辑距离** | 小写标题的归一化编辑距离：`1 - (edits / max(len_a, len_b))` | 0.40 |
| **子串包含** | 一个标题是另一个标题的子串（例如 "RSC" ⊂ "React Server Components"） | 0.50 |
| **别名交叉匹配** | 页面 A 的标题出现在页面 B 的 `aliases` 中，反之亦然 | 0.65 |

复合标题分数 = `min(max(token_overlap, edit_distance, substring), 0.65) + alias_cross_bonus`。

你不需要精确计算 — 对相似程度做出自信的判断。

**标题提取说明：** 某些页面使用 YAML 块标量 (`title: >-` 或 `title: |`)。当 `title:` 值为 `>-`、`>`、`|` 或 `|-` 时，实际标题位于下一个缩进行上 — 从那里读取。永远不要将字面字符串 `>-` 作为标题进行比较。

### 2b. 语义信号（快速通过）

| 信号 | 分数 |
|---|---|
| 相同 `category` 目录 | +0.10 |
| 标签重叠 ≥ 3 个共享标签 | +0.15 |
| 标签重叠 ≥ 2 个共享标签 | +0.05 |
| 相同第一个标签（主导标签） | +0.05 |

### 2c. 阈值

将复合分数 ≥ **0.75** 的对标记为 **候选对**。分数为 0.90+ 的对为 **高置信度**。

分数范围 → 置信度标签：

| 分数 | 标签 |
|---|---|
| ≥ 0.90 | HIGH — 几乎可以肯定是相同的概念 |
| 0.75–0.89 | MEDIUM — 可能是相同的，请验证 |
| 0.60–0.74 | LOW — 可能是缩写或专门化；除非用户询问，否则跳过 |

仅将 HIGH 和 MEDIUM 候选对带入第 3 步。

### 2d. 快速退出规则

如果保险库中的页面少于 10 个，则跳过配对循环并报告“保险库太小，无法存在有意义的重复”。如果保险库中的页面超过 500 个，则以 50 对候选为一批处理 — 在批次之间暂停并报告进度。

## 第 3 步：语义裁决

对于每个候选对（按分数降序排序）：

1. 读取两个页面的完整内容（完整页面读取 — 因为候选池很小）。
2. 询问：这些页面是否涵盖 **相同的概念**，或者它们是不同的？

分配以下三种裁决之一：

| 裁决 | 含义 |
|---|---|
| `merge` | 相同的概念 — 不同的名称、缩写、别名或意外重复。可以安全合并。 |
| `keep-separate` | 相关但不同 — 例如 "Server Actions" 和 "Server Components" 是相关的 React 功能，不是重复。 |
| `needs-review` | 模棱两可 — 重叠很大但也有重要差异。标记供用户决定。 |

为每个裁决附加简短的原因（一句话）。这会出现在报告中和日志中。

## 第 4 步：审计报告

始终生成此报告，即使在合并/自动合并模式下也是如此（以便用户看到将要发生什么）：

```markdown
## Wiki Dedup Report

### 高置信度候选对（分数 ≥ 0.90）：N 对

| 分数 | 页面 A | 页面 B | 裁决 | 原因 |
|---|---|---|---|---|
| 0.95 | `concepts/rsc.md` | `concepts/react-server-components.md` | merge | "RSC" 是缩写；两个页面涵盖相同的内容 |
| 0.91 | `entities/vaswani-2017.md` | `references/attention-is-all-you-need.md` | keep-separate | 一个是人物占位符，一个是论文引用 |

### 中置信度候选对（分数 0.75–0.89）：N 对

| 分数 | 页面 A | 页面 B | 裁决 | 原因 |
|---|---|---|---|---|
| 0.82 | `concepts/fine-tuning.md` | `concepts/finetuning.md` | merge | 相同的概念，连字符变体 |

### 需要人工审查：N 对

| 分数 | 页面 A | 页面 B | 原因 |
|---|---|---|---|
| 0.78 | `concepts/agents.md` | `concepts/autonomous-agents.md` | Substantial overlap but "agents" may intentionally be broader |

### 总结
- 扫描的页面：N
- 发现的候选对：M
- 推荐合并：X
- 保持独立：Y
- 需要审查：Z
```

在 **审计模式** 下，停止在此处并询问：“运行 `--merge` 交互式合并推荐对，或 `--auto` 自动合并所有高置信度对？”

## 第 5 步：合并

**预写快照** — 在第一次文件写入之前，检查保险库本身是否是 Git 仓库的根。仅仅是较大仓库的子目录并不符合条件：在 đó 运行 `git add -A` 可能会捕获不相关的文件。如果保险库不是独立的 Git 仓库，则静默跳过此步骤 — 不提示，也不建议 `git init`。

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
    if ! git -C "$OBSIDIAN_VAULT_PATH" commit -m "pre-wiki-dedup snapshot" --quiet; then
      echo "Pre-write snapshot failed; abort the skill without writing any vault files." >&2
      exit 1
    fi
    SNAPSHOT_SHA=$(git -C "$OBSIDIAN_VAULT_PATH" rev-parse HEAD)
  fi
fi
```

干净仓库分支故意避免调用 `git commit`，因此“没有可提交的内容”不被视为错误。如果 `git add` 或 `git commit` 失败，则在编辑保险库之前停止；永远不要在没有承诺的快照的情况下继续。

如果 `SNAPSHOT_SHA` 非空且技能写入文件，则在最终报告中包含 SHA。要丢弃整个运行，在确认没有值得保留的后续更改后，用户可以运行：

```bash
git -C "$OBSIDIAN_VAULT_PATH" reset --hard "$SNAPSHOT_SHA"
git -C "$OBSIDIAN_VAULT_PATH" clean -fd
```

对于每个 `merge` 裁决对（在合并或自动合并模式下）：

在 **合并模式** 下：显示配对和裁决，然后询问：“将 `[Page A]` 合并到 `[Page B]`？ (yes/skip/review)” 除 yes 外跳过。

在 **自动合并模式** 下：仅处理高置信度 (`score ≥ 0.90`) 合并，不提示。

### 5a: 选择规范页面

按顺序应用这些破折器，直到一个胜出：

1. **更多传入的维基链接** — 在保险库中 grep `[[node_id]]` 引用；计数高的胜出
2. **更丰富的内容** — 更长的页面正文（更多行）胜出
3. **更多来源** — 更大的 `sources:` 列表胜出
4. **标题长度** — 更长、更描述性的标题胜出（例如 "React Server Components" 比 "RSC" 胜出）
5. **字母顺序** — 标题越早胜出

规范页面是 **幸存者**。另一个页面成为 **次要**（将被合并，然后用重定向占位符替换）。

### 5b: 将内容合并到规范页面

读取两个页面。更新规范页面：

- **`aliases:`** — 添加次要页面的标题和所有别名（无重复）
- **`tags:`** — 合并两个标签列表（去重，最多 5 个领域标签 + 系统标签）
- **`sources:`** — 合并两个来源列表（去重）
- **`relationships:`** — 合并两个关系列表（按目标去重，优先考虑带类型的条目而不是不带类型的）
- **`base_confidence`** — 使用来源的并集和 `llm-wiki/SKILL.md` 中的公式重新计算
- **`updated`** — 设置为现在
- **`summary:`** — 如果次要页面添加了新的范围，重写以涵盖合并后的范围
- **正文内容** — 合并次要页面的唯一章节和项目符号。不要盲目追加 — 整合内容。避免重复规范页面中已有的声明。在需要综合的地方使用 `^[inferred]` 标记。
- **`provenance:`** — 合并后重新计算

### 5c: 在次要页面路径处写入重定向占位符

```markdown
---
title: <次要页面标题>
redirects_to: "[[<规范 node_id>]]"
aliases: [<次要别名>]
category: <次要分类>
tags: []
created: <次要原始创建>
updated: <ISO 时间戳现在>
---

此页面已合并到 [[<规范页面标题>]]。
```

`redirects_to:` 字段告诉任何读取此页面的技能跟随重定向，而不是将其视为内容。

### 5d: 全保险库重写维基链接

在保险库中 grep 任何指向次要 slugs 的链接：

- `[[secondary-slug]]` → `[[canonical-slug]]`
- `[[secondary-slug|显示文本]]` → `[[canonical-slug|显示文本]]`
- 如果 `OBSIDIAN_LINK_FORMAT=markdown`：`[文本](../path/to/secondary.md)` → `[文本](../path/to/canonical.md)`

**安全规则：**
- 永远不要在代码块内重写（``` 括号或 `inline code`）
- 永远不要在重定向占位符本身内重写（那是唯一一个旧 slugs 应该仍然可读的地方）
- 永远不要使用 `rm` 或破坏性 shell 操作 — 仅使用编辑/写入工具
- 一次重写一个文件，并在继续之前验证
- 如果文件没有出现，则跳过

### 5e: 更新跟踪文件

**`index.md`** 和 **`hot.md`** 由第 6 步中的 `memory sync` 调用重新生成 — 页面遍历器会跳过重定向占位符，因此次要页面的条目会消失，规范页面的条目会自行获取合并后的摘要。

**`.manifest.json`** — 对于次要页面的来源条目：将 `"merged_into": "<canonical node_id>"` 添加到每个条目中。对于规范页面：合并次要页面的 `pages_created` 和 `pages_updated` 列表。

### 5f: 最终检查

所有合并后，在非占位符文件中 grep 任何剩余的 `[[secondary-slug]]` 引用。如果有任何幸存，请报告它们 — 重写步骤可能错过了非标准链接格式。

## 第 6 步：日志

一个锁定调用写入日志行并协调索引和热缓存：

```bash
obsidian-wiki memory sync DEDUP \
  mode=<audit|merge|auto-merge> pages_scanned=<N> pairs_found=<M> \
  merged=<X> kept_separate=<Y> needs_review=<Z> \
  wikilinks_rewritten=<W> \
  --takeaways "Merged N duplicate pairs; canonical pages updated."
```

在审计模式（未合并）下使用 `obsidian-wiki memory log DEDUP ...` 而不是 — 这是一个只读运行，不能重写索引或热缓存。

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令获取的锁定防止并行写入者丢弃你的更新。

查看 `.skills/llm-wiki/references/MEMORY.md` 获取完整过程。

## 重定向占位符处理

其他技能应按以下方式处理重定向占位符：

- **`wiki-export`** — 跳过前导部分中有 `redirects_to:` 的页面；它们不是内容节点
- **`wiki-query`** — 如果搜索命中重定向占位符，则跟随 `redirects_to:` 并读取规范页面
- **`wiki-lint`** — 验证每个 `redirects_to:` 维基链接是否解析到现有的非占位符页面（重定向链 — 占位符指向占位符 — 是错误）
- **`cross-linker`** — 将重定向占位符视为非目标；永远不要添加指向占位符页面的新 `[[wikilink]]`

## 小贴士

- **始终先审计。** 即使在自动合并模式下，也会显示审计报告。在信任结果之前阅读它。
- **最后检查 `needs-review`。** 这些是难题 — 不要将它们与明显的合并批量处理。
- **缩写是最常见的案例。** "GPT" / "GPT-4" / "GPT4"，"RSC" / "React Server Components"，"LLM" / "Large Language Models" — 这些在子串包含中得分很高，几乎总是可以安全合并。
- **不同版本不是重复。** "GPT-3" 和 "GPT-4" 是相关的但不同的。"fine-tuning" 和 "fine-tuning-llms" 可能是不同的（技术 vs. 特定应用）。
- **合并后运行 `cross-linker`。** 重定向占位符会使图处于略微不一致的状态。Cross-linker 将会将其收紧。

## QMD 刷新后保险库写入

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，则跳过此步骤。仅在此技能写入或重写保险库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚保险库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，则使用它；否则使用 `qmd`。

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
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录一个：
- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`
