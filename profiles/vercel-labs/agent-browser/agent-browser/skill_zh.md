# agent-browser

面向 AI 智能体的快速浏览器自动化 CLI。通过 CDP 支持 Chrome/Chromium，提供无障碍树（accessibility-tree）快照和紧凑的 `@eN` 元素引用。

安装：`npm i -g agent-browser && agent-browser install`

## 从这里开始

该文件是一个发现占位符，并非使用指南。在运行任何 `agent-browser` 命令之前，请从 CLI 加载实际的工作流内容：

```bash
agent-browser skills get core             # 从这里开始 — 工作流、常见模式、故障排查
agent-browser skills get core --full      # 包含完整命令参考和模板
```

CLI 提供的技能内容始终与已安装版本匹配，因此指令永远不会过时。此占位符中的内容在版本发布之间不会更改，这就是它仅指向 `skills get core` 的原因。

## 专业技能

当任务超出浏览器网页范围时，加载专业技能：

```bash
agent-browser skills get electron          # Electron 桌面应用（VS Code、Slack、Discord、Figma 等）
agent-browser skills get slack             # Slack 工作区自动化
agent-browser skills get dogfood           # 探索性测试 / QA / 缺陷排查
agent-browser skills get derive-client     # 记录 HAR，为网站生成独立的 API 客户端
agent-browser skills get vercel-sandbox    # Vercel Sandbox 微虚拟机中的 agent-browser
agent-browser skills get protected-vercel-deployments  # 访问受保护的 Vercel 部署
agent-browser skills get agentcore         # AWS Bedrock AgentCore 云浏览器
```

运行 `agent-browser skills list` 以查看已安装版本上所有可用的内容。

## 为什么选择 agent-browser

- 快速的原生 Rust CLI，而非 Node.js 封装
- 支持任何 AI 智能体（Cursor、Claude Code、Codex、Continue、Windsurf 等）
- 通过 CDP 支持 Chrome/Chromium，无需 Playwright 或 Puppeteer 依赖
- 提供无障碍树快照及元素引用，确保交互可靠
- 会话管理、认证存储、状态持久化、视频录制
- 针对 Electron 应用、Slack、探索性测试、云提供商的专业技能

## 可观测性仪表盘

仪表盘在 4848 端口独立运行，且可通过代理或转发后的 URL（如 `https://dashboard.agent-browser.localhost`）打开。智能体应保持 dashboard 同源：会话标签页、状态和流式传输流量在内部进行代理，因此会话端口无需暴露。
