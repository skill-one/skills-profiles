# 使用 sleek 进行设计

[![在几分钟内设计移动应用](https://raw.githubusercontent.com/sleekdotdesign/agent-skills/main/assets/hero.png)](https://sleek.design)

## 概述

[sleek.design](https://sleek.design) 是一款由 AI 驱动的移动应用设计工具。您可以通过 `/api/v1/*` 路径下的 REST API 与其交互，以创建项目、用纯语言描述您希望构建的内容，并获取渲染后的屏幕。所有通信均采用标准 HTTP 协议配合 Bearer Token 认证。

**基础 URL**：`https://sleek.design`
**认证**：在每个 `/api/v1/*` 请求中使用 `Authorization: Bearer $SLEEK_API_KEY`
**内容类型**：`application/json`（请求和响应均为 JSON）
**CORS**：所有 `/api/v1/*` 端点均启用 CORS
**解析响应**：将响应体写入文件（`curl -o run.json`）并解析该文件。不要通过 `echo` 将 JSON 管道传输：在 zsh 中，转义的 `\n` 会被展开为实际的换行符，导致响应体无效 JSON。
**API 文档**：OpenAPI 规范位于 `https://sleek.design/api/v1/spec.json`；可浏览文档位于 `https://sleek.design/api/v1/docs`。针对此处未覆盖的契约细节，可获取规范进行查询。

---

## 前置条件：API Key

如果未设置 `SLEEK_API_KEY`，请使用设备流程，确保用户无需处理原始密钥：

1. `POST https://sleek.design/api/v1/device/start`（无需认证）并发送请求体 `{"source": "your-tool-slug"}`。响应中包含 `verificationUrl`、可人工核对的 `userCode`、secret `deviceCode`，以及轮询 `interval`（以秒为单位）。
2. 向用户展示 `verificationUrl` 和 `userCode`，并告知其在批准前确认代码匹配。
3. 每隔 `interval` 秒轮询 `POST https://sleek.design/api/v1/device/poll`，并发送 `{"deviceCode": "..."}`。当用户批准后，轮询将一次性返回 `{"status": "approved", "key": "sk_..."}`：将其保存为 `SLEEK_API_KEY`。代码在 15 分钟后过期；若变为 `expired`，请重新开始。

备用方案：将用户引导至 **https://sleek.design/agents/setup**，该页面统一处理登录、套餐升级和密钥创建，并请用户将密钥粘贴回来。密钥也可在 **https://sleek.design/dashboard/api-keys** 处管理。密钥的完整值仅在创建时显示一次。

**套餐**：免费账户可使用一次性试用额度（约一次设计运行）尝试 API，以便新用户在进行任何支付决策前即可查看首次设计。持续使用需要 Pro 套餐或更高（$49.99/月，或 $30/月按年计费，$360/年；包含每月 20,000 次 AI 额度，约 650 个屏幕）。当成本变得相关时（用户询问、需要升级才能继续，或即将引导用户至支付页面），需清晰说明此定价，包括年付选项。切勿让支付步骤成为意外出现。

### 关键权限范围

| 权限范围             | 解锁的内容                  |
| ------------------- | ---------------------------- |
| `projects:read`     | 列出 / 获取项目              |
| `projects:write`    | 创建 / 删除项目              |
| `components:read`   | 列出项目内的组件              |
| `chats:read`        | 获取聊天运行状态              |
| `chats:write`       | 发送聊天消息                 |
| `screenshots`       | 渲染组件截图                |

仅为任务所需权限范围创建密钥。

---

## 安全与隐私

- **单一主机**：所有请求仅发送到 `https://sleek.design`，数据不会发送给任何第三方。
- **仅限 HTTPS**：所有通信均使用 HTTPS。API 密钥仅通过 `Authorization` 请求头传输至 Sleek 端点。
- **最小权限范围**：仅为任务所需创建 API 密钥。优先使用短期有效或可撤销的密钥。
- **图片 URL**：在聊天消息中使用 `imageUrls` 时，这些 URL 由 Sleek 服务器获取。避免传入包含敏感内容的 URL。

---

## 设计

下文使用的所有接口的完整请求/响应结构参见 [API 参考](#quick-reference-all-endpoints)。

### 1. 创建项目

如尚未创建项目，请使用 `POST /api/v1/projects` 创建项目，从请求中推导名称。

每个项目拥有独立的主题、风格和设计系统。如果用户需要多种设计变体，请为每个变体创建独立的项目。

### 2. 发送聊天消息

使用 `POST /api/v1/projects/:id/chat/messages` 发送请求。Sleek 会根据您的消息规划屏幕内容和布局，若您未指定视觉风格，它会自行生成。请勿将请求拆解为屏幕，也勿添加用户未要求的产品细节；应将完整意图作为一条消息发送。若用户描述了具体的屏幕，请包含这些描述。给定规划空间时，Sleek 能产出更丰富的设计。

**编写风格方向**：当用户已提供可用于据此锚定内容时（参考图片、喜欢的应用、风格形容词、需避免的事项），或在进行变体生成时为每个变体编写一条风格方向。仅当请求内容仅为空时，才原样传递请求。风格方向为单一综合性段落，包含在消息中，涵盖情绪（2–3 个形容词）、色彩策略（逻辑而非色值）、字体质感、布局理念、组件风格（圆角、边框与阴影、导航处理方式）、图片与插画风格，以及一两个特色细节。需确定配色方案、字体方向与整体基调——仅用于营造氛围的内容不算方向。应明确立场，不要模棱两可。将个性融入色彩、字体与图片，而非不寻常的布局或导航。

在用户提供的信息基础上进行扩展，切勿与之矛盾。当用户指向参考图片或喜欢的应用时，需研究每一份并将其所体现的内容纳入方向中——Sleek 仅能看到以 `imageUrls` 形式传入的图片，因此对于本地内容，方向即如何将这些参考传递至 Sleek。借鉴模式，而非来源的品牌、内容或名称。

使用风格方向或 `referenceId`，二者不可同时使用——参考本身已包含完整的风格指南。

**使用参考 seed 风格**：Sleek 整理了一套设计参考目录。当用户需要特定风格或要求风格选项时，使用 `GET /api/v1/references` 列出它们（每项包含 `name` 和 `previewImageUrls` 供您展示），并将所选 id 作为 `referenceId` 在第一消息中传递给项目，从而其风格指南为整体设计提供 seed。

**识别您的工具**：始终发送 `source`，即发起请求的工具的 slug。Sleek 编辑器在运行流式传输时会用它向用户展示正在设计的人员。支持的取值：`claude-code`、`claude`、`codex`、`chatgpt`、`cursor`、`openclaw`、`grok`。若您的工具未列出，仍请发送其短的 kebab-case slug（最大 64 字符）。无法识别的取值不会造成影响，会获得通用标签。

**实时监控**：运行在 Sleek 编辑器中实时渲染。发送第一条项目消息后，告知用户可在 Sleek 中实时查看屏幕设计过程，并分享编辑器链接：`https://sleek.design/project/:projectId`。除非用户要求，否则不要自行打开浏览器。

**轮询**：聊天消息默认异步：您将获得 `runId` 并轮询 `GET /api/v1/projects/:id/chat/runs/:runId`。初始间隔 2 秒，10 秒后退避至 5 秒，5 分钟放弃。在状态为 `completed` 或 `failed` 时退出；若无法读取状态，应停止并报告，而非将其计为“尚未完成”。也可使用 `?wait=true` 进行阻塞调用（最长 300 秒；超时返回 `202` 时回退到轮询）。

**编辑特定屏幕**：使用 `target.screenId` 将修改导向正确的屏幕。`screenId` 来自运行结果的 `result.operations`，或来自 `GET /api/v1/projects/:id/components` 返回的每个组件的 `screenId` 字段；它不是组件 ID。

**一次运行一次**：每个项目仅允许一个活跃运行。若收到 `409 CONFLICT`，需等待当前运行完成后再发送下一条消息。若用户改变主意或停滞的运行阻塞了项目，需取消它（参见 [取消运行](#chat-cancel-run)）。不同项目的消息可并行运行；并行运行多个项目时使用异步轮询（而非 `?wait=true`）。

**安全重试**：在可安全重发时，添加 `idempotency-key` 请求头（≤255 字符）。服务器将返回已有运行，而非创建重复运行。

### 3. 展示结果

每次产生 `screen_created` 或 `screen_updated` 操作的聊天运行完成后，**需使用 `POST /api/v1/screenshots` 截取屏幕截图并展示给用户**。该步骤仅在用户看到运行创建或更新后每个屏幕的截图时才算完成；切勿静默完成运行。

- **新屏幕**：每个屏幕一张截图，外加一张所有屏幕的合并截图。
- **已更新屏幕**：每个受影响屏幕一张截图。

除非用户明确要求特定背景色，否则使用 `background: "transparent"`。

将截图保存在项目目录中（而非临时文件夹），以便用户能轻松查看。

**展示与审查**：默认仅捕获视口，这是面向用户的正确裁剪方式——屏幕呈现为手机屏幕。但对于评审自身产出，这是错误的裁剪方式，因为折叠线以下的内容均被截取。在评审运行产出的内容时，需使用 `fullHeight: true`（每次请求一个屏幕）重新截屏，以查看完整的可滚动页面。

截图请求相互独立，应并行发出——面向用户的截图与自身的 `fullHeight` 评审截图同步发出，不同屏幕的截图也同步发出。"每次请求一个屏幕"规范的是每个图像中的内容，而非发送速度；并非等待一个响应才开始下一个。仅在确实收到 `429` 时退避。

**切勿仅凭视口截图判定屏幕不完整**。看起来缺失的内容几乎总是在折叠线以下。在向用户报告缺失内容或发送要求 Sleek 补充的后续消息之前，需结合整屏进行确认：使用 `fullHeight: true` 截图，或从 `GET /api/v1/projects/:id/components/:componentId` 获取组件 HTML，这是屏幕上内容的唯一权威来源。截图是默认选择，且能单独回答大多数评审问题——无需去查看代码以核实其已展示的内容。仅当即将声称存在缺失内容时，才需要查阅代码：渲染可能省略实际存在的内容（超出高度上限、在折叠区域、在后续轮播页面上），因此负向结论才是值得二次核实的结论。同样注意反向情况——HTML 中存在的元素，用户可能仍无法看到。

---

## 实现设计

当用户希望以代码实现设计（而非仅预览）时，**始终获取组件 HTML 代码**。不要仅依赖截图。

使用 `GET /api/v1/projects/:id/components/:componentId` 获取每个屏幕的代码。`componentId` 来自聊天运行的 `result.operations`。

组件代码可能较大。将代码保存为文件时，避免通过文本输出写入内容：速度较慢且浪费 token。相反，使用 shell 命令获取 API 响应并直接写入磁盘（如将响应体管道至文件）。

### 使用哪个版本

每个组件包含 `versions[]` 数组和 `activeVersion: number`。**默认使用 `versions[i].version === activeVersion` 的条目**：即 Sleek 中当前展示的代码。

若用户提示词固定了特定版本，则遵循这些版本（见下方 [固定版本](#pinned-versions)）。

### 固定版本

用户提示词可能包含固定块，指示您实施特定历史版本而非当前版本，示例如下：

```
... 以项目当前版本之外的状态实现：
- component cmp_abc: version ver_001
- component cmp_def: version ver_002
- theme thm_ghi: version ver_003
```

看到固定块时，实施这些确切版本，而非 `activeVersion`。固定块未命名的组件继续使用其活跃版本。主题 ID 仅在固定块中出现；本技能未暴露独立的枚举端点。

#### 获取正确的代码

对每个固定组件，在 `versions[]` 中找到 `versions[i].id` 与给定版本 id（如 `ver_001`）匹配的条目，并使用其 `code`。**切勿**为固定组件回退到 `activeVersion`。

#### 固定版本的截图

向 `POST /api/v1/screenshots` 传递 `componentVersionOverrides` 和 `themeVersionOverrides`：

```json
{
  "componentIds": ["cmp_abc"],
  "projectId": "proj_xyz",
  "componentVersionOverrides": { "cmp_abc": "ver_001" },
  "themeVersionOverrides": { "thm_ghi": "ver_003" }
}
```

键为组件 / 主题的公开 id；值为对应的 `versions[i].id`。映射中缺失的实体回退到其活跃版本。当提示词指定了固定版本时，始终包含覆盖映射。

### HTML 原型

组件的 `code` 是完整的 HTML 文档。直接保存为 `.html` 文件。无需构建步骤。

### 原生框架（React Native、SwiftUI 等）

结合 HTML 代码与截图使用：

- **HTML 代码**是实现参考：包含确切的结构、布局、样式、颜色、间距、内容、图片 URL 和图标名称。
- **截图**是视觉目标：用于验证实现与预期外观一致。

HTML 告诉您如何构建；截图告诉您应呈现何种外观。

#### 图标

Sleek 使用 [Iconify](https://iconify.design) 图标，格式为 `prefix:name`（例如 `solar:heart-bold`、`material-symbols:search-rounded`、`lucide:settings`）。最常用的集合为 **Solar**、**Hugeicons**、**Material Symbols** 和 **MDI**。

**使用 HTML 代码中精确的图标**。勿用不同图标集替代。图标匹配对设计保真度至关重要。

实现图标时：

1. **检查项目是否已有支持 Sleek 使用相同集合的图标系统**（Solar、Hugeicons、Material Symbols、MDI）。若有，则使用。注意：`@expo/vector-icons` **不支持**这些集合，故不可作为替代。
2. **否则，从 Iconify API 获取 SVG 并嵌入代码中**：

   ```
   GET https://api.iconify.design/{prefix}/{name}.svg
   ```

   示例：`https://api.iconify.design/solar/heart-bold.svg`

   收集 HTML 中所有的图标名称，获取其 SVG，并保存为代码库中的静态资源或字符串常量。对于 **React Native / Expo**，使用 `react-native-svg` 的 `SvgXml` 组件进行渲染，该组件在 Expo Go 中无需额外原生依赖即可工作。

#### 字体

HTML 通过 `<head>` 中的 `<link>` 标签引入 Google Fonts。在原生框架中实现时，需使用相同的字体和字重。从 `<link>` 标签中提取字体族名和字重。

#### 导航

设计可能包含导航元素，如标签栏和页头。需更新项目的导航样式与结构以匹配设计。不要仅实现屏幕内容而保留默认导航不变。

---

## 快速参考：所有接口

| 方法   | 路径                                           | 权限范围             | 说明           |
| ------ | ---------------------------------------------- | -------------------- | -------------- |
| `GET`  | `/api/v1/projects`                             | `projects:read`      | 列出项目       |
| `POST` | `/api/v1/projects`                             | `projects:write`     | 创建项目       |
| `GET`  | `/api/v1/projects/:id`                         | `projects:read`      | 获取项目       |
| `DELETE` | `/api/v1/projects/:id`                        | `projects:write`     | 删除项目       |
| `GET`  | `/api/v1/projects/:id/components`              | `components:read`    | 列出组件       |
| `GET`  | `/api/v1/projects/:id/components/:componentId` | `components:read`    | 获取组件       |
| `GET`  | `/api/v1/references`                           | 任意有效密钥         | 列出参考       |
| `POST` | `/api/v1/projects/:id/chat/messages`           | `chats:write`        | 发送聊天消息   |
| `GET`  | `/api/v1/projects/:id/chat/runs/:runId`        | `chats:read`         | 轮询运行状态   |
| `POST` | `/api/v1/projects/:id/chat/runs/:runId/cancel` | `chats:write`        | 取消运行       |
| `POST` | `/api/v1/screenshots`                          | `screenshots`        | 渲染截图       |

---

## 接口

### 项目

#### 列出项目

```http
GET /api/v1/projects?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`：

```json
{
  "data": [
    {
      "id": "proj_abc",
      "name": "My App",
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

{ "name": "My New App" }
```

响应 `201`：与单个项目相同的结构。

#### 获取 / 删除项目

```http
GET    /api/v1/projects/:projectId
DELETE /api/v1/projects/:projectId   →  204 No Content
```

---

### 组件

#### 列出组件

```http
GET /api/v1/projects/:projectId/components?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

列表与获取均接受可选的 `inlineIcons` 查询参数（默认 `false`）。未提供时，图标渲染为 `<iconify-icon>` Web 组件，HTML 会引入 Iconify 脚本，故默认不启用。仅当消费方需要在 HTML 中获得自包含的 SVG（例如导入到不运行脚本的工具中）时，才使用 `?inlineIcons=true`。

响应 `200`：

```json
{
  "data": [
    {
      "id": "cmp_xyz",
      "screenId": "scr_xyz",
      "name": "Hero Section",
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

按 ID 获取单个组件。当需要特定屏幕的代码时（如聊天运行返回 `componentId` 时）使用此端点。

```http
GET /api/v1/projects/:projectId/components/:componentId
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`：`{ "data": ... }`，其中 `data` 包含单个组件，结构与列表项相同。

---

### 参考

参考是精选自 Sleek 精选项目的风格。全局可读：任何有效 API 密钥均可列出，无需权限范围。

```http
GET /api/v1/references?limit=50&offset=0
Authorization: Bearer $SLEEK_API_KEY
```

响应 `200`：

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

要使用某项，需在 [发送消息](#chat-send-message) 中以其 `id` 作为 `referenceId`。

---

### 聊天：发送消息

这是核心操作：在 `message.text` 中描述需求，AI 将创建或修改屏幕。

```http
POST /api/v1/projects/:projectId/chat/messages?wait=false
Authorization: Bearer $SLEEK_API_KEY
Content-Type: application/json
idempotency-key: <optional, max 255 chars>

{
  "message": { "text": "Add a pricing section with three tiers" },
  "source": "claude-code",
  "imageUrls": ["https://example.com/ref.png"],
  "target": { "screenId": "scr_abc" },
  "referenceId": "proj_ref1"
}
```

| 字段                    | 必需 | 说明                                                                                    |
| ------------------------ | ---- | -------------------------------------------------------------------------------------- |
| `message.text`           | 是   | 1+ 字符，去除首尾空白                                                                    |
| `source`                 | 视为必需 | 发起请求的工具的 slug（见 [设计](#2-send-a-chat-message) 第 2 步） |
| `imageUrls`              | 否   | 仅限 HTTPS URL；作为视觉上下文包含                                                |
| `target.screenId`        | 否   | 使用其 `screenId` 编辑特定屏幕（来自运行操作或组件列表；非 `componentId`）；省略则让 AI 决定 |
| `referenceId`            | 否   | 从参考（见 [参考](#references)）seed 设计风格；无效 id → `400` |
| `?wait=true/false`       | 否   | 同步等待模式（默认：false）                                                        |
| `idempotency-key` 请求头 | 否   | 可安全重发重传                                                                         |

#### 响应：异步（默认，`wait=false`）

状态 `202 Accepted`。`result` 和 `error` 在运行达到终止状态前均不存在。

```json
{
  "data": {
    "runId": "run_111",
    "status": "queued",
    "statusUrl": "/api/v1/projects/proj_abc/chat/runs/run_111"
  }
}
```

#### 响应：同步（`wait=true`）

最多阻塞 **300 秒**。完成后返回 `200`，超时返回 `202`。

```json
{
  "data": {
    "runId": "run_111",
    "status": "completed",
    "statusUrl": "...",
    "result": {
      "assistantText": "I added a pricing section with...",
      "operations": [
        {
          "type": "screen_created",
          "screenId": "scr_xyz",
          "screenName": "Pricing",
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

异步发送后使用此端点检查进度。

```http
GET /api/v1/projects/:projectId/chat/runs/:runId
Authorization: Bearer $SLEEK_API_KEY
```

响应 `data` 结构与发送消息相同：状态为 `completed` 时存在 `result`，为 `failed` 时存在 `error`：

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

将 `queued` 或 `running` 运行标记为 `failed`，错误码为 `cancelled`，并返回更新后的运行；已完成的运行原样返回。当用户在运行中改变主意，或停滞的运行以 `409 CONFLICT` 阻塞项目时使用此端点。

---

### 截图

截取一个或多个渲染后的组件的快照。

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

| 字段                          | 默认值       | 说明                                                                                                                                      |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `format`                      | `png`        | `png` 或 `webp`                                                                                                                            |
| `scale`                       | `2`          | 1–3（设备像素比）                                                                                                                       |
| `gap`                         | `40`         | 组件之间的像素间距                                                                                                                       |
| `padding`                     | `40`         | 各方向的统一内边距                                                                                                                       |
| `paddingX`                    | 可选         | 水平内边距；提供时覆盖左右方向的内边距                                                                                                |
| `paddingY`                    | 可选         | 垂直内边距；提供时覆盖上下方向的内边距                                                                                                |
| `paddingTop`                  | 可选         | 顶部内边距；提供时覆盖 `paddingY`                                                                                                       |
| `paddingRight`                | 可选         | 右侧内边距；提供时覆盖 `paddingX`                                                                                                       |
| `paddingBottom`               | 可选         | 底部内边距；提供时覆盖 `paddingY`                                                                                                       |
| `paddingLeft`                 | 可选         | 左侧内边距；提供时覆盖 `paddingX`                                                                                                       |
| `background`                  | `transparent`| 任意 CSS 颜色（十六进制、命名、`transparent`）                                                                                         |
| `showDots`                    | `false`      | 在背景上叠加细微的点阵                                                                                                                  |
| `fullHeight`                  | `false`      | 捕获整个可滚动屏幕而非仅视口（见下文）                                                                                                 |
| `radius`                      | `48`         | 每个组件的圆角半径（像素，整数 ≥ 0）；传 `0` 表示尖角                                                                                |
| `componentVersionOverrides`   | 可选         | 渲染固定版本而非 `activeVersion` 的映射：`componentId` → `versions[i].id`（见 [固定版本](#pinned-versions)）                      |
| `themeVersionOverrides`       | 可选         | 使用固定主题版本渲染的映射：`themeId` → `versions[i].id`（见 [固定版本](#pinned-versions)）                                        |

内边距按以下优先级解析：单侧 → 轴线 → 统一。例如，`paddingTop` 回退至 `paddingY`，`paddingY` 再回退至 `padding`。因此 `{ "padding": 20, "paddingX": 10, "paddingLeft": 5 }` 得到上下 20px、右侧 10px、左侧 5px。

默认在帧高度处捕获组件，用户通过滚动可到达的内容会被截取。`fullHeight: true` 会在捕获前将每个帧扩展至其内容的完整高度。评审自身产出时使用此选项；向用户展示的截图保持默认，手机形裁剪才是其核心要点。

帧高度最多限制为默认帧高度的 **4 倍**，因此屏幕即使使用 `fullHeight: true`，超过该高度部分仍会被底部截取。对于极长的屏幕，以下限以下的内容以组件 HTML 为权威。扩展后的帧会产生较高的图像；优先每次请求一个组件，使每个屏幕保持细节——而非串行发送请求。仅在确实收到 `429` 时退避。

当 `showDots` 为 `true` 时，会在背景色上绘制点阵。点的分布会自动适配背景：深色背景显示浅色点，浅色背景显示深色点。当 `background` 为 `"transparent"` 时，此设置无效果。

响应：原始二进制 `image/png` 或 `image/webp`，`Content-Disposition: attachment`。

---

## 错误格式

```json
{ "code": "UNAUTHORIZED", "message": "..." }
```

| HTTP | 代码                      | 发生条件                                                     |
| ---- | ------------------------- | ------------------------------------------------------------ |
| 401  | `UNAUTHORIZED`            | 缺失、无效或过期的 API 密钥                                   |
| 403  | `FORBIDDEN`               | 有效密钥，权限范围或套餐不符                                 |
| 404  | `NOT_FOUND`               | 资源不存在                                                   |
| 400  | `BAD_REQUEST`             | 验证失败                                                     |
| 409  | `CONFLICT`                | 该项目已有运行进行中                                           |
| 429  | `TOO_MANY_REQUESTS`       | 请求过多；退避后稍后重试                                       |
| 500  | `INTERNAL_SERVER_ERROR`   | 服务器错误                                                   |

`401`、`403` 和 `429` 的响应体可能包含 `data.url`：用户可在此页面修复条件（创建密钥、升级套餐）的页面。若存在，需向用户分享该 URL，而非自行临时生成。

聊天运行级别的错误（位于 `data.error` 内）：

| 代码               | 含义                     |
| ------------------ | ------------------------ |
| `out_of_credits`   | 组织无剩余额度           |
| `execution_failed` | AI 执行错误              |
| `cancelled`        | 通过取消端点取消运行     |

`out_of_credits` 错误包含 `error.url`，即用户可充值额度的页面。需将其传达给用户；在其充值前不得重试运行。

---

## 分页

所有列表端点接受 `limit`（1–100，默认 50）和 `offset`（≥0）。响应始终包含 `pagination.total`，以便您翻页获取所有结果。

```http
GET /api/v1/projects?limit=10&offset=20
```

---

## 常见错误

| 错误                                                                 | 修复                                                                                                  |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 聊天消息中省略 `source`                                              | 始终发送 `source`，以便运行在 Sleek 编辑器中被正确归因                                          |
| 在长生成中使用 `wait=true`                                           | 最长阻塞 300 秒；需针对返回 `202` 的情况设置轮询回退方案                                         |
| 假设 `202` 响应中包含 `result`                                      | `result` 在状态为 `completed` 前不存在                                                              |
| 将 JSON 响应通过 `echo` 管道解析                                           | zsh 会展开 `assistantText` 中的 `\n`，导致 JSON 失效；应从文件解析                                       |
| 将无法读取的运行状态视为“尚未完成”                                     | 后续循环会长时间超出上限循环；应停止并报告                                                          |
| 基于视口截图判定屏幕不完整                                            | 内容通常位于折叠线以下；需使用 `fullHeight: true` 重新截屏或在报告缺失内容前检查组件 HTML          |
| 截图时将 `screenId` 用作 `componentIds`                                | `screenId` 与 `componentId` 不同：每个屏幕均有两者（运行操作与组件列表均返回这对）。聊天消息的 `target.screenId` 使用 `screenId`；截图与组件读取使用 `componentId` |
| 混淆 `versions[i].version`（数字）与 `versions[i].id`（字符串）          | 解析固定版本时按 `id` 匹配（如 `ver_001`）；`version` 为数字索引                                       |
