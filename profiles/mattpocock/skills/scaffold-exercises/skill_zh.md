# 脚手架练习

创建能通过 `pnpm ai-hero-cli internal lint` 的练习目录结构，然后使用 `git commit` 进行提交。

## 目录命名

- **章节**：在 `exercises/` 目录内使用 `XX-section-name/` 格式（例如 `01-retrieval-skill-building`）
- **练习**：在章节内使用 `XX.YY-exercise-name/` 格式（例如 `01.03-retrieval-with-bm25`）
- 章节编号 = `XX`，练习编号 = `XX.YY`
- 名称采用连字符风格（小写，使用连字符）

## 练习变体

每个练习至少需要以下子文件夹中的一个：

- `problem/` - 学生工作区，包含 TODO 任务
- `solution/` - 参考实现
- `explainer/` - 概念材料，无 TODO 任务

在进行占位（stub）时，默认使用 `explainer/`，除非计划另有规定。

## 必需文件

每个子文件夹（`problem/`、`solution/`、`explainer/`）都需要一个满足以下要求的 `readme.md`：

- **非空**（必须有实际内容，即使只有一个标题行也可）
- 不包含失效链接

在进行占位（stub）时，创建一个包含标题和描述的最小化 readme：

```md
# Exercise Title

Description here
```

如果子文件夹包含代码，则还需要一个 `main.ts`（多于 1 行）。但对于占位练习，仅使用 readme 也是可以的。

## 工作流程

1. **解析计划** - 提取章节名称、练习名称和变体类型
2. **创建目录** - 为每个路径使用 `mkdir -p`
3. **创建占位 readme** - 为每个变体文件夹创建包含标题的一个 `readme.md`
4. **运行 lint** - 使用 `pnpm ai-hero-cli internal lint` 进行验证
5. **修复任何错误** - 迭代直至 lint 通过

## Lint 规则摘要

检查器（`pnpm ai-hero-cli internal lint`）检查以下内容：

- 每个练习都有子文件夹（`problem/`、`solution/`、`explainer/`）
- `problem/`、`explainer/` 或 `explainer.1/` 中至少存在一个
- 主子文件夹中存在 `readme.md` 且非空
- 没有 `.gitkeep` 文件
- 没有 `speaker-notes.md` 文件
- readme 中没有失效链接
- readme 中没有 `pnpm run exercise` 命令
- 除非是仅使用 readme，否则每个子文件夹都需要 `main.ts`

## 移动/重命名练习

在重新编号或移动练习时：

1. 使用 `git mv`（而非 `mv`）来重命名目录 - 保留 git 历史记录
2. 更新数字前缀以维持顺序
3. 在移动后重新运行 lint

示例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 示例：根据计划进行占位

给定如下计划：

```
章节 05：记忆技能构建
- 05.01 记忆入门
- 05.02 短期记忆（explainer + problem + solution）
- 05.03 长期记忆
```

创建：

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

然后创建占位 readme：

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# 记忆入门"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# 长期记忆"
```
