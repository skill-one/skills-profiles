# Firebase AI 逻辑基础

## 概述

Firebase AI 逻辑是 Firebase 的一项产品，允许开发者使用客户端 SDK 将生成式 AI 集成到他们的移动和 Web 应用中。您可以直接从应用中调用 Gemini 模型，而无需管理专用后端。Firebase AI 逻辑，以前被称为“Firebase Vertex AI”，代表了 Google 为移动和 Web 开发者提供的 AI 集成平台的演进。

它支持两个 Gemini API 提供商：

-   **Gemini 开发者 API**：它具有适合原型设计的免费层级，以及适合生产的按量付费模式
-   **代理平台 Gemini API**（以前品牌为 Vertex AI）：适合企业级生产就绪的可扩展性，需要 Blaze 计划

默认使用 Gemini 开发者 API，如果应用需要，则仅使用代理平台 Gemini API（以前品牌为 Vertex AI）。

## 设置与初始化

### 前置条件

-   在开始之前，确保您已安装 **Node.js 16+** 和 npm。如果尚未安装，请安装它们。
-   在开始之前，确定用户感兴趣的平台：Android、iOS、Flutter 或 Web。
-   如果他们的平台不受支持，请将用户引导至 Firebase 文档，了解如何为他们的应用设置 AI 逻辑（与用户分享此链接 https://firebase.google.com/docs/ai-logic/get-started）

### 安装

库是标准 Firebase Web SDK 的一部分。

`npm install firebase@latest`

如果您在 firebase 目录（带有 firebase.json）中，可以使用此命令将当前选定的项目标记为“current”：

`npx -y firebase-tools@latest projects:list`

确保当前项目至少有一个关联的应用

`npx -y firebase-tools@latest apps:list`

使用 init 命令初始化 AI 逻辑 SDK

`npx -y firebase-tools@latest init ailogic`

这将自动在 Firebase 控制台中启用 Gemini 开发者 API。

更多信息在
[Firebase AI 逻辑入门](https://firebase.google.com/docs/ai-logic/get-started.md.txt)

## 核心功能

> [!WARNING] **关键：使用当前模型名称**：始终检查
> [Firebase AI 逻辑模型文档](https://firebase.google.com/docs/ai-logic/models.md.txt)
> 以获取当前支持的模型名称。**不要**使用 `gemini-2.0-pro` 或
> `gemini-2.0-flash` 或其他已停用的旧模型。

### 仅文本生成

### 多模态（文本 + 图像/音频/视频/PDF 输入）

Firebase AI 逻辑允许 Gemini 模型直接从您的应用中分析图像文件。这可以实现创建标题、回答有关图像的问题、检测对象和分类图像等功能。除了图像，Gemini 还可以通过将其作为内联数据传递并附带其 MIME 类型来分析其他媒体类型，如音频、视频和 PDF。对于大于 20 兆字节的文件（作为内联数据可能导致 HTTP 413 错误），请将它们存储在 Firebase Cloud Storage 中，并将它们的 URL 传递给 Gemini 开发者 API。

### 聊天会话（多轮）

使用 `startChat` 自动维护历史记录。

### 流式传输响应

为了通过显示部分结果（如打字效果）来改善用户体验，请使用 `generateContentStream` 而不是 `generateContent` 以更快地显示结果。

### 使用 Nano Banana 生成图像

> [!WARNING] **使用当前图像模型名称**：始终检查
> [Firebase AI 逻辑模型文档](https://firebase.google.com/docs/ai-logic/models.md.txt)
> 以获取当前支持的图像生成（Nano Banana）模型名称。

-   需要升级到 Blaze 按量付费计费计划。

### 使用内置的 googleSearch 工具进行搜索基础

## 支持的平台和框架

支持的平台和框架包括 Android 的 Kotlin 和 Java、iOS 的 Swift、Web 应用的 JavaScript、Flutter 的 Dart 和 Unity 的 C Sharp。

## 高级功能

### 结构化输出（JSON）

为响应强制执行特定的 JSON 模式。

### 设备端 AI（混合）

Web 应用的混合设备端推理，其中 Firebase Javascript SDK 会自动检查 Gemini Nano 的可用性（安装后）并在设备端或云端托管提示执行之间切换。这需要在 Chrome 浏览器中启用模型使用，更多信息在
[混合设备端推理文档](https://firebase.google.com/docs/ai-logic/hybrid-on-device-inference.md.txt)。

## 安全与生产

### App Check

> [!WARNING] **关键安全要求**：为了安全地使用 AI 逻辑，您**必须**在您的应用上设置 App Check。这可以防止未经授权的客户使用您的 API 配额并访问您的后端资源。

参见
[使用 reCAPTCHA Enterprise 设置 App Check](https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider.md.txt)
以获取设置说明。

#### App Check 调试令牌用于本地开发 & CI/CD

由于 App Check 证明提供者（如 Play Integrity 或 DeviceCheck）会拒绝模拟器、模拟器或 CI 环境，因此您在开发和测试期间必须使用 **App Check 调试令牌**来绕过标准证明。

##### 本地开发（自动生成）

1.  将您的代码的 App Check 提供者配置为使用调试工厂：
    *   **Web**：在初始化 App Check 之前设置 `self.FIREBASE_APPCHECK_DEBUG_TOKEN = true;`。
    *   **Android**：安装 `DebugAppCheckProviderFactory.getInstance()`。
    *   **iOS**：将提供者工厂设置为 `AppCheckDebugProviderFactory()`。
2.  在模拟器/localhost 中运行您的应用。
3.  查看您的运行时调试控制台/Logcat 日志以获取生成的 UUID：
    *   *示例*：`AppCheck debug token: "123a4567-b89c-12d3-e456-789012345678"`
4.  在 Firebase 控制台下的 **安全 > App Check > 应用 > 管理调试令牌** 中注册此令牌。

##### CI/CD 管道（预配置）

1.  在 Firebase 控制台下的 **安全 > App Check > 应用 > 管理调试令牌** 中生成并注册一个新的调试令牌。
2.  将此令牌字符串作为加密密钥添加到您的 CI 系统中（例如 `APP_CHECK_DEBUG_TOKEN`）。
3.  配置您的构建以在测试执行期间将此密钥作为环境变量传递给 SDK（例如 `self.FIREBASE_APPCHECK_DEBUG_TOKEN = process.env.APP_CHECK_DEBUG_TOKEN`）。

### 远程配置

考虑您不需要将模型名称（例如特定的模型版本字符串）硬编码。使用 Firebase 远程配置动态更新模型版本，而无需部署新的客户端代码。参见
[远程更改模型名称](https://firebase.google.com/docs/ai-logic/change-model-name-remotely.md.txt)

> [!WARNING] **关键：后端配置要求** 对于所有平台（Flutter、Android、iOS、Web），您**必须**运行 `npx firebase-tools init ailogic`
> 以配置服务。`flutterfire configure` 仅处理客户端配置，**不会**启用 AI 服务，会导致 `PERMISSION_DENIED` 错误。

## 初始化代码参考

-   **Web 模块化 API**
    -   提供商：Gemini 开发者 API
    -   参考：[usage_patterns_web.md](references/usage_patterns_web.md)
-   **Android (Kotlin)**
    -   提供商：Gemini 开发者 API
    -   参考：[usage_patterns_android.md](references/usage_patterns_android.md)
-   **iOS (Swift)**
    -   提供商：Gemini 开发者 API
    -   参考：[ios_setup.md](references/ios_setup.md)
-   **Flutter (Dart)**
    -   提供商：Gemini 开发者 API
    -   参考：[flutter_setup.md](references/flutter_setup.md)

> [!WARNING] **关键：使用当前模型名称**：始终检查
> [Firebase AI 逻辑模型文档](https://firebase.google.com/docs/ai-logic/models.md.txt)
> 以获取当前支持的模型名称。**不要**使用 `gemini-2.0-pro` 或
> `gemini-2.0-flash` 或其他已停用的旧模型。

## 参考

[Web SDK 代码示例和使用模式](references/usage_patterns_web.md)
[iOS SDK 代码示例和使用模式](references/ios_setup.md)
[Flutter SDK 代码示例和使用模式](references/flutter_setup.md)

[Android (Kotlin) SDK 使用模式](references/usage_patterns_android.md)
