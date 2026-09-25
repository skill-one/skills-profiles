# Cargo CLI — 分析

测量和导出：监控运行指标、下载运行和批量结果、导出分段数据。

> 查看完整的 JSON 响应结构，请参阅 `references/response-shapes.md`。
> 查看常见错误及其解决方法，请参阅 `references/troubleshooting.md`。
> 查看运行指标和错误监控示例，请参阅 `references/examples/run-analytics.md`。
> 查看数据导出和下载示例，请参阅 `references/examples/exports.md`。
> 如需计费、使用指标和订阅信息，请使用 `cargo-billing` 技能。

## 初始化

如果已经登录（`cargo-ai whoami` 返回工作区），则跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令添加 `npx @cargo-ai/cli` 前缀
cargo-ai login --email you@company.com  # 通过邮件验证代码，无需浏览器；首次使用时创建账户
                                        # 其他选项：--oauth（浏览器）· --token <api-token>（CI）
cargo-ai whoami                         # 在执行任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批量的操作是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装完成后，`[../cargo/references/prerequisites.md](../cargo/references/prerequisites.md)` 会添加 CLI 版本固定、令牌范围和管理员专用的界面。

## 范围 — 测量和导出，而非解释

此技能回答 **"发生了什么"** 和 **"给我数据"**：指标、计数、下载、导出。当问题变成 **"为什么"** 时 — 为什么运行失败、为什么输出错误或为空、哪个根本原因解释这些错误、为什么这个流程如此昂贵 — 切换到 `cargo-diagnostics` 技能；其运行书将原始界面串联成诊断。

| 问题听起来像… | 负载 |
| --- | --- |
| "错误率是多少？" / "本周有多少运行失败？" / "导出结果 / 分段" | **此技能** |
| "为什么运行失败？" / "运行成功但输出看起来错误" | `cargo-diagnostics` → `references/run-trace.md` |
| "为什么这个批量有错误？哪个节点持续失败，是单一原因还是多个原因？" | `cargo-diagnostics` → `references/batch-error-sweep.md` |
| "为什么这个流程如此昂贵？积分去哪里了？" | `cargo-diagnostics` → `references/play-optimize-credits.md` |

这两个技能自然串联：分析 **检测**（错误率飙升、批量报告失败），诊断 **解释**（20个失败中有18个共享一个根本原因），然后分析 **检索** 清洁结果（在原因修复并重新执行运行后）。

## 首先发现资源

大多数分析命令需要 UUID。在查询前发现它们。

```bash
cargo-ai orchestration play list            # 所有流程（名称、workflowUuid）
cargo-ai orchestration tool list            # 所有工具（名称、workflowUuid）
cargo-ai orchestration workflow list        # 所有工作流（uuid 仅限 — 无名称）
cargo-ai ai agent list                     # 所有代理（uuid、名称）
cargo-ai connection connector list          # 所有连接器（uuid、名称、integrationSlug）
cargo-ai storage model list                # 所有模型（uuid、名称、slug）
```

## 快速参考

```bash
cargo-ai orchestration run get-metrics --workflow-uuid <uuid>
cargo-ai orchestration run download --workflow-uuid <uuid> --is-finished
cargo-ai orchestration run count --workflow-uuid <uuid> --statuses error
cargo-ai orchestration query execute "SELECT status, count() FROM runs GROUP BY status"
cargo-ai segmentation segment download --model-uuid <uuid> --filter '{"conjonction":"and","groups":[]}'
```

**选择正确的命令：**

- `run get-metrics` / `run count` — 工作流范围的预定义聚合。当你已经有 `workflowUuid` 时最佳。
- `orchestration query execute` — 跨整个工作空间的 ad-hoc SQL (`runs`, `batches`, `spans`, `records`)。适用于跨工作流分析、按节点细分和时间序列分析。
- `run download` / `run download-outputs` — 按记录检索输出。
- `segment download` / `storage query execute` — 存储数据（公司、联系人等）。

## 工作流运行指标

工作流运行的聚合指标（成功/错误率、每个节点的积分）。

```bash
# 工作流的指标
cargo-ai orchestration run get-metrics --workflow-uuid <uuid>

# 限定于发布、批量或日期范围
cargo-ai orchestration run get-metrics --workflow-uuid <uuid> --release-uuid <uuid>
cargo-ai orchestration run get-metrics --workflow-uuid <uuid> --batch-uuid <uuid>
cargo-ai orchestration run get-metrics --workflow-uuid <uuid> \
  --created-after <start-date> --created-before <end-date>
```

## 运行计数

按特定标准匹配的运行计数 — 对监控很有用。

```bash
cargo-ai orchestration run count --workflow-uuid <uuid> --statuses error
cargo-ai orchestration run count --workflow-uuid <uuid> --is-finished \
  --created-after <start-date> --created-before <end-date>
cargo-ai orchestration run count --workflow-uuid <uuid> --batch-uuid <uuid>
```

支持：`--statuses`、`--batch-uuid`、`--release-uuid`、`--is-finished`、`--created-after`、`--created-before`、`--record-id`、`--record-title`。

对于跨工作流分析或 `run count` 未暴露的形状（按节点失败细分、p95 持续时间、错误率随时间变化），使用 `orchestration query execute` — 见 [Ad-hoc 执行分析](#ad-hoc-execution-analytics-orchestration-query) 部分。

## Ad-hoc 执行分析（`orchestration query`）

对编排运行时表（`runs`、`batches`、`spans`、`records`）运行 SQL，以进行 canned 指标命令未涵盖的分析。表引用时不带模式前缀；工作空间范围自动生效。参见 `cargo-orchestration/references/examples/queries.md` 了解模式和限制。

```bash
# 工作空间最后一天的错误率
cargo-ai orchestration query execute \
  "SELECT countIf(status='error') / count() AS error_rate FROM runs WHERE created_at > now() - INTERVAL 1 DAY"

# 本周每个工作流的失败运行
cargo-ai orchestration query execute \
  "SELECT workflow_uuid, count() AS errors FROM runs WHERE status='error' AND created_at > now() - INTERVAL 7 DAY GROUP BY workflow_uuid ORDER BY errors DESC"

# 最后 24 小时每个节点的失败计数
cargo-ai orchestration query execute \
  "SELECT node_slug, count() AS failures FROM spans WHERE execution_status='error' AND execution_started_at > now() - INTERVAL 1 DAY GROUP BY node_slug ORDER BY failures DESC"

# 本月每个工作流的积分消耗
cargo-ai orchestration query execute \
  "SELECT workflow_uuid, sum(credits_used_count) AS credits FROM batches WHERE created_at >= toStartOfMonth(now()) GROUP BY workflow_uuid ORDER BY credits DESC"
```

只读且有限制：30 秒执行时间、10 000 行结果、10 000 万行扫描。使用 `created_at`/`execution_started_at` 谓词缩小范围，以保持在行扫描限制以下。

## 下载运行结果

两个不同的命令 — 为任务选择正确的命令。

### `run download` — 每个运行一行，每个节点一列（gzip 压缩的 CSV）

返回 `{"url": "..."}` — 一个用于 gzip 压缩 CSV 的签名 URL。每行是一个运行：`_uuid`、`_workspace_uuid`、`_workflow_uuid`、`_record_id`、`_record_title`、`_created_at`、`_finished_at`、`_status`、`_error_message`，然后是 **每个节点 slugs 的列**。

**每个节点列包含该执行的 `title` — 一个截断的人类可读摘要，不是节点的输出。** 此文件中没有 `runContext` 和 `executions[]`。将其视为跨多个运行的状况板（哪个节点出错、在哪个记录上），而不是节点生成的证据 — 在其他地方 `cargo-diagnostics` 也适用于 `title` 的相同规则。

```bash
# 工作流的所有运行
cargo-ai orchestration run download --workflow-uuid <uuid>

# 日期范围
cargo-ai orchestration run download --workflow-uuid <uuid> \
  --created-after <start-date> --created-before <end-date>

# 特定状态（运行状态：空闲、等待、运行、成功、错误、取消、已取消、跳过 — 不包括 "完成"/"失败"）
cargo-ai orchestration run download --workflow-uuid <uuid> --statuses success,error

# 每个达到终端状态的运行。`--is-finished` 是 `finished_at IS NOT NULL`，比成功+错误更宽泛：已取消和跳过的运行也标记了 finishedAt，所以不要互相替换。
cargo-ai orchestration run download --workflow-uuid <uuid> --is-finished

# 从特定批量
cargo-ai orchestration run download --workflow-uuid <uuid> --batch-uuid <uuid>
```

### `run download-outputs` — 每个运行的输入+输出（CSV/JSON 通过签名 URL）

**这是从平台获取动作结果的规范方式。** 映射到 API `POST /v1/orchestration/runs/download-outputs`。返回 `{"url": "..."}` — 一个用于 CSV（默认）或 JSON 文件的签名 URL。每行一个运行：相同的 `_` 前缀运行元数据，加上 `input`（第一个节点的解析配置）和 `output`（选择的节点的上下文，当省略 `--output-node-slug` 时默认为最后一个执行的节点）。

```bash
# `--workflow-uuid` 是唯一必需的标志
cargo-ai orchestration run download-outputs \
  --workflow-uuid <uuid> \
  --format json \
  --limit 20

# 明确指定输出节点，并按批量过滤
cargo-ai orchestration run download-outputs \
  --workflow-uuid <uuid> \
  --output-node-slug <slug> \
  --batch-uuid <uuid>
```

要找到 `output-node-slug`：`cargo-ai orchestration release get <release-uuid>` → 查看 `nodes[].slug`。终端输出节点通常命名为 `output` 或 `end`。如果没有 `--limit`，文件涵盖 **所有** 匹配的工作流运行，所以当你只需要样本时传递一个。

**按记录而非按运行：** `cargo-ai orchestration record download-outputs` 接受相同的 `--workflow-uuid` / `--output-node-slug`，并输出每 **记录** 一行。它使用 `--limit` 和 `--offset`（CLI ≥ 1.0.90）分页 — 导出太大而无法放入单个文件的方法是分固定切片（`--limit 1000 --offset 0`，然后 `--offset 1000`，…）而不是一次请求所有内容。`run download-outputs` 以相同方式分页，跨运行。

### 获取多个运行的完整 `runContext`

一次无法获取。完整的按节点上下文是 **每个运行的 S3 对象**，并且 `orchestration run get <run-uuid>` 是唯一能将其水合的命令 — 一次一个运行。上述两个导出是投影：`download` 给你跨多个运行的节点 *标题*，`download-outputs` 给你跨多个运行的第一个节点输入 + 一个节点的输出。对于介于两者之间的内容，请循环 `run get` 跨从发现阶梯（`[../cargo-diagnostics/references/run-trace.md](../cargo-diagnostics/references/run-trace.md) § 0`）获得的 UUID。

编排 SQL 不是这里的替代方案：`runs` 和 `spans` 携带状态、时间和积分，但没有节点输入/输出列。

## 下载批量结果

```bash
cargo-ai orchestration batch download --uuid <batch-uuid> --output-node-slug <node-slug>
```

要找到 `output-node-slug`：运行 `cargo-ai orchestration release get <release-uuid>`（从批量获取发布 UUID）并查看 `nodes[].slug`。

## 处理部分批量失败

状态为 `success` 的批量仍可能包含单个运行失败。在将结果视为完整前，始终检查批量中的错误。

**步骤 1 — 检查批量摘要：**

```bash
cargo-ai orchestration batch get <batch-uuid>
# → .runsCount          = 提交的总记录数
# → .executedRunsCount  = 达到终端状态（成功或错误）的记录数
# → .failedRunsCount    = 出错的记录数
```

**步骤 2 — 计数并下载失败的运行：**

```bash
cargo-ai orchestration run count \
  --workflow-uuid <uuid> \
  --batch-uuid <batch-uuid> \
  --statuses error

cargo-ai orchestration run download \
  --workflow-uuid <uuid> \
  --batch-uuid <batch-uuid> \
  --statuses error
```

**步骤 3 — 诊断。** 查明 *为什么* 它们失败 — 按根本原因分组失败、选择示例运行、阅读 `runContext` — 是 `cargo-diagnostics` 技能的工作：加载 `../cargo-diagnostics/references/batch-error-sweep.md` 并提供批量 UUID。

**步骤 4 — 仅重新运行失败的记录：**

在诊断并修复根本问题（连接器凭证、输入数据错误、速率限制）后：

```bash
# 从失败的运行下载中提取记录 ID，然后：
cargo-ai orchestration batch create \
  --workflow-uuid <uuid> \
  --data '{"kind":"recordIds","recordIds":["id1","id2","id3"]}'
```

**按节点输出 slug 过滤：**

要下载批量的特定节点输出（例如，仅富集节点，不包括完整运行）：

```bash
# 1. 从批量获取发布 UUID
cargo-ai orchestration batch get <batch-uuid>
# → .releaseUuid

# 2. 找到节点 slug
cargo-ai orchestration release get <release-uuid>
# → nodes[].slug

# 3. 下载该节点的输出
cargo-ai orchestration batch download \
  --uuid <batch-uuid> \
  --output-node-slug <node-slug>
```

## 分段数据导出

`conjonction` 使用 `conjonction`（不是 `conjunction`）— 这是故意的。参见 `cargo-orchestration` 技能的 `references/filter-syntax.md` 了解完整的过滤器语法。

```bash
# 完全导出（所有记录）
cargo-ai segmentation segment download \
  --model-uuid <uuid> \
  --filter '{"conjonction":"and","groups":[]}'

# 带排序和限制
cargo-ai segmentation segment download \
  --model-uuid <uuid> \
  --filter '{"conjonction":"and","groups":[]}' \
  --sort '[{"columnSlug":"created_at","kind":"desc"}]' \
  --limit 1000
```

**重要：** `segment download` 需要 `--model-uuid`，而不是 `--segment-uuid`。从 `segment list` 获取 `modelUuid`。

对于带富集的实时分页查询，使用 `cargo-orchestration` 技能的 `segmentation segment fetch`。

## 帮助

每个命令都支持 `--help`：

```bash
cargo-ai billing usage get-metrics --help
cargo-ai orchestration run download --help
cargo-ai segmentation segment download --help
```
