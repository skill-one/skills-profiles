# agent-browser

为 AI 代理提供的快速浏览器自动化 CLI 工具。通过 CDP 连接 Chrome/Chromium，并使用可访问性树快照和紧凑的 `@eN` 元素引用。

安装：`npm i -g agent-browser && agent-browser install`

## 入口指南

此文件是一个发现占位符，不是使用指南。在运行任何 `agent-browser` 命令之前，请从 CLI 加载实际的工作流内容：

```bash
agent-browser skills get core             # 从这里开始 — 工作流、常见模式、故障排除
agent-browser skills get core --full      # 包含完整的命令参考和模板
```

CLI 提供的技能内容始终与安装版本匹配，因此说明永远不会过时。此占位符中的内容在版本发布之间无法更改，这就是它只指向 `skills get core` 的原因。

## 专业技能

当任务超出浏览器网页范围时，加载专业技能：

```bash
agent-browser skills get electron          # Electron 桌面应用 (VS Code, Slack, Discord, Figma, ...)
agent-browser skills get slack             # Slack 工作空间自动化
agent-browser skills get dogfood           # 探索性测试 / QA / 缺陷搜索
agent-browser skills get derive-client     # 录制 HAR，为网站生成独立的 API 客户端
agent-browser skills get vercel-sandbox    # agent-browser 在 Vercel Sandbox 微 VM 中运行
agent-browser skills get protected-vercel-deployments  # 访问受保护的 Vercel 部署
agent-browser skills get agentcore         # AWS Bedrock AgentCore 云浏览器
```

运行 `agent-browser skills list` 查看安装版本上所有可用的技能。

## 为什么选择 agent-browser

- 快速的原生 Rust CLI，不是 Node.js 封装
- 可与任何 AI 代理（Cursor、Claude Code、Codex、Continue、Windsurf 等）配合使用
- 通过 CDP 连接 Chrome/Chromium，无需 Playwright 或 Puppeteer 依赖
- 可访问性树快照和元素引用，用于可靠交互
- 会话、认证保险库、状态持久化、视频录制
- 适用于 Electron 应用、Slack、探索性测试、云提供商的专业技能

## 可观察性仪表盘

仪表盘独立于浏览器会话在端口 4848 上运行，也可以通过代理或转发 URL（如 `https://dashboard.agent-browser.localhost`）打开。代理应保持在仪表盘原点：会话标签、状态和流交通量在内部被代理，因此会话端口无需暴露。
