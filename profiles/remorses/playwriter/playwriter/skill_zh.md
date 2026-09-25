## 阅读完整文档（每会话一次）

**在会话中的第一个 playwriter 命令之前，运行：**

```bash
playwriter skill # 重要！这里不要使用 | head。请阅读完整内容！
```

这将输出完整的文档，包括：

- 会话管理和超时配置
- 选择器策略（以及哪些需要避免）
- 防止超时和失败的规则
- 慢速页面和 SPAs 的最佳实践
- 上下文变量、实用函数等

**不要跳过此步骤。** 以下示例如果没有理解完整文档中的超时、选择器规则和陷阱将无法运行。您只需要每会话执行一次此操作；同一会话中的后续 playwriter 命令无需重新阅读。

**请阅读整个输出。** 不要通过 `head`、`tail` 或任何截断命令。关键规则分布在整个文档中，而不仅仅在顶部。

## 最小示例（在阅读完整文档后）

```bash
playwriter session new
playwriter -s 1 -e 'await page.goto("https://example.com")'
```

**始终使用单引号** 为 `-e` 参数。单引号可防止 bash 解释 `$`、反引号和反斜杠。在 JS 代码中使用双引号或反引号模板字面量。

如果找不到 `playwriter`，请使用 `npx playwriter@latest` 或 `bunx playwriter@latest`。
