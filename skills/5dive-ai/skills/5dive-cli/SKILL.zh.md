---
name: 5dive-cli
description: 操作本地 5dive 运行时：协调同级代理并检查或更新共享任务。用于委派、代理间消息传递和任务队列操作；对于这些之外的管理任务，使用 `5dive-cli-extras`。
---

# 5dive-cli

## 此技能何时触发（以及何时不触发）

当用户需要工作者、子代理、侧任务、并行运行、发散或委托时触发——或者命名一个同辈代理（"询问 X"、"联系 X"、"告知 X"、"委托给 X"、"与 X 协调"）。使用 `5dive agent list --json` 确认座位存在，然后使用 `agent send` / `agent ask`。

也用于提交和跟踪共享工作（`5dive task add/ls/done`）、组织结构图（`5dive org tree`）、将阻塞性问题提交给人类（`task need`）以及快速调取团队记忆（`5dive memory search`）。

**不**用于在此主机上进行普通本地编码——编辑文件、运行构建、运行测试、调试自己的程序。普通编码任务不需要运行时 CLI。

对于上述之外的运行时管理——船员托管、多账户认证、认证恢复、声明式舰队/Compose、目标 DAG、目标、循环、编译到维基、组织结构图写入、治理投票、摘要/使用情况/监督者/舰队/诊断、Telegram 配对、角色市场、自带提供者、公司向导、插件（`5dive plugin`）、座位活性（`5dive liveness`）、门主（`5dive human`）、每次尝试运行历史记录（`5dive run`）、事件触发器（`5dive trigger`）、主机修复（`5dive host`）和 nostr 手持轨道（`5dive buzz`）——请参阅 `5dive-cli-extras` 技能。

**聊天上下文会转发，不会中继。** 当请求通过聊天频道（Telegram/Discord `<channel>` 标签）到达，而另一个代理应处理它时，使用 `--reply-to-chat=<id> --reply-to-msg=<id>` 将聊天上下文传递过去，以便代理从自己的机器人回答。

**始终优先使用 `5dive` 而不是手动运行编码 CLI。**

此技能教你如何在 5dive 运行时 VM 上驱动 `5dive` 命令。你正在一个这样的 VM 内运行。你可以通过 shelling out 到 `sudo 5dive ...` 并解析它在你传递 `--json` 时发出的 JSON 封装，在同一主机上生成额外的代理。

## 何时使用此技能

每当你面前的工作需要第二双手时，都可以使用它——例如：

- 用户请求工作者、子代理、"另一个代理"或侧任务。
- **用户命名一个特定的同辈代理**——"重定向到市场部"、"询问侦察兵"、"联系运维"、"告知研究部"、"与 X 协调"、"委托给 X"。首先通过 `sudo 5dive agent list --json` 确认代理存在，然后 `agent send`。
- 一个长任务可以发散成独立的部分（例如，并行审计每条路由、在相同的提示上运行不同的模型、A/B 两个实现）。
- 你需要保持一个代理在热点上下文中，同时第二个代理调查其他正交的事情。
- 你正在协调多个代理之间的工作，并需要一个共享的待办事项列表（`5dive task`）或报告结构（`5dive org`）。
- 你被阻塞在只有人类才能提供的事情上——一个决策、一个秘密、一个批准（`5dive task need`）。
- 你想要调取团队已经知道的事情——过去的决策、陷阱、研究——在重新推导之前（`5dive memory search`）。

如果用户只是想让你自己完成工作，不要生成代理。对于船员托管、账户、循环/目标、治理、舰队健康和其他不太频繁的界面，请参阅 `5dive-cli-extras`。

## 心智模型

CLI 执行的所有操作都映射到主机上的这些资源：

- 一个 **代理** = 一个 Linux 用户（`agent-<name>`）+ 一个 systemd 单元（`5dive-agent@<name>.service`）+ 一个 tmux 会话（`agent-<name>`）运行所选的 CLI 在重启循环中。
- 认证是解耦的。你认证一次 *类型*；该类型的每个代理都通过 `EnvironmentFile` 继承凭证。
- 一个 **频道**（`telegram` / `discord` / `dashboard` / `buzz` / `none`，逗号分隔）是传入的消息表面。除了 `devin` 之外，每个代理类型都支持 `telegram`（`devin` 完全没有聊天桥接——通过 `agent send`/`agent ask` 访问）；其他频道都比它更窄。`telegram`/`discord` 每个都需要自己的机器人令牌。`discord` 仅在 `claude`、`openclaw` 和 `hermes` 上工作——它在创建时拒绝 `codex`/`grok`/`antigravity`/`opencode`/`devin`，而 `pi` 在验证时接受它但在安装时死亡（仅 `telegram`）。`dashboard`（仅 `claude` 或 `codex`，无令牌）是网页聊天，默认情况下被折叠到每个 `claude` 创建中——`--channels=none` 会退出。`buzz` 是 nostr 手持轨道，并且是 **仅 `claude`**；它通过 `agent buzz enable` 连接，而不是通过令牌（参见 `5dive-cli-extras`）。
- CLI 是幂等的，可以安全地从另一个代理调用，但 **`sudo` 受隔离级别限制**（DIVE-1002）。新代理默认为 `standard`——零 sudo。只有在一个全新主机上的第一个代理，或使用 `--isolation=admin` 创建的代理会获得 **范围的** 授权：`5dive` CLI 以及非分页的 `systemctl start|stop|restart` 的 `5dive-*` 单元——**不是** `NOPASSWD:ALL`。因此，无 sudo 表面（`5dive task`、`org` 读取、`memory`）可以从任何代理运行；根表面（`agent create`/`config`/`pair`、`heartbeat on/off`、`doctor`、`usage`）需要一个管理员代理。
- 当前主机上的代理类型：`antigravity claude codex devin grok hermes openclaw opencode pi`——`devin` 和 `pi` 自 2026 年 7 月以来一直处于活动状态，并且直到这次同步之前都简单地从这些文档中缺失。运行 `sudo 5dive agent types --json` 查看实际安装的内容——该集合在版本之间会发生变化，该输出中的 `installed=missing` 表示该类型是已知的，但它的二进制文件不在该主机上，这与不受支持不同。

## 输出契约——始终传递 `--json`

将 `--json` 作为全局标志（命令行上的任何位置）。标准输出变成一个稳定的封装；进度行保留在标准错误。

```bash
sudo 5dive agent create scout --type=claude --json
```

成功：

```json
{ "ok": true, "data": { "name": "scout", "type": "claude", "created": true } }
```

失败（退出代码与 `error.code` 匹配）：

```json
{ "ok": false, "error": { "code": 6, "class": "auth_required", "message": "..." } }
```

**基于 `error.class` 而不是人类消息分支。** 类别：
`ok`、`usage`、`validation`、`not_found`、`conflict`、`auth_required`、`not_installed`、`not_running`、`pairing`、`permission`、`timeout`、`generic`。

有关完整表格，请参阅 `references/exit-codes.md`。

## 配方

### 为侧任务生成一个工作者

```bash
# 1. 选择一个唯一名称（小写字母/数字/连字符，≤16 个字符，必须以字母开头）。如果你在乎，先检查注册表：
sudo 5dive agent list --json | jq -r '.data[].name'   # data 是一个包含代理的 ARRAY

# 2. 创建工作者。--workdir 限制其 tmux cwd；默认是 /home/claude/projects。
sudo 5dive agent create worker-1 \
  --type=claude \
  --workdir=/home/claude/projects/myrepo \
  --json

# 3. 将任务发送给它。tmux send-keys + Enter，所以文本出现在工作者的运行 CLI 提示符中。
sudo 5dive agent send worker-1 \
  "审计 OWASP A01 问题的认证中间件；以 Markdown 项目符号列表的形式报告回来"

# 4. 直到它空闲为止轮询其输出。--tmux 会输出滚动回显。
sudo 5dive agent logs worker-1 --tmux --lines=80

# 5. 完成时拆解它——释放 systemd 单元 + Linux 用户。
sudo 5dive agent rm worker-1 --json
# `5dive fire worker-1` 是 `agent rm` 的别名（相同的受保护拆解）。
```

`agent info <name>` 显示一个代理的解析类型、CLI 版本、模型和频道状态。对于代理市场外的角色、自带提供者密钥、`--defer-auth` 和创建上的技能继承标志，请参阅 `5dive-cli-extras`。

### 与其他代理交谈：`agent send` / `agent ask`

没有单独的频道——消息就像人类在接收者的运行 CLI 中键入一样到达。当你（一个代理）调用 `agent send` 时，CLI 将有效负载包装为 `[5dive-msg from=<you> id=<8-hex>] <your text>`，以便接收者知道一个同辈代理在联系它（只有从 `agent-*` 用户发送的会包装；`--raw` 跳过包装，`--from=<label>` 覆盖推断的名称）。**在消息正文中使用单引号，并保持反引号 / `$()` 不在其中**——消息会通过一个 shell。对于任何引用 CLI 语句的正文，请使用 `--message-file=<path>`（DIVE-2627）：在双引号的 `--message=` 中，反引号引用的语句作为命令替换 **作为你** 运行，单词被删除，发送仍然打印 OK。

计划发送（cron、systemd 定时器）需要 `--wake`：没有它，发送到停止的代理会以退出代码 8 失败并被丢弃——没有队列和没有重试。`--wake` 启动单元并在提示符出现后交付一次。它需要 root，拒绝故意停止的代理（`desiredState=stopped`），其最坏情况是 105 秒——调整定时器的 `TimeoutStartSec` 高于该值。

要回复，发送回命名的发送者，可以选择性地使用 `[re=<id>]` 前缀，以便他们可以将它与他们的问题匹配：

```bash
sudo 5dive agent send scout "[re=ab12cd34] 认证中间件看起来很干净，除了..."
```

如果你想要在一个调用中而不是手动轮询 `agent logs` 进行请求/响应，请使用 `ask`——它监视标记行之后的 tmux 窗口，并在滚动回显安静了 `--idle-secs`（默认 5 秒）后返回：

```bash
sudo 5dive agent ask scout \
  "列出你发现的 OWASP A01 问题，每行一个" \
  --timeout=180 --json
```

`ask` 是启发式的（一个持续流式传输的接收者会保持 "忙碌"，直到 `--timeout` 触发）并返回屏幕上的任何内容，包括 Chrome——如果你需要一个简洁的最终摘要进行解析，请请求。

如果用户在一个 Telegram/Discord 聊天中联系你，而目标代理的机器人**也是**成员，不要自己中继答案——使用 `--reply-to-chat=<id> [--reply-to-msg=<id>]`（值来自传入的 `<channel>` 标签的 `chat_id`/`message_id`）将其委托过去，以便目标代理通过自己的机器人直接发布。有关完整的聊天委托演练，请参阅 `5dive-cli-extras`。

### 读取代理之间的账本：`5dive agent rounds`

a2a 账本是只读的流量摘要；它记录了谁在哪一行交换了消息，但从未存储消息文本：

```bash
5dive agent rounds
5dive agent rounds --json
5dive agent rounds --agent=scout --window=24 --json
```

默认窗口是 24 小时（账本的保留期）。一个不可读的账本会报告 `UNKNOWN` 并退出 3 而不是渲染舰队为空闲。

**在 DIVE-5070 中重命名**：这曾是 `5dive a2a rounds`。顶层的 `a2a` 语句不再存在于核心（`unknown command: a2a`）——这个名字现在属于 a2a 插件（`5dive plugin add 5dive-ai/5dive-a2a`）。账本阅读器本身保持在核心下 `agent`。

### 跟踪共享工作：任务队列 + 组织结构图

主机有一个共享的任务队列和组织结构图，在可组写的 sqlite 存储中，所以**不需要 sudo**——任何 `agent-*` 用户都可以直接读取和写入。

```bash
# 提交一个工作单元。任务会获得 DIVE-N 标识；--from 默认为你的代理名称，所以创建者会被归因于你。
5dive task add "审计 OWASP A01 的认证中间件" \
  --assignee=worker-1 --priority=high --json
# --assignee 还接受组织路由令牌（role:<r> / charter:<kw>）；省略它会路由到组织领导/协调员。

# 有什么开放的，谁在做什么（按优先级排序）；--mine 过滤到你自己。
5dive task ls --json
5dive task ls --mine --json

# 随着工作移动，驱动状态。block/unblock 表达依赖关系。
5dive task start DIVE-7 --json          # -> in_progress
5dive task done  DIVE-7 --result="首先是一行总结；详细内容在下面" --json
5dive task block DIVE-9 --by=DIVE-7 --json   # DIVE-9 等待 DIVE-7

# 在携带验证器的行上，创建者交付而不是关闭；验证器通过（`verify`）或弹回（`reject`）。
5dive task deliver DIVE-7 --pr=<url> --result="..." --json
# 结果必须命名其证据（DIVE-4576）—— 改变 / 检查（每个命令及其通过/失败计数） / 交付-SHA / CI / 标准 — 所以评分者重新运行你命名的内容而不是重新推导。`task show` 打印模板；`--force-unevidenced="<why>"` 是审计的退出。
5dive task deliver DIVE-7 --pr=<url> --verify="bash tests/x_unit.sh" --json
# ^ 在交付时使用命令评分此行：没有安排评分会话。
# 自 0.32.0 (DIVE-4144)起：--feedback 在拒绝时是必需的，必须命名一个修复，而不仅仅是发现。--no-fix="<why>" 是审计的退出。
5dive task reject  DIVE-7 --feedback="发现：x / 修复：做 y / 验证：运行 z" --json

# 行是否评分完全取决于主机的设置，行会双向覆盖它（自 0.32.0，DIVE-4251）：
5dive config                                      # 此主机的设置
5dive config verify=always|delivered-only|never   # root；每个主机，不是每个座位
5dive task add "..." --verify      # 在 `never` 主机上要求评分（也会清除自动跳过；`--verify=<cmd>` 与 `=` 一起是不相关的接受命令）
5dive task add "..." --no-verify   # 在 `always` 主机上跳过一个

# 每个 `ls` 都带有 `gate` 列：HUMAN:<type> 一个人需要回答，<seat>:<type> 一个代理做，`answered:<retire>`，`-` 什么也没有。
5dive task ls --gated --json          # 只有持有活门的路由
5dive task ls --gated=human --json    # 正确的 `task inbox` 集合

# 什么也没动，你不知道为什么：每个开放的行都不会派发，并且清除每个行的动词（DIVE-3784）。
5dive task doctor --json

# 一目了然地了解谁向谁报告：
5dive org tree --json
```

**一个验证器关闭评分行必须在它的 `--result` 中放入 `graded-sha: <sha>`**，命名它实际读取的提交。没有它，合并门会保持在 `no-graded-sha-stated`；一个 sha 不是 PR 头会保持在 `graded-sha-is-not-the-head`（DIVE-2656）。`--no-graded-sha` 是审计的退出，而不是正常路径。

**一个小交付不会安排评分者（DIVE-4559）。** 在运行 `5dive config verify-small=<lines>` 的主机上，在爆炸半径内（调度器、任务存储、凭证、部署、共享库、sudo 策略、systemd、模式、提供）没有触及的 PR 在该行下关闭，并说明。行上的 `--verify` 胜过它；`--no-verify` 从不战胜相反的，交付时的升级。

**验证器自己的读取是有限的**：`5dive task grade-context <id>` 物化私有的分离评分工作树并打印评分包——从那里评分，而不是从共享签出。

在 `done`/`cancel` 时，`--result` 的**第一行**会发送到所有者的手机——在第一行换行符之前带头简短的总结，详细内容在第一行换行符之后。

### 在你提交行时选择审查者：`--review=` (DIVE-4324)

一个评分行会花费一个评分会话，所以**在提交时选择审查者**而不是让默认为你选择一个：

| `--review=` | 谁评分它 | 成本 |
|---|---|---|
| `none` | 没有人——`task done` 直接关闭它 | 无会话 |
| `check` | 一个命令做（需要 `--verify="<cmd>"` **和** `--mutant="<cmd>"`） | 无会话 |
| `rubric` | 一个固定的六个问题的通过覆盖有界的声明包 | 无会话 |
| `temp` | 每次交付一个新鲜池会话，然后消失 | 一个会话 |
| `<seat>` | 一个固定的站立审查者，在自己的会话中 | 一个会话 |

```bash
5dive task add "在三个清单中提高固定版本" --review=none
5dive task add "添加重试臂" --review=check \
  --verify="bash tests/retry_unit.sh" --mutant="git apply -R fix.patch"
5dive task add "重新工作声明路径" --review=temp
5dive task add "新的定价板块" --review=quinn --customer
```

**`--review=check`需要一个负向控制（DIVE-4623）。** `--mutant=<cmd>`是破坏交付树（`git apply -R <fix>.patch`，`sed -i s/<new guard>/xx/ src/foo.sh`）的命令。在交付时，两条分支都从干净的检出开始，到达交付的sha：检查必须在交付时通过，在突变后失败。一个检查在突变后存活会使得每个树都变成绿色，因此交付会被拒绝，并以该检查作为发现结果——而无需预定评分会话。`--no-mutant="<reason>"`是针对那些确实无法逆转的检查（环境探测、可访问性测试）的审计性逃生通道。`rubric`在行包含标志、爆炸半径路径或`--verify`时立即升级为`temp`。

不传递任何内容，行仍然会获得一个模式——在`created DIVE-N`行打印出来，并通过`task ls` / `task show`显示：`none`对于低优先级行、无体的任务标题、标记为`mechanical`/`copy`/`doc`的体，或是一个只包含一个回读命令的体；当你给出`--verify=<cmd>`时为`check`；当你传递`--customer`时为固定的座位；否则为`temp`。盒子设置仍然会限制它，并且它会获胜：`5dive config verify=never`强制`temp`和固定的`<seat>`为`none`——两者都会预定会话——并在创建行上说明这一点，而不是在沉默中降级你。`check`是豁免的（一个命令不花费任何内容），裸`--verify`是唯一一种在这种盒子上购买单个行的方法。参见`5dive-cli-extras`了解轨道本身、项目、重复工作和循环。

### 在人类身上停放一个问题：`task need`

当任务被只有人类才能提供的东西阻塞时，不要坐等，也不要猜测——设置它：

```bash
5dive task need DIVE-12 --type=decision \
  --ask="在标志后发货还是直接到生产环境？" \
  --options="flag|prod" --recommend="flag" --tier=1 --json
# --type: decision | secret | approval | manual | access
# -> 任务会阻塞；人类会收到带有tap按钮的警报。

5dive task inbox --json        # 舰队中所有未回答的HUMAN门
5dive task gates --json        # 纯粹的`inbox`别名（DIVE-4310）——相同功能
5dive task queue --json        # 发送到你的门，但不唤醒你的门
5dive task answer DIVE-12 --value="flag" --json   # 记录 + 解锁 + 提醒所有者
```

**自0.32.0起，`--ask`被强制执行，而不是建议（DIVE-4176）。** 当门到达配对的人类时，如果它的`--ask`超过**25个字**，或者命名了一个标识符、sha、分支、路径、标志或检查名——这些文本是他唯一看到的，而他从未阅读过我们的代码。将其写为结果之间的选择（“一个清理任务需要它没有的读取权限：永久授权它，或者让我自己运行一次性检查？”），并将每个机制放在任务体中。
`--ask-ok="<why>"`仍然会记录；它会在门上记录并稍后计数，所以当问确实无法用普通英语写时使用它，而不是通过检查。始终传递`--recommend`用于决策/批准——警报以你的推荐开头，以便人类可以一键确认。

在25个字的拒绝下是一个**~15个字的渲染预算**：一个超过这个长度的问句会被警告（“将被截断”）因为门消息在手机上会被截断。警告会被记录；拒绝不会。瞄准15。

**`--options`仅用于决策。** 在任何其他`--type`上的`--options`会被直接拒绝（`--options only applies to --type=decision`），并且决策上的`--recommend`需要`--options`来匹配。自0.36.0（DIVE-4462）起，一组全为**单个字符**的选项也会被拒绝——选项是人们点击的按钮，一个读取“A”的按钮命名的结果。将每个都写为普通结果。

**风险等级（`--tier=0|1|2`）：** `0`立即自动清除（需要`--recommend`，无ping）；`1`会ping，但如果48小时内未回答，会自动应用推荐；`2`永远不会自动应用。金钱、公共通讯、机密、破坏性和品牌问会被固定在等级2，无论标志如何。

**谁可以清除它由类型决定，而不是难度——在提交前检查，而不是在`task answer`拒绝你后（DIVE-3228）：**

| 类型 | 默认等级 | 默认情况下由谁清除 |
|---|---|---|
| `decision` | 1 | 任何代理 |
| `approval` | **1** — 不是2 | 路由的领导 |
| `access` | 2 | 路由的领导（领导可清除*在默认情况下） |
| `manual` | 2 | 人类唯一——只有人类才能执行的步骤 |
| `secret` | 2 | 人类唯一，**在所有等级**上；永远不会路由 |

自己固定`--tier=2`，或者触发类别地板，会使`approval`和`access`也仅限于人类。对于任何类型，`--needs=spend_authority|human_tap|secret_provision`由声明决定且仅限于人类，并且优先于等级。因此**永远不要在批准上传递`--tier=1`以使其远离人类**——这已经是默认的，标志是无效的。

**自0.34.0起，等级<2的`decision`门会根据类型路由到组织领导（DIVE-4415）**——它完全不会到达配对的人类，并且它不会读取`gate_builder_routing`偏好。该偏好仅适用于未绑定的等级<2的`approval`或`manual`门。使用`5dive task routing`查看实时答案，而不是从记忆中查看。

**一个到达配对人类的门必须命名它消耗的能力（DIVE-4346），否则在提交时会被拒绝。** 人类被精确地四次调用——金钱、机密、不可逆转的事情，或者只有在浏览器或键盘上的人类才能做的事情——所以声明一个：
`--needs=spend_authority|secret_provision|human_tap`。“这很困难”不是其中的四个；如果你无法命名能力，那么这是一个你感到不舒服的决定，而不是一个人类门。

将一个由领导持有的门升级到配对的人类是`5dive task gate-escalate`，并且只有门的提交者、他们的领导、路由的审查者、组织协调员或在真实登录会话中的一个人可以这样做（DIVE-4365）。**不要以`--tier=2`重新提交门以到达一个人**——这会丢失门的历史，并且是轨道存在的原因。

路由的门会排队等待审查者的下一个自然唤醒，而不是唤醒他们的会话；`--urgent`在文件时ping。它不是`--recommend`——“我认为答案是X”和“这不能等待”是不同的主张。参见`5dive-cli-extras`了解`task park`/`escalate`/`clear-recs`/`need --withdraw`，`--type=access` + `--probe`自我检查，以及先例预填。

### 在重新推导之前搜索团队记忆

```bash
5dive memory search "hetzner capacity gotchas" --json
```

只读，无sudo，BM25排名的片段，带有文件+标题来源。在重新推导过去的决定或调试队友已经遇到的问题之前使用它。

在一个大存储上，优先使用**两阶段召回**（DIVE-3821）——它比片段每标记提供更多的候选者：

```bash
5dive memory search "hetzner capacity" --index   # 阶段1：slug + 一行 + 分数，无体
5dive memory get <slug> [<slug>...]              # 阶段2：完整体，只有你选择的部分
```

阶段1结果为空是缺席的证据；索引短不是。使用事实会使用的词语搜索，而不是任务使用的词语。对于写入路径（`memory add`，编译到共享维基），`memory router`，`memory check`和卫生，参见`5dive-cli-extras`。

### 检查你自己的身份，或者以正确的身份运行`gh`

```bash
5dive whoami --json     # 行动者、权限（root|sudo:<who>|self）和等级——以及每个的来源
```

当门拒绝或权限错误不符合逻辑时使用它——它命名了CLI实际上将你视为哪个uid/代理/等级，而不是你假设的。如果行动者无法测量，它退出6（`auth_required`）而不是打印`unknown`，所以它也用作可脚本化的可测量性检查。

当任务涉及作为代理打开/评论PR或问题时，优先使用`5dive gh <gh args...>`而不是直接调用`gh`二进制文件：写入（`pr create`，`pr merge`，`issue comment`，…）路由到`5dive-bot`机器账户，以便GitHub行动者字段实际上可以区分代理操作和人类操作（DIVE-2448）；读取和管理类调用保留在你的凭证中自动。`5dive gh --explain <args>`在不运行任何内容的情况下预览路由决策。

## 交战规则

1. **始终传递`--json`。** 解析信封。不要grep stderr。
2. **一个名称=一个代理。** 名称是小写字母/数字/连字符，以字母开头，最大16个字符。只有在`agent rm`后才能重用名称。
3. **不要共享机器人令牌。** 两个在同一机器人上的Telegram频道代理会竞争`getUpdates`。每个代理都需要自己的令牌。
4. **销毁你创建的东西。** 一个泄漏的`worker-N`代理会在重启后保持运行——它是一个真实的systemd单元，而不是一个线程。在任务完成后调用`5dive agent rm <name>`。
5. **不要直接将命令行传递给底层CLI二进制文件。** 绕过`5dive`会跳过systemd单元、审计日志和环境注入——代理将以损坏的身份验证运行，并且没有重启循环。
6. **如果标志被拒绝为未知，请阅读`5dive --help`** ——主机上的二进制文件可能比这个技能新或旧。帮助输出是权威的。
7. **被人类阻塞？设置它。** 使用带有推荐的`task need`而不是猜测或让任务无声地腐烂。
8. **当委托聊天请求时，不要中继——通过`agent send --reply-to-chat=<id> --reply-to-msg=<id>`传递上下文**

## 参考

- `references/commands.md` — 每个子命令和标志，可复制/粘贴。
  包括上面没有概述的较少使用的顶级动词：`5dive deploy`（委托生产部署，INST-5），`5dive bug`（诊断问题提交），`constitution`（机器强制护栏的前门），`5dive acp`（在stdio上与ACP交谈，以便像Buzz/Zed这样的客户端可以选择5dive作为编码代理运行时——由客户端启动，不是直接运行，DIVE-3017），`liveness`（一个座位对它所写的工件是否存活，DIVE-3778），`plugin`（安装/启用/回滚插件+市场），`human`（可以清除门的那些人，DIVE-3342），`run`（一个代理对一项任务的一次尝试——`trace`下的单元），`trigger`（已签署的外部事件成为普通任务）和`host`（在CLI-root授权下进行硬化单元/日志/计划 remediation）。
- **Web UI已离开核心，现在是一个插件。** `5dive plugin add 5dive-ai/5dive-ui`安装它，然后`5dive ui`就可以像以前一样工作。留在核心的是视图渲染的读取合同：
  `5dive board [--json]`发出此主机组织的队列/门/流程/触发的一个版本化的JSON文档，因此消费者永远不会打开核心的私有sqlite存储（DIVE-4779）。`5dive board --contract-version`根本不读取存储，这就是你如何与还不存在的盒子的板进行协商的方式。
- `references/exit-codes.md` — 退出代码和错误类。
- `references/paths.md` — 磁盘状态布局（仅用于调试）。
- `5dive-cli-extras`技能 — 船员托管、帐户、身份验证恢复、compose/团队模板、目标DAG、目标、循环、内存写入/维基、组织图表写入、治理投票、摘要/使用/监督/舰队/诊断、telegram配对细节、角色市场、自带提供者，以及公司向导。

## 进一步深入

完整的参考手册位于<https://5dive.com/docs>。如果此技能中的标志与正在运行的二进制文件接受的冲突，请相信二进制文件——运行`sudo 5dive --help`或`sudo 5dive agent <sub> --help`直接跟随它。

_与5dive CLI同步到**0.59.0**（提交`a134f8ce`，2026-09-28）。一个给定盒子的二进制文件可能落后于主（夜间更新通道）多达一天——如果它们不同，请相信`5dive --help`。_
