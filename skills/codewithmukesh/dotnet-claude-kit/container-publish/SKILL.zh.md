---
name: container-publish
description: 使用 .NET 10 SDK 容器发布功能实现无需 Dockerfile 的容器化。涵盖 MSBuild 属性、精简镜像、多架构构建和注册表发布——所有这些都不需要编写 Dockerfile。当用户希望无需 Dockerfile 进行容器化，或提及“dotnet publish container”、“PublishContainer”、“ContainerRepository”、“ContainerFamily”、“精简镜像”、“distroless”、“container publish”、“SDK container”、“no Dockerfile”或“无需 Dockerfile 进行容器化”时，加载此技能。
---

# 容器发布（无需 Dockerfile）

## 核心原则

1. **无需 Dockerfile** — .NET 10 SDK 直接通过 `dotnet publish /t:PublishContainer` 从源代码构建 OCI 兼容的容器镜像，无需编写或维护 Dockerfile。
2. **精简镜像用于生产** — 使用 `noble-chiseled` 基础镜像：无 Shell、无包管理器、仅包含 7 个 Linux 组件而非 100 多个，攻击面最小。
3. **默认非 root 运行** — .NET 10 容器镜像自动以 `app` 用户身份运行。生产环境中切勿切换为 root。
4. **配置在 .csproj 文件中** — 所有容器设置均为 MSBuild 属性，与项目代码一同版本控制，无需额外文件导致配置漂移。

## 模式

### 最小化容器发布

无需修改项目文件，直接发布：

```bash
dotnet publish /t:PublishContainer --os linux --arch x64
```

这将在本地 Docker 守护进程中使用默认的 `aspnet:10.0` 基础镜像创建容器镜像。

### 生产就绪的 .csproj 配置

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ContainerRepository>mycompany/myapp-api</ContainerRepository>
    <ContainerFamily>noble-chiseled</ContainerFamily>
  </PropertyGroup>

  <ItemGroup>
    <ContainerPort Include="8080" Type="tcp" />
    <ContainerEnvironmentVariable Include="ASPNETCORE_HTTP_PORTS" Value="8080" />
    <ContainerEnvironmentVariable Include="DOTNET_EnableDiagnostics" Value="0" />
    <ContainerLabel Include="org.opencontainers.image.vendor" Value="MyCompany" />
  </ItemGroup>

</Project>
```

### 发布到镜像仓库

先使用 `docker login` 进行认证，然后指定镜像仓库：

```bash
# GitHub 容器镜像仓库
docker login ghcr.io
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=ghcr.io \
    -p ContainerImageTag=1.0.0

# Azure 容器镜像仓库
az acr login --name myregistry
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=myregistry.azurecr.io

# Docker Hub（仓库名需包含用户名前缀）
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=docker.io \
    -p ContainerRepository=myuser/myapp
```

### 多架构镜像

使用单一发布命令构建多个平台镜像：

```xml
<PropertyGroup>
    <RuntimeIdentifiers>linux-x64;linux-arm64</RuntimeIdentifiers>
    <ContainerRuntimeIdentifiers>linux-x64;linux-arm64</ContainerRuntimeIdentifiers>
</PropertyGroup>
```

```bash
dotnet publish /t:PublishContainer
```

这将生成 OCI 镜像索引，镜像仓库会自动分发正确的架构版本。

### 多个标签

```bash
# Bash — 注意分号的引号
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerImageTags='"1.0.0;latest"'
```

或直接在项目文件中配置：

```xml
<ContainerImageTags>1.0.0;latest</ContainerImageTags>
```

### 保存为 Tarball（无需 Docker）

构建机器无需容器运行时环境。适用于 CI 扫描：

```bash
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerArchiveOutputPath=./images/myapp.tar.gz

# 扫描前使用 Trivy
trivy image --input ./images/myapp.tar.gz
```

### Chiseled 镜像变体

| 容器系列 | 用途 | 是否包含 Shell | 大小 |
|---------|------|----------------|------|
| *(默认)* | 通用（Debian） | 是 | ~220 MB |
| `noble-chiseled` | 生产（无 Shell） | 否 | ~110 MB |
| `noble-chiseled-extra` | 生产带本地化（ICU） | 否 | ~120 MB |
| `alpine` | 小型化 | 是 | ~112 MB |

```xml
<!-- 标准精简镜像（InvariantGlobalization=true） -->
<ContainerFamily>noble-chiseled</ContainerFamily>

<!-- 带 ICU 的精简镜像用于本地化 -->
<ContainerFamily>noble-chiseled-extra</ContainerFamily>
```

对于原生 AOT，SDK 会自动选择 `chiseled-aot`：

```xml
<PublishAot>true</PublishAot>
<!-- SDK 自动选择 runtime-deps:10.0-noble-chiseled-aot -->
```

### GitHub Actions CI/CD

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-dotnet@v5
        with:
          dotnet-version: '10.0.x'
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          dotnet publish src/MyApp.Api/MyApp.Api.csproj \
            /t:PublishContainer --os linux --arch x64 \
            -p ContainerRegistry=ghcr.io \
            -p ContainerRepository=${{ github.repository_owner }}/myapp \
            -p ContainerImageTag=${{ github.sha }}
```

## 反模式

### 不要使用已弃用的属性名

```xml
<!-- BAD — ContainerImageName 已弃用 -->
<ContainerImageName>myapp</ContainerImageName>

<!-- GOOD — 使用 ContainerRepository -->
<ContainerRepository>myapp</ContainerRepository>
```

### 不要使用 PublishProfile=DefaultContainer

```bash
# BAD — 旧方法，跨项目类型不一致
dotnet publish -p:PublishProfile=DefaultContainer

# GOOD — 直接使用 MSBuild 目标
dotnet publish /t:PublishContainer
```

### 不要忘记指定 Linux 目标

```bash
# BAD 在 Windows 上 — 可能生成 Windows 容器
dotnet publish /t:PublishContainer

# GOOD — 明确指定 Linux
dotnet publish /t:PublishContainer --os linux --arch x64
```

### 发布前不要跳过认证

```bash
# BAD — 会报 CONTAINER1013 错误
dotnet publish /t:PublishContainer -p ContainerRegistry=ghcr.io

# GOOD — 先认证
docker login ghcr.io
dotnet publish /t:PublishContainer -p ContainerRegistry=ghcr.io
```

### 需要操作系统包时不要使用 SDK 发布

```xml
<!-- BAD — SDK 容器发布无法执行 apt-get 或安装原生包 -->
<!-- 没有等效的 RUN 命令 -->

<!-- GOOD — 先创建自定义基础镜像（Dockerfile），再引用 -->
<ContainerBaseImage>myregistry/custom-base:1.0</ContainerBaseImage>
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 标准 ASP.NET Core API | SDK 容器发布配合 `noble-chiseled` |
| 工作服务/控制台应用 | SDK 容器发布（原生 .NET 10 支持） |
| 需要原生操作系统包 | Dockerfile（或自定义基础镜像 + SDK 发布） |
| Azure Functions | Dockerfile（SDK 发布不支持） |
| 无 Docker 守护进程的 CI | 使用 `ContainerArchiveOutputPath` 输出 Tarball |
| 多架构部署（x64 + arm64） | `ContainerRuntimeIdentifiers` 属性 |
| 生产镜像大小 | `noble-chiseled` (~110 MB) 或原生 AOT (~10 MB) |
| 本地开发 | `dotnet publish /t:PublishContainer --os linux --arch x64` |
| 镜像仓库推送 | `ContainerRegistry` + `docker login` |
