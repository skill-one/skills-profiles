# 设置 Matt Pocock 的技能

搭建工程化技能所依赖的按仓库配置：

- **Issue tracker（问题追踪器）**：问题所在的存放位置（默认使用 GitHub；开箱即支持本地 Markdown）
- **Triage labels（分流标签）**：用于五个标准分流角色所使用的字符串
- **Domain docs（领域文档）**：`CONTEXT.md` 和 ADRs 所在的目录，以及阅读它们的消费规则

这是一个由提示词驱动的技能，而非确定性的脚本。请先探索、呈现你发现的内容，与用户确认，然后再编写。

## 流程

### 1. 探索

查看当前仓库，了解其初始状态。阅读现有内容；不要先入为主地假设：

- `git remote -v` 和 `.git/config`：这是一个 GitHub 仓库吗？是哪一个？
- 仓库根目录下的 `AGENTS.md` 和 `CLAUDE.md`：是否其中任一存在？是否已包含任一中的 `## Agent skills` 章节？
- 仓库根目录下的 `CONTEXT.md` 和 `CONTEXT-MAP.md`
- `docs/adr/` 以及任何 `src/*/docs/adr/` 目录
- `docs/agents/`：该技能此前是否有输出内容？
- `.scratch/`：表明已在使用本地 Markdown 问题追踪器惯例
- 是否已安装 `triage` 技能？（即与本技能并列的 `triage` 技能文件夹，或你可用技能中的 `triage`。这决定了第 B 节是否运行。）
- 单仓库信号：存在 `pnpm-workspace.yaml`、`package.json` 中的 `workspaces` 字段，或已填充的 `packages/*` 且其下自带 `src/`。这些仅存在于真正大型多包仓库中；其缺失意味着单上下文，这几乎是大多数仓库的情况。

### 2. 呈现发现并询问

总结现有内容与缺失内容。然后按顺序逐节处理。一节一问，确认后再处理下一节。

每个章节都先给出推荐答案，以便用户能用一句话接受。仅当选择确实存在分支时，才给出一行说明；若探索已解决该问题，则完全跳过该章节（`triage` 未安装时跳过第 B 节，无单仓库时跳过第 C 节）。

**A 节：问题追踪器。**

> 说明：对本仓库而言，“问题追踪器”是问题所在的存放位置。`to-tickets`、`triage` 和 `to-spec` 等技能会从中读取并写入内容。它们需要知道应该调用 `gh issue create`、在 `.scratch/` 下编写 Markdown 文件，还是遵循你所描述的某些其他工作流程。请选择你实际用于本仓库的工作跟踪位置。

默认立场：这些技能是为 GitHub 设计的。如果 `git remote` 指向 GitHub，则提议使用 GitHub。如果 `git remote` 指向 GitLab（`gitlab.com` 或自建主机），则提议使用 GitLab。否则（或用户有偏好时），请提供以下选项：

- **GitHub**：问题存在于仓库的 GitHub Issues 中（使用 `gh` CLI）
- **GitLab**：问题存在于仓库的 GitLab Issues 中（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **本地 Markdown**：问题作为文件存放在本仓库的 `.scratch/<feature>/` 下（适合个人项目或没有远程地址的仓库）
- **其他（Jira、Linear 等）**：请让用户用一段话描述工作流程；该技能会将其记录为自由文本

将选择记录在 `docs/agents/issue-tracker.md` 中。GitHub 和 GitLab 模板中包含一个“PRs as a request surface”（将 PRs 作为请求表面）标志，默认**关闭**。保持关闭，不要提及：想要将外部 PR 加入分流队列的用户稍后可在文件中将该标志切换开启。

**B 节：分流标签词汇。** 如果 `triage` 技能未安装（探索已告知你），则完全跳过本节，因为未安装的技能无需标签。

如果已安装，则提出一个确切问题：

> 是否希望保留默认的分流标签？（推荐：**是**）

默认为五个标准角色，每个标签字符串与其名称相同：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。若**是**，则按原样写入。仅当用户说否时，通常是因为其追踪器已使用其他名称（例如用 `bug:triage` 表示 `needs-triage`），此时收集这些覆盖配置，使 `triage` 应用现有标签，而非创建重复项。

**C 节：领域文档。** 默认采用**单上下文**（在仓库根目录下仅有一个 `CONTEXT.md` 和 `docs/adr/`）。这几乎适用于所有仓库；无需询问即可编写。

仅当探索发现单仓库信号时，才提供**多上下文**（根目录下的 `CONTEXT-MAP.md` 指向各上下文对应的 `CONTEXT.md` 文件）。然后确认他们想要的布局。

### 3. 确认并编辑

向用户展示草稿：

- 将添加到正编辑的 `CLAUDE.md` / `AGENTS.md` 中哪一个的 `## Agent skills` 区块（见第 4 步的选文件规则）
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md` 以及 `docs/agents/triage-labels.md` 的内容（仅在 `triage` 已安装时提供最后一份）

在编写前，让他们进行编辑。

### 4. 编写

**选择要编辑的文件：**

- 如果 `CLAUDE.md` 存在，则编辑它。
- 否则，如果 `AGENTS.md` 存在，则编辑它。
- 如果两者都不存在，则询问用户要创建哪一个；不要替用户选择。

永远不要在 `CLAUDE.md` 已存在时创建 `AGENTS.md`（反之亦然）；始终编辑已存在的那个文件。

如果所选文件中已存在 `## Agent skills` 区块，则就地更新其内容，而非追加重复内容。不要覆盖对周边章节的用户编辑。

该区块：

```markdown
## Agent skills

### Issue tracker

[问题被跟踪地点的简要说明]。参见 `docs/agents/issue-tracker.md`。

### Triage labels

[标签词汇的简要说明]。参见 `docs/agents/triage-labels.md`。

### Domain docs

[布局的简要说明：为“单上下文”或“多上下文”]。参见 `docs/agents/domain.md`。
```

仅在 `triage` 已安装且第 B 节运行的情况下，才包含 `### Triage labels` 子区块，并编写 `docs/agents/triage-labels.md`。若未运行，则两者均省略。

然后使用本技能文件夹中的种子模板作为起点，编写文档文件：

- [issue-tracker-github.md](./issue-tracker-github.md)：GitHub 问题追踪器
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)：GitLab 问题追踪器
- [issue-tracker-local.md](./issue-tracker-local.md)：本地 Markdown 问题追踪器
- [triage-labels.md](./triage-labels.md)：标签映射（仅在 `triage` 已安装时）
- [domain.md](./domain.md)：领域文档消费规则 + 布局

对于“其他”类型的问题追踪器，根据用户的描述从零开始编写 `docs/agents/issue-tracker.md`。

### 5. 完成

告知用户设置已完成，以及哪些工程化技能现在将读取这些文件。提及他们稍后可直接编辑 `docs/agents/*.md`；仅在用户想要切换问题追踪器或从头重启时，才需要再次运行本技能。
