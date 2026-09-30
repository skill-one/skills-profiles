---
name: parallel-data-enrichment
description: 批量数据增强。为公司、人员或产品列表添加来自网络的数据字段（如CEO姓名、融资信息、联系方式）。可用于增强CSV文件或内联数据。支持多轮交互：通过传递 --previous-interaction-id 参数（来自先前的研究任务）来延续上下文。
---

# 数据丰富

丰富：$ARGUMENTS

## 开始前

告知用户，根据请求的行数和字段数量，丰富过程可能需要几分钟时间。

## 可选：建议输出列

如果用户给出了模糊的意图（例如“用有用信息丰富这些公司”），并且不确定要添加哪些列，请在启动运行之前向 API 请求建议：

```bash
parallel-cli enrich suggest "查找CEO和最近融资信息" --json
```

响应是一个信封：`{title, processor, enriched_columns, warnings}`。仅提取**`enriched_columns`数组**（而不是整个信封），并将其作为 `--enriched-columns` 在 `enrich run` 中的值（替换 `--intent`）。这些标志是指定要丰富内容的不同方法。如果 `suggest` 返回了 `processor`，请通过 `--processor` 在 `run` 调用中显式传递它。如果用户已经指定了他们想要的字段，请跳过此部分。

> `enrich suggest` 需要 `parallel-cli` ≥ 0.3.0。如果只有该命令缺失，请跳过可选的建议步骤，并在步骤 1 中使用 `--intent`。从设置中建议特定于安装的升级。不要将身份验证、API 或无效输入失败归类为旧的 CLI。基于意图的运行本身会请求建议；显式列默认为 `core-fast`，而意图可以选择另一个处理器，除非 `--processor` 覆盖它。

## 第 1 步：开始丰富

使用以下命令模式之一（替换用户的实际数据）：

对于内联数据：

```bash
parallel-cli enrich run --data '[{"company": "Google"}, {"company": "Microsoft"}]' --intent "CEO 名称和成立年份" --target "output.csv" --no-wait --json
```

对于 CSV 文件：

```bash
parallel-cli enrich run --source-type csv --source "input.csv" --target "output.csv" --source-columns '[{"name": "company", "description": "公司名称"}]' --intent "CEO 名称和成立年份" --no-wait --json
```

如果这是一个**对先前研究任务的后续操作**并且您有它的 `interaction_id`，请添加上下文链接：

```bash
parallel-cli enrich run --data '...' --intent "..." --target "output.csv" --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

这会重用先前的任务的上下文。上下文链接对零数据保留（ZDR）账户不可用，因此请省略该标志并在那里明确包含所需的上下文。丰富操作**不会**返回新的 `interaction_id`；保留先前的任务 ID 以供后续操作使用。`taskgroup_id` 或 Search/Extract `session_id` 不是任务交互 ID。

**重要提示：** 始终包含 `--no-wait` 以使命令立即返回而不是阻塞。

立即保存 `--json` 输出的 `taskgroup_id`、`url` 和 `num_runs`。没有 `interaction_id` 字段。如果创建中断或其响应丢失，请检查是否已创建组，然后再提交另一个运行。立即告知用户：

- 丰富操作已启动
- 他们可以跟踪进度的监控 URL

该组在服务器端运行；稍后可以使用保存的 ID 进行轮询。

## 第 2 步：轮询结果

选择一个持久且特定于运行的输出路径（例如，`enrichment-acme-tgrp-<id>.json`）。轮询会覆盖其输出文件，因此请检查任何现有文件并使用新路径，除非您打算替换。无论扩展名如何，输出都是 JSON：一个包含 `input` 和 `output` 或 `error` 的行数组。异步轮询不包括基础或每行交互 ID；不要编造引用或上下文 ID。

```bash
parallel-cli enrich poll "$TASKGROUP_ID" --timeout 60 --output "enrichment-<描述性名称>-<组ID>.json"
```

重要提示：

- 保持轮询有边界；`--timeout 60` 允许在等待之间更新进度。
- 在 `--no-wait` 模式下，步骤 1 中的 `--target` 无用。此处仅 `--output` 决定结果保存的位置，并且文件始终为 JSON。
- 完成的组可以包含失败的行。分别计算包含 `output` 的行数和包含 `error` 的行数，并将它们的总数与 `num_runs` 进行比较；空文件或不完整文件不是成功的整个输入丰富。

### 如果轮询超时或中断

超时退出 5 或中断结束本地等待。在说它仍在运行之前，请检查组状态：

```bash
parallel-cli enrich status "$TASKGROUP_ID" --json
```

检查 `is_active`、`status_counts` 和 `num_runs`。对活动组继续相同的轮询，或检索非活动组的结果并报告失败或不解析的行。不要在超时或自动重试失败行时重新创建组。本地文件写入失败可以重试相同的组 ID 和可写入的输出路径。

### 如果用户请求 CSV

将保存的 JSON 本地转换为单独的 CSV。保留每个原始输入列和行，包括重复和失败的行；将丰富字段与冲突的输入名称分开，并为失败包含错误列。不要假设流式传输的行与原始输入顺序匹配或猜测行身份不明确时的连接。验证行数并保留输入 CSV 不变。这是本地转换，而不是异步轮询生成的 CSV；报告 JSON 和 CSV 路径。

## 响应格式

**步骤 1 之后：** 分享监控 URL（用于跟踪进度）。

**步骤 2 之后：**

1. 报告成功、失败和总行数，并指出任何缺失的结果。
2. 预览几行成功结果和代表性失败（如果存在），但不声称所有行都成功。
3. 告知用户输出文件的完整路径

完成后，链接保存的输出，而不是重复监控 URL。

## 设置

如果找不到 `parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果缺少文档中记录的选项或命令，请识别安装方法并通过该方法升级：独立的 `parallel-cli update`；pipx `pipx upgrade parallel-web-tools`；uv `uv tool upgrade parallel-web-tools`；Homebrew `brew upgrade parallel-web/tap/parallel-cli`；npm `npm update -g parallel-web-cli`。在重试之前，在代理的终端中重新检查版本和帮助。

对于身份验证或 API 错误，请检查返回的消息。`403` 可能表示权限、账户策略或计费；它并不能证明余额不足。在相关情况下检查 `parallel-cli auth --json` 及其 `authenticated` 布尔值，而不暴露凭证。只有计费特定错误才需要检查余额，而添加资金需要明确确认。重用保存的组 ID；不要自动重试模糊的创建。
