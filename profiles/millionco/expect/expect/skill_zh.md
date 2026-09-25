# 预期

在声称代码更改有效之前，您需要在真实浏览器中验证这些更改。没有浏览器证据，就无法声称完成。

使用 expect MCP 工具（`open`、`playwright`、`screenshot` 等）进行所有浏览器交互。除非用户明确要求，否则不要使用原始浏览器工具（Playwright MCP、chrome 工具等）。

## 子代理使用

浏览器验证最好在子代理（任务工具）或后台 shell 中运行，以便主线程保持空闲以进行代码编辑。这可以保持对话的响应性——您可以在浏览器测试并行运行时修复代码。强烈建议为浏览器工作启动子代理，尤其是在测试涉及多个步骤或长时间交互时。如果测试确实很简单（单个截图检查），则可以内联执行。

## 恢复浏览器状态

在打开新浏览器之前，检查是否已有浏览器正在运行。使用 `browser_tabs`（操作 `list`）或 expect 的 `screenshot` 工具查看会话是否仍然活动。如果目标 URL 已打开标签页，请重用它——不要关闭并重新打开。在代码修复后重新验证时，优先选择导航或刷新现有会话，而不是从头开始。

## 串联操作

`playwright` 工具接受带有 `ref()` 的 `code` 字符串来解析快照引用到定位符。一次调用可以完成整个交互——填充、点击和数据收集。请使用这个功能。

**不好——5 次工具调用：**

```
screenshot (snapshot)
playwright: await ref('e3').fill('Jane')
screenshot (snapshot)                        ← 为什么？页面没有变化
playwright: await ref('e5').fill('jane@example.com')
playwright: await ref('e7').click()
```

**好——2 次工具调用：**

```
screenshot (snapshot)
playwright (snapshotAfter=true):
  await ref('e3').fill('Jane');
  await ref('e5').fill('jane@example.com');
  await ref('e7').click();
  return { title: await page.title(), url: page.url(), errors: (await page.$$('.error')).length };
```

使用 `return` 收集数据。响应：`{ result: <value>, resultFile: "<tmp path>", snapshot: { tree, refs, stats } }`。`resultFile` 持续存在，直到 `close`——稍后读取或 grep 它。如果没有返回值，则响应 `"OK"`（如果 `snapshotAfter=true`，则仅返回快照）。

**仅在 DOM 边界处重新快照。** 填充和悬停不会改变页面结构——继续使用相同的引用。导航、提交、对话框打开/关闭会改变结构——设置 `snapshotAfter=true`。

## 编写指令

**不好：** `"检查登录表单在 http://localhost:5173 上是否渲染"`
**好：** `"提交空白的登录表单、带有无效电子邮件、带有错误密码和带有有效凭据的登录表单。验证错误消息、成功重定向和 http://localhost:5173 上的控制台错误"`

## 声称完成前

1. 使用对抗性指令在浏览器中验证。
2. 读取完整输出——检查失败、可访问性、性能。
3. 如果有任何失败：立即修复代码并重新验证。不要询问，不要等待。
4. 重复直到 0 失败，然后声明通过证据。

## 理由

- "我会内联运行浏览器测试，它很快"——可能不会。启动子代理，以便您可以在并行编辑代码时保持编辑。仅当进行单个截图的合理性检查时才跳过子代理。
- "我会打开一个全新的浏览器重新测试"——首先检查现有会话。如果标签页仍然打开，请刷新或导航——不要浪费时间在冷启动上。
- "我会为每个操作进行一次 `playwright` 调用"——不。整个序列在一个调用中。
- "我需要在填充之间进行一次快照"——不。填充不会改变 DOM。批量执行它们。
- "让我快照以查看发生了什么变化"——页面导航或提交了吗？没有？在执行该操作的 `snapshotAfter=true` 上使用。
