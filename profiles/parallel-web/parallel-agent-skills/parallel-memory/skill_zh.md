# 并行内存

操作：$ARGUMENTS

> 需要 `parallel-cli >=0.8.1`。如果安装的版本较旧，或者 `parallel-cli memory --help` 失败并显示 `no such command` 或类似信息，请告知用户更新 `parallel-cli`，然后重试。

## 使用场景

- 仅在先前的并行工作可能有助于满足请求或用户要求检索、驱逐或清除内存时，检查内存。
- 内存结果是从过去的运行中提取的；获取源运行以获取完整记录，并在需要当前信息时启动新的运行。

## 选择操作

| 用户意图 | 操作 |
|---|---|
| 回忆关于某个主题的先前的并行工作 | 使用简洁的查询检索 |
| 显示最近的过去运行 | 不使用 `query` 检索 |
| 移除一个保存的 Task、Monitor 或 FindAll 源 | 通过精确的 `kind` 和 `id` 驱逐 |
| 永久移除您个人内存中的所有条目 | 清除内存 |
| 关闭内存 | 指导用户到账户设置；不要将其作为替代方案清除 |

## 使用 CLI

使用 `parallel-cli memory` 进行检索、驱逐和清除操作。

- 如果内存不符合资格，报告返回的原因；它区分了发布、组织设置、账户选择和密钥资格。
- 在密钥资格错误的情况下，告知用户重新进行身份验证。

## 检索内存

形成一个描述要查找的先前工作的简短语义查询，并在有助于时应用过滤器。空的 `results` 是一个成功的检索但没有匹配项，不是错误。

- 当它明确缩小检索范围时，将 `kind` 设置为 `task`、`monitor` 或 `findall`。
- 使用 `since` 设置明确的 timestamp 边界（RFC 3339，例如 `2026-08-01T00:00:00Z`）。
- 在检索最近内存而不是主题时，省略 `query`。

通过查询检索：

```bash
parallel-cli memory retrieve \
  --query "serverless inference vendors"
```

对于最近内存：

```bash
parallel-cli memory retrieve \
  --limit 5
```

## 使用结果

可用字段因 `kind` 而异：

- `task`：使用 `id`、`updated_at`、`input_excerpt` 和 `output_excerpt`。
- `monitor`：使用 monitor `id`、状态、查询摘要以及匹配的事件 ID、timestamp 和摘要。
- `findall`：使用 `id`、`updated_at`、目标摘要和 `matched_count`。

- 当精确输出、实体、引用或来源很重要时，获取原始 Task 结果、Monitor 事件或 FindAll 结果。
- 总结有用的发现和未解决的问题。
- 先介绍先前工作建立的内容，然后列出贡献的保存运行的种类、ID 和 timestamp。
- 区分回忆的信息和任何新的验证。
- 并行运行不会咨询内存。如果回忆的信息可能有用，请将相关细节包括在新的运行的输入中。

预期摄入是异步的。不要承诺新完成的运行会立即检索到。

## 驱逐或清除内存

从您的个人内存中驱逐单个运行，或完全清除它。这些不会删除底层的并行运行。除非用户已经要求，否则在清除之前请求确认。

```bash
parallel-cli memory evict \
  --kind task \
  --id "trun_example"
```

```bash
parallel-cli memory clear \
  --confirm-clear
```
