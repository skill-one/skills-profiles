# OpenPencil

OpenPencil 提供用于 `.fig` 设计文件的 CLI 和 MCP 服务器，以及正在运行的 OpenPencil 编辑器。

使用两种模式：

- **应用模式** — 通过省略文件参数连接到正在运行的 OpenPencil 编辑器。
- **无头模式** — 通过传递文件路径直接处理 `.fig` 文件。

```bash
# 应用模式 — 对编辑器中打开的文档进行操作
openpencil tree

# 无头模式 — 对 .fig 文件进行操作
openpencil tree design.fig
```

当前参考版本：OpenPencil `0.12.x`。MCP 服务器在 `0.12.0` 中暴露了 106 个工具。

## 要求

```bash
# CLI
bun add -g @open-pencil/cli

# 由桌面应用和外部 MCP 客户端使用的 MCP 服务器
bun add -g @open-pencil/mcp
```

桌面应用在 `@open-pencil/mcp` 全局安装的生产 Tauri 构建中会自动启动 `openpencil-mcp-http`，并暴露自动化功能：

- HTTP/RPC: `http://127.0.0.1:7600`
- WebSocket 桥接: `ws://127.0.0.1:7601`
- MCP Streamable HTTP: `http://127.0.0.1:7600/mcp`

## CLI 命令

```bash
openpencil --help
```

`0.12.x` 中的命令：

- `info` — 文档概览：页面、节点数量、字体
- `tree` — 打印带有类型和大小的层次结构
- `pages` — 列出页面
- `node` — 通过 ID 查看详细节点属性
- `selection` — 从正在运行的应用中获取当前选择
- `find` — 按名称/类型查找节点
- `query` — 用于节点搜索的 XPath 选择器
- `variables` — 列出变量和集合
- `export` — 导出 PNG/JPG/WEBP/SVG/PDF/JSX/.fig
- `convert` — 在支持的文档格式之间转换
- `analyze` — 颜色、排版、间距、重复簇
- `lint` — 一致性、结构性和可访问性检查
- `formats` — 支持的文档/导出格式
- `eval` — 使用 Figma 插件 API 执行 JavaScript

### 检查

```bash
openpencil info design.fig
openpencil tree design.fig
openpencil tree --page "Components" --depth 3  # 应用模式
openpencil pages design.fig
openpencil node design.fig --id 1:23
openpencil node --id 1:23  # 应用模式
openpencil selection --json
openpencil variables design.fig
openpencil variables --collection "Colors" --type COLOR
```

### 搜索和 XPath 查询

```bash
openpencil find design.fig --name "Button"
openpencil find --type FRAME                          # 应用模式
openpencil find design.fig --type TEXT --page "Home"
openpencil find design.fig --name "Card" --type COMPONENT --limit 50

openpencil query design.fig "//FRAME"
openpencil query design.fig "//FRAME[@width < 300]"
openpencil query design.fig "//TEXT[contains(@name, 'Button')]"
openpencil query design.fig "//COMPONENT[@stackMode]"
openpencil query design.fig "//COMPONENT//FRAME//TEXT"
openpencil query "//FRAME[@width > 1000]"             # 应用模式
```

常见节点类型：`FRAME`、`TEXT`、`RECTANGLE`、`ELLIPSE`、`VECTOR`、`GROUP`、`COMPONENT`、`COMPONENT_SET`、`INSTANCE`、`SECTION`、`LINE`、`STAR`、`POLYGON`、`SLICE`、`BOOLEAN_OPERATION`。

### 导出和转换

```bash
openpencil export design.fig -o hero.png
openpencil export -o hero.png                         # 应用模式
openpencil export design.fig --node 1:23 -s 2 -o button@2x.png
openpencil export design.fig -f jpg -q 85 -o preview.jpg
openpencil export design.fig -f svg --node 1:23 -o icon.svg
openpencil export design.fig -f pdf -o page.pdf
openpencil export design.fig -f fig -o roundtrip.fig
openpencil export design.fig -f jsx -o component.jsx
openpencil export design.fig -f jsx --style tailwind -o component.tsx
openpencil export design.fig --thumbnail --width 1920 --height 1080
openpencil export --page "Components" -o components.png

openpencil convert design.fig -o design.pen
openpencil formats
```

### 分析和 lint

```bash
openpencil analyze colors design.fig
openpencil analyze colors --similar --threshold 10     # 应用模式
openpencil analyze typography design.fig --group-by size
openpencil analyze spacing design.fig --grid 8
openpencil analyze clusters design.fig --min-count 3
openpencil lint design.fig
openpencil lint design.fig --json
```

### Eval (Figma 插件 API)

使用与 Figma 插件 API 兼容的运行时对文档执行 JavaScript：

```bash
openpencil eval design.fig -c 'figma.currentPage.findAll(n => n.type === "TEXT").length'

# 应用模式 — 修改编辑器中的实时文档
openpencil eval -c '
  const buttons = figma.currentPage.findAll(n => n.name === "Button");
  buttons.forEach(b => { b.cornerRadius = 8 });
  buttons.length + " buttons updated"
'

# 修改并保存到同一文件
openpencil eval design.fig -w -c '
  const texts = figma.currentPage.findAll(n => n.type === "TEXT");
  texts.forEach(t => { t.fontSize = 16 });
'

# 保存到不同文件
openpencil eval design.fig -o modified.fig -c '...'

# 从标准输入读取代码
echo 'figma.currentPage.children.map(n => n.name)' | openpencil eval design.fig --stdin
```

报告结构化数据的每个命令在适当的情况下都支持 `--json`。

## MCP 服务器

### Stdio MCP 客户端

默认使用 Bun：

```json
{
  "mcpServers": {
    "open-pencil": {
      "command": "bunx",
      "args": ["openpencil-mcp"]
    }
  }
}
```

如果全局安装了 `@open-pencil/mcp`，直接二进制文件也有效：

```json
{
  "mcpServers": {
    "open-pencil": {
      "command": "openpencil-mcp"
    }
  }
}
```

### HTTP / Streamable HTTP

```bash
export PORT=7600
export OPENPENCIL_MCP_AUTH_TOKEN=secret       # 可选的 /mcp 认证
export OPENPENCIL_MCP_CORS_ORIGIN="*"         # 可选的 CORS
export OPENPENCIL_MCP_ROOT=/path/to/files     # 启用/作用域 open_file/save_file 路径

openpencil-mcp-http
# 或: bunx openpencil-mcp-http
```

### MCP 工作流

1. **打开/创建文档** — 当配置了 `OPENPENCIL_MCP_ROOT` 时，使用 `open_file { path }`，否则使用 `new_document {}`。
2. **查询** — `get_page_tree`、`find_nodes`、`query_nodes`、`get_node`、`list_pages`、`get_current_page`。
3. **检查** — `get_jsx`、`diff_jsx`、`describe`、`export_image`、`export_svg`、`export_pdf`。
4. **修改** — `render`、`batch_update`、`update_node`、`set_fill`、`set_layout`、`create_shape`、`import_svg` 等。
5. **导航** — 创建或编辑可见画布内容后，调用 `select_nodes` 和 `viewport_zoom_to_fit { id }`（或 `node_bounds` + `viewport_set`），以便用户可以在正在运行的编辑器中看到结果。
6. **保存/导出** — `save_file`、`export_image`、`export_svg`、`export_pdf`，或 CLI `export`。

## 0.12.0 中的 MCP 工具（共 106 个）

**读取和选择（17）：** `get_selection`、`get_node`、`find_nodes`、`get_page_tree`、`get_current_page`、`list_pages`、`select_nodes`、`query_nodes`、`get_components`、`switch_page`、`page_bounds`、`list_fonts`、`list_available_fonts`、`get_jsx`、`diff_jsx`、`describe`、`node_tree`

**创建和导入（12）：** `render`、`create_shape`、`create_component`、`create_instance`、`create_page`、`create_vector`、`create_slice`、`import_svg`、`search_icons`、`insert_icon`、`fetch_icons`、`stock_photo`

**修改（24）：** `update_node`、`batch_update`、`set_layout`、`set_layout_child`、`set_radius`、`set_fill`、`set_stroke`、`set_text`、`set_text_properties`、`set_effects`、`set_opacity`、`set_font`、`set_visible`、`set_constraints`、`set_rotation`、`set_minmax`、`set_font_range`、`set_text_resize`、`set_blend`、`set_locked`、`set_stroke_align`、`set_image_fill`、`set_variable`、`bind_variable`

**结构（16）：** `delete_node`、`reparent_node`、`node_resize`、`clone_node`、`node_move`、`rename_node`、`group_nodes`、`ungroup_node`、`flatten_nodes`、`node_to_component`、`node_bounds`、`node_ancestors`、`node_children`、`node_bindings`、`node_replace_with`、`arrange`

**变量（9）：** `list_variables`、`list_collections`、`get_variable`、`find_variables`、`create_variable`、`delete_variable`、`get_collection`、`create_collection`、`delete_collection`

**矢量和视口（15）：** `boolean_union`、`boolean_subtract`、`boolean_intersect`、`boolean_exclude`、`path_get`、`path_set`、`path_scale`、`path_flip`、`path_move`、`viewport_get`、`viewport_set`、`viewport_zoom_to_fit`、`export_svg`、`export_pdf`、`export_image`

**分析和生成（9）：** `analyze_colors`、`analyze_typography`、`analyze_spacing`、`analyze_clusters`、`diff_create`、`diff_show`、`design_to_tokens`、`design_to_component_map`、`calc`

**文件和提示（4）：** `save_file`、`open_file`、`new_document`、`get_codegen_prompt`

> 工具可用性可能取决于服务器模式。`open_file`、`save_file` 和磁盘写入导出路径需要 `OPENPENCIL_MCP_ROOT` 进行路径作用域。

## 适用于代理的关键工具

- **`query_nodes`** — 使用 XPath 选择器查找特定节点，无需获取完整树。
- **`get_jsx`** — 将任何节点检查为 JSX，格式与 `render` 接受的格式相同。
- **`diff_jsx`** — 在编辑前结构化比较两个节点。
- **`describe`** — 对角色、视觉样式、布局和设计问题进行语义分析。
- **`batch_update`** — 高效应用多个节点更新。
- **`export_image` / `export_svg` / `export_pdf`** — 视觉验证和交付物。
- **`viewport_zoom_to_fit` / `viewport_set` / `viewport_get`** — 使正在运行的编辑器聚焦于创建或编辑的设计。
- **`get_codegen_prompt`** — 获取 OpenPencil 当前的 JSX/代码生成指导。

## JSX 渲染

使用 `render` 工具或 `eval` 创建组件树。如果不确定 JSX 语法，请先调用 `get_codegen_prompt`。

```jsx
<Frame name="Card" w={320} h="hug" flex="col" gap={16} p={24} bg="#FFF" rounded={16}>
  <Text size={18} weight="bold" color="#111">Title</Text>
  <Text size={14} color="#666">Description text</Text>
  <Frame flex="row" gap={8}>
    <Frame w={80} h={36} bg="#3B82F6" rounded={8} justify="center" items="center">
      <Text size={14} color="#FFF" weight="600">Action</Text>
    </Frame>
  </Frame>
</Frame>
```

元素：`Frame`、`Text`、`Rectangle`、`Ellipse`、`Line`、`Star`、`Polygon`、`Group`、`Section`、`Component`、`Instance`。

文本内容是 `<Text>` 的子内容。使用设计-JSX 属性，而不是 Figma API 字段名：

```jsx
<Text size={48} weight="bold" font="Inter" color="#111">Design faster with AI</Text>
```

常见属性：

| 属性 | 含义 |
|------|-------|
| `w`, `h` | 宽度、高度（数字或 `"hug"` / `"fill"`) |
| `flex` | `"row"` 或 `"col"` |
| `grid`, `columns`, `rows` | CSS Grid，例如 `columns="1fr 200px 1fr"` |
| `gap`, `rowGap`, `columnGap` | 项间距 |
| `p`, `px`, `py`, `pt`, `pr`, `pb`, `pl` | 内边距 |
| `justify` | `"start"`、`"center"`、`"end"`、`"between"` |
| `items` | `"start"`、`"center"`、`"end"`、`"stretch"` |
| `grow` | Flex grow 因子 |
| `bg` | 填充颜色（十六进制） |
| `rounded`, `roundedTL/TR/BL/BR` | 角半径 |
| `stroke`, `strokeWidth` | 线条颜色和粗细 |
| `opacity` | 0–1 |
| `rotate` | 度数 |
| `overflow` | `"hidden"` 以裁剪子元素 |
| `shadow` | `"offsetX offsetY blur #color"` |
| `blur` | 层级模糊 |
| `size`, `weight`, `font`, `color`, `textAlign` | 文本属性 |
| `colStart`, `rowStart`, `colSpan`, `rowSpan` | Grid 子元素定位 |

## 小贴士

- 省略文件路径以处理正在运行的 OpenPencil 编辑器中打开的文档。
- 使用 `info` 或 `get_page_tree` 了解文档。
- 使用 `tree --depth 2` 或 `query_nodes` 避免在大型文件上输出过多信息。
- 使用 `--node` 导出特定节点以进行更快的视觉检查。
- 修改后使用 `export_image` 验证视觉质量。
- 创建可见设计后，选择它并缩放编辑器到它：`select_nodes { ids: [id] }` 然后调用 `viewport_zoom_to_fit { id}`。
- 如果客户端无法使用缩放至适合，使用 `node_bounds` 计算中心并调用 `viewport_set { x, y, zoom}`。
- 使用 `analyze colors --similar` 查找近似重复的颜色。
- 使用 `eval` 执行未由专用 CLI/MCP 工具覆盖的 Figma 插件 API 操作。
- 将 CLI 输出管道到脚本时使用 `--json`。
- 在应用模式下，`eval` 和 MCP 修改会实时反映在编辑器中。
