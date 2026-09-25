# 编程代理

用于背景功能构建、PR 审查、大规模重构以及问题到 PR 的循环。不要用于简单编辑、只读查找、ACP 线程绑定工作或在 `~/.openclaw`、`$OPENCLAW_STATE_DIR` 或活动 OpenClaw 状态目录内运行。

## 严格规则

- 始终使用 `background:true` 启动。
- Codex 和 OpenCode：使用 `pty:true`。
- Codex：从不继承环境 `CODEX_HOME` 或默认的 `~/.codex`。使用单独认证的编程代理主目录，并将其限定到每个 Codex 命令。
- Claude Code：无 PTY；使用 `claude --permission-mode bypassPermissions --print`。
- 在创建之前捕获真实的通知路径。
- 工作线程必须通过 `openclaw message send` 发送完成/失败信息。
- 不要依赖心跳、系统事件或退出时通知。
- 使用 `process` 监控；不要无故杀死慢速工作线程。
- 如果用户要求特定代理，则使用该代理。
- 如果工作线程失败/挂起，则重新启动或询问；不要在后台静默地手动处理。
- 永远不要检出分支或在 `~/Projects/openclaw` 中运行背景编程代理；使用隔离的检出。
- 在任何检出或工作树创建之前，将源引用分类为可信或不可信。永远不要在仓库的批准的不可信 PR 沙盒/审查工作流之外实现贡献者控制的引用，并且永远不要在其中启动权限绕过的工 作线程。
- 对于修改 Git 支持的项目的工作，在启动之前准备和验证 Git 工作树，然后在工作线程提示中包含确切的 Git 准备块。

## 强制 Git 准备

在为修改 Git 支持的项目的工作启动 Codex、Claude Code 或 OpenCode 之前：

1. 确定目标仓库，然后选择其规范远程。如果存在且与目标匹配，则优先使用 `upstream`；否则验证 `origin`。动态解析选定远程的默认分支。从显式的任务分支或权威的现有 PR 元数据确定目标基础；对于其他共享分支，证明配置/跟踪的基础或询问。仅对新工作且没有其他指定基础时使用规范默认值。如果无法证明仓库、远程或目标基础，则停止。
2. 在任何检出或工作树创建之前，将源引用分类为可信或不可信。对于贡献者控制的引用，使用仓库批准的不可信 PR 沙盒/审查工作流，该工作流必须在沙盒内拥有引用实现，或停止。其余步骤和启动形式仅适用于可信引用。
3. 对于可信的新工作，在创建新的隔离工作树和分支之前立即运行 `git fetch --prune <canonical>`。
4. 对于可信的新工作，验证工作树的初始 `HEAD` 等于获取的目标基础 SHA。记录规范远程、规范默认分支、目标基础分支、基础 SHA、工作树路径和分支。
5. 对于可信的现有 PR 或共享分支，在从获取的源分支创建隔离工作树之前立即获取规范目标基础和源分支。记录该源引用和起始 SHA，报告其与刷新的目标基础的差异，并且不要自动变基、合并、重置、强制推送或以其他方式重写共享历史。
6. 在隔离工作树中启动工作线程，而不是在主检出中。对于 OpenClaw，主检出在 `~/Projects/openclaw` 下仍然是禁止的。

对于修改 Git 支持的项目的工作，将此块附加到工作线程提示中，并使用实际值：

```text
Git 准备（编辑前强制执行）：
- 规范远程： <canonicalRemote>
- 规范默认分支： <canonicalDefaultBranch>
- 目标基础分支： <targetBaseBranch>
- 获取的目标基础 SHA： <targetBaseSha>
- 准备模式： <新工作 | 现有 PR/共享分支>
- 检出信任：可信
- 准备源引用： <canonicalRemote/targetBaseBranch | 获取的可信源引用>
- 准备起始 SHA： <preparedStartSha>
- 隔离工作树： <worktreePath>
- 工作分支： <branch>
- 准备收据： <新工作：`git fetch --prune <canonicalRemote>` 立即在创建时从 `<canonicalRemote>/<targetBaseBranch>` 运行 | 现有分支：规范目标基础和可信源引用在创建工作树之前立即从 `<preparedSourceRef>` 在 `<preparedStartSha>` 获取>

编辑前，验证当前目录是隔离工作树，并且其初始 HEAD 等于 <preparedStartSha>。对于新工作，该 SHA 必须等于 <targetBaseSha>。永远不要编辑主检出。对于现有 PR/共享分支工作，报告差异，并且不要变基、合并、重置、强制推送或以其他方式重写共享历史，除非明确要求。
新编写的最终推送或 PR 之前，立即运行 `git fetch --prune <canonicalRemote>` 和 `git merge-base --is-ancestor <canonicalRemote>/<targetBaseBranch> HEAD`。如果祖先检查失败，则将新分支更新到最新的目标基础，重新运行相关证明，然后才能推送而不强制。对于现有 PR/共享分支工作，报告失败的祖先检查，并按照仓库工作流操作，不要重写分支。
```

对于可信引用，启动器必须在启动编辑工作线程之前创建和验证工作树；不要将工作树创建委托给该工作线程。批准的不可信 PR 工作流必须在其沙盒内拥有检出和工作树实现。永远不要在 `~/Projects/openclaw` 中启动工作线程。只读任务和非项目草稿工作不需要 Git 准备块。

## 通知块

将此形状附加到每个工作线程提示中，并使用实际值：

```text
通知路径：
- channel: <notifyChannel>
- target: <notifyTarget>
- account: <notifyAccount or omit>
- reply_to: <notifyReplyTo or omit>
- thread_id: <notifyThreadId or omit>

完成时，使用以下方式发送一个完成或失败消息：
openclaw message send --channel <channel> --target '<target>' --message '<简要结果>'
仅当上面存在时才添加 --account、--reply_to 或 --thread_id。
不要使用 openclaw 系统事件或心跳。
```

如果不存在可信赖的路径，则说明完成自动通知不可用。

## 启动形式

首先将工作线程提示写入临时文件。这避免了当所需的 通知块包含引号或换行符时出现的 shell 引用错误。

```bash
PROMPT=$(mktemp -t openclaw-worker-prompt.XXXXXX)
cat >"$PROMPT" <<'EOF'
任务。
<强制 Git 准备块>
<通知块>
EOF
printf '提示文件：%s\n' "$PROMPT"
```

从同一 shell/会话启动时使用 `$PROMPT`。如果使用单独的工具调用，则替换打印的路径。下面的启动形式仅适用于可信检出；不可信贡献者引用需要仓库批准的沙盒/审查工作流。

在主机上第一次 Codex 工作线程之前，在前景中准备一个专用的认证主目录。不要从环境 `~/.codex` 复制 `auth.json` 或其他凭证；单独授权此主目录。Codex 通过 `CODEX_HOME` 对文件和密钥环凭证进行限定。

```bash
CODEX_WORKER_HOME="$HOME/.codex-coding-agent"
mkdir -p "$CODEX_WORKER_HOME"
if ! env -u CODEX_API_KEY -u CODEX_ACCESS_TOKEN -u OPENAI_API_KEY \
  CODEX_HOME="$CODEX_WORKER_HOME" codex login status >/dev/null 2>&1; then
  printf 'Codex 编程代理登录需要 %s\n' "$CODEX_WORKER_HOME"
  env -u CODEX_API_KEY -u CODEX_ACCESS_TOKEN -u OPENAI_API_KEY \
    CODEX_HOME="$CODEX_WORKER_HOME" codex login --device-auth
fi
printf 'Codex 工作主目录：%s\n' "$CODEX_WORKER_HOME"
```

登录是一个交互式的前景设置步骤，而不是背景工作。
启动命令重复固定的引号主目录，并移除环境 Codex 和 OpenAI 认证覆盖。永远不要将工作主目录导出到 OpenClaw Gateway 环境。

Codex：

```bash
bash pty:true background:true workdir:/path/isolated-worktree command:"env -u CODEX_API_KEY -u CODEX_ACCESS_TOKEN -u OPENAI_API_KEY CODEX_HOME=\"$HOME/.codex-coding-agent\" codex exec - < \"$PROMPT\""
```

Claude Code：

```bash
bash background:true workdir:/path/isolated-worktree command:"claude --permission-mode bypassPermissions --print < \"$PROMPT\""
```

OpenCode：

```bash
bash pty:true background:true workdir:/path/isolated-worktree command:"opencode run < \"$PROMPT\""
```

## 长期问题到 PR 工作

1. 创建/重用 GitHub 问题作为持久规范。
2. 包括问题 URL、仓库、规范远程/默认分支、目标基础分支/SHA、隔离工作树、工作分支、预期的 PR、证明和通知路径。
3. 包括强制 Git 准备块，然后告诉工作线程实现、测试、运行审查直到没有接受的可用性发现，并打开 PR。
4. 立即返回问题 URL 和 `sessionId`。
5. 使用 `process` 监控；如果镜像到任务注册表，则通过任务注册表取消。

## 草稿 Codex

Codex 需要一个可信的 git 仓库。这个一次性脚本是项目工作，没有规范远程，因此不适用 Git 准备块：

```bash
SCRATCH=$(mktemp -d)
git -C "$SCRATCH" init
PROMPT=$(mktemp -t openclaw-worker-prompt.XXXXXX)
cat >"$PROMPT" <<'EOF'
构建 X。
<通知块>
EOF
printf '提示文件：%s\n' "$PROMPT"
bash pty:true background:true workdir:$SCRATCH command:"env -u CODEX_API_KEY -u CODEX_ACCESS_TOKEN -u OPENAI_API_KEY CODEX_HOME=\"$HOME/.codex-coding-agent\" codex exec - < \"$PROMPT\""
```

## 进程操作

- `list`：运行/最近的会话。
- `poll`：状态。
- `log`：输出。
- `submit`：发送输入 + Enter。
- `write`：原始 stdin。
- `paste`：粘贴文本。
- `kill`：终止。

## 状态到用户

- 说明启动了什么，在哪里，以及 `sessionId`。
- 仅在里程碑、工作线程提问、错误、需要用户操作或完成时更新。
- 如果被杀死，说明原因。
