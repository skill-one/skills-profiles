# 创建拉取请求

## 分支策略

- **目标分支**: `canary`（开发分支，云生产环境）
- `main` 是发布分支 — 直接向 main 分支提交 PR 是不允许的

## 步骤

### 1. 收集上下文（并行执行）

- `git branch --show-current` — 当前分支名称
- `git status --short` — 未提交的更改
- `git rev-parse --abbrev-ref @{u} 2>/dev/null` — 远程跟踪状态
- `git log --oneline origin/canary..HEAD` — 未推送的提交
- `gh pr list --head "$(git branch --show-current)" --json number,title,state,url` — 现有的 PR
- `git diff --stat --stat-count=20 origin/canary..HEAD` — 更改摘要
- 当任务覆盖了交付行为时，重用现有的验收链接。如果需要查找，首先遵循 [发布 auth 预检](../../acceptance/PROCESS.md#publish-auth-preflight)，然后运行 `publish_lh acceptance run list --json` 并按 `branch` 匹配。不要盲目取消 API 密钥：生产凭证可能仅存在于环境中。查找永远不会需要创建新的回合。

### 2. 处理默认分支上的未提交更改

如果当前分支是 `canary`（或 `main`）并且存在未提交的更改：

1. 分析 diff (`git diff`) 以了解更改
2. 从更改中推断分支名称，格式：`<类型>/<简短描述>`（例如 `fix/i18n-cjk-spacing`）
3. 创建并切换到新分支：`git checkout -b <分支名称>`
4. 阶段相关文件：`git add <文件>`（优先使用显式文件路径而不是 `git add .`）
5. 使用适当的 gitmoji 消息提交
6. 继续步骤 3

如果当前分支是 `canary`/`main` 但没有未提交的更改且没有未推送的提交，则中止 — 没有创建 PR 的必要。

### 3. 如有需要则推送

- 没有上游：`git push -u origin $(git branch --show-current)`
- 有上游：`git push origin $(git branch --show-current)`

### 4. 搜索相关的 GitHub 问题

- `gh issue list --search "<关键词>" --state all --limit 10`
- 仅链接具有匹配范围的 issue（避免大型总括 issue）
- 如果没有找到匹配的 issue，则跳过

### 5. 验收门禁

功能或修复在 PR 打开之前需要一个已发布的验收回合（AGENTS.md → 验收）。如果步骤 1 没有找到此分支的验收回合，请先运行 `acceptance` 技能，并带上其 `https://app.lobehub.com/acceptance/<id>` 链接。如果在会话早期已经在真实产品上验证了交付，该技能的摄取路径会直接发布现有的观察结果和工件 — 无需重新运行，无需重新计划。纯重构或工具更改且没有用户可见结果的可以跳过 — 在 PR 正文中标明这一点，而不是省略该行。

### 6. 使用 `gh pr create --base canary` 创建 PR

- 标题：`<gitmoji> <类型>(<范围>): <描述>`
- 正文：基于 PR 模板（`.github/PULL_REQUEST_TEMPLATE.md`）
- 遵循模板中的 `AGENT-INSTRUCTIONS` HTML 注释。保持其注释，不要将它们复制到可见描述中。
- 使用魔法关键词链接相关的 GitHub 问题（`Fixes #123`，`Closes #123`）
- 如适用，链接 Linear 问题（`Fixes LOBE-xxx`）
- 在摘要部分的 **测试** 下放置验收链接（或显式的跳过原因）。
- 创建或更新 PR 时，遵循 **PR 模板** 下的源标签、隐私和 AI 辅助规则。不要请求提示披露或阻止正常的 PR 工作流程等待发布对话的同意。
- 将正文写入临时文件并使用 `--body-file` 以保留格式。

### 7. 在浏览器中打开

`gh pr view --web`

## PR 模板

使用 [`.github/PULL_REQUEST_TEMPLATE.md`](../../../.github/PULL_REQUEST_TEMPLATE.md) 作为正文结构、贡献分类、披露资格和必填字段的权威来源。填写这些部分时遵循其 `AGENT-INSTRUCTIONS`：

- **摘要**：每个 PR 都需要填写，包括必需的贡献源标签。即使组织成员资格豁免了作者披露细节，AI 辅助的工作仍然标记为 `AI-assisted`；人工审核不会使其变为纯人工。当无法确定源时，使用 `Unknown`。
- **AI 辅助**：应用模板的组织成员豁免仅适用于细节，绝不适用于源标签。当需要时，使用最终的 diff 和验证证据填写其六个字段，而不是私人对话摘要。每个 PR 使用一个部分，跨会话组合工具/模型；诚实地报告未知的元数据和未执行的审查/检查。

提示和文本记录默认为私密，不是必填字段。只有当作者明确请求共享时，才审查确切建议的文本中的敏感信息并确认后再发布该文本。创建或更新 PR 的授权不是发布对话的同意。检查附加的日志和截图中的敏感信息。

## 注意事项

- **语言**：所有 PR 内容必须为英文
- 如果分支已经存在 PR，则通知用户而不是创建重复的 PR

---

# 堆叠式 PR（跨层功能）

上述步骤为当前分支创建 **一个** PR。当单个分支跨层落地 — `packages/database` 模式/模型 → 共享的 `packages/*` 库 → `src/server` TRPC → `apps/desktop` + `apps/cli` 调用者 → `src/features` UI — 将其作为一个 PR 发送无法安全合并：客户端调用在主干上不存在的端点，直到相同的 PR 合并，因此任何部分/回滚或独立审查都会中断。将其拆分为 **有序的 PR**，低层优先。

## 排序规则

一个 PR 只有在它调用的每一层都已经合并到主干后才能合并。

- **服务器契约**（新的 TRPC 过程、更改返回形状、新的表/模型）首先合并。
- **调用者**（桌面、CLI、UI）在之后合并 — 它们调用该契约。
- 按以下问题打破平局：_“如果现在单独合并到 `canary`，它会构建和运行吗？”_ 如果不，它属于后面的 PR。

## 哪个文件放入哪个 PR

非明显的调用：

- **适应契约更改的前端与服务器 PR 一起发送。** 如果您扩展了 TRPC 返回形状（例如 `listDevices` 现在返回 `platform: string | null`），消费它的组件必须在 _同一个_ PR 中更改 — 否则服务器 PR 会自行破坏构建。契约及其存储库中的消费者一起交付。
- **新的共享包与其消费者一起发送，而不是服务器，除非服务器也导入它。** 仅由桌面/CLI 导入的 `@lobechat/*` 包发送在客户端 PR 中。不要在低层 PR 中携带未使用的包。
- **工作区依赖声明**（`package.json` `workspace:*`，`pnpm-workspace.yaml`）随导入包的代码一起移动。

## git 配方 — 拆分现有的完整分支

起点：一个分支（`feat/x`）包含一个单一提交 `<FULL>`，其中包含所有内容，并且已经推送（因此它在远程端也是安全的）。

```bash
# 1. 安全网 — 在重写任何内容之前，使完整工作不可丢失
git branch backup/x-full <FULL>          # 完整提交的本地引用
git branch feat/x-clients <FULL>         # 高层分支从这里开始

# 2. 重写低层分支以仅包含低层文件
git checkout feat/x                      # 这成为服务器 PR
git reset --hard origin/canary
git checkout <FULL> -- <服务器/db 文件…>   # 仅阶段这些路径
git commit -m "✨ feat(...): <服务器一半>"
git push --force-with-lease origin feat/x   # 从不 --force；从不推送到 canary

# 3. 在低层分支上堆叠构建高层分支
git checkout feat/x-clients
git reset --hard feat/x                  # 基础 = 刚刚重写的服务器 HEAD
git checkout backup/x-full -- <客户端/ui 文件…>   # 仅剩余路径
git commit -m "✨ feat(...): <客户端一半>"
git push -u origin feat/x-clients
```

然后基于低层分支打开高层 PR：

```bash
gh pr create --base feat/x --head feat/x-clients --title "…" --body "…"
```

`--base feat/x` 保持 diff 仅客户端（不泄漏服务器文件）并使其在物理上不可能在服务器合并之前合并客户端。**服务器 PR 合并到 `canary` 后，将客户端 PR 的基础重新指向 `canary`**（GitHub 通常在基础分支合并时自动重新指向；在 PR 正文中标明以便人工确认）。

## 验证依赖是否实际存在

整个目的是高层需要低层。证明它：在堆叠的高层分支上，类型检查调用者并确认低层引入的符号解析。

```bash
cd apps/cli && bun run type-check 2>&1 | grep -iE "connect\.ts|device\.register"
# 空的（关于您的更改）= 堆叠的基础提供 device.register ✓
```

过滤到您修改的文件 — 此存储库的独立类型检查会发出预先存在的环境噪音（`__ELECTRON__`，`@/types/llm`，未构建的 `@lobechat/types`）这不是您的。

## PR + Linear 管理账本

- **每个 PR 仅关闭其自己的层的 issue。** 服务器 PR：`Closes LOBE-<服务器>`。客户端 PR：`Closes LOBE-<包> / <桌面> / <cli>`。不要让一个 PR 的正文声称另一个层的 issue。
- 两个 PR 都是 `Part of LOBE-<父>`。
- 在 PR 创建时，将每个已关闭的子 issue 移动到 **待审核**（不是已完成）并添加完成评论 — 见 `linear` 技能。

## 注意事项

- **从不推送到 `canary`。** 使用 `git checkout -b feat/x origin/canary` 切割的分支 _跟踪_ `origin/canary`，因此一个裸 `git push` 目标 canary。始终 `git push origin feat/x` 并使用显式分支名称。
- **`--force-with-lease`，不是 `--force`** 当重写低层分支时 — 如果远程端在您下面移动，它会中止。
- **在 `reset --hard` 之前备份。** 步骤 1 的 `backup/x-full` + 推送的远程分支意味着完整提交在您重写任何内容之前由 ≥3 个引用引用。使用 `git branch --contains <FULL>` 验证。
- **锁文件**：此单存储库不提交根 `pnpm-lock.yaml`，因此新的 `workspace:*` 依赖不需要锁文件变更。在提交一个的存储库中，每次拆分后重新生成它。
- **不要过度拆分。** 两个 PR（契约 / 调用者）通常就足够了。一个只读取现有端点的 UI 页面可以是它自己的后续 PR，但不要为了自己的目的将单个层拆分到多个 PR 中。
