# use_figma — Figma插件API技能用于FigJam

此技能包含针对`use_figma` MCP工具的FigJam特定上下文。`[figma-use](../figma-use/SKILL.md)`技能为通过MCP执行插件API提供了基础上下文，以及用于更高级用例（此处未描述）的完整Figma插件API。

**在调用`use_figma`进行FigJam操作时，始终在逗号分隔的`skillNames`参数中包含`figma-use-figjam`。如果此技能是通过MCP资源加载的，则你必须将名称前缀为`resource:`（例如`resource:figma-use-figjam`）。** 这是一个用于跟踪技能使用的日志参数——它不会影响执行。

> **FigJam URL为`figma.com/board/...`。** 在FigJam中不要调用`figma.createPage()`——它会在`figma`全局对象上抛出`TypeError: figma.createPage no such property 'createPage'`错误。`createPage()`仅是设计文件API（`figma.com/design/...`）。FigJam文件具有单个隐式页面；使用部分（see [create-section](references/create-section.md)）来组织内容。

## 检查FigJam文件

**`get_figjam`是用于检查FigJam文件的工具。** 它返回完整的节点树作为XML，包括页面、部分、便利贴、连接器和其他节点ID，这些ID需要在后续的`use_figma`调用中引用。

- **在使用任何需要引用现有节点（页面ID、部分ID等）的`use_figma`代码之前，使用`get_figjam`。** 不要尝试通过运行检查脚本来发现ID——`use_figma`的`console.log`输出**不会返回给代理**（see [figma-use关键规则#4](../figma-use/SKILL.md)）。只有`return`值会返回。
- **`get_metadata`在FigJam文件上无效**——它仅适用于设计模式，并且会立即以"不适用于FigJam文件"失败。
- **`get_screenshot`需要一个有效的`nodeId`**——传递空节点ID会返回"invalid nodeId"错误。首先从`get_figjam`获取ID。
- 如果你忘记从之前的`use_figma`调用中返回ID，现在需要它，请调用`get_figjam`，而不是重新运行检查脚本。

## 高效加载参考文档

仅加载你的任务所需的参考文档——但当你确实需要加载多个时，**在单个并行工具调用批次中发出所有读取操作**，而不是按回合顺序进行。对于典型的板创建任务，这意味着包含`plan-board-content`以及你将使用的3-4个特定节点类型参考的单条消息。

## 延迟工具——批量加载模式

Figma MCP工具（`use_figma`、`get_figjam`、`get_screenshot`、`get_metadata`、`create_new_file`、`whoami`）通常作为需要`ToolSearch`加载其模式才能调用的延迟工具。**使用`select:`语法在单个`ToolSearch`调用中加载所有模式**，而不是每个工具一个调用：

```
ToolSearch query="select:use_figma,get_figjam,get_screenshot,get_metadata,create_new_file"
```

六个顺序`ToolSearch`调用是在任何工作发生之前进行的六次往返。一个批量调用是一次往返。

## 文本变更——规范配方

每个FigJam文本变更（便利贴/形状/标签/表格单元/连接器文本、独立文本节点）都遵循与设计文件相同的配方：加载字体 → `await` → 变更 → 返回受影响的ID。跳过加载会抛出`Cannot write to node with unloaded font "<family> <style>"`错误。参见[figma-use → gotchas.md → 规范文本编辑配方](../figma-use/references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids)。FigJam特定说明：子层默认值不同（便利贴 → `Inter Medium`，形状 → `Inter Medium`，连接器 → 设置前无效），因此始终从`node.text.fontName`加载，而不是硬编码`{ family: 'Inter', style: 'Regular' }`。

## 向FigJam板添加图像

**`upload_assets`是添加图像到FigJam文件的唯一支持方式。** 使用FigJam的`fileKey`调用`upload_assets`；该工具返回单次使用的上传URL，你将原始图像字节POST到这些URL，图像会自动提交并放置。传递`nodeIds`（每个上传一个条目）以将上传附加到现有的FigJam节点作为填充；省略`nodeIds`以将图像作为新层放置到板上。

有关完整的请求/响应形状，请参阅[figma-use → api-reference.md → 图像](../figma-use/references/api-reference.md#images)。

## 参考文档

- [plan-board-content](references/plan-board-content.md) - 对于任何板内容请求，请阅读此文档——板模板、回顾、头脑风暴、冰breaker、会议板、脚手架
  - 涵盖生成板内容的规划，包括顺序大纲、部分、意图和层次文本
  - 委托其他参考文档提供特定API细节
- [create-section](references/create-section.md) — 创建和配置FigJam部分（尺寸、命名、颜色、内容可见性、组织节点、列布局）
- [create-sticky](references/create-sticky.md) — 创建和配置FigJam便利贴（颜色、尺寸、文本、作者可见性、批量创建）
- [create-connector](references/create-connector.md) — 创建和配置FigJam连接器（端点、箭头、线类型、标签、颜色、图表布线）
- [create-text](references/create-text.md) — 创建和配置FigJam文本节点（字体加载、预设字体和颜色、尺寸、列表、思维导图操作）
- [position-figjam-nodes](references/position-figjam-nodes.md) — 在画布上定位、调整大小和重新父节点（包括在部分内）
- [create-shape-with-text](references/create-shape-with-text.md) — 创建和配置带有嵌入文本的FigJam形状（形状类型、颜色预设、调整大小以适应文本、图表布局）
- [create-code-block](references/create-code-block.md) — 创建和配置FigJam代码块节点（语言、语法高亮、定位、嵌入部分）
- [create-table](references/create-table.md) — 创建和配置FigJam表格（行、列、单元格文本、颜色预设、调整大小）
- [edit-text](references/edit-text.md) — 编辑现有文本节点（字体加载、样式范围、查找/替换、FigJam Charcoal默认颜色）
- [create-label](references/create-label.md) — 创建和配置FigJam标签节点（小号编号/字母圆圈标注标记、序列、定位）
- [batch-modify](references/batch-modify.md) — 修改多个现有节点的模式（批量样式更改、重新定位、属性更新）
- [figjam-colors](references/figjam-colors.md) — 每种节点类型的规范FigJam调色板（便利贴、部分、连接器、形状、标签）以及`hex/255`表示法规则和`h()`辅助函数
