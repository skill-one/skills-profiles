# 数据丰富

丰富：$ARGUMENTS

## 开始前

告知用户，根据请求的行数和字段数量，丰富过程可能需要几分钟时间。

## 可选：建议输出列

如果用户给出了模糊的意图（例如“用有用信息丰富这些公司”），并且不确定要添加哪些列，请在启动运行之前向 API 请求建议：

```bash
parallel-cli enrich suggest "查找CEO和最近融资信息" --json
```

响应是一个信封：`{title, processor, enriched_columns, warnings}`。仅提取 **`enriched_columns` 数组**（而不是整个信封），并将其作为 `--enriched-columns` 在 `enrich run` 中的值，**替换 `--intent`** — 这两个标志是指定要丰富内容的替代方法，不能组合使用。如果 `suggest` 返回了 `processor`，请通过 `--processor` 在 `run` 调用中显式传递它（这是针对模式的调整建议）。如果用户已经指定了他们想要的字段，则跳过此整个部分。

> `enrich suggest` 需要 `parallel-cli` ≥ 0.3.0。如果它错误地返回类似 `no such command` / `No such command` / `unknown command` 的信息，**不要退出** — 跳过建议步骤，跳转到步骤 1 并使用 `--intent`，完成运行，并在最终响应中提及 `parallel-cli update`（或 `pipx upgrade parallel-web-tools`），以便用户下次使用时获取该功能。

## 步骤 1：开始丰富

使用以下命令模式之一（替换用户的实际数据）：

对于内联数据：

```bash
parallel-cli enrich run --data '[{"company": "Google"}, {"company": "Microsoft"}]' --intent "CEO姓名和成立年份" --target "output.csv" --no-wait --json
```

对于 CSV 文件：

```bash
parallel-cli enrich run --source-type csv --source "input.csv" --target "output.csv" --source-columns '[{"name": "company", "description": "公司名称"}]' --intent "CEO姓名和成立年份" --no-wait --json
```

如果这是一个对先前研究任务的**后续操作**并且您有它的 `interaction_id`，请添加上下文链：

```bash
parallel-cli enrich run --data '...' --intent "..." --target "output.csv" --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

丰富将使用先前研究的全上下文运行 — 因此您可以丰富先前发现的实体，而无需重述已经找到的内容。注意：丰富本身**不会**生成新的 `interaction_id`，因此您不能在丰富上链式添加进一步的后续操作。

**重要提示：** 始终包含 `--no-wait`，以便命令立即返回而不是阻塞。

解析 `--json` 输出以提取 `taskgroup_id` 和 `url`。输出是 `{taskgroup_id, url, num_runs}` — 没有 `interaction_id` 字段，不要寻找它。立即告知用户：

- 丰富已启动
- 可以在以下监控 URL 中跟踪进度

告诉他们可以将轮询步骤置为后台，以便在运行时继续工作。

## 步骤 2：轮询结果

选择一个具体的输出路径（例如，`/tmp/enrichment-acme.json`）。注意：无论您选择什么扩展名，文件都是 JSON — 它是一个 `{input, output}` 对象的数组，而不是 CSV。将其命名为 `.json` 以避免混淆自己或用户。

```bash
parallel-cli enrich poll "$TASKGROUP_ID" --timeout 540 --output "/tmp/enrichment-<描述性名称>.json"
```

重要提示：

- 使用 `--timeout 540`（9 分钟）以保持在工具执行限制内
- 步骤 1 中的 `--target` 在 `--no-wait` 模式下未使用 — 仅 `--output` 此处决定结果保存位置，并且文件始终是 JSON

### 如果轮询超时

大型数据集的丰富可能需要超过 9 分钟。如果轮询未完成即退出：

1. 告知用户丰富仍在服务器端运行
2. 重新运行相同的 `parallel-cli enrich poll` 命令以继续等待

## 响应格式

**步骤 1 之后：** 分享监控 URL（用于跟踪进度）。

**步骤 2 之后：**

1. 报告丰富行数
2. 预览输出文件的前几行（它是一个 `{input, output}` 对象的 JSON 数组）
3. 告知用户输出文件的完整路径

完成时不重新分享监控 URL — 结果在输出文件中。

## 设置

如果找不到 `parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果任何 `parallel-cli enrich` 命令返回 `403`，请告知用户可能需要余额。提供运行 `parallel-cli balance get` 的选项，如果需要，在运行 `parallel-cli balance add <amount_cents>` 之前请求明确确认。然后重试原始丰富命令。
