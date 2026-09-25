# 使用流畅设计

[![快速设计移动应用](https://raw.githubusercontent.com/sleekdotdesign/agent-skills/main/assets/hero.png)](https://sleek.design)

## 概述

[sleek.design](https://sleek.design) 是一款基于人工智能的移动应用设计工具。您通过 `/api/v1/*` 的 REST API 与其交互，用 plain language 描述您想要构建的内容，并获取渲染后的屏幕。所有通信均使用标准 HTTP 协议和 bearer token 进行身份验证。

**基础 URL**: `https://sleek.design`
**认证**: 在所有 `/api/v1/*` 请求中使用 `Authorization: Bearer $SLEEK_API_KEY`
**内容类型**: `application/json`（请求和响应）
**CORS**: 在所有 `/api/v1/*` 端点启用
**解析响应**: 将正文写入文件 (`curl -o run.json`) 并解析该文件。不要将 JSON 通过 `echo` 管道：在 zsh 中，它会将字符串值中的转义 `\n` 展开为实际换行符，这会使正文无效 JSON。
**API 文档**: OpenAPI 规范位于 `https://sleek.design/api/v1/spec.json`；可浏览的文档位于 `https://sleek.design/api/v1/docs`。获取任何未在此处涵盖的合同细节的规范。

---

## 前置条件：API 密钥

如果 `SLEEK_API_KEY` 未设置，请使用设备流程，以便用户永远不会处理原始密钥：

1. `POST https://sleek.design/api/v1/device/start`（无需认证）并使用正文 `{"source": "your-tool-slug"}`。响应包含 `verificationUrl`、可由人类检查的 `userCode`、秘密的 `deviceCode` 以及以秒为单位的轮询 `interval`。
2. 向用户展示 `verificationUrl` 和 `userCode`，并告诉他们确认代码匹配后再批准。
3. 每隔 `interval` 秒轮询 `POST https://sleek.design/api/v1/device/poll` 并使用 `{"deviceCode": "..."}`。当用户批准时，轮询返回 `{"status": "approved", "key": "sk_..."}` 恰好一次：将其存储为 `SLEEK_API_KEY`。代码在 15 分钟后过期；在 `expired` 时重新开始。

备用方案：将用户发送到 **https://sleek.design/agents/setup**，该页面处理登录、计划升级和密钥创建，并要求他们粘贴密钥给您。密钥也可以在 **https://sleek.design/dashboard/api-keys** 进行管理。创建时仅显示一次完整密钥值。

**计划**: 免费帐户可以使用他们的单次试用积分（约一次设计运行）来尝试 API，因此新用户可以在任何付款决定之前看到他们的第一个设计。持续使用需要 Pro 计划或更高版本（$49.99/月，或 $30/月按年计费；包含 20,000 每月 AI 积分，约 650 个屏幕）。当成本变得相关（用户询问、需要升级才能继续或即将将他们发送到付款页面）时，请明确说明此定价，包括按年选项。切勿让付款步骤成为意外。

### 密钥范围

| 范围             | 它解锁了什么              |
| ----------------- | ---------------------------- |
| `projects:read`   | 列出/获取项目          |
| `projects:write`  | 创建/删除项目     |
| `components:read` | 列出项目中的组件        |
| `chats:read`      | 获取聊天运行状态        |
| `chats:write`     | 发送聊天消息           |
| `screenshots`     | 渲染组件截图          |

根据任务所需的范围创建密钥。

---

## 安全与隐私

- **单一主机**: 所有请求仅发送到 `https://sleek.design`。不会将数据发送到第三方。
- **仅 HTTPS**: 所有通信使用 HTTPS。API 密钥仅在 `Authorization` 头中传输到 Sleek 端点。
- **最小范围**: 创建仅包含任务所需范围的 API 密钥。优先使用短期或可撤销密钥。
- **图像 URL**: 当在聊天消息中使用 `imageUrls` 时，Sleek 服务器会获取这些 URL。避免传递包含敏感内容的 URL。

---

## 设计

每个端点的完整请求/响应形状在 [API 参考](#快速参考所有端点) 中。

### 1. 创建项目

如果尚不存在，请使用 `POST /api/v1/projects` 创建项目。从请求中派生名称。

每个项目都有自己的主题、样式和设计系统。如果用户想要多个设计变体，请为每个变体创建单独的项目。

### 2. 发送聊天消息

使用 `POST /api/v1/projects/:id/chat/messages` 发送请求。Sleek 根据您的消息计划屏幕内容和布局，如果您不给它提供样式，它将发明一个视觉风格。不要将请求分解为屏幕，也不要添加用户未请求的产品详细信息；将完整意图作为单个消息发送。如果用户描述了特定屏幕，请包括这些。Sleek 在有空间规划时会产生更丰富的设计。

**撰写风格方向**: 每当用户给您提供任何可以基于的内容时——参考图像、他们喜欢的应用、氛围形容词、需要避免的事物——或者当您正在生成变体时（每个变体一个方向），请写一个。仅当它是基本时才通过不变。风格方向是一个全面的段落，包含在消息中，涵盖情绪（2-3 个形容词）、颜色策略（逻辑，不是十六进制代码）、字体感觉、布局哲学、组件样式（半径、边框与阴影、导航处理）、图像和插图风格，以及一个或两个独特细节。坚持调色板、字体方向和整体感觉——任何只设置情绪的东西都读作暗示，而不是方向。要有主见；不要犹豫。将个性融入颜色、字体和图像，而不是不寻常的布局或导航。

扩展用户给出的内容，并永不与之矛盾。当他们指向他们喜欢的参考图像或应用时，研究每一款，并将您学到的东西带入方向——Sleek 只能看到作为 `imageUrls` 传递的图像，因此对于任何本地内容，方向是这些参考如何到达它。借用模式，而不是来源的品牌、内容或名称。

使用风格方向或 `referenceId`，而不是两者——参考已经包含了自己的完整风格指南。

**用参考种子风格**: Sleek 管理一个设计参考目录。当用户想要特定的外观或请求样式选项时，使用 `GET /api/v1/references`（每个都有 `name` 和 `previewImageUrls` 您可以显示）列出它们，并在向项目发送第一条消息时传递所选的 `referenceId`，以便其风格指南为整个设计种子。

**标识您的工具**: 始终发送 `source`，即请求工具的缩写。Sleek 编辑器使用它来向用户显示正在设计的人，同时运行正在流式传输。识别的值：`claude-code`、`claude`、`codex`、`chatgpt`、`cursor`、`openclaw`、`grok`。如果您的工具未列出，请无论如何发送一个简短的 kebab-case 缩写（最多 64 个字符）。未识别的值是允许的，并将获得一个通用标签。

**实时查看**: 运行在 Sleek 编辑器中实时渲染。在向项目发送第一条消息后，告诉用户他们可以在 Sleek 中实时查看他们的屏幕正在被设计，并与编辑器链接分享：`https://sleek.design/project/:projectId`。除非用户要求，否则不要自己打开浏览器。

**轮询**: 聊天消息默认为异步：您将获得 `runId` 并轮询 `GET /api/v1/projects/:id/chat/runs/:runId`。从 2 秒间隔开始，10 秒后退回到 5 秒，5 分钟后放弃。在 `completed` 或 `failed` 时退出；如果您无法读取状态，请停止并报告，而不是将其计为“尚未完成”。您也可以使用 `?wait=true` 进行阻塞调用（最多 300 秒；如果超时则回退到轮询）。

**编辑特定屏幕**: 使用 `target.screenId` 将更改定向到正确的屏幕。`screenId` 来自运行的 `result.operations` 或来自 `GET /api/v1/projects/:id/components/:componentId` 返回的每个组件的 `screenId`；它不是组件 ID。

**一次运行一次**: 每个项目只允许一个活动运行。如果您收到 `409 CONFLICT`，请等待当前运行完成后再发送下一条消息。如果用户改变了主意或过时的运行阻止了项目，请取消它（见 [取消运行](#chat-cancel-run)）。发送到不同项目的消息可以并行运行；在并发运行多个项目时，使用异步轮询（而不是 `?wait=true`）。

**安全的重试**: 在安全的重新发送中添加 `idempotency-key` 头（≤255 个字符）。服务器将返回现有运行，而不是创建重复运行。

### 3. 显示结果

在每次产生 `screen_created` 或 `screen_updated` 操作的聊天运行后，**必须拍摄截图并显示给用户**使用 `POST /api/v1/screenshots`。只有在用户已经看到了运行创建或更新的每个屏幕的截图后，该步骤才会完成；永远不要在无声中完成运行。

- **新屏幕**: 每个屏幕一张截图 + 项目中所有屏幕的组合截图。
- **更新屏幕**: 每个受影响的屏幕一张截图。

除非用户明确请求特定的背景颜色，否则使用 `background: "transparent"`。

将截图保存在项目目录中（而不是临时文件夹），以便用户可以轻松查看它们。

**显示与审查**: 默认情况下，它只捕获视口，这是用户正确的框架——屏幕看起来像手机屏幕。它们是您自己工作的错误框架，因为折叠以下的所有内容都被裁剪掉了。当您正在审查运行产生的内容时，使用 `fullHeight: true`（每个请求一个屏幕）重新拍摄屏幕，以查看整个可滚动的页面。

截图请求是独立的，因此可以并行发出——面向用户的面部截图和您的 `fullHeight` 审查截图一起发出，不同屏幕的截图也是如此。“每个屏幕一个请求”控制每个图像中放入的内容，而不是发送的速度；它不是等待一个响应再开始下一个的原因。只有在您实际上收到 `429` 时才回退。

**从视口截图永远不会称屏幕不完整**。看起来缺失的内容几乎总是位于折叠以下。在告诉用户某物缺失或发送后续消息要求 Sleek 添加它之前，请与整个屏幕进行确认：`fullHeight: true` 截图，或来自 `GET /api/v1/projects/:id/components/:componentId` 的组件 HTML，它是屏幕上内容的权威依据。截图是默认的，并且可以自行回答大多数审查问题——不要去代码中双倍检查它已经显示的内容。当您即将声称某物缺失时，请使用代码：渲染可能会省略实际存在的内容（超出高度限制、在折叠部分、在后续的轮播幻灯片中），因此负面的结论是值得第二个来源的。注意相反的情况——HTML 中存在的元素可能仍然对用户不可见。

---

## 实现设计

当用户想要在代码中实现设计（而不仅仅是预览它们）时，**始终获取组件 HTML 代码**。不要仅依赖截图。

使用 `GET /api/v1/projects/:id/components/:componentId` 获取每个屏幕的代码。`componentId` 来自聊天运行的 `result.operations`。

组件代码可能很大。在将其保存到文件时，避免通过文本输出写入内容：它很慢且浪费代币。相反，使用 shell 命令获取 API 响应并将其直接写入磁盘（例如，将响应正文管道到文件）。

### 使用哪个版本

每个组件都携带一个 `versions[]` 数组和 `activeVersion: number`。**默认情况下，使用 `versions[i].version === activeVersion` 的条目**：这是 Sleek 中当前显示的代码。

如果用户的提示固定了特定版本，请遵循这些版本（见下文 [固定版本](#pinned-versions)）。

### 固定版本

用户的提示可能包含一个固定块，告诉您要实现特定的历史版本而不是当前版本，如下所示：

```
... 在这个确切的状态而不是项目的当前版本：
- 组件 cmp_abc: 版本 ver_001
- 组件 cmp_def: 版本 ver_002
- 主题 thm_ghi: 版本 ver_003
```

当您看到固定块时，请使用 `activeVersion` 替代 `activeVersion` 实现这些确切版本。未在固定块中命名的组件继续使用其活动版本。主题 ID 仅在固定块内部出现；此技能不暴露任何单独的端点来枚举它们。

#### 获取正确的代码

对于每个固定组件，找到 `versions[]` 中 `versions[i].id` 与给定版本 ID 匹配的条目（例如 `ver_001`），并使用其 `code`。**不要**对于固定组件回退到 `activeVersion`。

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

键是组件/主题的公共 ID；值是相应的 `versions[i].id`。从映射中缺少的实体回退到其活动版本。每当提示指定了固定版本时，请包含覆盖映射。

### HTML 原型

组件 `code` 是一个完整的 HTML 文档。直接将其保存到 `.html` 文件中。无需构建步骤。

### 原生框架（React Native、SwiftUI 等）

使用 HTML 代码和截图的组合：

- **HTML 代码**是实施参考：它包含确切的结构、布局、样式、颜色、间距、内容、图像 URL 和图标名称。
- **截图**是视觉目标：使用它们来验证您的实施是否与预期的外观匹配。

HTML 告诉您如何构建它；截图告诉您它应该看起来像什么。

#### 图标

Sleek 使用 [Iconify](https://iconify.design) 图标，格式为 `prefix:name`（例如 `solar:heart-bold`、`material-symbols:search-rounded`、`lucide:settings`）。最常见的集合是 **Solar**、**Hugeicons**、**Material Symbols** 和 **MDI**。

**使用 HTML 代码中的确切图标**。不要用不同的图标集替换。匹配图标对于设计保真度很重要。

当实现图标时：

1. **检查是否项目已经有一个支持 Sleek 使用相同集合（Solar、Hugeicons、Material Symbols、MDI）的图标系统**。如果是，请使用它。注意：`@expo/vector-icons` 不支持这些集合，因此不要将其用作替代。
2. **否则，从 Iconify API 获取 SVG 并将其嵌入代码中**：

   ```
   GET https://api.iconify.design/{prefix}/{name}.svg
   ```

   示例：`https://api.iconify.design/solar/heart-bold.svg`

   收集所有图标名称来自 HTML，获取它们的 SVG，并将它们作为静态资源或代码库中的字符串常量保存。对于 **React Native / Expo**，使用 `react-native-svg` 的 `SvgXml` 组件渲染它们，它可以在 Expo Go 中工作，而无需额外的原生依赖。

#### 字体

HTML 通过 `<link>` 标签在 `<head>` 中包含 Google Fonts。在原生框架中实现时使用相同的字体和权重。从 `<link>` 标签中提取字体家族名称和权重。

#### 导航

设计可能包括导航元素，如标签栏和页眉。更新项目的导航样式和结构以匹配设计。不要只是实现屏幕内容，而将默认导航保留不变。

---

## 快速参考：所有端点

| 方法   | 路径                                           | 范围             | 描述       |
| ------ | ---------------------------------------------- | ----------------- | ---------- |
| `GET`    | `/api/v1/projects`                             | `projects:read`   | 列出项目     |
| `POST`   | `/api/v1/projects`                             | `projects:write`  | 创建项目    |
| `GET`    | `/api/v1/projects/:id`                         | `projects:read`   | 获取项目     |
| `DELETE` | `/api/v1/projects/:id`                         | `projects:write`  | 删除项目    |
| `GET`    | `/api/v1/projects/:id/components`              | `components:read` | 列出组件   |
| `GET`    | `/api/v1/projects/:id/components/:componentId` | `components:read` | 获取组件   |
| `GET`    | `/api/v1/references`                           | 任何有效密钥     | 列出参考   |
| `POST`   | `/api/v1/projects/:id/chat/messages`           | `chats:write`     | 发送聊天消息 |
| `GET`    | `/api/v1/projects/:id/chat/runs/:runId`        | `chats:read`      | 轮询运行状态   |
| `POST`   | `/api/v1/projects/:id/chat/runs/:runId/cancel` | `chats:write`     | 取消运行    |
| `POST`   | `/api/v1/screenshots`                          | `screenshots`     | 渲染截图   |

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

响应 `201`: 与单个项目形状相同。

#### 获取/删除项目

```http
GET    /api/v1/projects/:projectId
DELETE /api/v1/projects/:projectId   → 204 No Content
```

---

### 组件

#### 列出组件

```http
GET /api/v1/projects/:projectId/components?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

列表和获取都接受可选的 `inlineIcons` 查询参数（默认 `false`）。当省略时，图标作为 `<iconify-icon>` 网络组件渲染，HTML 会拉取 Iconify 脚本，因此默认情况下将其省略。仅在消费者需要 HTML 中的自包含 SVG 时才传递 `?inlineIcons=true`。例如，导入到不运行脚本的工具中。

响应 `200`:

```json
{
  "data": [
    {
      "id": "cmp_xyz",
      "screenId": "scr_xyz",
      "name": "英雄部分",
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

通过 ID 获取单个组件。当您需要特定屏幕的代码时使用此操作（例如，在聊天运行返回 `componentId` 后）。

```http
GET /api/v1/projects/:projectId/components/:componentId
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`: `{ "data": ... }` 包含与列表项相同的单个组件形状。

---

### 参考

参考是来自 Sleek 精选项目的管理设计风格。它们是全世界的可读的：任何有效的 API 密钥都可以列出它们，无需范围。

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

要使用其中一个，请将其 `id` 作为 `referenceId` 发送到 [发送消息](#chat-send-message)。

---

### 聊天：发送消息

这是核心操作：在 `message.text` 中描述您想要的内容，AI 将创建或修改屏幕。

```http
POST /api/v1/projects/:projectId/chat/messages?wait=false
Authorization: Bearer $SLEEK_API_KEY
Content-Type: application/json
idempotency-key: <可选, 最大 255 个字符>

{
  "message": { "text": "添加一个定价部分，包含三个层级" },
  "source": "claude-code",
  "imageUrls": ["https://example.com/ref.png"],
  "target": { "screenId": "scr_abc" },
  "referenceId": "proj_ref1"
}
```

| 字段                    | 必填 | 备注                                                                                    |
| ------------------------ | ---- | ---------------------------------------------------------------------------------------- |
| `message.text`           | 是   | 1+ 字符, 去除空格                                                                        |
| `source`                 | 治为必填 | 请求发送工具的缩写（见 [设计的第 2 步](#2-send-a-chat-message))               |
| `imageUrls`              | 否   | 仅 HTTPS URL; 仅包含作为视觉上下文                                                        |
| `target.screenId`        | 否   | 使用 `screenId` 指向特定屏幕进行更改。`screenId` 来自运行的 `result.operations` 或来自 `GET /api/v1/projects/:id/components/:componentId` 返回的每个组件的 `screenId`；它不是组件 ID。如果用户描述了特定屏幕，请包括这些。Sleek 在有空间规划时会产生更丰富的设计。 |
| `referenceId`            | 否   | 用参考种子设计风格 (见 [参考](#references)); 无效 ID → `400`                             |
| `?wait=true/false`       | 否   | 同步等待模式 (默认: false)                                                          |
| `idempotency-key` 头 | 否   | 安全重试                                                                                   |

#### 异步响应 (默认, `wait=false`)

状态 `202 Accepted`。`result` 和 `error` 在运行达到终端状态之前不存在。

```json
{
  "data": {
    "runId": "run_111",
    "status": "queued",
    "statusUrl": "/api/v1/projects/proj_abc/chat/runs/run_111"
  }
}
```

#### 同步响应 (`wait=true`)

最多阻塞 **300 秒**。完成时返回 `200`，超时返回 `202`。

```json
{
  "data": {
    "runId": "run_111",
    "status": "completed",
    "statusUrl": "...",
    "result": {
      "assistantText": "我添加了一个定价部分，包含...",
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

### 聊天：轮询运行状态

在异步发送后使用此操作检查进度。

```http
GET /api/v1/projects/:projectId/chat/runs/:runId
Authorization: Bearer $SLEEK_API_KEY
```

响应与发送消息具有相同的 `data` 形状：`result` 在 `completed` 时存在，`error` 在 `failed` 时存在：

```json
{
  "data": {
    "runId": "run_111",
    "status": "failed",
    |
