# AppInsights 仪器化

这项技能能够将 Web 应用的遥测数据发送到 Azure App Insights，以便更好地观察应用的健康状况。

## 使用此技能的场景

当用户希望为其 Web 应用启用遥测功能时，使用此技能。

## 前提条件

工作区中的应用必须是以下类型之一

- Azure 中托管的 ASP.NET Core 应用
- Azure 中托管的 Node.js 应用

## 指南

### 收集上下文信息

找出用户正在尝试为其添加遥测支持的应用的（编程语言、应用程序框架、托管）三元组。这决定了应用如何进行仪器化。通过阅读源代码进行有根据的猜测。对于任何不确定的信息，必须与用户确认。您必须始终询问用户应用的托管位置（例如：在个人计算机上、作为代码在 Azure App Service 中、作为容器在 Azure App Service 中、在 Azure Container App 中等）。

### 尽可能使用自动仪器化

如果应用是 Azure App Service 中托管的 C# ASP.NET Core 应用，请使用 [AUTO 指南](references/AUTO.md) 帮助用户自动仪器化应用。

### 手动仪器化

通过创建 AppInsights 资源并更新应用的代码来手动仪器化应用。

#### 创建 AppInsights 资源

使用以下选项中适合环境的选项。

- 将 AppInsights 添加到现有的 Bicep 模板。有关要添加的内容，请参阅 [examples/appinsights.bicep](examples/appinsights.bicep)。如果工作区中存在现有的 Bicep 模板文件，这是最佳选项。
- 使用 Azure CLI。有关执行创建 App Insights 资源 Azure CLI 命令的内容，请参阅 [scripts/appinsights.ps1](scripts/appinsights.ps1)。

无论您选择哪个选项，都建议用户在具有意义且便于管理资源的资源组中创建 AppInsights 资源。一个很好的候选者是包含 Azure 中托管应用资源的资源组。

#### 修改应用代码

- 如果应用是 ASP.NET Core 应用，请参阅 [ASPNETCORE 指南](references/ASPNETCORE.md) 了解如何修改 C# 代码。
- 如果应用是 Node.js 应用，请参阅 [NODEJS 指南](references/NODEJS.md) 了解如何修改 JavaScript/TypeScript 代码。
- 如果应用是 Python 应用，请参阅 [PYTHON 指南](references/PYTHON.md) 了解如何修改 Python 代码。
