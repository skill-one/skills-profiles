# Firebase 本地环境配置

本指南记录了为代理设置完整 Firebase 体验所需的最基本配置。在开始使用任何 Firebase 功能之前，你必须验证以下每个步骤是否已全部完成。

## 1. 验证 Node.js
- **操作**：运行 `node --version`。
- **处理**：确保已安装 Node.js 且版本为 `>= 20`。如果 Node.js 未安装或 `< v20`，请根据操作系统进行安装：

  **推荐：使用 Node 版本管理器**
  这可以避免安装全局包时出现的权限问题。

  **对于 macOS 或 Linux：**
  1. 指导用户到 [官方 nvm 仓库](https://github.com/nvm-sh/nvm#installing-and-updating)。
  2. 要求用户手动安装 `nvm` 并在完成后回复。**停止并等待**用户的确认。
  3. 通过源代码使当前终端会话中可用 `nvm`：
     ```bash
     # 对于 Bash
     source ~/.bash_profile
     source ~/.bashrc

     # 对于 Zsh
     source ~/.zprofile
     source ~/.zshrc
     ```
  4. 安装 Node.js：
     ```bash
     nvm install 24
     nvm use 24
     ```

  **对于 Windows：**
  1. 指导用户下载并安装 [nvm-windows](https://github.com/coreybutler/nvm-windows/releases)。
  2. 要求用户手动安装 `nvm-windows` 和 Node.js，并在完成后回复。**停止并等待**用户的确认。
  3. 用户确认后，验证 Node.js 是否可用：
     ```bash
     node --version
     ```

  **替代方案：官方安装程序**
  1. 指导用户从 [nodejs.org](https://nodejs.org/en/download) 下载并安装 LTS 版本。
  2. 要求用户手动安装 Node.js 并在完成后回复。**停止并等待**用户的确认。

## 2. 验证 Firebase CLI
Firebase CLI 是与 Firebase 服务交互的主要工具。
- **操作**：运行 `npx -y firebase-tools@latest --version`。
- **处理**：确保该命令成功运行并输出版本号。

## 3. 验证 Firebase 身份验证
你必须进行身份验证才能管理 Firebase 项目。
- **操作**：运行 `npx -y firebase-tools@latest login`。
- **处理**：如果环境是远程或受限（无法访问浏览器），请运行 `npx -y firebase-tools@latest login --no-localhost`。

## 4. 安装代理技能和 MCP 服务器
要完全管理 Firebase，代理需要安装特定的技能和 Firebase MCP 服务器。识别你当前正在运行的代理环境，并严格遵循相应的配置文档。

**阅读你当前代理的配置文档：**
- **Gemini CLI**：查阅 [references/gemini_cli.md](references/gemini_cli.md)
- **Antigravity**：查阅 [references/antigravity.md](references/antigravity.md)
- **Claude Code**：查阅 [references/claude_code.md](references/claude_code.md)
- **Cursor**：查阅 [references/cursor.md](references/cursor.md)
- **GitHub Copilot**：查阅 [references/github_copilot.md](references/github_copilot.md)
- **其他代理**（Windsurf、Cline 等）：查阅 [references/other_agents.md](references/other_agents.md)

---
**关键代理规则**：在以上所有步骤全部成功验证并完成后，才可进行任何其他 Firebase 任务。
