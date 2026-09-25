# Microsoft 技能创建器

为 Microsoft 技术 创建混合技能，这些技能将核心知识存储在本地，同时支持动态的 Learn MCP 查询以获取更深入的信息。

## 关于技能

技能是模块化包，通过专业知识和工作流程扩展代理的功能。一个技能可以将通用代理转换为特定领域的专业代理。

### 技能结构

```
skill-name/
├── SKILL.md (必需)     # 前置内容 (名称、描述) + 指导说明
├── references/         # 需要时加载到上下文中的文档
├── sample_codes/       # 可运行的代码示例
└── assets/             # 输出中使用的文件 (模板等)
```

### 关键原则

- **前置内容至关重要**: `name` 和 `description` 决定技能何时触发——要清晰全面
- **简洁是关键**: 仅包含代理已知的部分；上下文窗口是共享的
- **无重复**: 信息存在于 SKILL.md 或参考文件中，而非两者兼具

## Learn MCP 工具

| 工具               | 目的               | 使用时机             |
|-------------------|--------------------|---------------------|
| `microsoft_docs_search` | 搜索官方文档       | 初步发现、查找主题   |
| `microsoft_docs_fetch` | 获取完整页面内容   | 深入研究重要页面     |
| `microsoft_code_sample_search` | 查找代码示例       | 获取实现模式         |

### CLI 替代方案

如果 Learn MCP 服务器不可用，请从终端或 shell (例如 Bash、PowerShell 或 cmd) 使用 `mslearn` CLI 而不是：

```bash
# 直接运行 (无需安装)
npx @microsoft/learn-cli search "semantic kernel overview"

# 或者全局安装后运行
npm install -g @microsoft/learn-cli
mslearn search "semantic kernel overview"
```

| MCP 工具           | CLI 命令           |
|-------------------|--------------------|
| `microsoft_docs_search(query: "...")` | `mslearn search "..."` |
| `microsoft_code_sample_search(query: "...", language: "...")` | `mslearn code-search "..." --language ...` |
| `microsoft_docs_fetch(url: "...")` | `mslearn fetch "..."` |

生成的技能应包含此相同的 CLI 备用表格，以便代理可以使用任一路径。

## 创建过程

### 第 1 步：调查主题

使用 Learn MCP 工具分三个阶段构建深入理解：

**阶段 1 - 范围发现:**
```
microsoft_docs_search(query="{technology} overview what is")
microsoft_docs_search(query="{technology} concepts architecture")
microsoft_docs_search(query="{technology} getting started tutorial")
```

**阶段 2 - 核心内容:**
```
microsoft_docs_fetch(url="...")  # 从阶段 1 获取页面
microsoft_code_sample_search(query="{technology}", language="{lang}")
```

**阶段 3 - 深度:**
```
microsoft_docs_search(query="{technology} best practices")
microsoft_docs_search(query="{technology} troubleshooting errors")
```

#### 调查清单

调查后验证：
- [ ] 能用一句话解释该技术的作用
- [ ] 识别了 3-5 个关键概念
- [ ] 有基本用法的可运行代码
- [ ] 了解最常见的 API 模式
- [ ] 有用于深入主题的搜索查询

### 第 2 步：与用户澄清

展示发现并询问：
1. "我发现了这些关键领域：[列表]。哪些最重要？"
2. "代理将主要使用此技能执行哪些任务？"
3. "代码示例应优先使用哪种编程语言？"

### 第 3 步：生成技能

使用来自 [skill-templates.md](references/skill-templates.md) 的适当模板：

| 技术类型         | 模板         |
|-----------------|--------------|
| 客户端库、NuGet/npm 包 | SDK/库       |
| Azure 资源       | Azure 服务   |
| 应用开发框架     | 框架/平台   |
| REST API、协议   | API/协议     |

#### 生成的技能结构

```
{skill-name}/
├── SKILL.md                    # 核心知识 + Learn MCP 指导
├── references/                 # 需要时的详细本地文档
└── sample_codes/               # 可运行的代码示例
    ├── getting-started/
    └── common-patterns/
```

### 第 4 步：平衡本地与动态内容

**本地存储时:**
- 基础性 (任何任务都需要)
- 频繁访问
- 稳定性 (不会变化)
- 难以通过搜索找到

**保持动态时:**
- 全面参考 (太大)
- 版本特定
- 情境性 (仅特定任务)
- 易于索引 (易于搜索)

#### 内容指南

| 内容类型         | 本地         | 动态         |
|-----------------|--------------|--------------|
| 核心概念 (3-5)   | ✅ 完整     |              |
| Hello world 代码 | ✅ 完整     |              |
| 常见模式 (3-5)   | ✅ 完整     |              |
| 顶级 API 方法   | 签名 + 示例 | 通过 fetch 获取完整文档 |
| 最佳实践       | 5 个要点     | 搜索更多     |
| 故障排除       |              | 搜索查询     |
| 完整 API 参考   |              | 文档链接     |

### 第 5 步：验证

1. 审查：本地内容是否足以处理常见任务？
2. 测试：建议的搜索查询是否返回有用结果？
3. 验证：代码示例是否无错误运行？

## 常见调查模式

### 对于 SDK/库
```
"{name} overview" → 目的、架构
"{name} getting started quickstart" → 设置步骤
"{name} API reference" → 核心类/方法
"{name} samples examples" → 代码模式
"{name} best practices performance" → 优化
```

### 对于 Azure 服务
```
"{service} overview features" → 功能
"{service} quickstart {language}" → 设置代码
"{service} REST API reference" → 端点
"{service} SDK {language}" → 客户端库
"{service} pricing limits quotas" → 限制
```

### 对于框架/平台
```
"{framework} architecture concepts" → 概念模型
"{framework} project structure" → 规范
"{framework} tutorial walkthrough" → 端到端流程
"{framework} configuration options" → 定制
```

## 示例：创建 "Semantic Kernel" 技能

### 调查

```
microsoft_docs_search(query="semantic kernel overview")
microsoft_docs_search(query="semantic kernel plugins functions")
microsoft_code_sample_search(query="semantic kernel", language="csharp")
microsoft_docs_fetch(url="https://learn.microsoft.com/semantic-kernel/overview/")
```

### 生成的技能

```
semantic-kernel/
├── SKILL.md
└── sample_codes/
    ├── getting-started/
    │   └── hello-kernel.cs
    └── common-patterns/
        ├── chat-completion.cs
        └── function-calling.cs
```

### 生成的 SKILL.md

```markdown
---
name: semantic-kernel
description: 使用 Microsoft Semantic Kernel 构建 AI 代理。用于 .NET 或 Python 中的插件、规划和内存的 LLM 驱动应用。
---

# Semantic Kernel

用于将 LLM 集成到应用程序中的编排 SDK，支持插件、规划和内存。

## 关键概念

- **Kernel**: 管理 AI 服务和插件的中央协调器
- **Plugins**: AI 可以调用的函数集合
- **Planner**: 按顺序执行插件函数以实现目标
- **Memory**: 用于 RAG 模式的向量存储集成

## 快速入门

查看 [getting-started/hello-kernel.cs](sample_codes/getting-started/hello-kernel.cs)

## 了解更多

| 主题           | 如何查找           |
|----------------|--------------------|
| 插件开发       | `microsoft_docs_search(query="semantic kernel plugins custom functions")` |
| Planners       | `microsoft_docs_search(query="semantic kernel planner")` |
| Memory         | `microsoft_docs_fetch(url="https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-memory")` |

## CLI 替代方案

如果 Learn MCP 服务器不可用，请使用 `mslearn` CLI：

| MCP 工具           | CLI 命令           |
|-------------------|--------------------|
| `microsoft_docs_search(query: "...")` | `mslearn search "..."` |
| `microsoft_code_sample_search(query: "...", language: "...")` | `mslearn code-search "..." --language ...` |
| `microsoft_docs_fetch(url: "...")` | `mslearn fetch "..."` |

直接使用 `npx @microsoft/learn-cli <command>` 运行，或使用 `npm install -g @microsoft/learn-cli` 全局安装。
