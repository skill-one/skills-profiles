# MCP 服务器开发指南

## 概述

创建 MCP（模型上下文协议）服务器，使大型语言模型能够通过精心设计的工具与外部服务进行交互。MCP 服务器的质量取决于它是否能够有效地帮助大型语言模型完成实际任务。

---

# 流程

## 🚀 高层工作流程

创建高质量的 MCP 服务器涉及四个主要阶段：

### 阶段 1：深入研究与规划

#### 1.1 理解现代 MCP 设计

**API 覆盖率与工作流工具：**
在全面 API 端点覆盖和专用工作流工具之间取得平衡。工作流工具对于特定任务可能更方便，而全面覆盖则赋予代理组合操作的灵活性。性能因客户端而异——某些客户端从组合基本工具的代码执行中受益，而其他客户端则更适合使用高级工作流。在不确定的情况下，优先考虑全面 API 覆盖。

**工具命名与可发现性：**
清晰、描述性的工具名称有助于代理快速找到正确的工具。使用一致的命名前缀（例如，`github_create_issue`，`github_list_repos`）和动作导向的命名。

**上下文管理：**
代理受益于简洁的工具描述以及过滤/分页结果的能力。设计返回聚焦、相关数据的工具。某些客户端支持代码执行，这可以帮助代理高效地过滤和处理数据。

**可操作的错误消息：**
错误消息应通过具体的建议和下一步操作指导代理找到解决方案。

#### 1.2 研究 MCP 协议文档

**导航 MCP 规范：**

从站点地图开始查找相关页面：`https://modelcontextprotocol.io/sitemap.xml`

然后使用 `.md` 后缀获取特定页面以获取 Markdown 格式（例如，`https://modelcontextprotocol.io/specification/draft.md`）。

需要审查的关键页面：
- 规范概述和架构
- 传输机制（流式 HTTP，stdio）
- 工具、资源和提示定义

#### 1.3 研究框架文档

**推荐的技术栈：**
- **语言**：TypeScript（高质量的 SDK 支持和在许多执行环境（例如 MCPB）中的良好兼容性。此外，AI 模型擅长生成 TypeScript 代码，受益于其广泛使用、静态类型和良好的代码格式化工具）
- **传输**：流式 HTTP 用于远程服务器，使用无状态的 JSON（相对于有状态的会话和流式响应，更简单扩展和维护）。stdio 用于本地服务器。

**加载框架文档：**

- **MCP 最佳实践**：[📋 查看最佳实践](./reference/mcp_best_practices.md) - 核心指南

**对于 TypeScript（推荐）：**
- **TypeScript SDK**：使用 WebFetch 加载 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript 指南](./reference/node_mcp_server.md) - TypeScript 模式和示例

**对于 Python：**
- **Python SDK**：使用 WebFetch 加载 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python 指南](./reference/python_mcp_server.md) - Python 模式和示例

#### 1.4 规划您的实现

**理解 API：**
审查服务的 API 文档，以识别关键端点、身份验证要求和数据模型。按需使用网络搜索和 WebFetch。

**工具选择：**
优先考虑全面 API 覆盖。列出要实现的端点，从最常见的操作开始。

---

### 阶段 2：实现

#### 2.1 设置项目结构

查看语言特定的指南进行项目设置：
- [⚡ TypeScript 指南](./reference/node_mcp_server.md) - 项目结构，package.json，tsconfig.json
- [🐍 Python 指南](./reference/python_mcp_server.md) - 模块组织，依赖项

#### 2.2 实现核心基础设施

创建共享工具：
- 具有身份验证的 API 客户端
- 错误处理辅助工具
- 响应格式化（JSON/Markdown）
- 分页支持

#### 2.3 实现工具

对于每个工具：

**输入模式：**
- 使用 Zod（TypeScript）或 Pydantic（Python）
- 包括约束和清晰的描述
- 在字段描述中添加示例

**输出模式：**
- 尽可能定义 `outputSchema` 以获取结构化数据
- 在工具响应中使用 `structuredContent`（TypeScript SDK 功能）
- 帮助客户端理解和处理工具输出

**工具描述：**
- 功能的简洁摘要
- 参数描述
- 返回类型模式

**实现：**
- 异步/等待用于 I/O 操作
- 正确的错误处理和可操作的错误消息
- 在适用的情况下支持分页
- 使用现代 SDK 时返回文本内容和结构化数据

**注释：**
- `readOnlyHint`：true/false
- `destructiveHint`：true/false
- `idempotentHint`：true/false
- `openWorldHint`：true/false

---

### 阶段 3：审查和测试

#### 3.1 代码质量

审查：
- 无重复代码（DRY 原则）
- 一致的错误处理
- 完整的类型覆盖
- 清晰的工具描述

#### 3.2 构建 和 测试

**TypeScript：**
- 运行 `npm run build` 以验证编译
- 使用 MCP 检查器测试：`npx @modelcontextprotocol/inspector`

**Python：**
- 验证语法：`python -m py_compile your_server.py`
- 使用 MCP 检查器测试

查看语言特定的指南以获取详细的测试方法和质量清单。

---

### 阶段 4：创建评估

在实现您的 MCP 服务器后，创建全面的评估以测试其有效性。

**加载 [✅ 评估指南](./reference/evaluation.md) 获取完整的评估指南。**

#### 4.1 理解评估目的

使用评估来测试大型语言模型是否能够有效地使用您的 MCP 服务器回答现实、复杂的提问。

#### 4.2 创建 10 个评估问题

为了创建有效的评估，请遵循评估指南中概述的过程：

1. **工具检查**：列出可用工具并理解其功能
2. **内容探索**：使用只读操作探索可用数据
3. **问题生成**：创建 10 个复杂、现实的问题
4. **答案验证**：自己解决每个问题以验证答案

#### 4.3 评估要求

确保每个问题：
- **独立**：不依赖于其他问题
- **只读**：只需要非破坏性操作
- **复杂**：需要多个工具调用和深度探索
- **现实**：基于人类关心的实际用例
- **可验证**：可以由字符串比较验证的单一、清晰的答案
- **稳定**：答案不会随时间变化

#### 4.4 输出格式

创建一个具有以下结构的 XML 文件：

```xml
<evaluation>
  <qa_pair>
    <question>查找关于动物名称的 AI 模型发布讨论。一个模型需要一个特定格式的安全标识 ASL-X。正在确定该以斑点野生猫命名的模型中 X 的数字是多少？</question>
    <answer>3</answer>
  </qa_pair>
<!-- 更多 qa_pairs... -->
</evaluation>
```

---

# 参考文件

## 📚 文档库

在开发过程中按需加载这些资源：

### 核心MCP文档（首先加载）
- **MCP 协议**：从 `https://modelcontextprotocol.io/sitemap.xml` 的站点地图开始，然后获取具有 `.md` 后缀的特定页面
- [📋 MCP 最佳实践](./reference/mcp_best_practices.md) - 通用 MCP 指南，包括：
  - 服务器和工具命名约定
  - 响应格式指南（JSON vs Markdown）
  - 分页最佳实践
  - 传输选择（流式 HTTP vs stdio）
  - 安全和错误处理标准

### SDK 文档（在阶段 1/2 加载）
- **Python SDK**：从 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` 获取
- **TypeScript SDK**：从 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` 获取

### 语言特定实现指南（在阶段 2 加载）
- [🐍 Python 实现指南](./reference/python_mcp_server.md) - 完整 Python/FastMCP 指南，包括：
  - 服务器初始化模式
  - Pydantic 模型示例
  - 使用 `@mcp.tool` 注册工具
  - 完整的工作示例
  - 质量清单

- [⚡ TypeScript 实现指南](./reference/node_mcp_server.md) - 完整 TypeScript 指南，包括：
  - 项目结构
  - Zod 模式
  - 使用 `server.registerTool` 注册工具
  - 完整的工作示例
  - 质量清单

### 评估指南（在阶段 4 加载）
- [✅ 评估指南](./reference/evaluation.md) - 完整评估创建指南，包括：
  - 问题创建指南
  - 答案验证策略
  - XML 格式规范
  - 示例问题和答案
  - 使用提供的脚本运行评估
