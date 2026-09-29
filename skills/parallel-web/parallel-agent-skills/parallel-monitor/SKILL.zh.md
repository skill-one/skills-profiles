---
name: parallel-monitor
description: 持续追踪网络上的变化，并按固定频率进行。当用户要求“监控”、“追踪...的变化”、“关注”或“当...在网络上发生变化时通知我”时使用——例如，“追踪iPhone 16的价格变化”、“当特斯拉提交新的8-K文件时通知我”、“每周监控竞争对手的定价页面”。也用于列出、检查、更新或停止现有的监控任务，包括删除请求。
---

# 网页监控

操作：$ARGUMENTS

> GA 监控命令需要 `parallel-cli` ≥ 0.4.0。如果缺少监控命令或选项，请提示用户通过其安装方式更新（参见 <https://docs.parallel.ai/integrations/cli>），然后重试。

## 此技能的功能

监控是长时间运行的、服务器端的任务，它们按一定频率重新检查网页，并在发生变化时发出事件。与搜索/研究/查找（一次性查询）不同，监控会持续运行直到被取消，并且可以选择通过 webhook 传递检测到的事件。创建监控不会建立持续的代理通知服务：解释如何读取服务器端事件或使用配置的 webhook，而不承诺聊天或邮件提醒。

默认类型是 `event_stream`，频率为 `1d`，服务器处理器为 `lite`。`snapshot` 监控需要现有的任务运行 ID。仅创建或修改用户请求的资源；不要仅为了展示此技能而创建监控。

## 决定操作

解析用户请求并选择一个操作：

| 意图 | 操作 |
|---|---|
| "跟踪/监视/监控/当 X 发生时提醒我" | **创建** |
| "我在监控什么？" / "列出监控" | **列出** |
| "有什么变化？" / "显示监控 X 的事件" | **事件** |
| "显示监控 X" / "获取 X 的详细信息" | **获取** |
| "更改 X 的频率/webhook" | **更新** |
| "立即检查监控 X" / "立即运行" | **触发** |
| "显示事件组 X 的完整负载" | **事件** 并使用 `--event-group-id` |
| "停止/删除监控 X" | **取消**（永久性；验证权限和精确 ID） |

## 创建监控

```bash
parallel-cli monitor create "<query>" --frequency 1d --json
```

频率接受 `<n><单位>`，单位为 `h`、`d` 或 `w`（例如 `1h`、`1d` 或 `1w`），在支持的范围 1 小时到 30 天内。也接受别名 `hourly`、`daily`、`weekly` 和 `every_two_weeks`。根据用户请求的频率和源实际变化频率来匹配频率。

可选标志：

- `--webhook https://example.com/hook` — 将检测到的事件传递到 URL
- `--metadata '{"team":"competitive-intel"}'` — 添加 JSON 元数据用于自己的记录
- `--output-schema '<json>'` — 结构化事件负载（高级）

立即使用查询、频率和请求的设置捕获返回的 `monitor_id`。使用 `get` 和该 ID 验证创建。告诉用户：

- 监控已创建及其 ID
- 频率（让他们知道监控检查的频率）
- 近期事件可在服务器端获取——他们稍后可以运行 `parallel-cli monitor events $MONITOR_ID` 查看发生了什么变化

如果创建或其他突变超时或响应丢失，在重试之前解决现有监控/操作。使用保存的 ID、`get` 和 `events` 继续操作；不要自动重新创建。重新创建可能会重复持久监控和计费。

## 列出监控

```bash
parallel-cli monitor list -n 10 --json
```

默认使用 `-n 10` 以简洁输出。`list` 默认仅返回活动监控；当用户要求包含已取消监控时，添加 `--status active --status cancelled`。仅对较大集合提高限制。以表格形式呈现：ID、查询或任务运行（截断）、频率、创建时间。

> 注意：`monitor list` 按最新优先排序。如果用户正在验证创建，优先使用 `monitor get $MONITOR_ID`（使用创建返回的 ID）而不是扫描列表。

## 查看监控的事件

```bash
parallel-cli monitor events "$MONITOR_ID" --json
```

事件按最新优先返回。如果响应包含 `next_cursor`，使用 `--cursor` 将其传递以获取下一页。

空事件列表并不能证明检查已完成且未发生变化。要检查完成历史以及检测到的事件：

```bash
parallel-cli monitor events "$MONITOR_ID" --include-completions --limit 10 --json
```

区分类型检测事件、无变化 `completion` 事件和 `error` 事件。使用它们的实际时间戳并报告失败。无完成的完成历史不能证明执行。保留 `event_id` 和 `event_group_id`（如果存在）；这些标识事件和执行，而不是监控 ID。

对于特定事件组的更详细信息：

```bash
parallel-cli monitor events "$MONITOR_ID" --event-group-id "$EVENT_GROUP_ID" --json
```

事件组详细信息忽略分页参数。将检测到的变化与完成/错误分开总结，并附上日期或时间戳。读取类型的 `output` 或 `changed_output` 以及可用的 `basis`；为事实性声明引用其源 URL。当负载缺少依据时，不要编造来源。仅当需要获取请求的期间内继续分页时，才显示响应警告。

## 获取/更新/触发/取消

```bash
parallel-cli monitor get "$MONITOR_ID" --json
parallel-cli monitor update "$MONITOR_ID" --frequency 1w --json
parallel-cli monitor update "$MONITOR_ID" --webhook https://example.com/hook --json
parallel-cli monitor trigger "$MONITOR_ID" --json
parallel-cli monitor cancel "$MONITOR_ID" --json
```

仅提供用户请求更新的字段。仅 webhooks 更新会保持频率不变；更新没有默认频率。元数据和高级事件流设置也可以通过 CLI 更新，但查询和任务运行身份是不可变的。需要不同查询时，需要创建新的监控并单独决定旧监控；不要无声地重新创建或取消它。

`trigger` 会排队执行实际计费的离线执行，而不会更改常规计划。它不是合成 webhook 测试，不能替代测试通知传递的请求。成功的触发响应确认排队，而不是完成。只有在发现实质性变化时才会发出检测到的事件；检查完成历史以查看无变化执行。已取消的监控无法触发。

取消是不可逆的，不是删除或临时暂停。解释这一点并获取精确监控 ID 的确认，除非用户已经授权永久取消或清理特定的可丢弃监控。取消后，使用 `get` 验证其状态。永远不要自动重新创建它以继续监控。

在身份验证或 API 错误时，报告实际错误并保留 ID 以便恢复。不要将每个错误都归类为过时的 CLI 或将每个权限错误都归类为信用不足。失败的读取不是监控停止的证据；读取事件不会取消监控。

## 设置

需要已安装并经过身份验证的 `parallel-cli`。检查 `parallel-cli --version` 和 `parallel-cli auth --json`；身份验证可能成功而 `authenticated` 为 `false`。缺失二进制文件、不支持的命令/选项和身份验证失败需要不同的解决方法：安装、通过现有安装方式升级或终端登录。参见 <https://docs.parallel.ai/integrations/cli>。在身份验证失败时停止受影响的请求，不要在聊天中请求秘密，也不要更改账户策略以绕过阻止的设置。
