# 更新 CopilotKit 技能

运行以下命令从 GitHub 拉取最新的 CopilotKit 技能：

```bash
npx skills add copilotkit/CopilotKit --full-depth -y
```

这会每次都执行全新的克隆操作——无论缓存了什么内容，它总能获取到最新版本。

这个方法适用于所有工具——Claude Code、Codex、Cursor、Gemini CLI 以及其他工具。它会检测已安装的工具，并为每个工具更新技能。

命令执行完成后，请在您的工具中**启动一个新的会话**以应用更改。

## 何时建议使用此方法

- 用户表示技能的 API 名称不正确或信息已过时
- 用户报告某个 CopilotKit API 与技能说明不符
- 用户明确要求更新或刷新技能
- 新版本的 CopilotKit 已发布，技能可能已过时
