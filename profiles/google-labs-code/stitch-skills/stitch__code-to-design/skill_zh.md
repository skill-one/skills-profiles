# 代码设计

将您现有的前端代码（React + Vite、Next.js、Angular、Vue 等）转换为 Stitch Design，以便您可以使用 Stitch 进行迭代和改进。

这项技能按顺序协调其他三项技能：
1. `extract-static-html`：从您的构建输出或运行中的开发服务器（例如 Vite 开发服务器或 Angular CLI `ng serve`）中提取一个自包含的 HTML 文件。
2. `extract-design-md`：分析源代码（包括 Angular `angular.json`、外部 `.html` 模板、主题文件和组件）以创建设计系统（DESIGN.md）。
3. `upload-to-stitch`：将那个 HTML 文件和设计系统上传到您的 Stitch 项目。

## 工作流程

按照以下步骤转换您的现有代码。

### 前置条件

- 一个运行中的本地开发服务器（例如 `npm run dev`、`ng serve`）或包含 `index.html` 和资源的构建后的 Web 应用程序目录。
- 目标 Stitch `projectId`（如果未知，请使用 `list_projects`）。

### 步骤

#### 1. 提取自包含 HTML

委托给 `extract-static-html` 技能生成一个独立的 HTML 文件。
阅读 [skills/extract-static-html/SKILL.md](../extract-static-html/SKILL.md) 获取详细说明和脚本使用方法。

预期输出：一个类似 `/path/to/extracted/standalone.html` 的单个文件。

#### 2. 验证 HTML（可选 — 用户驱动）

提取后，通知用户输出文件路径，以便他们可以在浏览器中手动验证（如果需要）。**不要阻塞验证** — 直接进入步骤 3。

如果用户在查看后报告问题，请在继续之前修复它们。

#### 3. 提取设计系统（文件）

委托给 `extract-design-md` 技能分析项目的源文件（组件、样式表、主题配置）并生成设计系统。阅读 [skills/extract-design-md/SKILL.md](../extract-design-md/SKILL.md) 获取完整分析工作流程。

按照 `extract-design-md` 技能的输出结构编写 `.stitch/DESIGN.md`。

#### 4. 上传 DESIGN.md 并在 Stitch 中创建设计系统

委托给 `manage-design-system` 技能上传 `DESIGN.md` 并在 Stitch 中创建设计系统。阅读 [skills/manage-design-system/SKILL.md](../manage-design-system/SKILL.md) 获取完整工作流程（上传脚本使用方法、`create_design_system_from_design_md` 调用以及所需的模式）。在上传时传递 `--generated-by 'stitch::code-to-design'`。

#### 5. 上传 HTML 到 Stitch

使用与步骤 4 相同的 `upload-to-stitch` 技能的脚本上传提取的 HTML 文件。
阅读 [skills/upload-to-stitch/SKILL.md](../upload-to-stitch/SKILL.md) 获取详细说明和脚本使用方法。

您需要：
- 步骤 1 中生成的独立 HTML 文件的路径。
- 您的 Stitch API 密钥（与步骤 4 中使用的相同密钥）。
- 目标 `projectId`。
- 将 `--generated-by` 参数设置为 `'stitch::extract-static-html'`。
- 将 `--title` 参数设置为页面的**路由路径**（例如 `'/dashboard'`、`'/settings/profile'`、`'/inbox'`），以便 Stitch 中的屏幕名称/标题能清楚地标识其在应用程序中的路由。
