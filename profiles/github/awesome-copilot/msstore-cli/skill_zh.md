# Microsoft Store 开发者 CLI (msstore)

Microsoft Store 开发者 CLI (`msstore`) 是一个跨平台的命令行界面，用于在 Microsoft Store 中发布和管理应用程序。它与合作伙伴中心 API 集成，并支持各种应用程序类型的自动化发布工作流。

## 何时使用此功能

当你需要执行以下操作时，请使用此功能：

- 配置用于 API 访问的 Store 凭据
- 列出你 Store 账户中的应用程序
- 检查提交状态
- 将提交发布到 Store
- 为 Store 提交打包应用程序
- 初始化用于 Store 发布的项目
- 管理包飞行（测试版）
- 设置用于 Store 自动化发布的 CI/CD 管道
- 管理提交的渐进式发布
- 程序化更新提交元数据

## 前提条件

- Windows 10+、macOS 或 Linux
- .NET 9 桌面运行时（Windows）或 .NET 9 运行时（macOS/Linux）
- 具有适当权限的合作伙伴中心账户
- 具有合作伙伴中心 API 访问权限的 Azure AD 应用注册
- 通过以下任一方法安装的 msstore CLI：
  - **Microsoft Store**：[下载](https://www.microsoft.com/store/apps/9P53PC5S0PHJ)
  - **WinGet**：`winget install "Microsoft Store Developer CLI"`
  - **手动**：从 [GitHub 发布](https://aka.ms/msstoredevcli/releases) 下载

### 合作伙伴中心设置

在使用 msstore 之前，你需要创建一个具有合作伙伴中心访问权限的 Azure AD 应用程序：

1. 前往 [合作伙伴中心](https://partner.microsoft.com/dashboard)
2. 导航到 **账户设置** > **用户管理** > **Azure AD 应用程序**
3. 创建一个新的应用程序，并记下 **租户 ID**、**客户端 ID** 和 **客户端密钥**
4. 授予应用程序适当的权限（管理或开发者角色）

## 核心命令参考

### info - 打印配置

显示当前的凭据配置。

```bash
msstore info
```

**选项：**

| 选项 | 描述 |
|------|------|
| `-v, --verbose` | 打印详细输出 |

### reconfigure - 配置凭据

配置或更新 Microsoft Store API 凭据。

```bash
msstore reconfigure [选项]
```

**选项：**

| 选项 | 描述 |
|------|------|
| `-t, --tenantId` | Azure AD 租户 ID |
| `-s, --sellerId` | 合作伙伴中心卖家 ID |
| `-c, --clientId` | Azure AD 应用程序客户端 ID |
| `-cs, --clientSecret` | 用于身份验证的客户端密钥 |
| `-ct, --certificateThumbprint` | 证书指纹（客户端密钥的替代方案） |
| `-cfp, --certificateFilePath` | 证书文件路径（客户端密钥的替代方案） |
| `-cp, --certificatePassword` | 证书密码 |
| `--reset` | 不进行完整重新配置即可重置凭据 |

**示例：**

```bash
# 使用客户端密钥配置
msstore reconfigure --tenantId $TENANT_ID --sellerId $SELLER_ID --clientId $CLIENT_ID --clientSecret $CLIENT_SECRET

# 使用证书配置
msstore reconfigure --tenantId $TENANT_ID --sellerId $SELLER_ID --clientId $CLIENT_ID --certificateFilePath ./cert.pfx --certificatePassword MyPassword
```

### settings - CLI 设置

更改 Microsoft Store 开发者 CLI 的设置。

```bash
msstore settings [选项]
```

**选项：**

| 选项 | 描述 |
|------|------|
| `-t, --enableTelemetry` | 启用（true）或禁用（false）遥测 |

#### 设置发布者显示名称

```bash
msstore settings setpdn <publisherDisplayName>
```

为 `init` 命令设置默认发布者显示名称。

### apps - 应用程序管理

列出和检索应用程序信息。

#### 列出应用程序

```bash
msstore apps list
```

列出你合作伙伴中心账户中的所有应用程序。

#### 获取应用程序详细信息

```bash
msstore apps get <productId>
```

**参数：**

| 参数 | 描述 |
|------|------|
| `productId` | Store 产品 ID（例如，9NBLGGH4R315） |

**示例：**

```bash
# 获取特定应用的详细信息
msstore apps get 9NBLGGH4R315
```

### submission - 提交管理

管理 Store 提交。

| 子命令 | 描述 |
|--------|------|
| `status` | 获取提交状态 |
| `get` | 获取提交元数据和包信息 |
| `getListingAssets` | 获取提交的列表资产 |
| `updateMetadata` | 更新提交元数据 |
| `poll` | 循环查询提交状态，直到完成 |
| `publish` | 发布提交 |
| `delete` | 删除提交 |

#### 获取提交状态

```bash
msstore submission status <productId>
```

#### 获取提交详细信息

```bash
msstore submission get <productId>
```

#### 更新元数据

```bash
msstore submission updateMetadata <productId> <metadata>
```

其中 `<metadata>` 是包含更新元数据的 JSON 字符串。由于 JSON 包含 shell 解释的字符（引号、大括号等），你必须适当地引用和/或转义值：

- **Bash/Zsh**：用单引号将 JSON 包裹起来，以便 shell 字面传递它。
  ```bash
  msstore submission updateMetadata 9NBLGGH4R315 '{"description":"我的更新应用"}'
  ```
- **PowerShell**：使用单引号（或在双引号字符串内转义双引号）。
  ```powershell
  msstore submission updateMetadata 9NBLGGH4R315 '{"description":"我的更新应用"}'
  ```
- **cmd.exe**：用反斜杠转义每个内部双引号。
  ```cmd
  msstore submission updateMetadata 9NBLGGH4R315 "{\"description\":\"我的更新应用\"}"
  ```

> **提示**：对于复杂或多行的元数据，将 JSON 保存到文件中，并传递其内容，以避免引用问题：
> ```bash
> msstore submission updateMetadata 9NBLGGH4R315 "$(cat metadata.json)"
> ```

**选项：**

| 选项 | 描述 |
|------|------|
| `-s, --skipInitialPolling` | 跳过初始状态循环查询 |

#### 发布提交

```bash
msstore submission publish <productId>
```

#### 循环查询提交

```bash
msstore submission poll <productId>
```

循环查询，直到提交状态为 PUBLISHED 或 FAILED。

#### 删除提交

```bash
msstore submission delete <productId>
```

**选项：**

| 选项 | 描述 |
|------|------|
| `--no-confirm` | 跳过确认提示 |

### init - 初始化用于 Store 的项目

初始化项目用于 Microsoft Store 发布。自动检测项目类型并配置 Store 身份。

```bash
msstore init <pathOrUrl> [选项]
```

**参数：**

| 参数 | 描述 |
|------|------|
| `pathOrUrl` | 项目目录路径或 PWA URL |

**选项：**

| 选项 | 描述 |
|------|------|
| `-n, --publisherDisplayName` | 发布者显示名称 |
| `--package` | 同时打包项目 |
| `--publish` | 打包并发布（隐含 --package） |
| `-f, --flightId` | 发布到特定飞行 |
| `-prp, --packageRolloutPercentage` | 渐进式发布百分比（0-100） |
| `-a, --arch` | 架构：x86、x64、arm64 |
| `-o, --output` | 包的输出目录 |
| `-ver, --version` | 构建时使用的版本 |

**支持的项目类型：**

- Windows App SDK / WinUI 3
- UWP
- .NET MAUI
- Flutter
- Electron
- React Native for Desktop
- PWA（渐进式 Web 应用）

**示例：**

```bash
# 初始化 WinUI 项目
msstore init ./my-winui-app

# 初始化 PWA
msstore init https://contoso.com --output ./pwa-package

# 初始化并发布
msstore init ./my-app --publish
```

### package - 打包用于 Store

为 Microsoft Store 提交打包应用程序。

```bash
msstore package <pathOrUrl> [选项]
```

**参数：**

| 参数 | 描述 |
|------|------|
| `pathOrUrl` | 项目目录路径或 PWA URL |

**选项：**

| 选项 | 描述 |
|------|------|
| `-o, --output` | 包的输出目录 |
| `-a, --arch` | 架构：x86、x64、arm64 |
| `-ver, --version` | 包的版本 |

**示例：**

```bash
# 默认架构打包
msstore package ./my-app

# 多架构打包
msstore package ./my-app --arch x64,arm64 --output ./packages

# 指定版本打包
msstore package ./my-app --version 1.2.3.0
```

### publish - 发布到 Store

将应用程序发布到 Microsoft Store。

```bash
msstore publish <pathOrUrl> [选项]
```

**参数：**

| 参数 | 描述 |
|------|------|
| `pathOrUrl` | 项目目录路径或 PWA URL |

**选项：**

| 选项 | 描述 |
|------|------|
| `-i, --inputFile` | 现有 .msix 或 .msixupload 文件的路径 |
| `-id, --appId` | 应用程序 ID（如果未初始化） |
| `-nc, --noCommit` | 将提交保持在草稿状态 |
| `-f, --flightId` | 发布到特定飞行 |
| `-prp, --packageRolloutPercentage` | 渐进式发布百分比（0-100） |

**示例：**

```bash
# 发布项目
msstore publish ./my-app

# 发布现有包
msstore publish ./my-app --inputFile ./packages/MyApp.msixupload

# 发布为草稿
msstore publish ./my-app --noCommit

# 渐进式发布
msstore publish ./my-app --packageRolloutPercentage 10
```

### flights - 包飞行管理

管理包飞行（测试版组）。

| 子命令 | 描述 |
|--------|------|
| `list` | 列出应用程序的所有飞行 |
| `get` | 获取飞行详细信息 |
| `delete` | 删除飞行 |
| `create` | 创建新的飞行 |
| `submission` | 管理飞行提交 |

#### 列出飞行

```bash
msstore flights list <productId>
```

#### 获取飞行详细信息

```bash
msstore flights get <productId> <flightId>
```

#### 创建飞行

```bash
msstore flights create <productId> <friendlyName> --group-ids <group-ids>
```

**选项：**

| 选项 | 描述 |
|------|------|
| `-g, --group-ids` | 飞行组 ID（逗号分隔） |
| `-r, --rank-higher-than` | 指定比该飞行 ID 排名更高的飞行 ID |

#### 删除飞行

```bash
msstore flights delete <productId> <flightId>
```

#### 飞行提交

```bash
# 获取飞行提交
msstore flights submission get <productId> <flightId>

# 发布飞行提交
msstore flights submission publish <productId> <flightId>

# 检查飞行提交状态
msstore flights submission status <productId> <flightId>

# 循环查询飞行提交
msstore flights submission poll <productId> <flightId>

# 删除飞行提交
msstore flights submission delete <productId> <flightId>
```

#### 飞行发布管理

```bash
# 获取发布状态
msstore flights submission rollout get <productId> <flightId>

# 更新发布百分比
msstore flights submission rollout update <productId> <flightId> <percentage>

# 停止发布
msstore flights submission rollout halt <productId> <flightId>

# 最终化发布（100%）
msstore flights submission rollout finalize <productId> <flightId>
```

## 常见工作流

### 工作流 1：首次 Store 设置

```bash
# 1. 安装 CLI
winget install "Microsoft Store Developer CLI"

# 2. 配置凭据（从合作伙伴中心获取这些值）
msstore reconfigure --tenantId $TENANT_ID --sellerId $SELLER_ID --clientId $CLIENT_ID --clientSecret $CLIENT_SECRET

# 3. 验证配置
msstore info

# 4. 列出你的应用以确认访问权限
msstore apps list
```

### 工作流 2：初始化并发布新应用

```bash
# 1. 导航到项目
cd my-winui-app

# 2. 初始化用于 Store（创建/更新应用身份）
msstore init .

# 3. 打包应用程序
msstore package . --arch x64,arm64

# 4. 发布到 Store
msstore publish .

# 5. 检查提交状态
msstore submission status <productId>
```

### 工作流 3：更新现有应用

```bash
# 1. 构建你的更新后的应用程序
dotnet publish -c Release

# 2. 打包并发布
msstore publish ./my-app

# 或从现有包发布
msstore publish ./my-app --inputFile ./artifacts/MyApp.msixupload
```

### 工作流 4：渐进式发布

```bash
# 1. 发布并设置初始发布百分比
msstore publish ./my-app --packageRolloutPercentage 10

# 2. 监控并增加发布
msstore submission poll <productId>

# 3. （验证后）最终化为 100%
# 这通过合作伙伴中心或提交更新完成
```

### 工作流 5：使用飞行进行测试版测试

```bash
# 1. 首先在合作伙伴中心创建飞行组
# 然后创建飞行
msstore flights create <productId> "测试版测试者" --group-ids "group-id-1,group-id-2"

# 2. 发布到飞行
msstore publish ./my-app --flightId <flightId>

# 3. 检查飞行提交状态
msstore flights submission status <productId> <flightId>

# 4. 测试后，发布到生产环境
msstore publish ./my-app
```

### 工作流 6：CI/CD 管道集成

```yaml
# GitHub Actions 示例
name: 发布到 Store

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: 设置 .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'
      
      - name: 安装 msstore CLI
        run: winget install "Microsoft Store Developer CLI" --accept-package-agreements --accept-source-agreements
      
      - name: 配置 Store 凭据
        run: |
          msstore reconfigure --tenantId ${{ secrets.TENANT_ID }} --sellerId ${{ secrets.SELLER_ID }} --clientId ${{ secrets.CLIENT_ID }} --clientSecret ${{ secrets.CLIENT_SECRET }}
      
      - name: 构建应用程序
        run: dotnet publish -c Release
      
      - name: 发布到 Store
        run: msstore publish ./src/MyApp
```

## 与 winapp CLI 集成

winapp CLI（v0.2.0+）通过 `winapp store` 子命令与 msstore 集成：

```bash
# 这些命令是等效的：
msstore reconfigure --tenantId xxx --clientId xxx --clientSecret xxx
winapp store reconfigure --tenantId xxx --clientId xxx --clientSecret xxx

# 列出应用
msstore apps list
winapp store apps list

# 发布
msstore publish ./my-app
winapp store publish ./my-app
```

当你希望获得统一 CLI 体验以进行打包和发布时，使用 `winapp store`。

## 故障排除

| 问题 | 解决方案 |
|------|------|
| 身份验证失败 | 使用 `msstore info` 验证凭据；重新运行 `msstore reconfigure` |
| 应用未找到 | 确保产品 ID 正确；运行 `msstore apps list` 以验证 |
| 权限不足 | 检查合作伙伴中心中的 Azure AD 应用角色（需要管理或开发者角色） |
| 包验证失败 | 确保包符合 Store 要求；在合作伙伴中心查看详细信息 |
| 提交卡住 | 运行 `msstore submission poll <productId>` 检查状态 |
| 飞行未找到 | 使用 `msstore flights list <productId>` 验证飞行 ID |
| 发布百分比无效 | 值必须在 0 到 100 之间 |
| 初始化 PWA 失败 | 确保 URL 公开可访问且具有有效的 Web 应用清单 |

## 环境变量

CLI 支持用于凭据的环境变量：

| 变量 | 描述 |
|------|------|
| `MSSTORE_TENANT_ID` | Azure AD 租户 ID |
| `MSSTORE_SELLER_ID` | 合作伙伴中心卖家 ID |
| `MSSTORE_CLIENT_ID` | Azure AD 应用程序客户端 ID |
| `MSSTORE_CLIENT_SECRET` | 客户端密钥 |

## 参考

- [Microsoft Store 开发者 CLI 文档](https://learn.microsoft.com/windows/apps/publish/msstore-dev-cli/overview)
- [CLI 命令参考](https://learn.microsoft.com/windows/apps/publish/msstore-dev-cli/commands)
- [GitHub 仓库](https://github.com/microsoft/msstore-cli)
- [合作伙伴中心 API](https://learn.microsoft.com/windows/uwp/monetize/using-windows-store-services)
- [应用提交 API](https://learn.microsoft.com/windows/uwp/monetize/create-and-manage-submissions-using-windows-store-services)
- [包飞行概述](https://learn.microsoft.com/windows/uwp/publish/package-flights)
- [渐进式包发布](https://learn.microsoft.com/windows/uwp/publish/gradual-package-rollout)
