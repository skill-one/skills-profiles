# NuGet 管理器

## 概述

此技能确保在 .NET 项目中始终如一且安全地管理 NuGet 包。它优先使用 `dotnet` CLI 来维护项目完整性，并对版本更新强制执行严格的验证和还原工作流。

## 前置条件

- 已安装 .NET SDK（通常为 .NET 8.0 SDK 或更高版本，或与目标解决方案兼容的版本）。
- `dotnet` CLI 可在您的 `PATH` 中使用。
- `jq`（JSON 处理器）或 PowerShell（用于使用 `dotnet package search` 进行版本验证）。

## 核心规则

1.  **绝对不要**直接编辑 `.csproj`、`.props` 或 `Directory.Packages.props` 文件来**添加**或**移除**包。始终使用 `dotnet add package` 和 `dotnet remove package` 命令。
2.  **直接编辑**仅允许用于**更改**现有包的版本。
3.  **版本更新**必须遵循强制的工作流：
    - 验证目标版本是否存在于 NuGet 上。
    - 确定版本是按项目（`.csproj`）管理还是集中（`Directory.Packages.props`）管理。
    - 在适当的文件中更新版本字符串。
    - 立即运行 `dotnet restore` 以验证兼容性。

## 工作流

### 添加包
使用 `dotnet add [<PROJECT>] package <PACKAGE_NAME> [--version <VERSION>]`。
示例：`dotnet add src/MyProject/MyProject.csproj package Newtonsoft.Json`

### 移除包
使用 `dotnet remove [<PROJECT>] package <PACKAGE_NAME>`。
示例：`dotnet remove src/MyProject/MyProject.csproj package Newtonsoft.Json`

### 更新包版本
更新版本时，请按照以下步骤操作：

1.  **验证版本存在性**：
    使用 `dotnet package search` 命令并使用精确匹配和 JSON 格式进行检查。
    使用 `jq`：
    `dotnet package search <PACKAGE_NAME> --exact-match --format json | jq -e '.searchResult[].packages[] | select(.version == "<VERSION>")'`
    使用 PowerShell：
    `(dotnet package search <PACKAGE_NAME> --exact-match --format json | ConvertFrom-Json).searchResult.packages | Where-Object { $_.version -eq "<VERSION>" }`
    
2.  **确定版本管理方式**：
    - 在解决方案根目录中搜索 `Directory.Packages.props`。如果存在，应通过 `<PackageVersion Include="Package.Name" Version="1.2.3" />` 在其中管理版本。
    - 如果不存在，检查单个 `.csproj` 文件中的 `<PackageReference Include="Package.Name" Version="1.2.3" />`。

3.  **应用更改**：
    修改已识别的文件，并使用新的版本字符串。

4.  **验证稳定性**：
    对项目或解决方案运行 `dotnet restore`。如果出现错误，请回滚更改并进行调查。

## 示例

### 用户："将 Serilog 添加到 WebApi 项目"
**操作**：执行 `dotnet add src/WebApi/WebApi.csproj package Serilog`。

### 用户："在整个解决方案中将 Newtonsoft.Json 更新为 13.0.3"
**操作**：
1. 验证 13.0.3 是否存在：`dotnet package search Newtonsoft.Json --exact-match --format json`（并解析输出以确认 "13.0.3" 存在）。
2. 找到其定义位置（例如，`Directory.Packages.props`）。
3. 编辑文件以更新版本。
4. 运行 `dotnet restore`。
