# 设置 Matt Pocock 的技能

搭建工程技能所假设的每个仓库配置：

- **问题追踪器**：问题存放的位置（默认为 GitHub；也支持本地 Markdown）
- **分诊标签**：用于五个标准分诊角色的字符串
- **领域文档**：存放 `CONTEXT.md` 和 ADR 的位置，以及读取它们的消费者规则

这是一个基于提示的技能，而不是一个确定性脚本。探索、展示你发现的内容、与用户确认，然后编写。

## 流程

### 1. 探索

查看当前仓库以了解其初始状态。读取所有现有内容；不要假设：

- `git remote -v` 和 `.git/config`：这是一个 GitHub 仓库吗？是哪个？
- 仓库根目录下的 `AGENTS.md` 和 `CLAUDE.md`：是否存在？是否已经有 `## Agent skills` 部分？
- 仓库根目录下的 `CONTEXT.md` 和 `CONTEXT-MAP.md`
- `docs/adr/` 和任何 `src/*/docs/adr/` 目录
- `docs/agents/`：这个技能的先前输出是否已存在？
- `.scratch/`：一个本地 Markdown 问题追踪器约定的标志
- `triage` 技能是否已安装？（与这个技能并列的 `triage` 技能文件夹，或可用的技能中的 `triage`。）这决定了 B 部分是否运行。
- 单一仓库信号：`pnpm-workspace.yaml`、`package.json` 中的 `workspaces` 字段，或填充的 `packages/*` 及其自身的 `src/`。这些仅在真正的大型多包仓库中存在；它们的缺失意味着单上下文，这几乎适用于每个仓库。

### 2. 展示发现并询问

总结现有内容和缺失内容。然后按顺序处理各个部分。一个部分，一个答案，然后下一个。

每个部分以推荐答案开头，以便用户可以一次性接受。仅在真实分支的情况下才提供单行解释；当探索已经确定时，完全跳过该部分（当 `triage` 未安装时跳过 B 部分，当没有单一仓库时跳过 C 部分）。

**部分 A：问题追踪器。**

> 解释：这个仓库的“问题追踪器”是问题存放的位置。像 `to-tickets`、`triage` 和 `to-spec` 这样的技能从其中读取和写入。它们需要知道是调用 `gh issue create`、在 `.scratch/` 下编写 Markdown 文件，还是遵循你描述的其他工作流程。选择你实际跟踪这个仓库工作的位置。

默认立场：这些技能是为 GitHub 设计的。如果 `git remote` 指向 GitHub，建议使用 GitHub。如果 `git remote` 指向 GitLab（`gitlab.com` 或自托管主机），建议使用 GitLab。否则（或如果用户更喜欢），提供：

- **GitHub**：问题存放在仓库的 GitHub Issues（使用 `gh` CLI）
- **GitLab**：问题存放在仓库的 GitLab Issues（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **本地 Markdown**：问题存放在这个仓库的 `.scratch/<feature>/` 下的文件（适用于个人项目或没有远程的仓库）
- **其他**（Jira、Linear 等）：要求用户用一段话描述工作流程；技能将把它记录为自由文本

在 `docs/agents/issue-tracker.md` 中记录选择。GitHub 和 GitLab 模板带有“将 PR 作为请求表面”标志，默认**关闭**。保持关闭，不要提出：想要在分诊队列中外部 PR 的用户可以在稍后切换该标志。

**部分 B：分诊标签词汇。** 如果 `triage` 技能未安装（探索已经告诉你），则完全跳过这个部分，因为未安装的技能不需要标签。

如果已安装，问一个问题：

> 你想保留默认的分诊标签吗？（推荐：**是**）

默认值是五个标准角色，每个标签字符串等于其名称：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。在 **是** 的情况下，按原样写入。只有在用户说不（通常是因为他们的追踪器已经使用其他名称，例如 `bug:triage` 用于 `needs-triage`）时，才收集覆盖项，以便 `triage` 应用现有标签而不是创建重复标签。

**部分 C：领域文档。** 默认为 **单上下文**（仓库根目录下的一个 `CONTEXT.md` + `docs/adr/`）。这适用于几乎每个仓库；无需询问就写入。

仅在探索发现单一仓库信号时才提供 **多上下文**（根目录下的 `CONTEXT-MAP.md` 指向每个上下文的 `CONTEXT.md` 文件）。然后确认他们想要的布局。

### 3. 确认和编辑

向用户展示以下草稿：

- 要添加到 `CLAUDE.md` / `AGENTS.md` 中（见第 4 步的选择规则）的 `## Agent skills` 块
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md` 和 `docs/agents/triage-labels.md` 的内容（最后一个仅在 `triage` 安装时）

让他们编辑后再写入。

### 4. 编写

**选择要编辑的文件：**

- 如果存在 `CLAUDE.md`，编辑它。
- 否则，如果存在 `AGENTS.md`，编辑它。
- 如果两者都不存在，询问用户要创建哪个；不要替他们选择。

永远不要在 `CLAUDE.md` 已经存在时创建 `AGENTS.md`（反之亦然）；始终编辑已经存在的那个。

如果在所选文件中已经存在 `## Agent skills` 块，请就地更新其内容而不是追加重复内容。不要覆盖用户对周围部分的编辑。

该块：

```markdown
## Agent skills

### 问题追踪器

[问题存放在哪里的一行总结]。参见 `docs/agents/issue-tracker.md`。

### 分诊标签

[标签词汇的一行总结]。参见 `docs/agents/triage-labels.md`。

### 领域文档

[布局的一行总结：“单上下文”或“多上下文”]。参见 `docs/agents/domain.md`。
```

仅在 `triage` 安装且 B 部分运行时，包含 `### Triage labels` 子块，并编写 `docs/agents/triage-labels.md`。当它不存在时，两者都省略。

然后使用此技能文件夹中的种子模板作为起点编写文档文件：

- [issue-tracker-github.md](./issue-tracker-github.md)：GitHub 问题追踪器
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)：GitLab 问题追踪器
- [issue-tracker-local.md](./issue-tracker-local.md)：本地 Markdown 问题追踪器
- [triage-labels.md](./triage-labels.md)：标签映射（仅在 `triage` 安装时）
- [domain.md](./domain.md)：领域文档消费者规则 + 布局

对于“其他”问题追踪器，从用户的描述开始，从头编写 `docs/agents/issue-tracker.md`。

### 5. 完成

告诉用户设置已完成，哪些工程技能将从此读取这些文件。提到他们可以稍后直接编辑 `docs/agents/*.md`；只有当他们想切换问题追踪器或从头开始时，才需要重新运行这个技能。
