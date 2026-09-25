## 前置条件

- 需要 GitHub CLI `gh`。检查 `gh --version`。如果缺失，提示用户安装 `gh` 并停止。
- 需要 `gh` 认证会话。运行 `gh auth status`。如果未认证，提示用户运行 `gh auth login`（并重新运行 `gh auth status`）后再继续。

## 命名规范

- 分支：从 `main/master/default` 开始时使用 `{description}`。
- 提交：`{description}`（简洁）。
- PR 标题：`{description}` 概括完整差异。

## PR 模板发现

在创建 PR 之前，解析仓库根目录并从此处查找活跃的 GitHub PR 模板：

```shell
repo_root="$(git rev-parse --show-toplevel)"
```

模板候选顺序：

- `.github/pull_request_template.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/pull_request_template/` 下一个 `*.md` 文件
- `.github/PULL_REQUEST_TEMPLATE/` 下一个 `*.md` 文件

使用从仓库根目录发出的路径，例如 `.github/pull_request_template.md`，而不是 `./.github/pull_request_template.md`。

如果找到确切一个模板，在组合最终 PR 正文之前读取它，并使用 `--template "$template"` 传递给 `gh pr create`。

如果找到多个模板文件，在 PR 创建前停止并询问使用哪个模板。如果没有模板，使用此技能中的备用正文格式。

## 工作流

- 如果在 `main/master/default` 上，创建分支：`git checkout -b "{description}"`
- 否则保持当前分支。
- 确认状态，然后全部暂存：`git status -sb` 然后 `git add -A`。
- 简洁地提交描述：`git commit -m "{description}"`
- 如果未运行检查，运行检查。如果检查因缺失依赖/工具失败，安装依赖并重新运行一次。
- 跟踪推送：`git push -u origin $(git branch --show-current)`
- 如果 git push 因工作流认证错误失败，从 master 拉取并重试推送。
- 发现并读取仓库 PR 模板（如果存在）。
- 检查当前分支是否已有 PR：`gh pr view "$(git branch --show-current)" --json number,isDraft,url`
- 如果已存在 PR，就地更新该 PR。不要创建另一个 PR，也不要更改现有 PR 是否为草稿或准备审查。
- 如果没有 PR，打开新的草稿 PR：
  - 有模板时：`GH_PROMPT_DISABLED=1 GIT_TERMINAL_PROMPT=0 gh pr create --draft --fill --template "$template" --head "$(git branch --show-current)"`
  - 无模板时：`GH_PROMPT_DISABLED=1 GIT_TERMINAL_PROMPT=0 gh pr create --draft --fill --head "$(git branch --show-current)"`
- 编辑 PR 标题和正文，使其反映实际差异。
- 将 PR 描述写入临时文件，使用真实换行符，并通过 `--body-file` 或 `gh pr edit --body-file` 传递，以避免 `\n` 转义 markdown。

## 确定 PR

在更新流程中先前创建的 PR 时，尽可能从当前分支推断 PR：

```shell
git branch --show-current
gh pr view "$(git branch --show-current)" --json number --jq '.number'
```

如果找到现有 PR，保留其当前审查状态。永远不要将现有的准备审查 PR 转回草稿作为 `yeet` 的一部分；只有此流程创建的新 PR 应该以草稿开始。

## PR 标题

格式：`<类型>(<范围>): <主题>`

`<范围>` 是可选的。范围由描述代码库一部分的名词组成（组件、服务或子系统）。

### 示例

```
feat: 添加帽子晃动
^--^  ^------------^
|     |
|     +-> 现在时态的摘要。
|
+-------> 类型：chore、docs、feat、fix、refactor、style 或 test。
```

更多示例：

- `feat`：用户的新功能（不是构建脚本的新功能）
- `fix`：用户的 Bug 修复（不是构建脚本的修复）
- `docs`：文档更改
- `style`：格式化、缺失的分号等；无生产代码更改
- `refactor`：重构生产代码，例如重命名变量
- `test`：添加缺失的测试、重构测试；无生产代码更改
- `chore`：更新 grunt 任务等；无生产代码更改

## PR 正文内容

在调用时，使用 `gh` 编辑 PR 正文和标题以反映指定 PR 的内容。确保检查现有 PR 正文，查看是否应保留关键信息。例如，永远不要删除现有 PR 正文中的图像，因为作者可能没有恢复它的方法。

当仓库 PR 模板存在时，将最终 PR 正文适配到该模板。保留有意义的标题、必需的检查清单和特定于仓库的提示，但用净差异特定内容或 `N/A` 替换模板要求的内容。不要因为备用形状更短而丢弃模板部分。

解释更改原因至关重要。如果当前对话中讨论了动机，请确保在 PR 正文中捕获这一点。

正文还应解释发生了什么更改，但这应在解释原因之后出现。

将讨论限制在提交的净变化。通常不鼓励讨论在 PR 开发过程中尝试但后来撤销的更改。在重写 PR 正文时，如果这些细节不再适当/对未来的读者不再感兴趣，可能需要删除这些细节。

避免引用本地磁盘上的绝对路径。当谈论存储库内的路径时，只需使用仓库相对路径。

默认省略 `Verification`。仅在您有值得为审查者保留的行为证据时添加它：复现的 Bug、前后检查、针对更改行为的测试或具有输入和观察结果的场景。不要用于通用命令或自动化结果，如包测试、类型检查、代码格式化程序、预提交/预推送钩子或 CI 状态。

如果仓库模板需要验证或验证部分，保留该部分并避免通用填充：包含有意义的命令/结果、针对的手动场景或 `Not run` 并说明原因。

使用专业的 Markdown：

- 将代码、路径、命令、标志和标识符放在反引号中。
- 使用代码块引用 shell 脚本记录或多行示例。
- 使用 GitHub 永久链接引用与更改相关的现有代码。
- 引用相关的问题或 PR，但不要在 PR 自身正文中引用 PR。

### 建议的 PR 正文形状

当仓库没有 PR 模板时，使用此作为备用：

```markdown
## 为什么

描述用户可见或维护者可见的问题，包括有用的因果关系。

## 发生了什么更改

用简洁的散文描述净实现更改。
```
