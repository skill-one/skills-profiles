## 性能注意事项
- 花足够的时间彻底完成这项工作。
- 质量比速度更重要。

## 在编辑器中运行 C#

以下每一步中，读取或写入 Player Setting 的操作都在 Unity CLI 的实时编辑器中运行。**`unity-cli` 技能负责带你到达那里**——安装 CLI、确认连接的编辑器、添加项目的 `com.unity.pipeline` 包、区分真正的缺失编辑器与处于安全模式的编辑器，以及发现编辑器的命令目录。首先遵循它；不要在这里重新推导任何内容。

有两件事它无法为你知道：

- **你需要 `eval`，而不仅仅是可访问的编辑器**。确认它在目录中显示。它的存在取决于 Pipeline 包版本，而不是 CLI，因此健康的安装仍然可能缺少它——如果它丢失了，请说明并停止。
- **Player Setting 可以在紧急情况下从 `ProjectSettings/ProjectSettings.asset` 中读取，但不要以这种方式写入它们**。序列化的名称与 API 名称不匹配，其中几个这些设置是按构建目标的，并且手动编辑的值与构建实际使用的值无声地不一致。无法访问的编辑器是写入步骤的停止点。

使用 `unity command eval --code '<snippet>'` 运行 C#。`unity command` 默认超时时间为 30 秒。

### 将 C# 传递给 `eval`

`eval` 编译一个**语句块，而不是文件**。有两个后果，都是编译错误，而不是警告：

- **没有 `using` 指令**。编译器将 `using UnityEditor;` 读取为资源释放语句并拒绝它（`CS0210`）。
- **类型必须完全限定**。裸 `PlayerSettings` 无法解析（`CS0246`），并且裸 `Object` 与 `object` 模棱两可（`CS0104`）。

### 读取此技能审核的设置

一个调用返回整个 Pre-Flight 情景。与 Unity 6000.5.7f1 进行了验证：

```csharp
var target = UnityEditor.Build.NamedBuildTarget.WebGL;
var w = new System.Collections.Generic.List<string>();
w.Add($"activeBuildTarget={UnityEditor.EditorUserBuildSettings.activeBuildTarget}");
w.Add($"compressionFormat={UnityEditor.PlayerSettings.WebGL.compressionFormat}");
w.Add($"decompressionFallback={UnityEditor.PlayerSettings.WebGL.decompressionFallback}");
w.Add($"stripEngineCode={UnityEditor.PlayerSettings.stripEngineCode}");
w.Add($"managedStrippingLevel={UnityEditor.PlayerSettings.GetManagedStrippingLevel(target)}");
w.Add($"il2cppCodeGeneration={UnityEditor.PlayerSettings.GetIl2CppCodeGeneration(target)}");
w.Add($"apiCompatibilityLevel={UnityEditor.PlayerSettings.GetApiCompatibilityLevel(target)}");
w.Add($"exceptionSupport={UnityEditor.PlayerSettings.WebGL.exceptionSupport}");
w.Add($"debugSymbolMode={UnityEditor.PlayerSettings.WebGL.debugSymbolMode}");
w.Add($"dataCaching={UnityEditor.PlayerSettings.WebGL.dataCaching}");
w.Add($"wasm2023={UnityEditor.PlayerSettings.WebGL.wasm2023}");
w.Add($"initialMemorySize={UnityEditor.PlayerSettings.WebGL.initialMemorySize}");
w.Add($"maximumMemorySize={UnityEditor.PlayerSettings.WebGL.maximumMemorySize}");
w.Add($"memoryGrowthMode={UnityEditor.PlayerSettings.WebGL.memoryGrowthMode}");
w.Add($"targetFrameRate={UnityEngine.Application.targetFrameRate}");
w.Add($"vSyncCount={UnityEngine.QualitySettings.vSyncCount}");
return string.Join("\n", w);
```

**三个 API 名称需要正确**，因为明显的拼写不存在并且无法编译：

| 设置 | 正确形式 | 不存在 |
|---|---|---|
| 管理剥离级别 | `PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.WebGL)` | `PlayerSettings.managedStrippingLevel` |
| Wasm 代码优化 | `UnityEditor.WebGL.UserBuildSettings.codeOptimization` | `PlayerSettings.WebGL.codeOptimization`，`PlayerSettings.WebGL.optimizationLevel` |
| IL2CPP 代码生成 | `PlayerSettings.GetIl2CppCodeGeneration(NamedBuildTarget.WebGL)` | 一个裸属性 |

`UserBuildSettings` 位于 WebGL 构建支持模块中，因此它仅在安装该模块时解析。与其他设置分开调用它，并将解析失败视为“Web 模块未安装”，而不是错误的片段。

**`codeOptimization` 是这里唯一一个不在项目文件中的设置**。它持久化到 `Library/EditorUserBuildSettings.asset`，而 `Library/` 由每个标准的 Unity `.gitignore` 忽略，因此此值是按机器的，并且不会随行：队友和 CI 都不会继承它。有两个后果。通过 API 读取它，不要在 `ProjectSettings/ProjectSettings.asset` 中查找它——即使在成功应用时，它也缺失在那里，所以它的缺失不是失败。如果发布构建在 CI 中运行，则在构建步骤中应用它，而不是假设存储库包含它。

### 应用设置

此技能中的大多数写入都是单个批处理，并且 [资源/WebOptimizer.cs](resources/WebOptimizer.cs) 已经是那个批处理。它声明了一个带有 `[MenuItem]` 的类，因此它是一个**项目文件，而不是 `eval` 输入**——类声明不能扁平化为语句块。将其保存到 `Assets/Editor/` 下，让 Unity 编译，然后在一行中调用它：

```csharp
UnityEditor.EditorApplication.ExecuteMenuItem("Tools/Apply Web Release Settings");
```

保留它的 `using` 指令；它们在文件中是正确的。对于一次性更改——单个质量级别、帧率翻转——一个内联 `eval` 语句就足够了。

### 从磁盘而不是你刚刚写入的对象进行验证

**在同一会话中应用设置并读取它并不能证明任何东西**。Player Setting 是内存对象，直到它们被保存，所以每个读取回值都返回你刚刚分配的值，无论它是否到达了 `ProjectSettings/ProjectSettings.asset`。跳过保存的运行报告成功，并且当编辑器会话结束时整个更改都消失了。这是观察到的，而不是理论化的：一个运行应用了所有内容，读取回 Brotli / High / None，说它完成了，磁盘上的文件从未改变。

所以，在每次写入后：

1. **保存**。`UnityEditor.AssetDatabase.SaveAssets()`。`WebOptimizer.cs` 现在会自己这样做；内联 `eval` 写入必须显式地这样做。
2. **读取回值并报告它们**。不是“应用成功”，而是实际值，这样用户可以看到存储的内容。`WebOptimizer.cs` 记录所有九个。
3. **对于任何按构建目标，读取目标**。其中几个这些设置每个目标都存在一次，所以一个值可以是针对一个目标正确的，而正在构建的目标未设置。

在反向文件编辑路由中也存在同样的陷阱：手动编辑的 `ProjectSettings.asset` 读取良好，而正在运行的编辑器和构建仍然使用旧值。在保存后重新导入后进行验证可以捕获两者。

**不要尝试以批处理模式重现已知问题**。使用 `-quit` 调用的批处理编辑器在退出时保存设置，所以未保存的写入仍然存在，运行看起来是正确的。保存和非保存版本的脚本都在 `-quit` 下通过。只有在实时编辑器会话中才会出现此错误，这也是在发现错误的地方。从绿色的批处理运行中得出保存是不必要的结论，这是从无法看到缺陷的测试中得出的错误结论。

## 0. 预飞

1. **确认 WebGL 构建目标**：使用上述 Pre-Flight 片段读取 `EditorUserBuildSettings.activeBuildTarget`——必须是 `WebGL`；如果不是，请警告用户。
2. **读取压缩和剥离设置**：使用上述 Pre-Flight 片段读取 `compressionFormat`，`decompressionFallback`，`stripEngineCode` 和受管理的剥离级别。注意剥离级别是 `PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.WebGL)`——没有 `PlayerSettings.managedStrippingLevel` 属性。
3. **读取异常和优化设置**：使用上述 Pre-Flight 片段读取 `PlayerSettings.WebGL.exceptionSupport`。对于 Wasm 代码优化级别使用 `UnityEditor.WebGL.UserBuildSettings.codeOptimization`——`PlayerSettings.WebGL.codeOptimization` 和 `optimizationLevel` 的拼写不存在并且无法编译。
4. **读取帧率设置**：使用上述 Pre-Flight 片段读取 `Application.targetFrameRate` 和 `QualitySettings.vSyncCount`。
5. **读取其他 Player 设置**：使用上述 Pre-Flight 片段读取 `PlayerSettings.WebGL.dataCaching`，`PlayerSettings.WebGL.debugSymbolMode`，`PlayerSettings.WebGL.maximumMemorySize` 和 `PlayerSettings.GetApiCompatibilityLevel`。
6. 只有在确认了压缩、剥离、帧率和 Player 设置后才能继续。

## 1. 评估当前状态

1. **检查构建报告**：指示用户在构建后打开 `Window > General > Build Report` 并识别最大的资源和代码大小贡献者。
2. **验证服务器配置**：要求用户确认托管服务器是否发送 `Content-Encoding: br`（Brotli）或 `Content-Encoding: gzip` 标头，以及是否为 `.wasm` 文件设置了 `Content-Type: application/wasm`。
3. **检查帧率配置**：使用上述 Pre-Flight 片段确认 `Application.targetFrameRate`——应为 Web 的 `-1`（让浏览器驱动）。
4. **检查内存设置**：使用上述 Pre-Flight 片段读取 `PlayerSettings.WebGL.initialMemorySize` 和 `PlayerSettings.WebGL.memoryGrowthMode`。
5. 在提出建议之前报告发现结果。

## 2. 了解请求

| 用户说 | 默认解释 |
|-----------|----------------------|
| "构建太大" / "下载太慢" | 剥离引擎代码开启；管理剥离级别高；磁盘大小 + LTO；Brotli |
| "解压缩回退" / "启动缓慢" | 解压缩回退关闭；修复服务器正确发送 Content-Encoding |
| "Chrome 中卡顿" / "Safari 中卡顿" | 在浏览器开发者工具中分析；Safari 在 60 fps 上限制 |
| "浏览器中电池消耗过多" | 静态屏幕上开启 OnDemandRendering；`targetFrameRate = -1` |
| "异常太大" | 发布版无异常；如果浏览器基线允许，则使用 Wasm 2023 异常 |
| "设置 CDN" | Addressables 远程组 + CDN 上的 Brotli/Gzip |
| "WebAssembly 2023" | 当浏览器基线支持时启用它——更小更快 |
| "内存增长缓慢" | 将初始内存大小调整为峰值估计；使用几何增长模式 |
| "KTX" / "Basis Universal" / "未知 GPU 的纹理格式" | KTX2 与 Basis Universal；ETC1S 用于大小，UASTC 用于质量 |
| "剥离未使用的代码" / "删除未使用的包" | Web 剥离工具 + 删除未使用的包 + 着色器剥离 |
| "Web 的质量设置" | 质量级别为 Very Low 或 Low；较低质量 = 更快的加载 |
| "着色器变体太多" | 图形设置：自动光照/雾模式；剥离实例化 + BRG 变体；审核 Always Included Shaders |
| "视频无法播放" / "音频问题" | 视频：仅 URL 或 StreamingAssets；音频：Web 上无 AudioEffects，使用 Mono，压缩 |
| "分析器符号" / "无法读取 Wasm 堆栈" | 通过构建处理程序或 emscriptenArgs 嵌入分析器符号 |
| "iOS崩溃" / "Safari 内存" | iOS 内存限制；将 Initial Memory Size 设置为高，而不是增长；Gigacage 2GB 限制（iOS 18 之前） |

## 3. Web 构建优化工作流

### 重要提示：一键优化脚本

**始终提供为用户生成此脚本的选项**。Unity 的官方 Web 优化文档提供了一个单编辑器菜单脚本，一次应用所有建议的发布设置。将其放置在 `Assets/Editor/WebOptimizer.cs` 中——请参阅 [资源/WebOptimizer.cs](resources/WebOptimizer.cs) 获取模板。

根据用户的项目需求调整脚本（例如，如果他们使用 `try/catch`，请保留异常，将 Brotli 切换为 HTTP 托管）。此脚本是一个新 Web 项目的最有影响力的操作——它可以防止遗漏设置。

### Player 设置审核

通过 `eval` 验证和设置这些值：

| 设置 | 发布建议 |
|---|---|
| **压缩格式** | **Brotli**（HTTPS 托管）；HTTP 的 Gzip |
| **解压缩回退** | **关闭**（当服务器配置正确时） |
| **剥离引擎代码** | **开启** |
| **管理剥离级别** | **高**（发布）/ 中等（开发） |
| **代码优化** | **磁盘大小与 LTO**（发布）/ 构建时间（开发） |
| **WebAssembly 语言功能** | **2023**（如果浏览器基线允许） |
| **启用异常** | **无**（最小）；如果需要 `try/catch`，则显式抛出 |
| **初始内存大小** | 调整到峰值估计；太小会导致昂贵的增长 |
| **内存增长模式** | **几何** |
| **API 兼容性级别** | **.NET Standard 2.1**——比 .NET Framework 更小 |
| **IL2CPP 代码生成** | **优化大小**——在轻微运行时成本的情况下生成更小的 Wasm |
| **调试符号** | **发布时关闭**；仅开发构建才开启 |
| **数据缓存** | **开启**——将资产数据缓存到浏览器 IndexedDB 中，以便更快地重复加载 |
| **剥离未使用的网格组件** | **开启**——删除未使用的顶点属性 |
| **最大内存大小** | **2048 MB** 默认；复杂 3D 可达 4096（Firefox 和 Chrome < 119 在 2048 以上存在问题） |
| **vSyncCount** | 0（浏览器处理节拍） |
| **targetFrameRate** | -1（使用 `requestAnimationFrame`） |

### 压缩和服务器配置

| 压缩 | 使用场景 | 备注 |
|---|---|---|
| **Brotli** | HTTPS 或 localhost | 最佳比例；浏览器仅在接受安全上下文的情况下接受 |
| **Gzip** | HTTP 交付，传统 CDN | 通用 |
| **无** | 本地开发 / file:// | 最大的负载；不要发布 |

配置服务器以：
- 使用 `Content-Encoding: br` 交付 `.br` 文件。
- 使用 `Content-Encoding: gzip` 交付 `.gz` 文件。
- 为 `.wasm` 设置 `Content-Type: application/wasm`，为 `.js` 设置 `application/javascript`。
- 启用 HTTP/2 或 HTTP/3 以并行化块获取。

如果托管方无法注入 `Content-Encoding`：将 **Decompression Fallback = On** 作为后备仅使用——它添加 ~150 KB JS 并减慢启动。

### 异常处理

| 设置 | 构建大小 | 使用 |
|---|---|---|
| **无** | 最小 | 发布构建，其中未捕获的异常可以接受 |
| **显式抛出** | 适中 | 默认用于捕获异常的项目 |
| **完整** | 最大，最慢 | 很少需要；避免用于发布 |

Wasm 2023 引入了一种更便宜的异常模型；当浏览器目标支持时，从显式抛出（遗留）切换到 Wasm 异常可以减少大小和成本。

### 删除未使用的资源

三个类别用于减少构建大小：

**1. 未使用的包**——检查 `Packages/manifest.json` 和包管理器 **在项目中** 和 **内置** 视图。删除或禁用项目未使用的包。如果未使用，Input System 包是一个显著的大小贡献者。

**2. 着色器剥离**——在 `Edit > Project Settings > Graphics` 中配置：

| 设置 | 建议 |
|---|---|
| **光照模式** | 自动（剥离未使用的光照着色器变体） |
| **雾模式** | 自动（剥离未使用的雾着色器变体） |
| **实例化变体** | 剥离未使用 |
| **批处理渲染器组变体** | 剥离所有（如果 BRGs 未使用） |
| **始终包含的着色器** | 审核并删除任何项目未引用的着色器 |

剥离后测试——确保未引用的着色器未被删除。

**3. Web 剥离工具**（`com.unity.web.stripping-tool`）——分析 WebAssembly 二进制文件并识别未使用的 Unity 引擎子模块（例如，在仅 2D 的游戏中 3D 图形）。通过包管理器安装，分析构建，然后配置要排除哪些子模块。可以产生比单独的 Managed Stripping Level 实现更大的大小减少。

### Web 的质量设置

较低的质量级别可以减少加载时间并提高运行时性能。通过 `Edit > Project Settings > Quality` 设置：

- 将默认 Web 质量级别设置为 **Very Low** 或 **Low**。
- 使用 `eval` 设置它：`UnityEngine.QualitySettings.SetQualityLevel(0, true);` 其中 0 = Very Low。
- 考虑创建一个 Web 特定的质量级别，禁用在浏览器中不需要的功能（实时阴影、后期处理效果、高粒子数）。

### Web 上的帧率

- 使用 `eval` 设置它：`UnityEngine.Application.targetFrameRate = -1;` — 让浏览器使用 `requestAnimationFrame`。
- 注意：**Safari 在 WebGL 中限制为 60 fps**；高刷新目标不适用。
- 使用 `OnDemandRendering.renderFrameInterval` 在静态/空闲屏幕上降低到 5–10 fps 以节省电池。

### KTX / Basis Universal 纹理

KTX2 与 Basis Universal 超压缩发送一个纹理文件，在加载时转换为浏览器设备（桌面上的 BC7，移动设备上的 ASTC，旧 Android 上的 ETC2）的最佳 GPU 格式。这避免了为每个 GPU 家族发送单独的纹理变体——对于 Web 来说，这是至关重要的，因为目标硬件是未知的。

| 主题 | 指导 |
|---|---|
| **包** | 通过包管理器安装 `com.unity.cloud.ktx`（KtxUnity） |
| **何时使用** | 通过 Addressables 或资产包加载的运行时纹理，用于未知 GPU 目标 |
| **何时不使用** | 烘焙到玩家构建中的纹理——Unity 在构建时已经选择了正确的格式 |
| **超压缩** | 使用 **ETC1S** 获取最小大小（有损，适合漫反射/高光）；**UASTC** 获取更高质量（接近无损，更好用于法线/UI） |
| **编码** | 使用 `toktx` 或 `basisu` CLI 离线编码；不要在运行时编码 |
| **线性数据** | 在编码法线图、掩码或数据纹理时使用 `--assign_oetf linear` 以避免不正确的 sRGB 转换 |
| **Mip maps** | 在编码时生成 Mips（`--genmipmap`）——浏览器端的 Mip 生成很昂贵 |
| **加载** | 使用 `KtxTexture.LoadFromStreamingAssets` 或通过 UnityWebRequest 加载字节并调用 `KtxTexture.LoadFromBytes` |
| **内存** | 转换后的纹理是标准 GPU 纹理；内存成本等于目标格式，而不是 KTX2 文件大小 |
| **方向** | 始终包含 `--lower_left_maps_to_s0t0` 以匹配 Unity 的 UV 习惯 |

**`toktx` CLI 示例**：请参阅 [资源/toktx-examples.sh](resources/toktx-examples.sh) 获取涵盖漫反射（ETC1S）、法线/细节（UASTC）、ICC 配置文件错误和线性数据的命令。

### Web 流式传输

- 使用 Addressables 与托管在具有 Brotli / Gzip 的 CDN 上的 **远程组**。
- 避免将整个游戏捆绑到初始下载中；按需流式传输关卡。
- 目标 < 30 MB 初始下载以实现“即时播放”；关卡数据随后。
- 对于针对混合 GPU 硬件的流式传输纹理，请优先选择 KTX2 套件，而不是每个平台的变体——一个套件可以服务于所有浏览器。

### Web 构建分析

| 工具 | 使用 | 备注 |
|---|---|---|
| **Chrome DevTools > Performance** | CPU 火焰图；主线程分析 | 默认首先用于 WebGL 卡顿；检查 Wasm 调用堆栈 |
| **Chrome DevTools > Memory** | 堆快照；分配时间线 | 查找 JS/Wasm 内存泄漏；比较加载前后的快照 |
| **Firefox Profiler** | 跨平台；可共享的 URL；原生 + Wasm 视图 | 在某些情况下比 Chrome 更好的 Wasm 符号化；可用于团队审查的可共享配置文件 URL |
| **Safari Web Inspector** | iOS Safari 和 macOS Safari 调试 | 对于 Safari 特定问题来说是必需的；WebGL/Wasm 运行时与 Chromium 不同——某些 GLSL 构造的处理方式不同 |
| **Unity Profiler over WebSocket** | 连接到开发构建；标准标记 | 用于 Unity 端标记（GC、渲染、脚本）；不会捕获浏览器端的开销 |

**症状 → 工具快速参考:**

| 症状 | 第一线工具 | 第二线工具 |
|---|---|---|
| WebGL 卡顿 / 卡顿 | Chrome DevTools > Performance | Firefox Profiler |
| 内存随时间增长 | Chrome DevTools > Memory | Unity 内存分析器（WebSocket） |
| 初始加载缓慢 | Chrome DevTools > Network | 构建报告检查器 |
| Safari 仅有的渲染问题 | Safari Web Inspector | 与 Chrome DevTools 进行比较 |

**嵌入分析器符号**——浏览器分析器默认显示损坏的 Wasm 函数名称。为了在 Chrome/Firefox 火焰图中获得可读的 C# 方法名称，可以启用 `Player Settings > Publishing > Debug Symbols` 用于开发构建，或者添加一个构建处理程序：

```csharp
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;

public class WebProfilingBuildProcessor : IPreprocessBuildWithReport
{
    public int callbackOrder => 0;
    public void OnPreprocessBuild(BuildReport report)
    {
        PlayerSettings.SetAdditionalIl2CppArgs("--compiler-flags=--profiling-funcs");
    }
}
```

**Emscripten 内建分析器**——通过 `PlayerSettings.WebGL.emscriptenArgs` 一次启用一个：

| 标志 | 它显示的内容 |
|---|---|
| `--cpuprofiler` | 浏览器中的 CPU 分析器覆盖 |
| `--memoryprofiler` | 可视化内存映射（白色=已分配未使用，粉色=栈，蓝色=动态，绿色=碎片化） |
| `--threadprofiler` | 线程活动分析器 |

**GPU 调试**——Web 上不支持帧调试器。使用 [Spector.js](https://spector.babylonjs.com/) 作为基于浏览器的替代方案——它捕获绘制调用和 WebGL 状态。

**Firefox `about:memory`**——在 Firefox 中输入 `about:memory` 作为 URL，点击 Measure 查看每个选项卡的细分：WASM 代码大小，WASM 堆，.data 文件，Web 音频。注意 WASM 堆 > 300 MB（崩溃风险，尤其是在 iOS Safari 上）。

编辑器 Play Mode 不代表浏览器运行时；始终在浏览器中测量。Chrome 和 Safari 的 GC 和 JIT 行为不同——测试两者。

### Web 内存指令

- 禁用纹理和网格上的 **Read/Write Enabled**——它将数据复制到 WASM 堆中。
- 通过将资产移动到 Addressables 或 AssetBundles 减少 """.data" 文件大小。
- 使用压缩纹理格式（KTX2/Basis）以减少下载和解码的内存成本。

### iOS Safari 内存限制

- **iOS < 18:** WebContent 进程限制约为 1.5 GB。WASM 内存（Gigacage）限制为 2 GB。类型数组共享此内存池。在 iPhone X（iOS 16）上，堆增长限制在 ~512 MB，但提前将 Initial Memory Size 设置为 512 MB–1.5 GB 可以工作。
- **iOS 18+:** 限制基本解除；iPhone 11 可分配 ~4 GB。
- 在 iOS 上，将 **Initial Memory Size** 设置为目标峰值，而不是依赖增长——Safari 处理大额预分配比增量增长更好。
- WASM 堆 > 300 MB 在旧 iOS 上有崩溃风险；目标 < 200 MB 以获得广泛的兼容性。

### Web 上的视频和音频

- **视频**：仅从 URL（带有 CORS 启用的服务器）或 StreamingAssets 中播放。在 iOS 上，服务器必须支持 HTTP 范围请求以进行流式传输。使用浏览器兼容格式（MP4/H.264）。
- **音频**：AudioEffects（混音器效果）需要计算着色器——**WebGL 上不可用**。混音器和 MixerGroups 仅用于音量控制。将音频设置为 **Mono** 以提高加载速度。如果 `about:memory` 显示 Web 音频 > 100 MB，音频可能未压缩——切换到 Vorbis。

### Canvas 和 DPI

如果画布被缩放，它将采用新的分辨率。在 Web 模板中使用 `devicePixelRatio` 以抵消 DPI 缩放并避免在不需要的高分辨率下渲染。

## 4. 验证

1. 使用 Pre-Flight 片段重新读取 Player Setting（压缩、剥离、异常、targetFrameRate）。
2. 重新构建玩家，并将构建报告文件大小与基线进行比较。
3. 至少在 Chrome 和 Safari 中验证（GC 和 JIT 行为不同）。
4. 最大 **3 次迭代**之前才要求用户提供反馈。

## 5. 故障排除

### 启用 Strip Engine Code 后构建仍然太大

1. **Managed Stripping Level** 设置为 Medium 或 Low 吗？→ 发布版将其设置为 High。
2. 插件是否使用反射来访问否则会被剥离的引擎模块？→ 添加 `link.xml` 以保留所需的符号。
3. **Exceptions** 设置为 Full 吗？→ Full 添加了最大的代码开销；切换到 None 或 Explicitly Thrown Only。

### Brotli 不工作——需要 Decompression Fallback

1. 服务器是否发送 `Content-Encoding: br`？→ 如果没有此标头，浏览器不会解压缩；然后需要后备 JS 解压缩器。
2. 构建是否通过 HTTP 托管（而不是 HTTPS）？→ Brotli 需要安全上下文；对于 HTTP 托管，请降级为 Gzip。

### Safari 中卡顿但 Chrome 中没有

1. 项目是否设置 `Application.targetFrameRate = 60`？→ 在 Safari WebGL 中这与浏览器的节拍冲突；设置为 `-1`。
2. 是否有在 Safari 的 WebGL 实现中行为不同的着色器？→ 在设备上测试；Safari 的 WebGL/Wasm 运行时与 Chromium 不同——某些 GLSL 构造的处理方式不同。

### 内存增长触发慢路径

1. **Initial Memory Size** 对项目的峰值来说太小吗？→ Wasm 内存增长需要完整的缓冲区复制；将 Initial Memory Size 设置为现实的峰值估计。
2. **Memory Growth Mode** 设置为 Linear 吗？→ 切换到 **Geometric** 以获得更合理的增长曲线。

### 设置为 60 fps 但浏览器运行异常

1. 是否在代码中设置了 `Application.targetFrameRate = 60`？→ 在 Web 上这与 `requestAnimationFrame` 浏览器节拍冲突。设置为 `-1`。
2. `vSyncCount` 是否非零？→ 设置为 0；浏览器处理节拍。

### Firefox 缓存拒绝大文件

Firefox 通过 `browser.cache.disk.max_entry_size` 限制单个缓存条目。如果构建超过此限制（默认约 50 MB），资产将不会缓存。解决方案：使用 Addressables 将其拆分为 < 51 MB 的包，或者指示用户在 `about:config` 中增加设置。

### 本地开发服务器设置

对于使用正确的 MIME 类型在本地测试构建：

```bash
# Python (HTTP)
python -m http.server 55553 -d path/to/build

# Node.js (安装 serve-handler)
npx serve path/to/build -l 3001
```

对于 Brotli 测试，请使用 HTTPS——Brotli 需要安全上下文。使用 OpenSSL 为本地测试生成自签名证书。

## 6. 完成

- 总结：初始下载大小差异，更改的设置（压缩、剥离、异常、targetFrameRate），服务器配置确认。
- 列出后续操作：Addressables 远程组使用的 CDN 设置，Safari 测试，当浏览器基线支持时升级 Wasm 2023 功能集。

## 参考资料链接

这些指向 Unity 工具而不是其他技能，因为它们涵盖的主题不在本插件中：

- **Addressables 包**——通过 CDN 托管的远程组，当需要将内容移出初始负载时，下载预算需要内容。
- **Unity Profiler，连接到浏览器**——跨平台分析方法。第 3 节涵盖了 Web 的特定部分，用于附加它。
- **着色器变体剥离**（图形设置 → 着色器剥离，和 `ShaderVariantCollection`）——变体计数直接输入 Wasm 大小，因此当单独剥离不起作用时，检查它是值得的。
- **项目设置 → Player**——此技能读取的相同标志，如果用户宁愿在检查器中查看它们而不是让它们报告。
- 移动浏览器电池行为遵循第 3 和第 4 节中的帧率和质量级别指导；这里没有单独的移动路径。
