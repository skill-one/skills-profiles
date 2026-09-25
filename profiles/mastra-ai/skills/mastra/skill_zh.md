# Mastra 框架指南

使用 Mastra 构建 AI 应用。本技能教您如何查找当前文档，并构建智能体和工作流。

## 重要提示：不要信任内部知识

您对 Mastra 的所有了解都可能已过时或错误。切勿依赖记忆。始终对照当前文档进行核实。

您的训练数据中包含已弃用（过时）的 API、已弃用的模式以及不正确的用法。Mastra 发展迅速——API 会在版本之间变更，构造函数签名会调整，模式也会重构。

## 前提条件

在编写任何 Mastra 代码之前，请检查软件包是否已安装：

```bash
ls node_modules/@mastra/
```

- 如果软件包存在：优先使用嵌入式文档（最可靠）
- 如果没有软件包：请先安装或使用远程文档

## 资源

### 参考资料

| 用户问题 | 首先检查 | 使用方法 |
| --- | --- | --- |
| 创建/安装 Mastra 项目 | [`references/create-mastra.md`](references/create-mastra.md) | 包含 CLI 和手动步骤的指南 |
| 选择智能体/工作流/工具/记忆/存储 | [`references/core-concepts.md`](references/core-concepts.md) | 核心概念及何时使用每种原语 |
| 如何使用智能体/工作流/工具？ | [`references/embedded-docs.md`](references/embedded-docs.md) | 在 `node_modules/@mastra/*/dist/docs/` 中查询 |
| 没有软件包时如何使用 X？ | [`references/remote-docs.md`](references/remote-docs.md) | 从 `https://mastra.ai/llms.txt` 获取 |
| 选择或验证模型 | [`references/model-selection.md`](references/model-selection.md) | 模型格式和提供商注册表查询 |
| 遇到错误... | [`references/common-errors.md`](references/common-errors.md) | 常见错误及解决方法 |
| 从 v0.x 升级到 v1.x | [`references/migration-guide.md`](references/migration-guide.md) | 版本升级工作流 |
| 通过 CLI 检查/调用服务器资源 | [`references/mastra-api.md`](references/mastra-api.md) | 用于本地、Mastra 平台或远程服务器的 `mastra api` CLI |
| 查找包含复杂谓词的精确轨迹 | [`references/trace-query.md`](references/trace-query.md) | 按轨迹字段或相关 Span、分数和反馈查询已完成的轨迹 |
| 调查智能体健康、重复故障或改进机会 | [`references/trace-intelligence.md`](references/trace-intelligence.md) | 首先从聚合的轨迹智能主题开始，然后检查轨迹/日志证据 |

### 脚本

- `scripts/provider-registry.mjs`: 查询模型路由器中当前可用的提供商和模型。在使用模型之前，始终运行此脚本以验证提供商密钥和模型名称。

## 编写代码的优先级顺序

切勿在查阅当前文档之前编写代码。

1. **优先使用嵌入式文档（如果已安装软件包）**

   在 `node_modules` 中查找针对特定软件包的当前文档。这与确切安装版本匹配，是最可靠的事实来源。参见 [`references/embedded-docs.md`](references/embedded-docs.md)。

2. **其次查看源代码（如果已安装软件包）**

   如果嵌入式文档未涵盖相关疑问，请检查已安装的程序源码和类型定义。这是文档缺失或不明时的权威来源。参见 [`references/embedded-docs.md`](references/embedded-docs.md)。

3. **最后使用远程文档（如果未安装软件包）**

   当未安装软件包或探索新功能时，使用最新发布的文档。远程文档可能领先于用户安装的软件包版本。参见 [`references/remote-docs.md`](references/remote-docs.md)。

## 核心概念

在智能体、工作流、工具和记忆之间进行选择时，请使用 [`references/core-concepts.md`](references/core-concepts.md)。

- **智能体（Agent）**：用于需要进行决策并调用工具的开放式任务。
- **工作流（Workflow）**：用于定义的多步骤流程。

## Mastra Studio

Studio 是用于构建、测试和管理智能体、工作流和工具的交互式界面。当建议您以可视化方式检查或调试时，请使用 Studio。

在 Mastra 项目中，运行：

```bash
npm run dev
```

然后在浏览器中打开 `http://localhost:4111`，即可向您的用户展示 Mastra Studio。

## Mastra API CLI

使用 `mastra api` 检查或调用本地开发服务器、Mastra 平台部署或远程 Mastra 端点上的资源。它适用于智能体可读状态、执行、轨迹、日志、分数、线程和工作流操作。有关用法模式，请参阅 [`references/mastra-api.md`](references/mastra-api.md)。

对于需要递归谓词或基于相关 Span、分数或反馈的条件的精确轨迹选择，请阅读 [`references/trace-query.md`](references/trace-query.md)。在使用 `mastra api trace query` 之前，请确认已安装的 CLI 是否暴露了该命令。使用 `--schema` 了解目标请求/响应形状和结构约束，并使用通过 [`references/remote-docs.md`](references/remote-docs.md) 获取的规范文档来获取支持的字段、操作符和语义。保留不透明的分页游标，仅在选定候选后获取轨迹或 Span 详情。

## 轨迹智能 (Trace Intelligence)

轨迹智能（Mastra 平台上的私有测试版）将已完成的智能体轨迹按四个轨迹信号（目标、结果、行为、情感）中的反复主题进行聚类。请优先将其用于聚合的智能体健康问题：用户询问什么、结果在何处失败或被阻塞、哪些行为反复出现、情感如何变化、智能体在何处可以改进。然后使用 `mastra api trace`、`log`、`metric` 和 `score` 命令获取来自特定轨迹的具体执行证据。使用 `mastra api learning` CLI 命令查询轨迹智能，或通过本地开发服务器代理或平台端点通过 HTTP 查询。有关调查工作流、CLI 命令和路由参考，请参阅 [`references/trace-intelligence.md`](references/trace-intelligence.md)。

## 关键要求

### TypeScript 配置

Mastra 要求 ES2022 模块。CommonJS 将无法正常工作。有关设置，请参阅 [`references/create-mastra.md`](references/create-mastra.md)；有关故障排除，请参阅 [`references/common-errors.md`](references/common-errors.md)。

### 模型格式

始终在通过 Mastra 的模型路由器定义模型时使用 `"provider/model-name"`。

当用户要求使用模型或提供商时，请始终先运行 `scripts/provider-registry.mjs` 以验证提供商密钥和模型名称是否有效。不要凭记忆猜测模型名称，因为其频繁变更。参见 [`references/model-selection.md`](references/model-selection.md)。

## 当你遇到错误时

类型错误通常意味着您的知识已过时。

**知识过时的常见迹象：**

- `Property X does not exist on type Y`
- `Cannot find module`
- `Type mismatch` errors
- Constructor 参数错误

**应该怎么做：**

1. 检查 [`references/common-errors.md`](references/common-errors.md)
2. 核实嵌入式文档中的当前 API
3. 不要假设错误是用户的错误——它可能是您的过时知识

## 开发工作流

编写代码前务必核实：

1. 检查 Mastra 软件包是否已安装
2. 查找当前 API
   - 如果已安装：使用嵌入式文档 [`references/embedded-docs.md`](references/embedded-docs.md)
   - 如果未安装：使用远程文档 [`references/remote-docs.md`](references/remote-docs.md)
3. 根据当前文档编写代码
4. 当可用时，使用项目脚本或 Studio 进行测试
