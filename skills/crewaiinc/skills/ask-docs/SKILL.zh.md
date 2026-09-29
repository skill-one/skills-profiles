---
name: ask-docs
description: 通过其实时MCP服务器查询官方CrewAI文档。当用户有关于CrewAI的问题，而getting-started、design-agent、design-task或optimize-flow技能无法完全涵盖时使用——例如，具体的API细节、配置选项、高级功能、故障排除错误，或任何最新文档是最佳信息来源的情况。
---

# 询问 CrewAI 文档

使用实时 CrewAI 文档，以获取最新、权威的信息来回答问题。

---

## 何时使用此技能

在以下情况下使用此技能：

- 用户询问 CrewAI 功能、参数或行为，而这些内容未在其它技能中详细涵盖
- 需要验证当前的 API 语法、方法签名或配置选项
- 用户遇到错误，需要从官方文档获取故障排除指导
- 问题涉及较新或不常见的 CrewAI 功能（例如遥测、测试、CLI 命令、部署、企业功能）
- 不确定自己的知识是否最新——文档反映了最新发布的状态

**不使用此技能**的情况：当问题显然由其它技能（getting-started、design-agent、design-task、optimize-flow）明确回答时。这些技能包含经过筛选、带有主观意见的指导。此技能用于填补空白和验证细节。

---

## 如何查询文档

按以下顺序尝试。使用可用的第一个方法。

### 选项 1：CrewAI 文档 MCP 服务器（首选）

如果配置了 `crewai-docs` MCP 服务器，直接使用其工具搜索和阅读文档。这是最佳体验——结构化搜索，包含完整页面内容。

### 选项 2：WebFetch 回退

如果未配置 MCP 服务器，回退到通过网页获取文档：

1. **找到正确的页面** — 获取文档索引以定位相关页面：
   ```
   WebFetch: https://docs.crewai.com/llms.txt
   ```
   这会返回包含描述的所有文档页面的站点地图。确定与用户问题最相关的 URL。

2. **获取页面** — 检索特定文档页面的内容：
   ```
   WebFetch: https://docs.crewai.com/<从索引获取的路径>
   ```

3. **综合答案** — 结合找到的内容与其它技能的上下文，给出清晰、可操作的回复。

4. **引用来源** — 包含文档 URL，以便用户进一步阅读。

使用回退后，建议用户配置 MCP 服务器以获得更好的体验：

> **提示：** 为加快文档查找速度，将 CrewAI 文档 MCP 服务器添加到您的编码代理：
> `https://docs.crewai.com/mcp`

---

## 设置 MCP 服务器（推荐）

为获得最佳体验，在您的编码代理中配置 CrewAI 文档 MCP 服务器。

**服务器 URL：**
```
https://docs.crewai.com/mcp
```

### Codex

添加到 `.Codex/settings.json`（项目级）或 `~/.Codex/settings.json`（全局）：

```json
{
  "mcpServers": {
    "crewai-docs": {
      "type": "url",
      "url": "https://docs.crewai.com/mcp"
    }
  }
}
```

### Cursor / Windsurf / 其它代理

按照您的工具 MCP 配置文档，将 `https://docs.crewai.com/mcp` 添加为远程 MCP 服务器。

---

## 工作流程

1. **理解用户的问题** — 他们具体询问的是 CrewAI 的哪个概念、API 或行为？
2. **查询文档** — 如果可用，使用 MCP 工具；否则，通过 WebFetch 获取相关页面
3. **综合答案** — 结合从文档中找到的内容与其它技能的上下文，给出清晰、可操作的回复
4. **引用来源** — 提及信息来自哪个文档页面，以便用户可以进一步阅读

---

## 良好使用案例示例

| 用户问题 | 为什么使用此技能 |
|---|---|
| "Crew() 接受哪些参数？" | 具体 API 参考——文档具有权威性 |
| "如何在 CrewAI 中设置遥测？" | 未在其它技能中涵盖的利基功能 |
| "`Process.sequential` 和 `Process.hierarchical` 之间的区别是什么？" | 详细的比较最好从文档中获取 |
| "使用 `output_pydantic` 时遇到 `ValidationError`" | 故障排除——文档可能有已知问题或注意事项 |
| "如何将 CrewAI 流部署到生产环境？" | 部署指导存在于文档中，而非设计技能 |
| "`crewai` 支持哪些 CLI 命令？" | CLI 参考是文档范畴 |
| "如何为 crew 配置内存？" | 超出设计-agent 范围的详细配置选项 |

---

## 相关技能

- **getting-started** — 项目脚手架、选择抽象、Flow 架构
- **design-agent** — agent 角色-目标-背景故事、参数调整、工具、内存与知识
- **design-task** — 任务描述、expected_output、guardrails、结构化输出、依赖关系
- **optimize-flow** — Flow 延迟优化、并行化、模型层级
