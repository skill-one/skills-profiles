---
name: mo-qa
description: 使用 Momentic 的 `qa` 命令行界面 (CLI) 运行和控制 Mo QA 会话。可用于 Bug Bash、状态检查、报告导出、回复 Mo、文件传输或根据 Mo 查找结果进行修复。
---

# 使用 Mo 进行测试

Mo 在托管沙盒中运行浏览器测试。其文件和进程都是远程的。

## 在 Mo 运行时工作

通过初始测试和其重现保持测试的修订版本稳定。在 Mo 使用期间，不要更改目标提供的内容、热重载、重启应用程序、部署到其 URL 或变异共享测试数据。其他工作，如代码审查，是可以的。对于长时间运行期间的独立错误修复，请遵循 [修复循环](references/remediation-loop.md)。

通过 `qa status "$session_id" --full` 获取发现结果。一个 `kind: "bug"` 条目已被独立重现。一个 `kind: "flag"` 条目是一个静态的、单帧错误，例如拼写错误，而无需重现。测试用例的判定结果是 `verified`、`issues_found` 或 `blocked`。当您向用户报告发现结果时，请包括其名称、证据、状态和 `web_url`。

如果 Mo 被阻止，当您可以时，从简要信息、存储库或授权环境数据中回答。否则，请向用户索要缺失的访问权限、权限或决策，然后将答案发送给根 Mo。根 Mo 将上下文转发给其内部子代理。永远不要编造或泄露秘密。

## 准备简要信息

运行 `qa version`。如果 Mo 缺失或已过时，请阅读 [安装](references/installation.md)。在出现身份验证错误后，请阅读 [身份验证](references/authentication.md)。

使用请求中的目标。对于本地或私有目标，请阅读 [隧道](references/tunneling.md)。

简要信息是 Mo 的规范。包括：

1. 精确的目标 URL，包括受影响的路径和查询。
2. 预期行为和通过标准。
3. 登录方法、测试帐户标签和允许的测试数据。
4. 禁止的操作和 Mo 不得更改的数据。
5. 范围内的产品区域和用户流程，以及明确的排除项。
6. 任何非默认的浏览器设置。需要时请阅读 [浏览器设置](references/browser-settings.md)。

从请求和存储库中填写空白。仅在缺少范围、访问权限或权限会改变运行时才询问。

### 设置范围和详细程度

简要信息设置范围。`--granularity` 在该范围内设置详细程度：

- `low` 用于早期的烟雾测试：主要快乐路径和重要错误状态。
- `medium` 当变更的流程正常工作时：每个有意义的交互和重要错误状态。
- `high` 用于发布就绪的覆盖率：每个范围内的路径、替代路径、错误状态和可操作的控件。

明确传递该设置，因为默认值是 `high`。轻量级的错误轰炸意味着狭窄的范围和低详细程度，并使用 Mo 的正常子代理架构。根据任务的复杂性和网站的容量，允许大约 5-25 个并发代理；不要串行化烟雾测试或告诉 Mo 不要委托，即使请求说“轻”。仅当针对具体目标、帐户或用户约束时，才将并发性降低到此范围以下。

对于仅测试快乐路径的烟雾测试，告诉 Mo 跳过错误状态。Mo 没有会话范围的计时或测试计数选项。如果用户指定了硬时间或支出上限，请缩小简要信息，监控墙时间或 `qa cost <session-id>`，在上限时运行 `qa stop <session-id> --subagents`，并报告未完成的覆盖率。不要从“轻”中推断硬截止日期，或在仅为了保持运行时间短而仅验证核心断言之前停止。

## 启动会话

将简要信息作为 `qa` 之后的单个参数传递（选项标志跟在简要信息之后）：

```bash
brief=$(cat <<'EOF'
目标：https://preview.example.com/checkout?variant=express
目标：返回支付后保持选择的运输方式。
登录：使用暂存 QA 买家帐户。
测试数据：仅创建测试购物车和订单。
不要：提交支付、发送电子邮件、删除数据或更改共享目录。
覆盖率：烟雾测试 express-checkout 快乐路径和标准结账。跳过其他流程和错误状态。
通过标准：
- 运输方式保持选择。
- 总额不变。
- 标准结账仍然正常工作。
EOF
)
session_json=$(qa start "$brief" --granularity low)
session_id=$(jq -r .sessionId <<<"$session_json")
web_url=$(jq -r .webUrl <<<"$session_json")
created_at=$(jq -r '.createdAt // empty' <<<"$session_json")
```

启动返回之前 Mo 完成工作。保留这些值：每个后续命令都需要 `session_id`，用户可以通过 `web_url` 观看或加入，`created_at` 记录会话开始的时间。`createdAt` 在服务器运行较早的 API 版本时可能不存在。

一个 Momentic 环境将 `BASE_URL` 与可重用的非秘密变量按名称（例如 `staging`）分组。`--environment NAME` 选择在 Momentic 仪表板中的 **环境** 下创建的一个，而不是来自 shell 或 `momentic.config.yaml` 的一个。Mo 在启动时将其变量复制到会话中。

使用可重复的 `--env-file` 或 `--env-var NAME` 选项用于本地值和秘密；它们覆盖匹配的环境变量。`--env-var` 传递已在 `qa start` 进程环境中的变量；它不接受 `NAME=value`。永远不要在命令或简要信息中放入秘密值。使用 `--tunnel` 进行私有访问。保留正常并发性可用，或在上述任务和网站范围内设置 `--max-concurrency`。限制在会话开始时固定。如果目标过载，请运行 `qa stop --subagents` 并以较低值启动新的会话。`--granularity <low|medium|high>` 设置 explore-agent 测试发现的具体程度。`--interaction-speed <default|human>` 在目标需要时减慢浏览器交互速度至人类速度。

## 跟踪会话

在后台运行此监视器。它每次新的发现或状态变化打印一行，并在 Mo 需要输入或会话结束时退出：

```bash
seen=""
while :; do
  snapshot=$(qa status "$session_id" --full) ||
    { echo "status request failed"; sleep 30; continue; }
  events=$(jq -r '"displayState \(.displayState // .state)",
    (.findings.bugs[] | "\(.kind) \(.name)"),
    (.findings.verdicts[] | "verdict \(.status) \(.testCaseName // "-")")' \
    <<<"$snapshot" | sort)
  comm -13 <(printf '%s\n' "$seen") <(printf '%s\n' "$events")
  seen=$events
  case $(jq -r '.displayState // .state' <<<"$snapshot") in
    needs_you | ready | sleeping | cancelled | failed_start) break ;;
  esac
  sleep 30
done
```

以两种方式运行监视器：

- **后台命令**。使用主机工具（例如 Claude Code 的 `Monitor`）自行运行它，并在它到期时重新启动。如果没有，请将其作为后台会话启动，并在其他任务之间检查其输出。
- **运行器子代理**。将 `session_id`、监视器和此技能提供给子代理。它在每次事件时向您发送消息并继续监视。仅在运行中的子代理可以向您发送消息时使用此方法，例如启用 `multi_agent_v2` 的 Codex（`send_message` 到 `/root`，然后在父级中 `wait_agent`）。Claude Code 和默认 Codex 子代理仅在完成时报告。

在 Codex 没有运行器子代理的情况下，将监视器保持在长时间运行的 `exec_command` 的前台，保留其返回的会话 ID，并使用 `write_stdin` 排空它。在它运行时不要追加 `&`、分离它或结束回合。Shell 变量不会跨不同的命令持久化，因此请插值 Mo 会话 ID 或在同一个设置它的 shell 中启动监视器。

无论哪种方式，您都回答阻塞项并将用户的决定发送给 Mo。

`displayState` 是 UI 显示的会话状态。`status`、`read` 和 `report` 都报告相同的状态：

| 状态               | 含义                                                    |
| ------------------- | ---------------------------------------------------------- |
| `running`           | 根 Mo 正在工作。                                        |
| `waiting_on_agents` | 根 Mo 空闲；其内部子代理正在工作。                      |
| `needs_you`         | Mo 提出了一个问题。用 `qa send` 回答它。                 |
| `ready`             | 没有代理正在运行，结果可用。                           |
| `sleeping`          | 没有代理正在运行，没有报告或最终回复。                 |
| `cancelled`         | 工作已停止。                                          |
| `failed_start`      | 会话从未开始。启动一个新的。                          |

`sessionState` 是生命周期状态（`starting`、`working`、`waitingOnUser`、`waitingOnAgents`、`idle` 或 `stopped`），在所有三个命令中都相同。`state` 是遗留字段，是 `sessionState` 在任何出现处的别名。`createdAt` 是会话创建时间，`lastActivityAt` 是最后持久更新的时间。`latestTurn` 包含最新的持久化助手计时元数据：`startedAt`、`completedAt` 和 `durationMs`。部分计时使用 `null`。运行较早 API 的服务器可以在 `read` 和 `report` 中省略 `displayState`；使用 `qa status` 获取显示词。

使用此有界读取来获取 Mo 的提问和回复，而不是发现结果：

```bash
qa read "$session_id" --from start --timeout 45s --json
```

它省略了 Mo 在运行回合期间发送的消息，直到该回合结束。`--from latest` 也错过了在读取开始之前完成的回合。在 `read` 响应中，`displayState` 与 `status` 词匹配，而 `state` 和 `sessionState` 携带生命周期状态。运行较早 API 的服务器省略 `displayState`；在这些服务器上使用 `qa status` 获取显示词。`timedOut: true` 表示 Mo 仍在工作。

使用 `--json`，`read` 将一个 JSON 响应写入 stdout 并不打印任何进度文本。不使用 `--json`，如果读取等待时间超过两秒，则向 stderr 打印活动状态。返回的消息保留在 stdout 上，而超时或停止状态文本保留在 stderr 上。

`qa wait "$session_id" --json` 在根 Mo 的回合完成、停止或需要输入时返回。退出代码 `2` 表示 Mo 需要输入；`4` 表示它被停止了。内部子代理可能仍在运行，因此在将会话视为完成之前，请确认 `qa status` 报告 `ready` 或 `sleeping`。

永远不要发送消息来请求进度。使用 `status`、`read` 或 `wait`。仅当回答阻塞项或故意引导或重新检查工作时要发送。最好在 Mo 空闲或等待时发送：

```bash
qa send --session-id "$session_id" --wait 45s "使用暂存帐户。"
```

在活动状态下发送会停止根 Mo 的当前回合和正在进行的工具调用。仅在新的方向应优先时才这样做。不使用 `--wait`，请用 `read` 确认回复。

## 完成或修复

在展示最终结果之前，请阅读 [报告](references/reports.md)。确认简要信息仍然描述了产品的预期行为。

如果用户要求修复，请阅读 [修复循环](references/remediation-loop.md)。否则，不要更改应用程序代码。

选择如何停止：

- `qa stop <session-id>` 仅中断根 Mo。子代理继续测试、提交发现结果并计费。根 Mo 保持停止状态，直到您的下一个 `qa send`。使用它来重新引导 Mo 而不丢失正在进行的测试。
- `qa stop <session-id> --subagents` 也停止每个正在运行的子代理。使用它来结束支出。`qa send` 仍然可以恢复会话。
- `qa archive <session-id>` 取消所有工作，隐藏会话，并拒绝进一步的 `qa send`。仅限网络解档。

`qa upload` 返回沙盒路径。将此路径发送给 Mo，因为本地路径在其沙盒中不存在。在 `qa download` 之前创建目标目录，当 `--output` 指定目录时。运行 `qa <command> --help` 获取语法。
