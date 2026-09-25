# Power Platform MCP 连接器套件

使用模型上下文协议集成，为 Microsoft Copilot Studio 生成全面的 Power Platform 自定义连接器实现。

## Copilot Studio 中的 MCP 功能

**目前支持：**
- ✅ **工具**：LLM 可调用的函数（需用户批准）
- ✅ **资源**：代理可读取的文件类数据（必须是工具输出）

**尚未支持：**
- ❌ **提示**：预写模板（准备未来支持）

## 连接器生成

使用以下内容创建完整的 Power Platform 连接器：

**核心文件：**
- `apiDefinition.swagger.json`，包含 `x-ms-agentic-protocol: mcp-streamable-1.0`
- `apiProperties.json`，包含连接器元数据和认证信息
- `script.csx`，包含用于 MCP JSON-RPC 处理的自定义 C# 转换
- `readme.md`，包含连接器文档

**MCP 集成：**
- POST `/mcp` 端点用于 JSON-RPC 2.0 通信
- McpResponse 和 McpErrorResponse 架构定义
- Copilot Studio 约束符合性（不支持引用类型，仅支持单类型）
- 资源集成作为工具输出（支持资源和工具；尚未支持提示）

## 架构验证与故障排除

**验证架构以符合 Copilot Studio 要求：**
- ✅ 工具输入/输出中无引用类型（`$ref`）
- ✅ 仅支持单类型值（不是 `["string", "number"]`）
- ✅ 基本类型：字符串、数字、整数、布尔值、数组、对象
- ✅ 资源作为工具输出，不是独立实体
- ✅ 所有端点使用完整 URI

**常见问题和修复方法：**
- 工具被过滤 → 移除引用类型，使用基本类型
- 类型错误 → 使用带验证逻辑的单类型
- 资源不可用 → 包含在工具输出中
- 连接失败 → 验证 `x-ms-agentic-protocol` 标头

## 上下文变量

- **连接器名称**：[连接器的显示名称]
- **服务器用途**：[MCP 服务器应实现的功能]
- **所需工具**：[要实现的 MCP 工具列表]
- **资源**：[要提供的资源类型]
- **认证**：[无、api-key、oauth2、basic]
- **主机环境**：[Azure Function、Express.js 等]
- **目标 API**：[要集成的外部 API]

## 生成模式

### 模式 1：全新连接器
从零开始生成新的 Power Platform MCP 连接器的所有文件，包括 CLI 验证设置。

### 模式 2：架构验证
使用 paconn 和验证工具分析并修复现有架构以符合 Copilot Studio 要求。

### 模式 3：集成故障排除
使用 CLI 调试工具诊断和解决与 Copilot Studio 的 MCP 集成问题。

### 模式 4：混合连接器
为现有的 Power Platform 连接器添加 MCP 功能，并使用适当的验证工作流。

### 模式 5：认证准备
准备连接器以提交给 Microsoft 认证，包括完整的元数据和验证符合性。

### 模式 6：OAuth 安全加固
实施 OAuth 2.0 认证，并结合 MCP 安全最佳实践和高级令牌验证。

## 预期输出

**1. apiDefinition.swagger.json**
- 使用 Microsoft 扩展的 Swagger 2.0 格式
- MCP 端点：`POST /mcp`，带有正确的协议标头
- 符合规范的架构定义（仅基本类型）
- McpResponse/McpErrorResponse 定义

**2. apiProperties.json**
- 连接器元数据和品牌标识（需要 `iconBrandColor`）
- 认证配置
- 用于 MCP 转换的策略模板

**3. script.csx**
- JSON-RPC 2.0 消息处理
- 请求/响应转换
- MCP 协议符合性逻辑
- 错误处理和验证

**4. 实现指南**
- 工具注册和执行模式
- 资源管理策略
- Copilot Studio 集成步骤
- 测试和验证程序

## 验证清单

### 技术符合性
- [ ] MCP 端点包含 `x-ms-agentic-protocol: mcp-streamable-1.0`
- [ ] 任何架构定义中无引用类型
- [ ] 所有类型字段为单类型（不是数组）
- [ ] 资源作为工具输出
- [ ] script.csx 中的 JSON-RPC 2.0 符合性
- [ ] 全程使用完整 URI 端点
- [ ] 为 Copilot Studio 代理提供清晰描述
- [ ] 认证配置正确
- [ ] 用于 MCP 转换的策略模板
- [ ] 生成编排兼容性

### CLI 验证
- [ ] **paconn validate**：`paconn validate --api-def apiDefinition.swagger.json` 无错误通过
- [ ] **pac CLI 就绪**：可以使用 `pac connector create/update` 创建/更新连接器
- [ ] **脚本验证**：script.csx 在 pac CLI 上传期间通过自动验证
- [ ] **包验证**：`ConnectorPackageValidator.ps1` 成功运行

### OAuth 和安全要求
- [ ] **OAuth 2.0 增强版**：标准 OAuth 2.0 结合 MCP 安全最佳实践实现
- [ ] **令牌验证**：实现令牌受众验证以防止传递攻击
- [ ] **自定义安全逻辑**：script.csx 中的增强验证以符合 MCP 要求
- [ ] **状态参数保护**：为 CSRF 防护安全保护状态参数
- [ ] **HTTPS 强制**：所有生产端点仅使用 HTTPS
- [ ] **MCP 安全实践**：在 OAuth 2.0 中实现混淆代理攻击防护

### 认证要求
- [ ] **完整元数据**：settings.json 包含产品和服务的详细信息
- [ ] **图标符合性**：PNG 格式，尺寸为 230x230 或 500x500
- [ ] **文档**：认证就绪的 readme，包含全面示例
- [ ] **安全符合性**：结合 MCP 安全实践的 OAuth 2.0，隐私政策
- [ ] **认证流程**：配置正确的 OAuth 2.0 和自定义安全验证

## 示例用法

```yaml
模式：全新连接器
连接器名称：Customer Analytics MCP
服务器用途：客户数据分析与洞察
所需工具：
  - searchCustomers：按条件查找客户
  - getCustomerProfile：检索详细客户数据
  - analyzeCustomerTrends：生成趋势分析
资源：
  - 客户资料（JSON 数据）
  - 分析报告（结构化数据）
认证：oauth2
主机环境：Azure Function
目标 API：CRM REST API
```
