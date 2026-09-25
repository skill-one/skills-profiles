# Aspire — 多语言分布式应用编排

Aspire 是一个 **以代码优先的多语言工具链**，用于构建可观测、适用于生产环境的分布式应用。它从单个 AppHost 项目中编排容器、可执行程序和云资源——无论工作负载是 C#、Python、JavaScript/TypeScript、Go、Java、Rust、Bun、Deno 还是 PowerShell。

> **心智模型**：AppHost 是一个 *指挥家* —— 它不演奏乐器，而是告诉每个服务何时启动、如何相互发现，并监控问题。

详细的参考材料位于 `references/` 文件夹中——按需加载。

---

## 参考

| 参考 | 加载时机 |
|---|---|
| [CLI 参考](references/cli-reference.md) | 命令标志、选项或详细用法 |
| [MCP 服务器](references/mcp-server.md) | 设置 AI 助手使用的 MCP、可用工具 |
| [集成目录](references/integrations-catalog.md) | 通过 MCP 工具发现集成、接线模式 |
| [多语言 API](references/polyglot-apis.md) | 方法签名、链式选项、特定语言的模式 |
| [架构](references/architecture.md) | DCP 内部结构、资源模型、服务发现、网络、遥测 |
| [仪表板](references/dashboard.md) | 仪表板功能、独立模式、GenAI 可视化器 |
| [部署](references/deployment.md) | Docker、Kubernetes、Azure 容器应用、App Service |
| [测试](references/testing.md) | 对 AppHost 的集成测试 |
| [故障排除](references/troubleshooting.md) | 诊断代码、常见错误和修复 |

---

## 1. 研究 Aspire 文档

Aspire 团队提供了一个 **MCP 服务器**，它直接在您的 AI 助手中提供文档工具。有关设置详情，请参阅 [MCP 服务器](references/mcp-server.md)。

### Aspire CLI 13.2+（推荐——内置文档搜索）

如果运行 Aspire CLI **13.2 或更高版本** (`aspire --version`)，MCP 服务器包含文档搜索工具：

| 工具 | 描述 |
|---|---|
| `list_docs` | 列出 aspire.dev 提供的所有可用文档 |
| `search_docs` | 在索引的文档中执行加权词法搜索 |
| `get_doc` | 通过其缩写获取特定文档 |

这些工具是在 [PR #14028](https://github.com/dotnet/aspire/pull/14028) 中添加的。要更新：`aspire update --self --channel daily`。

有关此方法的更多信息，请参阅 David Pine 的文章：https://davidpine.dev/posts/aspire-docs-mcp-tools/

### Aspire CLI 13.1（仅集成工具）

在 13.1 上，MCP 服务器提供集成查找，但**不**提供文档搜索：

| 工具 | 描述 |
|---|---|
| `list_integrations` | 列出可用的 Aspire 托管集成 |
| `get_integration_docs` | 获取特定集成包的文档 |

在 13.1 上进行一般文档查询时，请使用 **Context7** 作为主要来源（见下文）。

### 备用方案：Context7

当 Aspire MCP 文档工具不可用（13.1）或 MCP 服务器未运行时，请使用 **Context7** (`mcp_context7`)：

**步骤 1 — 解析库 ID**（会话内一次性）：

调用 `mcp_context7_resolve-library-id`，参数为 `libraryName: ".NET Aspire"`。

| 排名 | 库 ID | 使用时机 |
|---|---|---|
| 1 | `/microsoft/aspire.dev` | 主要来源。指南、集成、CLI 参考、部署。 |
| 2 | `/dotnet/aspire` | API 内部结构、源级实现细节。 |
| 3 | `/communitytoolkit/aspire` | 非微软多语言集成（Go、Java、Node.js、Ollama）。 |

**步骤 2 — 查询文档：**

```
libraryId: "/microsoft/aspire.dev", query: "Python 集成 AddPythonApp 服务发现"
libraryId: "/communitytoolkit/aspire", query: "Golang Java Node.js 社区集成"
```

### 备用方案：GitHub 搜索（当 Context7 也不可用时）

在 GitHub 上搜索官方文档仓库：
- **文档仓库**：`microsoft/aspire.dev` — 路径：`src/frontend/src/content/docs/`
- **源代码仓库**：`dotnet/aspire`
- **示例仓库**：`dotnet/aspire-samples`
- **社区集成**：`CommunityToolkit/Aspire`

---

## 2. 前置条件和安装

| 要求 | 详情 |
|---|---|
| **.NET SDK** | 10.0+（即使对于非 .NET 工作负载也必需——AppHost 是 .NET） |
| **容器运行时** | Docker Desktop、Podman 或 Rancher Desktop |
| **IDE（可选）** | VS Code + C# 开发套件、Visual Studio 2022、JetBrains Rider |

```bash
# Linux / macOS
curl -sSL https://aspire.dev/install.sh | bash

# Windows PowerShell
irm https://aspire.dev/install.ps1 | iex

# 验证
aspire --version

# 安装模板
dotnet new install Aspire.ProjectTemplates
```

---

## 3. 项目模板

| 模板 | 命令 | 描述 |
|---|---|---|
| **aspire-starter** | `aspire new aspire-starter` | ASP.NET Core/Blazor 启动器 + AppHost + 测试 |
| **aspire-ts-cs-starter** | `aspire new aspire-ts-cs-starter` | ASP.NET Core/React 启动器 + AppHost |
| **aspire-py-starter** | `aspire new aspire-py-starter` | FastAPI/React 启动器 + AppHost |
| **aspire-apphost-singlefile** | `aspire new aspire-apphost-singlefile` | 空单文件 AppHost |

---

## 4. AppHost 快速入门（多语言）

AppHost 编排所有服务。非 .NET 工作负载作为容器或可执行程序运行。

```csharp
var builder = DistributedApplication.CreateBuilder(args);

// 基础设施
var redis = builder.AddRedis("cache");
var postgres = builder.AddPostgres("pg").AddDatabase("catalog");

// .NET API
var api = builder.AddProject<Projects.CatalogApi>("api")
    .WithReference(postgres).WithReference(redis);

// Python ML 服务
var ml = builder.AddPythonApp("ml-service", "../ml-service", "main.py")
    .WithHttpEndpoint(targetPort: 8000).WithReference(redis);

// React 前端（Vite）
var web = builder.AddViteApp("web", "../frontend")
    .WithHttpEndpoint(targetPort: 5173).WithReference(api);

// Go 工作器
var worker = builder.AddGolangApp("worker", "../go-worker")
    .WithReference(redis);

builder.Build().Run();
```

有关完整的 API 签名，请参阅 [多语言 API](references/polyglot-apis.md)。

---

## 5. 核心概念（摘要）

| 概念 | 关键点 |
|---|---|
| **运行 vs 发布** | `aspire run` = 本地开发（DCP 引擎）。`aspire publish` = 生成部署清单。 |
| **服务发现** | 通过环境变量自动发现：`ConnectionStrings__<name>`，`services__<name>__http__0` |
| **资源生命周期** | DAG 排序——依赖项首先启动。`.WaitFor()` 在健康检查上阻塞。 |
| **资源类型** | `ProjectResource`，`ContainerResource`，`ExecutableResource`，`ParameterResource` |
| **集成** | 跨 13 个类别的 144+ 集成。托管包（AppHost）+ 客户端包（服务）。 |
| **仪表板** | 实时日志、跟踪、指标、GenAI 可视化器。与 `aspire run` 自动运行。 |
| **MCP 服务器** | AI 助手可通过 CLI（STDIO）查询运行中的应用并搜索文档。 |
| **测试** | `Aspire.Hosting.Testing` — 在 xUnit/MSTest/NUnit 中启动完整 AppHost。 |
| **部署** | Docker、Kubernetes、Azure 容器应用、Azure App Service。 |

---

## 6. CLI 快速参考

Aspire CLI 13.1 中的有效命令：

| 命令 | 描述 | 状态 |
|---|---|---|
| `aspire new <template>` | 从模板创建 | 稳定 |
| `aspire init` | 在现有项目中初始化 | 稳定 |
| `aspire run` | 本地启动所有资源 | 稳定 |
| `aspire add <integration>` | 添加集成 | 稳定 |
| `aspire publish` | 生成部署清单 | 预览 |
| `aspire config` | 管理配置设置 | 稳定 |
| `aspire cache` | 管理磁盘缓存 | 稳定 |
| `aspire deploy` | 部署到定义的目标 | 预览 |
| `aspire do <step>` | 执行管道步骤 | 预览 |
| `aspire update` | 更新集成（或 `--self` 用于 CLI） | 预览 |
| `aspire mcp init` | 为 AI 助手配置 MCP | 稳定 |
| `aspire mcp start` | 启动 MCP 服务器 | 稳定 |

完整命令参考（含标志）：[CLI 参考](references/cli-reference.md)。

---

## 7. 常见模式

### 添加新服务

1. 创建您的服务目录（任何语言）
2. 添加到 AppHost：`Add*App()` 或 `AddProject<T>()`
3. 接线依赖项：`.WithReference()`
4. 健康检查：如果需要，`.WaitFor()` 阻塞
5. 运行：`aspire run`

### 从 Docker Compose 迁移

1. `aspire new aspire-apphost-singlefile`（空 AppHost）
2. 用 Aspire 资源替换每个 `docker-compose` 服务
3. `depends_on` → `.WithReference()` + `.WaitFor()`
4. `ports` → `.WithHttpEndpoint()`
5. `environment` → `.WithEnvironment()` 或 `.WithReference()`

---

## 8. 关键 URL

| 资源 | URL |
|---|---|
| **文档** | https://aspire.dev |
| **运行时仓库** | https://github.com/dotnet/aspire |
| **文档仓库** | https://github.com/microsoft/aspire.dev |
| **示例** | https://github.com/dotnet/aspire-samples |
| **社区工具包** | https://github.com/CommunityToolkit/Aspire |
| **仪表板镜像** | `mcr.microsoft.com/dotnet/aspire-dashboard` |
| **Discord** | https://aka.ms/aspire/discord |
| **Reddit** | https://www.reddit.com/r/aspiredotdev/ |
