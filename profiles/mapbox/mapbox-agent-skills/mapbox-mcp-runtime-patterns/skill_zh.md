# Mapbox MCP 运行时模式

此技能为将 Mapbox MCP 服务器集成到具有地理空间功能的 AI 应用中提供生产模式。

## 什么是 Mapbox MCP 服务器？

[Mapbox MCP 服务器](https://github.com/mapbox/mcp-server) 是一个模型上下文协议 (MCP) 服务器，为 AI 代理提供地理空间工具：

**离线工具 (Turf.js):**

- 距离、方位角、中点计算
- 点在多边形内测试
- 面积、缓冲区、质心操作
- 边界框、几何体简化
- 无 API 调用，即时结果

**Mapbox API 工具:**

- 导航和路线规划
- 反向地理编码
- POI 类别搜索
- 等时线（可达性）
- 旅行时间矩阵
- 静态地图图像
- GPS 追踪地图匹配
- 多点路线优化

**实用工具:**

- 服务器版本信息
- POI 类别列表

**主要优势:** 无需手动集成多个 API，即可为您的 AI 应用提供地理空间超能力。

## 理解工具类别

在集成之前，了解工具之间的关键区别，以帮助您的 LLM 正确选择：

### 距离：“直线距离”与“沿道路距离”

**直线距离**（离线，即时）：

- 工具：`distance_tool`、`bearing_tool`、`midpoint_tool`
- 用于：邻近性检查，“X 距离多远？”，比较距离
- 示例： "这家餐厅在 2 英里范围内吗？" → `distance_tool`

**路线距离**（API，考虑交通状况）：

- 工具：`directions_tool`、`matrix_tool`
- 用于：导航、驾驶时间，“开车需要多长时间？”
- 示例： "开车到那里需要多长时间？" → `directions_tool`

### 搜索：类别/类型与具体地点

**类别/类型搜索**：

- 工具：`category_search_tool`
- 用于： "查找咖啡店"、"附近有餐厅"、"按类型浏览"
- 示例： "附近有什么酒店？" → `category_search_tool`

**具体地点/地址**：

- 工具：`search_and_geocode_tool`、`reverse_geocode_tool`
- 用于：命名地点、街道地址、地标
- 示例： "查找 123 Main Street" → `search_and_geocode_tool`

### 旅行时间：区域与路线

**可达区域**（在可达范围内）：

- 工具：`isochrone_tool`
- 返回：可到达的每个地方的 GeoJSON 多边形
- 示例： "15 分钟内我能到达什么？" → `isochrone_tool`

**具体路线**（如何到达那里）：

- 工具：`directions_tool`
- 返回：前往一个目的地的逐向导航
- 示例： "我如何去机场？" → `directions_tool`

### 成本与性能

**离线工具**（免费，即时）：

- 无 API 调用，无 token 使用
- 当不需要实时数据时使用
- 示例： `distance_tool`、`point_in_polygon_tool`、`area_tool`

**API 工具**（需要 token，计入使用量）：

- 实时交通、实时 POI 数据、当前条件
- 当准确性和新鲜度很重要时使用
- 示例： `directions_tool`、`category_search_tool`、`isochrone_tool`

**最佳实践：** 尽可能优先使用离线工具，当需要实时数据或路线时使用 API 工具。

## 安装与设置

### 选项 1：托管服务器（推荐）

**最简单的集成** - 使用 Mapbox 托管的 MCP 服务器：

```
https://mcp.mapbox.com/mcp
```

无需安装。只需在 `Authorization` 头中传递您的 Mapbox 访问 token。

**优势：**

- 无需服务器管理
- 始终保持最新
- 生产就绪
- 更低延迟（Mapbox 基础设施）

**认证：**

使用基于 token 的认证（程序化访问的标准）：

```
Authorization: Bearer your_mapbox_token
```

**注意：** 托管服务器也支持 OAuth，但主要用于交互式流程（编码助手，而非生产应用）。

### 选项 2：自托管

用于自定义部署或开发：

```bash
npm install @mapbox/mcp-server
```

或直接通过 npx 使用：

```bash
npx @mapbox/mcp-server
```

**环境设置：**

```bash
export MAPBOX_ACCESS_TOKEN="your_token_here"
```

## 参考文件

详细的集成模式和生产指南按任务相关组织到参考文件中。加载与您的任务相关的文件。

- **Pydantic AI** -- 类型安全的 Python 代理
  加载：`references/pydantic-ai.md`

- **CrewAI** -- 多代理编排
  加载：`references/crewai.md`

- **Smolagents** -- 轻量级 HuggingFace 代理
  加载：`references/smolagents.md`

- **Mastra** -- 多代理 TypeScript 系统
  加载：`references/mastra.md`

- **LangChain** -- 基于工具链的对话式 AI
  加载：`references/langchain.md`

- **自定义代理** -- Zillow/TripAdvisor/DoorDash 风格的模式、架构图、混合方法
  加载：`references/custom-agent.md`

- **用例** -- 房地产、外卖、旅行规划示例
  加载：`references/use-cases.md`

- **生产模式** -- 缓存、批量操作、工具描述、错误处理、安全、速率限制、测试
  加载：`references/production.md`

## 资源

- [Mapbox MCP 服务器](https://github.com/mapbox/mcp-server)
- [模型上下文协议](https://modelcontextprotocol.io)
- [Pydantic AI](https://ai.pydantic.dev/)
- [Mastra](https://mastra.ai/)
- [LangChain](https://docs.langchain.com/oss/javascript/langchain/overview/)
- [Mapbox API 文档](https://docs.mapbox.com/api/)

## 何时使用此技能

在以下情况下调用此技能：

- 将 Mapbox MCP 服务器集成到 AI 应用中
- 构建具有地理空间功能的 AI 代理
- 架构 Zillow/TripAdvisor/DoorDash 风格的应用程序并使用 AI
- 在 MCP、直接 API 或 SDK 之间进行选择
- 优化生产中的地理空间操作
- 实现地理空间 AI 功能的错误处理
- 使用地理空间工具测试 AI 应用程序
