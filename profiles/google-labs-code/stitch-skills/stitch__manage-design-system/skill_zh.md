# 设计系统

为您的项目设计语言创建一个"事实来源"，以确保未来所有屏幕的一致性。

> [!NOTE]
> 参考您的系统提示，了解如何处理本技能中提到的所有工具的 MCP 工具前缀（例如，`get_screen`、`create_design_system_from_design_md`、`apply_design_system`）。

## 📥 获取

要分析一个 Stitch 项目，您必须使用 Stitch MCP 工具获取元数据和资源：

1. **项目查找**：使用 `list_projects` 找到目标 `projectId`。
2. **屏幕查找**：使用 `list_screens` 为该 `projectId` 找到代表性屏幕（例如，“主页”、“主仪表板”）。
3. **元数据获取**：为目标屏幕调用 `get_screen` 以获取 `screenshot.downloadUrl` 和 `htmlCode.downloadUrl`。
4. **资源下载**：使用 `read_url_content` 获取 HTML 代码。

## 🧠 从描述中合成

如果您需要从现有屏幕中提取设计系统，请使用 `design-md` 技能（在 `stitch-utilities` 插件中）。

如果不存在现有屏幕（新项目），或者用户提供直接描述（例如，“暗主题、蓝色和紫色、圆角、Inter 字体”）：

1. 使用设计映射将用户的模糊术语映射到精确值（参见 `stitch-utilities` 插件中的 `design-md` 技能或 `generate-design` 技能）。
2. 选择具体的十六进制代码、字体家族和圆角值。
3. 生成 `DESIGN.md` 文件（参考 `stitch-utilities` 插件中的 `design-md` 技能的结构）。
4. 继续执行下方的“在 Stitch 中创建或更新设计系统”步骤。

## 📝 输出结构

`DESIGN.md` 文件应遵循 `stitch-utilities` 插件中定义的 `design-md` 技能的结构。

## 🚀 在 Stitch 中创建或更新设计系统

生成 `.stitch/DESIGN.md` 后，请确保在 Stitch 中创建或更新设计系统。

**两步设计系统创建：**

> [!WARNING]
> **检查点 — 用户确认需要。**
> 在上传之前，您**必须**暂停并要求用户确认。展示您即将创建的设计系统摘要（显示名称、关键颜色、字体和圆角），并在获得明确批准之前不要继续。在用户确认之前**不要**上传。

1. **上传 `DESIGN.md`**：
   - **选项 A（推荐 — 上传器脚本）**：使用修改后的 `upload-to-stitch` Python 脚本，该脚本原生处理 `.md` 文件。它在进程内对 markdown 文件进行 base64 编码，并将其发送到 `/v1/projects/{projectId}/screens:batchCreate` 端点，绕过输出令牌限制。
     ```bash
     python3 stitch-skills/plugins/stitch-design/skills/upload-to-stitch/scripts/upload_to_stitch.py \
       --project-id <PROJECT_ID> \
       --file-path /path/to/DESIGN.md \
       --api-key <API_KEY> \
       --generated-by <GENERATED_BY>
     ```
     将 `<GENERATED_BY>` 设置为标识生成 `DESIGN.md` 的技能或工具。从另一个技能调用时使用调用技能名称（例如 `stitch::code-to-design`），或在独立使用时使用代理/工具名称（例如 `Gemini`、`Claude Code`）。如果省略，脚本将默认为 `UserUploadedDesignMd`。

     这将返回 `sourceScreen` ID 和 `screenInstance` ID。
   - **选项 B（直接 MCP 工具）**：如果 `DESIGN.md` 较小（小于 ~5KB），您可以直接调用 `upload_design_md` MCP 工具，将 base64 编码的设计 markdown 内容作为 `designMdBase64` 传递。

2. **创建设计系统**：在上传后立即调用 `create_design_system_from_design_md` 工具，传递 `projectId` 和 `selectedScreenInstance`（包含从上传步骤返回的 `id` 和 `sourceScreen`）。

一旦上传脚本和 `create_design_system_from_design_md` 都已完成，Stitch 将在项目级别持有设计令牌 — 您不需要在生成提示中重复它们。

## 🎨 将设计系统应用于屏幕

使用 `apply_design_system` 将设计系统应用于现有屏幕。

> [!IMPORTANT]
> `selectedScreenInstances` 必须仅包含 **仅** `id` 和 `sourceScreen` — **不要**包含位置/尺寸字段（`x`、`y`、`width`、`height`）或请求将因“无效参数”而失败。从 `get_project` 获取屏幕实例 ID。

```json
{
  "projectId": "...",
  "assetId": "...",
  "selectedScreenInstances": [
    {
      "id": "...",
      "sourceScreen": "projects/.../screens/..."
    }
  ]
}
```

**如何获取所需的 ID：**
1. 调用 `get_project` 以检索 `screenInstances` — 每个实例都有一个 `id` 和 `sourceScreen`。
2. 调用 `list_design_systems` 以检索设计系统 `name`（格式：`assets/{assetId}`） — 使用 `assets/` 之后的部分作为 `assetId`。
3. 过滤掉任何类型为 `type: "DESIGN_SYSTEM_INSTANCE"` 的实例 — 仅传递实际屏幕。

## 📋 更新项目元数据

写入 `.stitch/DESIGN.md` 后，还创建或更新 `.stitch/metadata.json` 以跟踪 `projectId`、`title`、所有已知屏幕和设计系统摘要。参见 [examples/metadata.json](examples/metadata.json) 了解格式。

## Schema 参考

参见 [reference/tool-schema.md](reference/tool-schema.md) 了解完整的 `designSystem` 对象 schema 及所有可用选项。

## 💡 最佳实践

参考 `design-md` 技能（在 `stitch-utilities` 插件中）了解描述设计元素的最佳实践。
