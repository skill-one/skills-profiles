# FLOW 框架为博主使用（查找、优化、获胜）

针对博客主题或 URL 运行 FLOW 查找/优化/获胜提示，将查询数据、来源笔记和页面证据转化为结构化决策，而不是即兴提示。

> 框架和提示 (c) Daniel Agrici, CC BY 4.0。来源：github.com/AgriciDaniel/flow

FLOW 是一个以证据为导向的操作模型，用于检索、引用和转换工作流程。Claude Blog 集成了 FLOW 提示库，使写作者能够将查询数据、来源笔记和页面证据转化为结构化决策，而不是即兴提示。

这项技能暴露了与博客相关的三个阶段（查找、优化、获胜），并通过提示索引保持单个 Leverage 提示可用。本地 SEO 提示（GBP、引用、本地审核）有意被排除，因为它们针对实体工作，而不是博客。

**运行时上下文。** 每次激活 `/blog flow` 时加载 `references/flow-framework.md`。仅在需要时加载提示文件，并限定在用户请求的阶段范围内。

---

## 命令

| 命令 | 它的作用 |
|------|---------|
| `/blog flow` | 显示 FLOW 概览和阶段菜单 |
| `/blog flow find [主题\|url]` | 查找阶段：关键词发现、意图映射、差距分析（5 个提示） |
| `/blog flow optimize [url]` | 优化阶段：根据上下文从 21 个提示中选择 2 到 3 个最相关的提示 |
| `/blog flow win [url]` | 获胜阶段：BOFU、转换、双重表面评分卡（3 个提示） |
| `/blog flow prompts` | 所有 30 个博客适用的提示的完整索引（查找、Leverage、优化、获胜） |
| `/blog flow sync` | 从 github.com/AgriciDaniel/flow 拉取最新的提示文件 |

单个 Leverage 提示（站外权威）可以通过 `/blog flow prompts` 访问，并且不会被提升为顶级命令，因为大多数博客工作流程将站外工作路由到其他地方。

---

## 协调逻辑

### 在 `/blog flow`（无子命令）
1. 读取 `references/flow-framework.md`。
2. 显示 FLOW 阶段概览，每个阶段有一行描述。
3. 询问用户哪个阶段符合他们当前的情况。

### 在 `/blog flow find [主题|url]`
1. 读取 `references/prompts/find/` 中的所有文件。
2. 将每个提示应用于主题或 URL，捕获需求和意图信号。
3. 交叉引用："对于更深入的简报和提纲，请查看 `/blog brief <主题>`、`/blog outline <主题>`，以及 `/blog cannibalization` 以检测与现有文章的重叠。

### 在 `/blog flow optimize [url]`
1. 读取 `references/prompts/optimize/` 中的文件名。
2. 读取先前的上下文（目标 URL、细分领域、本对话中任何先前的技能输出、来自 `/blog analyze` 的评分差异）。
3. 选择 2 到 3 个最相关的提示，然后仅加载这些文件。
4. 应用选定的提示；请注意，其余的可以通过 `/blog flow prompts` 访问。
5. 交叉引用："对于更深入的改写和验证，请查看 `/blog rewrite <文件>`、`/blog seo-check <文件>`、`/blog geo <文件>`、`/blog schema <文件>`，以及 `/blog factcheck <文件>`。"

### 在 `/blog flow win [url]`
1. 读取 `references/prompts/win/` 中的所有文件。
2. 将每个提示应用于 URL 的转换和 BOFU 上下文。
3. 交叉引用："对于再利用、全站健康和质量评分，请查看 `/blog repurpose <文件>`、`/blog audit`，以及 `/blog analyze <文件>`。"

### 在 `/blog flow prompts`
1. 读取 `references/prompts/README.md`。
2. 显示完整索引：30 个提示按阶段分组（查找、Leverage、优化、获胜），包含名称和触发条件。
3. 说明设计上排除了本地 SEO 提示；如果需要，请指向 `claude-seo` (`/seo flow local`)。

### 在 `/blog flow sync`
1. 运行：`python3 scripts/sync_flow.py`。
2. 显示 JSON 摘要（添加的文件、更新的文件、未更改的文件）。
3. 同步完成后显示归属声明。

---

## 上下文匹配（优化阶段）

优化阶段有 21 个提示。列出所有 21 个是噪音。按优先级选择：

1. **细分领域**（SaaS 或 B2B 博客侧重于页面加上技术；生活方式侧重于新鲜度加上 E-E-A-T；出版商侧重于权威加上引用）。
2. **先前的技能输出** (`/blog analyze` E-E-A-T 差距路由到权威提示；`/blog seo-check` 失败路由到页面提示；`/blog geo` 差距路由到提取格式提示）。
3. **URL 信号**（商业页面需要转换提示；信息性文章需要新鲜度加上先回答提示）。

始终显示 2 到 3 个提示。说明你选择了哪些提示以及原因。

---

## 参考文件

按需加载。启动时不要加载所有文件。

- `references/flow-framework.md`。FLOW 操作模型。每次激活 `/blog flow` 时加载。
- `references/bibliography.md`。证据来源。引用研究或统计数据时加载。
- `references/prompts/README.md`。提示索引。用于 `/blog flow prompts` 时加载。
- `references/prompts/find/`。5 个提示。用于 `/blog flow find` 时加载。
- `references/prompts/leverage/`。1 个提示。仅通过 `/blog flow prompts` 显示时加载。
- `references/prompts/optimize/`。21 个提示。选择性地用于 `/blog flow optimize` 时加载。
- `references/prompts/win/`。3 个提示。用于 `/blog flow win` 时加载。

如果 `references/` 缺失，请指示用户首先运行 `/blog flow sync`。

---

## 同步脚本

`scripts/sync_flow.py` 从 github.com/AgriciDaniel/flow 拉取提示文件，并将它们写入 `skills/blog-flow/references/` 下。仅使用标准库，仅使用 HTTPS，主机白名单为 `api.github.com`，5 MB 响应限制，原子写入，路径遍历保护。

模式：

- `python3 scripts/sync_flow.py`。将每个博客相关阶段的最新版本同步到磁盘并刷新锁文件。
- `python3 scripts/sync_flow.py --dry-run`。报告计划更改而不写入。
- `python3 scripts/sync_flow.py --ref <sha>`。将获取固定在特定的 FLOW 提交 SHA 上，以实现可重复的安装。

锁文件位于 `skills/blog-flow/references/flow-prompts.lock`，并使用与 sha256sum 兼容的格式。磁盘内容与锁文件之间的差异在每次同步运行时报告。

该脚本仅同步博客适用的阶段 (`find`、`leverage`、`optimize`、`win`)。`local` 阶段有意被跳过，以保持参考目录与技能的表面区域一致。

GitHub API 调用默认为匿名。如果环境变量中设置了 `GITHUB_TOKEN`，或者 `gh auth token` 在 403 响应后返回令牌，脚本将使用该令牌重试请求。不会将令牌写入磁盘。

---

## 归属声明

每次 `/blog flow` 激活（任何子命令）在分析之前输出：

```
Framework and prompts (c) Daniel Agrici, CC BY 4.0. Source: github.com/AgriciDaniel/flow
```

不要省略或修改归属声明。同步的文件也带有由同步脚本注入的 HTML 许可声明头。

---

## 错误处理

| 情景 | 操作 |
|------|------|
| `references/flow-framework.md` 缺失 | "FLOW 参考文件未同步。运行：`/blog flow sync`。" |
| 提示文件缺失 | "运行 `/blog flow sync` 从 FLOW 仓库拉取最新的提示。" |
| `sync_flow.py` 网络错误 | 显示脚本的 stderr。如果安装了 `gh`，请使用 `gh api rate_limit` 检查速率限制。 |
| `sync_flow.py` 403 重试后 | 设置 `GITHUB_TOKEN` 或运行 `gh auth login`，然后重试。 |
| 路径遍历中止 | 同步目标尝试逃离参考目录。检查上游仓库并固定到已知的良好 `--ref`。 |
