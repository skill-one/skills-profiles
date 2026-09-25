# Cargo CLI — 诊断

工作流行为的法医运行手册：追踪单个运行、批量扫描错误、分析某个 play 的信用消耗。这项技能是**解释层**——原始表面（`run get`、编排 SQL、计费指标）在 `cargo-orchestration` 和 `cargo-billing` 中进行了记录；这里的每个运行手册会告诉你需要从它们中拉取哪些内容、按什么顺序拉取，以及每个输出形状的含义。

## 初始化

已经登录（`cargo-ai whoami` 返回一个工作区）？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在进行任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批量的任何操作都是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。信用归因步骤（`billing usage get-metrics`、`billing subscription get`）需要具有**管理员权限**的 token；其他所有操作都可以使用标准 token。当完整技能包安装完成后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、token 范围以及仅管理员可见的表面。

## 选择哪个运行手册？

```
您正在诊断什么？
│
├── 单个运行/单个记录（"为什么这个记录失败？",
│   "运行成功但输出不正确/为空"）
│   └── references/run-trace.md
│
├── 多个运行（"批量有错误"、"错误率飙升",
│   "哪个节点持续失败？"）
│   └── references/batch-error-sweep.md
│
└── 成本（"这个 play 太昂贵"、"信用消耗在哪里？",
    "如何使其更便宜"）
    └── references/play-optimize-credits.md
```

经验法则：当您还不确定要查看哪个运行时，从**扫描**开始——它会以示例运行 UUID 的形式结束，您可以将其输入到**追踪**中。

**完全没有运行 UUID**（"查看最后一个运行"、"acme.com 的运行"、"我在编辑器中做了什么"）？那是 [`references/run-trace.md`](references/run-trace.md) § 0，它将症状解析为 UUID。请注意，`orchestration run list` **需要** `--workflow-uuid` 并且无法回答它——编排 SQL 对 `runs` 没有过滤器并且可以。永远不要因为 `run list` 拒绝就得出结论认为运行输入和输出不可访问。

**与 `cargo-analytics` 的边界**：分析*测量和导出*（"错误率是多少？"、"下载批量结果"、"导出这个片段"）；这项技能*解释*（"为什么错误率上升？"、"为什么这个记录的输出为空？"）。诊断通常从一个分析信号（错误计数飙升、批量报告 `failedRunsCount > 0`）开始，并最终回到分析——一旦问题解决并且运行重新执行，批量检索通过 `run download-outputs` / `batch download` / `segment download` 进行，所有内容都在 `../cargo-analytics/SKILL.md` 中记录。这项技能的证据表面（`run get`、编排 SQL、计费指标）用于诊断，而不是批量导出。

## 参考

| 文档 | 覆盖内容 |
| --- | --- |
| [`references/run-trace.md`](references/run-trace.md) | 当您没有 UUID 时找到运行（§ 0），然后端到端地跟踪它：每个节点的执行、`runContext` 输出、分支路由、每个节点的信用和计时。 |
| [`references/batch-error-sweep.md`](references/batch-error-sweep.md) | 在批量/Play/工作区中找到出错的运行，按根本原因分组失败，选择示例，决定修复还是报告。 |
| [`references/play-optimize-credits.md`](references/play-optimize-credits.md) | 将信用消耗归因于工作流和节点，然后按优先级顺序应用成本杠杆。单独归因**执行费用**（§ 2b）——每个节点执行 0.01 信用，`creditsUsedCount` 不携带并且因此每个节点的归因会遗漏。 |

## 每个运行手册依赖的表面

| 表面 | 命令 | 提供给您 |
| --- | --- | --- |
| 运行详情 | `cargo-ai orchestration run get <run-uuid>` | `run.executions[]`（按节点追踪）、`runContext`（按 `nodeSlug` 的每个节点输出）、`runComputedConfigs`（每个节点实际调用参数） |
| 编排 SQL | `cargo-ai orchestration query execute "<sql>"` | 对 `runs`、`batches`、`spans`、`records` 进行聚合（ClickHouse；没有模式前缀；工作区范围） |
| 计费指标 | `cargo-ai billing usage get-metrics --from <date> --to <date>` | 信用总计，可按 `workflow_uuid`、`connector_uuid`、`agent_uuid`、`integration_slug`、`model_uuid` 进行过滤和分组 |
| 图形展示 | `cargo-ai orchestration node diagram --run-uuid <uuid> --highlight <slug> --format ascii --raw` | 运行执行的图，标出失败的节点。免费，不执行任何操作 |

**在解释路由错误之前绘制图形。** 对于 "选择了错误的分支" 或 "这个步骤从未运行" 的情况，图形是证据，并且它显示了 `run get` 无法明显显示的一件事：`on failure` 边缘。看起来被跳过的步骤通常是运行通过 `fallbackChildUuid` 边缘*达到*的，这意味着提供者出错而不是返回空——不同的诊断和不同的修复方法。标志和 ASCII 图例：[`../cargo-orchestration/references/node-diagram.md`](../cargo-orchestration/references/node-diagram.md)。

完整查询语法、表列和全大写：[`../cargo-orchestration/references/examples/queries.md`](../cargo-orchestration/references/examples/queries.md)。调试字段语义：[`../cargo-orchestration/references/troubleshooting.md`](../cargo-orchestration/references/troubleshooting.md)。

## 展示结果

遵循 [`../cargo/references/interaction.md`](../cargo/references/interaction.md)：首先提出结论（"20 个失败中有 18 个是同一个原因：连接器的 token 过期"），用简短表格总结证据，永远不要将原始 `run get` JSON 或完整查询结果直接输入对话中。任何重新运行付费节点的修复会通过试点门：首先重新运行 **10–20 条记录**，报告观察到的成本和命中率，然后要求用户引用**记录数量**和**信用估计**批准其余部分——诊断不是批准重新计费产生它的批量。完整支出规则在 [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md) 中。

## 诊断遇到死胡同时

如果证据与记录的行为矛盾（`run get` 缺少字段、查询限制与文档不符、出现无意义的错误），请提交报告——这是官方渠道，团队会阅读每一个：

```bash
cargo-ai workspaceManagement report create \
  --title "<一句话摘要>" \
  --description "<运行的命令、errorMessage 原文、预期与实际、UUIDs>"
```
