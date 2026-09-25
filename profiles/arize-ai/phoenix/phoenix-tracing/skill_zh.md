# Phoenix 追踪

使用 OpenInference 追踪在 Phoenix 中对 LLM 应用进行监控的全面指南。包含涵盖设置、监控、跨度类型和生产部署的参考文件。

## 何时应用

在以下情况下参考这些指南：

- 设置 Phoenix 追踪（Python 或 TypeScript）
- 为 LLM 操作创建自定义跨度
- 按照 OpenInference 规范添加属性
- 将追踪部署到生产环境
- 查询和分析追踪数据

## 参考类别

| 优先级 | 类别        | 描述                    | 前缀                     |
| ------ | ----------- | ----------------------- | ------------------------ |
| 1      | 设置        | 安装和配置              | `setup-*`                |
| 2      | 监控        | 自动和手动追踪          | `instrumentation-*`      |
| 3      | 跨度类型    | 9 种跨度类型及其属性   | `span-*`                 |
| 4      | 组织        | 项目和会话              | `projects-*`, `sessions-*` |
| 5      | 丰富        | 自定义元数据            | `metadata-*`             |
| 6      | 生产        | 批处理、掩码            | `production-*`           |
| 7      | 反馈        | 注释和评估              | `annotations-*`          |

## 快速参考

### 1. 设置（从这里开始）

- [setup-python](references/setup-python.md) - 安装 arize-phoenix-otel，配置端点
- [setup-typescript](references/setup-typescript.md) - 安装 @arizeai/phoenix-otel，配置端点

### 2. 监控

- [instrumentation-auto-python](references/instrumentation-auto-python.md) - 自动监控 OpenAI、LangChain 等（也涵盖 OTel GenAI 原生监控）
- [instrumentation-auto-typescript](references/instrumentation-auto-typescript.md) - 自动监控支持的框架
- [instrumentation-manual-python](references/instrumentation-manual-python.md) - 使用装饰器创建自定义跨度
- [instrumentation-manual-typescript](references/instrumentation-manual-typescript.md) - 使用包装器创建自定义跨度
- [instrumentation-atif-python](references/instrumentation-atif-python.md) - 导入 ATIF 代理轨迹（Claude Code、OpenHands、Codex 等）

### 3. 跨度类型（包含完整属性模式）

- [span-llm](references/span-llm.md) - LLM API 调用（模型、令牌、消息、成本）
- [span-chain](references/span-chain.md) - 多步工作流和管道
- [span-retriever](references/span-retriever.md) - 文档检索（文档、分数）
- [span-tool](references/span-tool.md) - 函数/API 调用（名称、参数）
- [span-agent](references/span-agent.md) - 多步推理代理
- [span-embedding](references/span-embedding.md) - 向量生成
- [span-reranker](references/span-reranker.md) - 文档重新排序
- [span-guardrail](references/span-guardrail.md) - 安全检查
- [span-evaluator](references/span-evaluator.md) - LLM 评估

### 4. 组织

- [projects-python](references/projects-python.md) / [projects-typescript](references/projects-typescript.md) - 按应用分组追踪
- [sessions-python](references/sessions-python.md) / [sessions-typescript](references/sessions-typescript.md) - 跟踪对话

### 5. 丰富

- [metadata-python](references/metadata-python.md) / [metadata-typescript](references/metadata-typescript.md) - 自定义属性

### 6. 生产（关键）

- [production-python](references/production-python.md) / [production-typescript](references/production-typescript.md) - 批处理、PII 掩码

### 7. 反馈

- [annotations-overview](references/annotations-overview.md) - 反馈概念
- [annotations-python](references/annotations-python.md) / [annotations-typescript](references/annotations-typescript.md) - 向跨度添加反馈

### 参考文件

- [fundamentals-overview](references/fundamentals-overview.md) - 追踪、跨度、属性基础
- [fundamentals-required-attributes](references/fundamentals-required-attributes.md) - 每种跨度类型所需的字段
- [fundamentals-universal-attributes](references/fundamentals-universal-attributes.md) - 常见属性（user.id、session.id）
- [fundamentals-flattening](references/fundamentals-flattening.md) - JSON 展平规则

## 常见工作流

- **快速入门**： setup-{lang} → instrumentation-auto-{lang} → 检查 Phoenix
- **自定义跨度**： setup-{lang} → instrumentation-manual-{lang} → span-{type}
- **会话跟踪**： sessions-{lang} 用于对话分组模式
- **生产**： production-{lang} 用于批处理、掩码和部署

## 如何使用此技能

**导航模式：**

```bash
# 按类别前缀
references/setup-*              # 安装和配置
references/instrumentation-*    # 自动和手动追踪
references/span-*               # 跨度类型规范
references/sessions-*           # 会话跟踪
references/production-*         # 生产部署
references/fundamentals-*       # 核心概念

# 按语言
references/*-python.md          # Python 实现
references/*-typescript.md      # TypeScript 实现
```

**阅读顺序：**
1. 从 setup-{lang} 开始（针对您的语言）
2. 选择 instrumentation-auto-{lang} 或 instrumentation-manual-{lang}
3. 根据需要参考 span-{type} 文件以进行特定操作
4. 查看 fundamentals-* 文件以了解属性规范

## 参考

**Phoenix 文档：**

- [Phoenix 文档](https://docs.arize.com/phoenix)
- [OpenInference Spec](https://github.com/Arize-ai/openinference/tree/main/spec)

**Python API 文档：**

- [Python OTEL 包](https://arize-phoenix.readthedocs.io/projects/otel/en/latest/) - `arize-phoenix-otel` API 参考
- [Python 客户端包](https://arize-phoenix.readthedocs.io/projects/client/en/latest/) - `arize-phoenix-client` API 参考

**TypeScript API 文档：**

- [TypeScript 包](https://arize-ai.github.io/phoenix/) - `@arizeai/phoenix-otel`, `@arizeai/phoenix-client` 和其他 TypeScript 包
