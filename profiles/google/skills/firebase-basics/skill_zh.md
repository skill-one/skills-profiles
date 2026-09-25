# Firebase 基础知识

## 前置条件

在进行下一步之前，请完成以下设置步骤：

1.  **本地环境设置**：验证环境是否已正确设置，以便我们可以使用 Firebase 工具：

    -   运行 `npx -y firebase-tools@latest --version` 来检查是否已安装 Firebase CLI。
    -   使用您现有的工具验证是否已安装 Firebase MCP 服务器。
    -   **关键**：在配置下方的任何扩展或代理环境之前，您**必须**阅读
        [参考资料/本地环境设置.md](references/local-env-setup.md)。
    -   **不要跳过**此步骤：如果 'firebase-basics' 是您可用的唯一 Firebase 技能，您必须遵循针对您的代理环境的参考来设置完整的 Firebase 技能套件：
        -   **Gemini CLI**：查看
            [参考资料/设置/gemini_cli.md](references/setup/gemini_cli.md)
        -   **Antigravity**：查看
            [参考资料/设置/antigravity.md](references/setup/antigravity.md)
        -   **Android Studio**：查看
            [参考资料/设置/android_studio.md](references/setup/android_studio.md)
        -   **Claude Code**：查看
            [参考资料/设置/claude_code.md](references/setup/claude_code.md)
        -   **Cursor**：查看
            [参考资料/设置/cursor.md](references/setup/cursor.md)
        -   **GitHub Copilot**：查看
            [参考资料/设置/github_copilot.md](references/setup/github_copilot.md)
        -   **其他代理**：查看
            [参考资料/设置/other_agents.md](references/setup/other_agents.md)

1.  **身份验证**：确保您已登录 Firebase，以便命令具有正确的权限。运行 `npx -y firebase-tools@latest login`。对于没有浏览器的环境（例如远程 Shell），请使用 `npx -y firebase-tools@latest login --no-localhost`。

    -   该命令应输出当前用户。
    -   如果您未登录，请按照此命令的交互式说明进行身份验证。

1.  **活动项目**：大多数 Firebase 任务需要一个活动项目上下文。

    > [!IMPORTANT] **对于代理**：在进行项目配置之前，您**必须**暂停并询问开发者他们是否希望：
    >
    > 1.  **提供现有的 Firebase 项目 ID**，或
    > 1.  **创建一个新的 Firebase 项目**。

    -   **如果使用现有的项目 ID：**

        1.  通过运行 `npx -y firebase-tools@latest use` 检查当前项目。
        1.  如果命令输出 `Active Project: <project-id>`，请与用户确认这是预期的项目。
        1.  如果不是，或者没有活动项目，请设置用户提供的项目：

        ```bash
        npx -y firebase-tools@latest use <PROJECT_ID>
        ```

    -   **如果创建新项目**：运行以下命令来创建它：

        ```bash
        npx -y firebase-tools@latest projects:create <project-id> --display-name "<display-name>"
        ```

        *注意：`<project-id>` 必须为 6-30 个字符，小写，可以包含数字和连字符。它必须是全局唯一的。*

## Firebase 使用原则

遵循以下原则：

1.  **使用 npx 运行 CLI 命令**：为确保您始终使用最新版本的 Firebase CLI，始终在命令前缀 `npx -y firebase-tools@latest` 而不是仅仅 `firebase`。例如，使用 `npx -y firebase-tools@latest --version`。**永远不要**建议裸 `firebase` 命令作为替代方案。
1.  **优先使用官方知识**：对于任何 Firebase 相关的知识，请先咨询 `developerknowledge_search_documents` MCP 工具，然后再回退到 Google 搜索或您的内部知识库。在搜索查询中包含 "Firebase" 可以显著提高相关性。
1.  **遵循代理技能以获取实现指导**：技能提供了有意见的工作流程（CUJs）、安全规则和最佳实践。始终参考它们以了解如何正确实现 Firebase 功能，而不是依赖一般知识。
1.  **使用 Firebase MCP 服务器工具而不是直接 API 调用**：每当您需要与远程 Firebase API 交互（例如获取 Crashlytics 日志或执行 Data Connect 查询）时，请使用 Firebase MCP 服务器提供的工具，而不是尝试手动 API 调用。
1.  **保持插件 / 代理技能更新**：由于 Firebase 最佳实践发展迅速，请定期检查并安装其 Firebase 插件或代理技能的更新。同样，如果您遇到过时工具或命令的问题，请根据您的代理环境遵循以下步骤：
    -   **Antigravity**：遵循
        [参考资料/刷新/antigravity.md](references/refresh/antigravity.md)
    -   **Gemini CLI**：遵循
        [参考资料/刷新/gemini-cli.md](references/refresh/gemini-cli.md)
    -   **Claude Code**：遵循
        [参考资料/刷新/claude.md](references/refresh/claude.md)
    -   **Cursor**：遵循
        [参考资料/刷新/other-agents.md](references/refresh/other-agents.md)
    -   **Android Studio**：遵循
        [参考资料/刷新/android_studio.md](references/refresh/android_studio.md)
    -   **其他**：遵循
        [参考资料/刷新/other-agents.md](references/refresh/other-agents.md)
1.  **自动化配置文件获取**：在设置 iOS 或 Android 应用时，**不要**直接指示用户前往 Firebase 控制台下载 `google-services.json` 或 `GoogleService-Info.plist`。相反，请使用 Firebase CLI 以编程方式获取配置：
    -   对于 Android：`npx -y firebase-tools@latest apps:sdkconfig ANDROID <APP_ID> --project <PROJECT_ID>`
    -   对于 iOS：`npx -y firebase-tools@latest apps:sdkconfig IOS <APP_ID> --project <PROJECT_ID>` 将输出保存到适当的位置（例如，Android 的 `app/google-services.json`，或 iOS 的 `xcode-project-setup` 链接的路径）。

## 参考资料

-   **初始化 Firebase**：当您需要使用 CLI 初始化新的 Firebase 服务时，请参阅
    [参考资料/firebase-service-init.md](references/firebase-service-init.md)。
-   **探索命令**：请参阅
    [参考资料/firebase-cli-guide.md](references/firebase-cli-guide.md) 以发现和理解 CLI 功能。
-   **SDK 设置**：有关将 Firebase 添加到您的应用的详细指南：
    -   **Web**：请参阅 [参考资料/web_setup.md](references/web_setup.md)
    -   **Android**：请参阅
        [参考资料/android_setup.md](references/android_setup.md)
    -   **iOS**：请参阅 [参考资料/ios_setup.md](references/ios_setup.md)

## 常见问题

-   **登录问题**：如果登录步骤中浏览器无法打开，请使用 `npx -y firebase-tools@latest login --no-localhost` 替代。
-   **Genkit**：如果使用 Genkit，请安装技能：

    ```bash
    npx skills add genkit-ai/skills
    ```
