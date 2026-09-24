# Firebase AI Logic 基础

## 概览

Firebase AI Logic 是 Firebase 的产品，允许开发者使用客户端 SDK 将生成式 AI 添加到他们的移动和网页应用中。您可以在应用内直接调用 Gemini 模型，无需管理专用的后端。Firebase AI Logic 以前被称为“Vertex AI for Firebase”，代表了 Google 为移动和网页开发者打造的 AI 集成平台的演进。

它支持两种 Gemini API 提供商：

- **Gemini Developer API**：提供适合原型制作的免费层级，以及用于生产的按量付费模式
- **Agent Platform Gemini API**（以前品牌为 Vertex AI）：适合规模化扩展，具备企业级生产就绪能力，需要 Blaze 计划

请使用 Gemini Developer API 作为默认，仅在应用需要时才使用 Agent Platform Gemini API（以前品牌为 Vertex AI）。

## 配置与初始化

### 前置条件

- 在开始之前，请确保已安装 **Node.js 16+** 和 npm。如果尚未安装，请进行安装。
- 在开始之前，确定用户感兴趣的平台：Android、iOS、Flutter 或 Web。
- 如果平台不受支持，请引导用户查阅 Firebase 文档以了解如何为应用配置 AI Logic（向用户分享此链接 https://firebase.google.com/docs/ai-logic/get-started）

### 安装

该库是标准 Firebase Web SDK 的一部分。

`npm install firebase@latest`

如果位于包含 `firebase.json` 的 firebase 目录中，可以使用此命令将当前选定的项目标记为“current”：

`npx -y firebase-tools@latest projects:list`

确保当前项目至少关联一个应用

`npx -y firebase-tools@latest apps:list`

使用 init 命令初始化 AI Logic SDK

`npx -y firebase-tools@latest init ailogic`

这将自动在 Firebase 控制台中启用 Gemini Developer API。

更多信息，请参阅 [Firebase AI Logic 入门](https://firebase.google.com/docs/ai-logic/get-started.md.txt)

## 核心能力

> [!WARNING] **CRITICAL: 使用当前模型名称：** 始终检查 [Firebase AI Logic 模型文档](https://firebase.google.com/docs/ai-logic/models.md.txt) 中当前支持的模型名称。请勿使用 `gemini-2.0-pro` 或 `gemini-2.0-flash` 或其他已停止服务的旧模型。

### 仅文本生成

### 多模态（文本 + 图片/音频/视频/PDF 输入）

Firebase AI Logic 允许 Gemini 模型直接从应用中分析图像文件，支持创建字幕、回答关于图像的问题、检测物体以及分类图像等功能。除了图像，Gemini 还可以通过附带 MIME 类型的内联数据来分析音频、视频和 PDF 等其他媒体类型。对于超过 20 兆字节的文件（如果以内联数据形式传递可能会引发 HTTP 413 错误），请将其存储到 Firebase Cloud Storage 中，然后将 URL 传递给 Gemini Developer API。

### 聊天会话（多轮）

使用 `startChat` 自动维护历史记录。

### 流式响应

为改善用户体验，在结果到达时显示部分结果（类似打字效果），请使用 `generateContentStream` 代替 `generateContent` 以加快结果展示。

### 使用 Nano Banana 生成图像

> [!WARNING] **使用当前图像模型名称：** 始终检查 [Firebase AI Logic 模型文档](https://firebase.google.com/docs/ai-logic/models.md.txt) 中当前支持的图像生成（Nano Banana）模型名称。

-   需要升级 Blaze 按量付费计费计划。

### 使用内置的 googleSearch 工具进行搜索 grounding

## 支持的平台和框架

支持的平台和框架包括：Android 上的 Kotlin 和 Java、iOS 上的 Swift、网页应用上的 JavaScript、Flutter 上的 Dart 以及 Unity 上的 C Sharp。

## 高级功能

### 结构化输出（JSON）

为响应强制使用特定的 JSON schema。

### 端侧 AI（混合）

网页应用支持混合端侧推理，其中 Firebase Javascript SDK 在安装后会自动检查 Gemini Nano 的可用性，并在端侧执行或云端托管的提示执行之间切换。这需要在 Chrome 浏览器中启用模型使用，需要特定步骤，更多信息，请参阅 [混合端侧推理文档](https://firebase.google.com/docs/ai-logic/hybrid-on-device-inference.md.txt)。

## 安全与生产

### App Check

> [!WARNING] **关键安全要求：** 为了安全使用 AI Logic，您必须在应用中设置 App Check。这可以防止未授权客户端使用您的 API 配额并访问您的后端资源。

设置说明请参阅 [使用 reCAPTCHA Enterprise 的 App Check](https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider.md.txt)。

#### 用于本地开发与 CI/CD 的 App Check 调试令牌

因为 App Check 认证提供程序（如 Play Integrity 或 DeviceCheck）会拒绝模拟器、测试器和 CI 环境，因此您在开发和测试期间必须使用 **App Check 调试令牌** 以绕过标准认证。

##### 本地开发（自动生成）

1.  配置代码的 App Check 提供程序以使用调试工厂：
    *   **Web**：在初始化 App Check 之前设置 `self.FIREBASE_APPCHECK_DEBUG_TOKEN = true;`
    *   **Android**：安装 `DebugAppCheckProviderFactory.getInstance()`。
    *   **iOS**：将提供程序工厂设置为 `AppCheckDebugProviderFactory()`。
2.  在模拟器/本地主机中运行您的应用。
3.  查看运行时的调试器控制台/Logcat 日志，以获取生成的 UUID：
    *   *示例：* `AppCheck debug token:
        "123a4567-b89c-12d3-e456-789012345678"`
4.  在 Firebase 控制台的 **安全 > App Check > 应用 > 管理调试令牌** 下注册该令牌。

##### CI/CD 流水线（预配置）

1.  在 Firebase 控制台的 **安全 > App Check > 应用 > 管理调试令牌** 下生成并注册一个新的调试令牌。
2.  将该令牌字符串作为加密的秘密信息添加到您的 CI 系统中（例如 `APP_CHECK_DEBUG_TOKEN`）。
3.  配置您的构建在测试执行期间将该秘密作为环境变量传递给 SDK（例如 `self.FIREBASE_APPCHECK_DEBUG_TOKEN = process.env.APP_CHECK_DEBUG_TOKEN`）。

### 远程配置

请注意，您无需硬编码模型名称（例如特定模型版本字符串）。使用 Firebase 远程配置动态更新模型版本，而无需部署新的客户端代码。请参阅 [远程更改模型名称](https://firebase.google.com/docs/ai-logic/change-model-name-remotely.md.txt)

> [!WARNING] **CRITICAL: 后端配置必需** 对于所有平台（Flutter、Android、iOS、Web），您必须运行 `npx firebase-tools init ailogic` 来配置服务。`flutterfire configure` 仅处理客户端配置，不会启用 AI 服务，会导致 `PERMISSION_DENIED` 错误。

## 初始化代码引用

-   **Web 模块化 API**
    -   提供商：Gemini Developer API
    -   参考：[usage_patterns_web.md](references/usage_patterns_web.md)
-   **Android (Kotlin)**
    -   提供商：Gemini Developer API
    -   参考：[usage_patterns_android.md](references/usage_patterns_android.md)
-   **iOS (Swift)**
    -   提供商：Gemini Developer API
    -   参考：[ios_setup.md](references/ios_setup.md)
-   **Flutter (Dart)**
    -   提供商：Gemini Developer API
    -   参考：[flutter_setup.md](references/flutter_setup.md)

> [!WARNING] **CRITICAL: 使用当前模型名称：** 始终检查 [Firebase AI Logic 模型文档](https://firebase.google.com/docs/ai-logic/models.md.txt) 中当前支持的模型名称。请勿使用 `gemini-2.0-pro` 或 `gemini-2.0-flash` 或其他已停止服务的旧模型。

## 参考资料

[Web SDK 代码示例和用法模式](references/usage_patterns_web.md)
[iOS SDK 代码示例和用法模式](references/ios_setup.md)
[Flutter SDK 代码示例和用法模式](references/flutter_setup.md)

[Android (Kotlin) SDK 用法模式](references/usage_patterns_android.md)
