---
name: parallel-deep-research
description: 仅在用户明确表示需要“深度研究”、“彻底”、“全面报告”或“彻底调查”时使用。比并行网络搜索慢且昂贵。对于常规研究/查询请求，请使用并行网络搜索。支持已知先前任务交互ID的后续查询。
---

# 深入研究

研究主题：$ARGUMENTS

> 需要 `parallel-cli` ≥ 0.3.0 以支持文本输出和上下文链式操作。如果文档中缺少某个命令或选项，请检查 `parallel-cli --version` 以及该命令的 `--help`，然后根据安装指南中的特定升级说明进行操作。API、认证和输入错误并非证明 CLI 版本过旧的证据。

## 何时使用（与 parallel-web-search 的区别）

仅当用户明确要求深入/详尽研究时才使用此技能。这可能需要几分钟时间，并且成本高于快速搜索，具体取决于处理器和任务。对于普通的“研究 X”请求、快速查找或事实核查，请使用 **parallel-web-search**。

## 第一步：开始研究

选择一个描述性的输出基础目录（例如 `reports/ai-chip-market-2026`）。包含返回的运行 ID 以确保唯一性，然后在步骤 2 中使用 `-o "$FILENAME"`。保存前检查是否存在 `.json` 和 `.md` 文件。

```bash
parallel-cli research run "$ARGUMENTS" --processor pro-fast --text --no-wait --json
```

`--text` 标志指示 API 在任务完成后返回 Markdown 报告（带内联引用），而不是默认的 JSON 结构化输出。用于叙述/报告风格请求，这是大多数用户期望的“深入研究”类型。如果用户明确要求结构化 JSON 输出，请移除 `--text`。

`--text` 可选参数：传递 `--text-description "保持 1500 字以内，重点关注并购活动"` 以控制长度、格式或重点。

如果这是一个**后续任务**并且您有先前的任务的 `interaction_id`，请添加上下文链式操作。增强任务的 `taskgroup_id` 和搜索/提取的 `session_id` 不是任务交互 ID。异步增强不会返回新的交互 ID；请保留先前的任务 ID。对于零数据保留（ZDR）账户，上下文链式操作不可用，因此请在此处省略它，并明确提供所需的上下文。

```bash
parallel-cli research run "$ARGUMENTS" --processor lite-fast --text --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

这会重用先前的任务的上下文。较轻的处理器（`lite-fast` 或 `base-fast`）适合专注的后续任务；根据新问题的深度选择，而不是假设所有后续任务都很简单。

始终使用 `--no-wait` 将创建与有界轮询分开。立即保存返回的 ID。如果创建中断或其响应丢失，请不要在检查第一个任务是否创建成功之前提交替换任务。

默认情况下使用 `pro-fast` 进行探索性研究。运行 `parallel-cli research processors` 获取已安装 CLI 的处理器列表和延迟估计；这些不是截止日期。仅在明确要求且在用户批准的预算内时才选择 `ultra` 级别。请查看 [当前定价](https://parallel.ai/pricing)，而不是引用固定的成本倍数。

快速变体优先考虑速度，可能使用较少的新索引数据。标准变体可能适合对新鲜度敏感的工作，但两者都不保证所有来源都是实时获取的。在研究提示中说明相关日期或新鲜度要求，并检查返回的证据。

解析 JSON 输出以保存 `run_id`、`interaction_id` 和 `result_url`。立即告知用户：

- 深入研究已启动
- 如果可用，选择的处理器的估计延迟
- 他们可以跟踪进度的监控 URL

任务在服务器端运行；稍后可以使用保存的 `run_id` 继续轮询。

## 第二步：轮询结果

```bash
parallel-cli research poll "$RUN_ID" -o "$FILENAME" --timeout 60
```

重要：

- 保持每次轮询有界；`--timeout 60` 允许在等待期间更新进度。
- 轮询大型报告时避免使用 `--json`。`-o` 标志将完整结果保存到文件。
- 使用 `-o "$FILENAME"`：
  - `$FILENAME.json` 始终被写入（元数据 + 基础）
  - `$FILENAME.md` 仅在返回文本输出时被写入，通常使用 `--text` 请求；自动模式结果可以是 JSON 格式。
  - 对于文本，JSON 引用 `output.content_file` 相对于保存的 JSON 文件，而不是重复报告正文。
- 如果打印了执行摘要，请分享它。一些成功的输出没有摘要；不要编造一个或将其缺失视为失败。
- 除非明确使用 `--force`，否则拒绝现有输出文件。优先使用新基础；仅在打算覆盖这些文件时使用 `--force`。
- 读取实际打印的路径。在写入错误时，CLI 可能会回退到系统临时目录，并且写入可能不完整。在重试之前检查这两个位置。在呈现持久保存的报告之前，将最终报告从临时存储复制到预期的持久位置。

### 如果轮询超时或中断

超时退出 5 或中断仅结束本地等待，不一定结束服务器任务。检查保存的任务：

```bash
parallel-cli research status "$RUN_ID" --json
```

仅对挂起/运行中的任务继续相同的轮询；准确检索已完成输出并报告失败/取消或 `action_required` 状态。CLI 的轮询循环可能不识别 `action_required`，因此不要无限期地轮询该状态。仅因本地等待结束而重新创建任务。

## 响应格式

**步骤 1 之后：** 分享用于跟踪进度的监控 URL。

**步骤 2 之后：**

1. 如果打印了执行摘要，请分享；否则，说明结果已保存，并在需要时仅从检查的输出中提供简要总结。
2. 告知用户生成的文件路径：
   - 如果存在文本报告，实际的 `.md` 路径
   - 实际的 `.json` 路径，包含元数据和基础（以及 JSON 输出的结构化内容）
3. 分享 `interaction_id` 并告知用户他们可以提出基于此研究的后续问题（例如，“深入挖掘 X”或“与 Y 进行比较”）

完成后，链接保存的文件，而不是重复监控 URL。

避免将整个报告加载到上下文中。在回答请求的摘要或后续问题时，仅读取相关部分，并引用返回的来源。

**记住 `interaction_id`：** 当账户支持上下文链式操作时，使用它进行相关研究或增强的后续任务。

## 安装设置

如果找不到 `parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果缺少文档中提到的选项或命令，请识别安装方法并通过该方法进行升级：独立的 `parallel-cli update`；pipx 的 `pipx upgrade parallel-web-tools`；uv 的 `uv tool upgrade parallel-web-tools`；Homebrew 的 `brew upgrade parallel-web/tap/parallel-cli`；npm 的 `npm update -g parallel-web-cli`。在重试之前，在代理终端中检查版本和帮助信息。

对于认证或 API 错误，请检查返回的消息。`403` 可能表示权限、账户策略或计费；它并不能证明余额不足。在无需暴露凭证的情况下相关时，检查 `parallel-cli auth --json` 及其 `authenticated` 布尔值。只有计费特定错误才需要检查余额，添加资金需要明确确认。重用保存的任务 ID；不要自动重试模糊的创建。
