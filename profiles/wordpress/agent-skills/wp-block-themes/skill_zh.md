# WP区块主题

## 使用场景

用于区块主题开发工作，例如：

- 编辑 `theme.json`（预设、设置、样式、单个区块样式）
- 添加或修改模板（`templates/*.html`）和模板片段（`parts/*.html`）
- 添加模式（`patterns/*.php`）和控制插入器中显示的内容
- 添加样式变体（`styles/*.json`）
- 调试“样式未应用”/“编辑器未反映theme.json”问题

## 所需输入

- 仓库根目录和目标主题（如果存在多个主题，则为主题目录）。
- 目标WordPress版本范围（theme.json版本和功能随核心版本变化）。
- 问题表现位置：站点编辑器、帖子编辑器、前端或全部。

## 操作步骤

### 0) 初步筛选和定位区块主题根目录

1. 运行初步筛选：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2. 检测主题根目录和关键文件夹：
   - `node skills/wp-block-themes/scripts/detect_block_themes.mjs`

如果存在多个主题，选择其中一个并将所有更改范围限定在该主题根目录下。

### 1) 创建新的区块主题（如需）

如果你从零开始创建区块主题（或从经典主题转换）：

- 优先从已知良好的脚手架（或从WP环境导出）开始，而不是猜测文件布局。
- 明确指定最低支持的WordPress版本，因为 `theme.json` 架构版本不同。

阅读：
- `references/creating-new-block-theme.md`

创建主题根目录后，重新运行 `detect_block_themes` 并继续以下步骤。

### 2) 确认主题类型和调整预期

- 区块主题指示器：
  - 存在 `theme.json`
  - 存在 `templates/` 和/或 `parts/`
- 记住样式层级：
  - 核心默认值 → theme.json → 子主题 → 用户自定义
  - 用户自定义可能会使theme.json编辑“被忽略”

阅读：
- `references/debugging.md`（样式层级 + 最快检查方法）

### 3) 安全地修改 `theme.json`

确定你要修改：

- **设置**（UI允许的选项）：预设、字体大小比例、颜色、布局、间距
- **样式**（默认外观）：元素/区块的CSS样式规则

阅读：
- `references/theme-json.md`

### 4) 模板和模板片段

- 模板位于 `templates/` 下，为HTML格式。
- 模板片段位于 `parts/` 下，且不能嵌套在子目录中。

阅读：
- `references/templates-and-parts.md`

### 5) 模式

当你需要主题拥有的模式时，优先使用 `patterns/` 下的文件系统模式。

阅读：
- `references/patterns.md`

### 6) 样式变体

样式变体是 `styles/` 下的JSON文件。注意：一旦用户选择了一个样式变体，该选择会存储在数据库中，因此更改文件可能不会自动“更新用户看到的内容”。

阅读：
- `references/style-variations.md`

## 验证

- 站点编辑器按预期反映更改（样式UI、模板、模式）。
- 前端使用预期样式渲染。
- 如果样式未更改，确认用户自定义是否覆盖了主题默认值。
- 如果涉及资源（字体、自定义JS/CSS构建），运行仓库的构建/校验脚本。

## 失败模式 / 调试

从以下内容开始：

- `references/debugging.md`

常见问题：

- 错误的主题根目录（编辑了一个非活动的主题）
- 用户自定义覆盖了你的默认值
- 无效的 `theme.json` 结构/拼写错误阻止应用
- 模板/片段位于错误文件夹（或嵌套的片段）

## 升级处理

如果上游行为不明确，请查阅权威文档：

- 主题手册和区块编辑器手册，用于 `theme.json`、模板、模式和样式变体。
