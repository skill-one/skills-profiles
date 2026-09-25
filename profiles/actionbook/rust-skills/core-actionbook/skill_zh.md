# Actionbook

浏览器自动化预计算操作手册。代理接收结构化的页面信息，而不是解析整个 HTML。

## 工作流程

1. **search_actions** - 通过关键词搜索，返回基于 URL 的操作 ID 及内容预览
2. **get_action_by_id** - 获取完整操作手册，包含页面详情、DOM 结构和元素选择器
3. **执行** - 使用返回的选择器与您的浏览器自动化工具配合使用

## MCP 工具

- `search_actions` - 通过关键词搜索。返回：基于 URL 的操作 ID、内容预览、相关性分数
- `get_action_by_id` - 获取完整操作详情。返回：操作内容、页面元素选择器（CSS/XPath）、元素类型、允许的方法（点击、输入、提取）、文档元数据

### 参数

**search_actions**:
- `query` (必需)：搜索关键词（例如，"airbnb 搜索"、"google 登录")
- `type`：`vector` | `fulltext` | `hybrid` (默认)
- `limit`：最大结果数（默认：5）
- `sourceIds`：按源 ID 过滤（逗号分隔）
- `minScore`：最低相关性分数（0-1）

**get_action_by_id**:
- `id` (必需)：基于 URL 的操作 ID（例如，`example.com/page`）

## 示例响应

```json
{
  "title": "Airbnb 搜索",
  "url": "www.airbnb.com/search",
  "elements": [
    {
      "name": "location_input",
      "selector": "input[data-testid='structured-search-input-field-query']",
      "type": "textbox",
      "methods": ["type", "fill"]
    }
  ]
}
```
