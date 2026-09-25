# 项目结构

## 核心原则

1. **中央包管理** — 使用 `Directory.Packages.props` 在一处管理 NuGet 包版本。各个 `.csproj` 文件中无需包含版本号。
2. **共享构建属性** — 使用 `Directory.Build.props` 用于通用设置（目标框架、可空性、隐式引用）。无需在每个项目中重复。
3. **.slnx 用于解决方案** — 新的基于 XML 的解决方案格式比传统的 `.sln` 格式更简洁且更易于合并。
4. **src/ 和 tests/ 分离** — 源项目位于 `src/`，测试项目位于 `tests/`。边界清晰。

## 模式

### 解决方案布局

```
MyApp/
├── MyApp.slnx                       # 解决方案文件
├── Directory.Build.props             # 共享 MSBuild 属性
├── Directory.Packages.props          # 中央包管理
├── .editorconfig                     # 代码风格规则
├── .gitignore
├── global.json                       # SDK 版本锁定
├── src/
│   ├── MyApp.Api/                    # Web API (入口点)
│   │   ├── MyApp.Api.csproj
│   │   ├── Program.cs
│   │   └── Features/
│   ├── MyApp.Domain/                 # 领域实体、值对象 (可选)
│   │   └── MyApp.Domain.csproj
│   └── MyApp.Infrastructure/         # EF Core、外部服务 (可选)
│       └── MyApp.Infrastructure.csproj
└── tests/
    └── MyApp.Api.Tests/
        └── MyApp.Api.Tests.csproj
```

### Directory.Build.props

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <LangVersion>14</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
```

### Directory.Packages.props (中央包管理)

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <!-- 以下版本仅为示例 — 使用 `dotnet add package <name>` (无 --version 标志) 解析当前稳定版本；参见包规则 -->
    <!-- ASP.NET Core -->
    <PackageVersion Include="Mediator.Abstractions" Version="3.0.0" />
    <PackageVersion Include="Mediator.SourceGenerator" Version="3.0.0" />
    <PackageVersion Include="FluentValidation.DependencyInjectionExtensions" Version="12.0.0" />

    <!-- 数据 -->
    <PackageVersion Include="Microsoft.EntityFrameworkCore" Version="10.0.10" />
    <PackageVersion Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="10.0.10" />

    <!-- 可观察性 -->
    <PackageVersion Include="Serilog.AspNetCore" Version="10.0.0" />
    <PackageVersion Include="OpenTelemetry.Extensions.Hosting" Version="1.17.0" />

    <!-- 测试 -->
    <PackageVersion Include="xunit.v3" Version="3.2.2" />
    <PackageVersion Include="Microsoft.AspNetCore.Mvc.Testing" Version="10.0.10" />
    <PackageVersion Include="Testcontainers.PostgreSql" Version="4.13.0" />
  </ItemGroup>
</Project>
```

### 项目文件 (.csproj) 带中央包管理

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <!-- 此处无需 TargetFramework — 从 Directory.Build.props 继承 -->

  <ItemGroup>
    <!-- 无 Version 属性 — 由中央管理 -->
    <PackageReference Include="Mediator.Abstractions" />
    <PackageReference Include="Mediator.SourceGenerator" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" />
    <PackageReference Include="Microsoft.EntityFrameworkCore" />
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" />
    <PackageReference Include="Serilog.AspNetCore" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\MyApp.Domain\MyApp.Domain.csproj" />
    <ProjectReference Include="..\MyApp.Infrastructure\MyApp.Infrastructure.csproj" />
  </ItemGroup>
</Project>
```

### global.json (SDK 锁定)

```json
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestFeature"
  }
}
```

### .slnx 解决方案格式

```xml
<Solution>
  <Folder Name="/src/">
    <Project Path="src/MyApp.Api/MyApp.Api.csproj" />
    <Project Path="src/MyApp.Domain/MyApp.Domain.csproj" />
    <Project Path="src/MyApp.Infrastructure/MyApp.Infrastructure.csproj" />
  </Folder>
  <Folder Name="/tests/">
    <Project Path="tests/MyApp.Api.Tests/MyApp.Api.Tests.csproj" />
  </Folder>
</Solution>
```

### 命名约定

| 元素 | 约定 | 示例 |
|------|------|------|
| 解决方案 | `CompanyName.AppName` 或 `AppName` | `MyApp.slnx` |
| 项目 | `AppName.Layer` | `MyApp.Api`, `MyApp.Domain` |
| 命名空间 | 与文件夹路径匹配 | `MyApp.Api.Features.Orders` |
| 功能文件夹 | PascalCase、复数 | `Features/Orders/` |
| 测试项目 | `ProjectName.Tests` | `MyApp.Api.Tests` |

## 反模式

### 不要分散包版本

```xml
<!-- BAD — 每个 .csproj 中都有版本，版本漂移 -->
<PackageReference Include="Mediator.Abstractions" Version="2.0.0" />  <!-- 在项目 A 中 -->
<PackageReference Include="Mediator.Abstractions" Version="3.0.0" />  <!-- 在项目 B 中 -->

<!-- GOOD — 中央管理，单一版本 -->
<!-- Directory.Packages.props: <PackageVersion Include="Mediator.Abstractions" Version="3.0.0" /> -->
<!-- .csproj: <PackageReference Include="Mediator.Abstractions" /> -->
```

### 不要重复构建属性

```xml
<!-- BAD — 每个 .csproj 中都有相同属性 -->
<PropertyGroup>
  <TargetFramework>net10.0</TargetFramework>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
</PropertyGroup>

<!-- GOOD — 在 Directory.Build.props 中定义一次，处处继承 -->
```

### 不要混合源代码和测试项目

```
# BAD — 测试与源代码混合
src/
  MyApp.Api/
  MyApp.Api.Tests/    # 源代码中的测试项目

# GOOD — 清晰分离
src/
  MyApp.Api/
tests/
  MyApp.Api.Tests/
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 新解决方案 | `.slnx` 格式 |
| 包版本管理 | `Directory.Packages.props` (中央) |
| 共享构建设置 | `Directory.Build.props` |
| SDK 版本锁定 | `global.json` |
| 常用 using 指令 | 在 `Directory.Build.props` 中定义全局 using |
| 小型 API (1-2 名开发者) | 单个项目 (`MyApp.Api`) |
| 中型 API (3-5 名开发者) | 2-3 个项目 (`Api`, `Domain`, `Infrastructure`) |
| 大型/模块化应用 | 每个模块一个项目，共享 `Contracts` |
