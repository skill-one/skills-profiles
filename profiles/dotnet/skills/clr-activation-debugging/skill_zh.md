# CLR 激活调试

通过分析由 shim（mscoree.dll）生成的 CLR 激活日志（CLRLoad 日志），诊断 .NET Framework 运行时激活问题。这些日志记录了 shim 在选择和加载 CLR 版本时做出的每一个决策。

## 使用场景

- 进程完全无法加载 CLR（"找不到可用的运行时版本"）
- shim 选择错误的 CLR 版本（例如，选择 v2.0 而不是 v4.0）
- 出现意外的 .NET 3.5 按需功能（FOD）安装对话框
- 预期会出现 FOD 对话框，但实际上没有出现
- CLR v2 和 CLR v4 同时加载到同一个进程中，导致失败
- COM 对象因 shim 无法解析运行时而无法激活
- 传统托管 API（CorBindToRuntime）绑定到意外的版本

## 不适用场景

- **现代 .NET (CoreCLR / .NET 5+)** — 此技能仅涵盖 .NET Framework（mscoree.dll shim）
- **程序集绑定失败** — 使用 Fusion 日志（fuslogvw.exe），而不是 CLR 激活日志
- **CLR 加载后的运行时崩溃** — 激活成功；问题出在其他地方

## 背景

### shim 架构

.NET Framework shim 有两层结构：
- **mscoree.dll**（"外壳 shim"）— 面向公众的 DLL，是 CLR 托管 COM 对象的注册 `InprocServer32`，以及 `_CorExeMain`、传统 API 等的入口点
- **mscoreei.dll** — 实际的 shim 实现，其中包含运行时选择逻辑、日志记录和激活决策。mscoree.dll 会转发到 mscoreei.dll。

在读取日志时，FOD 命令行中的 `caller-name:mscoreei.dll` 反映了这一点 — 这是 mscoreei.dll 在执行工作。

### .NET 3.5 / v2.0.50727 版本映射

.NET 2.0、3.0 和 3.5 都共享相同的 CLR 运行时版本：**v2.0.50727**。"3.0" 和 "3.5" 发布是在 CLR v2.0 之上的库添加。在激活方面，它们都是 "v2.0.50727"。当 shim 解析到 v2.0.50727 或 FOD 提供安装 "NetFx3" 时，它正在安装 CLR v2.0 运行时（以及 3.0/3.5 库）。类似地，CLR v4.0（v4.0.30319）涵盖了从 4.0 到 4.8.x 的所有 .NET Framework 版本。

### 近期 Windows 上的 .NET 3.5 可用性

在近期 Windows 版本（Windows 11 Insider Preview Build 27965 及以后的平台发布）上，.NET Framework 3.5 **不再作为 Windows 可选组件（按需功能）** 提供。必须从独立的 MSI 进行安装。这意味着即使触发，FOD 对话框（`fondue.exe /enable-feature:NetFx3`）在这些系统上也不会成功。在 Windows 10 和 Windows 11 通过 25H2 时，FOD 仍然可用。.NET Framework 3.5 的支持将于 2029 年 1 月 9 日结束。

### shim HRESULT 代码

当 shim 失败时，它会在 `0x8013xxxx` 范围内返回特定的 HRESULT。这些是调用者（而不是激活日志本身，激活日志记录可读消息）看到的错误：

| HRESULT | 符号 | 含义 |
|---------|------|------|
| `0x80131700` | `CLR_E_SHIM_RUNTIMELOAD` | 无法找到或加载合适的运行时版本。**这是最常见的 shim 错误** — 这是调用者在 v4 仅机器上因限制传统激活而看到的情况。 |
| `0x80131701` | `CLR_E_SHIM_RUNTIMEEXPORT` | 找到运行时，但无法从中获取所需的导出或接口。 |
| `0x80131702` | `CLR_E_SHIM_INSTALLROOT` | 注册表中缺少或无效的 .NET Framework 安装根。 |
| `0x80131703` | `CLR_E_SHIM_INSTALLCOMP` | 安装的一个必需组件丢失。 |
| `0x80131704` | `CLR_E_SHIM_LEGACYRUNTIMEALREADYBOUND` | 已有其他运行时作为传统运行时绑定。尝试绑定到与已选择版本冲突的版本的传统 API。 |
| `0x80131705` | `CLR_E_SHIM_SHUTDOWNINPROGRESS` | shim 正在关闭，无法处理请求。 |

如果用户报告其中一个 HRESULT（尤其是 `0x80131700`），CLR 激活日志是正确的诊断工具。

## 前提条件

CLR 激活日志必须启用才能生成日志文件。如果用户还没有日志，请指示他们启用日志：

**通过环境变量（推荐 — 作用域限于当前会话）：**
```
set COMPLUS_CLRLoadLogDir=C:\CLRLoadLogs
```

**通过注册表（机器范围 — 影响所有 .NET Framework 进程）：**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\.NETFramework
  CLRLoadLogDir = "C:\CLRLoadLogs" (REG_SZ)
```

在 64 位系统上，如果涉及 32 位进程，也必须在 `Wow6432Node` 下设置。

> ⚠️ **日志目录必须已经存在。** shim 不会创建它。如果不存在，则不会写入日志，并且不会有错误或失败指示。

日志以 `{ProcessName}.CLRLoad{NN}.log`（NN = 00–99，每个进程实例一个）的形式写入。**日志必须在进程退出后才能读取** — 文件被保持打开状态。

捕获后，**删除环境变量或注册表键**以停止日志记录。

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|------|
| CLR 激活日志文件 | 是 | 一个或多个 `.CLRLoad*.log` 文件 |
| 症状描述 | 推荐 | 用户观察到的内容（FOD 对话框、错误运行时、失败等） |
| 预期行为 | 推荐 | 用户期望发生的情况 |

## 工作流程

### 第 1 步：加载参考材料

从包含此 `SKILL.md` 的目录（而不是用户的工位空间）解析捆绑路径。按以下顺序加载参考文件 — 它们包含详细的日志格式、决策流程和 CLSID 注册文档：

1. `references/log-format.md` — 日志行格式、字段和所有已知日志消息类型
2. `references/activation-flow.md` — shim 的运行时选择决策树
3. `references/com-activation.md` — COM（DllGetClassObject）激活的具体细节，CLSID 注册布局

如果直接读取失败，请列出此技能的 `references/` 目录一次，并在列出显示预期文件时重试。不要使用工作空间文件或文本搜索来定位技能安装。

如果一个或多个预期的参考文件不可用，尽可能使用已加载的参考，并使用以下内联知识来补充缺失的覆盖范围。在最终诊断中包含 `Reference coverage: reduced; unavailable: <paths>; used inline guidance for missing references.`，将 `<paths>` 替换为缺失的相对路径。

### 第 2 步：调查日志文件

在深入任何单个日志之前，先了解整体情况：

1. **列出所有日志文件** 并按进程名称分组 — 这显示了哪些可执行文件触发了 CLR 激活
2. **针对每个进程，扫描结果行：**
   - `Decided on runtime: vX.Y.Z` — 成功解析
   - `ERROR:` — 解析失败
   - `Launching feature-on-demand` — 显示了 FOD 对话框
   - `Could have launched feature-on-demand` — FOD 会触发，但被抑制
   - `V2.0 Capping is preventing consideration` — 由于限制，跳过了 v4+
```
grep -l "ERROR:\|Launching feature-on-demand\|Could have launched" *.log
grep -c "Launching feature-on-demand" *.log
```

3. **构建摘要表：**

| 进程 | 日志文件 | 结果 | 选择的运行时 | FOD? |
|------|----------|------|--------------|------|

### 第 3 步：分析有问题的日志

对于每个具有意外结果的日志文件，跟踪完整的激活流程。从上到下读取日志并识别：

> ⚠️ **嵌套日志条目：** shim 的内部调用可以触发已在激活序列中记录的额外日志条目。例如，一个 `DllGetClassObject` 调用可能会内部调用 `ComputeVersionString`，它调用 `FindLatestVersion`，每个都会生成日志行。当 FOD 检查运行时（"Checking if feature-on-demand installation would help"）时，它会重新运行版本计算 — 在同一个激活中生成第二个 `ComputeVersionString` 块。不要将这些嵌套/重入条目误认为是单独的激活尝试。

#### 3a. 入口点

第一个 `FunctionCall:` 或 `MethodCall:` 行告诉您激活是如何触发的：

| 入口点 | 含义 |
|--------|------|
| `_CorExeMain` | 托管 EXE 启动 — 二进制文件是 .NET 程序集 |
| `DllGetClassObject. Clsid: {guid}` | COM 激活 — 某些东西 CoCreated 通过 mscoree.dll 路由的 COM 类 |
| `ClrCreateInstance` | 现代（v4+）托管 API |
| `CorBindToRuntimeEx` | 传统（v1/v2）托管 API — 将进程绑定到一个运行时 |
| `ICLRMetaHostPolicy::GetRequestedRuntime` | 基于策略的托管 API（通常在调用其他入口点后内部调用） |
| `LoadLibraryShim` | 传统 API 通过名称加载框架 DLL |

#### 3b. 输入参数

在入口点之后，日志会转储版本计算的输入：

- **`IsLegacyBind`**: 这是传统（v4 之前）激活路径吗？如果为 1，shim 使用单运行时"传统"的视角。传统 API（`CorBindToRuntimeEx`、`DllGetClassObject` 用于传统 COM、`LoadLibraryShim` 等）设置此值。
- **`IsCapped`**: 如果为 1，shim 的向前滚动语义限制在 Whidbey（v2.0.50727）— 在枚举安装的运行时时，它**不会**考虑 v4.0+。这是使 v4 安装无影响（传统代码路径继续表现得好像 v4 不存在）的机制。在 v4 仅机器上没有 .NET 3.5 时，限制的枚举看到**没有任何运行时**。限制**不会**阻止通过显式提供特定 v4 版本字符串（例如，通过 `CorBindToRuntimeEx("v4.0.30319", ...)` 或通过配置使用 `useLegacyV2RuntimeActivationPolicy`）加载 v4+。
- **`SkuCheckFlags`**: 控制 SKU（版本）兼容性检查。
- **`ShouldEmulateExeLaunch`**: 是否为了策略目的假装这是一个 EXE 启动。
- **`LegacyBindRequired`**: 是否严格要求传统绑定。

#### 3c. 配置文件处理

查找配置文件解析结果：

- `Parsing config file: {path}` — shim 正在查找 `.config` 文件
- `Config File (Open). Result:00000000` — 配置文件找到并成功打开
- `Config File (Open). Result:80070002` — **未找到配置文件**（ERROR_FILE_NOT_FOUND 的 HRESULT）
- `Found config file: {path}` — 成功读取配置
- `UseLegacyV2RuntimeActivationPolicy is set to {0|1}` — 是否存在 `<startup useLegacyV2RuntimeActivationPolicy="true">`。当为 1 时，所有运行时都被视为传统代码路径的候选者 — 意味着传统 shim API 可以枚举并选择 v4+。这可以与多个 `<supportedRuntime>` 条目、其他配置选项一起使用，甚至在没有 `<supportedRuntime>` 条目的情况下使用（在这种情况下，传统 API 可以简单地枚举 v4）。**副作用：** 关闭预 v4 运行时的 in-proc SxS — 将它们锁定在进程之外。
- `Config file includes SupportedRuntime entry. Version: vX.Y.Z, SKU: {sku}` — 在配置中找到的每个 `<supportedRuntime>` 条目

**关键洞察：** 如果进程没有配置文件并且正在进行限制传统绑定，shim 没有可以引导它到 v4 的东西。它会枚举安装的运行时（限制为 ≤v2.0），如果没有安装 3.5，就会失败。这是设计如此 — v4 故意对这些代码路径不可见，以保持 v4 安装无影响。

#### 3d. 版本解析

- `Installed Runtime: vX.Y.Z. VERSION_ARCHITECTURE: N` — 机器上安装的运行时
- `{exe} was built with version: vX.Y.Z` — 二进制文件的 PE 头中的版本（仅限托管程序集；原生 EXE 不会有这个）
- `Using supportedRuntime: vX.Y.Z` — shim 从配置的 `<supportedRuntime>` 列表中选择了一个版本
- `FindLatestVersion is returning the following version: vX.Y.Z ... V2.0 Capping: {0|1}` — 基于策略的最新版本搜索的结果
- `Default version of the runtime on the machine: vX.Y.Z` 或 `(null)` — shim 最终确定；`(null)` 意味着未找到
- `Decided on runtime: vX.Y.Z` — **最终决策** — 这将是加载的版本

#### 3e. 失败和 FOD 路径

如果版本解析失败：

1. `ERROR: Unable to find a version of the runtime to use` — shim 没有找到合适的运行时
2. `SEM_FAILCRITICALERRORS is set to {value}` — 检查进程错误模式：
   - **值 0**：允许错误对话框和 FOD
   - **非零**（任何位设置，通常 0x8001）：抑制错误对话框和 FOD。`SEM_FAILCRITICALERRORS` 标志（0x0001）是从父进程继承的。
3. `Checking if feature-on-demand installation would help` — shim 重新运行版本计算，看看安装 .NET 3.5 是否会解决请求
4. 然后：
   - `Launching feature-on-demand installation. CmdLine: "...\fondue.exe" /enable-feature:NetFx3` — **显示 FOD 对话框**
   - `Could have launched feature-on-demand installation if was not opted out.` — **FOD 被抑制**，因为 `SEM_FAILCRITICALERRORS` 被设置

#### 3f. 单个进程中多次激活

一个日志可以包含多个激活序列。每个序列都以新的 `FunctionCall:` 或 `MethodCall:` 条目开始。一个常见模式：

1. 首次通过 `ClrCreateInstance` / `GetRequestedRuntime` 激活 → 成功（通过配置加载 v4.0）
2. 第二次通过 `DllGetClassObject`（COM）激活 → 传统绑定，限制 → 失败

这发生在原生 EXE（如 link.exe 或 mt.exe）成功加载 CLR 以执行其主要工作后，一个二级 COM 激活请求（例如，用于 diasymreader）触发一个单独的传统解析，该解析无法找到 v2.0。

### 第 4 步：检查系统状态（如果需要）

当日志分析指向注册或配置问题时，检查：

**CLSID 注册**（用于 COM 激活问题）：
```powershell
# 检查 CLSID 条目
Get-ItemProperty 'Registry::HKCR\CLSID\{guid}'
Get-ItemProperty 'Registry::HKCR\CLSID\{guid}\InprocServer32'
Get-ChildItem 'Registry::HKCR\CLSID\{guid}\InprocServer32' | ForEach-Object {
    Write-Output "--- $($_.PSChildName) ---"
    Get-ItemProperty "Registry::$($_.Name)"
}
```

`InprocServer32` 下键值：
- `(Default)` 应该是 `mscoree.dll`，用于 CLR 托管的 COM 对象
- **版本子键**（例如，`2.0.50727`、`4.0.30319`）指示哪些运行时版本注册了此 CLSID
- **`ImplementedInThisVersion`** 在版本子键下意味着该运行时版本原生实现了 COM 类（不是通过托管互操作）
- **`Assembly`** 和 **`Class`** 在版本子键下指示托管 COM 互操作注册
- **`RuntimeVersion`** 在版本子键下指定应托管此对象的 CLR 版本

**安装的运行时：**
```powershell
Get-ChildItem 'Registry::HKLM\SOFTWARE\Microsoft\.NETFramework\policy'
```

**进程错误模式**（为什么 FOD 触发/未触发）：
`SEM_FAILCRITICALERRORS` 标志是从父进程继承的。如果构建系统或脚本设置了它（或调用 `SetErrorMode`），所有子进程都会继承它。

### 第 5 步：诊断和报告

生成清晰的诊断，涵盖：

1. **发生了什么** — 哪些进程出现激活问题以及症状是什么
2. **为什么会发生** — 跟踪 shim 中导致结果的特定决策路径
3. **什么控制了行为** — 确定决定结果的特定输入（配置文件存在/缺失、错误模式、CLSID 注册、限制状态）
4. **什么发生了变化**（如果适用） — 如果用户说行为发生了变化，确定可能发生变化的输入（来自父进程的错误模式、配置文件、CLSID 注册、安装的运行时）

## 常见场景

### 意外的 FOD 对话框

**模式：** `DllGetClassObject` → `IsCapped: 1` → 没有配置文件 → `(null)` → `SEM_FAILCRITICALERRORS: 0` → FOD 触发

**根本原因：** 原生 EXE 正在通过 mscoree.dll 注册的 CLSID 执行 COM 激活。这会采用传统代码路径，该路径限制在 v2.0。没有配置文件（并且没有 `useLegacyV2RuntimeActivationPolicy`），v4 对此代码路径不可见。在没有 .NET 3.5 的机器上，没有可见的运行时，并且 `SEM_FAILCRITICALERRORS` 未设置，FOD 对话框会触发。

**关键问题：** 为什么 `SEM_FAILCRITICALERRORS` 改变了？它是从父进程继承的。不同的启动方法（脚本与直接调用、不同的构建系统）产生不同的错误模式。底层的限制传统绑定在 v4 仅机器上的失败始终存在 — 只是 `SEM_FAILCRITICALERRORS` 控制它是否表现为可见对话框或静默失败。

### 选择错误的运行时

**模式：** 配置中列出了多个版本 `supportedRuntime`；shim 选择安装的第一个版本。如果 v2.0 列在第一位，而 .NET 3.5 已安装，v2.0 将获胜，即使 v4.0 也可用。

**关键洞察：** 配置 `<supportedRuntime>` 条目按顺序评估。第一个安装的匹配项获胜。

### 同时加载 v2 和 v4

**模式：** 同一个进程的日志中包含多个激活序列 — 一个绑定 v4，另一个绑定 v2（反之亦然）。CLR v2 和 v4 在同一个进程中并排加载是受支持的，但可能会导致共享状态问题。

**关键洞察：** 在同一个日志文件中查找具有不同版本的多个 `Decided on runtime` 行。

### 传统运行时已绑定

**模式：** 传统代码路径在进程早期成功（例如，使用 `CorBindToRuntimeEx` 指定 v4 版本，或配置使用 `useLegacyV2RuntimeActivationPolicy`）。这会将传统运行时设置为 v4.0。所有后续的传统激活 — 包括限制的 COM 激活，否则会失败 — 都会通过重用已绑定的传统运行时而静默成功。

**关键洞察：** 进程内激活的顺序很重要。如果 v4.0 首先绑定作为传统运行时，限制的 COM 激活会工作。如果限制的 COM 激活首先发生（在绑定任何传统运行时之前），它将失败。这意味着行为可能取决于哪个组件首先激活 — 并发代码中的竞争条件可以改变结果。

## 常见陷阱

| 陷阱 | 正确方法 |
|------|----------|
| 假设 `IsCapped: 1` 意味着 v4.0 永远无法加载 | 限制仅限制向前枚举。v4.0 仍然可以加载，如果：显式传递特定版本字符串、配置具有 `useLegacyV2RuntimeActivationPolicy="true"` 与 `<supportedRuntime version="v4.0"/>`、或传统运行时已绑定到 v4+ |
| 认为 capping 是错误的或是有 bug | capping 是有意为之 — 它使 v4 安装无影响。在 v4 仅机器上，传统代码路径正确地看到没有运行时。这是按设计运行的。 |
| 假设 FOD 是按进程控制的 | `SEM_FAILCRITICALERRORS` 是从父进程继承的。父级中的更改（构建系统、脚本、外壳）会改变所有子进程的行为。 |
| 只查看日志中的第一个激活 | 一个日志可以包含多个独立的激活序列。有问题的通常是二次 COM 激活，而不是初始的 CLR 加载。 |
| 假设缺失配置文件是无害的 | 对于执行 COM 激活的原生 EXE（使用传统/限制绑定），配置文件（带有 `useLegacyV2RuntimeActivationPolicy`）是使传统代码路径看到 v4.0 的主要方式。没有配置 = 限制 = v4 不可见。 |
| 添加 `<supportedRuntime>` 而不使用 `useLegacyV2RuntimeActivationPolicy` | 没有 `useLegacyV2RuntimeActivationPolicy="true"`，通过配置向前滚动到 v4 适用于主 EXE 加载，但传统代码路径（COM 激活、P/Invoke 到 mscoree.h API）仍然限制在 v2.0。两者都需要使传统代码路径工作。 |
| 不理解设置 `useLegacyV2RuntimeActivationPolicy` 的权衡而设置它 | 此属性关闭 in-proc SxS — 它将预 v4 运行时锁定在进程之外。这通常适用于构建工具，但应考虑需要同时托管 v2 和 v4 的应用程序。 |

## 验证

在交付诊断之前，验证：

- [ ] 所有包含错误或 FOD 触发的日志文件都被分析（不只是第一个）
- [ ] 每个有问题的激活的入口点都已识别
- [ ] 每个激活序列的限制和传统绑定状态都已记录
- [ ] 检查了配置文件的缺失/存在
- [ ] 记录了 FOD 相关问题的 SEM_FAILCRITICALERRORS 状态
- [ ] 单个日志内的多次激活被单独跟踪
- [ ] 诊断解释了特定的决策路径，而不仅仅是结果
