# 前置条件

在继续操作之前，请完成以下设置步骤：

1. **本地环境配置：** 请核实环境已正确设置，以便我们使用 Firebase 工具：

   - 运行 `npx -y firebase-tools@latest --version` 检查 Firebase CLI 是否已安装。
   - 使用现有工具核实 Firebase MCP 服务器是否已安装。
   - **关键**：在进行以下任何扩展或代理环境配置之前，您**必须**阅读
     [references/local-env-setup.md](references/local-env-setup.md)。
   - **切勿跳过**此步骤：如果“firebase-basics”是您唯一可用的 Firebase 技能，您必须根据代理环境参考文档设置完整的 Firebase 技能套件：
     - **Gemini CLI**：查阅
       [references/setup/gemini_cli.md](references/setup/gemini_cli.md)
     - **Antigravity**：查阅
       [references/setup/antigravity.md](references/setup/antigravity.md)
     - **Android Studio**：查阅
       [references/setup/android_studio.md](references/setup/android_studio.md)
     - **Claude Code**：查阅
       [references/setup/claude_code.md](references/setup/claude_code.md)
     - **Cursor**：查阅
       [references/setup/cursor.md](references/setup/cursor.md)
     - **GitHub Copilot**：查阅
       [references/setup/github_copilot.md](references/setup/github_copilot.md)
     - **其他代理**：查阅
       [references/setup/other_agents.md](references/setup/other_agents.md)

1. **认证：** 请确保已登录 Firebase，以便命令具有正确的权限。运行 `npx -y firebase-tools@latest login`。对于没有浏览器的环境（例如远程 shell），请使用
   `npx -y firebase-tools@latest login --no-localhost`。

   - 命令应输出当前用户。
   - 如果您未登录，请遵循该命令提供的交互式说明进行认证。

1. **活跃项目：** 大多数 Firebase 任务需要活跃的项目上下文。

   > [!重要] **针对代理：** 在进行项目配置之前，您**必须**暂停并询问开发者，他们倾向于：
   >
   > 1. **提供现有的 Firebase 项目 ID**，或
   > 1. **创建新的 Firebase 项目**。

   - **如果使用现有的项目 ID：**

     1. 通过运行 `npx -y firebase-tools@latest use` 检查当前项目。
     1. 如果命令输出 `Active Project: <project-id>`，请确认这是否是预期的项目。
     1. 如果不是，或者没有项目处于激活状态，请设置用户提供的项目：
        
        ```bash
        npx -y firebase-tools@latest use <PROJECT_ID>
        ```

   - **如果创建新项目：** 运行以下命令以创建它：

     ```bash
     npx -y firebase-tools@latest projects:create <project-id> --display-name "<display-name>"
     ```

     *注意：`<project-id>` 必须为 6 至 30 个字符，小写，可包含数字和连字符。它必须全局唯一。*

# Firebase 使用原则

请遵守以下原则：

1. **使用 npx 执行 CLI 命令：** 为确保始终使用 Firebase CLI 的最新版本，请始终在命令前加上 `npx -y firebase-tools@latest`，而不是仅使用 `firebase`。例如，使用 `npx -y firebase-tools@latest --version`。**切勿**将裸露的 `firebase` 命令作为替代方案提出。
1. **优先使用官方知识：** 对于任何 Firebase 相关知识，在回退到 Google 搜索或内部知识库之前，请先查阅 `developerknowledge_search_documents` MCP 工具。在搜索查询中包含“Firebase”能显著提高相关性。
1. **遵循代理技能获取实现指导：** 技能提供带有指导性的工作流（CUJs）、安全规则和最佳实践。始终查阅这些技能以理解如何正确实现 Firebase 功能，而不是依赖通用知识。
1. **使用 Firebase MCP 服务器工具，而非直接 API 调用：**  whenever 您需要与远程 Firebase API 交互（例如获取 Crashlytics 日志或执行 Data Connect 查询），请使用 Firebase MCP 服务器提供的工具，而非尝试手动 API 调用。
1. **保持插件 / 代理技能更新：** 由于 Firebase 最佳实践演进迅速，请定期检查并安装其 Firebase 插件或代理技能的更新。同样，如果您遇到工具或命令过时的问题，请根据您的代理环境遵循以下步骤：
   - **Antigravity**：遵循
     [references/refresh/antigravity.md](references/refresh/antigravity.md)
   - **Gemini CLI**：遵循
     [references/refresh/gemini-cli.md](references/refresh/gemini-cli.md)
   - **Claude Code**：遵循
     [references/refresh/claude.md](references/refresh/claude.md)
   - **Cursor**：遵循
     [references/refresh/other-agents.md](references/refresh/other-agents.md)
   - **Android Studio**：遵循
     [references/refresh/android_studio.md](references/refresh/android_studio.md)
   - **其他**：遵循
     [references/refresh/other-agents.md](references/refresh/other-agents.md)
1. **自动化配置文件获取：** 在设置 iOS 或 Android 应用时，**切勿**直接引导用户到 Firebase 控制台下载 `google-services.json` 或 `GoogleService-Info.plist`。相反，请使用 Firebase CLI 程序化获取配置：
   - **Android**：
     `npx -y firebase-tools@latest apps:sdkconfig ANDROID <APP_ID> --project <PROJECT_ID>`
   - **iOS**：
     `npx -y firebase-tools@latest apps:sdkconfig IOS <APP_ID> --project <PROJECT_ID>`
     将输出保存至适当位置（例如，Android 的 `app/google-services.json`，或 iOS 中 `xcode-project-setup` 链接的路径）。

# 参考资料

- **初始化 Firebase：** 当您需要使用 CLI 初始化新的 Firebase 服务时，请参阅
  [references/firebase-service-init.md](references/firebase-service-init.md)。
- **探索命令：** 请参阅
  [references/firebase-cli-guide.md](references/firebase-cli-guide.md)，以发现并理解 CLI 功能。
- **SDK 设置：** 获取向您的应用添加 Firebase 的详细指南：
  - **Web**：参阅 [references/web_setup.md](references/web_setup.md)
  - **Android**：参阅 [references/android_setup.md](references/android_setup.md)
  - **iOS**：参阅 [references/ios_setup.md](references/ios_setup.md)

# 常见问题

- **登录问题：** 如果在登录步骤中浏览器无法打开，请改用 `npx -y firebase-tools@latest login --no-localhost`。
- **Genkit：** 如果使用 Genkit，请安装以下技能：
  
  ```bash
  npx skills add genkit-ai/skills
  ```
