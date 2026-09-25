# MSBuild现代化：从传统到SDK风格的迁移

## 识别传统项目与SDK风格项目

**传统指示器：**

- `<Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />`
- 显式文件列表（每个`.cs`文件使用`<Compile Include="..." />`）
- `<Project>`元素上的`ToolsVersion`属性
- 存在`packages.config`文件
- `Properties\AssemblyInfo.cs`包含程序集级别属性

**SDK风格指示器：**

- 根元素上具有`<Project Sdk="Microsoft.NET.Sdk">`属性
- 内容简洁——简单项目可能只有10-15行
- 无显式文件包含（隐式通配符）
- 使用`<PackageReference>`替代`packages.config`

**快速检查：** 如果`.csproj`文件对于简单的类库或控制台应用程序超过50行，则可能是传统格式。

```xml
<!-- 传统：简单库约80+行 -->
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props" />
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
    <OutputType>Library</OutputType>
    <RootNamespace>MyLibrary</RootNamespace>
    <AssemblyName>MyLibrary</AssemblyName>
    <TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion>
    <FileAlignment>512</FileAlignment>
    <Deterministic>true</Deterministic>
  </PropertyGroup>
  <!-- ... 60+更多行... -->
  <Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />
</Project>
```

```xml
<!-- SDK风格：相同库约8行 -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net472</TargetFramework>
  </PropertyGroup>
</Project>
```

## 迁移检查清单：传统→SDK风格

### 第1步：替换项目根元素

**之前：**

```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props"
          Condition="Exists('$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props')" />
  <!-- ... 项目内容... -->
  <Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />
</Project>
```

**之后：**

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <!-- ... 项目内容... -->
</Project>
```

删除XML声明、`ToolsVersion`、`xmlns`以及两个`<Import>`行。`Sdk`属性取代了所有这些内容。

### 第2步：设置TargetFramework

**之前：**

```xml
<PropertyGroup>
  <TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion>
</PropertyGroup>
```

**之后：**

```xml
<PropertyGroup>
  <TargetFramework>net472</TargetFramework>
</PropertyGroup>
```

**TFM映射表：**

| 传统`TargetFrameworkVersion` | SDK风格`TargetFramework` |
|-----------------------------|---------------------------|
| `v4.6.1`                    | `net461`                  |
| `v4.7.2`                    | `net472`                  |
| `v4.8`                      | `net48`                   |
| （迁移到.NET 6）            | `net6.0`                  |
| （迁移到.NET 8）            | `net8.0`                  |

### 第3步：删除显式文件包含

**之前：**

```xml
<ItemGroup>
  <Compile Include="Controllers\HomeController.cs" />
  <Compile Include="Models\User.cs" />
  <Compile Include="Models\Order.cs" />
  <Compile Include="Services\AuthService.cs" />
  <Compile Include="Services\OrderService.cs" />
  <Compile Include="Properties\AssemblyInfo.cs" />
  <!-- ... 50+更多行... -->
</ItemGroup>
<ItemGroup>
  <Content Include="Views\Home\Index.cshtml" />
  <Content Include="Views\Shared\_Layout.cshtml" />
  <!-- ...更多内容文件... -->
</ItemGroup>
```

**之后：**

完全删除所有这些`<Compile>`和`<Content>`项组。SDK风格项目通过隐式通配符自动包含它们。

**例外：** 仅保留需要特殊元数据或位于项目目录外部的显式条目：

```xml
<ItemGroup>
  <Content Include="..\shared\config.json" Link="config.json" CopyToOutputDirectory="PreserveNewest" />
</ItemGroup>
```

### 第4步：删除AssemblyInfo.cs

**之前**（`Properties\AssemblyInfo.cs`）：

```csharp
using System.Reflection;
using System.Runtime.InteropServices;

[assembly: AssemblyTitle("MyLibrary")]
[assembly: AssemblyDescription("一个有用的库")]
[assembly: AssemblyCompany("Contoso")]
[assembly: AssemblyProduct("MyLibrary")]
[assembly: AssemblyCopyright("版权所有 © Contoso 2024")]
[assembly: ComVisible(false)]
[assembly: Guid("...")]
[assembly: AssemblyVersion("1.2.0.0")]
[assembly: AssemblyFileVersion("1.2.0.0")]
```

**之后**（在`.csproj`中）：

```xml
<PropertyGroup>
  <AssemblyTitle>MyLibrary</AssemblyTitle>
  <Description>一个有用的库</Description>
  <Company>Contoso</Company>
  <Product>MyLibrary</Product>
  <Copyright>版权所有 © Contoso 2024</Copyright>
  <Version>1.2.0</Version>
</PropertyGroup>
```

删除`Properties\AssemblyInfo.cs`——SDK会根据这些属性自动生成程序集属性。

**替代方案：** 如果您希望保留`AssemblyInfo.cs`，则禁用自动生成：

```xml
<PropertyGroup>
  <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
</PropertyGroup>
```

### 第5步：迁移packages.config→PackageReference

**之前**（`packages.config`）：

```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="Newtonsoft.Json" version="13.0.3" targetFramework="net472" />
  <package id="Serilog" version="3.1.1" targetFramework="net472" />
  <package id="Microsoft.Extensions.DependencyInjection" version="8.0.0" targetFramework="net472" />
</packages>
```

**之后**（在`.csproj`中）：

```xml
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  <PackageReference Include="Serilog" Version="3.1.1" />
  <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
</ItemGroup>
```

迁移后删除`packages.config`。

**迁移选项：**

- **Visual Studio：** 右键单击`packages.config` → *将packages.config迁移到PackageReference*
- **CLI：** `dotnet migrate-packages-config`或手动转换
- **绑定重定向：** SDK风格项目自动生成绑定重定向——如果`app.config`中存在`<runtime>`部分，则删除它

### 第6步：删除不必要的模板代码

删除以下所有内容——SDK提供合理的默认值：

```xml
<!-- 删除：SDK导入（由Sdk属性取代） -->
<Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props" ... />
<Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />

<!-- 删除：默认的Configuration/Platform（SDK提供这些） -->
<PropertyGroup>
  <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
  <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
  <ProjectGuid>{...}</ProjectGuid>
  <OutputType>Library</OutputType>  <!-- 仅在不是库时保留 -->
  <AppDesignerFolder>Properties</AppDesignerFolder>
  <FileAlignment>512</FileAlignment>
  <AutoGenerateBindingRedirects>true</AutoGenerateBindingRedirects>
  <Deterministic>true</Deterministic>
</PropertyGroup>

<!-- 删除：标准的Debug/Release配置（SDK默认值匹配） -->
<PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
  <DebugSymbols>true</DebugSymbols>
  <DebugType>full</DebugType>
  <Optimize>false</Optimize>
  <OutputPath>bin\Debug\</OutputPath>
  <DefineConstants>DEBUG;TRACE</DefineConstants>
  <ErrorReport>prompt</ErrorReport>
  <WarningLevel>4</WarningLevel>
</PropertyGroup>
<PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Release|AnyCPU' ">
  <DebugType>pdbonly</DebugType>
  <Optimize>true</Optimize>
  <OutputPath>bin\Release\</OutputPath>
  <DefineConstants>TRACE</DefineConstants>
  <ErrorReport>prompt</ErrorReport>
  <WarningLevel>4</WarningLevel>
</PropertyGroup>

<!-- 删除：框架程序集引用（SDK隐式包含） -->
<ItemGroup>
  <Reference Include="System" />
  <Reference Include="System.Core" />
  <Reference Include="System.Data" />
  <Reference Include="System.Xml" />
  <Reference Include="System.Xml.Linq" />
  <Reference Include="Microsoft.CSharp" />
</ItemGroup>

<!-- 删除：packages.config引用 -->
<None Include="packages.config" />

<!-- 删除：设计器服务条目 -->
<Service Include="{508349B6-6B84-11D3-8410-00C04F8EF8E0}" />

**保留**仅与SDK默认值不同的属性（例如，`<OutputType>Exe</OutputType>`，如果`RootNamespace`与程序集名称不同，自定义`<DefineConstants>`）。

### 第7步：启用现代功能

迁移后，考虑启用现代C#功能：

```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
</PropertyGroup>
```

- `<Nullable>enable</Nullable>` — 启用可空引用类型分析
- `<ImplicitUsings>enable</ImplicitUsings>` — 自动导入常用命名空间（.NET 6+）
- **避免`<LangVersion>latest`** — 实际语言版本由SDK/编译器默认值决定，而不仅由TFM决定，因此不同SDK安装的机器上构建可能不同。除非需要固定特定版本，否则省略`<LangVersion>`。对于可重复构建，使用`global.json`在仓库范围内固定SDK版本（这间接固定了默认语言版本），或为每个项目设置显式数字`<LangVersion>`（例如`<LangVersion>12</LangVersion>`）直接控制语言版本。

## 完整的Before/After示例

**之前**（传统——65行）：

```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props"
          Condition="Exists('$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props')" />
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
    <ProjectGuid>{12345678-1234-1234-1234-123456789ABC}</ProjectGuid>
    <OutputType>Library</OutputType>
    <AppDesignerFolder>Properties</AppDesignerFolder>
    <RootNamespace>MyLibrary</RootNamespace>
    <AssemblyName>MyLibrary</AssemblyName>
    <TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion>
    <FileAlignment>512</FileAlignment>
    <Deterministic>true</Deterministic>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
    <DebugSymbols>true</DebugSymbols>
    <DebugType>full</DebugType>
    <Optimize>false</Optimize>
    <OutputPath>bin\Debug\</OutputPath>
    <DefineConstants>DEBUG;TRACE</DefineConstants>
    <ErrorReport>prompt</ErrorReport>
    <WarningLevel>4</WarningLevel>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Release|AnyCPU' ">
    <DebugType>pdbonly</DebugType>
    <Optimize>true</Optimize>
    <OutputPath>bin\Release\</OutputPath>
    <DefineConstants>TRACE</DefineConstants>
    <ErrorReport>prompt</ErrorReport>
    <WarningLevel>4</WarningLevel>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="System" />
    <Reference Include="System.Core" />
    <Reference Include="System.Xml.Linq" />
    <Reference Include="Microsoft.CSharp" />
  </ItemGroup>
  <ItemGroup>
    <Compile Include="Models\User.cs" />
    <Compile Include="Models\Order.cs" />
    <Compile Include="Services\UserService.cs" />
    <Compile Include="Services\OrderService.cs" />
    <Compile Include="Helpers\StringExtensions.cs" />
    <Compile Include="Properties\AssemblyInfo.cs" />
  </ItemGroup>
  <ItemGroup>
    <None Include="packages.config" />
  </ItemGroup>
  <Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />
</Project>
```

**之后**（SDK风格——11行）：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net472</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="Serilog" Version="3.1.1" />
  </ItemGroup>
</Project>
```

## 常见迁移问题

**嵌入式资源：** 标准位置之外的文件可能需要显式包含：

```xml
<ItemGroup>
  <EmbeddedResource Include="..\shared\Schemas\*.xsd" LinkBase="Schemas" />
</ItemGroup>
```

**具有`CopyToOutputDirectory`的内容文件：** 这些仍然需要显式条目：

```xml
<ItemGroup>
  <Content Include="appsettings.json" CopyToOutputDirectory="PreserveNewest" />
  <None Include="scripts\*.sql" CopyToOutputDirectory="PreserveNewest" />
</ItemGroup>
```

**多目标：** 将元素名称从单数改为复数：

```xml
<!-- 单目标 -->
<TargetFramework>net8.0</TargetFramework>

<!-- 多目标 -->
<TargetFrameworks>net472;net8.0</TargetFrameworks>
```

**WPF/WinForms项目：** 使用适当的SDK或属性：

```xml
<!-- 选项A：WindowsDesktop SDK -->
<Project Sdk="Microsoft.NET.Sdk.WindowsDesktop">

<!-- 选项B：标准SDK中的属性（推荐用于.NET 5+） -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <UseWPF>true</UseWPF>
    <!-- 或 -->
    <UseWindowsForms>true</UseWindowsForms>
  </PropertyGroup>
</Project>
```

**测试项目：** 使用标准SDK和测试框架包：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageReference Include="xunit" Version="2.7.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.7" />
  </ItemGroup>
</Project>
```

## 中央包管理迁移

跨多项目解决方案集中管理NuGet版本。有关详细信息，请参阅[https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)。

**步骤1：** 在仓库根目录创建`Directory.Packages.props`，包含`<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`和所有包的`<PackageVersion>`条目。

**步骤2：** 删除每个项目`PackageReference`中的`Version`：

```xml
<!-- 之前 -->
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />

<!-- 之后 -->
<PackageReference Include="Newtonsoft.Json" />
```

## Directory.Build整合

识别跨多个`.csproj`文件重复的属性，并将它们移动到共享文件。

**`Directory.Build.props`**（用于属性——放置在仓库或源根目录）：

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <Company>Contoso</Company>
    <Copyright>版权所有 © Contoso 2024</Copyright>
  </PropertyGroup>
</Project>
```

**`Directory.Build.targets`**（用于目标/任务——放置在仓库或源根目录）：

```xml
<Project>
  <Target Name="PrintBuildInfo" AfterTargets="Build">
    <Message Importance="High" Text="构建 $(AssemblyName) → $(TargetPath)" />
  </Target>
</Project>
```

**在单独的`.csproj`文件中保留**仅项目特定的内容：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <AssemblyName>MyApp</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Serilog" />
    <ProjectReference Include="..\MyLibrary\MyLibrary.csproj" />
  </ItemGroup>
</Project>
```

## 工具和自动化

| 工具 | 使用 |
|------|-------|
| `dotnet try-convert` | 自动化传统到SDK的转换。安装：`dotnet tool install -g try-convert` |
| .NET Upgrade Assistant | 包含API更改的完整迁移。安装：`dotnet tool install -g upgrade-assistant` |
| Visual Studio | 右键单击`packages.config` → *将packages.config迁移到PackageReference* |
| 手动迁移 | 对于简单项目通常最干净——遵循上述检查清单 |

**推荐方法：**

1. 运行`try-convert`进行初步处理
2. 手动审查和清理输出
3. 构建并修复任何问题
4. 启用现代功能（可空、隐式using）
5. 将共享设置整合到`Directory.Build.props`
