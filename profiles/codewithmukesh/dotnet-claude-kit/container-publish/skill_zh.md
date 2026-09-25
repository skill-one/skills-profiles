# 容器发布（无需 Dockerfile）

## 核心原则

1. **无需 Dockerfile** — .NET 10 SDK 直接通过 `dotnet publish /t:PublishContainer` 从源代码构建 OCI 兼容的容器镜像，无需编写或维护 Dockerfile。
2. **精简镜像用于生产** — 使用 `noble-chiseled` 基础镜像：无 Shell、无包管理器、仅 7 个 Linux 组件而非 100 多个，最小化攻击面。
3. **默认非 root 运行** — .NET 10 容器镜像自动以 `app` 用户身份运行。生产环境中切勿以 root 身份运行。
4. **配置在 .csproj 文件中** — 所有容器设置均为 MSBuild 属性，与项目一同版本控制，无需额外文件导致配置漂移。

## 模式

### 最小化容器发布

无需修改项目文件，只需发布：

```bash
dotnet publish /t:PublishContainer --os linux --arch x64
```

这将在本地 Docker 守护进程中创建一个使用默认 `aspnet:10.0` 基础镜像的容器镜像。

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
# GitHub Container Registry
docker login ghcr.io
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=ghcr.io \
    -p ContainerImageTag=1.0.0

# Azure Container Registry
az acr login --name myregistry
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerRegistry=myregistry.azurecr.io

# Docker Hub（需要仓库名前缀）
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

这将生成 OCI 镜像索引，镜像仓库会自动提供正确的架构。

### 多个标签

```bash
# Bash — 注意分号的引号
dotnet publish /t:PublishContainer --os linux --arch x64 \
    -p ContainerImageTags='"1.0.0;latest"'
```

或直接在项目文件中：

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

| ContainerFamily | 用途 | 是否有 Shell | 大小 |
|----------------|------|-------------|------|
| *(默认)* | 通用（Debian） | 是 | ~220 MB |
| `noble-chiseled` | 生产（无 Shell） | 否 | ~110 MB |
| `noble-chiseled-extra` | 生产带本地化（ICU） | 否 | ~120 MB |
| `alpine` | 小尺寸，有 Shell | 是 | ~112 MB |

```xml
<!-- 标准的 Chiseled（InvariantGlobalization=true） -->
<ContainerFamily>noble-chiseled</ContainerFamily>

<!-- Chiseled 带 ICU 用于本地化 -->
<ContainerFamily>noble-chiseled-extra</ContainerFamily>
```

对于原生 AOT，SDK 会自动选择 `chiseled-aot`：

```xml
<PublishAot>true</PublishAot>
<!-- SDK 自动选择 runtime-deps:10.0-noble-chiseled-aot -->
```

### GitHub Actions 中的 CI/CD

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

### 不要忘记指定 Linux

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
<!-- BAD — SDK 容器发布无法运行 apt-get 或安装原生包 -->
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
| 生产镜像大小 | `noble-chiseled` (~110 MB) 或 Native AOT (~10 MB) |
| 本地开发 | `dotnet publish /t:PublishContainer --os linux --arch x64` |
| 镜像仓库推送 | `ContainerRegistry` + `docker login` |
