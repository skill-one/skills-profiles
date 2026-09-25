# ASP.NET Core 容器化提示

## 容器化请求

容器化下方设置中指定的 ASP.NET Core (.NET) 项目，专注于应用程序在 Linux Docker 容器中运行所需的**更改**。容器化应考虑此处指定的所有设置。

遵循容器化 .NET Core 应用的最佳实践，确保容器针对性能、安全性和可维护性进行了优化。

## 容器化设置

本提示部分包含容器化 ASP.NET Core 应用程序所需的特定设置和配置。在运行此提示之前，请确保用必要的信息填写了设置。请注意，在许多情况下，只需要填写前几个设置。如果它们不适用于要容器化的项目，则可以保留后续设置为默认值。

未指定的任何设置都将设置为默认值。默认值提供在 `[方括号]` 中。

### 基本项目信息
1. 要容器化的项目：
   - `[ProjectName (提供 .csproj 文件的路径)]`

2. 要使用的 .NET 版本：
   - `[8.0 或 9.0 (默认 8.0)]`

3. 要使用的 Linux 发行版：
   - `[debian, alpine, ubuntu, chiseled, 或 Azure Linux (mariner) (默认 debian)]`

4. Docker 图像构建阶段的自定义基础镜像（使用标准 Microsoft 基础镜像，请输入 "None"）：
   - `[指定用于构建阶段的基础镜像 (默认 None)]`

5. Docker 图像运行阶段的自定义基础镜像（使用标准 Microsoft 基础镜像，请输入 "None"）：
   - `[指定用于运行阶段的基础镜像 (默认 None)]`   

### 容器配置
1. 容器图像中必须暴露的端口：
   - 主要 HTTP 端口：`[例如，8080]`
   - 其他端口：`[列出任何其他端口，或 "None"]`

2. 容器应作为哪个用户帐户运行：
   - `[用户帐户，或默认为 "$APP_UID"]`

3. 应用程序 URL 配置：
   - `[指定 ASPNETCORE_URLS，或默认为 "http://+:8080"]`

### 构建配置
1. 构建容器图像之前必须执行的任何自定义构建步骤：
   - `[列出任何特定构建步骤，或 "None"]`

2. 构建容器图像之后必须执行的任何自定义构建步骤：
   - `[列出任何特定构建步骤，或 "None"]`

3. 必须配置的 NuGet 包源：
   - `[列出具有身份验证详细信息的私有 NuGet 源，或 "None"]`

### 依赖项
1. 容器图像中必须安装的系统包：
   - `[针对所选 Linux 发行版的包名称，或 "None"]`

2. 必须复制到容器图像的原生库：
   - `[库名称和路径，或 "None"]`

3. 必须安装的附加 .NET 工具：
   - `[工具名称和版本，或 "None"]`

### 系统配置
1. 容器图像中必须设置的任何环境变量：
   - `[变量名称和值，或 "使用默认值"]`

### 文件系统
1. 需要复制到容器图像的文件/目录：
   - `[相对于项目根目录的路径，或 "None"]`
   - 容器中的目标位置：`[容器路径，或 "不适用"]`

2. 要排除的文件/目录：
   - `[要排除的路径，或 "None"]`

3. 应配置的卷挂载点：
   - `[用于持久数据的卷路径，或 "None"]`

### .dockerignore 配置
1. 要包含在 `.dockerignore` 文件中的模式（.dockerignore 将已经具有常见默认值；这些是附加模式）：
   - 附加模式：`[列出任何附加模式，或 "None"]`

### 健康检查配置
1. 健康检查端点：
   - `[健康检查 URL 路径，或 "None"]`

2. 健康检查间隔和超时：
   - `[间隔和超时值，或 "使用默认值"]`

### 附加说明
1. 容器化项目必须遵循的其他说明：
   - `[特定要求，或 "None"]`

2. 已知问题：
   - `[描述任何已知问题，或 "None"]`

## 范围

- ✅ 应用程序配置修改，以确保应用程序设置和连接字符串可以从环境变量中读取
- ✅ 创建和配置 ASP.NET Core 应用的 Dockerfile
- ✅ 在 Dockerfile 中指定多个阶段以构建/发布应用程序并将输出复制到最终图像
- ✅ 配置 Linux 容器平台兼容性（Alpine、Ubuntu、Chiseled 或 Azure Linux (Mariner)）
- ✅ 正确处理依赖项（系统包、原生库、附加工具）
- ❌ 无基础设施设置（假设另行处理）
- ❌ 无代码更改，超出容器化所需范围

## 执行过程

1. 审查上述容器化设置，了解容器化要求
2. 创建 `progress.md` 文件以跟踪更改，使用复选标记
3. 通过检查 `.csproj` 文件中的 `TargetFramework` 元素来确定 .NET 版本
4. 根据以下条件选择适当的 Linux 容器图像：
   - 从项目中检测到的 .NET 版本
   - 容器化设置中指定的 Linux 发行版（Alpine、Ubuntu、Chiseled 或 Azure Linux (Mariner)）
   - 如果用户在容器化设置中未请求特定基础镜像，则基础镜像**必须**是有效的 mcr.microsoft.com/dotnet 图像，如示例 Dockerfile 中所示，或在文档中显示的标签
   - 官方 Microsoft .NET 图像用于构建和运行阶段：
      - SDK 图像标签（用于构建阶段）：https://github.com/dotnet/dotnet-docker/blob/main/README.sdk.md
      - ASP.NET Core 运行时图像标签：https://github.com/dotnet/dotnet-docker/blob/main/README.aspnet.md
      - .NET 运行时图像标签：https://github.com/dotnet/dotnet-docker/blob/main/README.runtime.md
5. 在项目目录根目录创建 Dockerfile 以容器化应用程序
   - Dockerfile 应使用多个阶段：
     - 构建阶段：使用 .NET SDK 图像构建应用程序
       - 首先复制 csproj 文件
       - 如果存在，则复制 NuGet.config 并配置任何私有源
       - 恢复 NuGet 包
       - 然后，复制其余的源代码并构建和发布应用程序到 /app/publish
     - 最终阶段：使用选定的 .NET 运行时图像运行应用程序
       - 将工作目录设置为 /app
       - 按照指示设置用户（默认情况下，为非根用户（例如，`$APP_UID`））
         - 除非在容器化设置中另有指示，否则不需要创建新用户。使用 `$APP_UID` 变量指定用户帐户。
       - 将构建阶段的发布输出复制到最终图像
   - 确保考虑容器化设置中的所有要求：
     - .NET 版本和 Linux 发行版
     - 暴露的端口
     - 容器用户帐户
     - ASPNETCORE_URLS 配置
     - 系统包安装
     - 原生库依赖项
     - 附加 .NET 工具
     - 环境变量
     - 文件/目录复制
     - 卷挂载点
     - 健康检查配置
6. 在项目目录根目录创建 `.dockerignore` 文件，以排除 Docker 图像中不必要的文件。`.dockerignore` 文件**必须**包含以下元素以及容器化设置中指定的附加模式：
   - bin/
   - obj/
   - .dockerignore
   - Dockerfile
   - .git/
   - .github/
   - .vs/
   - .vscode/
   - **/node_modules/
   - *.user
   - *.suo
   - **/.DS_Store
   - **/Thumbs.db
   - 容器化设置中指定的任何附加模式
7. 如果在容器化设置中指定了健康检查，请配置健康检查：
   - 如果提供了健康检查端点，请将 HEALTHCHECK 指令添加到 Dockerfile
   - 使用 curl 或 wget 检查健康端点
8. 将任务标记为已完成：[ ] → [✓]
9. 继续直到所有任务完成并且 Docker 构建成功

## 构建和运行时验证

完成 Dockerfile 后，确认 Docker 构建成功。使用以下命令构建 Docker 图像：

```bash
docker build -t aspnetcore-app:latest .
```

如果构建失败，请查看错误消息并对 Dockerfile 或项目配置进行必要的调整。报告成功/失败。

## 进度跟踪

维护一个 `progress.md` 文件，结构如下：

```markdown
# 容器化进度

## 环境检测
- [ ] .NET 版本检测（版本：___）
- [ ] Linux 发行版选择（发行版：___）

## 配置更改
- [ ] 应用程序配置验证以支持环境变量
- [ ] NuGet 包源配置（如果适用）

## 容器化
- [ ] Dockerfile 创建
- [ ] .dockerignore 文件创建
- [ ] 使用 SDK 图像创建构建阶段
- [ ] 复制 csproj 文件以进行包恢复
- [ ] 如果适用，复制 NuGet.config
- [ ] 使用运行时图像创建运行阶段
- [ ] 非根用户配置
- [ ] 依赖项处理（系统包、原生库、工具等）
- [ ] 健康检查配置（如果适用）
- [ ] 特殊要求实现

## 验证
- [ ] 审查容器化设置并确保满足所有要求
- [ ] Docker 构建成功
```

在步骤之间不要暂停确认。按部就班地继续，直到应用程序已容器化并且 Docker 构建成功。

**直到所有复选框都标记完成，您才算完成！** 这包括成功构建 Docker 图像并解决构建过程中出现的任何问题。

## 示例 Dockerfile

用于 ASP.NET Core (.NET) 应用程序并使用 Linux 基础镜像的示例 Dockerfile。

```dockerfile
# ============================================================
# 阶段 1：构建和发布应用程序
# ============================================================

# 基础镜像 - 选择适当的 .NET SDK 版本和 Linux 发行版
# 可能的标签包括：
# - 8.0-bookworm-slim (Debian 12)
# - 8.0-noble (Ubuntu 24.04)
# - 8.0-alpine (Alpine Linux)
# - 9.0-bookworm-slim (Debian 12)
# - 9.0-noble (Ubuntu 24.04)
# - 9.0-alpine (Alpine Linux)
# 使用 .NET SDK 图像构建应用程序
FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim AS build
ARG BUILD_CONFIGURATION=Release

WORKDIR /src

# 首先复制项目文件以更好地缓存
COPY ["YourProject/YourProject.csproj", "YourProject/"]
COPY ["YourOtherProject/YourOtherProject.csproj", "YourOtherProject/"]

# 如果存在，则复制 NuGet 配置
COPY ["NuGet.config", "."]

# 恢复 NuGet 包
RUN dotnet restore "YourProject/YourProject.csproj"

# 复制源代码
COPY . .

# 在这里执行任何自定义的预构建步骤，如果需要
# RUN echo "Running pre-build steps..."

# 构建并发布应用程序
WORKDIR "/src/YourProject"
RUN dotnet build "YourProject.csproj" -c $BUILD_CONFIGURATION -o /app/build

# 发布应用程序
RUN dotnet publish "YourProject.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

# 在这里执行任何自定义的 post-build 步骤，如果需要
# RUN echo "Running post-build steps..."

# ============================================================
# 阶段 2：最终运行时图像
# ============================================================

# 基础镜像 - 选择适当的 .NET 运行时版本和 Linux 发行版
# 可能的标签包括：
# - 8.0-bookworm-slim (Debian 12)
# - 8.0-noble (Ubuntu 24.04)
# - 8.0-alpine (Alpine Linux)
# - 8.0-noble-chiseled (Ubuntu 24.04 Chiseled)
# - 8.0-azurelinux3.0 (Azure Linux)
# - 9.0-bookworm-slim (Debian 12)
# - 9.0-noble (Ubuntu 24.04)
# - 9.0-alpine (Alpine Linux)
# - 9.0-noble-chiseled (Ubuntu 24.04 Chiseled)
# - 9.0-azurelinux3.0 (Azure Linux)
# 使用 .NET 运行时图像运行应用程序
FROM mcr.microsoft.com/dotnet/aspnet:8.0-bookworm-slim AS final

# 如果需要，安装系统包（取消注释并修改）
# RUN apt-get update && apt-get install -y \
#     curl \
#     wget \
#     ca-certificates \
#     libgdiplus \
#     && rm -rf /var/lib/apt/lists/*

# 如果需要，安装附加 .NET 工具（取消注释并修改）
# RUN dotnet tool install --global dotnet-ef --version 8.0.0
# ENV PATH="$PATH:/root/.dotnet/tools"

WORKDIR /app

# 从构建阶段复制发布的应用程序
COPY --from=build /app/publish .

# 如果需要，复制其他文件（取消注释并修改）
# COPY ./config/appsettings.Production.json .
# COPY ./certificates/ ./certificates/

# 设置环境变量
ENV ASPNETCORE_ENVIRONMENT=Production
ENV ASPNETCORE_URLS=http://+:8080

# 如果需要，添加自定义环境变量（取消注释并修改）
# ENV CONNECTIONSTRINGS__DEFAULTCONNECTION="your-connection-string"
# ENV FEATURE_FLAG_ENABLED=true

# 如果需要，配置 SSL/TLS 证书（取消注释并修改）
# ENV ASPNETCORE_Kestrel__Certificates__Default__Path=/app/certificates/app.pfx
# ENV ASPNETCORE_Kestrel__Certificates__Default__Password=your_password

# 暴露应用程序监听的端口
EXPOSE 8080
# EXPOSE 8081  # 如果使用 HTTPS，请取消注释

# 如果尚未存在，则安装 curl 以进行健康检查
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 配置健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 如果需要，创建用于持久数据的卷（取消注释并修改）
# VOLUME ["/app/data", "/app/logs"]

# 切换到非根用户以提高安全性
USER $APP_UID

# 设置应用程序的入口点
ENTRYPOINT ["dotnet", "YourProject.dll"]
```

## 适应此示例

**注意：** 根据容器化设置中的特定要求自定义此模板。

在适应此示例 Dockerfile 时：

1. 将 `YourProject.csproj`、`YourProject.dll` 等替换为您的实际项目名称
2. 根据需要调整 .NET 版本和 Linux 发行版
3. 根据您的需求修改依赖项安装步骤，并删除任何不必要的步骤
4. 配置特定于您的应用程序的环境变量
5. 根据您的特定工作流程添加或删除阶段
6. 更新健康检查端点以匹配您的应用程序的健康检查路由

## Linux 发行版变体

### Alpine Linux
对于更小的图像大小，您可以使用 Alpine Linux：

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
# ... 构建步骤 ...

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final
# 使用 apk 安装包
RUN apk update && apk add --no-cache curl ca-certificates
```

### Ubuntu Chiseled
对于最小的攻击面，请考虑使用 chiseled 图像：

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-jammy-chiseled AS final
# 注意：Chiseled 图像具有最少的包，因此您可能需要使用不同的基础镜像以安装额外的依赖项
```

### Azure Linux (Mariner)
对于 Azure 优化的容器：

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-azurelinux3.0 AS final
# 使用 tdnf 安装包
RUN tdnf update -y && tdnf install -y curl ca-certificates && tdnf clean all
```

## 阶段命名的说明

- `AS stage-name` 语法为每个阶段提供一个名称
- 使用 `--from=stage-name` 从先前的阶段复制文件
- 您可以有多个中间阶段，这些阶段在最终图像中不使用
- `final` 阶段是最终容器图像

## 安全最佳实践

- 始终以非根用户在生产环境中运行
- 使用特定图像标签而不是 `latest`
- 最小化安装的包数量
- 保持基础镜像更新
- 使用多阶段构建以将构建依赖项排除在最终图像之外
