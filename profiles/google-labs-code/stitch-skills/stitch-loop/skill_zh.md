# Stitch 构建循环

你是一个**自主前端构建器**，参与一个迭代的站点构建循环。你的目标是使用 Stitch 生成一个页面，将其集成到站点中，并为下一次迭代做准备。

## 概述

构建循环模式通过“接力棒”系统实现持续、自主的网站开发。每次迭代：
1. 从接力棒文件（`.stitch/next-prompt.md`）中读取当前任务
2. 使用 Stitch MCP 工具生成页面
3. 将页面集成到站点结构中
4. 为下一次迭代将下一个任务写入接力棒文件

## 前置条件

**必需：**
- Stitch MCP 服务器的访问权限
- 一个 Stitch 项目（已存在或将要创建）
- 一个 `.stitch/DESIGN.md` 文件（如有需要，使用 `design-md` 技能生成一个）
- 一个记录站点愿景和路线图的 `.stitch/SITE.md` 文件

**可选：**
- Chrome DevTools MCP 服务器 — 启用生成页面的可视化验证

## 接力棒系统

`.stitch/next-prompt.md` 文件作为迭代之间的接力棒：

```markdown
---
page: about
---
一个描述 jules.top 跟踪机制的页面。

**设计系统（必需）：**
[从 .stitch/DESIGN.md 第 6 节复制]

**页面结构：**
1. 带导航的页眉
2. 跟踪方法的解释
3. 带链接的页脚
```

**关键规则：**
- YAML 前置内容的 `page` 字段决定输出文件名
- 提示内容必须包含来自 `.stitch/DESIGN.md` 的设计系统块
- 你必须在完成工作之前更新此文件以继续循环

## 执行协议

### 第 1 步：读取接力棒

解析 `.stitch/next-prompt.md` 以提取：
- **页面名称** 从 `page` 前置内容字段
- **提示内容** 从 Markdown 正文

### 第 2 步：查阅上下文文件

生成之前，读取这些文件：

| 文件 | 目的 |
|------|---------|
| `.stitch/SITE.md` | 站点愿景、**Stitch 项目 ID**、现有页面（站点地图）、路线图 |
| `.stitch/DESIGN.md` | Stitch 提示所需的视觉样式 |

**重要检查：**
- 第 4 节（站点地图）— 不要重新创建站点地图中已存在的页面
- 第 5 节（路线图）— 如果有积压任务，从这里选择任务
- 第 6 节（创意自由）— 如果路线图为空，则为新页面提供想法

### 第 3 步：使用 Stitch 生成

使用 Stitch MCP 工具生成页面：

1. **发现命名空间**：运行 `list_tools` 找到 Stitch MCP 前缀
2. **获取或创建项目**： 
   - 如果存在 `.stitch/metadata.json`，使用其中的 `projectId`
   - 否则，调用 `[prefix]:create_project`，然后调用 `[prefix]:get_project` 获取完整项目详情，并将它们保存到 `.stitch/metadata.json`（见下方架构）
   - 生成每个屏幕后，再次调用 `[prefix]:get_project` 并更新 `.stitch/metadata.json` 中的 `screens` 映射，为每个屏幕添加完整的元数据（id、sourceScreen、尺寸、画布位置）
3. **生成屏幕**：调用 `[prefix]:generate_screen_from_text` 并传入：
   - `projectId`：项目 ID
   - `prompt`：接力棒中的完整提示（包括设计系统块）
   - `deviceType`：`DESKTOP`（或指定）
4. **检索资源**：下载前，检查 `.stitch/designs/{page}.html` 和 `.stitch/designs/{page}.png` 是否已存在：
   - **如果文件存在**：询问用户是否要从 Stitch 项目刷新设计或重用现有本地文件。只有在用户确认后才重新下载
   - **如果文件不存在**：继续下载：
     - `htmlCode.downloadUrl` — 下载并保存为 `.stitch/designs/{page}.html`
      - `screenshot.downloadUrl` — 下载前将 `=w{width}` 添加到 URL，其中 `{width}` 是屏幕元数据中的 `width` 值（Google CDN 默认提供低分辨率缩略图）。保存为 `.stitch/designs/{page}.png`

### 第 4 步：集成到站点

1. 将生成的 HTML 从 `.stitch/designs/{page}.html` 移动到 `site/public/{page}.html`
2. 修复任何资产路径以使其相对于公共文件夹
3. 更新导航：
   - 查找现有占位符链接（例如，`href="#"`）并将其连接到新页面
   - 如果合适，将新页面添加到全局导航
4. 确保所有页面的一致页眉/页脚

### 第 4.5 步：可视化验证（可选）

如果**Chrome DevTools MCP 服务器**可用，验证生成页面：

1. **检查可用性**：运行 `list_tools` 查看是否存在 `chrome*` 工具
2. **启动开发服务器**：使用 Bash 启动本地服务器（例如，`npx serve site/public`）
3. **导航到页面**：调用 `[chrome_prefix]:navigate` 打开 `http://localhost:3000/{page}.html`
4. **捕获截图**：调用 `[chrome_prefix]:screenshot` 捕获渲染后的页面
5. **视觉比较**：与 Stitch 截图（`.stitch/designs/{page}.png`）进行保真度比较
6. **停止服务器**：终止开发服务器进程

> **注意**：此步骤是可选的。如果未安装 Chrome DevTools MCP，则跳到第 5 步。

### 第 5 步：更新站点文档

修改 `.stitch/SITE.md`：
- 将新页面添加到第 4 节（站点地图）并标记为 `[x]`
- 从第 6 节（创意自由）中删除你已使用的想法
- 如果完成了积压任务，更新第 5 节（路线图）

### 第 6 步：准备下一个接力棒（关键）

**你必须完成工作前更新 `.stitch/next-prompt.md`。** 这能保持循环的运行。

1. **决定下一个页面**： 
   - 检查 `.stitch/SITE.md` 第 5 节（路线图）中的待处理项
   - 如果为空，从第 6 节（创意自由）中选择
   - 或者为站点愿景发明新内容
2. **编写接力棒** 并使用正确的 YAML 前置内容：

```markdown
---
page: achievements
---
一个展示开发者徽章和里程碑的竞争成就页面。

**设计系统（必需）：**
[复制 .stitch/DESIGN.md 的整个设计系统块]

**页面结构：**
1. 带标题和导航的页眉
2. 显示已解锁/锁定状态的徽章网格
3. 用于里程碑跟踪的进度条
```

## 文件结构参考

```
project/
├── .stitch/
│   ├── metadata.json   # Stitch 项目和屏幕 ID（持久化此文件！）
│   ├── DESIGN.md       # 视觉设计系统（来自 design-md 技能）
│   ├── SITE.md         # 站点愿景、站点地图、路线图
│   ├── next-prompt.md  # 接力棒 — 当前任务
│   └── designs/        # Stitch 输出的暂存区
│       ├── {page}.html
│       └── {page}.png
└── site/public/        # 生产页面
    ├── index.html
    └── {page}.html
```

### `.stitch/metadata.json` 架构

此文件持久化所有 Stitch 标识符，以便未来的迭代可以引用它们进行编辑或变体。通过调用 `[prefix]:get_project` 在创建项目或生成屏幕后填充它。

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

| 字段 | 描述 |
|-------|-------------|
| `name` | 完整资源名称（`projects/{id}`） |
| `projectId` | Stitch 项目 ID（来自 `create_project` 或 `get_project`） |
| `title` | 人类可读的项目标题 |
| `designTheme` | 设计系统标记：颜色模式、字体、圆角、自定义颜色、饱和度 |
| `deviceType` | 目标设备：`MOBILE`、`DESKTOP`、`TABLET` |
| `screens` | 页面名称 → 屏幕对象的映射。每个屏幕包括 `id`、`sourceScreen`（MCP 调用的资源路径）、画布位置（`x`、`y`）和尺寸（`width`、`height`） |
| `metadata.userRole` | 用户在项目中的角色（`OWNER`、`EDITOR`、`VIEWER`） |

## 协调选项

循环可以由不同的协调层驱动：

| 方法 | 工作原理 |
|--------|--------------|
| **CI/CD** | GitHub Actions 在 `.stitch/next-prompt.md` 变更时触发 |
| **人工参与** | 开发人员在继续之前审查每个迭代 |
| **代理链** | 一个代理派发给另一个（例如，Jules API） |
| **手动** | 开发人员使用相同代码库重复运行代理 |

此技能与触发机制无关 — 关注模式，而非触发方式。

## 设计系统集成

此技能与 `design-md` 技能配合最佳：

1. **首次设置**：使用 `design-md` 技能从现有 Stitch 屏幕生成 `.stitch/DESIGN.md`
2. **每次迭代**：将第 6 节（"用于 Stitch 生成的设计系统说明"）复制到你的接力棒提示中
3. **一致性**：所有生成的页面将共享相同的视觉语言

## 常见陷阱

- ❌ 忘记更新 `.stitch/next-prompt.md`（会中断循环）
- ❌ 重新创建站点地图中已存在的页面
- ❌ 提示中未包含来自 `.stitch/DESIGN.md` 的设计系统块
- ❌ 留下占位符链接（`href="#"`）而不是连接真实导航
- ❌ 忘记在创建新项目后持久化 `.stitch/metadata.json`

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| Stitch 生成失败 | 检查提示是否包含设计系统块 |
| 样式不一致 | 确保 `.stitch/DESIGN.md` 是最新的并正确复制 |
| 循环停滞 | 验证 `.stitch/next-prompt.md` 是否用有效的前置内容更新 |
| 导航中断 | 检查所有内部链接是否使用正确的相对路径 |
