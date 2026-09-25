# 使用 Mo 进行测试

Mo 在托管沙箱中运行浏览器测试。其文件和进程均位于远程。

## Mo 运行时的工作

在初始测试通过及其复现过程中，保持被测版本的稳定性。在 Mo 使用期间，不要更改目标服务的内容或热重载、重启应用、部署到其 URL 或修改共享测试数据。其他工作，如代码审查，是允许的。对于长时间运行期间的独立 Bug 修复，请遵循 [修复循环](references/remediation-loop.md)。

通过 `qa status "$session_id" --full` 获取测试结果。一个 `kind: "bug"` 的条目表示 Bug 已被独立复现。一个 `kind: "flag"` 的条目是静态的单帧错误，例如拼写错误，且未进行复现。测试用例的判定结果为 `verified`、`issues_found` 或 `blocked`。当您向用户报告发现时，请包含其名称、证据、状态和 `web_url`。

如果 Mo 被阻止，在您能访问时从简报、存储库或授权环境数据中回答。否则，请向用户索要缺失的访问权限、权限或决策，然后将答案发送给根 Mo。根 Mo 将上下文转发给其内部子代理。切勿编造或泄露秘密。

## 准备简报

运行 `qa version`。如果 Mo 缺失或过时，请阅读 [安装](references/installation.md)。在出现身份验证错误后，请阅读 [身份验证](references/authentication.md)。

使用请求中的目标。对于本地或私有目标，请阅读 [隧道](references/tunneling.md)。

简报是 Mo 的规范。包括：

1. 精确的目标 URL，包括受影响路径和查询。
2. 预期行为和通过标准。
3. 登录方法、测试账户标签和允许的测试数据。
4. 禁止的操作和 Mo 不得更改的数据。
5. 范围内的产品区域和用户流程，以及明确的排除项。
6. 任何非默认的浏览器设置。需要时请阅读 [浏览器设置](references/browser-settings.md)。

从请求和存储库中补充信息。仅在缺少范围、访问权限或权限会改变运行时，才询问。

### 设置范围和细节

简报设置范围。`--granularity` 在该范围内设置细节：

- `low` 用于早期冒烟测试：主要成功路径和重要失败状态。
- `medium` 当变更的流程正常工作时：每个有意义的交互和重要失败状态。
- `high` 用于发布就绪的覆盖范围：所有范围内的路径、替代路径、失败状态和可操作的控件。

需要显式传递设置，因为默认值为 `high`。对于仅测试成功路径的冒烟测试，告诉 Mo 跳过失败状态。Mo 没有会话范围的计时或测试计数选项。对于硬性时间或花费上限，请缩小简报，监控墙时间或 `qa cost <session-id>`，在达到上限时运行 `qa stop <session-id> --subagents`，并报告未完成的覆盖范围。

## 启动会话

将简报作为单个参数传递：

```bash
brief=$(cat <<'EOF'
目标: https://preview.example.com/checkout?variant=express
目标: 返回支付后保持所选的运货方式。
登录: 使用暂存 QA 买家账户。
测试数据: 仅创建测试购物车和订单。
禁止: 提交支付、发送电子邮件、删除数据或更改共享目录。
覆盖范围: 冒烟测试 express-checkout 成功路径和标准结账。跳过其他流程和失败状态。
通过标准:
- 运货方式保持选择。
- 总金额不变。
- 标准结账仍然正常。
EOF
)
session_json=$(qa start --granularity low "$brief")
session_id=$(jq -r .sessionId <<<"$session_json")
web_url=$(jq -r .webUrl <<<"$session_json")
created_at=$(jq -r '.createdAt // empty' <<<"$session_json")
```

启动会话会返回 Mo 完成之前的状态。保留这些值：每个后续命令都需要 `session_id`，用户可以通过 `web_url` 观看或加入，`created_at` 记录会话开始时间。`createdAt` 在服务器运行较早的 API 版本时可能不存在。

一个 Momentic 环境将 `BASE_URL` 与可重用的非秘密变量组合在名称为 `staging` 的名称下。`--environment NAME` 选择在 Momentic 仪表板 **环境** 下创建的一个，而不是来自 shell 或 `momentic.config.yaml` 的环境。Mo 在启动时将其变量复制到会话中。

使用可重复的 `--env-file` 或 `--env-var NAME` 选项用于本地值和秘密；它们会覆盖匹配的环境变量。`--env-var` 会转发已在 `qa start` 进程环境中的变量；它不接受 `NAME=value`。切勿将秘密值放在命令或简报中。使用 `--tunnel` 用于私有访问。仅在目标或测试账户限制并行用户时设置 `--max-concurrency`。它在会话启动时是固定的。如果目标过载，请运行 `qa stop --subagents` 并启动一个新的会话，使用较低的值。

## 跟踪会话

在后台运行此监视器。它每次打印一条新发现或状态变更的行，并在 Mo 需要输入或会话结束时退出：

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

- **后台命令。** 使用主机工具（如 Claude Code 的 `Monitor`）在每行输出时通知您，并在过期时重新启动它。如果没有，请将其作为后台会话启动，并在其他任务之间检查其输出。
- **运行器子代理。** 给子代理传递 `session_id`、监视器和此技能。它在每次事件时向您发送消息并继续监视。仅在运行中的子代理可以向您发送消息时使用此方法，例如启用 `multi_agent_v2` 的 Codex（`send_message` 到 `/root`，然后在父级中 `wait_agent`）。Claude Code 和默认 Codex 子代理仅在完成时报告。

在 Codex 没有运行器子代理的情况下，将监视器保持在长时间运行的 `exec_command` 前台，保留其返回的会话 ID，并使用 `write_stdin` 排空它。不要追加 `&`，分离它，或在它运行时结束回合。Shell 变量不会跨独立命令持久化，因此请插入字面 Mo 会话 ID 或在设置它的同一 shell 中启动监视器。

无论哪种方式，您都回答阻塞项并将用户的决策发送给 Mo。

`status.displayState` 描述了整个会话以供显示和轮询。`status.state` 是其遗留别名：

| 状态               | 含义                                                    |
| ------------------- | ---------------------------------------------------------- |
| `running`           | 根 Mo 正在工作。                                        |
| `waiting_on_agents` | 根 Mo 空闲；其内部子代理正在工作。                      |
| `needs_you`         | Mo 提出了一个问题。用 `qa send` 回答它。                 |
| `ready`             | 没有代理在运行，结果可用。                               |
| `sleeping`          | 没有代理在运行，没有报告或最终回复。                    |
| `cancelled`         | 工作被停止。                                          |
| `failed_start`      | 会话从未开始。启动一个新的会话。                        |

`status.sessionState` 是 `read`、`status` 和 `report` 共享的生命周期状态：`starting`、`working`、`waitingOnUser`、`waitingOnAgents`、`idle` 或 `stopped`。`createdAt` 是会话创建时间，`lastActivityAt` 是最后持久化更新时间。`latestTurn` 包含最新的持久化助手计时元数据：`startedAt`、`completedAt` 和 `durationMs`。部分计时使用 `null`。运行较早 API 的服务器可能会省略这些新字段。

使用此有界读取来获取 Mo 的提问和回复，而不是发现：

```bash
qa read "$session_id" --from start --timeout 45s --json
```

它省略了 Mo 在运行回合期间发送的消息，直到该回合结束。`--from latest` 也错过了在读取开始前完成的回合。在 `read` 响应中，请优先使用 `sessionState`；当服务器省略它时，使用其遗留别名 `state`。`timedOut: true` 表示 Mo 仍在工作。

使用 `--json`，`read` 将一个 JSON 响应写入 stdout，不打印任何进度文本。不使用 `--json`，等待时间超过两秒的读取会在 stderr 打印活动状态。返回的消息保留在 stdout，而超时或停止状态文本保留在 stderr。

`qa wait "$session_id" --json` 在根 Mo 的回合结束、停止或需要输入时返回。退出代码 `2` 表示 Mo 需要输入；`4` 表示它被停止。内部子代理可能仍在运行，因此在使用会话之前，请确认 `status.displayState` 是 `ready` 或 `sleeping`。

切勿发送消息以请求进度。使用 `status`、`read` 或 `wait`。仅用于回答阻塞项或故意引导或重新检查工作。优先在 Mo 空闲或等待时发送：

```bash
qa send --session-id "$session_id" --wait 45s "使用暂存账户。"
```

在活动时发送会停止根 Mo 的当前回合和正在进行的工具调用。仅在新的方向应优先时才这样做。不使用 `--wait`，请用 `read` 确认回复。

## 结束或修复

在展示最终结果之前，请阅读 [报告](references/reports.md)。确认简报仍然描述了产品的预期行为。

如果用户要求修复，请阅读 [修复循环](references/remediation-loop.md)。否则，不要更改应用代码。

选择如何停止：

- `qa stop <session-id>` 仅中断根 Mo。子代理继续测试、提交发现并计费。根 Mo 停止，直到您的下一个 `qa send`。使用它来重新引导 Mo 而不丢失正在进行的测试。
- `qa stop <session-id> --subagents` 也停止每个正在运行的子代理。使用它来结束支出。`qa send` 仍可恢复会话。
- `qa archive <session-id>` 取消所有工作，隐藏会话，并拒绝进一步的 `qa send`。解档仅限网络操作。

`qa upload` 返回沙箱路径。将此路径发送给 Mo，因为本地路径不存在于其沙箱中。在 `qa download` 之前创建目标目录，当 `--output` 指定目录时。运行 `qa <command> --help` 获取语法。
