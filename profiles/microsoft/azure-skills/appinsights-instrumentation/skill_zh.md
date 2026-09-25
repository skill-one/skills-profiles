# AppInsights 仪器指南

本技能提供使用 Azure Application Insights 仪器 Web 应用的**指导和支持材料**。

> **⛔ 添加组件？**
>
> 如果用户希望**将 App Insights 添加到他们的应用**，请调用 **azure-prepare**。
> 本技能提供支持材料 — azure-prepare 负责实际变更的编排。

## 使用此技能的场景

- 用户询问**如何**进行仪器（指导、模式、示例）
- 用户需要 SDK 安装说明
- azure-prepare 在研究阶段调用此技能
- 用户希望了解 App Insights 概念

## 应该使用 azure-prepare 的情况

- 用户说“将遥测数据添加到我的应用”
- 用户说“添加 App Insights”
- 用户希望修改他们的项目
- 任何要求更改/添加组件的请求

## 前提条件

工作区中的应用必须是以下类型之一

- 在 Azure 中托管的 ASP.NET Core 应用
- 在 Azure 中托管的 Node.js 应用

## 指南

### 收集上下文信息

确定用户正在尝试为其添加遥测支持的应用的（编程语言、应用程序框架、托管）三元组。这决定了应用程序如何进行仪器。通过阅读源代码进行有根据的猜测。对于任何不确定的信息，请与用户确认。您必须始终询问用户应用程序的托管位置（例如，在个人计算机上、作为代码在 Azure App Service 中、作为容器在 Azure App Service 中、在 Azure Container App 中等）。

### 尽可能使用自动仪器

如果应用是在 Azure App Service 中托管的 C# ASP.NET Core 应用，请使用 [AUTO 指南](references/auto.md) 帮助用户自动仪器应用。

### 手动仪器

通过创建 AppInsights 资源并更新应用的代码来手动仪器应用。

#### 创建 AppInsights 资源

使用以下选项之一，以适应环境。

- 将 AppInsights 添加到现有的 Bicep 模板。有关要添加的内容，请参阅 [examples/appinsights.bicep](examples/appinsights.bicep)。如果工作区中存在现有的 Bicep 模板文件，这是最佳选项。
- 使用 Azure CLI。有关执行 Azure CLI 命令以创建 App Insights 资源的说明，请参阅 [scripts/appinsights.ps1](scripts/appinsights.ps1)。

无论您选择哪种选项，都建议用户在具有意义且便于管理资源的资源组中创建 AppInsights 资源。一个很好的候选者是包含 Azure 中托管应用资源的资源组。

#### 修改应用代码

- 如果应用是 ASP.NET Core 应用，请参阅 [ASPNETCORE 指南](references/aspnetcore.md) 了解如何修改 C# 代码。
- 如果应用是 Node.js 应用，请参阅 [NODEJS 指南](references/nodejs.md) 了解如何修改 JavaScript/TypeScript 代码。
- 如果应用是 Python 应用，请参阅 [PYTHON 指南](references/python.md) 了解如何修改 Python 代码。

## SDK 快速参考

- **OpenTelemetry Distro**: [Python](references/sdk/azure-monitor-opentelemetry-py.md) | [TypeScript](references/sdk/azure-monitor-opentelemetry-ts.md)
- **OpenTelemetry Exporter**: [Python](references/sdk/azure-monitor-opentelemetry-exporter-py.md) | [Java](references/sdk/azure-monitor-opentelemetry-exporter-java.md)

## 平台特定指南

- **Container Apps**: [Observability Guide](references/container-apps.md)
