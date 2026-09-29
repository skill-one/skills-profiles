---
name: appinsights-instrumentation
description: 使用 Azure Application Insights 为 Web 应用添加监控的指南。提供遥测模式、SDK 设置和配置参考。何时：如何为应用添加监控、App Insights SDK、遥测模式、App Insights 是什么、Application Insights 指南、监控示例、APM 最佳实践。
---

# AppInsights 仪器指南

本技能为使用 Azure Application Insights 仪器 Web 应用提供**指导和支持材料**。

> **⛔ 添加组件？**
>
> 如果用户希望**将 App Insights 添加到他们的应用**，请调用 **azure-prepare**。
> 本技能提供支持材料 — azure-prepare 执行实际变更。

## 使用此技能的场景

- 用户询问**如何**仪器（指导、模式、示例）
- 用户需要 SDK 安装说明
- azure-prepare 在研究阶段调用此技能
- 用户希望了解 App Insights 概念

## 应该使用 azure-prepare 的情况

- 用户说“向我的应用添加遥测”
- 用户说“添加 App Insights”
- 用户希望修改他们的项目
- 任何要求更改/添加组件的请求

## 前提条件

工作区中的应用必须是以下类型之一

- 在 Azure 中托管的 ASP.NET Core 应用
- 在 Azure 中托管的 Node.js 应用

## 指南

### 收集上下文信息

确定用户正在尝试为其添加遥测支持的应用的（编程语言、应用程序框架、托管）三元组。这决定了应用如何被仪器。阅读源代码进行有根据的猜测。对于任何不确定的信息，请与用户确认。您必须始终询问用户应用托管的位置（例如，在个人计算机上、作为代码在 Azure App Service 中、作为容器在 Azure App Service 中、在 Azure Container App 中等）。

### 尽可能使用自动仪器

如果应用是在 Azure App Service 中托管的 C# ASP.NET Core 应用，请使用 [AUTO 指南](references/auto.md) 帮助用户自动仪器应用。

### 手动仪器

通过创建 AppInsights 资源并更新应用的代码来手动仪器应用。

#### 创建 AppInsights 资源

使用以下选项之一，以适应环境。

- 向现有的 Bicep 模板添加 AppInsights。有关要添加的内容，请参阅 [examples/appinsights.bicep](examples/appinsights.bicep)。如果工作区中存在现有的 Bicep 模板文件，这是最佳选项。
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
