# Lavish Editor

Lavish Editor 在浏览器中打开代理生成的 HTML，以便人类可以对其进行注释并将反馈发送回代理。
当计划、比较、图表、表格、代码视图、报告、原型或评审循环以页面形式呈现比以文本形式更清晰时，请使用它。

## 当前指南存储在 CLI 中

不要从此文件中遵循工作流、设计或剧本说明——已安装的副本会过时。从 CLI 获取当前的真实来源：

- 使用 `npx -y lavish-axi --help` 获取命令和评审循环工作流
- 使用 `npx -y lavish-axi design` 获取设计方向优先级和当前片段
- 使用 `npx -y lavish-axi playbook <id>` 获取聚焦的工件指导（`npx -y lavish-axi playbook` 列出 ID）

您不需要全局安装 lavish-axi - 使用 `npx -y lavish-axi <html-file>` 调用它。
如果 lavish-axi 输出显示以 `lavish-axi` 开头的后续命令，请作为 `npx -y lavish-axi ...` 运行它。

## 请求

$ARGUMENTS

如果上述请求非空，则用户明确调用了 `/lavish` - 获取当前 CLI 指南，然后构建该工件。
如果为空，则根据对话推断要可视化什么。
