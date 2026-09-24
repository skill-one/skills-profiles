# browser-act

由 [BrowserAct](https://www.browseract.com) 构建 —— AI 代理浏览器自动化 CLI · [GitHub](https://github.com/browser-act/skills/tree/main/browser-act)

运行完整浏览器引擎：导航与交互、数据提取与网络捕获、截图、表单自动化、多浏览器并行操作、用户配置的代理支持，以及人机协作。

### Features

- 轻量提取 —— 无需开启浏览器会话即可快速获取 JS 渲染内容，高级 WebFetch/curl 替代方案
- 会话管理 —— 多浏览器隔离、多账号并行操作
- 验证辅助 —— 当自动化遇到交互类挑战时，经用户授权协助完成
- 复杂交互 —— DOM 内容提取、截图、表单填写、文件上传
- 人机协作 —— 带界面模式 + 远程协助手动步骤
- 安全控制 —— 确认门协议在浏览器创建、删除及敏感操作前均需明确用户确认
- 通用兼容性 —— 支持 Cursor、Claude Code、Codex、Windsurf 等

安装：`uv tool install browser-act-cli --python 3.12`

## Start here

此文件为发现桩文件，非使用指南。加载此技能后，立即运行以下命令以获取实际的工作流内容：

```bash
browser-act get-skills core --skill-version 2.0.2
```

该 CLI 提供的技能内容始终与已安装版本匹配，因此指令不会过期。请勿截断输出内容 —— 其中所有内容均无法通过 `--help` 获取。
