---
name: winmd-api-search
description: 查找并探索 Windows 桌面 API。在构建需要平台功能（如相机、文件访问、通知、UI 控件、人工智能/机器学习、传感器、网络等）的功能时使用。发现适合任务的正确 API，并检索完整的类型详细信息（方法、属性、事件、枚举值）。
---

# WinMD API 搜索

这项技能可以帮助你为任何功能找到正确的 Windows API 并获取其详细信息。它搜索一个包含所有 WinMD 元数据的本地缓存，来源包括：

- **Windows 平台 SDK** — 所有 `Windows.*` WinRT API（始终可用，无需还原）
- **WinAppSDK / WinUI** — 作为缓存生成器的基础包捆绑（始终可用，无需还原）
- **NuGet 包** — 还原项目中包含 `.winmd` 文件的任何附加包
- **项目输出 WinMD** — 生成 `.winmd` 作为构建输出的类库（C++/WinRT, C#）

即使在全新克隆的代码库中，没有进行还原或构建，你仍然可以获得完整的平台 SDK + WinAppSDK 覆盖。

## 何时使用此技能

- 用户想构建一个功能，你需要找到提供该功能的 API
- 用户询问“如何做 X？”其中 X 涉及平台功能（相机、文件、通知、传感器、AI 等）
- 在编写代码之前，你需要知道某个类型的精确方法、属性、事件或枚举值
- 你不确定用于 UI 或系统任务的哪个控件、类或接口

## 前置条件

- **.NET SDK 8.0 或更高版本** — 用于构建缓存生成器。如果不可用，请从 [dotnet.microsoft.com](https://dotnet.microsoft.com/download) 安装。

## 缓存设置（首次使用前必须执行）

所有查询和搜索命令都从本地 JSON 缓存中读取。**你必须在使用任何查询之前生成缓存。**

```powershell
# 仓库中的所有项目（推荐首次运行时使用）
.\.github\skills\winmd-api-search\scripts\Update-WinMdCache.ps1

# 单个项目
.\.github\skills\winmd-api-search\scripts\Update-WinMdCache.ps1 -ProjectDir <项目文件夹>
```

对于基础覆盖（平台 SDK + WinAppSDK），无需项目还原或构建。对于附加 NuGet 包，项目需要 `dotnet restore`（这将生成 `project.assets.json`）或 `packages.config` 文件。

缓存存储在 `Generated Files\winmd-cache\`，按包+版本进行去重。

### 被索引的内容

| 来源 | 可用时机 |
|------|----------|
| Windows 平台 SDK | 始终可用（从本地 SDK 安装中读取） |
| WinAppSDK（最新版） | 始终可用（作为缓存生成器中的基础包捆绑） |
| WinAppSDK 运行时 | 安装在系统上时可用（通过 `Get-AppxPackage` 检测） |
| 项目 NuGet 包 | 执行 `dotnet restore` 后或使用 `packages.config` |
| 项目输出 `.winmd` | 项目构建后（生成 WinMD 的类库） |

> **注意**：此缓存目录应添加到 `.gitignore` 中——它是生成的，不是源代码。

## 如何使用

选择与情况匹配的路径：

---

### 发现 — “我不知道该使用哪个 API”

用户用自己的话描述了功能。你需要找到正确的 API。

**0. 确保缓存存在**

如果缓存尚未生成，请先运行 `Update-WinMdCache.ps1` —— 参见上方 [缓存设置](#缓存设置required-before-first-use)。

**1. 将用户语言翻译为搜索关键词**

将用户的日常语言映射到编程术语。尝试多种变体：

| 用户说 | 尝试的搜索关键词（按顺序） |
|--------|--------------------------|
| “拍张照片” | `camera`, `capture`, `photo`, `MediaCapture` |
| “从磁盘加载” | `file open`, `picker`, `FileOpen`, `StorageFile` |
| “描述其中内容” | `image description`, `Vision`, `Recognition` |
| “显示弹窗” | `dialog`, `flyout`, `popup`, `ContentDialog` |
| “拖放” | `drag`, `drop`, `DragDrop` |
| “保存设置” | `settings`, `ApplicationData`, `LocalSettings` |

从简单的日常词汇开始。如果结果较弱或不相关，请尝试更专业的变体。

**2. 运行搜索**

```powershell
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action search -Query "<关键词>"
```

这将返回按排名排序的命名空间，其中包含最匹配的类型以及**JSON 文件路径**。

如果结果**得分较低（低于 60）或不相关**，请回退到搜索在线文档：

1. 使用网络搜索在 Microsoft Learn 上找到正确的 API，例如：
   - `site:learn.microsoft.com/uwp/api <功能关键词>` 用于 `Windows.*` API
   - `site:learn.microsoft.com/windows/windows-app-sdk/api/winrt <功能关键词>` 用于 `Microsoft.*` WinAppSDK API
2. 阅读文档页面以识别哪个类型符合用户的要求。
3. 一旦知道类型名称，请返回并使用 `-Action members` 或 `-Action enums` 获取精确的本地签名。

**3. 读取 JSON 以选择正确的 API**

读取顶部结果中的文件路径。JSON 包含该命名空间中的所有类型——完整的成员、签名、参数、返回类型、枚举值。

读取并决定哪些类型和成员符合用户的要求。

**4. 查阅官方文档以获取上下文**

缓存仅包含签名——不包含描述或使用说明。对于解释、示例和备注，请在 Microsoft Learn 上查阅该类型：

| 命名空间前缀 | 文档基础 URL |
|-------------|--------------|
| `Windows.*` | `https://learn.microsoft.com/uwp/api/{完全限定的类型名称}` |
| `Microsoft.*`（WinAppSDK） | `https://learn.microsoft.com/windows/windows-app-sdk/api/winrt/{完全限定的类型名称}` |

例如，`Microsoft.UI.Xaml.Controls.NavigationView` 映射到：
`https://learn.microsoft.com/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.controls/navigationview`

**5. 使用 API 知识回答或编写代码**

---

### 查找 — “我知道 API，显示详细信息”

你已经知道（或怀疑）类型或命名空间名称。直接操作：

```powershell
# 获取已知类型的所有成员
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action members -TypeName "Microsoft.UI.Xaml.Controls.NavigationView"

# 获取枚举值
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action enums -TypeName "Microsoft.UI.Xaml.Visibility"

# 列出命名空间中的所有类型
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action types -Namespace "Microsoft.UI.Xaml.Controls"

# 浏览命名空间
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action namespaces -Filter "Microsoft.UI"
```

如果你需要 `-Action members` 显示之外的完整详细信息，请使用 `-Action search` 获取 JSON 文件路径，然后直接读取 JSON 文件。

---

### 其他命令

```powershell
# 列出缓存的已生成项目
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action projects

# 列出项目的 NuGet 包
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action packages

# 显示统计信息
.\.github\skills\winmd-api-search\scripts\Invoke-WinMdQuery.ps1 -Action stats
```

> 如果只缓存了一个项目，`-Project` 会自动选择。
> 如果存在多个项目，请添加 `-Project <名称>`（使用 `-Action projects` 查看可用名称）。
> 在扫描模式下，清单名称包含短哈希后缀以避免冲突；如果名称明确，可以传递不带后缀的基本项目名称。

## 搜索评分

搜索将类型名称和成员名称与你的查询进行评分：

| 分数 | 匹配类型 | 示例 |
|------|----------|------|
| 100 | 完全匹配 | `Button` → `Button` |
| 80 | 以...开头 | `Navigation` → `NavigationView` |
| 60 | 包含 | `Dialog` → `ContentDialog` |
| 50 | PascalCase 初始字母 | `ASB` → `AutoSuggestBox` |
| 40 | 多关键词 AND | `navigation item` → `NavigationViewItem` |
| 20 | 模糊字符匹配 | `NavVw` → `NavigationView` |

结果按命名空间分组。得分较高的命名空间会首先显示。

## 故障排除

| 问题 | 解决方法 |
|------|----------|
| “缓存未找到” | 运行 `Update-WinMdCache.ps1` |
| “已缓存多个项目” | 添加 `-Project <名称>` |
| “命名空间未找到” | 使用 `-Action namespaces` 列出可用命名空间 |
| “类型未找到” | 使用完全限定的名称（例如，`Microsoft.UI.Xaml.Controls.Button`） |
| NuGet 更新后过时 | 重新运行 `Update-WinMdCache.ps1` |
| 缓存存在于 git 历史记录中 | 将 `Generated Files/` 添加到 `.gitignore` |

## 参考

- [Windows 平台 SDK API 参考](https://learn.microsoft.com/uwp/api/) — `Windows.*` 命名空间的文档
- [Windows App SDK API 参考](https://learn.microsoft.com/windows/windows-app-sdk/api/winrt/) — `Microsoft.*` WinAppSDK 命名空间的文档
