# 深度研究

研究主题：$ARGUMENTS

> 需要 `parallel-cli` ≥ 0.3.0。如果以下任何命令出现 `no such option`、`no such command` 或 `unrecognized arguments` 错误，则用户使用的 CLI 版本较旧。建议他们运行 `parallel-cli update`（如果通过 pipx 安装，则运行 `pipx upgrade parallel-web-tools`），然后重试。

## 何时使用（与 parallel-web-search 相比）

仅当用户明确要求深度/详尽研究时才使用此技能。深度研究比 parallel-web-search 慢 10-100 倍且成本更高。对于正常的 "研究 X" 请求、快速查找或事实核查，请使用 **parallel-web-search**。

## 第 1 步：开始研究

根据主题选择一个描述性的文件名（例如，`ai-chip-market-2026`、`react-vs-vue-comparison`）。使用小写字母和连字符，不要有空格。在步骤 2 中，将此基本名称作为 `-o "$FILENAME"` 重复使用。

```bash
parallel-cli research run "$ARGUMENTS" --processor pro-fast --text --no-wait --json
```

`--text` 标志指示 API 在任务完成时返回 Markdown 报告（带内联引用），而不是默认的 JSON 结构化输出。用于叙述/报告风格的请求，这是大多数用户期望从 "深度研究" 中获得的内容。如果用户明确要求结构化 JSON 输出，请删除 `--text`。

可选的 `--text`：传递 `--text-description "保持在 1500 字以内，重点关注并购活动"` 来引导长度、格式或重点。

如果这是一个对先前研究或丰富任务（您知道 `interaction_id`）的**后续**，请添加上下文链接：

```bash
parallel-cli research run "$ARGUMENTS" --processor lite-fast --text --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

通过跨请求链接 `interaction_id` 值，每个后续问题都会自动具有先前回合的完整上下文——因此您可以深入挖掘，而无需重述已研究的内容。对于后续问题，使用较轻的处理器（`lite-fast` 或 `base-fast`），因为初始回合的重型工作已经完成。

此命令立即返回。**请勿省略 `--no-wait`**——否则，该命令会阻塞几分钟并超时。

处理器选项（根据用户请求选择）：

| 处理器     | 预期延迟   | 使用场景         |
|------------|------------|------------------|
| `lite-fast` | 10–60 秒  | 快速查找、后续问题 |
| `base-fast` | 15–100 秒 | 简单问题         |
| `core-fast` | 1–5 分钟  | 中等研究         |
| `pro-fast` | 2–10 分钟 | **默认**——探索性研究，深度/速度平衡良好 |
| `ultra-fast` | 5–25 分钟 | 多源深度研究 (~2 倍成本) |
| `ultra2x-fast` / `ultra4x-fast` / `ultra8x-fast` | 最长 2 小时 | 最难的问题，仅在明确要求时使用 |

关于 `-fast` 后缀的说明：`-fast` 等级使用缓存的网络数据，速度更快。非 `-fast` 变体（`pro`、`ultra` 等）重新获取最新数据——较慢但更适合非常近期的事件。除非用户明确要求查看过去一两天内的新闻，否则默认使用 `-fast`。

运行 `parallel-cli research processors` 查看完整列表及延迟。

解析 JSON 输出以提取 `run_id`、`interaction_id` 和监控 URL。立即告知用户：

- 深度研究已启动
- 所选处理器等级的预期延迟（如上表所示）
- 监控 URL，他们可以在其中跟踪进度

告诉他们可以将轮询步骤置为后台，以便在研究运行时继续工作。

## 第 2 步：轮询结果

```bash
parallel-cli research poll "$RUN_ID" -o "$FILENAME" --timeout 540
```

重要：

- 使用 `--timeout 540`（9 分钟）以保持在工具执行限制内
- **不要**传递 `--json`——完整输出很大，会淹没上下文。`-o` 标志将结果写入文件。
- 使用 `-o "$FILENAME"`：
  - `$FILENAME.json` 始终会被写入（元数据+基础）
  - `$FILENAME.md` 仅在步骤 1 使用 `--text` 时被写入（Markdown 报告）
- 轮询命令在研究完成时将**执行摘要**打印到 stdout。与用户分享执行摘要——它为他们提供了快速概览，而无需打开文件。
- 如果重新轮询并希望覆盖现有文件，请传递 `--force`

### 如果轮询超时

更高处理器等级可能需要超过 9 分钟。如果轮询未完成即退出：

1. 告知用户研究仍在服务器端运行
2. 重新运行相同的 `parallel-cli research poll` 命令以继续等待

## 响应格式

**步骤 1 之后：** 分享监控 URL（仅用于跟踪进度——它不是最终报告）。

**步骤 2 之后：**

1. 分享轮询命令打印到 stdout 的**执行摘要**
2. 告知用户生成的文件路径：
   - `$FILENAME.md` — 格式化的 Markdown 报告（如果使用了 `--text`）
   - `$FILENAME.json` — 元数据和基础
3. 分享 `interaction_id` 并告知用户他们可以提出基于此研究的后续问题（例如，“深入挖掘 X”或“将其与 Y 进行比较”）

完成时**不要**重新分享监控 URL——结果在文件中，不在该链接。

询问用户是否希望阅读文件以获取更多细节。除非用户要求，否则**不要**将文件内容读入上下文。

**记住 `interaction_id`**——如果用户提出与本研究相关的后续问题，请在下一个研究或丰富命令中使用它作为 `--previous-interaction-id`。

## 设置

如果找不到 `parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果任何 `parallel-cli research` 命令返回 `403`，请告知用户可能需要余额。提供运行 `parallel-cli balance get` 的选项，如有必要，在运行 `parallel-cli balance add <amount_cents>` 之前请求明确确认。然后重试原始研究命令。
