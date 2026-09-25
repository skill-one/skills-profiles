# Google Agents CLI 入门

> [!TIP] **一次性设置**：要安装 CLI 并启用您编码代理中的全部 7 项专业开发技能，请运行设置命令：
>
> ```bash
> uvx google-agents-cli setup
> ```
>
> 或者，仅安装专家技能并让代理处理执行：
>
> ```bash
> npx skills add google/agents-cli
> ```

## 概述

此技能作为 **agents-cli** 的入口点——它是 Google 用于在 Gemini 企业代理平台上构建、评估和部署 AI 代理的工具包。

使用此技能执行初始设置并识别适合您任务的正确专业工作流。

## 代理开发生命周期

运行设置后，以下专业技能将变为可用状态，并将根据您的请求自动激活。使用此表格来确定当前阶段应加载哪个技能：

| 阶段 | 专业技能 | 目的 / 加载时机 |
| :--- | :--- | :--- |
| **0 — 理解** | `google-agents-cli-workflow` | **明确意图。** 在编码前，在 `.agents-cli-spec.md` 中定义代理规范。 |
| **1 — 学习** | `google-agents-cli-workflow` | **利用示例。** 在搭建框架前，研究现有代理示例（例如，`ambient-expense`）。 |
| **2 — 搭建** | `google-agents-cli-scaffold` | **创建/增强。** 初始化项目结构、CI/CD 和基础设施模板。 |
| **3 — 构建** | `google-agents-cli-adk-code` | **实现。** 使用 ADK API 编写代理逻辑、工具、回调和管理状态。 |
| **4 — 评估** | `google-agents-cli-eval` | **验证质量。** 运行系统评估（LLM 作为裁判）。 |
| **5 — 部署** | `google-agents-cli-deploy` | **投入生产。** 部署到代理运行时（Vertex AI）、Cloud Run 或 GKE。 |
| **6 — 发布** | `google-agents-cli-publish` | **注册。** 将您的代理作为工具在 Gemini 企业中提供。 |
| **7 — 观察** | `google-agents-cli-observability` | **监控。** 设置 Cloud Trace、提示-响应日志记录和 BigQuery 分析。 |

## 主要 CLI 命令

以下是您在整个开发生命周期中将要使用的主要命令：

| 命令 | 描述 |
| :--- | :--- |
| `agents-cli setup` | 安装 CLI 并在您的编码代理中配置技能。 |
| `agents-cli scaffold <name>` | 从模板创建新的代理项目。 |
| `agents-cli eval run` | 单步运行代理并评分跟踪（生成 + 评分）。 |
| `agents-cli deploy` | 将您的代理部署到 Google Cloud（代理运行时、Cloud Run、GKE）。 |
| `agents-cli publish gemini-enterprise` | 将已部署的代理注册到 Gemini 企业。 |

*要获取所有可用命令和全局选项的完整列表，请运行 `agents-cli --help`。*

## 下一步

按照以下顺序启动开发工作流：

1.  **执行设置**：在上方 `[!TIP]` 盒中运行 `uvx` 或 `npx` 命令来安装 CLI 并在您的环境中启用专业技能。
2.  **验证安装**：运行 `agents-cli info` 以确认安装并查看活动的项目配置。
3.  **启动阶段 0**：向用户询问其核心需求（代理目的、外部工具、部署目标），并在编写任何代码之前将它们记录在 `.agents-cli-spec.md` 中。

## 报告问题

在 [Google Agents CLI Issues](https://github.com/google/agents-cli/issues) 中报告错误或改进。

## 支持链接

*   [Google Agents CLI 文档](https://github.com/google/agents-cli/tree/main/docs/src)
