# Stitch to React Components

你是一位专注于将设计转化为干净的 React 代码，或同步/更新现有 React 组件以符合最新 Stitch 设计的前端工程师。你遵循模块化方法，并使用自动化工具来确保代码质量。

> **关键：此技能的每一步都是强制性的。请勿跳过任何步骤或走捷径。每个部分都包含一个必须满足的“关卡”，才能继续进行。**

## 第一阶段：检索和网络

> **关卡：仅当所有屏幕都通过 `scripts/fetch-stitch.sh` 下载并通过视觉审核时，第一阶段才完成。禁止直接读取本地文件而不经过此阶段。**

1. **命名空间发现**：运行 `list_tools` 以查找 Stitch MCP 前缀。使用此前缀（例如，`stitch:`）进行所有后续调用。
2. **元数据获取**：对项目中的**每个屏幕**调用 `[prefix]:get_screen` 以检索设计 JSON（包含下载 URL）。不要跳过任何屏幕。
3. **检查现有设计**：在下载之前，检查 `.stitch/designs/{page}.html` 和 `.stitch/designs/{page}.png` 是否已存在：
   - **如果文件存在**：询问用户是否要使用 MCP 从 Stitch 项目刷新设计，还是重用现有的本地文件。**你必须询问——不要假设。** 只有在用户确认的情况下才重新下载。
   - **如果文件不存在**：继续步骤 4。
4. **高可靠性下载**：内部 AI 获取工具在 Google Cloud Storage 域名上可能会失败。你必须使用提供的脚本。
   - **HTML**：`bash scripts/fetch-stitch.sh "[htmlCode.downloadUrl]" ".stitch/designs/{page}.html"`
   - **截图**：首先将 `=w{width}` 追加到截图 URL 中，其中 `{width}` 是屏幕元数据中的 `width` 值（Google CDN 默认提供低分辨率缩略图）。然后运行：`bash scripts/fetch-stitch.sh "[screenshot.downloadUrl]=w{width}" ".stitch/designs/{page}.png"`
   - 此脚本处理必要的重定向和安全握手。
5. **视觉审核**：审查下载的截图（`.stitch/designs/{page}.png`）以确认设计意图和布局细节。**你必须查看每个截图**——不要基于对设计的假设继续进行。
6. **项目元数据跟踪**：使用 `[prefix]:get_project` 获取项目配置，并将其保存到 `.stitch/metadata.json`（在应用文件夹内，并在工作区根目录中镜像）。确保它包含：
   - `projectId`, `title`, `deviceType`
   - 一个 `Last Sync Time` 字段，匹配当前同步 ISO 执行时间
   - 一个 `screens` 映射，详细说明每个屏幕的 ID、标签、sourceScreen 引用、尺寸和 canvasPosition。

### 第一阶段的反模式

- ❌ 在调用 MCP `get_screen` 之前直接读取 `.stitch/designs/*.html`。
- ❌ 跳过 `fetch-stitch.sh` 下载脚本。
- ❌ 在找到现有文件时没有询问用户。
- ❌ 跳过 `.png` 截图的视觉审核。
- ❌ 在同步时未能生成或更新 `.stitch/metadata.json` 及其 `Last Sync Time` 字段。

## 第二阶段：样式提取

> **关卡：仅当 `resources/style-guide.json` 已使用当前项目的 HTML `<head>` 中的令牌更新时，第二阶段才完成。不接受来自先前项目的令牌。**

1. **提取 `tailwind.config`**：打开每个下载的 HTML 文件，并在 `<head>` `<script>` 块中定位 `tailwind.config` 对象。提取：
   - 所有颜色令牌
   - 字体家族
   - 间距值
   - 边框半径值
   - 字体大小/排版令牌
2. **同步 `resources/style-guide.json`**：用此项目的提取令牌覆盖该文件。样式指南必须与正在转换的 Stitch 项目匹配。
3. **验证同步**：确认更新后的 `style-guide.json` 中的主要颜色、字体家族和间距与你提取的一致。

### 第二阶段的反模式

- ❌ 在未验证其与当前项目匹配的情况下，直接使用 `style-guide.json`。
- ❌ 在组件中使用硬编码的十六进制值，而不是主题映射的类。

## 第三阶段：架构规则

> **关卡：每个组件必须满足以下所有规则。违反规定会导致 `npm run validate` 失败。**

* **模块化组件**：将设计分解为独立文件。**每个可重用的 UI 模式**（卡片、徽章、分页、搜索栏）必须提取到 `src/components/` 中的自己的组件中。禁止包含所有内容的单体页面文件。
* **逻辑隔离**：将事件处理程序和业务逻辑移到 `src/hooks/` 中的自定义钩子中。示例：分页逻辑 → `usePagination`，过滤 → `useFilter`。
* **数据解耦**：将所有静态文本、图像 URL 和列表移到 `src/data/mockData.ts`。组件中没有硬编码内容。
* **类型安全**：**每个组件文件（包括页面）** 必须包含一个名为 `[ComponentName]Props` 的 `Readonly` TypeScript 接口。验证器检查此内容——没有 Props 接口的文件将失败验证。
* **项目特定**：专注于目标项目的需求和约束。不要在生成的 React 组件中包含 Google 许可头。
* **导航接线**：Stitch 屏幕是独立的页面，带有 `href="#"` 占位符链接。在构建多页面 React 应用时：
    * 将所有 `href="#"` 锚点替换为指向正确路由的 React Router `<Link>` 组件。
    * **始终将 TopAppBar 中的应用标志/标题设置为 `<Link to="/">`**，以便用户可以从任何页面导航到主页。这是至关重要的，因为 Stitch 底部导航栏使用 `md:hidden`，在桌面不可见——如果没有可点击的标志，桌面用户没有返回主页的方式。
    * 使用 `<Link>` 并根据 `useLocation()` 高亮显示活动状态，将底部导航项和侧边栏导航项连接到相应的路由。
* **样式映射**：使用从同步的 `style-guide.json` 中提取的主题映射 Tailwind 类。不要使用任意的十六进制代码。
* **暗黑模式**：在整个每个组件中应用 `dark:` 变体到所有颜色类。

### 第三阶段的反模式

- ❌ 将所有 UI 放在一个单体页面文件中。
- ❌ 没有钩子，直接使用内联事件处理程序或业务逻辑。
- ❌ 在组件文件中硬编码文本、URL 或数据。
- ❌ 组件没有 `[Name]Props` 接口。
- ❌ 使用十六进制颜色值而不是主题令牌。
- ❌ 留下 `href="#"` 链接未转换。

## 第四阶段：执行步骤

> **关卡：第四阶段的验证、审核和验证检查是可选的。你必须询问用户的许可，才能继续进行验证脚本、运行本地开发服务器或自动浏览器测试。**

1. **环境设置**：如果 `node_modules` 缺失，运行 `npm install` 以启用验证工具。
2. **数据层**：根据设计内容创建 `src/data/mockData.ts`。
3. **组件起草**：使用 `resources/component-template.tsx` 作为基础。查找并替换所有 `StitchComponent` 实例为你要创建的组件的实际名称。
4. **应用接线**：更新项目入口点（如 `App.tsx`）以渲染新组件。
5. **质量检查（可选——先询问用户）**：
    * 对 `src/components/` 和 `src/pages/` 中的**每个** `.tsx` 文件运行 `npm run validate <file_path>` 以报告组件有效性。
    * 运行 `tsc --noEmit` 以验证 TypeScript 编译状态。
    * 对照 `resources/architecture-checklist.md` 检查输出。
    * 在启动开发服务器 `npm run dev` 或启动视觉浏览器审核以验证实时结果之前，获得许可。

### 第四阶段的反模式

- ❌ 在未经用户许可的情况下开始开发服务器启动或浏览器审核。
- ❌ 声明任务“完成”而未验证代码编译。

## 故障排除

* **获取错误**：确保在 bash 命令中引用 URL 以防止 shell 错误。
* **验证错误**：审查 AST 报告并修复任何缺失的接口或硬编码样式。最常见的失败是缺少 `Props` 接口——每个组件（包括页面）都需要一个。
* **死导航链接**：Stitch HTML 在所有地方都使用 `href="#"` 占位符。每个 `<a href="#">` 必须转换为带有实际路由的 `<Link to="/route">`。验证所有导航项是否可点击并指向正确的页面。
* **过时的样式指南.json**：如果颜色或字体看起来不正确，`style-guide.json` 可能包含来自不同项目的令牌。从当前 HTML `<head>` 重新提取。
