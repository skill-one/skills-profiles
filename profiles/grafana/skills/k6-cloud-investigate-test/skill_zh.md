# k6 Cloud 测试调查工具

针对 Grafana Cloud k6 测试或运行，提供结构化的 9 步工作流程进行调查。

这项技能是 **仅限工作流程** 的。所有 API 调用都通过 `gcx api` 对插件代理进行，使用 v6 进行 REST 调用，使用 v5 进行指标调用。对于底层机制（gcx 认证、路径约定、端点发现、日志查询、脚本编辑、阈值语义、常见问题），请参阅 `k6-manage` 技能——下面每一步都引用它。

本技能特有的内容包括：

- 有序的调查流程（第 1-9 步）
- 日期对齐检查（“过去 7 天”≠“过去 7 次运行”）
- 3 层级通过/失败判定（`result` vs `status` vs 每个检查的 `checks` 查询）
- 带有真实数字的示例（`references/worked-example.md`）

## 核心原则

1. **先读后写。** 在任何 PUT 之前，始终 GET 脚本。`gcx k6 load-tests update-script` 是一个 *写* 操作，它会用你传递的文件替换实时脚本——运行它“只是为了看看它访问的 URL”已经导致用户丢失了生产脚本。如果你需要学习 URL，请使用 `-vvv --log-http-payload` 运行任何非修改命令。
2. **枚举运行时使用分页。** `/test_runs` 端点最多 1000 行，`gcx k6 runs list --limit 0` 不会自动跟随 `@nextLink`。使用 `k6-manage` §3 中记录的 `gcx api` 循环模式。
3. **验证日期范围。** 当用户说“过去 7 天”、“本周”、“最近运行”——请确认最新运行的 `created` 确实在该时间窗口内。如果没有，请暴露差距。
4. **`check()` 不会导致运行失败；只有 `thresholds` 才会。** 并且零观察值的阈值报告为 ✓ 通过。有关完整深入分析，请参阅“阈值语义”部分；第 5 步中的每个检查的 `checks` 指标查询可以捕获这两种情况。

## 前置条件

已安装 `gcx` 并针对用户的堆栈进行认证。请参阅 `k6-manage` §1。使用以下命令进行验证：

```bash
gcx --context <stack> config check    # expect "✔ Connectivity: online"
```

## 调查工作流程

### 第 1 步：识别测试和目标运行（运行）

从用户的 URL：

- `/a/k6-app/tests/<id>` → 负载测试（许多运行的父级）
- `/a/k6-app/runs/<id>` → 特定运行

要运行→测试：通过 `gcx api` 获取运行，请参阅 `k6-manage` §2 中的路径形状规则：

```bash
gcx --context <stack> api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/<run_id>
```

并从响应中读取 `.test_id`。要列出测试的运行，请参阅第 3 步。

### 第 2 步：获取测试元数据和脚本

```bash
gcx --context <stack> k6 load-tests get <test_id> -o json
```

对于脚本，请遵循 `k6-manage` §5 中的安全编辑配方的一半——如果你稍后要编辑，请保存备份。

**存在两个脚本端点，它们的区别对调查很重要。** `k6-manage` §5 记录了两者：当前的负载测试脚本和实际执行的每个运行快照。它们在脚本编辑后与运行分离。当问题涉及“发生了什么变化”、“为什么这次运行失败”，或者你正在检查一个超过几天旧的运行时，请通过 `k6-manage` §5 的运行脚本端点获取运行捆绑快照并与当前的负载测试脚本（或另一个运行的快照）进行比较。当前的负载测试脚本不是推理过去运行的正确工件。

### 第 3 步：带分页列出运行

使用 `gcx api` + `@nextLink` 循环模式（在 `k6-manage` §3 中记录）针对 `/cloud/v6/load_tests/<test_id>/test_runs`。收集 `all_runs` 后：

```python
print(f"Total: {len(all_runs)}")
runs_sorted = sorted(all_runs, key=lambda r: r['created'], reverse=True)
for r in runs_sorted[:10]:
    print(f"  {r['created']:30s} id={r['id']:>8} status={r['status']:<10} result={r.get('result','?')}")
```

向用户报告：运行总数、日期范围、最新运行日期。**如果“最新运行”超过一天**，请指出——他们可能认为计划正在运行，但实际上没有。

### 第 4 步：验证日期与用户意图对齐

如果用户要求“过去 7 天” / “本周” / “最近”：按日期范围过滤，而不是按行数——“最近的 7 次运行”可能跨越一天或一年，具体取决于测试运行的频率。

```python
last7 = [r for r in all_runs if r['created'] >= '<today_minus_7_days_iso>']
```

如果 `len(last7) == 0`：立即向用户暴露这一点。不要使用过时的数据继续进行。

### 第 5 步：确定通过/失败状态

针对每个运行检查三个独立层级：

| 层级 | 字段 | 含义 |
|---|---|---|
| 运行级结果 | `result` (`passed` / `failed` / `error` / `aborted`) | 阈值是否被违反 |
| 运行级状态 | `status` (`completed` / `aborted`) | 运行是否有序完成 |
| 脚本内检查 | v5 `checks` 指标，按 `check` 标签聚合 | 每个检查的成功率 |

对于用户认为“失败”但报告 `result: passed` 的运行：检查第三层级。常见模式：每个迭代中的 `check()` 返回 false，但运行仍然“通过”，因为未在 `checks` 上定义阈值。有关完整深入分析，请参阅“阈值语义”部分（零观察值陷阱、`abortOnFail` 云延迟、操作员支持）。

通过 v5 查询每个检查的分解（请参阅 `k6-manage/references/metrics.md` §7 中的 `query_aggregate_k6` 形状）：

```bash
gcx --context <stack> api \
  "/api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<run_id>/query_aggregate_k6(query='ratio by (check)',metric='checks')"
```

响应中的每个结果条目都带有 `check` 标签，其中包含检查名称和一个值：成功率（0.0–1.0）。对于原始成功/失败计数，还查询 `increase_nz by (check)`（成功次数）和 `increase_z by (check)`（失败次数）。

### 第 6 步：获取运行的指标

使用 `k6-manage/references/metrics.md` 中记录的 v5 指标端点。典型工作流程：

```bash
# 6a. 列出运行可用的指标（metrics.md §1）
gcx --context <stack> api /api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<run_id>/metrics

# 6b. 列出指标的标签，以了解可用于过滤/分组的内容（metrics.md §4）
gcx --context <stack> api \
  "/api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<run_id>/labels?match[]=http_req_duration"

# 6c. 时间序列——选择与指标类型匹配的查询方法（metrics.md §6）
gcx --context <stack> api \
  "/api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<run_id>/query_range_k6(query='histogram_quantile(0.95) by (name,status)',metric='http_req_duration',step=10)"

# 6d. 整个运行的标量聚合（metrics.md §7）
gcx --context <stack> api \
  "/api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<run_id>/query_aggregate_k6(query='increase',metric='http_reqs')"
```

根据每个指标类型选择正确的查询方法很重要——请参阅 `k6-manage/references/metrics.md` 中的“查询方法”表格。对于浏览器测试，URL/状态分解来自 `labels` + `label/{name}/values`（metrics.md §4/§5），而不是来自单独的标签端点。

### 第 7 步：获取运行的日志

遵循 `k6-manage` §4 中的 Loki 配方（`gcx api` 对 `/api/plugins/k6-app/resources/logs/...`，`{test_run_id="<id>"}` 选择器，强制 `X-K6TestRun-Id` 头，范围 `start`/`end` 到 `run.created`/`run.ended`）。将响应保存到 `/tmp/run_<id>_logs.json` 并按其中描述的方式从文件中总结。

### 第 8 步：（如果要求）安全编辑脚本

使用 `k6-manage` §5 中的完整安全编辑配方（GET → 备份 → 编辑 → `k6 inspect` → 1-iter 烟雾测试 → PUT with `Content-Type: application/octet-stream` → sha256 验证）。

当编辑涉及阈值时，请阅读“阈值语义”部分，了解零观察值陷阱、`abortOnFail` 云延迟和操作员支持（`==`/`!=` 尽管在文档中没有，但它们也起作用）。

### 第 9 步：报告

根据问题形状选择模板。

**对于单次运行调查**（“运行 X 出现了什么问题”）：

```
测试： <name> (id <test_id>)
运行： <run_id> @ <created> → <ended>, load_zone=<zone>, result=<result>

日志（<n> 个流，<m> 行）：
  - <流摘要>

指标（关键指标）：
  - <metric>: <method> = <value> (n=<count>)
  ...

每个检查的分解：
  - <check name>: <success_rate> (succ=<n>, fail=<n>)
  ...

诊断：<一段话>
```

**对于多次运行比较**（“通过运行和失败运行之间的差异是什么”、“这次更改是否导致了失败”）：

```
问题：<用户试图归因的内容的一行重述>

运行时间线（相关窗口）：

| Run ID | Created (UTC) | Result | exec_duration | processing_duration | k6 build | error code | key check ratios |
|---|---|---|---|---|---|---|---|
| ... | ... | passed | 60s | 195s | <build> | — | 1.0/1.0/1.0 |
| ... | ... | failed | 27s | 193s | <build> | — | 0.0/n=0/n=0 |
| ... | ... | error  | 51s | 3601s aborted | <build> | 8016 | 1.0/1.0/1.0 |

重要差异：
  - <field>: <value-in-passing> vs <value-in-failing> — <解释>
  ...

脚本差异（如果相关）：<代表通过和失败运行之间捆绑脚本的差异，总结>

诊断：<一段话归因于测试端、SUT 端或平台端，并附有支持证据>
```

表格使并排异常显而易见（例如，一列在通过和失败规则中完全相同，可以排除该维度作为原因；一列在它们之间翻转，是你的候选者）。

如果用户要求原始数据转储，也将其保存到 `/tmp/k6inv/run<id>/` 并告诉他们路径。

## 阈值语义

阈值，而不是 `check()` 调用，决定了运行的 `result`。行为有几个非明显的角落，会让第一次调查者误导，因此它们被收集在这里。第 5 步（“确定通过/失败状态”）和第 8 步（“安全编辑脚本”）都依赖于本节。

### `result` 的含义是什么

| `result` 值 | 含义                                                       |
|----------------|---------------------------------------------------------------|
| `passed`       | 所有阈值通过（或未定义）                                   |
| `failed`       | 至少一个阈值失败                                           |
| `error`        | 要么脚本在完成前崩溃（例如浏览器不会启动）**要么** k6 Cloud 平台端中止了运行。要判断是哪一个，请检查运行上的 `status_history[*].extra.code`——非空代码表示平台中止（例如 `8016` = “测试运行最大生命周期超过”在 `processing_metrics` 期间）。平台中止不是你代码的错，尽管它们作为 `error` 出现。 |
| `aborted`      | 用户或系统中止了运行                                      |

`check()` 调用**不会**直接影响 `result`。它们将观察值发射到内置的 `checks` 速率指标，然后阈值可能会评估它。如果没有阈值引用 `checks`，失败的检查对运行级 `result` 是不可见的。

### “零观察值=通过”陷阱

k6 在底层指标为零样本时报告阈值 ✓ 通过——即使阈值表达式否则会评估为 false：

```
checks{check:response is 200}
✓ 'rate==1.0' rate=0.00%       ← ✓ 通过！？
```

当脚本在到达相关的 `check()` 调用之前抛出时，这会咬人。在 `catch` 块中强制检查观察值，让阈值看到*一些东西*：

```javascript
try {
  const r = await page.goto(URL);
  check(r, { "response is 200": x => x.status() === 200 });
  // ... 迭代体的其余部分
  check(true, { "script completed without exception": () => true });
} catch (e) {
  console.error(e);
  check(null, { "script completed without exception": () => false });
} finally {
  await page.close();
}
```

然后添加 `'checks{check:script completed without exception}': ['rate==1.0']` 到阈值。这可以捕获导航失败和后期异常。

### `abortOnFail` 云延迟

> 当 k6 在云中运行时，阈值每 60 秒评估一次。`abortOnFail` 功能可能延迟高达 60 秒。

对于运行时间少于 60 秒的运行，`abortOnFail` 可能不会在迭代自然完成之前触发。阈值仍在运行结束时评估，`result` 切换到 `failed`——中止只是没有节省执行时间。

### 操作员

文档显示 `<`、`>`、`<=`、`>=`。**`==` 和 `!=` 也起作用**，尽管它们不在文档中。对于 `rate` 指标（值 0.00–1.00），`rate==1.0` 意味着“每个观察值都是非零”而 `rate==0` 意味着“所有观察值都是零。”

## 工作流程特定陷阱

对于规范陷阱列表（认证过期、重复的 `cloud/cloud/`、脚本 PUT 的 415、Loki 缺少 `X-K6TestRun-Id`、脚本 PUT 没有递增 `updated`、`gcx k6 runs list --limit 0` 没有跟随 `@nextLink`），请参阅 `k6-manage` §7。下表中的条目是本调查工作流程特有的：

| 症状 | 原因 | 修复 |
|---|---|---|
| “最新运行是 6 个月前”但计划说每天 | 你没有分页 `/test_runs` | 使用 `k6-manage` §3 中的 `@nextLink` 循环（第 3 步） |
| “过去 7 天”报告只包含旧运行 | 按行数过滤，而不是按日期 | 重新按 `created >= <iso_date>` 过滤（第 4 步） |
| 阈值报告 ✓ 通过但检查失败 | 零检查观察值；迭代在 `check()` 运行之前中止 | 查看“阈值语义”部分 |
| `result: error` 但脚本日志/指标看起来很好 | 可能是平台中止（例如 `processing_metrics` 超过 1 小时上限，`code 8016`）。执行本身正常完成。 | 检查运行上的 `status_history[*].extra.code`。非空平台代码→不是你代码的错。查看“阈值语义”部分 |
| 通过读取当前负载测试脚本调查过去运行 | 脚本可能在运行执行后已编辑——你所读的不是运行的内容 | 通过每个运行端点获取运行*捆绑*脚本（`k6-manage` §5），并在得出结论之前与当前的负载测试脚本进行比较 |
| 刚刚覆盖了用户的脚本 | 调用 `update-script` 来“看看 URL” | 从第 2 步中恢复备份。要在不写入的情况下学习 URL，请在任何非修改命令上使用 `-vvv --log-http-payload`。 |
| CLI `--iterations 1` 打破了浏览器场景 | 完全覆盖了场景块 | 使用 sed 编辑文件中的 `iterations:` 而不是 CLI。 |

## 参考

- [`references/worked-example.md`](references/worked-example.md) — 一个具有真实发现的合成调查，可作为第 9 步报告模板。
