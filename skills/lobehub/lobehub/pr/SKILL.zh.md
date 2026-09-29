---
name: pr
description: 为当前分支创建一个 PR（默认目标为 `canary`），包括将一个跨层分支拆分为有序堆叠的 PR，以便较低层（数据库 / 共享包 / 服务器 TRPC）在它们的调用者（桌面端 / 命令行 / UI）之前合并。在用户请求创建/提交 PR，或因客户端调用尚未在主干上的服务器合约而拆分分支时使用。触发条件包括 'pr', 'create pr', 'submit pr', 'open a PR', 'pull request', 'split this PR', 'stacked PR', 'backend should merge first', '提 PR', '提个 PR', '新建 PR', '拆 PR', '后端先合', '分层合并'。
---

# 创建拉取请求

## 分支策略

- **目标分支**: `canary`（开发分支，云生产环境）
- `main` 是发布分支 — 直接PR到main是禁止的

## 步骤

### 1. 收集上下文（并行执行）

- `git branch --show-current` — 当前分支名称
- `git status --short` — 未提交的变更
- `git rev-parse --abbrev-ref @{u} 2>/dev/null` — 远程跟踪状态
- `git log --oneline origin/canary..HEAD` — 未推送的提交
- `gh pr list --head "$(git branch --show-current)" --json number,title,state,url` — 现有的PR
- `git diff --stat --stat-count=20 origin/canary..HEAD` — 变更摘要
- 从任务中复用现有的验收链接，如果需要查找，首先遵循 [发布认证预检](../../acceptance/PROCESS.md#publish-auth-preflight)，然后运行 `publish_lh acceptance run list --json` 并按 `branch` 匹配。不要盲目取消API密钥：生产凭证可能仅存在于环境中。查找永远不会需要创建新的轮次。

### 2. 处理默认分支上的未提交变更

如果当前分支是 `canary`（或 `main`）并且存在未提交的变更：

1. 分析diff (`git diff`) 以理解变更
2. 从变更中推断分支名称，格式：`<类型>/<简短描述>`（例如 `fix/i18n-cjk-spacing`）
3. 创建并切换到新分支：`git checkout -b <分支名称>`
4. 阶段相关文件：`git add <文件>`（优先使用显式文件路径而不是 `git add .`）
5. 使用适当的gitmoji消息提交
6. 继续到步骤3

如果当前分支是 `canary`/`main` 但没有未提交的变更且没有未推送的提交，则中止 — 没有需要创建PR的内容。

### 3. 如有需要则推送

- 没有上游：`git push -u origin $(git branch --show-current)`
- 有上游：`git push origin $(git branch --show-current)`

### 4. 搜索相关的GitHub问题

- `gh issue list --search "<关键词>" --state all --limit 10`
- 仅链接具有匹配范围的issue（避免大型总括问题）
- 如果没有找到匹配的issue则跳过

### 5. 验收门禁

功能或修复在PR打开之前需要发布验收轮次（AGENTS.md → 验收）。如果步骤1未为此分支找到，首先运行 `acceptance` 技能，并带上其 `https://app.lobehub.com/acceptance/<id>` 链接。当在会话早期已经在实际产品上验证了交付时，该技能的摄取路径会直接发布现有的观察结果和工件 — 无需重新运行，无需重新计划。纯重构或工具变更且没有用户可见结果的可以跳过 — 在PR正文中说明这一点，而不是省略该行。

### 6. 使用 `gh pr create --base canary` 创建PR

- 标题：`<gitmoji> <类型>(<范围>): <描述>`
- 正文：基于PR模板（`.github/PULL_REQUEST_TEMPLATE.md`）
- 遵循模板中的 `AGENT-INSTRUCTIONS` HTML注释。保持注释，不要将它们复制到可见描述中。
- 使用魔法关键词链接相关的GitHub issue（`Fixes #123`，`Closes #123`）
- 如适用，链接Linear issue（`Fixes LOBE-xxx`）
- 在摘要部分的“测试”下放置验收链接（或明确的跳过原因）。
- 创建或更新PR时，遵循**PR模板**下源标签、隐私和AI协助规则。不要请求提示披露或阻止正常的PR工作流程等待发布对话的同意。
- 将正文写入临时文件并使用 `--body-file` 以保留格式。

### 7. 在浏览器中打开

`gh pr view --web`

## PR模板

使用 [`.github/PULL_REQUEST_TEMPLATE.md`](../../../.github/PULL_REQUEST_TEMPLATE.md) 作为正文结构、贡献分类、披露资格和必填字段的权威来源。填写这些部分时遵循其 `AGENT-INSTRUCTIONS`：

- **摘要**：每个PR都需要填写，包括必需的贡献来源标签。即使组织成员资格豁免了作者披露细节，AI辅助的工作仍然标记为 `AI-assisted`；人工审核不会使其变为仅人类。当来源无法确定时使用 `Unknown`。
- **AI协助**：应用模板的组织成员豁免仅适用于细节，绝不适用于来源标签。当需要时，使用最终的diff和验证证据填写其六个字段，而不是私人对话摘要。每个PR使用一个部分，跨会话组合工具/模型；诚实地报告未执行的审查/检查的未知元数据和未执行的检查。

提示和文本记录默认为私密，不是必填字段。只有当作者明确请求共享时，才审查确切提议的文本中的敏感信息并确认后再发布该文本。创建或更新PR的授权不是发布对话的同意。检查附加的日志和截图中的敏感信息。

### 无生产数据标识符

PR标题、正文、评论和审查回复是公开的。永远不要在它们中放入从生产数据中获取的标识符或详细信息，即使问题是在那里发现的：

- 记录id：主题 (`tpc_…`)、消息 (`msg_…`)、操作 (`op_…`)、代理 (`agt_…`)、文档 (`docs_…`)、用户、设备和机器人id。这包括代理通风id和内部复现报告的id。
- 用户详细信息：设备或主机名、本地路径、文件名、引用的用户文本和指向用户代理或主题的应用链接。

描述证据而不是："在生产主题中观察到"、"具有两个桌面的用户（设备A和设备B）"。示例中的明显占位符（`tpc_xxx`，`C:\Users\user`）是允许的。提交哈希、部署id和代码标识符不是生产数据。相同的规则适用于提交消息和代码注释。

## 注意事项

- **语言**：所有PR内容必须为英文
- 如果该分支已经存在PR，则通知用户而不是创建重复的PR

---

# 堆叠PR（跨层功能）

上述步骤为当前分支创建**一个**PR。当单个分支跨层落地 — `packages/database` 模式/模型 → 共享的 `packages/*` 库 → `src/server` TRPC → `apps/desktop` + `apps/cli` 调用者 → `src/features` UI — 将其作为一个PR发布无法安全合并：客户端调用在主干上不存在的端点，直到相同的PR合并，因此任何部分/回滚或独立审查都会中断。将其拆分为**有序的PR**，低层优先。

## 排序规则

PR只能在它调用的每一层都已经位于主干上之后才能合并。

- **服务器契约**（新的TRPC过程、更改返回形状、新的表/模型）首先合并。
- **调用者**（桌面、CLI、UI）在之后合并 — 它们调用该契约。
- 按以下问题打破平局：_“如果现在单独合并到 `canary`，它会构建并运行吗？”_ 如果不，它属于后面的PR。

## 哪个文件放入哪个PR

非明显的调用：

- **适应契约变更的前端与服务器PR一起**。如果你扩展了TRPC返回形状（例如 `listDevices` 现在返回 `platform: string | null`），消费它的组件必须在**同一个**PR中更改 — 否则服务器PR会在自己的分支上破坏构建。契约及其存储库中的消费者一起发布。
- **新的共享包与其消费者一起**，而不是服务器，除非服务器也导入它。仅由桌面/CLI导入的 `@lobechat/*` 包在客户端PR中发布。不要在低层PR中携带未使用的包。
- **工作区依赖声明**（`package.json` `workspace:*`，`pnpm-workspace.yaml`）随导入包的代码一起移动。

## git配方 — 分割现有的完整分支

起点：一个分支（`feat/x`）和一个包含所有内容的单个提交 `<FULL>`，已经推送（因此它在远程也是安全的）。

```bash
# 1. 安全网 — 在重写任何内容之前，使完整工作不可丢失
git branch backup/x-full <FULL>          # 完整提交的本地引用
git branch feat/x-clients <FULL>         # 高层分支从这里开始

# 2. 重写低层分支仅包含低层文件
git checkout feat/x                      # 这成为服务器PR
git reset --hard origin/canary
git checkout <FULL> -- <服务器/db文件…>   # 仅阶段这些路径
git commit -m "✨ feat(...): <服务器部分>"
git push --force-with-lease origin feat/x   # 从不 --force；从不推送到canary

# 3. 在低层分支上堆叠构建高层分支
git checkout feat/x-clients
git reset --hard feat/x                  # 基础 = 刚刚重写的服务器HEAD
git checkout backup/x-full -- <客户端/ui文件…>   # 仅剩余路径
git commit -m "✨ feat(...): <客户端部分>"
git push -u origin feat/x-clients
```

然后基于低层分支打开高层PR：

```bash
gh pr create --base feat/x --head feat/x-clients --title "…" --body "…"
```

`--base feat/x` 保持diff客户端专用（不泄漏服务器文件）并使其在物理上不可能在服务器合并之前合并客户端。**服务器PR合并到 `canary` 后，将客户端PR的基础重置为 `canary`**（GitHub通常在基础分支合并时自动重置；在PR正文中注明以便人工确认）。

## 验证依赖关系确实存在

整个要点是高层需要低层。证明它：在堆叠的高层分支上，类型检查调用者并确认低层引入的符号解析。

```bash
cd apps/cli && bun run type-check 2>&1 | grep -iE "connect\.ts|device\.register"
# 空的（关于你的变更）= 堆叠的基础提供 device.register ✓
```

过滤到你的修改文件 — 该仓库的独立类型检查发出预先存在的环境噪音（`__ELECTRON__`，`@/types/llm`，未构建的 `@lobechat/types`）这些不是你的。

## PR + Linear账本管理

- **每个PR仅关闭自己的层的issue**。服务器PR：`Closes LOBE-<服务器>`。客户端PR：`Closes LOBE-<包> / <桌面> / <cli>`。不要让一个PR的正文声称另一个层的issue。
- 两个PR都是 `Part of LOBE-<父>`。
- 在PR创建时，将每个已关闭的子issue移动到 **待审查**（不是完成）并添加完成评论 — 见 `linear` 技能。

## 注意事项

- **永远不要推送到 `canary`**。使用 `git checkout -b feat/x origin/canary` 切割的分支 _跟踪_ `origin/canary`，因此一个裸 `git push` 目标canary。始终使用 `git push origin feat/x` 并显式指定分支名称。
- **`--force-with-lease`，不是 `--force`** 当重写低层分支时 — 如果远程在你下面移动，它会中止。
- **在 `reset --hard` 之前备份**。步骤1的 `backup/x-full` + 推送的远程分支意味着完整提交在重写任何内容之前由 ≥3 个引用引用。使用 `git branch --contains <FULL>` 验证。
- **锁文件**：此单体仓库不提交根 `pnpm-lock.yaml`，因此新的 `workspace:*` 依赖不需要锁文件变更。在一个提交了它的仓库中，在分割后每个分支上重新生成它。
- **不要过度分割**。两个PR（契约/调用者）通常就足够了。只读取现有端点的UI页面可以是它自己的后续PR，但不要为了自己的目的将单个层分割到多个PR中。
