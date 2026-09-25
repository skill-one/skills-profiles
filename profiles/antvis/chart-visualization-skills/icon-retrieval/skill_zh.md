# 图标搜索

直接使用 `curl` 调用图标 HTTP API。

## API

### 搜索接口

- **方法**: `GET`
- **URL**: `https://www.weavefox.cn/api/v1/infographic/icon`
- **查询参数**:
  - `text` (必填): 搜索关键词，例如 `"数据分析"`
  - `topK` (可选): 需要获取的图标数量 (1-20)，默认 `5`

示例:

```bash
curl -sS -L --max-time 20 "https://www.weavefox.cn/api/v1/infographic/icon?text=document&topK=5"
```

典型响应:

```json
{
  "success": true,
  "data": [
    "https://example.com/icon1.svg",
    "https://example.com/icon2.svg"
  ]
}
```

### 获取 SVG 内容

```bash
curl -sS -L --max-time 20 "https://example.com/icon1.svg"
```

## 工作流程

1. 确定图标概念关键词 (例如: `security`, `document`, `data`)。
2. 使用 API 接口搜索图标 URL。
3. 使用 `curl` 获取选定 URL 的 SVG 内容。
4. 直接在页面、图表或信息图表材料中使用 SVG。

## 注意事项

- `text` 中的特殊字符需进行 URL 编码。
- `topK` 范围为 1–20；若未指定，服务将返回最多 5 条结果。
- 网络问题可尝试使用较小的 `topK` 重试或验证接口可访问性。
