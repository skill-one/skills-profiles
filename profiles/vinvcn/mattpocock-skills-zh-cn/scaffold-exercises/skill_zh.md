# 创建练习结构

创建能通过 `pnpm ai-hero-cli internal lint` 命令的练习目录结构，然后用 `git commit` 提交。

## 目录命名

- **章节**：`exercises/` 下的 `XX-章节名/`（例如 `01-检索技能构建`）
- **练习**：章节下的 `XX.YY-练习名/`（例如 `01.03-bm25检索`）
- 章节编号 = `XX`，练习编号 = `XX.YY`
- 名称使用 dash-case（小写、连字符）

## 练习变体

每个练习至少需要包含以下子文件夹中的一个：

- `problem/` — 学生工作区，包含 TODOs
- `solution/` — 参考实现
- `explainer/` — 概念材料，不含 TODOs

创建 stub 时，除非计划指定其他变体，否则默认使用 `explainer/`。

## 必要文件

每个子文件夹（`problem/`、`solution/`、`explainer/`）都需要一个 `readme.md`，要求：

- **非空**（必须有真实内容，即使只有一行标题也可以）
- 没有 broken links

创建 stub 时，生成带标题和描述的最小 readme：

```md
# 练习标题

描述内容
```

如果子文件夹包含代码，还需要 `main.ts`（>1 行）。但对 stubs 来说，只有 readme 的练习可以接受。

## 工作流程

1. **解析计划** — 提取章节名、练习名和变体类型
2. **创建目录** — 对每个路径执行 `mkdir -p`
3. **创建 stub readme** — 每个变体文件夹一个带标题的 `readme.md`
4. **运行 lint** — 执行 `pnpm ai-hero-cli internal lint` 验证
5. **修复任何错误** — 迭代直到 lint 通过

## lint 规则摘要

linter（`pnpm ai-hero-cli internal lint`）检查：

- 每个练习有子文件夹（`problem/`、`solution/`、`explainer/`）
- 至少存在 `problem/`、`explainer/` 或 `explainer.1/` 之一
- 主子文件夹中存在非空 `readme.md`
- 没有 `.gitkeep` 文件
- 没有 `speaker-notes.md` 文件
- readme 中没有 broken links
- readme 中没有 `pnpm run exercise` 命令
- 除非是 readme-only，否则每个子文件夹都需要 `main.ts`

## 移动/重命名练习

重新编号或移动练习时：

1. 使用 `git mv`（不是 `mv`）重命名目录，保留 git history
2. 更新数字前缀以维持顺序
3. 移动后重新运行 lint

示例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 示例：从计划创建 stub

给定这样的计划：

```
章节 05：记忆技能构建
- 05.01 记忆简介
- 05.02 短期记忆 (explainer + problem + solution)
- 05.03 长期记忆
```

创建：

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

然后创建 readme stubs：

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# 记忆简介"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# 长期记忆"
```
