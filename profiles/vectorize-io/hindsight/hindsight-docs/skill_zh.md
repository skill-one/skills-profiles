# Hindsight 文档编写技巧

Hindsight 技术文档完整指南 - 一种用于 AI 代理的仿生记忆系统。

## 何时使用此技巧

当你需要以下功能时，请使用此技巧：
- 理解 Hindsight 架构和核心概念
- 学习关于 retain/recall/reflect 操作
- 配置记忆库和 disposition
- 设置 Hindsight API 服务器（Docker、Kubernetes、pip）
- 集成 Python/Node.js/Rust SDK
- 理解检索策略（语义、BM25、图、时间）
- 调试问题或优化性能
- 查看 API 端点和参数

## 文档结构

所有文档都按类别组织在 `references/` 目录下：

```
references/
├── best-practices.md # 从这里开始 — 任务、标签、格式、反模式
├── faq.md            # 常见问题和决策
├── changelog/        # 版本历史和变更记录（index.md + integrations/）
├── openapi.json      # 完整的 OpenAPI 规范 — 端点模式、请求/响应模型
├── developer/
│   ├── api/          # 核心操作：retain、recall、reflect、记忆库
│   └── *.md          # 架构、配置、部署、性能
└── sdks/
    ├── *.md          # Python、Node.js、CLI、嵌入式
    └── integrations/ # 框架和工具集成
```

## 如何查找文档

### 1. 通过模式查找文件（使用 Glob 工具）

```bash
# 核心 API 操作
references/developer/api/*.md

# SDK 文档
references/sdks/*.md
references/sdks/integrations/*.md

# 查找特定主题
references/**/configuration.md
references/**/*python*.md
references/**/*deployment*.md
```

### 2. 搜索内容（使用 Grep 工具）

```bash
# 搜索概念
pattern: "disposition"        # 记忆库配置
pattern: "graph retrieval"    # 基于图的搜索
pattern: "helm install"       # Kubernetes 部署
pattern: "document_id"        # 文档管理
pattern: "HINDSIGHT_API_"     # 环境变量

# 在特定区域搜索
path: references/developer/api/
pattern: "POST /v1"           # 查找 API 端点

path: references/sdks/
pattern: "def |async def "    # 查找 Python 示例
```

### 3. 阅读完整文档（使用 Read 工具）

```
references/developer/api/retain.md
references/sdks/python.md
references/sdks/integrations/litellm.md
```

## 从这里开始：最佳实践

在阅读 API 文档之前，请先阅读最佳实践指南。它涵盖了任务、标签、内容格式、观察范围和反模式的实用规则 — 最快正确集成的途径。

```
references/best-practices.md
```

## 核心概念

- **记忆库**：隔离的记忆存储（每个用户/代理一个）
- **retain**：存储记忆（自动提取事实、实体、关系）
- **recall**：检索记忆（4 种并行策略：语义、BM25、图、时间）
- **reflect**：使用记忆进行 disposition 感知的推理
- **document_id**：将对话中的消息分组（相同 ID 的 upsert）
- **disposition**：怀疑论、字面主义、同理心特质（1-5）影响 reflect
- **Mental Models**：从事实中综合而成的知识模型

## 注意事项

- 代码示例来自可运行的示例
- 配置使用 `HINDSIGHT_API_*` 环境变量
- 数据库迁移在启动时自动运行
- 多库查询需要客户端端协调
- 使用 `document_id` 进行对话演进（相同 ID = upsert）

---

**自动生成**自 `hindsight-docs/docs/` 和 `hindsight-docs/docs-integrations/`。运行 `./scripts/generate-docs-skill.sh` 更新。
