# AppInsights 埋点指南

本技能为通过 Azure Application Insights 对 Web 应用进行埋点，提供**指导与参考材料**。

**⛔ 添加组件？**

如果用户希望**为其应用添加 App Insights**，请改用 **azure-prepare**。
本技能提供参考材料——azure-prepare 负责实际执行更改。

## 使用本技能的场景

- 用户询问**如何进行埋点**（指导、模式、示例）
- 用户需要 SDK 设置说明
- azure-prepare 在研究阶段调用本技能
- 用户希望了解 App Insights 相关概念

## 改用 azure-prepare 的场景

- 用户表示"在我的应用中添加遥测"
- 用户表示"添加 App Insights"
- 用户希望修改其项目
- 任何涉及更改或添加组件的请求

## 前置条件

工作区中的应用必须是以下类型之一：

- 托管在 Azure 中的 ASP.NET Core 应用
- 托管在 Azure 中的 Node.js 应用

## 指南

### 收集上下文信息

了解用户想要为应用添加遥测支持的程序语言、应用程序框架、托管方式的元组。这决定了应用可以进行埋点的具体方式。阅读源代码进行合理推测。对于不了解的内容，务必向用户确认。您必须始终询问用户应用所在的位置（例如：个人电脑、Azure App Service 代码、Azure App Service 容器、Azure Container App 等）。

### 优先使用自动埋点，如可能

如果应用是托管在 Azure App Service 中的 C# ASP.NET Core 应用，使用 [AUTO guide](references/auto.md) 帮助用户自动埋点该应用。

### 手动埋点

通过创建 AppInsights 资源并更新应用代码来手动埋点该应用。

#### 创建 AppInsights 资源

选择符合环境要求的一种方案。

- 将 AppInsights 添加到现有的 Bicep 模板。参见 [examples/appinsights.bicep](examples/appinsights.bicep) 了解需要添加的内容。如果工作区中存在现有 Bicep 模板文件，这是最佳选项。
- 使用 Azure CLI。参见 [scripts/appinsights.ps1](scripts/appinsights.ps1) 了解需要执行的 Azure CLI 命令，以创建 App Insights 资源。

无论选择哪种方案，都建议用户将 App Insights 资源创建在更有意义的资源组中，以便资源管理更便捷。一个良好的选择是与托管在 Azure 中的应用所包含资源的相同资源组。

#### 修改应用代码

- 如果应用是 ASP.NET Core 应用，参见 [ASPNETCORE guide](references/aspnetcore.md) 了解如何修改 C# 代码。
- 如果应用是 Node.js 应用，参见 [NODEJS guide](references/nodejs.md) 了解如何修改 JavaScript/TypeScript 代码。
- 如果应用是 Python 应用，参见 [PYTHON guide](references/python.md) 了解如何修改 Python 代码。

## SDK 快速参考

- **OpenTelemetry Distro**：[Python](references/sdk/azure-monitor-opentelemetry-py.md) | [TypeScript](references/sdk/azure-monitor-opentelemetry-ts.md)
- **OpenTelemetry Exporter**：[Python](references/sdk/azure-monitor-opentelemetry-exporter-py.md) | [Java](references/sdk/azure-monitor-opentelemetry-exporter-java.md)

## 平台特定指南

- **容器应用**：[可观测性指南](references/container-apps.md)
