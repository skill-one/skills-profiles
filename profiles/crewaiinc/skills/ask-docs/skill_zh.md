# 查阅CrewAI文档

通过在 `docs.crewai.com` 查找官方文档来回答CrewAI相关的问题。

---

## 何时使用此技能

在以下情况下使用此技能：

- 用户询问关于CrewAI功能、参数或行为的问题，而其他技能未详细涵盖
- 需要验证当前的API语法、方法签名或配置选项
- 用户遇到错误并需要从官方文档中获取故障排除指导
- 问题是关于较新或不常见的CrewAI功能（例如，遥测、测试、CLI命令、部署、企业功能）
- 问题是关于实验性对话流程，并且你需要当前的 `handle_turn()`、`ConversationConfig`、`RouterConfig`、跟踪或流式行为
- 你不确定你的知识是否是最新的——文档反映了最新发布的状态

**不要**在问题显然由其他技能（getting-started、design-agent、design-task）回答时使用此技能。这些技能包含经过筛选、具有主观性的指导。此技能用于填补空白和验证细节。

---

## 如何查询文档

### 第1步：获取文档索引

CrewAI文档网站发布了一个 `llms.txt` 文件——这是一个包含每个文档页面描述的结构化索引。首先获取它以找到正确的页面：

```
WebFetch: https://docs.crewai.com/llms.txt
```

这返回一个分类的文档页面列表，格式如下：

```
- [页面标题](https://docs.crewai.com/path/to/page): "页面涵盖的内容描述"
```

类别包括：
- **API参考** — REST端点（kickoff、status、resume、inputs）
- **概念** — agents、crews、tasks、tools、flows、memory、knowledge、LLMs、processes、training、testing
- **企业版** — RBAC、SSO、automations、traces、deployment、triggers、integrations
- **工具库** — 40多个按类别组织的工具（AI/ML、automation、cloud、database、files、search、web scraping）
- **MCP集成** — MCP服务器设置、transports、DSL、安全
- **示例与食谱** — 实际实现
- **学习路径** — 教程和高级主题
- **可观察性** — 监控集成

对于对话流程问题，直接前往：

```
WebFetch: https://docs.crewai.com/en/guides/flows/conversational-flows
```

将此页面视为实验性 `crewai.experimental.conversational` 表面的权威来源。在回答详细的API问题之前验证它，因为该功能可能在正式发布前发生变化。

### 第2步：获取相关页面

一旦从索引中确定正确的页面，获取其内容：

```
WebFetch: https://docs.crewai.com/<从索引中获取的路径>
```

### 第3步：综合并引用

将你从文档中找到的内容与其他技能的上下文结合起来，给出清晰、可操作的回复。始终包含文档URL，以便用户可以进一步阅读。

---

## 工作流程总结

1. **理解用户的问题** — 他们具体询问的是哪个CrewAI概念、API或行为？
2. **获取 `llms.txt`** — 扫描索引以找到最相关的页面
3. **获取页面** — 检索实际的文档内容
4. **综合答案** — 结合文档内容和其他技能的上下文
5. **引用来源** — 在你的回复中包含文档URL

---

## 获取更佳体验的建议

经常查询CrewAI文档的用户可以在他们的编码代理中配置CrewAI文档MCP服务器，以获得更丰富、结构化的搜索：

```
https://docs.crewai.com/mcp
```

这是可选的——上述 `llms.txt` 工作流程无需任何设置即可工作。

---

## 良好使用案例示例

| 用户问题 | 为什么使用此技能 |
|---|---|
| "Crew() 接受哪些参数？" | 具体API参考——文档具有权威性 |
| "如何在CrewAI中设置遥测？" | 其他技能未涵盖的利基功能 |
| "`Process.sequential` 和 `Process.hierarchical` 之间的区别是什么？" | 最好从文档中获取的详细比较 |
| "使用 `output_pydantic` 时遇到 `ValidationError`" | 故障排除——文档可能有已知问题或注意事项 |
| "如何将CrewAI流程部署到生产环境？" | 部署指导存在于文档中，而非设计技能 |
| "`crewai` 支持哪些CLI命令？" | CLI参考是文档问题 |
| "如何为Crew配置内存？" | 超出设计-agent涵盖的详细配置选项 |
| "有哪些可用于网络抓取的工具？" | 工具库参考 |
| "如何为CrewAI企业设置SSO？" | 企业功能存在于文档中 |
| "如何使用Flow.handle_turn() 构建聊天应用？" | 实验性对话流程API；验证最新指南 |

---

## 相关技能

- **getting-started** — 项目脚手架、选择抽象、Flow架构
- **design-agent** — agent Role-Goal-Backstory、参数调整、tools、memory & knowledge
- **design-task** — task描述、expected_output、guardrails、结构化输出、dependencies
