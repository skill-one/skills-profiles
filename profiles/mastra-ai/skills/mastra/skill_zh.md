# Mastra 框架指南

使用 Mastra 构建人工智能应用。本技能将教您如何查找当前文档并构建代理和工作流。

## 重要提示：不要信任内部知识

您所知道的关于 Mastra 的所有内容很可能已经过时或错误。切勿依赖记忆。始终对照当前文档进行验证。

您的训练数据包含过时的 API、已弃用的模式和错误的使用方式。Mastra 发展迅速 - API 在版本之间会发生变化，构造函数签名会改变，模式会被重构。

## 前置条件

在编写任何 Mastra 代码之前，请检查是否已安装包：

```bash
ls node_modules/@mastra/
```

- 如果包存在：首先使用嵌入式文档（最可靠）
- 如果没有包：先安装或使用远程文档

## 资源

### 参考

| 用户问题                       | 首次检查                                                      | 如何操作                                         |
| ------------------------------ | ---------------------------------------------------------------- | ---------------------------------------------- |
| 创建/安装 Mastra 项目         | [`references/create-mastra.md`](references/create-mastra.md)     | 带有 CLI 和手动步骤的设置指南                  |
| 选择代理/工作流/工具/内存/存储 | [`references/core-concepts.md`](references/core-concepts.md) | 核心概念以及何时使用每个原始数据类型            |
| 如何使用代理/工作流/工具？     | [`references/embedded-docs.md`](references/embedded-docs.md)     | 在 `node_modules/@mastra/*/dist/docs/` 中查找 |
| 如何使用 X？（没有包）       | [`references/remote-docs.md`](references/remote-docs.md)         | 从 `https://mastra.ai/llms.txt` 获取            |
| 选择或验证模型                | [`references/model-selection.md`](references/model-selection.md) | 模型格式和提供者注册表查找                      |
| 我遇到了错误...               | [`references/common-errors.md`](references/common-errors.md)     | 常见错误和解决方案                                |
| 从 v0.x 升级到 v1.x           | [`references/migration-guide.md`](references/migration-guide.md) | 版本升级工作流                                  |
| 通过 CLI 检查/调用服务器资源 | [`references/mastra-api.md`](references/mastra-api.md)       | `mastra api` CLI 用于本地、Mastra 平台或远程服务器 |
| 查找具有复杂谓词的确切跟踪     | [`references/trace-query.md`](references/trace-query.md) | 通过跟踪字段或相关跨度、分数和反馈查询完成的跟踪 |
| 调查代理健康、重复失败或改进机会 | [`references/trace-intelligence.md`](references/trace-intelligence.md) | 从聚合跟踪智能主题开始，然后检查跟踪/日志证据 |

### 脚本

- `scripts/provider-registry.mjs`：查找当前提供者和模型路由器中可用的模型。在使用模型之前始终运行此脚本以验证提供者密钥和模型名称。

## 编写代码的优先级顺序

在编写代码之前，请始终先检查当前文档。

1. 首先使用嵌入式文档（如果已安装包）

   在 `node_modules` 中查找当前包的文档。这匹配已安装的确切版本，并且是最可靠的真相来源。参见 [`references/embedded-docs.md`](references/embedded-docs.md)。

2. 源代码第二（如果已安装包）

   如果嵌入式文档没有涵盖问题，请检查已安装的源和类型定义。当文档缺失或不明确时，这是真相来源。参见 [`references/embedded-docs.md`](references/embedded-docs.md)。

3. 第三使用远程文档（如果未安装包）

   当未安装包或探索新功能时，使用最新发布的文档。远程文档可能领先于用户的已安装版本。参见 [`references/remote-docs.md`](references/remote-docs.md)。

## 核心概念

在您选择代理、工作流、工具、内存和存储时，请使用 [`references/core-concepts.md`](references/core-concepts.md)。

- 代理：用于开放式任务，这些任务会做决策并使用工具。
- 工作流：用于定义的多步骤流程。

## Mastra Studio

Studio 是用于构建、测试和管理代理、工作流和工具的交互式 UI。当您建议人类用户进行视觉检查或调试时，请使用 Studio。

在 Mastra 项目中，运行：

```bash
npm run dev
```

然后在浏览器中打开 `http://localhost:4111` 以向您的用户展示 Mastra Studio。

## Mastra API CLI

使用 `mastra api` 来检查或调用本地开发服务器、Mastra 平台部署或远程 Mastra 端点的资源。它对于代理可读状态、执行、跟踪、日志、分数、线程和工作流操作很有用。参见 [`references/mastra-api.md`](references/mastra-api.md) 了解使用模式。

对于需要递归谓词或相关跨度、分数或反馈的条件的确切跟踪选择，请阅读 [`references/trace-query.md`](references/trace-query.md)。在使用 `mastra api trace query` 之前，请确认已安装的 CLI 暴露该命令。使用 `--schema` 为目标请求/响应形状和结构约束，并使用通过 [`references/remote-docs.md`](references/remote-docs.md) 找到的规范文档来查找支持的字段、运算符和语义。保留不透明的分页游标，并在选择候选者后获取跟踪或跨度详细信息。

## Mastra Factory

对于 Factory 项目，工作项、队列健康、决策、会话历史记录、内存检查或授权操作，请激活 **`mastra-factory`** 技能。Factory 是一个操作控制平面，而不是搭建或部署新 Mastra 应用的原因。

如果技能缺失，请从此存储库中提议安装它：

```bash
npx skills add mastra-ai/skills --skill mastra-factory
```

交互式选择用户的预期代理和范围。对于全局安装，请明确指定支持代理 `--agent <agent> -g`；PromptScript 不支持全局安装。即使另一个代理目标失败，也要验证预期代理的安装和引用文件。

Factory 技能涵盖 CLI 检查、`mastra auth whoami` / 授权的 `mastra auth login`，以及从任何目录通过用户的实际实例 URL 连接。不需要部署的存储库或 `.mastra-project.json`（使用 `--url`）。切勿猜测共享的 Factory 主机或项目 ID。其连接和会话检查参考涵盖部署特定的身份验证、项目发现、线程和观察内存限制。

## 跟踪智能

跟踪智能（Mastra 平台上的私人测试版）将完成的代理跟踪聚类为四个跟踪信号（目标、结果、行为和情感）中的反复主题。首先用于聚合代理健康问题：用户请求的内容、结果失败或被阻塞的位置、反复出现的行为、情感变化以及代理可以改进的地方。然后使用 `mastra api trace`、`log`、`metric` 和 `score` 命令获取来自特定跟踪的具体执行证据。使用 `mastra api learning` CLI 命令或通过本地开发服务器代理或平台端点通过 HTTP 查询跟踪智能。参见 [`references/trace-intelligence.md`](references/trace-intelligence.md) 了解调查工作流、CLI 命令和路由参考。

## 关键要求

### TypeScript 配置

Mastra 需要 ES2022 模块。CommonJS 会失败。参见 [`references/create-mastra.md`](references/create-mastra.md) 了解设置和 [`references/common-errors.md`](references/common-errors.md) 了解故障排除。

### 模型格式

在使用 Mastra 的模型路由器定义模型时，始终使用 `"provider/model-name"`。

当用户要求使用模型或提供者时，始终先运行 `scripts/provider-registry.mjs` 以验证提供者密钥和模型名称是否有效。不要从记忆中猜测模型名称，因为它们经常变化。参见 [`references/model-selection.md`](references/model-selection.md)。

## 当您看到错误时

类型错误通常意味着您的知识已经过时。

过时知识的常见迹象：

- `属性 X 不存在于类型 Y`
- `找不到模块`
- `类型不匹配` 错误
- 构造函数参数错误

要做什么：

1. 查看 [`references/common-errors.md`](references/common-errors.md)
2. 在嵌入式文档中验证当前 API
3. 不要假设错误是用户错误 - 它可能是您过时的知识

## 开发工作流

在编写代码之前始终验证：

1. 检查 Mastra 包是否已安装
2. 查找当前 API
   - 如果已安装：使用嵌入式文档 [`references/embedded-docs.md`](references/embedded-docs.md)
   - 如果未安装：使用远程文档 [`references/remote-docs.md`](references/remote-docs.md)
3. 根据当前文档编写代码
4. 当可用时，使用项目脚本或 Studio 进行测试
