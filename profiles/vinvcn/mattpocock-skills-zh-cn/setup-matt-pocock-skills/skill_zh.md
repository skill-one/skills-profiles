# 搭建 Matt Pocock 的技能

搭建 engineering skills 所假定的每仓库配置：

- **问题追踪器** - issues 存放的位置（默认 GitHub；也原生支持本地 markdown）
- **分诊标签** - 五个 canonical 分诊角色使用的字符串
- **领域文档** - `CONTEXT.md` 与 ADRs 的位置，以及读取它们的 consumer rules

这是 prompt-driven 技能，不是确定性脚本。先探索，展示发现，与用户确认，然后写入。

## 流程

### 1. 探索

查看当前仓库，理解起始状态。读取已有内容，不要假设：

- `git remote -v` 和 `.git/config` - 这是 GitHub 仓库吗？是哪一个？
- 仓库根目录的 `AGENTS.md` 和 `CLAUDE.md` - 是否存在？其中是否已有 `## Agent skills` section？
- 仓库根目录的 `CONTEXT.md` 和 `CONTEXT-MAP.md`
- `docs/adr/` 以及任何 `src/*/docs/adr/` 目录
- `docs/agents/` - 这个技能之前是否已经输出过内容？
- `.scratch/` - 表明已经在使用 local-markdown 问题追踪器约定
- 是否已安装 `triage` 技能（本技能旁边有 `triage` 文件夹，或 available skills 中存在 `triage`）？这决定 Section B 是否运行。
- Monorepo 信号：`pnpm-workspace.yaml`、`package.json` 的 `workspaces` field，或已有内容且各自带 `src/` 的 `packages/*`。只有真正的大型 multi-package 仓库才算；没有这些信号就是 single-context，几乎所有仓库都如此。

### 2. 展示发现并询问

总结已有内容和缺失内容。按顺序处理 sections：每次一个 section、一个回答，再进入下一个。

每个 section 都先给推荐答案，让用户一个词就能接受。只有 choice 真正分叉时才给一行 explainer；exploration 已经确定答案时跳过整个 section（未安装 `triage` 时跳过 Section B；没有 monorepo 时跳过 Section C）。

**Section A - 问题追踪器。**

> 解释器: "问题追踪器" 是这个仓库存放 issues 的地方。`to-tickets`、`triage` 和 `to-spec` 等技能会从中读取并写入；它们需要知道是调用 `gh issue create`、在 `.scratch/` 下写 markdown 文件，还是遵循你描述的其他工作流。请选择你实际用于跟踪这个仓库工作的位置。

默认姿态：这些技能是为 GitHub 设计的。如果 `git remote` 指向 GitHub，推荐 GitHub。如果 `git remote` 指向 GitLab（`gitlab.com` 或 self-hosted host），推荐 GitLab。否则（或用户偏好），提供：

- **GitHub** - issues 位于仓库的 GitHub Issues（使用 `gh` CLI）
- **GitLab** - issues 位于仓库的 GitLab Issues（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **本地 markdown** - issues 作为文件位于本仓库的 `.scratch/<feature>/` 下（适合个人项目或没有 remote 的仓库）
- **其他**（Jira、Linear 等）- 让用户用一段话描述工作流；技能会把它记录为 freeform prose

把选择记录到 `docs/agents/issue-tracker.md`。GitHub 和 GitLab templates 带有 “PRs as a request surface” flag，默认 **off**；保持关闭且不要提问。想把 external PRs 放入 triage queue 的用户可以之后直接修改文件。

**Section B - Triage label 词汇。** 如果未安装 `triage`，完全跳过本 section；未安装的技能不需要 labels。

如果已安装，只问一个问题：

> 是否保留默认 triage labels？（推荐: **yes**）

默认值是五个 canonical roles，label string 与 role name 相同：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。回答 yes 就原样写入。只有用户说 no（通常因为 tracker 已使用其他名称，例如用 `bug:triage` 表示 `needs-triage`）时，才收集 overrides，避免 `triage` 创建重复 labels。

**Section C - 领域文档。** 默认 **single-context**：仓库根目录下一个 `CONTEXT.md` + `docs/adr/`。这适合几乎所有仓库，直接写入，无需提问。

只有 exploration 找到 monorepo signals 时，才提供 **multi-context**（root 下 `CONTEXT-MAP.md` 指向每个 context 的 `CONTEXT.md` files），并确认用户想要哪种 layout。

### 3. 确认并编辑

向用户展示草稿：

- 要添加到 `CLAUDE.md` / `AGENTS.md` 的 `## Agent skills` block（选择规则见 step 4）
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md`，以及仅在安装了 `triage` 时才有的 `docs/agents/triage-labels.md` 内容

写入前允许用户修改。

### 4. 写入

**选择要编辑的文件：**

- 如果 `CLAUDE.md` 存在，编辑它。
- 否则如果 `AGENTS.md` 存在，编辑它。
- 如果两者都不存在，询问用户要创建哪一个；不要替用户选择。

当 `CLAUDE.md` 已存在时，绝不创建 `AGENTS.md`（反之亦然）；始终编辑已经存在的那个。

如果所选文件已有 `## Agent skills` block，就原地更新其内容，而不是追加重复 block。不要覆盖周围 sections 的用户编辑。

Block：

```markdown
## Agent skills

### 问题追踪器

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### 领域文档

[one-line summary of the layout - "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

只有安装了 `triage` 且 Section B 实际运行时，才包含 `### Triage labels` sub-block 并写入 `docs/agents/triage-labels.md`；否则两者都省略。

然后使用本技能文件夹中的 seed templates 作为起点写 docs files：

- [issue-tracker-github.md](./issue-tracker-github.md) - GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) - GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md) - local-markdown issue tracker
- [triage-labels.md](./triage-labels.md) - label mapping（仅当安装了 `triage`）
- [domain.md](./domain.md) - domain doc consumer rules + layout

对于 "other" issue trackers，根据用户描述从头写 `docs/agents/issue-tracker.md`。

### 5. 完成

告诉用户 setup 已完成，以及哪些 engineering skills 现在会读取这些文件。说明他们之后可以直接编辑 `docs/agents/*.md`；只有当他们想切换问题追踪器或从头开始时，才需要重新运行此技能。
