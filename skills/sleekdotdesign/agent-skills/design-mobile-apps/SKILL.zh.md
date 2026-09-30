---
name: sleek-design-mobile-apps
description: 当用户想要设计移动应用程序或UI界面时使用，当他们提到自己的Sleek（sleek.design）项目时，或者在代码（HTML、React Native、SwiftUI）中实现Sleek设计时。
---

# 使用流畅设计

![快速设计移动应用](https://raw.githubusercontent.com/sleekdotdesign/agent-skills/main/assets/hero.png) (点击查看流畅设计网站)

## 概述

[sleek.design](https://sleek.design) 是一款基于人工智能的移动应用设计工具。您通过 `/api/v1/*` 路径的 REST API 与其交互，创建项目、用普通语言描述您想要构建的内容，并获取渲染后的屏幕。所有通信均使用标准 HTTP 协议，并采用令牌认证。

**基础 URL**: `https://sleek.design`
**认证**: 在每个 `/api/v1/*` 请求中使用 `Authorization: Bearer $SLEEK_API_KEY`
**内容类型**: `application/json` (请求和响应)
**CORS**: 在所有 `/api/v1/*` 端点启用
**解析响应**: 将正文写入文件 (`curl -o run.json`) 并解析该文件。不要将 JSON 通过 `echo` 管道：在 zsh 中，它会将字符串值中的转义 `\n` 展开为实际换行符，使正文无效 JSON。
**API 文档**: OpenAPI 规范位于 `https://sleek.design/api/v1/spec.json`；可浏览的文档位于 `https://sleek.design/api/v1/docs`。对于此处未涵盖的任何合同细节，请获取规范。

---

## 前置条件：API 密钥

如果未设置 `SLEEK_API_KEY`，请使用设备流程，以便用户无需处理原始密钥：

1. 使用 `POST https://sleek.design/api/v1/device/start` (无需认证) 并在正文中传递 `{"source": "your-tool-slug"}`。响应包含 `verificationUrl`、可人工核实的 `userCode`、秘密 `deviceCode` 以及以秒为单位的轮询 `interval`。
2. 向用户展示 `verificationUrl` 和 `userCode`，并告诉他们确认代码匹配后再批准。
3. 每隔 `interval` 秒轮询 `POST https://sleek.design/api/v1/device/poll` 并传递 `{"deviceCode": "..."}`。当用户批准时，轮询返回 `{"status": "approved", "key": "sk_..."}` 一次：将其存储为 `SLEEK_API_KEY`。代码在 15 分钟后过期；如果 `expired`，请重新开始。

备用方案：将用户引导至 **https://sleek.design/agents/setup**，该页面可处理登录、计划升级和密钥创建，并要求他们粘贴密钥给您。密钥也可以在 **https://sleek.design/dashboard/api-keys** 处进行管理。创建时仅显示一次完整密钥值。

**计划**: 免费账户可以使用一次性试用积分（约一次设计运行）来试用 API，因此新用户可以在做出任何支付决定之前看到他们的第一个设计。持续使用需要 Pro 计划或更高版本（$49.99/月，或 $30/月按年付费，每年 $360；包含 20,000 每月 AI 积分，约 650 个屏幕）。当成本变得相关时（用户询问、需要升级才能继续或即将将他们引导至支付页面），请明确说明此定价，包括按年选项。切勿让支付步骤成为意外。

### 密钥范围

| 范围             | 它解锁的内容              |
| ----------------- | ---------------------------- |
| `projects:read`   | 列出/获取项目          |
| `projects:write`  | 创建/删除项目     |
| `components:read` | 列出项目中的组件      |
| `chats:read`      | 获取聊天运行状态          |
| `chats:write`     | 发送聊天消息           |
| `screenshots`     | 渲染组件截图 |

根据任务需要创建密钥。

---

## 安全与隐私

- **单一主机**: 所有请求仅发送到 `https://sleek.design`。数据不会发送给第三方。
- **仅 HTTPS**: 所有通信使用 HTTPS。API 密钥仅在 `Authorization` 头中传输到 Sleek 端点。
- **最小范围**: 创建仅包含任务所需范围的 API 密钥。优先使用短期或可撤销密钥。
- **图像 URL**: 当在聊天消息中使用 `imageUrls` 时，Sleek 服务器会获取这些 URL。避免传递包含敏感内容的 URL。

---

## 设计

每个端点的完整请求/响应形状在 [API 参考](#quick-reference-all-endpoints) 中。

### 1. 创建项目

如果尚不存在项目，请使用 `POST /api/v1/projects` 创建项目。从请求中派生名称。

每个项目都有自己的主题、样式和设计系统。如果用户需要多个设计变体，请为每个变体创建单独的项目。

### 2. 发送聊天消息

使用 `POST /api/v1/projects/:id/chat/messages` 发送请求。Sleek 根据您的消息规划屏幕内容和布局，如果没有提供视觉风格，则会自行发明。不要将请求分解为多个屏幕，也不要添加用户未请求的产品详细信息；将完整意图作为单个消息发送。如果用户描述了特定屏幕，请包含这些。当给予 Sleek 留出规划空间时，Sleek 生成更丰富的设计。

**撰写风格方向**: 每当用户提供了任何用于参考的内容（参考图像、他们喜欢的应用、氛围形容词、需要避免的内容）或当您生成变体（每个变体一个方向）时，请写一个。仅在内容为空时才传递请求。风格方向是一个全面的段落，包含在消息中，涵盖情绪（2-3 个形容词）、颜色策略（逻辑，不是十六进制代码）、字体感觉、布局哲学、组件样式（圆角、边框与阴影、导航处理）、图像和插图风格，以及一两个独特细节。坚持调色板、字体方向和整体感觉——任何仅设置情绪的内容都应被视为暗示，而不是方向。要果断；不要犹豫。将个性融入颜色、字体和图像，而不是不寻常的布局或导航。

扩展用户给出的内容，并始终与其保持一致。当用户指向他们喜欢的参考图像或应用时，研究每个图像并提取您学到的内容到方向中——Sleek 只能看到作为 `imageUrls` 传递的图像，因此对于任何本地内容，方向是如何到达它的。借鉴模式，而不是源品牌的标志、内容或名称。

使用风格方向或 `referenceId`，而不是两者——参考图像已经包含了自己的完整风格指南。

**用参考图像初始化风格**: Sleek 管理设计参考目录。当用户想要特定外观或请求风格选项时，使用 `GET /api/v1/references` 列出它们（每个都有 `name` 和 `previewImageUrls` 您可以展示），并将选择的 ID 作为 `referenceId` 在项目第一条消息中传递，以便其风格指南为整个设计提供种子。

**标识您的工具**: 始终发送 `source`，即发出请求的工具的缩写。Sleek 编辑器使用它来向用户显示正在设计的是谁，同时运行正在流式传输。识别的值：`claude-code`、`claude`、`codex`、`chatgpt`、`cursor`、`openclaw`、`grok`。如果您的工具未列出，请无论如何发送其短划线分隔的缩写（最多 64 个字符）。未识别的值是允许的，并将获得通用标签。

**实时查看**: 运行在 Sleek 编辑器中实时渲染。在向项目发送第一条消息后，告诉用户他们可以在 Sleek 中实时查看他们的屏幕被设计的过程，并分享编辑器链接：`https://sleek.design/project/:projectId`。除非用户要求，否则不要自行打开浏览器。

**轮询**: 聊天消息默认为异步：您将获得 `runId` 并轮询 `GET /api/v1/projects/:id/chat/runs/:runId`。从 2 秒间隔开始，10 秒后退回到 5 秒，5 分钟后放弃。在 `completed` 或 `failed` 时退出；如果您无法读取状态，请停止并报告它，而不是将其计为“尚未完成”。您也可以使用 `?wait=true` 进行阻塞调用（最多 300 秒；如果超时则回退到轮询，并返回 `202`）。

**编辑特定屏幕**: 使用 `target.screenId` 指向正确的屏幕进行更改。`screenId` 来自运行的 `result.operations` 或来自 `GET /api/v1/projects/:id/components` 返回的每个组件的 `screenId` 字段；它不是组件 ID。

**一次运行一次**: 每个项目只允许一个活动运行。如果您收到 `409 CONFLICT`，请在发送下一条消息前等待当前运行完成。如果用户改变了主意或过时的运行阻塞了项目，请取消它（见 [取消运行](#chat-cancel-run)）。向不同项目发送的消息可以并行运行；在并发运行多个项目时，使用异步轮询（而不是 `?wait=true`）。

**安全的重试**: 添加 `idempotency-key` 头进行安全的重发。服务器将返回现有运行，而不是创建重复项。

### 3. 展示结果

在每次产生 `screen_created` 或 `screen_updated` 操作的聊天运行后，**必须截图并展示给用户**，使用 `POST /api/v1/screenshots`。仅在用户看到运行创建或更新的每个屏幕的截图后完成此步骤；切勿无声完成运行。

- **新屏幕**: 每个屏幕一张截图 + 项目中所有屏幕的组合截图。
- **更新屏幕**: 每个受影响的屏幕一张截图。

使用 `background: "transparent"`，除非用户明确请求特定背景颜色。

将截图保存在项目目录中（而不是临时文件夹），以便用户可以轻松查看。

**展示与审查**: 默认情况下，截图仅捕获视口，这是用户正确的框架——屏幕看起来像手机屏幕。它们是您自己工作评估的错误框架，因为所有视口以下的內容都被裁剪掉了。当您审查运行生成的内容时，使用 `fullHeight: true` 重新拍摄屏幕（每个屏幕一个请求）以查看整个可滚动的页面。

截图请求是独立的，因此请并行发出——用户界面截图和您的 `fullHeight` 审查截图一起发送，不同屏幕的截图也是如此。"每个请求一个屏幕" 决定每个图像中包含的内容，而不是发送速度；这不是开始下一个请求的理由。仅在您实际收到 `429` 时才回退。

**从视口截图切勿称屏幕不完整。** 看起来缺失的内容几乎总是位于视口以下。在告诉用户某物缺失或发送后续消息要求 Sleek 添加它之前，请与整个屏幕进行确认：`fullHeight: true` 截图，或来自 `GET /api/v1/projects/:id/components/:componentId` 的组件 HTML，它是屏幕上内容的真实依据。截图是默认的，并且可以自行回答大多数审查问题——不要去代码中双查它已经显示的内容。只有在您准备声称某物缺失时才去代码：渲染可能会省略实际存在的内容（超出高度限制、在折叠部分、在后续的轮播幻灯片中），因此负面结论是值得第二个来源的。注意反向情况——HTML 中存在的元素可能仍然对用户不可见。

---

## 实现设计

当用户希望将设计代码实现（而不仅仅是预览）时，**始终获取组件 HTML 代码**。不要仅依赖截图。

使用 `GET /api/v1/projects/:id/components/:componentId` 获取每个屏幕的代码。`componentId` 来自聊天运行的 `result.operations`。

组件代码可能很大。在保存到文件时，避免通过文本输出写入内容：它很慢且浪费代币。相反，使用 shell 命令获取 API 响应并将其直接写入磁盘（例如，将响应正文管道到文件）。

### 使用哪个版本

每个组件都带有 `versions[]` 数组和 `activeVersion: number`。**默认情况下，使用 `versions[i].version === activeVersion` 的条目**：那是 Sleek 中当前显示的代码。

如果用户的提示固定了特定版本，请遵循这些版本（见下文 [固定版本](#pinned-versions)）。

### 固定版本

用户的提示可能包含一个固定块，告诉您要实现特定历史版本，而不是当前版本，如下所示：

```
... 在这个确切状态下，而不是项目的当前版本：
- 组件 cmp_abc: 版本 ver_001
- 组件 cmp_def: 版本 ver_002
- 主题 thm_ghi: 版本 ver_003
```

当您看到固定块时，请实现这些确切版本，而不是 `activeVersion`。未在固定块中命名的组件继续使用其活动版本。主题 ID 仅在固定块内部出现；此技能不暴露单独的端点来枚举它们。

#### 获取正确的代码

对于每个固定组件，找到 `versions[]` 中 `versions[i].id` 与给定版本 ID 匹配的条目（例如 `ver_001`），并使用其 `code`。对于固定组件，**不要**回退到 `activeVersion`。

#### 固定版本的截图

将 `componentVersionOverrides` 和 `themeVersionOverrides` 传递给 `POST /api/v1/screenshots`：

```json
{
  "componentIds": ["cmp_abc"],
  "projectId": "proj_xyz",
  "componentVersionOverrides": { "cmp_abc": "ver_001" },
  "themeVersionOverrides": { "thm_ghi": "ver_003" }
}
```

键是组件/主题的公共 ID；值是相应的 `versions[i].id`。未在映射中出现的实体回退到其活动版本。每当提示指定了固定版本时，请包含这些覆盖映射。

### HTML 原型

组件 `code` 是一个完整的 HTML 文档。直接将其保存为 `.html` 文件。无需构建步骤。

### 原生框架（React Native、SwiftUI 等）

同时使用 HTML 代码和截图：

- **HTML 代码** 是实现参考：它包含确切的结构、布局、样式、颜色、间距、内容、图像 URL 和图标名称。
- **截图** 是视觉目标：使用它们来验证您的实现与预期外观匹配。

HTML 告诉您如何构建它；截图告诉您它应该看起来像什么。

#### 图标

Sleek 使用 [Iconify](https://iconify.design) 图标，格式为 `prefix:name`（例如 `solar:heart-bold`、`material-symbols:search-rounded`、`lucide:settings`）。最常见的集合是 **Solar**、**Hugeicons**、**Material Symbols** 和 **MDI**。

**使用 HTML 代码中的确切图标**。不要用不同的图标集替换。匹配图标对于设计保真度很重要。

在实现图标时：

1. **检查项目是否已经有一个支持 Sleek 使用的相同集合（Solar、Hugeicons、Material Symbols、MDI）的图标系统**。如果是，请使用它。注意：`@expo/vector-icons` **不支持**这些集合，因此不要将其用作替代。
2. **否则，从 Iconify API 获取 SVG 并将它们嵌入代码中：**

   ```
   GET https://api.iconify.design/{prefix}/{name}.svg
   ```

   示例：`https://api.iconify.design/solar/heart-bold.svg`

   收集所有图标名称，获取它们的 SVG，并将它们作为静态资源或代码库中的字符串常量保存。对于 **React Native / Expo**，使用 `react-native-svg` 的 `SvgXml` 组件渲染它们，它在 Expo Go 中无需额外的原生依赖即可工作。

#### 字体

HTML 通过 `<head>` 中的 `<link>` 标签包含 Google Fonts。在原生框架中实现时使用相同的字体和权重。从 `<link>` 标签中提取字体家族名称和权重。

#### 导航

设计可能包括导航元素，如标签栏和页眉。更新项目的导航样式和结构以匹配设计。不要仅实现屏幕内容而保留默认导航不变。

---

## 快速参考：所有端点

| 方法   | 路径                                           | 范围             | 描述       |
| ------ | --------------------------------------------- | ---------------- | ---------- |
| `GET`  | `/api/v1/projects`                             | `projects:read`   | 列出项目   |
| `POST` | `/api/v1/projects`                             | `projects:write`  | 创建项目   |
| `GET`  | `/api/v1/projects/:id`                         | `projects:read`   | 获取项目   |
| `DELETE` | `/api/v1/projects/:id`                         | `projects:write`  | 删除项目   |
| `GET`  | `/api/v1/projects/:id/components`              | `components:read` | 列出组件   |
| `GET`  | `/api/v1/projects/:id/components/:componentId` | `components:read` | 获取组件   |
| `GET`  | `/api/v1/references`                           | 任何有效密钥     | 列出参考   |
| `POST` | `/api/v1/projects/:id/chat/messages`           | `chats:write`     | 发送聊天消息 |
| `GET`  | `/api/v1/projects/:id/chat/runs/:runId`        | `chats:read`      | 检查运行状态 |
| `POST` | `/api/v1/projects/:id/chat/runs/:runId/cancel` | `chats:write`     | 取消运行   |
| `POST` | `/api/v1/screenshots`                          | `screenshots`     | 渲染截图   |

---

## 端点

### 项目

#### 列出项目

```http
GET /api/v1/projects?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`:

```json
{
  "data": [
    {
      "id": "proj_abc",
      "name": "我的应用",
      "slug": "my-app",
      "createdAt": "2026-01-01T00:00:00Z",
      "updatedAt": "..."
    }
  ],
  "pagination": { "total": 12, "limit": 50, "offset": 0 }
}
```

#### 创建项目

```http
POST /api/v1/projects
Authorization: Bearer $SLEEK_API_KEY
Content-Type: application/json

{ "name": "我的新应用" }
```

响应 `201`: 与单个项目的形状相同。

#### 获取/删除项目

```http
GET    /api/v1/projects/:projectId
DELETE /api/v1/projects/:projectId   → 204 无内容
```

---

### 组件

#### 列出组件

```http
GET /api/v1/projects/:projectId/components?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

列表和获取都接受一个可选的 `inlineIcons` 查询参数（默认 `false`）。当省略时，图标作为 `<iconify-icon>` 网络组件渲染，并且 HTML 会引入 Iconify 脚本，因此默认情况下省略它。只有当消费者需要在 HTML 中包含自包含的 SVG 时才传递 `?inlineIcons=true`（例如，导入不运行脚本的工具）。

响应 `200`:

```json
{
  "data": [
    {
      "id": "cmp_xyz",
      "screenId": "scr_xyz",
      "name": "英雄区域",
      "activeVersion": 3,
      "versions": [
        {
          "id": "ver_001",
          "version": 1,
          "code": "<!DOCTYPE html>...</html>",
          "createdAt": "..."
        }
      ],
      "createdAt": "...",
      "updatedAt": "..."
    }
  ],
  "pagination": { "total": 5, "limit": 50, "offset": 0 }
}
```

#### 获取组件

通过 ID 获取单个组件。当你需要特定屏幕的代码时使用此方法（例如，在聊天运行返回 `componentId` 的操作之后）。

```http
GET /api/v1/projects/:projectId/components/:componentId
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`: `{ "data": ... }` 包含与列表项相同的单个组件形状。

---

### 参考

参考是精选 Sleek 项目的策划设计风格。它们是全世界可读的：任何有效的 API 密钥都可以列出它们，不需要范围。

```http
GET /api/v1/references?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`:

```json
{
  "data": [
    {
      "id": "proj_ref1",
      "name": "Ember Fitness",
      "previewImageUrls": ["https://.../screenshot.png"]
    }
  ],
  "pagination": { "total": 44, "limit": 50, "offset": 0 }
}
```

要使用其中一个，将其 `id` 作为 `referenceId` 传递给 [发送消息](#chat-send-message)。

---

### 聊天：发送消息

这是核心操作：在 `message.text` 中描述你想要的内容，AI 会创建或修改屏幕。

```http
POST /api/v1/projects/:projectId/chat/messages?wait=false
Authorization: Bearer $SLEEK_API_KEY
Content-Type: application/json
idempotency-key: <可选，最多 255 个字符>

{
  "message": { "text": "添加一个定价区域，包含三个层级" },
  "source": "claude-code",
  "imageUrls": ["https://example.com/ref.png"],
  "target": { "screenId": "scr_abc" },
  "referenceId": "proj_ref1"
}
```

| 字段                    | 是否必需 | 备注                                                                                      |
| ----------------------- | -------- | ---------------------------------------------------------------------------------------- |
| `message.text`           | 是      | 1+ 字符，会被修剪                                                                        |
| `source`                 | 视为必需 | 发送请求的工具的缩写（见 [设计步骤 2](#2-send-a-chat-message)） |
| `imageUrls`              | 否       | 仅限 HTTPS URL；作为视觉上下文包含                                                        |
| `target.screenId`        | 否       | 使用其 `screenId`（从运行操作或组件列表中获取；不是 `componentId`）编辑特定屏幕；省略则让 AI 决定 |
| `referenceId`            | 否       | 从参考中种子设计风格（见 [参考](#references)）；无效 ID → `400` |
| `?wait=true/false`       | 否       | 同步等待模式（默认：false）                                                          |
| `idempotency-key` 头部 | 否       | 安全重发                                                                             |

#### 响应：异步（默认，`wait=false`）

状态 `202 Accepted`。`result` 和 `error` 在运行达到终端状态之前不会出现。

```json
{
  "data": {
    "runId": "run_111",
    "status": "queued",
    "statusUrl": "/api/v1/projects/proj_abc/chat/runs/run_111"
  }
}
```

#### 响应：同步 (`wait=true`)

最多阻塞 **300 秒**。完成时返回 `200`，超时则返回 `202`。

```json
{
  "data": {
    "runId": "run_111",
    "status": "completed",
    "statusUrl": "...",
    "result": {
      "assistantText": "我添加了一个定价区域，...",
      "operations": [
        {
          "type": "screen_created",
          "screenId": "scr_xyz",
          "screenName": "定价",
          "componentId": "cmp_xyz"
        },
        {
          "type": "screen_updated",
          "screenId": "scr_abc",
          "componentId": "cmp_abc"
        },
        { "type": "theme_updated" }
      ]
    }
  }
}
```

---

### 聊天：检查运行状态

在异步发送后使用此方法检查进度。

```http
GET /api/v1/projects/:projectId/chat/runs/:runId
Authorization: Bearer $SLEEK_API_KEY
```

响应的 `data` 形状与发送消息相同：`result` 在 `completed` 时出现，`error` 在 `failed` 时出现：

```json
{
  "data": {
    "runId": "run_111",
    "status": "failed",
    "statusUrl": "...",
    "error": { "code": "execution_failed", "message": "..." }
  }
}
```

**运行状态生命周期**：`queued` → `running` → `completed | failed`

---

### 聊天：取消运行

```http
POST /api/v1/projects/:projectId/chat/runs/:runId/cancel
Authorization: Bearer $SLEEK_API_KEY
```

将 `queued` 或 `running` 运行标记为 `failed` 并带有错误代码 `cancelled`，然后返回更新后的运行；已完成的运行将保持不变。在运行中途用户改变主意或过时的运行阻塞项目时使用它（`409 CONFLICT`）。

---

### 截图

对一个或多个渲染的组件进行截图。

```http
POST /api/v1/screenshots
Authorization: Bearer $SLEEK_API_KEY
Content-Type: application/json

{
  "componentIds": ["cmp_xyz", "cmp_abc"],
  "projectId": "proj_abc",
  "format": "png",
  "scale": 2,
  "gap": 40,
  "padding": 40,
  "background": "transparent"
}
```

| 字段                       | 默认       | 备注                                                                                                                                    |
| ------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `format`                    | `png`      | `png` 或 `webp`                                                                                                                          |
| `scale`                     | `2`        | 1–3（设备像素比）                                                                                                                       |
| `gap`                       | `40`       | 组件之间的像素                                                                                                                          |
| `padding`                   | `40`       | 所有边的统一填充                                                                                                                        |
| `paddingX`                  | _(可选)_  | 水平填充；提供时覆盖 `padding` 左右                                                                                                    |
| `paddingY`                  | _(可选)_  | 垂直填充；提供时覆盖 `paddingY` 上下                                                                                                   |
| `paddingTop`                | _(可选)_  | 顶部填充；提供时覆盖 `paddingY` 顶部                                                                                                   |
| `paddingRight`              | _(可选)_  | 右侧填充；提供时覆盖 `paddingX` 右侧                                                                                                    |
| `paddingBottom`             | _(可选)_  | 底部填充；提供时覆盖 `paddingY` 底部                                                                                                  |
| `paddingLeft`               | _(可选)_  | 左侧填充；提供时覆盖 `paddingX` 左侧                                                                                                    |
| `background`                | `transparent` | 任何 CSS 颜色（十六进制、命名、`transparent`）                                                                                          |
| `showDots`                  | `false`    | 在背景上覆盖一个微妙的点网格                                                                                                              |
| `fullHeight`                | `false`    | 捕获整个可滚动的屏幕而不是仅捕获视口（见下文）                                                                                          |
| `radius`                    | `48`       | 每个组件的像素圆角半径（整数 ≥ 0）；传递 `0` 用于尖角                                                                                   |
| `componentVersionOverrides` | _(可选)_  | `componentId` → `versions[i].id` 的映射，以渲染固定版本而不是 `activeVersion`（见 [固定版本](#pinned-versions)） |
| `themeVersionOverrides`     | _(可选)_  | `themeId` → `versions[i].id` 的映射，以使用固定主题版本渲染（见 [固定版本](#pinned-versions)） |

填充按级联解析：每边 → 轴 → 统一。例如，`paddingTop` 退回到 `paddingY`，再退回到 `padding`。因此，`{ "padding": 20, "paddingX": 10, "paddingLeft": 5 }` 给顶部/底部 20px，右侧 10px，左侧 5px。

默认情况下，组件按帧高度捕获，因此用户通过滚动可以到达的内容会被裁剪。`fullHeight: true` 将每个帧扩展到其内容的高度再进行捕获。在审阅自己的工作时使用它；对于向用户展示的截图，保留它，因为手机形状的框架才是重点。

帧高度限制为 **默认帧高度的 4 倍**，因此即使使用 `fullHeight: true`，超过该高度的屏幕也会在底部被裁剪。对于非常长的屏幕，将组件 HTML 视为权威，以确定裁剪以下内容。扩展帧会生成高图像；最好每个请求一个组件，以保持每个屏幕的细节——并且并行发送这些请求，而不是一个接一个。

当 `showDots` 为 `true` 时，会在背景颜色上绘制点图案。点会自动适应背景：深色背景会得到浅色点，浅色背景会得到深色点。当 `background` 为 `"transparent"` 时，此功能无效。

响应：原始二进制 `image/png` 或 `image/webp`，`Content-Disposition: attachment`。

---

## 错误形状

```json
{ "code": "UNAUTHORIZED", "message": "..." }
```

| HTTP | 代码                    | 当...时                                             |
| ---- | ----------------------- | -------------------------------------------------- |
| 401  | `UNAUTHORIZED`          | 缺失/无效/过期 API 密钥                             |
| 403  | `FORBIDDEN`             | 有效密钥，范围或计划错误                           |
| 404  | `NOT_FOUND`             | 资源不存在                                         |
| 400  | `BAD_REQUEST`           | 验证失败                                           |
| 409  | `CONFLICT`              | 此项目有另一个活跃运行                             |
| 429  | `TOO_MANY_REQUESTS`     | 请求过多；稍后重试                               |
| 500  | `INTERNAL_SERVER_ERROR` | 服务器错误                                         |

`401`、`403` 和 `429` 的正文可能包含 `data.url`：用户可以修复条件的页面（创建密钥、升级计划）。如果存在，请与用户分享该 URL，而不是临时编造一个。

聊天运行级别的错误（在 `data.error` 内）：

| 代码               | 含义                               |
| ------------------ | ---------------------------------- |
| `out_of_credits`   | 组织没有剩余积分                  |
| `execution_failed` | AI 执行错误                        |
| `cancelled`        | 通过取消端点取消运行              |

`out_of_credits` 错误包含 `error.url`，用户可以充值积分的页面。将此 URL 传递给用户；在他们充值之前不要重试运行。

---

## 分页

所有列表端点都接受 `limit`（1–100，默认 50）和 `offset`（≥0）。响应始终包含 `pagination.total`，以便您可以分页浏览所有结果。

```http
GET /api/v1/projects?limit=10&offset=20
```

---

## 常见错误

| 错误                                                                 | 修复                                                                                                  |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 在聊天消息中省略 `source`                                                 | 始终发送 `source`，以便在 Sleek 编辑器中将运行归因                                           |
| 在长时间生成中使用 `wait=true`                                             | 它最多阻塞 300 秒；使用回退轮询 `202` 响应                                                 |
| 假设 `202` 中的 `result` 存在                                               | `result` 在状态为 `completed` 之前不存在                                                     |
| 将 JSON 响应通过 `echo` 管道解析                                           | zsh 会展开 `assistantText` 中的 `\n` 并破坏 JSON；改为从文件中解析                               |
| 将无法读取的运行状态视为 "尚未完成"                                       | 循环会在运行结束后长时间旋转到其上限；停止并报告，而不是继续旋转                               |
| 基于 视口截图判断屏幕不完整                                               | 内容通常在折叠区域下方；使用 `fullHeight: true` 重新拍摄，或在报告任何缺失内容之前检查组件 HTML |
| 在截图中使用 `screenId` 作为 `componentIds`                               | `screenId` 和 `componentId` 是不同的：每个屏幕都有这两个（运行操作和组件列表返回这对）。聊天消息 `target.screenId` 使用 `screenId`；截图和组件读取使用 `componentId` |
| 混淆 `versions[i].version`（数字）与 `versions[i].id`（字符串）             | 在解析固定版本时，按 `id` 匹配（例如 `ver_001`）；`version` 是数字索引
