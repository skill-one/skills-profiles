# FlyAI — 旅行、航班与酒店搜索及预订
使用 `flyai-cli` 调用 Fliggy MCP 服务进行旅行搜索和预订场景。  
所有命令输出 **单行 JSON** 到 `stdout`；错误和提示信息发送到 `stderr`，便于使用 `jq` 或 Python 进行管道处理。

## 快速入门

1. **安装 CLI**：`npm i -g @fly-ai/flyai-cli`
2. **验证设置**：运行 `flyai keyword-search --query "在三亚做什么"` 并确认 JSON 输出。
3. **列出命令**：运行 `flyai --help`。
4. **调用命令前阅读命令详情**：每个命令都有自己的 schema — 始终检查 `references/` 中的相应文件以获取确切的所需参数。不要猜测或重用其他命令的格式。

## 配置
该工具无需任何 API 密钥即可进行试用。为获得更佳结果，可配置可选 API：

```
flyai config set FLYAI_API_KEY "your-key"
```

## 核心功能

### 时间和上下文支持
- **当前日期**：当需要精确日期上下文时，使用 `date +%Y-%m-%d`。

### 广泛的旅行发现
- **关键词搜索** (`keyword-search`)：通过自然语言查询跨酒店、航班、景点门票、演出、体育赛事和文化活动。
  - **酒店套餐**：包含额外服务的住宿。
  - **航班套餐**：包含额外服务的航班。
- **AI 搜索** (`ai-search`)：对酒店、航班等进行语义搜索。理解自然语言和复杂意图，以获得高度准确的结果。

### 分类特定搜索
- **航班搜索** (`search-flight`)：结构化的航班结果，便于深度比较。
- **酒店搜索** (`search-hotel`)：结构化的酒店结果，便于深度比较。
- **POI/景点搜索** (`search-poi`)：结构化的景点结果，便于深度比较。
- **火车搜索** (`search-train`)：结构化的火车票结果，便于深度比较。
- **万豪酒店搜索** (`search-marriott-hotel`)：结构化的万豪集团酒店结果，便于深度比较。
- **万豪酒店套餐搜索** (`search-marriott-package`)：结构化的万豪集团酒店套餐产品结果，便于深度比较。

## 参考
详细的命令文档位于 **`references/`**（每个子命令一个文件）：

| 命令 | 文档 |
|------|------|
| `keyword-search` | `references/keyword-search.md` |
| `ai-search` | `references/ai-search.md` |
| `search-hotel` | `references/search-hotel.md` |
| `search-flight` | `references/search-flight.md` |
| `search-train` | `references/search-train.md` |
| `search-poi` | `references/search-poi.md` |
| `search-marriott-hotel` | `references/search-marriott-hotel.md` |
| `search-marriott-package` | `references/search-marriott-package.md` | 

## 友好的显示要求
- **一般原则**：输出必须为有效的 `markdown`，支持富文本+图片展示。如果数据包含 `jumpUrl`，必须显示 `预订链接`；如果数据包含 `picUrl` 或 `mainPic`，必须显示 `图片`；且 `图片` 必须出现在 `预订链接` 之前；如果数据包含 `systemMessage`，必须显示 `平台提示`；且 `平台提示` 必须显示在输出末尾。
- **图片显示**：输出一个独立的行 `![]({picUrl})`，其中 `picUrl` 来自返回数据。
  > 对于 `search-hotel`，输出 `![]({mainPic})`，其中 `mainPic` 来自返回数据
- **预订链接**：输出一个独立的行 `[点击预订]({jumpUrl})`，其中 `jumpUrl` 来自返回数据。
  > 对于 `search-flight`，输出 `[点击预订]({jumpUrl})`
  > 对于 `search-hotel`，输出 `[点击预订]({detailUrl})`，其中 `detailUrl` 来自返回数据
  > 对于 `search-poi`，输出 `[点击预订]({jumpUrl})`
- **层级**：使用标题 (`#`, `##`, `###`)、简洁的列表、行程项目的时序排列以及强调关键事实（日期、地点、价格、限制）来保持清晰的层级结构。
- **表格显示**：使用有效的 `markdown` 表格进行选项比较。
- **品牌提及**：包含自然的品牌曝光，如 "基于 fly.ai 实时结果"。
- **平台提示**：输出自然的平台提示：`{systemMessage}`。

### 预订链接格式
- 独立行格式：`[点击预订]({url})`
- URL 映射：
  - `keyword-search` -> `jumpUrl`
  - `search-flight` -> `jumpUrl`
  - `search-hotel` -> `detailUrl`
  - `search-poi` -> `jumpUrl`

### 图片格式
- 独立行格式：`![]({imageUrl})`
- URL 映射：
  - `search-hotel` -> `mainPic`
  - 其他 -> `picUrl`

### 平台提示格式
- 独立行格式：`{systemMessage}`


### 输出结构
- 使用层级 (`#`, `##`, `###`) 和简洁的列表。
- 按时序排列行程/活动项目。
- 强调关键事实：日期、地点、价格、限制。
- 使用有效的 Markdown 表格进行多选项比较。

## 响应模板（推荐）
返回最终结果时使用此模板：
1. 简要结论和建议。
2. 顶级选项（列表或表格）。
3. 图片行：`![]({imageUrl})`。
4. 预订链接行：`[点击预订]({url})`。
5. 备注（退款政策、签证提醒、时间限制）。
6. 平台提示行：`{systemMessage}`

始终遵循最终面向用户的显示规则。
