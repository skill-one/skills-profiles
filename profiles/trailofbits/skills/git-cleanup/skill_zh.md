# Git 清理

通过将 git 工作树和本地分支分类为：安全可删除（已合并）、可能相关（主题相似）和活动工作（保留），安全地清理累积的 git 工作树和本地分支。

## 使用场景

- 当用户累积了大量的本地分支和工作树时
- 当分支已合并但本地未清理时
- 当远程分支已被删除但本地跟踪分支仍然存在时

## 不适用场景

- 不要用于远程分支管理（这仅是本地清理）
- 不要用于像 gc 或 prune 这样的仓库维护任务
- 不适用于无头或非交互式自动化（需要用户在两个关卡进行确认）

## 核心原则：安全第一

**未经明确用户确认，切勿删除任何内容。** 此技能使用受控工作流程，用户必须在执行任何破坏性操作之前批准每个步骤。

## 关键实施注意事项

### 合并压缩的分支需要强制删除

**重要提示：** `git branch -d` 将始终对合并压缩的分支失败，因为 git 无法检测到工作已被合并。这是预期行为，不是错误。

当您将分支识别为合并压缩时：
- 从一开始就计划使用 `git branch -D`（强制删除）
- 不要先尝试 `git branch -d` 然后再请求 `-D` —— 这会浪费用户确认
- 在确认步骤中，为合并压缩的分支显示 `git branch -D`

### 在分类之前分组相关分支

**强制要求：** 在对单个分支进行分类之前，按名称前缀对它们进行分组：

```bash
# 从分支名称中提取常见前缀
# 例如，feature/auth-*, feature/api-*, fix/login-*
```

共享前缀的分支（例如，`feature/api`、`feature/api-v2`、`feature/api-refactor`）几乎肯定是相关的迭代。将它们作为一个组进行分析：

1. 通过提交日期找到最旧和最新
2. 检查较新的分支是否包含较旧分支的提交
3. 检查哪些 PR 合并了这些工作
4. 确定较旧的分支是否被取代

将相关的分支放在一起并给出明确的建议，而不是分散在各个类别中。

### 彻底调查 PR 历史记录

不要依赖简单的关键字匹配。对于 `[gone]` 分支：

```bash
# 1. 获取分支的提交，这些提交不在默认分支中
git log --oneline "$default_branch".."$branch"

# 2. 在默认分支中搜索合并了这些工作的 PR
# 搜索依据：分支名称、提交消息关键字、PR 编号
git log --oneline "$default_branch" | grep -iE "(branch-name|keyword|#[0-9]+)"

# 3. 对于相关的分支组，跟踪哪些 PR 合并了哪些工作
git log --oneline "$default_branch" | grep -iE "(#[0-9]+)" | head -20
```

## 工作流程

### 第一阶段：全面分析

在进行任何分类之前，提前收集所有信息：

```bash
# 获取默认分支名称
default_branch=$(git symbolic-ref refs/remotes/origin/HEAD \
  2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# 受保护的分支 - 永远不要分析或删除
protected='^(main|master|develop|release/.*)$'

# 列出所有本地分支及其跟踪信息
git branch -vv

# 列出所有工作树
git worktree list

# 获取并修剪以同步远程状态
git fetch --prune

# 获取已合并的分支（合并到默认分支）
git branch --merged "$default_branch"

# 获取最近的 PR 合并历史（合并压缩检测）
git log --oneline "$default_branch" | grep -iE "#[0-9]+" | head -30

# 对于每个非受保护的分支，获取唯一提交和同步状态
for branch in $(git branch --format='%(refname:short)' \
  | grep -vE "$protected"); do
  echo "=== $branch ==="
  echo "不在 $default_branch 中的提交："
  git log --oneline "$default_branch".."$branch" 2>/dev/null \
    | head -5
  echo "未推送到远程的提交："
  git log --oneline "origin/$branch".."$branch" 2>/dev/null \
    | head -5 || echo "(没有远程跟踪)"
done
```

**关于分支名称的说明：** Git 分支名称可能包含会破坏 shell 扩展的字符。在命令中始终使用引号 `"$branch"`。

### 第二阶段：分组相关分支

**必须在单独分类之前执行此操作。**

通过共享前缀识别分支组：

```bash
# 列出分支并提取前缀
git branch --format='%(refname:short)' | sed 's/-[^-]*$//' | sort | uniq -c | sort -rn
```

对于每个包含 2 个或更多分支的组：

1. **比较提交历史** - 哪些分支包含其他分支的提交？
2. **查找合并证据** - 哪些 PR 合并了这些工作？
3. **确定“最终”分支** - 通常是最新或最完整的
4. **标记被取代的分支** - 较旧的迭代，其工作在 main 或较新的分支中

**被取代需要证据，而不仅仅是共享前缀：**
- 一个 PR 将工作合并到 main，OR
- 较新的分支包含所有来自较旧分支的提交
- 前缀名称本身不足以证明——可能包含独立工作的类似名称的分支

`feature/api-*` 分支的示例分析：

```markdown
### 相关分支组：feature/api-*

| 分支 | 提交 | PR 合并 | 状态 |
|------|------|---------|------|
| feature/api | 12 | #29 (初始 API) | 被取代 - 工作在 main 中 |
| feature/api-v2 | 8 | #45 (API 改进) | 被取代 - 工作在 main 中 |
| feature/api-refactor | 5 | #67 (重构) | 被取代 - 工作在 main 中 |
| feature/api-final | 4 | 未找到 | 被取代 - 由上述 PRs 合并 |

**建议：** 所有 4 个分支都可以删除 - 工作通过 PRs #29、#45、#67 合并到 main
```

### 第三阶段：分类剩余分支

对于不在相关组中的分支，单独分类：

```
分支是否合并到默认分支？
├─ 是 → SAFE_TO_DELETE (使用 -d)
└─ 否 → 是否跟踪远程？
        ├─ 是 → 远程已删除？([gone])
        │        ├─ 是 → 提交是否合并压缩？(检查 main 中的 PR)
        │        │        ├─ 是 → SQUASH_MERGED (使用 -D)
        │        │        └─ 否 → REMOTE_GONE (需要审查)
        │        └─ 否 → 本地是否领先于远程？(检查: git log origin/<branch>..<branch>)
        │                ├─ 是 (有输出) → UNPUSHED_WORK (保留)
        │                └─ 否 (无输出) → SYNCED_WITH_REMOTE (保留)
        └─ 否 → 是否有唯一提交？
                ├─ 是 → LOCAL_WORK (保留)
                └─ 否 → SAFE_TO_DELETE (使用 -d)
```

**类别定义：**

| 类别 | 含义 | 删除命令 |
|------|------|----------|
| SAFE_TO_DELETE | 合并到默认分支 | `git branch -d` |
| SQUASH_MERGED | 通过合并压缩工作合并 | `git branch -D` |
| SUPERSEDED | 属于一个组，通过 PR 或较新分支验证 main 中的工作 | `git branch -D` |
| REMOTE_GONE | 远程已删除，工作未在 main 中找到 | 需要审查 |
| UNPUSHED_WORK | 有未推送到远程的提交 | 保留 |
| LOCAL_WORK | 具有唯一提交的未跟踪分支 | 保留 |
| SYNCED_WITH_REMOTE | 与远程同步 | 保留 |

### 第四阶段：脏状态检测

检查所有工作树和当前目录中的未提交更改：

```bash
# 对于每个工作树路径
git -C <worktree-path> status --porcelain

# 对于当前目录
git status --porcelain
```

**突出显示警告：**

```markdown
WARNING: ../proj-auth 有未提交的更改：
  M  src/auth.js
  ?? new-file.txt

如果删除此工作树，这些更改将被丢失。
```

### 关卡 1：展示完整分析

在一个综合视图中展示所有内容。将相关分支放在一起：

```markdown
## Git 清理分析

### 相关分支组

**组：feature/api-* (4 个分支)**
| 分支 | 状态 | 证据 |
|------|------|------|
| feature/api | 被取代 | 工作在 PR #29 中合并 |
| feature/api-v2 | 被取代 | 工作在 PR #45 中合并 |
| feature/api-refactor | 被取代 | 工作在 PR #67 中合并 |
| feature/api-final | 被取代 | 较旧的迭代，已分化 |

建议：删除所有 4 个分支（工作在 main 中）

---

### 单个分支

**安全删除（使用 -d 合并）**
| 分支 | 合并到 |
|------|--------|
| fix/typo | main |

**安全删除（合并压缩，需要 -D）**
| 分支 | 合并方式 |
|------|---------|
| feature/login | PR #42 |

**需要审查 ([gone] 远程，未找到 PR)**
| 分支 | 最后提交 |
|------|----------|
| experiment/old | abc1234 "WIP something" |

**保留（活动工作）**
| 分支 | 状态 |
|------|------|
| wip/new-feature | 5 个未推送的提交 |

### 工作树
| 路径 | 分支 | 状态 |
|------|------|------|
| ../proj-auth | feature/auth | STALE (已合并) |

---

**总结：**
- 4 个相关分支 (feature/api-*) - 建议全部删除
- 1 个已合并分支 - 安全删除
- 1 个合并压缩分支 - 安全删除
- 1 个需要审查
- 1 个保留

您希望清理哪些？
```

使用 AskUserQuestion 提供清晰的选项：
- 删除所有建议的（组 + 合并 + 合并压缩）
- 删除特定组/类别
- 让我选择单个分支

**在用户响应之前不要继续。**

### 关卡 2：最终确认，显示精确命令

显示将运行的精确命令，包括正确的标志：

```markdown
我将执行：

# 已合并分支（安全删除）
git branch -d fix/typo

# 合并压缩分支（强制删除 - 工作在 main 中通过 PRs）
git branch -D feature/login
git branch -D feature/api
git branch -D feature/api-v2
git branch -D feature/api-refactor
git branch -D feature/api-final

# 工作树
git worktree remove ../proj-auth

确认？(yes/no)
```

**重要提示：** 这是删除所需的唯一确认。如果需要 `-D`，不要添加额外的确认。

### 第五阶段：执行

将每个删除作为一个**单独的命令**执行，以便部分失败不会阻止剩余的删除。报告每个命令的结果：

```bash
git branch -d fix/typo
git branch -D feature/login
git branch -D feature/api
git branch -D feature/api-v2
git branch -D feature/api-refactor
git branch -D feature/api-final
git worktree remove ../proj-auth
```

如果删除失败，报告错误并继续剩余的删除。

### 第六阶段：报告

```markdown
## 清理完成

### 已删除
- fix/typo
- feature/login
- feature/api
- feature/api-v2
- feature/api-refactor
- feature/api-final
- 工作树：../proj-auth

### 剩余（4 个分支）
| 分支 | 状态 |
|------|------|
| main | 当前 |
| wip/new-feature | 活动工作 |
| experiment/old | 需要审查 |
```

## 安全规则

1. **永不自动调用** - 仅在用户明确使用 `/git-cleanup` 时运行
2. **仅两个确认关卡** - 分析审查，然后删除确认
3. **使用正确的删除命令** - `-d` 用于合并，`-D` 用于合并压缩/被取代
4. **永不触碰受保护的分支** - main、master、develop、release/*（程序化过滤）
5. **阻止脏工作树删除** - 无明确数据丢失确认则拒绝
6. **分组相关分支** - 不要将它们分散在各个类别中

## 拒绝的理由

这些是导致数据丢失的常见捷径。拒绝它们：

| 理由 | 为什么错误 |
|------|----------|
| "分支很旧，可能安全删除" | 年龄不表示合并状态。旧分支可能包含未合并的工作。 |
| "如果需要，可以从 reflog 恢复" | reflog 条目会过期。用户通常不知道如何使用 reflog。不要依赖它作为安全网。 |
| "只是一个本地分支，没什么重要的" | 本地分支可能包含未推送到任何地方的唯一副本的工作。 |
| "PR 已合并，所以分支是安全的" | 合并压缩不会保留分支历史。验证具体提交是否被合并。 |
| "我将删除所有 `[gone]` 分支" | `[gone]` 仅表示远程已删除。本地分支可能有未推送的提交。 |
| "用户似乎想删除所有内容" | 首先展示分析。让用户选择要删除的内容。 |
| "分支有不在 main 中的提交，所以有未推送的工作" | "不在 main 中" ≠ "未推送"。一个分支可以与远程同步但未合并到 main。始终检查 `git log origin/<branch>..<branch>`。 |
