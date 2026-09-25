# Power Platform MCP 连接器生成器

为 Microsoft Copilot Studio 生成具有模型上下文协议（MCP）集成的完整 Power Platform 自定义连接器。此提示将根据 Power Platform 连接器标准创建所有必要文件，并支持 MCP 流式化 HTTP。

## 说明

创建完整的 MCP 服务器实现，要求：

1. **使用 Copilot Studio MCP 模式**：
   - 实现 `x-ms-agentic-protocol: mcp-streamable-1.0`
   - 支持 JSON-RPC 2.0 通信协议
   - 提供 `/mcp` 的流式化 HTTP 端点
   - 遵循 Power Platform 连接器结构

2. **模式合规性要求**：
   - **工具输入/输出中不引用类型**（由 Copilot Studio 过滤）
   - **仅单类型值**（不是多类型的数组）
   - **避免枚举输入**（解释为字符串，而非枚举）
   - 使用基本类型：字符串、数字、整数、布尔值、数组、对象
   - 确保所有端点返回完整 URI

3. **要包含的 MCP 组件**：
   - **工具**：语言模型调用的函数（✅ Copilot Studio 支持此功能）
   - **资源**：工具的文件状数据输出（✅ Copilot Studio 支持此功能 - 必须是工具输出才能访问）
   - **提示**：特定任务的预定义模板（❌ Copilot Studio 尚不支持此功能）

4. **实现结构**：
   ```
   /apiDefinition.swagger.json  (Power Platform 连接器模式)
   /apiProperties.json         (连接器元数据和配置)
   /script.csx                 (自定义代码转换和逻辑)
   /server/                    (MCP 服务器实现)
   /tools/                     (单个 MCP 工具)
   /resources/                 (MCP 资源处理程序)
   ```

## 上下文变量

- **服务器目的**：[描述 MCP 服务器应实现的功能]
- **所需工具**：[要实现的特定工具列表]  
- **资源**：[要提供的资源类型]
- **认证**：[认证方法：无、api-key、oauth2]
- **主机环境**：[Azure Function、Express.js、FastAPI 等]
- **目标 API**：[要集成的外部 API]

## 预期输出

生成：

1. **apiDefinition.swagger.json**，包含：
   - 正确的 `x-ms-agentic-protocol: mcp-streamable-1.0`
   - POST `/mcp` 的 MCP 端点
   - 合规的模式定义（无引用类型）
   - McpResponse 和 McpErrorResponse 定义

2. **apiProperties.json**，包含：
   - 连接器元数据和品牌标识
   - 认证配置
   - 如有需要，策略模板

3. **script.csx**，包含：
   - 用于请求/响应转换的自定义 C# 代码
   - MCP JSON-RPC 消息处理逻辑
   - 数据验证和处理函数
   - 错误处理和日志记录功能

4. **MCP 服务器代码**，包含：
   - JSON-RPC 2.0 请求处理程序
   - 工具注册和执行
   - 资源管理（作为工具输出）
   - 正确的错误处理
   - Copilot Studio 兼容性检查

5. **单个工具**，要求：
   - 仅接受基本类型输入
   - 返回结构化输出
   - 当需要时，将资源作为输出包含
   - 为 Copilot Studio 提供清晰的描述

6. **部署配置**，用于：
   - Power Platform 环境
   - Copilot Studio 代理集成
   - 测试和验证

## 验证清单

确保生成的代码：
- [ ] 模式中无引用类型
- [ ] 所有类型字段为单类型
- [ ] 通过字符串进行枚举处理并验证
- [ ] 资源可通过工具输出访问
- [ ] 完整 URI 端点
- [ ] JSON-RPC 2.0 合规性
- [ ] 正确的 x-ms-agentic-protocol 标头
- [ ] McpResponse/McpErrorResponse 模式
- [ ] 为 Copilot Studio 提供清晰的工具描述
- [ ] 兼容生成式编排

## 示例用法

```yaml
服务器目的：客户数据管理和分析
所需工具： 
  - searchCustomers
  - getCustomerDetails
  - analyzeCustomerTrends
资源：
  - 客户档案
  - 分析报告
认证：oauth2
主机环境：Azure Function
目标 API：CRM 系统REST API
```
