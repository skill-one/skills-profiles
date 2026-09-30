---
name: conventional-git
description: 常规提交 v1.0.0 分支命名、工作区命名和提交信息标准，适用于 GitHub 和 GitLab 项目。在创建分支、命名工作区、编写提交信息、生成提交信息、审查分支规范或设置变更日志自动化时使用。当您的项目需要一致的 git 历史记录、基于 SemVer 的发布、可解析的变更日志生成或自动关闭问题时适用。当用户询问如何命名工作区、创建 git 工作区或在分支旁边组织工作区时触发。
---

# 传统的提交规范与分支命名

遵循 Conventional Commits v1.0.0 规范进行分支命名和提交信息编写——一致的命名方式能让工具自动生成变更日志、强制 SemVer 版本号变更，并按关注点过滤历史记录。

## 分支命名

格式：`<类型>/<[问题编号]-]<描述>`——全部小写，仅使用短横线，除`/`外不包含特殊字符。

```
feat/user-authentication
feat/42-user-authentication
fix/login-race-condition
fix/87-login-race-condition
docs/api-reference-update
refactor/payment-module
```

当存在问题编号时，使用其作为前缀——GitHub 和 GitLab 会自动关联，并且能让`git log`立即追溯到追踪器。保持描述在 50 个字符以内——大多数 git UI 在这个长度附近截断分支名。将类型与你的工作内容匹配——这是读者一眼就能理解分支用途的契约。

**绝对不要**在分支名中包含`worktree`——git worktrees 是本地检出机制，不是分支概念；这样命名会将实现细节泄露到远程仓库，并混淆其他贡献者。

## Worktree 命名

Worktrees 是本地检出目录——它们永远不会出现在远程仓库中。将它们放在`.claude/worktrees/`下，并将分支`/`分隔符替换为短横线进行命名。

```
git worktree add .claude/worktrees/feat-user-authentication feat/user-authentication
git worktree add .claude/worktrees/fix-87-login-race-condition fix/87-login-race-condition
```

目录名与分支名保持一致，这样`git worktree list`能保持可读性，并且每个 worktree 都能立即追溯到其对应的分支，无需检查检出状态。创建新的 worktree 前运行`git worktree list`——如果已有覆盖相同分支的 worktree，请复用它。

将 worktree 限制在单个分支范围内。在别人的 worktree 中进行无关工作会混淆哪些变更属于哪里，并使清理工作出错风险增加。

一旦其对应的分支被合并，就移除 worktree——无论是本地合并后，还是远程的拉取/合并请求关闭后。过时的 worktree 会累积，并使`git worktree list`变得难以阅读。

```bash
git worktree remove .claude/worktrees/feat-user-authentication   # 分支已本地合并
git worktree prune                                                # 移除指向已删除目录的引用
```

## 提交信息格式

```
<类型>[可选范围]: <描述>
[可选正文]
[可选页脚]
```

**类型：**

| 类型       | SemVer | 使用场景                 |
| ---------- | ------ | ------------------------ |
| `feat`     | MINOR  | 新功能                   |
| `fix`      | PATCH  | 修复 Bug                |
| `docs`     | —      | 仅文档变更               |
| `style`    | —      | 格式调整，无逻辑变更     |
| `refactor` | —      | 代码重构，无功能/修复变更 |
| `perf`     | —      | 性能改进                 |
| `test`     | —      | 添加/修复测试           |
| `build`    | —      | 构建系统、依赖           |
| `ci`       | —      | CI 配置                 |
| `chore`    | —      | 其他（非 src/test）      |
| `revert`   | —      | 撤销之前的提交           |

**规则：**

- 标题行 ≤ 72 个字符——git log 和 GitHub/GitLab UI 会静默截断更长的标题
- 使用祈使语气："add" 而不是 "added"——读起来像指令，而不是历史记录
- 无首字母大写，无句号——强制变更日志工具的统一解析
- 正文与前文用空行分隔——解析器在第一个空行处分割标题和正文
- 重大变更：在类型/范围后使用`!`，或添加`BREAKING CHANGE:`页脚（触发 MAJOR 版本号变更）——仅正文描述的变更对变更日志工具不可见
- `revert` 提交的正文应包含`This reverts commit <hash>.`——`git revert` 会自动生成；不要删除它
- **绝对不要**为 Claude 或其他 AI 代理添加 Claude 签名、AI 代理归属或`Co-authored-by`后缀到提交中

**示例：**

```
feat(auth): 添加 JWT token 刷新
```

```
fix: 防止并发请求中的竞争条件

引入请求 ID 并引用最新请求。
忽略过期请求的响应。
```

```
refactor!: 停用 Go 1.18 支持

BREAKING CHANGE: Go 1.18 不再受支持；使用 1.21+ 的 stdlib API
```

## 通过提交信息关闭问题

GitHub 和 GitLab 都能检测提交信息中的关键词，并在提交合并到默认分支时自动关闭引用的问题。将引用放在**页脚**（推荐——保持标题行整洁）。

**关键词：** `close`、`closes`、`closed`、`fix`、`fixes`、`fixed`、`resolve`、`resolves`、`resolved`——不区分大小写。

**GitHub:**

```
fix(auth): 防止 token 过期竞争条件

Closes #42
Closes owner/repo#99
```

- 触发条件：合并到**默认分支**（通常是`main`）
- 跨仓库：`Closes owner/repo#42`
- 关闭多个：`Closes #42, closes #43`
- PR 描述中也有效

**GitLab:**

```
feat: 添加暗黑模式支持

Resolves #101
Closes group/project#42
```

- 触发条件：合并到**默认分支**（项目可配置）
- 跨项目：`Closes group/project#42`
- 关闭多个：`Closes #101, closes #102`
- PR 描述中也有效

**技巧：** 与提交类型配合使用——`fix:`关闭 Bug 问题，`feat:`关闭功能请求——保持变更日志在语义上连贯。

## 常见错误

| 错误 | 修正 |
| --- | --- |
| `feat: Added login page` | `feat: add login page`——祈使语气，无首字母 |
| `fix: fix bug.` | `fix: fix bug`——无句号 |
| 标题超过 72 个字符 | 缩短；将详情移至正文 |
| 重大变更仅存在于正文 | 添加`!`或`BREAKING CHANGE:`页脚——工具无法检测仅正文 |
| `feat(adding-auth): ...` | `feat(auth): ...`——范围是名词，不是动词 |
| 标题行包含`Closes #42` | 移至页脚——保持标题整洁且可解析 |

## 最佳实践

- 保持分支类型与提交类型一致——`feat/auth-*`分支 → `feat(auth):`提交
- 每个分支一个关注点——将修复混入功能分支会混淆变更日志
- 在分支内一致使用范围——全程使用`feat(auth):`，中途不改为`feat(user):`
- **合并压缩（Squash merge）：** 当压缩合并 PR/MR 时，分支提交会被合并为一条——PR/MR 标题成为提交信息。如果标题不符合传统提交规范格式，变更日志生成会静默失败。始终在压缩前设置 PR 标题。
