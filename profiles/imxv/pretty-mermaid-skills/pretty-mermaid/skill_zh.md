# 精美的 Mermaid

使用捆绑的 Node.js CLI 创建或渲染 Mermaid 图表。使用 SVG 进行可缩放文档，PNG 用于共享或仅栅格的消费者，以及 ASCII 或 Unicode 用于终端和纯文本。

## 工作目录

将包含此文件的目录视为 `<skill-root>`。从该目录运行捆绑脚本，或使用绝对路径调用它们。将用户源和渲染输出保存在用户请求的位置；不要将渲染器复制到他们的项目中。

## 工作流程

1. 确定用户是否提供了 Mermaid 源代码或需要从文本中创建图表。
2. 从下表中选择图表类型和输出格式。
3. 当语法、主题选择或 API 行为需要更多详细信息时，仅读取相关的参考文件。
4. 将新源保存为 `.mmd` 文件，保留用户术语和关系。
5. 使用命名的主题或显式颜色进行渲染。
6. 检查结果。修复语法、裁剪、拥挤的布局或模糊的标签并重新渲染。
7. 返回源和输出路径，以及选择的格式和主题。

除非用户要求替换，否则不要覆盖现有的源或输出文件。

## 选择图表类型

| 需求 | 图表类型 | 起始 |
| --- | --- | --- |
| 流程、决策树、架构 | 流程图 | `flowchart LR` |
| API 调用、消息、交互 | 序列图 | `sequenceDiagram` |
| 生命周期或有限状态机 | 状态图 | `stateDiagram-v2` |
| 类、模块、关系 | 类图 | `classDiagram` |
| 数据库实体和基数 | ER 图 | `erDiagram` |
| 条形图、线图、趋势、比较 | XY 图表 | `xychart-beta` |

在编写非平凡的 Mermaid 语法时，请阅读 `references/DIAGRAM_TYPES.md`。

## 选择输出

| 输出 | 最佳用途 | 备注 |
| --- | --- | --- |
| SVG | README、文档、幻灯片、网站 | 可缩放、可主题化、支持透明度 |
| PNG | 聊天、预览、仅栅格的工具 | 设置 `--format png`；无需外部转换器 |
| Unicode | 现代终端和可读的文本预览 | 默认 ASCII 渲染器输出 |
| 纯 ASCII | 日志和受限终端 | 添加 `--use-ascii` |
| ANSI 颜色文本 | 交互式终端 | 设置 `--color-mode` |

## 核心命令

从 `<skill-root>` 运行这些命令。

### 列出主题

```bash
node scripts/themes.mjs
```

### 渲染 SVG

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.svg \
  --theme tokyo-night
```

### 渲染终端文本

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.txt \
  --format ascii \
  --color-mode none
```

当 Unicode 箭头绘制字符不可接受时，添加 `--use-ascii`。

### 渲染 PNG

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.png \
  --format png \
  --width 1200 \
  --theme tokyo-night
```

### 批量渲染目录

```bash
node scripts/batch.mjs \
  --input-dir ./diagrams \
  --output-dir ./rendered \
  --format svg \
  --theme github-dark \
  --workers 4
```

对于三个或更多图表，或当必须将一致选项应用于目录时，请使用批量渲染。

## 主题选择

- 通用暗色文档：`tokyo-night`
- GitHub 暗色或浅色表面：`github-dark`，`github-light`
- 打印和演示文稿：`zinc-light`
- 高对比度颜色：`dracula`
- 凉爽、克制的调色板：`nord`，`nord-light`

当视觉主题选择很重要时，请阅读 `references/THEMES.md` 或打开 `docs/THEME_GALLERY.md`。命名的主题可以使用显式颜色标志进行细化。

## 有用的选项

### 共享样式

| 选项 | 目的 |
| --- | --- |
| `--theme <name>` | 应用 15 个内置主题之一 |
| `--bg`，`--fg` | 设置所需的背景色和前景色 |
| `--line`，`--accent`，`--muted` | 细化连接器、高亮和次要文本 |
| `--surface`，`--border` | 细化节点填充和描边 |
| `--font <name>` | 设置 SVG 字体族 |

### SVG

| 选项 | 目的 |
| --- | --- |
| `--transparent` | 移除 SVG 背景 |
| `--padding <n>` | 设置画布填充 |
| `--node-spacing <n>` | 设置水平节点间距 |
| `--layer-spacing <n>` | 设置垂直层间距 |
| `--component-spacing <n>` | 分离不连接的组件 |
| `--interactive` | 启用 XY 图表悬停工具提示 |

### PNG

| 选项 | 目的 |
| --- | --- |
| `--width <n>` | 设置输出宽度，从 100 到 10000 像素，同时保持纵横比 |
| `--transparent` | 保留透明背景 |

### 终端输出

| 选项 | 目的 |
| --- | --- |
| `--use-ascii` | 用纯 ASCII 替换 Unicode 箭头绘制 |
| `--padding-x`，`--padding-y` | 调整图表间距 |
| `--box-border-padding` | 调整节点框内的填充 |
| `--color-mode <mode>` | `none`，`auto`，`ansi16`，`ansi256`，`truecolor` 或 `html` |

运行 `node scripts/render.mjs --help` 或 `node scripts/batch.mjs --help` 获取权威的 CLI 列表。

## 编写指南

- 优先使用简短、具体的标签；保留用户的专业术语。
- 当分支或消息不明确时，使用显式的边标签。
- 通过拆分不相关的关注点而不是缩小文本来保持大型图表的可读性。
- 对于宽流程使用 `LR`，对于窄文档使用 `TB`。
- 避免仅通过颜色传达含义。
- 使用浅色主题进行打印，并确认与最终背景的对比度。
- 对于不熟悉的语法，从 `assets/example_diagrams/` 开始并咨询图表参考。

## 验证

渲染后：

1. 确认命令成功退出且输出文件非空。
2. 确认 SVG 输出以 `<svg>` 开头；确认 PNG 输出作为有效图像打开；确认文本输出包含可见的图表内容。
3. 当布局很重要时，检查视觉输出，特别是长标签、CJK 文本、不连接的组件和 XY 图表。
4. 确认箭头、基数、状态和标签与源请求匹配。
5. 报告渲染器限制，而不是静默地忽略不支持的语法。

更改此技能、其脚本、模板或参考时，请运行 `npm test` 和 `npm run validate`。

## 故障排除

- 缺少依赖项：在 `<skill-root>` 中运行 `npm install`；CLI 还会尝试首次运行安装。
- 未知主题：运行 `node scripts/themes.mjs` 并使用确切列出的名称。
- 解析错误：咨询 `references/DIAGRAM_TYPES.md`，将问题简化为失败语句，然后逐步恢复图表。
- 拥挤的 SVG：增加 `--node-spacing`，`--layer-spacing` 或 `--component-spacing`。
- PNG 颜色错误：使用具体的十六进制值自定义颜色；无法栅格化未解析的外部 CSS 变量。
- 重定向输出中的终端颜色转义序列：使用 `--color-mode none`。

## 参考路由

| 资源 | 在何时阅读或使用 |
| --- | --- |
| `references/DIAGRAM_TYPES.md` | 编写或调试 Mermaid 语法时 |
| `references/THEMES.md` | 比较主题或定义自定义颜色时 |
| `references/api_reference.md` | 扩展脚本或直接调用 `beautiful-mermaid` 时 |
| `docs/THEME_GALLERY.md` | 视觉选择主题时 |
| `assets/example_diagrams/` | 从支持的图表模板开始时 |
| `scripts/render.mjs` | 渲染一个图表时 |
| `scripts/batch.mjs` | 并行渲染目录时 |
| `scripts/themes.mjs` | 列出安装的主题时 |
