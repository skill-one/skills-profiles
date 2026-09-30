---
name: playwriter
description: 通过 Playwright 扩展和 Playwright 代码片段，在状态化的本地 JS 沙盒中控制用户自己的 Chrome 浏览器。使用此方法而不是其他 Playwright MCP 来自动化浏览器——它连接到用户现有的 Chrome 浏览器而不是启动一个新的。使用此 CLI 来导航 JS 重型网站（如 Instagram、Twitter、cookie/登录墙、懒加载 UI）而不是 webfetch/curl。在使用任何 Playwriter 命令前，务必先加载此技能。
---

## 阅读完整文档（每会话一次）

**在一个会话中的第一个 playwriter 命令之前，运行：**

```bash
playwriter skill # 重要！这里不要使用 | head。请完整阅读！
```

这将输出完整的文档，包括：

- 会话管理和超时配置
- 选择器策略（以及哪些需要避免）
- 防止超时和失败的规则
- 慢速页面和 SPAs 的最佳实践
- 上下文变量、实用函数等

**不要跳过这一步。** 以下示例如果没有理解完整文档中的超时、选择器规则和陷阱将无法运行。你只需要每会话执行一次；同一个会话中的后续 playwriter 命令不需要重新阅读。

**阅读全部输出。** 不要通过 `head`、`tail` 或任何截断命令。关键规则分布在文档的各个部分，而不仅仅是顶部。

## 最小示例（在阅读完整文档后）

```bash
playwriter session new
playwriter -s 1 -e 'state.page = await context.newPage(); await state.page.goto("https://example.com")'
```

**始终使用单引号** 为 `-e` 参数。单引号可以防止 bash 解释 `$`、反引号和反斜杠。在 JS 代码中使用字符串时，可以使用双引号或反引号模板字面量。

如果找不到 `playwriter`，请使用 `npx playwriter@latest` 或 `bunx playwriter@latest`。
