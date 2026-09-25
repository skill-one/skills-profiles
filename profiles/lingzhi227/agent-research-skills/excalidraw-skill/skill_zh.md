# Excalidraw 技能

## 第 0 步：检测连接模式

在执行任何操作之前，确定可用的模式。按顺序运行以下检查：

### 检查 1：MCP 服务器（最佳体验）
```bash
mcp-cli tools | grep excalidraw
```
如果你看到像 `excalidraw/batch_create_elements` 这样的工具 → **使用 MCP 模式**。直接调用 MCP 工具。

### 检查 2：REST API（备用——无需 MCP 服务器）
```bash
curl -s http://localhost:3000/health
```
如果你得到 `{"status":"ok"}` → **使用 REST API 模式**。使用来自备忘单的 HTTP 端点（`curl` / `fetch`）。

### 检查 3：都不行 → 指导用户安装
如果都不行，告诉用户：
> Excalidraw 画布服务器未运行。要设置：
> 1. 克隆：`git clone https://github.com/yctimlin/mcp_excalidraw && cd mcp_excalidraw`
> 2. 构建：`npm ci && npm run build`
> 3. 启动画布：`HOST=0.0.0.0 PORT=3000 npm run canvas`
> 4. 在浏览器中打开 `http://localhost:3000`
> 5. （推荐）安装 MCP 服务器以获得最佳体验：
>    ```
>    claude mcp add excalidraw -s user -e EXPRESS_SERVER_URL=http://localhost:3000 -- node /path/to/mcp_excalidraw/dist/index.js
>    ```

### MCP 与 REST API 快速参考

| 操作 | MCP 工具 | REST API 对应 |
|-----------|----------|-------------------|
| 创建元素 | `batch_create_elements` | `POST /api/elements/batch` with `{"elements": [...]}` |
| 获取所有元素 | `query_elements` | `GET /api/elements` |
| 获取单个元素 | `get_element` | `GET /api/elements/:id` |
| 更新元素 | `update_element` | `PUT /api/elements/:id` |
| 删除元素 | `delete_element` | `DELETE /api/elements/:id` |
| 清空画布 | `clear_canvas` | `DELETE /api/elements/clear` |
| 描述场景 | `describe_scene` | `GET /api/elements` (手动解析) |
| 导出场景 | `export_scene` | `GET /api/elements` (保存到文件) |
| 导入场景 | `import_scene` | `POST /api/elements/sync` with `{"elements": [...]}` |
| 快照 | `snapshot_scene` | `POST /api/snapshots` with `{"name": "..."}` |
| 恢复快照 | `restore_snapshot` | `GET /api/snapshots/:name` then `POST /api/elements/sync` |
| 截图 | `get_canvas_screenshot` | 仅通过 MCP（需要浏览器） |
| 设计指南 | `read_diagram_guide` | 不可用——请参阅备忘单获取指南 |
| 视图 | `set_viewport` | `POST /api/viewport` (需要浏览器) |
| 导出图像 | `export_to_image` | `POST /api/export/image` (需要浏览器) |
| 导出 URL | `export_to_excalidraw_url` | 仅通过 MCP |

### REST API 注意事项（关键——在使用 REST API 之前阅读）

1. **标签**：使用 `"label": {"text": "My Label"}`（而不是 `"text": "My Label"`）。MCP 工具自动转换，REST API 不转换。
2. **箭头绑定**：使用 `"start": {"id": "svc-a"}, "end": {"id": "svc-b"}`（而不是 `"startElementId"`/`"endElementId"`）。MCP 工具接受 `startElementId` 并转换，REST API 需要直接使用 `start`/`end` 对象格式。
3. **fontFamily**：必须是字符串（例如 `"1"`）或完全省略。不要传递数字，如 `1`。
4. **更新标签**：当通过 `PUT /api/elements/:id` 更新形状时，在更新体中包含完整的 `label` 以保留它。从更新体中省略 `label` 不会删除它，但重新发送可确保它正确渲染。
5. **REST 模式下的截图**：`POST /api/export/image` 返回 `{"data": "<base64>"}`。保存到文件并读取以进行视觉验证。需要浏览器打开。

## 质量门禁（强制——在创建任何图表之前阅读）

**在每次迭代（每个元素批次）之后，你必须运行质量检查，然后才能继续。永远不要说“看起来很好”，除非所有检查都通过。**

### 质量检查清单——在添加更多元素之前验证所有内容：
1. **文本截断**：所有文本是否完全可见？标签必须适合其形状内。如果文本被截断或换行不良 → 增加 `width` 和/或 `height`。
2. **重叠**：任何元素是否重叠对方？检查没有矩形、椭圆或文本元素共享相同的空间。背景区域必须完全包含其子元素并带有填充。
3. **箭头交叉**：箭头是否穿过无关的元素或与文本标签重叠？如果是 → **使用带航点的曲线/弯角箭头**绕过障碍物（见“箭头路由”部分）。永远不要接受交叉的箭头。
4. **箭头-文本重叠**：任何箭头标签（“charge”、“event”等）是否与形状重叠？箭头标签位于中点——如果它们重叠，则要么删除标签、缩短标签或调整箭头路径。
5. **间距**：元素之间是否有至少 40px 的间距？拥挤的布局难以阅读。
6. **可读性**：所有标签在正常缩放下是否都能阅读？正文字体大小 >= 16，标题 >= 20。

### 如果发现任何问题：
- **停止添加新元素**
- 首先修复问题（调整大小、重新定位、删除并重新创建）
- 重新验证并拍摄新截图
- 只有在所有检查都通过后才能继续到下一个迭代

### 尺寸规则（防止截断）：
- **形状宽度**：`max(160, labelTextLength * 9)` 像素。对于像“API Gateway (Kong)”这样的多词标签，计算所有字符。
- **形状高度**：单行 60px，两行 80px，三行 100px。
- **背景区域**：在包含的元素周围所有边添加 50px 的填充。
- **元素间距**：层之间垂直 60px，同级元素之间水平 40px。
- **侧面板**：至少距离主图表元素 80px。
- **箭头标签**：保持标签简短（1-2 个词）。长箭头标签与其他元素重叠。

### 布局规划（防止重叠）
在创建元素之前，**先在纸上规划坐标网格**：
- 层级 1（y=50-130）：客户端应用程序
- 层级 2（y=200-280）：网关/边缘
- 层级 3（y=350-440）：服务（横向展开：每个服务 ~180px 间隔）
- 层级 4（y=510-590）：数据存储
- 侧面板：x < 0（左侧）或 x > mainDiagramRight + 80（右侧）

**不要将侧面板（可观察性、外部 API）放置在与主图表相同的 x 范围内——它们会重叠。**

## 快速入门

1. 运行上述第 0 步以检测连接模式。
2. 在浏览器中打开画布 URL（导出图像/截图需要浏览器）。
3. **MCP 模式**：使用 MCP 工具进行所有操作。**REST 模式**：使用备忘单中的 HTTP 端点。
4. 对于完整的工具/端点参考，请阅读 `references/cheatsheet.md`。

## 工作流程：绘制图表

### MCP 模式
1. **首先调用 `read_diagram_guide`** 加载设计最佳实践。
2. **在编写任何 JSON 之前规划你的坐标网格**（见质量门禁→布局规划）。
3. 可选：`clear_canvas` 以开始全新。
4. 使用 `batch_create_elements` 一次性创建形状和箭头。
5. **为形状分配自定义 `id`**（例如 `id": "auth-svc"`）。将 `text` 字段设置为形状标签。
6. **根据文本调整形状大小**——使用 `width: max(160, textLength * 9)`。
7. **绑定箭头**使用 `startElementId` / `endElementId`——箭头自动路由。
8. `set_viewport` 使用 `scrollToContent: true` 自动适应图表。
9. **运行质量检查清单**——`get_canvas_screenshot` 并严格评估。在继续之前修复问题。

### REST API 模式
1. 阅读 `references/cheatsheet.md` 获取设计指南。
2. **在编写任何 JSON 之前规划你的坐标网格**（见质量门禁→布局规划）。
3. 可选：`curl -X DELETE http://localhost:3000/api/elements/clear`
4. 一次性创建元素（使用 `@file.json` 处理大量负载）：
   ```bash
   curl -X POST http://localhost:3000/api/elements/batch \
     -H "Content-Type: application/json" \
     -d '{"elements": [
       {"id": "svc-a", "type": "rectangle", "x": 0, "y": 0, "width": 160, "height": 60, "label": {"text": "Service A"}},
       {"id": "svc-b", "type": "rectangle", "x": 0, "y": 200, "width": 160, "height": 60, "label": {"text": "Service B"}},
       {"type": "arrow", "x": 0, "y": 0, "start": {"id": "svc-a"}, "end": {"id": "svc-b"}}
     ]}'
   ```
5. **使用 `"label": {"text": "..."}` 为形状标签**（而不是 `"text": "..."`）。
6. **使用 `"start": {"id": "..."}` / `"end": {"id": "..."}` 绑定箭头**——服务器自动路由边。
7. **根据文本调整形状大小**——使用 `width: max(160, labelTextLength * 9)`。
8. **运行质量检查清单**——拍摄截图并严格评估。在添加更多元素之前修复问题。

### 箭头绑定（推荐）

将箭头绑定到形状以实现自动路由的边。MCP 和 REST API 之间的格式不同：

**MCP 模式**——使用 `startElementId` / `endElementId`：
```json
{"elements": [
  {"id": "svc-a", "type": "rectangle", "x": 0, "y": 0, "width": 120, "height": 60, "text": "Service A"},
  {"id": "svc-b", "type": "rectangle", "x": 0, "y": 200, "width": 120, "height": 60, "text": "Service B"},
  {"type": "arrow", "x": 0, "y": 0, "startElementId": "svc-a", "endElementId": "svc-b", "text": "calls"}
]}
```

**REST API 模式**——使用 `start: {id}` / `end: {id}` 和 `label: {text}`：
```json
{"elements": [
  {"id": "svc-a", "type": "rectangle", "x": 0, "y": 0, "width": 120, "height": 60, "label": {"text": "Service A"}},
  {"id": "svc-b", "type": "rectangle", "x": 0, "y": 200, "width": 120, "height": 60, "label": {"text": "Service B"}},
  {"type": "arrow", "x": 0, "y": 0, "start": {"id": "svc-a"}, "end": {"id": "svc-b"}, "label": {"text": "calls"}}
]}
```

未绑定的箭头使用手动 `x`、`y`、`points` 坐标。

### 箭头路由——避免重叠（复杂图表的关键）

直线箭头（2 点）在复杂图表中会导致交叉和重叠。**使用曲线或弯角箭头**：

**选项 1：曲线箭头**——添加中间航点 + `roundness`：
```json
{
  "type": "arrow", "x": 100, "y": 100,
  "points": [[0, 0], [50, -40], [200, 0]],
  "roundness": {"type": 2},
  "strokeColor": "#1971c2"
}
```
航点 `[50, -40]` 将箭头向上弯曲以越过元素。`roundness: {type: 2}` 使其成为平滑曲线。

**选项 2：弯角箭头**——直角路由（L 形或 Z 形）：
```json
{
  "type": "arrow", "x": 100, "y": 100,
  "points": [[0, 0], [0, -50], [200, -50], [200, 0]],
  "elbowed": true,
  "strokeColor": "#1971c2"
}
```

**何时使用哪种**：
- **扇出箭头**（一个源→多个目标）：使用带垂直分布的航点的曲线箭头以避免彼此重叠。
- **跨道箭头**（连接到侧面板）：使用绕主图表的弯角箭头——先向上，再横移，再向下。
- **服务间箭头**（水平连接）：使用带轻微垂直偏移的曲线箭头以避免穿过相邻元素。

**经验法则**：如果箭头会穿过无关元素，添加航点绕过它。永远不要接受交叉的箭头——一定要修复它们。

## 工作流程：迭代优化（关键差异）

使此技能独特的反馈循环。**每个迭代必须包含质量检查。**

### MCP 模式（完整反馈循环）
1. 添加元素（`batch_create_elements`，`create_element`）。
2. `set_viewport` 使用 `scrollToContent: true`。
3. `get_canvas_screenshot` — **严格评估**与质量检查清单。
4. **如果发现问题** → 先修复它们（`update_element`，`delete_element`，调整大小，重新定位）。
5. 再次 `get_canvas_screenshot` — 重新验证修复。
6. **只有当所有质量检查通过时才继续到下一个迭代。**

### REST API 模式（部分反馈循环）
1. 通过 `POST /api/elements/batch` 添加元素。
2. `POST /api/viewport` 使用 `{"scrollToContent": true}`。
3. 拍摄截图：`POST /api/export/image` → 保存 PNG → **严格评估**与质量检查清单。
4. **如果发现问题** → 通过 `PUT /api/elements/:id` 或删除并重新创建修复。
5. 重新拍摄截图并重新验证。
6. **只有当所有质量检查通过时才继续到下一个迭代。**

### 如何严格评估截图：
- 检查每个标签——是否有任何文本被截断或溢出其容器？
- 检查每个箭头——是否有任何箭头穿过无关元素？
- 检查所有元素对——是否有任何重叠或接触？
- 检查间距——是否有任何东西被挤在一起？
- **要诚实。** 如果看到任何问题，请说“我看到[问题]，正在修复它”——不要说“看起来很好”。

示例流程（MCP）：
```
batch_create_elements → get_canvas_screenshot → "2 个形状的文本被截断"
→ update_element (增加宽度) → get_canvas_screenshot → "X 和 Y 之间有重叠"
→ update_element (重新定位) → get_canvas_screenshot → "所有检查通过"
→ 继续到下一个迭代
```

## 工作流程：优化现有图表

1. `describe_scene` 了解当前状态。
2. 通过 id、类型或标签文本（不是 x/y 坐标）识别目标。
3. `update_element` 移动/调整大小/重新着色，`delete_element` 删除。
4. `get_canvas_screenshot` 视觉验证更改。
5. 如果更新失败：检查元素 id 存在（`get_element`），元素未被锁定（`unlock_elements`）。

## 工作流程：文件 I/O（图表即代码）

- 导出为 .excalidraw 格式：`export_scene` 使用可选 `filePath`。
- 从 .excalidraw 导入：`import_scene` 使用 `mode: "replace"` 或 `"merge"`。
- 导出为图像：`export_to_image` 使用 `format: "png"` 或 `"svg"`（需要浏览器打开）。
- CLI 导出：`node scripts/export-elements.cjs --out diagram.elements.json`
- CLI 导入：`node scripts/import-elements.cjs --in diagram.elements.json --mode batch|sync`

## 工作流程：快照（保存/恢复画布状态）

1. 在进行风险更改之前使用 `snapshot_scene` 并命名。
2. 进行更改，`describe_scene` / `get_canvas_screenshot` 评估。
3. `restore_snapshot` 如有必要回滚。

## 工作流程：复制

- `duplicate_elements` 使用 `elementIds` 和可选 `offsetX`/`offsetY`（默认 20,20）。
- 对于创建重复模式或复制现有布局很有用。

## 箭头/线的点格式

`points` 字段接受以下格式：
- 元组：`[[0, 0], [100, 50]]`
- 对象：`[{"x": 0, "y": 0}, {"x": 100, "y": 50}]`

两者都会自动规范化为元组。

## 工作流程：共享图表（excalidraw.com URL）

1. 使用上述任何工作流程创建图表。
2. `export_to_excalidraw_url` — 上传加密场景，返回可共享的 URL。
3. 分享 URL — 任何人都可以在 excalidraw.com 中打开它以查看和编辑。

## 工作流程：视图控制

- `set_viewport` 使用 `scrollToContent: true` — 自动适应所有元素（缩放以适应）。
- `set_viewport` 使用 `scrollToElementId: "my-element"` — 将视图居中于特定元素。
- `set_viewport` 使用 `zoom: 1.5, offsetX: 100, offsetY: 200` — 手动相机控制。

## 参考

- `references/cheatsheet.md`：完整的 MCP 工具列表（26 个工具）+ REST API 端点 + 有效载荷形状。

## 相关技能
- 另见：[figure-generation](../figure-generation/)，[algorithm-design](../algorithm-design/)，[slide-generation](../slide-generation/)
