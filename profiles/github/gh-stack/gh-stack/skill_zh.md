# gh-stack

`gh stack` 是一个 [GitHub CLI](https://cli.github.com/) 扩展，用于处理堆叠的分支和拉取请求。堆叠是一个以主干为根的有序分支链，其中每个分支都基于其下方的分支有一个拉取请求，因此审阅者只看到该层级的差异。

`gh stack` 从主干开始，从左到右打印堆叠：

```
(main) <- auth <- api <- frontend
```

左边是**底部**，右边是**顶部**。`auth` 基于 `main` 并首先合并；`frontend` 最后合并。`up` 向顶部移动，远离主干；`down` 向主干移动。基础工作应位于底部，依赖于它的代码位于上方。关于如何选择层级，请阅读 `references/stack-design.md`。

## 安装

```bash
gh extension install github/gh-stack
git config rerere.enabled true         # 记录冲突解决方案
git config remote.pushDefault origin   # 如果仓库有多个远程，则必需
```

## 非交互式使用

`gh stack` 根据**标准输出是否为 TTY** 来决定是否创建分支。管道、大多数命令会干净地报错或打印静态文本；在 PTY 下，相同的命令会打开提示符或全屏 TUI 并永久阻塞。代理程序不同，因此始终传递下面的标志，而不是依赖该检测。

**多个远程仓库：** 除非配置了 `remote.pushDefault`，否则永远不要在没有 `--remote <name>` 的情况下运行 `push`、`submit`、`sync`、`rebase` 或 `link`。`checkout` 和 `trunk` 没有 `--remote` 标志，并且需要该配置。

| 始终运行 | 从不运行裸命令 | 原因 |
|---|---|---|
| `gh stack view --json` | `gh stack view` | 在 PTY 下打开 TUI |
| `gh stack submit --auto` | `gh stack submit` | 为每个新 PR 提示标题 |
| `gh stack merge <target> --yes` | `gh pr merge` | `gh pr merge` 无法合并堆叠 |
| `gh stack init <branch>...` | `gh stack init` | 提示输入分支名称 |
| `gh stack add <branch>` | `gh stack add` | 提示输入名称，即使管道也会失败 |
| `gh stack checkout <target>` | `gh stack checkout` | 打开选择菜单 |
| `gh stack up` / `down` / `top` / `bottom` | `gh stack switch` | `switch` 仅限于菜单 |
| — | `gh stack modify` | 仅 TUI，没有非交互式路径 |

- `view --short` 在两种模式下都是安全的，但它是为人类格式化的。使用 `--json` 进行解析。
- **当不同的本地堆叠已经覆盖了这些分支时，无法强制执行 `checkout <pr>`**。首先运行 `gh stack unstack --local`（这将保留 GitHub 上的堆叠），然后重试。

## 分支放置

- **开始多部分工作：** 在编写文件之前创建堆叠。不要在主干上实现所有问题，然后再拆分。将每个依赖项放在每个层级中，从底部到顶部。
- **编辑现有堆叠：** 在编辑之前检出拥有该更改的层级。永远不要在当前顶分支上提交较低层级的关注点。运行 `gh stack view --json`；如果所有权不明确，请检查 `git log --all -- <path>`。然后检出所有者，编辑，提交，向上重基，并返回顶部。

```bash
gh stack down                   # 或者：gh stack checkout api
git add ... && git commit -m "添加 get-user 端点"
gh stack rebase --upstack       # 在更改上重播所有上级分支
gh stack top                    # 返回到原来的位置
gh stack push
```

## 核心循环

```bash
gh stack init auth              # 创建堆叠并检出其分支
git add ... && git commit -m "添加 auth 中间件"
gh stack add api                # 下一个层级，从当前分支分出
git add ... && git commit -m "添加 API 路由"
gh stack submit --auto          # 推送每个分支并打开草稿 PR
gh stack view --json            # 确认
```

向 `submit` 添加 `--open` 以创建已准备好审查的 PR，而不是草稿。分支名称是逐字复制的 — `gh stack add refactor/foo` 创建 `refactor/foo`。

## 保持同步

```bash
gh stack sync                   # 获取，与 GitHub 重新同步，重基，推送，刷新 PR 状态
gh stack sync --prune           # 还会删除已合并 PR 的本地分支
```

在没有 `--prune` 的情况下，非交互式时不会发生修剪。如果本地和远程堆叠已经分叉，`sync` 会打印两个链，不会进行任何更改，并以状态码 0 退出，显示 `Sync aborted` — 请参阅 `references/troubleshooting.md`。

## 合并

使用参数限定合并范围：

```bash
gh stack merge 42 --yes          # PR #42 以及它下方所有未合并的 PR
gh stack merge 7 --yes           # 堆叠 #7 中所有未合并的 PR
gh stack merge 42 --yes --squash # 或者 --merge，--rebase，--merge-method <方法>
```

传递一个 PR 编号来合并该 PR 以及它下方所有未合并的 PR，或者传递一个堆叠编号来合并该堆叠中所有未合并的 PR。该操作是全有或全无的：如果该集合中的任何 PR 无法合并，则都不会合并。

如果没有方法标志，则重用最后使用的方法。如果基础分支使用合并队列，则堆叠会被加入队列，并且队列会选择方法，忽略任何你传递的标志并发出警告；加入队列的 PR 可能会分到不同的组。

## 读取状态

`gh stack view --json` 将 JSON 写入 **标准输出**。状态消息发送到 **标准错误** — 不要解析它们，而是根据退出码进行分支。

```
trunk           string
currentBranch   string
branches[]      名称，头部，基础，是当前，已合并，已排队，需要重基
branches[].pr   数值，URL，状态 ("OPEN" | "MERGED" | "QUEUED"); 当没有 PR 存在时不存在
```

`base` 是该分支最后一次已知包含父分支的保存 SHA。它可能比父分支的当前尖端旧。`needsRebase` 在当前父尖端不再是该分支的祖先时为真。

## 退出码

| 代码 | 含义 | 恢复 |
|---|---|---|
| 0 | 成功 | — |
| 1 | 通用错误 | 读取标准错误 |
| 2 | 不在堆叠中 | `gh stack init`，或者 `gh stack checkout <target>` |
| 3 | 重基冲突 | 跟随退出 3 恢复下的说明 |
| 4 | GitHub API 失败 | 检查 `gh auth status`，重试 |
| 5 | 无效参数 | 修正调用；请参阅 `<command> --help` |
| 6 | 需要消歧义 | 分支位于多个堆叠中；检出一个非共享分支 |
| 7 | 重基已经在进行中 | `gh stack rebase --continue` 或 `--abort` |
| 8 | 堆叠文件被锁定 | 另一个 `gh stack` 进程正在写入；在 5 秒后重试 |
| 9 | 堆叠 PR 不可用 | 仓库未启用该功能；通知用户 |
| 10 | 需要修改恢复 | `gh stack modify --abort` |

**退出 3 恢复：**

- 在 `gh stack rebase` 之后：解决文件，运行 `git add`，然后 `gh stack rebase --continue`；使用 `gh stack rebase --abort` 来恢复堆叠。
- 在 `gh stack sync` 之后：堆叠已经恢复。运行 `gh stack rebase` 来重新创建冲突，然后像上面一样解决并继续。

## 限制

- 堆叠是严格线性的：一个父级，最多一个子级。对于并行工作，请使用单独的堆叠。
- 没有非交互式重新排序或删除。错误可能会建议 `gh stack modify`，但它仅限于 TUI — 使用 `unstack` 然后是 `init` 来重新结构。
- PR 标题和正文是自动生成的。之后使用 `gh pr edit` 来更改它们。

## 更多细节

`gh stack <command> --help` 是标志和参数的权威来源。请注意，`gh stack help <command>` **不起作用** — 它会打印顶层帮助。

打开与任务触发的参考匹配的参考；无需预加载所有三个。

- `references/stack-design.md` — 在创建堆叠之前、决定使用多少层级、每个层级包含什么，或者工作是否属于新堆叠时阅读。
- `references/commands.md` — 当命令意外失败或需要其先决条件、副作用、原子性或顺序保证时阅读。
- `references/troubleshooting.md` — 在重基冲突、草稿合并后、本地和远程分叉、重新结构堆叠、或从其他工具驱动堆叠时阅读。
