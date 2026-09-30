---
name: docker
description: 为 .NET 10 应用程序提供 Docker 容器化支持。涵盖多阶段构建、.NET 容器镜像、非根用户配置、健康检查以及 .dockerignore。在以下场景加载此技能：使用 Dockerfile 容器化应用程序、优化镜像大小、为本地开发设置 Docker Compose，或当用户提及“Docker”、“Dockerfile”、“容器”、“docker-compose”、“镜像”、“多阶段”、“非根”、“.dockerignore”或“容器健康检查”时。对于无需 Dockerfile 的 SDK 发布（`dotnet publish /t:PublishContainer`），请加载“容器发布”技能。
---

# Docker

## 核心原则

1. **始终使用多阶段构建** — 分离构建和运行阶段。在 SDK 镜像中构建，在 ASP.NET 运行时镜像中运行。
2. **默认非 root 用户** — 自 .NET 8 起，.NET 容器镜像默认支持 `USER app`。生产环境中切勿以 root 用户运行。
3. **层缓存很重要** — 在复制源代码前，先复制 `.csproj` 文件并执行还原。这能在多次构建中缓存 NuGet 依赖。
4. **在编排器级别设置健康探针** — 暴露 `/health/live` 端点，让 Kubernetes/Compose 探测它。Chiseled 和默认的 aspnet 镜像没有 shell 或 curl，因此镜像内的 `HEALTHCHECK` 命令无法执行任何操作。

## 模式

### Web API 的多阶段 Dockerfile

```dockerfile
# 阶段 1：构建
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# 复制项目文件并还原（利用缓存层）
COPY ["src/MyApp.Api/MyApp.Api.csproj", "src/MyApp.Api/"]
COPY ["src/MyApp.Domain/MyApp.Domain.csproj", "src/MyApp.Domain/"]
COPY ["Directory.Build.props", "."]
COPY ["Directory.Packages.props", "."]
RUN dotnet restore "src/MyApp.Api/MyApp.Api.csproj"

# 复制所有文件并构建
COPY . .
RUN dotnet publish "src/MyApp.Api/MyApp.Api.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore

# 阶段 2：运行时
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app

# 非 root 用户（.NET 8+ 镜像默认设置）
USER app

COPY --from=build /app/publish .

EXPOSE 8080

ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```

### 容器健康探针

优先使用编排器级别的探针（Kubernetes `livenessProbe`、Compose `healthcheck`）而非 Dockerfile 中的 `HEALTHCHECK` — 标准 `aspnet` 和 chiseled 镜像不包含 shell、curl 或 wget，容器内无任何可执行探针的工具。让编排器指向 `/health/live`：

```yaml
# docker-compose — 从应用进程外部探测
services:
  api:
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/health/live || exit 1"]
      interval: 30s
      timeout: 3s
      retries: 3
# 注意：CMD-SHELL 需要镜像中包含 shell + wget。使用非 chiseled 版本，或更好的：让 Kubernetes httpGet 探针处理 — 它们从 kubelet 运行，无需镜像内资源。
```

如果必须使用镜像内 `HEALTHCHECK`，基于包含 `wget` 的非 chiseled 镜像构建运行时阶段 — 切勿以应用二进制文件重新运行探针命令；那样会启动第二个实例而非检查第一个。

### .dockerignore

```
**/.git
**/.vs
**/bin
**/obj
**/node_modules
**/Dockerfile*
**/docker-compose*
**/tests
```

### Docker Compose 用于本地开发

关键 .NET 特定注意事项 — 通过环境变量传递连接字符串，使用 `depends_on` 配合健康检查：

```yaml
services:
  api:
    build:
      context: .
      dockerfile: src/MyApp.Api/Dockerfile
    ports:
      - "5000:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Host=postgres;Database=myapp;Username=postgres;Password=postgres
      - ConnectionStrings__Redis=redis:6379
    depends_on:
      postgres:
        condition: service_healthy
  # 添加 postgres/redis 服务并设置 healthcheck — 标准模板
```

### 使用 .slnx 优化构建

对于多项目解决方案，仅还原必要项目。

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# 复制解决方案和所有项目文件
COPY *.slnx .
COPY Directory.Build.props .
COPY Directory.Packages.props .
COPY src/**/*.csproj ./src/

# 还原项目结构
RUN for file in src/**/*.csproj; do \
    mkdir -p $(dirname $file) && mv $file $(dirname $file)/; \
    done
RUN dotnet restore

COPY . .
RUN dotnet publish src/MyApp.Api -c Release -o /app/publish --no-restore
```

### 健康检查端点

```csharp
// 在 Program.cs 中 — Docker 用的轻量级健康端点
app.MapGet("/health/live", () => Results.Ok("healthy"))
    .ExcludeFromDescription();
```

## 反模式

### 不要使用 SDK 镜像运行时

```dockerfile
# BAD — SDK 镜像体积 900MB+，包含编译器
FROM mcr.microsoft.com/dotnet/sdk:10.0
COPY . .
RUN dotnet run

# GOOD — 分离构建和运行时，运行时镜像体积约 200MB
FROM mcr.microsoft.com/dotnet/aspnet:10.0
```

### 还原前不要复制所有文件

```dockerfile
# BAD — 任何源代码变更都会使 NuGet 缓存失效
COPY . .
RUN dotnet restore

# GOOD — 先复制项目文件，再还原
COPY ["src/MyApp.Api/MyApp.Api.csproj", "src/MyApp.Api/"]
RUN dotnet restore "src/MyApp.Api/MyApp.Api.csproj"
COPY . .
```

### 不要以 root 用户运行

```dockerfile
# BAD — 以 root 用户运行（安全风险）
FROM mcr.microsoft.com/dotnet/aspnet:10.0
COPY --from=build /app .
ENTRYPOINT ["dotnet", "MyApp.Api.dll"]

# GOOD — 使用内置的非 root 用户
FROM mcr.microsoft.com/dotnet/aspnet:10.0
USER app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```

## 决策指南

| 场景 | 建议 |
|------|------|
| Web API 容器 | 使用 aspnet 运行时镜像的多阶段构建 |
| 工作服务 | 使用 dotnet/runtime 镜像的多阶段构建 |
| 本地开发 | 使用 Docker Compose 配合服务依赖 |
| CI 构建 | 多阶段构建（自包含） |
| 镜像体积优化 | 使用 Alpine 版本 + 剪枝生成小镜像 |
| 健康监控 | `/health` 端点 + 编排器探针（K8s `httpGet` / Compose healthcheck） |
| 密钥 | 环境变量或挂载密钥，绝不在镜像内 |
