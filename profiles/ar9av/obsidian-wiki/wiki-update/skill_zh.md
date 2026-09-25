# Wiki 更新 — 将任何项目同步到您的 Wiki

您正在将当前项目的知识提炼到用户的 Obsidian Wiki 中。此技能在任何项目目录中均可工作，而不仅限于 obsidian-wiki 仓库。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH`、`OBSIDIAN_WIKI_REPO`、`OBSIDIAN_LINK_FORMAT`（默认为 `wikilink` 或 `markdown`）以及可选的 QMD 设置（如 `QMD_WIKI_COLLECTION`）。可在任何项目目录中工作。
3. 读取 `$OBSIDIAN_VAULT_PATH/.manifest.json` 以检查该项目是否之前已同步过。
4. 读取 `$OBSIDIAN_VAULT_PATH/index.md` 以了解 Wiki 中已包含的内容。

在步骤 4–5 中编写内部链接时，请使用 `llm-wiki/SKILL.md`（链接格式部分）中的 `OBSIDIAN_LINK_FORMAT` 值应用链接格式。

## 第 1 步：理解项目

通过扫描当前工作目录来确定此项目的性质：

- `README.md`、docs/、任何 Markdown 文件
- 源结构（框架、语言、关键抽象）
- `package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml` 或其他定义项目的文件
- Git 日志（关注表示决策的提交消息，而非“修复拼写错误”之类的消息）
- 如果存在，则读取 Claude 内存文件（项目中的 `.claude/` 目录）

从目录名称中推导出干净的项目名称。

## 第 2 步：计算差异

检查此项目的 `.manifest.json`：

- **首次同步？** 全扫描。所有内容都是新的。
- **之前已同步？** 查看 `last_commit_synced`。在计算差异之前，验证存储的 SHA 是否仍然可访问：
  ```bash
  git merge-base --is-ancestor <last_commit_synced> HEAD
  ```
  - **退出 0（祖先）：** 安全。运行 `git log <last_commit_synced>..HEAD --oneline` 查看发生了什么变化。
  - **退出 1（不是祖先 — 发生了变基或强制推送）：** 存储的 SHA 已不再在此分支的历史中。警告用户：*"存储的提交 `<sha>` 已不再可访问 — 分支可能已变基或强制推送。回退到全扫描。"* 然后将其视为首次同步：重新扫描所有内容，并在步骤 6 结束时更新 `last_commit_synced` 为当前 HEAD SHA。

如果自上次同步以来未发生有意义的变化，请告知用户并停止。

## 第 3 步：决定要提炼的内容

这是 Karpathy 模式中的核心问题：**如果你在 3 个月后带着零背景信息回来，你会想了解这个项目的哪些内容？**

值得提炼的：

- 架构决策及其原因
- 在构建过程中发现的模式（否则你会再次在 Google 上搜索）
- 项目依赖的工具、服务和 API 以及它们如何连接在一起
- 关键抽象、它们如何连接、心智模型是什么
- 评估的权衡、选择的内容及其原因
- 在构建过程中学到的、从代码中无法明显看出的事物

不值得提炼的：

- 文件列表、样板代码、显而易见的配置
- 没有更广泛教训的单独 Bug 修复
- 依赖版本、锁文件内容
- 代码已明确说明的实现细节
- 任何人都可以从差异中阅读的常规更改

启发式方法：**如果阅读代码库就能回答问题，就不要将其写入 Wiki。如果你不得不通过阅读 20 个提交的 git blame 来重新推导推理，就将其写入 Wiki。**

### 第 3b 步：构建代码理解焦点图（可选）

**GUARD：如果 `obsidian-wiki code-understand` 命令失败或不可用，跳过此步骤并继续 — 它是一个优化，不是要求。**

当此项目包含代码时，在提炼之前运行本地代码理解提取器。它将本地解析代码库并返回焦点图 — 架构依赖的排名文件和符号 — 这样你就可以阅读承重部分，而不是扫描所有内容。

```bash
obsidian-wiki code-understand --project "$(pwd)" --pretty
```

当这不是首次同步（步骤 2 计算 `last_commit_synced`）时，从差异中为焦点图提供种子：

```bash
obsidian-wiki code-understand --project "$(pwd)" --since <last_commit_synced> --pretty
```

（首次同步：省略 `--since`。）

#### 如何处理焦点图输出

1. **有选择地阅读输出** — 当 `backend: codegraph` 时，将焦点图条目视为具有 `file:line` 引证的结构性事实；当 `backend: builtin` 时，将 `defines`/`imports` 条目视为事实，但将 `rg-reference` 条目视为较弱的证据 — 打开文件并验证后再引用。仅打开焦点图指向的排名 `files`/`file:lines`；永远不要将 JSON 粘贴到 Wiki 或 Vault 中。
2. **引用证据** — 写入页面的每个架构声明都引用其证据，作为来自焦点图的 `(file:lines)` 或从打开的源中；继续使用现有的来源标记。
3. **修剪过时的关系（必须）** — 在更新现有的 `projects/<name>/` 页面时，将每个先前记录的代码关系与当前焦点图（或 `obsidian-wiki ast-extract` 进行符号级重新检查）进行交叉检查。删除目标符号不再存在或不再可访问的关系；更新页面并在 `log.md` 中记录删除项。这可以防止误报累积。
4. **永远** 不要将 `.codegraph/` 或 `code-understand` JSON 写入 `$OBSIDIAN_VAULT_PATH` — 图是项目仓库中的缓存/副产物，不是 Wiki 知识。
5. **在缺失时提供 CodeGraph（可选）** — 如果输出报告 `backend: builtin` 因为 codegraph 不可用且用户希望使用增强的后端，请提出为他们安装它：`npm install -g @colbymchenry/codegraph`（或设置 `CODE_UNDERSTANDING_CODEGRAPH_BIN` 为现有二进制文件），然后重新运行此步骤，以便焦点图使用图。永远不要未经用户同意就安装，也永远不要让缺失的 codegraph 阻止同步。

如果 `obsidian-wiki` 未安装或命令失败，跳过此步骤并按正常流程继续 — 它是一个优化，不是要求。

## 第 4 步：提炼到 Wiki 页面

### 项目特定知识

放在 `$VAULT/projects/<project-name>/` 下：

```
projects/<project-name>/
├── <project-name>.md          ← 项目概述（以项目命名，不是 _project.md）
├── concepts/                  ← 项目特定想法、架构
├── skills/                    ← 项目特定操作指南、模式
└── references/                ← 项目特定源摘要
```

概述页面（`<project-name>.md`）应包含：

- 项目的性质（一段话）
- 关键概念及其连接方式
- 链接到项目特定和全局 Wiki 页面

### 全局知识

不是项目特定的内容放在全局类别中：

| 你发现的内容 | 放置位置 |
|---|---|
| 一个通用概念 | `concepts/` |
| 一个可重用模式或技术 | `skills/` |
| 一个工具/服务/人员 | `entities/` |
| 跨项目分析 | `synthesis/` |

### 页面格式

每个页面都需要 YAML 前置：

```markdown
---
title: >-
    页面标题
category: concepts
tags: [tag1, tag2]
sources: [projects/<project-name>]
summary: >-
    一两句（≤200 字符）描述此页面涵盖的内容。
provenance:
  extracted: 0.6
  inferred: 0.35
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: TIMESTAMP_DATE
created: TIMESTAMP
updated: TIMESTAMP
---

使用折叠标量语法（summary: >-）来保持标题和摘要的内容在标点符号（:、#、引号）下安全，而无需转义规则。
在 summary: >- 下缩进两格标题和摘要内容。

# 页面标题

- 代码库或文档实际声明的 факты。
- 设计以此方式工作的原因。 ^[inferred]

使用 [[wikilinks]] 连接到其他页面。
```

**在所有新/更新的页面上编写 `summary:` 前置字段**（1–2 句话，≤200 字符），使用 `>-` 折叠样式。对于项目同步，一个好的摘要回答“此页面告诉我关于项目的哪些内容，而这些内容我无法从其标题中猜测？”此字段支持 `wiki-query` 的快速检索。

**应用来源标记**，根据 `llm-wiki`（来源标记部分）。对于项目同步特别：

- **提取** — 代码、配置或文档/提交消息中可见的任何内容：文件结构、依赖项、函数签名、文件的作用。
- **推断** — 决策的原因、设计理由、权衡，“团队选择 X 因为 Y”——除非提交消息、文档或 ADR 明确声明。
- **模糊** — 当代码和文档不一致，或存在明显正在进行中的迁移，同时存在两种模式共存时。

计算大致比例并编写每个新/更新页面的 `provenance:` 块。

### 更新与创建

- 如果 Vault 中已存在页面，**合并** 新信息到其中。不要创建重复项。
- 如果您正在向现有页面添加内容，请更新 `updated` 时间戳并添加新来源。
- 在创建任何新内容之前，检查 `index.md` 了解其中已有内容。

## 第 5 步：交叉链接

创建/更新页面后：

- 从新页面添加 `[[wikilinks]]` 到现有相关页面
- 从现有页面添加 `[[wikilinks]]` 回新页面（如果相关）
- 将项目概述链接到所有项目特定页面和相关的全局页面

## 第 6 步：更新跟踪

### 更新 `.manifest.json`

添加或更新此项目的条目。项目身份必须在机器之间可移植：在 `source_repo`（从 `git remote get-url origin` 正规化为 `host/owner/name`）中记录仓库 URL，并且仅可选地记录 `source_cwd_hint` 为此机器碰巧检出此项目的位置。永远不要写入机器绝对路径 — 见 `llm-wiki/SKILL.md` → `.manifest.json`（来源键合同 v2）。

```json
{
  "projects": {
    "<project-name>": {
      "source_repo": "github.com/owner/<project-name>",
      "source_cwd_hint": "~/code/<project-name>",
      "last_synced": "TIMESTAMP",
      "last_commit_synced": "abc123f",
      "pages_in_vault": ["projects/<project-name>/<project-name>.md", "..."]
    }
  }
}
```

如果项目不是 Git 仓库，请使用 `repo:<stable-name>` 伪键作为 `source_repo`，并保留 `source_cwd_hint` 作为唯一位置字段。

### 更新 `index.md`

添加任何新创建页面的条目。

### 更新 `index.md`、`log.md` 和 `hot.md`

一次锁定调用，不是三次手动编辑：

```bash
obsidian-wiki memory sync WIKI_UPDATE project=<project-name>
  pages_created=X pages_updated=Y \
  source_repo=github.com/owner/<project-name> \
  --takeaways "同步了 obsidian-wiki — wiki-capture 和 wiki-research 添加了；新功能是自主网络研究和对话捕获。"
```

`--takeaways` 应包含在此同步期间出现的最重要的架构见解或决策，以概念性方式而不是文件列表的形式编写。省略它以保留先前的 takeaways。

如果此项目是持续关注的重点，请记录线程，以便下次会话接续：

```bash
obsidian-wiki memory todo add "<the open thread>" --origin projects/<project-name>.md
```

有关完整过程的详细信息，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 第 7 步：刷新 QMD Wiki 索引（可选 — 需要 `QMD_WIKI_COLLECTION`）

**GUARD：如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。** Markdown Vault 是真相来源；QMD 只是一个搜索索引。

仅在写入页面、`.manifest.json`、`index.md`、`log.md` 和 `hot.md` 后运行此步骤。如果步骤 2 未发现有意义的变化且同步提前停止，则不要刷新 QMD。

此刷新目前需要本地 QMD CLI。如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。如果 CLI 不可用或返回错误，请不要回滚 Wiki 更新；报告 Wiki 已更新但 QMD 刷新被跳过或失败。

对于 CLI 刷新：

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要新哈希的向量，或者页面被创建/更新且嵌入可能已过时，请运行：

```bash
${QMD_CLI:-qmd} embed
```

验证至少有一个创建或实质性更新的页面在 Wiki 集合中可见：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/projects/<project-name>/<page>.md" -l 5
```

如果确切的 `qmd://` 路径不确定，请使用：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION" | rg "<project-name>"
```

在最终报告中记录 QMD 刷新为以下之一：

- `QMD refreshed: update + embed + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`

## 小贴士

- **积极合并。** 如果项目使用 React Server Components，如果 `concepts/react-server-components.md` 已存在，则不要创建新页面。更新现有页面并将此项目作为来源添加。
- **参考标签分类法。** 如果存在 `$VAULT/_meta/taxonomy.md`，请阅读它，并使用规范标签。
- **不要复制代码。** 提炼的是 *知识*，而不是实现。“此项目使用带 300ms 延迟的防抖搜索模式”是有用的。粘贴实际的防抖函数没有用。
- **项目概述是锚点。** `<project-name>.md` 文件是您获取方向时会阅读的。使其变得出色。
