# Stitch 构建循环

你是一名参与迭代式网站构建循环的 **自主前端构建者**。你的目标是使用 Stitch 生成页面，将其集成到网站中，并为下一轮迭代准备说明。

## 概览

Build Loop 模式通过 "接力棒"（baton）系统实现持续的、自主的网站开发。每个迭代：
1. 从接力棒文件（`.stitch/next-prompt.md`）中读取当前任务
2. 使用 Stitch MCP 工具生成页面
3. 将页面集成到网站结构中
4. 为下一轮迭代在接力棒文件中写入下一条任务

## 前提条件

**必需：**
- 访问 Stitch MCP Server 的权限
- 一个 Stitch 项目（已有或将在后续创建）
- `.stitch/DESIGN.md` 文件（如需，可使用 `design-md` 技能生成）
- `.stitch/SITE.md` 文件，记录网站愿景与路线图

**可选：**
- Chrome DevTools MCP Server — 用于生成页面的可视化验证

## 接力棒系统

`.stitch/next-prompt.md` 文件在迭代之间起到接力棒的作用：

```markdown
---
page: about
---
一个描述 jules.top 追踪功能的页面。

**DESIGN SYSTEM (REQUIRED):**
[从 .stitch/DESIGN.md Section 6 复制]

**页面结构：**
1. 带导航的页眉
2. 追踪方法说明
3. 带链接的页脚
```

**重要规则：**
- YAML frontmatter 中的 `page` 字段决定输出文件名
- 提示词内容必须包含 `.stitch/DESIGN.md` 中的设计系统区块
- 你必须在工作完成前更新此文件，以继续循环

## 执行协议

### Step 1：读取接力棒

解析 `.stitch/next-prompt.md`，提取：
- 从 `page` frontmatter 字段中提取 **页面名称**
- 从 markdown 正文提取 **提示词内容**

### Step 2：查阅上下文文件

生成前，请阅读以下文件：

| 文件 | 用途 |
|------|---------|
| `.stitch/SITE.md` | 网站愿景、**Stitch 项目 ID**、已有页面（站点地图）、路线图 |
| `.stitch/DESIGN.md` | Stitch 提示词所需的视觉风格 |

**重要检查：**
- Section 4（站点地图）—— 请勿重复创建已存在的页面
- Section 5（路线图）—— 如有积压任务，从此处选取任务
- Section 6（创意自由）—— 如路线图为空，从中挑选新页面创意

### Step 3：使用 Stitch 生成

使用 Stitch MCP 工具生成页面：

1. **发现命名空间**：运行 `list_tools` 以找到 Stitch MCP 前缀
2. **获取或创建项目**：
   - 如果 `.stitch/metadata.json` 存在，使用其中的 `projectId`
   - 否则，调用 `[prefix]:create_project`，然后调用 `[prefix]:get_project` 获取完整项目详情，并保存到 `.stitch/metadata.json`（参见下方 schema）
   - 生成每个屏幕后，再次调用 `[prefix]:get_project`，并根据每个屏幕的完整元数据（id、sourceScreen、尺寸、画布位置）更新 `.stitch/metadata.json` 中的 `screens` 映射
3. **生成屏幕**：调用 `[prefix]:generate_screen_from_text`，参数包括：
   - `projectId`：项目 ID
   - `prompt`：接力棒中的完整提示词（包含设计系统区块）
   - `deviceType`：`DESKTOP`（或按指定值）
4. **获取资源**：下载前，检查 `.stitch/designs/{page}.html` 和 `.stitch/designs/{page}.png` 是否已存在：
   - **如果文件已存在**：询问用户是否要从 Stitch 项目刷新设计，还是复用现有本地文件。仅在用户确认时才重新下载。
   - **如果文件不存在**：继续下载：
     - `htmlCode.downloadUrl` — 下载并保存为 `.stitch/designs/{page}.html`
     - `screenshot.downloadUrl` — 下载前将 URL 追加 `=w{width}`，其中 `{width}` 为屏幕元数据中的 `width` 值（Google CDN 默认提供低分辨率缩略图）。保存为 `.stitch/designs/{page}.png`

### Step 4：集成到网站

1. 将生成的 HTML 从 `.stitch/designs/{page}.html` 移动到 `site/public/{page}.html`
2. 修复所有资源路径，使其相对于 public 文件夹
3. 更新导航：
   - 找到现有的占位链接（例如 `href="#"`）并将其连接到新页面
   - 如适用，将新页面添加到全局导航中
4. 确保所有页面之间的页眉/页脚保持一致

### Step 4.5：可视化验证（可选）

如果 **Chrome DevTools MCP Server** 可用，验证生成的页面：

1. **检查可用性**：运行 `list_tools` 查看是否包含 `chrome*` 工具
2. **启动开发服务器**：使用 Bash 启动本地服务器（例如 `npx serve site/public`）
3. **导航至页面**：调用 `[chrome_prefix]:navigate` 打开 `http://localhost:3000/{page}.html`
4. **截图**：调用 `[chrome_prefix]:screenshot` 截取渲染后的页面
5. **可视化对比**：与 Stitch 截图（`.stitch/designs/{page}.png`）对比，确认保真度
6. **停止服务器**：终止开发服务器进程

> **注意**：此步骤为可选。如果未安装 Chrome DevTools MCP，请跳过至第 5 步。

### Step 5：更新网站文档

修改 `.stitch/SITE.md`：
- 在 Section 4（站点地图）中新增该页面，并标记为 `[x]`
- 从 Section 6（创意自由）中移除已消耗的创意
- 如完成了积压任务，更新 Section 5（路线图）

### Step 6：准备下一接力棒（关键）

**你必须在工作完成前更新 `.stitch/next-prompt.md`。** 这是保持循环运行的关键。

1. **确定下一页面**：
   - 检查 `.stitch/SITE.md` Section 5（路线图）中的待办项
   - 如为空，从 Section 6（创意自由）中选取
   - 或构思符合网站愿景的新内容
2. **撰写接力棒**，包含正确的 YAML frontmatter：

```markdown
---
page: achievements
---
一个展示开发者徽章和里程碑的竞争性成就页面。

**DESIGN SYSTEM (REQUIRED):**
[完整复制 .stitch/DESIGN.md 中的设计系统区块]

**页面结构：**
1. 带标题和导航的页眉
2. 展示已解锁/未解锁状态的徽章网格
3. 用于里程碑追踪的进度条
```

## 文件结构参考

```
project/
├── .stitch/
│   ├── metadata.json   # Stitch 项目与屏幕 ID（请持久化保存！）
│   ├── DESIGN.md       # 视觉设计系统（来自 design-md 技能）
│   ├── SITE.md         # 网站愿景、站点地图、路线图
│   ├── next-prompt.md  # 接力棒——当前任务
│   └── designs/        # Stitch 输出的暂存区
│       ├── {page}.html
│       └── {page}.png
└── site/public/        # 生产页面
    ├── index.html
    └── {page}.html
```

### `.stitch/metadata.json` Schema

该文件持久化所有 Stitch 标识符，以便后续迭代能够引用它们进行编辑或变体修改。在创建项目或生成屏幕后，通过调用 `[prefix]:get_project` 进行填充。

```json
{
  "name": "projects/6139132077804554844",
  "projectId": "6139132077804554844",
  "title": "My App",
  "visibility": "PRIVATE",
  "createTime": "2026-03-04T23:11:25.514932Z",
  "updateTime": "2026-03-04T23:34:40.400007Z",
  "projectType": "PROJECT_DESIGN",
  "origin": "STITCH",
  "deviceType": "MOBILE",
  "designTheme": {
    "colorMode": "DARK",
    "font": "INTER",
    "roundness": "ROUND_EIGHT",
    "customColor": "#40baf7",
    "saturation": 3
  },
  "screens": {
    "index": {
      "id": "d7237c7d78f44befa4f60afb17c818c1",
      "sourceScreen": "projects/6139132077804554844/screens/d7237c7d78f44befa4f60afb17c818c1",
      "x": 0,
      "y": 0,
      "width": 390,
      "height": 1249
    },
    "about": {
      "id": "bf6a3fe5c75348e58cf21fc7a9ddeafb",
      "sourceScreen": "projects/6139132077804554844/screens/bf6a3fe5c75348e58cf21fc7a9ddeafb",
      "x": 549,
      "y": 0,
      "width": 390,
      "height": 1159
    }
  },
  "metadata": {
    "userRole": "OWNER"
  }
}
```

| 字段 | 说明 |
|-------|-------------|
| `name` | 完整资源名称（`projects/{id}`） |
| `projectId` | Stitch 项目 ID（来自 `create_project` 或 `get_project`） |
| `title` | 人类可读的项目标题 |
| `designTheme` | 设计系统令牌：配色模式、字体、圆角、自定义颜色、饱和度 |
| `deviceType` | 目标设备：`MOBILE`、`DESKTOP`、`TABLET` |
| `screens` | 页面名称 → 屏幕对象的映射。每个屏幕包含 `id`、`sourceScreen`（MCP 调用时的资源路径）、画布位置（`x`、`y`）和尺寸（`width`、`height`） |
| `metadata.userRole` | 用户在项目中的角色（`OWNER`、`EDITOR`、`VIEWER`） |

## 编排选项

循环可由不同的编排层驱动：

| 方法 | 运作方式 |
|--------|--------------|
| **CI/CD** | GitHub Actions 在 `.stitch/next-prompt.md` 变更时触发 |
| **人工介入循环** | 开发者在继续前审核每一轮迭代 |
| **Agent 链** | 一个 Agent 调度给另一个（例如 Jules API） |
| **手动** | 开发者在同一仓库中重复运行 Agent |

该技能与编排方式无关——关注模式，而非触发机制。

## 设计系统集成

此技能与 `design-md` 技能配合效果最佳：

1. **首次设置**：使用 `design-md` 技能基于现有 Stitch 屏幕生成 `.stitch/DESIGN.md`
2. **每轮迭代**：将 Section 6（"用于 Stitch 生成的设计系统说明"）复制到你的接力棒提示词中
3. **一致性**：所有生成的页面将共享相同的视觉语言

## 常见陷阱

- ❌ 忘记更新 `.stitch/next-prompt.md`（会中断循环）
- ❌ 重复创建站点地图中已存在的页面
- ❌ 在提示词中不包含 `.stitch/DESIGN.md` 中的设计系统区块
- ❌ 不将占位链接（`href="#"`）连接到真实导航
- ❌ 创建新项目后忘记持久化 `.stitch/metadata.json`

## 故障排查

| 问题 | 解决方案 |
|-------|----------|
| Stitch 生成失败 | 检查提示词是否包含设计系统区块 |
| 样式不一致 | 确保 `.stitch/DESIGN.md` 为最新并正确复制 |
| 循环停滞 | 验证 `.stitch/next-prompt.md` 是否更新了有效的 frontmatter |
| 导航损坏 | 检查所有内部链接是否使用正确的相对路径 |
