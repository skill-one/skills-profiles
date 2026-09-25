# Firebase AI 逻辑基础

## 概述

Firebase AI 逻辑是 Firebase 的一项产品，允许开发者通过客户端 SDK 将生成式 AI 添加到他们的移动和 Web 应用中。您可以直接从应用中调用 Gemini 模型，而无需管理专用后端。Firebase AI 逻辑，以前被称为“Vertex AI for Firebase”，代表了 Google 为移动和 Web 开发者提供的 AI 集成平台的演进。

它支持两个 Gemini API 提供商：
- **Gemini 开发者 API**：具有适合原型设计的免费层级，以及按量付费的生产环境
- **Vertex AI Gemini API**：适合企业级生产就绪的扩展，需要 Blaze 计划

默认使用 Gemini 开发者 API，如果应用需要，才使用 Vertex AI Gemini API。

## 设置与初始化

### 前置条件

- 在开始之前，确保您已安装 **Node.js 16+** 和 npm。如果尚未安装，请安装它们。
- 在开始之前，确定用户感兴趣的平台：Android、iOS、Flutter 或 Web。
- 如果他们的平台不受支持，请将用户引导至 Firebase 文档，了解如何为他们的应用设置 AI 逻辑（与用户分享此链接 https://firebase.google.com/docs/ai-logic/get-started）

### 安装

库是标准 Firebase Web SDK 的一部分。

`npm install -g firebase@latest`

如果您在 firebase 目录（带有 firebase.json）中，可以使用此命令将当前选定的项目标记为“current”：

`npx -y firebase-tools@latest projects:list`

确保当前项目至少有一个关联的应用

`npx -y firebase-tools@latest apps:list`

使用 init 命令初始化 AI 逻辑 SDK

`npx -y firebase-tools@latest init # 选择 AI 逻辑`

这将自动在 Firebase 控制台中启用 Gemini 开发者 API。

更多信息在 [Firebase AI 逻辑入门](https://firebase.google.com/docs/ai-logic/get-started.md.txt)

## 核心功能

### 文本生成

### 多模态（文本 + 图像/音频/视频/PDF 输入）

Firebase AI 逻辑允许 Gemini 模型直接从您的应用中分析图像文件。这支持创建标题、回答有关图像的问题、检测对象和分类图像等功能。除了图像，Gemini 还可以通过传递其 MIME 类型作为内联数据来分析其他媒体类型，如音频、视频和 PDF。对于大于 20 兆字节的文件（作为内联数据可能导致 HTTP 413 错误），请将它们存储在 Firebase Cloud Storage 中，并将它们的 URL 传递给 Gemini 开发者 API。

### 聊天会话（多轮）

使用 `startChat` 自动维护历史记录。

### 流式响应

为了通过显示部分结果来改善用户体验（例如打字效果），使用 `generateContentStream` 而不是 `generateContent` 以更快地显示结果。

### 使用 Nano Banana 生成图像

- 对于大多数用例，从 Gemini 开始，对于需要特定图像质量和特定风格的特殊任务，选择 Imagen。（示例：gemini-2.5-flash-image）
- 需要升级到 Blaze 按量付费计费计划。

### 使用内置的 googleSearch 工具进行搜索基础

## 支持的平台和框架

支持的平台和框架包括 Android 的 Kotlin 和 Java、iOS 的 Swift、Web 应用的 JavaScript、Flutter 的 Dart 和 Unity 的 C Sharp。

## 高级功能

### 结构化输出（JSON）

强制执行特定的 JSON 模式作为响应。

### 设备端 AI（混合）

Web 应用的混合设备推理，其中 Firebase Javascript SDK 会自动检查 Gemini Nano 的可用性（安装后）并在设备端或云端托管提示执行之间切换。这需要在 Chrome 浏览器中启用模型使用，更多信息在 [混合设备推理文档](https://firebase.google.com/docs/ai-logic/hybrid-on-device-inference.md.txt)。

## 安全与生产

### App Check

> [!WARNING]
> **关键安全要求**：为了安全地使用 AI 逻辑，您必须在您的应用上设置 App Check。这可以防止未经授权的客户端使用您的 API 配额并访问您的后端资源。

有关设置说明，请参阅 [使用 reCAPTCHA Enterprise 的 App Check](https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider.md.txt)。

### 远程配置

考虑您不需要硬编码模型名称（例如，`gemini-flash-lite-latest`）。使用 Firebase Remote Config 动态更新模型版本，而无需部署新的客户端代码。请参阅 [远程更改模型名称](https://firebase.google.com/docs/ai-logic/change-model-name-remotely.md.txt) 

## 初始化代码参考

| 语言、框架、平台 | Gemini API 提供商 | 上下文 URL |
| :---- | :---- | :---- |
| Web 模块 API | Gemini 开发者 API (开发者 API) | firebase://docs/ai-logic/get-started  |

**始终使用最新的 Gemini 版本（gemini-flash-latest），除非文档或用户请求其他模型。不要使用 gemini-1.5-flash**

## 参考

[Web SDK 代码示例和使用模式](references/usage_patterns_web.md)
