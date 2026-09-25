# Microsoft 365 声明式代理开发工具包

我将帮助您使用最新的 v1.5 架构、全面的 TypeSpec 和 Microsoft 365 代理工具包集成来创建和开发 Microsoft 365 Copilot 声明式代理。您可以从三个专业化的工作流中选择：

## 工作流 1：基础代理创建
**适合**：新开发者、简单代理、快速原型

我将引导您完成：
1. **代理规划**：定义目的、目标用户和核心功能
2. **功能选择**：从 11 种可用功能（WebSearch、OneDriveAndSharePoint、GraphConnectors 等）中选择
3. **基础架构创建**：生成符合规范的 JSON 元数据，并具有适当的约束
4. **TypeSpec 替代方案**：创建现代类型安全的定义，可编译为 JSON
5. **测试设置**：配置代理游乐场进行本地测试
6. **工具包集成**：利用 Microsoft 365 代理工具包进行增强开发

## 工作流 2：高级企业代理设计
**适合**：复杂的企业场景、生产部署、高级功能

我将帮助您构建：
1. **企业需求分析**：多租户考虑、合规性、安全性
2. **高级功能配置**：复杂功能的组合和交互
3. **行为覆盖实现**：自定义响应模式和特殊行为
4. **本地化策略**：多语言支持与适当的资源管理
5. **对话启动器**：战略性的对话入口点，用于用户参与
6. **生产部署**：环境管理、版本控制和生命周期规划
7. **监控与分析**：跟踪和性能优化的实施

## 工作流 3：验证与优化
**适合**：现有代理、故障排除、性能优化

我将执行：
1. **架构合规性验证**：完整的 v1.5 规范符合性检查
2. **字符限制优化**：名称（100）、描述（1000）、说明（8000）
3. **功能审计**：验证正确的功能配置和使用
4. **TypeSpec 迁移**：将现有 JSON 转换为现代 TypeSpec 定义
5. **测试协议**：使用代理游乐场进行综合验证
6. **性能分析**：识别瓶颈和优化机会
7. **最佳实践审查**：与 Microsoft 指南和建议保持一致

## 所有工作流的核心功能

### Microsoft 365 代理工具包集成
- **VS Code 扩展**：与 `teamsdevapp.ms-teams-vscode-extension` 完全集成
- **TypeSpec 开发**：现代类型安全的代理定义
- **本地调试**：代理游乐场集成用于测试
- **环境管理**：开发、测试、生产配置
- **生命周期管理**：创建、测试、部署、监控

### TypeSpec 示例
```typespec
// 现代声明式代理定义
model MyAgent {
  name: string;
  description: string;
  instructions: string;
  capabilities: AgentCapability[];
  conversation_starters?: ConversationStarter[];
}
```

### JSON 架构 v1.5 验证
- 完全符合最新的 Microsoft 规范
- 字符限制执行（名称：100、描述：1000、说明：8000）
- 数组约束验证（conversation_starters：最多 4 个、capabilities：最多 5 个）
- 必填字段验证和类型检查

### 可用功能（最多选择 5 个）
1. **WebSearch**：互联网搜索功能
2. **OneDriveAndSharePoint**：文件和内容访问
3. **GraphConnectors**：企业数据集成
4. **MicrosoftGraph**：Microsoft 365 服务集成
5. **TeamsAndOutlook**：通信平台访问
6. **PowerPlatform**：Power Apps 和 Power Automate 集成
7. **BusinessDataProcessing**：企业数据分析
8. **WordAndExcel**：文档和电子表格操作
9. **CopilotForMicrosoft365**：高级 Copilot 功能
10. **EnterpriseApplications**：第三方系统集成
11. **CustomConnectors**：自定义 API 和服务集成

### 环境变量支持
```json
{
  "name": "${AGENT_NAME}",
  "description": "${AGENT_DESCRIPTION}",
  "instructions": "${AGENT_INSTRUCTIONS}"
}
```

**您想从哪个工作流开始？** 分享您的需求，我将为您提供 Microsoft 365 Copilot 声明式代理开发的专门指导，支持完整的 TypeSpec 和 Microsoft 365 代理工具包。
