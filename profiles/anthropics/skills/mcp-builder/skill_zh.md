# MCP 服务器开发指南

## 概述

创建 MCP (Model Context Protocol) 服务器，使大语言模型（LLMs）能够通过设计合理的工具与外部服务进行交互。MCP 服务器的质量以衡量其如何助力大语言模型完成真实世界任务的能力为标准。

---

# 流程

## 流程

## 🚀 高级工作流程

创建高质量的 MCP 服务器涉及四个主要阶段：

### 阶段 1：深度研究与规划

#### 1.1 理解现代 MCP 设计

**API 覆盖与工作流工具：**
平衡全面的 API 端点覆盖与专门的 workflow 工具。对于特定任务，工作流工具更为便捷；而全面的覆盖则为智能体（agents）提供组合操作的灵活性。性能因客户端而异——某些客户端受益于将基础工具与代码执行相结合，而其他客户端则更适合高级工作流。不确定时，优先确保全面的 API 覆盖。

**工具命名与可发现性：**
清晰、描述性的工具名称有助于智能体（agents）快速找到合适的工具。使用一致的名称前缀（例如 `github_create_issue`、`github_list_repos`）以及面向操作的命名方式。

**上下文管理：**
智能体（agents）受益于简洁的工具描述以及能够过滤和分页的结果能力。设计能够返回聚焦、相关数据的工具。某些客户端支持代码执行，有助于智能体高效过滤和处理数据。

**可操作的错误提示：**
错误提示应引导智能体（agents）找到解决方案，并给出具体的建议和后续步骤。

#### 1.2 研读 MCP 协议文档

**导航 MCP 规范：**

首先从站点地图（sitemap）查找相关页面：`https://modelcontextprotocol.io/sitemap.xml`

随后使用 `.md` 后缀获取特定页面，以获取 Markdown 格式（例如 `https://modelcontextprotocol.io/specification/draft.md`）。

**需审阅的关键页面：**
- 规范概述与架构
- 传输机制（可流式 HTTP、stdio）
- 工具、资源和提示词定义

#### 1.3 研读框架文档

**推荐技术栈：**
- **语言**：TypeScript（提供高质量的 SDK 支持，且在 MCPB 等多种执行环境中具有良好的兼容性；此外，AI 模型擅长生成 TypeScript 代码，得益于其广泛的用法、静态类型以及优秀的 linting 工具）。
- **传输方式**：远程服务器使用可流式 HTTP，采用无状态 JSON（相较于有状态会话和流式响应，更易扩展与维护）；本地服务器使用 stdio。

**加载框架文档：**

- **MCP 最佳实践**：[📋 查看最佳实践](./reference/mcp_best_practices.md) - 核心准则

**对于 TypeScript（推荐）：**
- **TypeScript SDK**：使用 WebFetch 加载 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript 指南](./reference/node_mcp_server.md) - TypeScript 模式与示例

**对于 Python：**
- **Python SDK**：使用 WebFetch 加载 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python 指南](./reference/python_mcp_server.md) - Python 模式与示例

#### 1.4 规划你的实现

**理解 API：**
查阅服务的 API 文档，识别关键端点、认证要求和数据模型。根据需要，使用网络搜索和 WebFetch。

**工具选择：**
优先确保全面的 API 覆盖。列出待实现的端点，从最常见的操作开始。

---

### 阶段 2：实现

#### 2.1 设置项目结构

参见语言特定的指南以完成项目设置：
- [⚡ TypeScript 指南](./reference/node_mcp_server.md) - 项目结构、package.json、tsconfig.json
- [🐍 Python 指南](./reference/python_mcp_server.md) - 模块组织、依赖项

#### 2.2 实现核心基础设施

创建共享工具：
- API 客户端（含认证）
- 错误处理辅助函数
- 响应格式化（JSON/Markdown）
- 分页支持

#### 2.3 实现工具

对于每个工具：

**输入模式：**
- 使用 Zod（TypeScript）或 Pydantic（Python）
- 包含约束条件与清晰的描述
- 在字段描述中添加示例

**输出模式：**
- 尽可能定义 `outputSchema`
- 在工具响应中使用 `structuredContent`（TypeScript SDK 功能）
- 有助于客户端理解与处理工具输出

**工具描述：**
- 功能的简洁总结
- 参数描述
- 返回类型模式

**实现：**
- 使用 async/await 处理 I/O 操作
- 使用可操作的错误提示进行正确的错误处理
- 必要时支持分页
- 使用现代 SDK 时，同时返回文本内容与结构化数据

**注解：**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### 阶段 3：审查与测试

#### 3.1 代码质量

审查时需检查：
- 无重复代码（DRY 原则）
- 一致的错误处理
- 完整的类型覆盖
- 清晰的工具描述

#### 3.2 构建与测试

**TypeScript：**
- 运行 `npm run build` 以验证编译
- 使用 MCP Inspector 测试：`npx @modelcontextprotocol/inspector`

**Python：**
- 验证语法：`python -m py_compile your_server.py`
- 使用 MCP Inspector 测试

参见语言特定的指南，了解详细的测试方法与质量检查清单。

---

### 阶段 4：创建评估

在实现你的 MCP 服务器后，创建全面的评估，以测试其有效性。

**加载 [✅ 评估指南](./reference/evaluation.md) 以获取完整的评估准则。**

#### 4.1 理解评估目的

使用评估来测试大语言模型（LLMs）是否能够有效地利用你的 MCP 服务器回答现实、复杂的提问。

#### 4.2 创建 10 个评估问题

创建有效的评估，需遵循评估指南中概述的流程：

1. **工具检查**：列出可用工具并理解其功能
2. **内容探索**：使用 READ-ONLY 操作来探索可用数据
3. **问题生成**：创建 10 个复杂、现实的提问
4. **答案验证**：自行解答每个问题以验证答案

#### 4.3 评估要求

确保每个问题均满足以下要求：
- **独立**：不依赖其他问题
- **只读**：仅使用非破坏性操作
- **复杂**：需要多次调用工具并深入探索
- **现实**：基于真实用例
- **可验证**：存在单一、清晰的答案，可通过字符串比较进行验证
- **稳定**：答案不会随时间变化

#### 4.4 输出格式

创建包含以下结构的 XML 文件：

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# 参考文件

## 📚 文档库

在开发过程中根据需要加载这些资源：

### 核心 MCP 文档（优先加载）
- **MCP 协议**：从 `https://modelcontextprotocol.io/sitemap.xml` 的站点地图开始，随后使用 `.md` 后缀获取特定页面
- [📋 MCP 最佳实践](./reference/mcp_best_practices.md) - 包含：
  - 服务器与工具命名规范
  - 响应格式准则（JSON 与 Markdown 对比）
  - 分页最佳实践
  - 传输方式选择（可流式 HTTP 与 stdio）
  - 安全与错误处理标准

### SDK 文档（在 1/2 阶段加载）
- **Python SDK**：从 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` 获取
- **TypeScript SDK**：从 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` 获取

### 语言特定实现指南（在阶段 2 加载）
- [🐍 Python 实现指南](./reference/python_mcp_server.md) - 完整的 Python/FastMCP 指南，包含：
  - 服务器初始化模式
  - Pydantic 模型示例
  - 使用 `@mcp.tool` 的工具注册
  - 完整可用示例
  - 质量检查清单

- [⚡ TypeScript 实现指南](./reference/node_mcp_server.md) - 完整的 TypeScript 指南，包含：
  - 项目结构
  - Zod 模式
  - 使用 `server.registerTool` 的工具注册
  - 完整可用示例
  - 质量检查清单

### 评估指南（在阶段 4 加载）
- [✅ 评估指南](./reference/evaluation.md) - 完整的评估创建指南，包含：
  - 问题创建准则
  - 答案验证策略
  - XML 格式规范
  - 示例问题与答案
  - 使用提供的脚本运行评估
