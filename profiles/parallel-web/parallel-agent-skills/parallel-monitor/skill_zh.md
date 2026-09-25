# 网页监控

操作：$ARGUMENTS

> GA 监控命令需要 `parallel-cli` ≥ 0.4.0。如果缺少监控命令或选项，请提示用户通过其安装方式更新（参见 <https://docs.parallel.ai/integrations/cli>），然后重试。

## 此技能的功能

监控是长时间运行的、服务器端的任务，它们按一定频率重新检查网页，并在发生变化时发出事件。与搜索/研究/查找（一次性查询）不同，监控会持续运行直到被取消，并且可以选择通过 webhook 传递检测到的事件。

## 确定操作

解析用户的请求并选择一个操作：

| 意图 | 操作 |
|---|---|
| "跟踪 / 观察 / 监控 / 当 X 发生时提醒我" | **创建** |
| "我在监控什么？" / "列出监控" | **列出** |
| "有什么变化？" / "显示监控 X 的事件" | **事件** |
| "显示监控 X" / "获取 X 的详细信息" | **获取** |
| "更改 X 的频率 / webhook" | **更新** |
| "立即检查监控 X" / "立即运行" | **触发** |
| "显示事件组 X 的完整负载" | **事件** 并使用 `--event-group-id` |
| "停止 / 删除监控 X" | **取消**（取消前必须确认） |

## 创建监控

```bash
parallel-cli monitor create "<查询>" --frequency 1d --json
```

频率接受 `<n><单位>`，其中 `h`、`d` 或 `w`（例如 `1h`、`1d` 或 `1w`）。也接受别名 `hourly`、`daily`、`weekly` 和 `every_two_weeks`。根据源实际变化的频率匹配频率——每小时用于价格/新闻，每周用于报告/人员。

可选标志：

- `--webhook https://example.com/hook` — 将检测到的事件传递到 URL
- `--metadata '{"team":"competitive-intel"}'` — 添加 JSON 元数据用于自己的账本
- `--output-schema '<json>'` — 结构化事件负载（高级）

解析 JSON 以提取 `monitor_id`。告诉用户：

- 已创建监控及其 ID
- 频率（以便他们知道监控检查的频率）
- 近期事件在服务器端可用——他们稍后可以运行 `parallel-cli monitor events $MONITOR_ID` 查看发生了什么变化

## 列出监控

```bash
parallel-cli monitor list -n 10 --json
```

默认使用 `-n 10` 以简洁输出。`list` 默认仅返回活动监控；当用户要求包含已取消监控时，添加 `--status active --status cancelled`。仅当需要较大集合时才提高限制。以表格形式呈现：ID、查询或任务运行（截断）、频率、创建时间。

> 注意：`monitor list` 按最新优先排序。如果用户正在验证创建，优先使用 `monitor get $MONITOR_ID`（使用创建返回的 ID）而不是扫描列表。

## 查看监控的事件

```bash
parallel-cli monitor events "$MONITOR_ID" --json
```

事件按最新优先返回。如果响应包含 `next_cursor`，使用 `--cursor` 传递它以检索下一页。

对于特定事件组的更详细信息：

```bash
parallel-cli monitor events "$MONITOR_ID" --event-group-id "$EVENT_GROUP_ID" --json
```

为用户总结：事件数量，然后是一个带日期或时间戳的要点列表，引用事件负载中的源 URL。

## 获取 / 更新 / 触发 / 取消

```bash
parallel-cli monitor get "$MONITOR_ID" --json
parallel-cli monitor update "$MONITOR_ID" --frequency 1w --json
parallel-cli monitor trigger "$MONITOR_ID" --json
parallel-cli monitor cancel "$MONITOR_ID" --json
```

当前 CLI 暂不暴露查询更新；创建新的监控以更改查询。

`trigger` 将实际的非计划运行入队，而不会更改常规计划。它不是合成 webhook 测试，并且只有在运行检测到实质性变化时才会发出事件。

**取消前必须确认**——取消是永久性的。

## 设置

需要 `parallel-cli`（已安装并认证）。如果 `parallel-cli --version` 失败，或者后续命令因认证错误失败，请提示用户查看 <https://docs.parallel.ai/integrations/cli> 并停止。
