# create_new_file — 创建新的 Figma 文件

使用 `create_new_file` MCP 工具在用户的草稿文件夹中创建一个新的空白 Figma 文件。这通常在 `use_figma` 之前使用，当你需要一个新文件来工作时。

## 技能参数

此技能接受可选参数：`/figma-create-new-file [editorType] [fileName]`

- **editorType**: `design`（默认）或 `figjam`
- **fileName**: 新文件的名称（默认为 "Untitled"）

示例：
- `/figma-create-new-file` — 创建一个名为 "Untitled" 的设计文件
- `/figma-create-new-file figjam My Whiteboard` — 创建一个名为 "My Whiteboard" 的 FigJam 文件
- `/figma-create-new-file design My New Design` — 创建一个名为 "My New Design" 的设计文件

从技能调用中解析参数。如果未提供 `editorType`，则默认为 `"design"`。如果未提供 `fileName`，则默认为 `"Untitled"`。

## 工作流程

### 第 1 步：解析 planKey

`create_new_file` 工具需要一个 `planKey` 参数。请按照以下决策树操作：

1. **用户已经提供了一个 planKey**（例如，来自之前的 `whoami` 调用或在他们的提示中）→ 直接使用它，跳到第 2 步。

2. **没有可用的 planKey** → 调用 `whoami` 工具。响应中包含一个 `plans` 数组。每个计划都有一个 `key`、`name`、`seat` 和 `tier`。

   - **单个计划**：自动使用其 `key` 字段。
   - **多个计划**：询问用户他们想在哪个团队或组织中创建文件，然后使用相应计划的 `key`。

### 第 2 步：调用 create_new_file

使用以下参数调用 `create_new_file` 工具：

| 参数    | 必填 | 描述 |
|-------------|----------|-------------|
| `planKey`   | 是      | 第 1 步的 plan key |
| `fileName`  | 是      | 新文件的名称 |
| `editorType`| 是      | `"design"` 或 `"figjam"` |

示例：
```json
{
  "planKey": "team:123456",
  "fileName": "My New Design",
  "editorType": "design"
}
```

### 第 3 步：使用结果

该工具返回：
- `file_key` — 新创建的文件的 key
- `file_url` — 在 Figma 中打开文件的直接 URL

使用 `file_key` 进行后续工具调用，如 `use_figma`。

## 重要提示

- 文件创建在用户选择的计划的 **草稿文件夹** 中。
- 仅支持 `"design"` 和 `"figjam"` 编辑器类型。
- 如果你的下一步是 `use_figma`，请在调用它之前加载 `figma-use` 技能。
