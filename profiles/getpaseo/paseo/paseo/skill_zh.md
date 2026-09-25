Paseo 是一个远程守护进程，用于管理编码代理和终端。通过 MCP 工具或 CLI 来控制它。

## 项目

通过 CLI 管理守护进程的项目注册表：

```bash
paseo project create [路径]
paseo project ls
paseo project rename <项目ID> <名称>
paseo project rename <项目ID> --reset
paseo project delete <项目ID>
```

对于本地守护进程，`project create` 默认为当前目录，并在 CLI 机器上解析相对路径。使用 `--host` 或 `PASEO_HOST` 时，始终提供一个路径；目标守护进程将在其自己的机器上解释它。删除项目会存档其活动工作区，并从 Paseo 中删除该项目，但不会删除项目目录。

## 工作区

**`create_workspace`** — 独立于任何代理创建工作区。必需：`isolation` (`local` 或 `worktree`)。Worktree 孤立支持 `mode: "branch-off" | "checkout-branch" | "checkout-pr"`：使用 `branchName`/`baseBranch` 为新分支，`branch` 为现有分支，或 `prNumber` 加上可选的 `forge`/`projectPath` 为更改请求。`worktreeSlug` 控制管理路径。返回以 `workspaceId` 为中心的工 作区描述符。

明确选择 `baseBranch`：`origin/main` 选择远程跟踪分支；`refs/heads/main` 选择本地 main。裸 `main` 在存在时优先选择本地 main，否则 `origin/main`。Paseo 保留用于工作区比较的解析引用，即使在重新构建分支或更改其 PR 目标后也是如此。

**`list_workspaces`** — 列出活动工作区。

**`archive_workspace`** — `{ workspaceId }`。存档工作区及其代理和终端。本地目录保留；Paseo 仅在存档其最终活动工作区引用后才会删除拥有的 worktree。

**`rename_workspace`** — `{ workspaceId, name }`。重命名工作区。

## 工作区脚本

配置的 `paseo.json` 脚本使用与工具和 CLI 相同的受监督生命周期。

**`list_workspace_scripts`** — `{ workspaceId }`。列出配置的脚本，包括生命周期、服务端口、代理 URL、健康状态、退出代码和终端 ID。

**`start_workspace_script`** — `{ workspaceId, scriptName }`。通过 Paseo 的管理的工作区脚本启动器启动一个配置的脚本，并返回其状态元数据。

**`stop_workspace_script`** — `{ workspaceId, scriptName }`。通过其受监督的终端停止正在运行的脚本，并返回停止状态元数据。

匹配的 CLI 界面接受显式的工作区 ID 或解析当前目录：

```bash
paseo script ls [--cwd <路径> | --workspace <workspace-id>]
paseo script start <名称> [--cwd <路径> | --workspace <workspace-id>]
paseo script stop <名称> [--cwd <路径> | --workspace <workspace-id>]
```

## 代理

**`create_agent`** — 必需：`title`，`provider` (`claude/opus`，`codex/gpt-5.4`，…)`，`initialPrompt`。可选：`workspaceId`，`notifyOnFinish`，`settings`，`labels`。返回 `{ agentId, workspaceId, … }`。

初始运行时设置位于 `settings` 下：`modeId`，`thinkingOptionId` 和提供程序特定的 `features`。代理配置文件是这些值的首选来源。对于 Codex 快速模式，在创建代理时传递 `settings: { features: { "fast_mode": true } }`。

代理范围的创建始终创建您的子代理。省略 `workspaceId` 以使用当前工作区；传递由 `create_workspace` 返回的工作区以进行隔离委托。位置永远不会改变父级。

分离是子代理跟踪中的明确用户操作，而不是代理工具。跨工作区的子代理即使它也出现在其工作区的普通选项卡中，仍然是您的子代理。

代理范围的 `create_agent` 默认 `notifyOnFinish` 为 true。仅当工作真正是“发射并忘记”时才将其设置为 `false`。

**`send_agent_prompt`** — `{ agentId, prompt }`。用于对现有代理的后续操作。代理范围的提示调用默认为 `background: true` 和 `notifyOnFinish: true`；顶层调用默认为阻塞且无回调。对于同步后续操作，传递 `background: false` 并使用返回的结果。

**`update_agent`** — `{ agentId, name?, labels?, settings? }`。使用 `settings` 对现有代理进行运行时更改：`modeId`，`model`，`thinkingOptionId` 和提供程序特定的 `features`。对于 Codex 快速模式，传递 `settings: { features: { "fast_mode": true } }`。

**`list_agents`** — 按 `cwd`，`statuses`，`sinceHours`，`includeArchived` 过滤。

**`archive_agent`** — `{ agentId }`。如果正在运行，则中断，并从活动列表中删除。

## 代理配置文件和提供程序发现

**`list_profiles`** — 由人类配置的命名启动包。在决定如何启动委托代理之前，调用此工具并阅读每个配置文件的 `notes`。选择用户请求的命名配置文件，或 `notes` 与工作最匹配的配置文件。

`create_agent` 上没有 `profile` 参数。将选定的配置文件实例化为调用：

- 将 `provider` 和 `model` 组合为 `create_agent.provider` 的 `provider/model` 值
- 将 `modeId` 复制到 `settings.modeId`
- 将 `thinkingOptionId` 复制到 `settings.thinkingOptionId`
- 将 `featureValues` 复制到 `settings.features`

省略缺失的值。不要记住选定的配置文件或稍后推断漂移；配置文件仅是启动配置。

如果没有配置文件匹配，或者没有配置任何配置文件，则使用下面的提供程序发现工具，而不是猜测。当没有配置的配置文件匹配时，告诉用户您回退的原因。

**`list_providers`** — 紧凑的提供程序可用性和模式。

**`list_models`** — 一个提供程序的完整模型列表。仅当您需要模型 ID 或思考选项时才使用；列表可能很大。

**`inspect_provider`** — 紧凑的提供程序能力和功能检查。必需：`provider`；当您不在代理范围会话中时传递 `cwd`。可选：`settings`，包含草稿 `model`，`modeId`，`thinkingOptionId` 和 `features`。

仅设置 `inspect_provider` 返回的功能 ID。对于 Codex 快速模式，查找 `fast_mode` 并将 `settings: { features: { "fast_mode": true } }` 传递给 `create_agent` 或 `update_agent`。

## 计划和心跳

**`create_schedule`** — 按cron计划启动新代理。必需：`prompt`，`cron`，`provider`。可选：`timezone`，`name`，`cwd`，`maxRuns`，`expiresIn`。当周期性工作应存在于新鲜代理中时使用。

**`create_heartbeat`** — 按cron计划向您发送提示。必需：`prompt`，`cron`。可选：`timezone`，`name`，`maxRuns`，`expiresIn`。用于提醒、PR/构建看护和应返回到此对话的状态检查。

**`delete_heartbeat`** 停止它。MCP 故意不暴露心跳更新工具；当任务或计划更改时，删除并重新创建。

计划具有完整的列表/检查/更新/暂停/恢复/运行一次/日志/删除界面。心跳故意没有。

## 等待

代理需要时间 — 10–30+ 分钟是常规的。优先使用异步工作流。

对于代理范围的 `create_agent` 和后台 `send_agent_prompt`，除非工作真正是“发射并忘记”，否则省略 `notifyOnFinish` 或将其设置为 `true`。当目标代理完成、出错或需要权限时，您将收到通知。继续其他工作。通知会自行到达。

不要轮询 `list_agents` 或 `get_agent_status` 来“检查”正在运行的代理。通知会告诉您。

## CLI 语义

CLI 和工具即使在语法不同的情况下也使用相同的所有权语义：

```bash
paseo workspace create --isolation worktree --mode branch-off --new-branch fix-x --base origin/main
paseo workspace create --isolation worktree --mode checkout-branch --branch existing-work
paseo workspace create --isolation worktree --mode checkout-pr --pr-number 42
paseo run --provider codex/gpt-5.4 --mode full-access --workspace <workspace-id> "<prompt>"
paseo run --provider codex/gpt-5.4 --mode full-access --new-workspace worktree --worktree-mode branch-off --new-branch fix-x --base origin/main "<prompt>"
paseo send <agent-id> "<follow-up>"
paseo ls
paseo schedule create --cron "*/15 * * * *" "ping main build"
paseo heartbeat create --cron "*/15 * * * *" "check the build"
```

使用 `paseo --help` 和 `paseo <cmd> --help` 进行发现。

对于产品问题、设置、日志、版本问题或故障排除，使用 **paseo-help** 技能。
