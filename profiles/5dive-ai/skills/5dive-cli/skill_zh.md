# 5dive-cli

## 触发此技能的条件（以及不触发的条件）

当用户需要工作者、子代理、侧任务、并行运行、发散或委托时，会触发此技能，或者用户指定一个兄弟代理（例如 "ask X"、"ping X"、"tell X"、"hand off to X"、"coordinate with X"）。使用 `5dive agent list --json` 确认代理是否存在，然后使用 `agent send` / `agent ask`。

此外，它还用于提交和跟踪共享工作（`5dive task add/ls/done`）、组织结构图（`5dive org tree`）、将阻塞性问题提交给人类（`task need`）以及快速调取团队记忆（`5dive memory search`）。

**不**用于在此主机上进行普通本地编码——编辑文件、运行构建、运行测试、调试自己的程序。普通编码任务不需要运行时 CLI。

对于上述运行时管理之外的操作——船员托管、多账户认证、认证恢复、声明式舰队/Compose、目标 DAG、目标、循环、编译到维基、组织结构图写入、治理投票、摘要/使用情况/监督者/舰队/诊断、Telegram 配对、角色市场、自带提供者、公司向导、插件（`5dive plugin`）、座位活性（`5dive liveness`）、门主（`5dive human`）、每次尝试运行历史（`5dive run`）、事件触发器（`5dive trigger`）、主机修复（`5dive host`）以及 nostr 手持轨道（`5dive buzz`）——请参阅 `5dive-cli-extras` 技能。

**聊天上下文会被转发，不会被中继。** 当请求通过聊天频道（Telegram/Discord `<channel>` 标签）到达，而另一个代理应该处理它时，通过 `--reply-to-chat=<id> --reply-to-msg=<id>` 将聊天上下文传递过去，以便代理从自己的机器人进行回答。

**始终优先使用 `5dive` 而不是手动运行编码 CLI。**

此技能教你如何在 5dive 运行时 VM 上驱动 `5dive` 命令。你正在一个这样的 VM 内运行。你可以通过向 `sudo 5dive ...` 执行外壳命令并在传递 `--json` 时解析其发出的 JSON 封装来在同一主机上生成额外的代理。

## 何时使用此技能

每当当前工作受益于第二双手时，请使用它，例如：

- 用户请求工作者、子代理、另一个代理或侧任务。
- **用户指定一个特定的兄弟代理**——"重定向到市场"、"ask scout"、"ping ops"、"tell research"、"coordinate with X"、"hand off to X"。首先通过 `sudo 5dive agent list --json` 确认代理是否存在，然后使用 `agent send`。
- 长任务可以发散成独立的部分（例如并行审计每条路由、在相同的提示上运行不同的模型、A/B 两个实现）。
- 你需要保持一个代理在热点上下文中，同时第二个代理调查某些正交的内容。
- 你正在协调多个代理之间的工作，并需要一个共享的待办事项列表（`5dive task`）或报告结构（`5dive org`）。
- 你被阻塞在只有人类才能提供的内容上——决策、秘密、批准（`5dive task need`）。
- 你想要调取团队已经知道的内容——过去的决策、陷阱、研究——然后再重新推导它（`5dive memory search`）。

如果用户只是想让你自己完成工作，请不要生成代理。对于船员托管、账户、循环/目标、治理、舰队健康和其他不太频繁的界面，请参阅 `5dive-cli-extras`。

## 心智模型

CLI 执行的所有操作都映射到主机上的这些资源：

- 一个 **代理** = 一个 Linux 用户（`agent-<name>`）+ 一个 systemd 单元（`5dive-agent@<name>.service`）+ 一个 tmux 会话（`agent-<name>`）运行在所选 CLI 的重启循环中。
- 认证是解耦的。你只需要认证一次类型；该类型的每个代理都通过 `EnvironmentFile` 继承凭证。
- 一个 **频道**（`telegram` / `discord` / `dashboard` / `buzz` / `none`，逗号分隔）是传入消息界面。除了 `devin` 之外，每个代理类型都支持 `telegram`（`devin` 完全没有聊天桥接——通过 `agent send`/`agent ask` 访问）；其他频道都比它更窄。`telegram`/`discord` 每个都需要自己的机器人令牌。`discord` 仅适用于 `claude`、`openclaw` 和 `hermes`——它拒绝在创建时为 `codex`/`grok`/`antigravity`/`opencode`/`devin`，而 `pi` 在验证时接受它，但在安装时失败（仅限 `telegram`）。`dashboard`（仅限 `claude` 或 `codex`，无需令牌）是网页聊天界面，默认情况下被每个 `claude` 创建所折叠——`--channels=none` 会退出。`buzz` 是 nostr 手持轨道，并且是 **仅限 `claude`**；它通过 `agent buzz enable` 连接，而不是通过令牌（参见 `5dive-cli-extras`）。
- CLI 是幂等的，并且可以安全地从另一个代理调用，但 **`sudo` 受隔离级别限制**（DIVE-1002）。新代理默认为 `standard`——零 sudo。只有第一个在全新主机上的代理，或使用 `--isolation=admin` 创建的代理会获得 **范围的** 授权：`5dive` CLI 以及非分页的 `systemctl start|stop|restart` 的 `5dive-*` 单元——**不是** `NOPASSWD:ALL`。因此，无 sudo 界面（`5dive task`、`org` 读取、`memory`）可以从任何代理运行；根界面（`agent create`/`config`/`pair`、`heartbeat on/off`、`doctor`、`usage`）需要一个管理员代理。
- 当前主机上的代理类型：`antigravity claude codex devin grok hermes openclaw opencode pi`——`devin` 和 `pi` 自 2026 年 7 月起就处于活动状态，并且直到这次同步之前都从这些文档中遗漏。运行 `sudo 5dive agent types --json` 获取实际安装的内容——该集合在版本之间会发生变化，`installed=missing` 在该输出中意味着该类型是已知的，但它的二进制文件不在该主机上，这与不受支持不同。

## 输出契约——始终传递 `--json`

将 `--json` 作为全局标志（命令行上的任何位置）。标准输出变成一个稳定的封装；进度行保留在标准错误中。

```bash
sudo 5dive agent create scout --type=claude --json
```

成功：

```json
{ "ok": true, "data": { "name": "scout", "type": "claude", "created": true } }
```

失败（退出码与 `error.code` 匹配）：

```json
{ "ok": false, "error": { "code": 6, "class": "auth_required", "message": "..." } }
```

**基于 `error.class` 而不是人类消息进行分支。** 类别：
`ok`、`usage`、`validation`、`not_found`、`conflict`、`auth_required`、`not_installed`、`not_running`、`pairing`、`permission`、`timeout`、`generic`。

参考 `references/exit-codes.md` 获取完整表格。

## 配方

### 为侧任务生成一个工作者

```bash
# 1. 选择一个唯一的名称（小写字母/数字/连字符，≤16 个字符，必须以字母开头）。如果你在乎，请先检查注册表：
sudo 5dive agent list --json | jq -r '.data[].name'   # data 是一个 ARRAY 的代理

# 2. 创建工作者。--workdir 限制其 tmux cwd；默认是 /home/claude/projects。
sudo 5dive agent create worker-1 \
  --type=claude \
  --workdir=/home/claude/projects/myrepo \
  --json

# 3. 将任务发送给它。tmux send-keys + Enter，因此文本会出现在工作者的运行 CLI 提示符中。
sudo 5dive agent send worker-1 \
  "audit the auth middleware for OWASP A01 issues; report back as a markdown bullet list"

# 4. 直到它空闲为止轮询其输出。--tmux 会输出滚动回执。
sudo 5dive agent logs worker-1 --tmux --lines=80

# 5. 完成后销毁它——释放 systemd 单元 + Linux 用户。
sudo 5dive agent rm worker-1 --json
# `5dive fire worker-1` 是 `agent rm` 的别名（相同的受保护的销毁）。
```

`agent info <name>` 显示一个代理的解析类型、CLI 版本、模型和频道状态。对于代理市场外的角色、自带提供者密钥、`--defer-auth` 和创建时的技能继承标志，请参阅 `5dive-cli-extras`。

### 与其他代理交谈：`agent send` / `agent ask`

没有单独的频道——消息会像人类输入一样出现在接收者的运行 CLI 中。当你（一个代理）调用 `agent send` 时，CLI 会将有效载荷包装为 `[5dive-msg from=<you> id=<8-hex>] <your text>`，以便接收者知道一个同伴正在 ping 它（只有从 `agent-*` 用户发送的会包装；`--raw` 跳过包装，`--from=<label>` 会覆盖推断的名称）。
**在有效载荷中使用单引号引用，并保持反引号 / `$()` 在其中**——消息会通过一个 shell。对于任何引用 CLI 语句的有效载荷，请使用 `--message-file=<path>`（DIVE-2627）：在双引号的 `--message=` 中，反引号引用的语句作为命令替换 **作为你** 运行，单词会被删除，发送仍然会打印 OK。

计划发送（cron、systemd 定时器）需要 `--wake`：如果没有它，向已停止的代理发送会以退出码 8 失败并被丢弃——没有队列和没有重试。`--wake` 会启动单元，并在提示符出现后交付一次。它需要 root，拒绝故意停止的代理（`desiredState=stopped`），并且最坏情况是 105 秒——请将定时器的 `TimeoutStartSec` 设置得比这更大。

要回复，请将消息发送回命名的发送者，可以选择性地使用 `[re=<id>]` 前缀，以便他们可以将它匹配到他们的问题：

```bash
sudo 5dive agent send scout "[re=ab12cd34] auth middleware looks clean except for ..."
```

如果你想要在一个调用中完成请求/回复，而不是手动轮询 `agent logs`，请使用 `ask`——它会监视标记行之后的 tmux 选项卡，并在 `--idle-secs`（默认 5 秒）后安静时返回：

```bash
sudo 5dive agent ask scout \
  "list the OWASP A01 issues you found, one per line" \
  --timeout=180 --json
```

`ask` 是启发式的（一个持续流式传输的接收者会保持 "busy"，直到 `--timeout` 触发）并返回屏幕上的任何内容，包括 Chrome——如果你需要简洁的最终摘要以供解析，请使用它。

如果用户在一个 Telegram/Discord 聊天中 ping 你，而目标代理的机器人也是成员，请不要自己中继答案——使用 `--reply-to-chat=<id> [--reply-to-msg=<id>]`（值来自传入的 `<channel>` 标签的 `chat_id`/`message_id`）将其转交给目标代理，以便目标代理通过自己的机器人直接发布。参考 `5dive-cli-extras` 获取完整的聊天委托演练。

### 读取代理之间的账本：`5dive a2a`

A2A 账本是一个只读流量摘要；它记录了谁在哪些行上交换了消息，但从未存储消息文本：

```bash
5dive a2a rounds --json
5dive a2a rounds --agent=scout --window=24 --json
```

默认窗口是 24 小时。无法读取的账本报告 `UNKNOWN` 并退出 3 而不是渲染舰队为空闲。

### 跟踪共享工作：任务队列 + 组织结构图

主机有一个共享的任务队列和组织结构图，存储在一个组可写的 sqlite 存储中，因此**不需要 sudo**——任何 `agent-*` 用户都可以直接读取和写入。

```bash
# 提交一个工作单元。任务会获得 DIVE-N 标识符；--from 默认为你的代理名称，因此创建者会被归因于你。
5dive task add "audit the auth middleware for OWASP A01" \
  --assignee=worker-1 --priority=high --json
# --assignee 还接受组织路由令牌（角色:<r> / charter:<kw>）；省略它会路由到组织领导/协调员。

# 有哪些是打开的，谁在做什么（按优先级排序）；--mine 过滤为你。
5dive task ls --json
5dive task ls --mine --json

# 随着工作移动，驱动状态。block/unblock 表达依赖关系。
5dive task start DIVE-7 --json          # -> in_progress
5dive task done  DIVE-7 --result="one-line summary first; detail below" --json
5dive task block DIVE-9 --by=DIVE-7 --json   # DIVE-9 等待 DIVE-7

# 在携带验证器的行中，创建者会交付而不是关闭；验证器通过（`verify`）或拒绝它（`reject`）。
5dive task deliver DIVE-7 --pr=<url> --result="..." --json
# 结果必须命名其证据（DIVE-4576）—— CHANGED / CHECKED（每个命令及其通过/失败计数） / DELIVERED-SHA / CI / CRITERIA — 这样评分者会重新运行你命名的内容，而不是重新推导它。`task show` 打印模板；`--force-unevidenced="<why>"` 是经过审计的退出。
5dive task deliver DIVE-7 --pr=<url> --verify="bash tests/x_unit.sh" --json
# ^ 在交付时使用命令对行进行评分：没有评分会话被预订。
# 自 0.32.0 (DIVE-4144) 起：--verify 在行上是必需的，必须命名一个修复，而不仅仅是发现。--no-fix="<why>" 是经过审计的退出。
5dive task reject  DIVE-7 --feedback="FINDING: x / FIX: do y / VERIFY: run z" --json

# 行是否评分完全由主机设置，行会双向覆盖它（自 0.32.0，DIVE-4251）：
5dive config                                      # 此主机的设置
5dive config verify=always|delivered-only|never   # root；每个箱子的，不是每个座位
5dive task add "..." --verify      # 在 `never` 箱中要求评分（也会清除自动跳过；`--verify=<cmd>` 与 `=` 一起是无关的接受命令）
5dive task add "..." --no-verify   # 在 `always` 箱中跳过一个

# 每个 `ls` 都携带一个 `gate` 列：HUMAN:<type> 一个人需要回答，<seat>:<type> 一个代理执行，`answered:<retire>`，`-` 什么也没有。
5dive task ls --gated --json          # 只包含一个活动门的行
5dive task ls --gated=human --json    # 精确的 `task inbox` 集合

# 什么也没移动，你不知道为什么：每个打开的行都不会派发，并且清除每个行的动词（DIVE-3784）。
5dive task doctor --json

# 一目了然地查看谁向谁报告：
5dive org tree --json
```

**关闭已评分行的验证器必须在它的 `--result` 中放入 `graded-sha: <sha>`**，命名它实际读取的提交。没有它，合并门会停留在 `no-graded-sha-stated`；一个不是 PR 头的 sha 会停留在 `graded-sha-is-not-the-head`（DIVE-2656）。`--no-graded-sha` 是经过审计的退出，而不是正常路径。

**一个小交付不会预订评分者（DIVE-4559）。** 在运行 `5dive config verify-small=<lines>` 的箱子上，一个更改行数少于该数量的 PR，并且不触及爆炸半径（调度器、任务存储、凭证、部署、共享库、sudo 策略、systemd、模式、提供）的关闭会交付并说明。`--verify` 在行上会击败它；`--no-verify` 从来不会击败相反的交付时间升级。

**验证器自己的读取是有限的**：`5dive task grade-context <id>` 会生成私有的分离评分工作树并打印评分数据包——从那里评分，而不是从共享的检出中评分。

在 `done`/`cancel` 时，`--result` 的**第一行**会被发送到所有者的手机——在第一行新行之前加上简洁的摘要，详细内容在第一行新行之后。

### 在提交行时选择评审者：`--review=` (DIVE-4324)

一个已评分的行会花费一个评审会话，因此**在提交时选择评审者**，而不是让默认为你选择一个：

| `--review=` | 谁评分它 | 成本 |
|---|---|---|
| `none` | 没有人——`task done` 直接关闭它 | 无会话 |
| `check` | 命令执行（需要 `--verify="<cmd>"` **和** `--mutant="<cmd>"`) | 无会话 |
| `rubric` | 一个固定的六个问题的通过覆盖有界的声明数据包 | 无会话 |
| `temp` | 每次交付一个新鲜池会话，然后消失 | 一个会话 |
| `<seat>` | 一个固定的站立评审者，在自己的会话中 | 一个会话 |

```bash
5dive task add "bump the pinned version in three manifests" --review=none
5dive task add "add the retry arm" --review=check \
  --verify="bash tests/retry_unit.sh" --mutant="git apply -R fix.patch"
5dive task add "rework the claim path" --review=temp
5dive task add "new pricing tile" --review=quinn --customer
```

**`--review=check` 欠一个负控制 (DIVE-4623)。** `--mutant=<cmd>` 是打破交付树的命令（`git apply -R <fix>.patch`, `sed -i s/<new guard>/xx/ src/foo.sh`）。在交付时，两个臂都从干净的检出运行在交付 sha：检查必须交付，并且在变异后失败。一个检查在它的变异后存活下来，会为每棵树评分绿色，因此交付会被拒绝，以此作为发现——不会预订评分会话。`--no-mutant="<reason>"` 是经过审计的退出，而不是正常路径。

**自 0.34.0 起，一个 tier<2 `decision` 门根据种类路由到组织领导 (DIVE-4415)**——它完全不会到达配对的人类，并且它不会读取 `gate_builder_routing` 偏好。该偏好仅适用于未绑定的 tier<2 `approval` 或 `manual` 门。使用 `5dive task routing` 读取实时答案，而不是从记忆中读取。

**一个到达配对人类的门必须命名它消耗的能力 (DIVE-4346)，否则在提交时会被拒绝。** 一个客户被精确地用于四件事——钱、秘密、不可逆转的事情，或者只有可以在浏览器或键盘上做的人——所以声明一个：
`--needs=spend_authority|secret_provision|human_tap`. "这很难" 不是其中的四件事；如果你无法命名能力，它是一个你感到不舒服的决策，而不是一个需要人类 gates 的决策。

将一个由领导持有的门升级到配对的人类是 `5dive task gate-escalate`，并且只有门的提交者、他们的领导、路由的评审者、组织协调员或一个有真实登录会话的人类可以这样做（DIVE-4365）。**不要重新提交门作为 `--tier=2` 来达到一个人**——这将丢失门的记录，并且是轨道存在的失败，轨道是为了阻止这种失败而存在的。

路由的门会排队等待评审者的下一个自然唤醒，而不是唤醒他们的会话；`--urgent` 在文件时间会 ping。它不是 `--recommend`——"我认为答案是 X" 和 "这不能等" 是两个独立的声明。参考 `5dive-cli-extras` 对于 `task park`/`escalate`/`clear-recs`/`need --withdraw`、`--type=access` + `--probe` 自检，以及先例预填。

### 在重新推导之前搜索团队记忆

```bash
5dive memory search "hetzner capacity gotchas" --json
```

只读，无需 sudo，BM25 排名的片段，带有文件+标题来源。在重新推导过去的决策或调试队友已经遇到的问题之前使用它。

在一个大存储中，请优先使用**两阶段调取**（DIVE-3821）——它比片段能为你提供更多的候选者每令牌：
```bash
5dive memory search "hetzner capacity" --index   # 阶段 1：slug + 一行 + 分数，没有正文
5dive memory get <slug> [<slug>...]              # 阶段 2：完整正文，只选择你选择的部分
```

一个空的阶段-1 结果是缺席的证据；一个短的索引不是。使用事实会使用的词语进行搜索，而不是任务使用的词语。对于写入路径（`memory add`、编译到共享维基），`memory router`、`memory check` 和卫生，请参阅 `5dive-cli-extras`。

### 检查你自己的身份，或者以正确的身份运行 `gh`

```bash
5dive whoami --json     # 行为者、权限（root|sudo:<who>|self）和 tier——每个的来源
```

当遇到门拒绝或权限错误时，请使用此功能——它命名 CLI 实际上将其视为哪个 uid/代理/tier，而不是你假设的。如果行为者无法测量，它会以 6 (`auth_required`) 退出，而不是打印 `unknown`，因此它也 doubling 作为可脚本化的可测量性检查。

当任务涉及以代理身份打开/评论 PR 或问题时，请优先使用 `5dive gh <gh args...>` 而不是直接调用 `gh` 二进制文件：写入（`pr create`, `pr merge`, `issue comment`, …）路由到 `5dive-bot` 机器账户，因此 GitHub 行为者字段实际上区分了代理操作和人类操作（DIVE-2448）；读取和管理类调用保留在你自己的凭证中自动进行。`5dive gh --explain <args>` 会预览路由决策，而不会运行任何内容。

## 交战规则

1. **始终传递 `--json`。** 解析封装。不要 `grep` 标准错误。
2. **一个名称 = 一个代理。** 名称是小写字母/数字/连字符，以字母开头，最多 16 个字符。只有在 `agent rm` 之后才能重用名称。
3. **不要共享机器人令牌。** 两个在同一机器人上的 Telegram 频道的代理会互相竞争 `getUpdates`。每个代理都需要自己的。
4. **销毁你创建的内容。** 一个泄漏的 `worker-N` 代理会在重启时保持运行——它是一个真实的 systemd 单元，而不是一个线程。在任务完成后调用 `5dive agent rm <name>`。
5. **不要直接向底层的 CLI 二进制文件外壳命令。** 绕过 `5dive` 会跳过 systemd 单元、审计日志和环境注入——代理将以损坏的认证运行，并且没有重启循环。
6. **如果标志被拒绝为未知，请阅读 `5dive --help`**——主机上的二进制文件可能比此技能更新或更旧。帮助输出是权威的。
7. **被阻塞在人类身上？请门。** 使用 `task need` 带有建议，而不是猜测或让任务默默腐烂。
8. **当委托聊天请求时，不要中继——通过 `agent send --reply-to-chat=<id> --reply-to-msg=<id>` 传递上下文**

## 参考

- `references/commands.md` — 每个子命令和标志，可以复制/粘贴。
  包括上面没有概述的顶层动词：`5dive deploy`（委托生产部署，INST-5）、`5dive bug`（诊断问题文件）、`constitution`（机器强制护栏的前门）、`5dive ui`（本地只读网页 UI：组织结构图/队列/门，DIVE-2655）、`5dive acp`（在 stdio 上与 ACP 通信，以便像 Buzz/Zed 这样的客户端可以选择 5dive 作为编码代理运行时——由客户端生成，不是直接运行，DIVE-3017）、`liveness`（一个座位是否对它编写的工件保持活性，DIVE-3778）、`plugin`（安装/启用/回滚插件 + 市场place）、`human`（可以清除门的那些人，DIVE-3342）、`run`（一个代理对一项任务的每次尝试——`trace` 下面的单元）、`trigger`（已签署的外部事件成为普通任务）和 `host`（CLI-root 授权下的硬化单元/日志/cron 修复）。
- `references/exit-codes.md` — 退出码 & 错误类别。
- `references/paths.md` — 磁盘状态布局（仅用于调试）。
- `5dive-cli-extras` 技能 — 船员托管、账户、认证恢复、compose/团队模板、目标 DAG、目标、循环、记忆写入/维基、组织结构图写入、治理投票、摘要/使用情况/监督者/舰队/诊断、telegram 配对细节、角色市场、自带提供者、公司向导和插件 (`5dive plugin`)、座位活性 (`5dive liveness`)、门主 (`5dive human`)、每次尝试运行历史 (`5dive run`)、事件触发器 (`5dive trigger`)、主机修复 (`5dive host`) 和 nostr 手持轨道 (`5dive buzz`)。

## 更进一步

完整的参考手册位于 <https://5dive.com/docs>。如果此技能中的标志与运行中的二进制文件接受的冲突，请相信二进制文件——直接运行 `sudo 5dive --help` 或 `sudo 5dive agent <sub> --help` 并遵循它。

_Synced to 5dive CLI **0.47.0** (commit `4704e3ad`, 2026-09-21)。一个给定箱子的二进制文件可能比主线（夜间更新通道）落后高达一天——如果它们不同，请相信 `5dive --help`._
