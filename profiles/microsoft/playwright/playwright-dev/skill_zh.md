# Playwright 开发指南

请参阅 [CLAUDE.md](../../../CLAUDE.md) 了解单体仓库结构、构建/测试/校验命令以及编码规范。

## 详细指南

- [库架构](library.md) — 客户端/服务器/调度器结构、协议层、DEPS 规则
- [添加和修改 API](api.md) — 定义 API 文档、实现客户端/服务器、添加测试
- [MCP 工具和 CLI 命令](tools.md) — 添加 MCP 工具、CLI 命令、配置选项
- [供应商依赖项与打包](vendor.md) — utilsBundle、coreBundle、babelBundle；添加 npm 供应商包；DEPS.list；`check_deps`
- [更新 WebKit Safari 版本](webkit-safari-version.md) — 更新 WebKit 用户代理中的 Safari 版本字符串
- [WebView (iOS Safari) 后端](webview.md) — `webkit/webview/` 对比标准 Mobile Safari；临时目标暂停/恢复；上游与 Playwright 补丁的区别；本地 + CI 测试设置
- [跨已发布版本进行二分查找](bisect-published-versions.md) — 并行重现 npm 中的回归问题，并比较不同版本间 `node_modules/playwright/lib/` 的差异
- [仪表盘](dashboard.md) — 驱动 "playwright cli show" 命令的 UI，以及如何对其进行开发
