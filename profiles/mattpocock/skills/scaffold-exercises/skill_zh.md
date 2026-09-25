# 创建练习目录结构

创建通过 `pnpm ai-hero-cli internal lint` 检查的练习目录结构，然后使用 `git commit` 提交。

## 目录命名

- **章节**: 在 `exercises/` 下使用 `XX-章节名称/` (例如，`01-检索技能构建`)
- **练习**: 在章节下使用 `XX.YY-练习名称/` (例如，`01.03-使用 BM25 的检索`)
- 章节编号 = `XX`，练习编号 = `XX.YY`
- 名称使用短横线命名法 (小写，短横线)

## 练习变体

每个练习至少需要一个以下子文件夹：

- `problem/` - 学生工作区，包含 TODO 列表
- `solution/` - 参考实现
- `explainer/` - 概念材料，不包含 TODO 列表

在创建占位符时，默认使用 `explainer/`，除非计划另有说明。

## 必要文件

每个子文件夹 (`problem/`、`solution/`、`explainer/`) 需要一个 `readme.md`，该文件必须：

- **非空** (必须包含实际内容，即使只有一条标题行也可以)
- 没有损坏的链接

在创建占位符时，创建一个包含标题和描述的最小 readme：

```md
# 练习标题

描述内容
```

如果子文件夹包含代码，还需要一个 `main.ts` (>1 行)。但对于占位符，只有 readme 的练习也可以。

## 工作流程

1. **解析计划** - 提取章节名称、练习名称和变体类型
2. **创建目录** - 使用 `mkdir -p` 为每个路径创建目录
3. **创建占位符 readme** - 每个变体文件夹一个 `readme.md`，包含标题
4. **运行 lint** - 使用 `pnpm ai-hero-cli internal lint` 进行验证
5. **修复任何错误** - 迭代直到 lint 通过

## lint 规则摘要

lint 工具 (`pnpm ai-hero-cli internal lint`) 检查：

- 每个练习都有子文件夹 (`problem/`、`solution/`、`explainer/`)
- 至少存在 `problem/`、`explainer/` 或 `explainer.1/` 中的一个
- 主要子文件夹中存在 `readme.md` 且非空
- 没有 `.gitkeep` 文件
- 没有 `speaker-notes.md` 文件
- readme 中没有损坏的链接
- readme 中没有 `pnpm run exercise` 命令
- 每个子文件夹需要 `main.ts`，除非是只有 readme 的练习

## 移动/重命名练习

当重新编号或移动练习时：

1. 使用 `git mv` (而不是 `mv`) 重命名目录 - 保留 git 历史记录
2. 更新数字前缀以保持顺序
3. 移动后重新运行 lint

示例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 示例：从计划创建占位符

给定一个如下的计划：

```
章节 05：记忆技能构建
- 05.01 记忆简介
- 05.02 短期记忆 (explainer + problem + solution)
- 05.03 长期记忆
```

创建：

```bash
mkdir -p exercises/05-记忆技能构建/05.01-记忆简介/explainer
mkdir -p exercises/05-记忆技能构建/05.02-短期记忆/{explainer,problem,solution}
mkdir -p exercises/05-记忆技能构建/05.03-长期记忆/explainer
```

然后创建 readme 占位符：

```
exercises/05-记忆技能构建/05.01-记忆简介/explainer/readme.md -> "# 记忆简介"
exercises/05-记忆技能构建/05.02-短期记忆/explainer/readme.md -> "# 短期记忆"
exercises/05-记忆技能构建/05.02-短期记忆/problem/readme.md -> "# 短期记忆"
exercises/05-记忆技能构建/05.02-短期记忆/solution/readme.md -> "# 短期记忆"
exercises/05-记忆技能构建/05.03-长期记忆/explainer/readme.md -> "# 长期记忆"
```
