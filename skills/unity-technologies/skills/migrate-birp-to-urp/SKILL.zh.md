---
name: migrate-birp-to-urp
description: 制定计划、执行并解决从内置渲染管线迁移到URP的问题。在需要将项目、场景、材质或着色器转换为URP，或修复因转换导致的视觉效果问题时使用。
---

对请求进行分类，检查当前项目状态，选择正确的迁移路径，并仔细验证内置到URP的迁移结果。

## 强制执行参考

对于任何实际的迁移或修复流程，在首次调用`eval`编辑项目设置、材质、后期处理、光照、探头或场景之前，必须阅读[references/implementation-patterns.md](references/implementation-patterns.md)。即使对于“将此项目迁移到URP”这样简短的提示，当回滚安全性已经确认时，这也是强制性的。

如果无法加载该资源，请使用此SKILL.md中的嵌入式规则，并降低置信度：不要仅凭意图或工具日志声称PPv2转换、光照/探头刷新或迁移完成。

## 关键默认值

对于“将此内置项目迁移到URP”或“将此项目迁移到URP”等简单请求，请启动或继续安全的迁移工作流程，而不是直接跳转到转换。

通用的升级提示不应要求用户提及所有迁移风险。检查和处理常见的内置依赖项，例如PPv2、烘焙光照/光照贴图、反射探头、粒子/雾/烟雾材质、质量级别、相机后期处理和代表性场景验证。

默认结果是分阶段的：

1. 检测项目是否为内置、部分迁移、已经是URP或HDRP。
2. 将请求分类为标准3D URP、URP 2D、选定材质转换、仅规划或故障排除。
3. 在推荐更改之前检查迁移风险：不透明材质、粒子/VFX材质、自定义着色器、后期处理、相机效果、烘焙光照/光照贴图/反射探头、质量级别和代表性场景。
4. 在用户确认回滚点（例如分支、备份、存档或可丢弃副本）之前，停止任何修改管道的工作。修改管道的工作包括安装URP、在图形/质量设置中分配URP资源、运行转换器以及编辑材质或场景。
5. 选择下一个迁移阶段，执行该阶段，保存/重新查询其输出，并报告其阶段状态。
6. 将自定义着色器、`GrabPass`、表面着色器、`OnRenderImage`、替换着色器和包拥有的着色器视为范围后续工作，而不是自动转换工作。
7. 在声明完全迁移成功之前，验证代表性场景、控制台输出、相机渲染、光照/烘焙GI状态、材质、后期处理持久性和质量级别分配。

默认阶段：

- 阶段0：检查和规划。检测管道状态、代表性场景、回滚安全性、PPv2、材质/着色器风险、质量级别、光照/光照贴图/探头状态和自定义渲染代码。
- 阶段1：URP设置和受支持材质转换。安装/重用URP，在图形/质量中创建/分配URP资源，转换受支持的半透明和粒子/效果材质，并验证内置着色器上不再有受支持的材质。
- 阶段2：后期处理和相机迁移。创建持久的URP Volume配置文件，连接场景Volume/相机后期处理，禁用用于URP验证的旧PPv2，并分类不受支持的PPv2效果，例如SSR。
- 阶段3：光照、光照贴图和反射探头。解决陈旧的内置光照状态，配置URP光照/探头设置，在可行时重新烘焙/刷新，或明确标记光照/探头部分。
- 阶段4：最终验证和报告。保存/重新加载/重新查询项目状态，捕获代表性场景，检查控制台，并报告完整/不完整/手动项。

如果项目较小且Unity保持稳定，一次操作可能完成多个阶段，但不要将所有阶段强制合并到一个响应中。优先考虑诚实的阶段边界，而不是过度声称“完成”的结果。

仅在项目状态或用户意图留下实际未解决的决策时才询问配置问题。如果用户说“不要修改文件”，请保持在审计/规划模式，不要执行转换或资源编辑。

### 通用升级合同

当用户给出通用迁移请求并允许更改时，根据项目状态驱动下一阶段：

1. 在检查之前，不要要求用户列举已知的内置功能。发现它们。
2. 如果存在PPv2、烘焙光照、反射探头、粒子/雾/烟雾材质或多个质量级别，请自动将它们包含在迁移中。
3. 优先考虑阶段完成而不是一次性完成。每个阶段应保存/重新查询其自己的输出，并以“阶段完成”、“阶段部分”或“阻塞”结束。
4. 如果Unity编译、包安装、域重新加载或长时间的烘焙中断了流程，请报告中断为阶段边界，并在下一次操作中从保存的部分状态恢复，而不是重新开始。
5. 不要依赖用户编写详细的检查清单提示来获得正确行为。详细的检查清单用于基准测试或压力测试；普通用户提示仍应触发此分阶段合同。
6. 通用迁移请求允许检查和规划，但并不能证明回滚安全性。如果未确认回滚点，请在包安装或URP分配之前停止并请求确认。不要将项目置于洋红色部分状态只是为了达到备份问题。
7. 如果回滚安全性已经确认或用户说项目是可丢弃副本，请在当前阶段内继续，不要再询问常规工作。
8. 在阶段结束时，给出简洁的下一阶段提示或说明下一个应运行的阶段。仅在引入新的昂贵或风险操作时（例如长时间的烘焙、删除/清理旧资源或自定义着色器重写）才在下一阶段之前请求确认。
9. 如果回滚安全性已确认且当前活动阶段内的常规工作未完成，不要询问“您希望我继续吗？”继续修复该阶段，直到其门禁通过、工具/域重新加载边界中断执行或出现真正的风险决策。

### 通用迁移成功门禁

在说通用迁移是“成功”、“完整”或“完全迁移”之前，验证保存的项目状态，而不仅仅是工具日志：

1. 图形设置和每个相关的质量级别点都指向预期的URP资源。
2. URP资源在保存状态中具有有效的默认渲染器，当前控制台输出不包含未解决的渲染管道错误，例如“Default Renderer is missing”。如果分配后出现渲染器错误，请重新查询保存的渲染器列表/默认索引，在可能的情况下清除陈旧的控制台输出，触发新的场景/相机验证，并继续修复，而不是在“URP设置完成”时停止。
3. 受支持的内置材质，包括粒子/雾/烟雾材质，具有URP兼容的着色器或被明确列为未解决的自定义/包着色器案例。带纹理/着色的源材质必须保留其源贴图/颜色；如果源`_MainTex`或`_Color`包含内容，则带有缺失的`_BaseMap`或所有白色的`_BaseColor`的URP着色器分配是不完整的。粒子、雾、烟雾、蒸汽、贴花、VFX、加法和不透明效果材质不应盲目强制转换为`Universal Render Pipeline/Lit`；在适当的情况下，优先使用URP粒子/效果着色器，例如`Universal Render Pipeline/Particles/Unlit`。
4. 如果源场景使用了PPv2，则保存的URP `VolumeProfile`存在具有持久的非空覆盖组件，代表性场景通过URP `Volume`引用它，并且旧PPv2已禁用以进行URP视觉验证。带有`components: []`、`{fileID: 0}`组件引用或场景仍然仅引用旧`PostProcessProfile`的保存配置文件是不完整的。
5. 如果代表性场景使用烘焙/混合光照，则使用了Enlighten/实时GI光照设置资源、光照数据资源、光照贴图、光照探头或反射探头，不要在通用完整迁移期间将常规光照/探头修复作为手动后续工作。尝试分配URP兼容的光照设置，根据需要清除/重新烘焙或继续烘焙，在可行时刷新反射探头，然后保存/重新加载并验证场景引用了预期的光照状态。创建`.lighting`资源并调用`Lightmapping.lightingSettings = target`加上`AssetDatabase.SaveAssets()`是不够的；标记/保存场景，重新加载/重新查询，并比较保存场景的`m_LightingSettings`引用或资产GUID。如果长时间的烘焙或工具中断阻止了这一点，请将迁移标记为部分并从该阶段恢复。
6. 在迁移验证之前，有意识地打开或选择代表性场景；不要从默认/测试场景推断烘焙光照或PPv2的缺失。场景在保存/重新加载后已被捕获或检查，控制台输出已被检查以查找渲染管道、着色器或渲染器功能错误。
7. 最终措辞必须与门禁结果匹配。仅在所有门禁通过时才使用“完整”。当URP设置完成但PPv2 Volume持久性、旧PPv2禁用、光照烘焙/探头刷新或保存状态验证仍然存在时使用“部分”。如果任何所需门禁为部分，则不要以“成功迁移”开头。

完整报告清单：

- 如果旧PPv2配置文件包含活动的`DepthOfField`，新URP配置文件必须包含保存的`DepthOfField`覆盖或最终报告必须称其为省略/手动。
- 如果旧PPv2配置文件包含活动的`AmbientOcclusion`，在可行时配置URP SSAO渲染器功能，或标记AO为手动/部分。
- 如果旧PPv2配置文件包含活动的`ScreenSpaceReflections`，除非实际添加并验证了URP渲染器功能/自定义替换，否则将SSR列为不支持/手动。
- 如果场景仍然序列化旧光照设置GUID或非零的旧`m_LightingDataAsset`，光照是部分的。
- 如果场景具有反射探头且URP资源仍然序列化`m_ReflectionProbeBlending: 0`或`m_ReflectionProbeBoxProjection: 0`，除非有意禁用并报告，否则反射是部分的。
- 如果任何清单项为假，不要在最终答案中使用“完整”、“完全迁移”或“在URP上完全功能”。

不受支持的功能可以保持手动，但必须精确命名。例如，需要URP渲染器功能/自定义/第三方替换的PPv2屏幕空间反射，复杂的自定义着色器端口、`GrabPass`、替换着色器或包拥有的渲染代码。如果任何成功门禁项失败，在允许的情况下继续修复或报告部分迁移和不完整项；不要将项目呈现为完全迁移。

回归保护摘要：

- 使用详细的[执行回归检查清单](references/implementation-patterns.md#execution-regression-checklist)进行实际迁移或修复工作。
- 在状态声明之前验证保存的场景引用：URP Volume/配置文件、质量分配、光照设置/数据、URP资源/渲染器以及反射探头设置。
- 从转换前快照保留材质源数据，然后在着色器更改后恢复`_BaseMap`、`_BaseColor`、纹理缩放/偏移和相关贴图。
- 在最终措辞之前验证代表性视觉效果，包括PPv2、植被、粒子/效果、烘焙光照、探头和曝光。
- 报告确切的阶段状态。`Phase complete`允许用于通过的阶段；仅在所有成功门禁通过时才允许项目级`complete`。

## 执行路径：在编辑器中运行C#

此技能中的每个C#步骤都在通过Unity CLI的实时编辑器中运行。**`unity-cli`技能负责带您到达那里**——安装CLI、确认连接的编辑器、添加项目的`com.unity.pipeline`包、区分真正缺失的编辑器与处于安全模式的编辑器，以及发现编辑器的命令目录。首先遵循它；不要在此处重新推导任何内容。

有两件事它无法为您知道：

- **您需要`eval`，而不仅仅是可访问的编辑器**。确认它出现在目录中。它的存在取决于管道包版本，而不是CLI，因此即使安装健康，它也可能缺失——如果缺失，请说明并停止。
- **在6000.3之前的编辑器上，预期管道包完全无法工作**，并正确读取症状，而不是重试。`com.unity.pipeline`使用`IPreprocessBuildWithContext`和`BuildCallbackContext`，Unity在**6000.3**中引入了这些；包自己的清单声明`"unity": "6000.0"`，因此它安装愉快，但编译失败。测量：6000.3 / 6000.4 / 6000.5中存在，6000.0 / 6000.1 / 6000.2以及2022和2023线中不存在。症状具有误导性——服务器从未启动，`unity status`显示没有行且没有错误，真正的原因是编辑器日志中的这两个类型上的`CS0246`。如果您看到这种情况，请告诉用户编辑器太旧，无法使用管道包，而不是调试CLI。

  **这比大多数技能更重要**：正在将项目从内置管道迁移的人，按定义通常使用较旧的编辑器。
- **渲染管道迁移不是盲目可授权的**。分配URP资源、转换材质和重新烘焙光照都需要实时编辑器。无法访问的编辑器是一个停止信号，而不是提示手动编辑`ProjectSettings/GraphicsSettings.asset`。

使用`unity command eval --code '<snippet>'`运行C#。`unity command`默认超时时间为30秒，这在此处很重要：安装URP会触发包刷新和域重新加载，这些操作将持续超过超时时间。将其视为阶段边界，而不是提高超时时间。

### 将C#传递给`eval`

`eval`编译的是**语句块，而不是文件**。三个后果，所有后果都会导致编译错误而不是警告：

- **没有`using`指令**。编译器将`using UnityEngine;`读取为资源释放语句并拒绝它（`CS0210`）。
- **类型必须完全限定**。裸`GraphicsSettings`或`Volume`无法解析（`CS0246` / `CS0103`），裸`Object`与`object`歧义（`CS0104`）。
- **扩展方法不可用**，因为它们通过`using`解析。此技能中原本会使用的两个扩展方法：`camera.GetUniversalAdditionalCameraData()`变为`camera.GetComponent<UnityEngine.Rendering.Universal.UniversalAdditionalCameraData>()`，LINQ调用必须静态编写——`System.Linq.Enumerable.FirstOrDefault(sequence, predicate)`而不是`sequence.FirstOrDefault(predicate)`。

### 两种执行模式——根据代码片段的形状选择

参考资料包含两种形状，它们是不可互换的：

- **语句形状**（一组裸的语句，如上文的检测片段）——直接传递给`eval`，完全限定，没有`using`行。
- **类或方法形状**（声明`class`、`static`方法或`[MenuItem]`的任何内容，如材质快照模式）——这些是**项目文件，而不是`eval`输入**。类声明不能展平为语句块。将片段保存在`Assets/Editor/`下，让Unity编译它，然后通过一行`eval`调用调用其入口点。在该文件中保留`using`指令；它们在那里是正确的。

对于多步骤迁移，脚本路线无论如何更可靠：它会在URP安装和材质转换触发的域重新加载中生存，而长`eval`负载不会。

### 检测活动的渲染管道

```csharp
var rp = UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline;
var qrp = UnityEngine.QualitySettings.renderPipeline;
return $"graphics={(rp == null ? "NULL (Built-in)" : rp.GetType().Name + ":" + rp.name)}, "
     + $"activeQualityLevel={(qrp == null ? "inherits Graphics" : qrp.GetType().Name + ":" + qrp.name)}";
```

一个 `UniversalRenderPipelineAsset` 代表 URP；`HDRenderPipelineAsset` 代表 HDRP；两处均为 `NULL` 表示内置。**也要检查每个质量级别的分配情况**——项目可以在图形设置中切换，而质量级别仍然指向不同的资源，或指向无资源：

```csharp
var names = UnityEngine.QualitySettings.names;
var rows = new System.Collections.Generic.List<string>();
for (int i = 0; i < names.Length; i++)
{
    var a = UnityEngine.QualitySettings.GetRenderPipelineAssetAt(i);
    rows.Add($"{i}:{names[i]}={(a == null ? "继承 Graphics" : a.name)}");
}
return string.Join(", ", rows);
```

如果 `GetRenderPipelineAssetAt` 在项目的 Unity 版本中不可用，请读取 `ProjectSettings/QualitySettings.asset` 而不是在运行时切换级别——`SetQualityLevel` 会改变项目状态。

## 0. 飞行前检查：管线检测和引用加载

在执行任何其他操作之前，你必须**确定活动的渲染管线和迁移模式**：

1. **检测管线：** 运行上面执行路径部分中的渲染管线检测代码片段。
   - 如果 `currentRenderPipeline` 或 `defaultRenderPipelineAsset` 引用 `UniversalRenderPipelineAsset` -> **URP**。
   - 如果没有分配渲染管线资源 -> **内置**。
   - 如果它引用 `HDRenderPipelineAsset` -> **HDRP**。说明这个技能仅涵盖内置到 URP 的迁移。可以提供基本的比较建议，但不要用这个技能驱动 HDRP 迁移。
2. **加载基础引用：** 读取 [references/migration-workflow.md](references/migration-workflow.md)。
3. **在相关情况下加载着色器引用：** 如果请求中提到材质、着色器、品红色材质、渲染错误、图像效果或自定义渲染，也读取：
   - [references/custom-shader-triage.md](references/custom-shader-triage.md)
   - [references/complex-shader-situations.md](references/complex-shader-situations.md) 当检查或项目文件搜索发现高级着色器/效果模式时
4. **在相关情况下加载质量引用：** 如果请求中提到阴影、光照、烘焙光照、光照贴图、反射探头、质量设置、视觉不匹配或迁移后的性能，也读取 [references/quality-settings-map.md](references/quality-settings-map.md)。
5. **执行时加载实现模式：** 如果请求允许实际迁移更改、后期处理转换、烘焙光照/探头修复或从部分迁移中恢复，也读取 [references/implementation-patterns.md](references/implementation-patterns.md)。
6. **将请求分类**为以下之一：
   - 全项目内置到 URP 迁移
   - 内置 2D 到 URP 2D 迁移
   - 仅选中材质转换
   - 仅规划/解释
   - 迁移后的故障排除
7. **如果项目已经在 URP 上，** 切换到故障排除模式而不是盲目重新运行设置。
8. **只有在管线和迁移路径明确后，** 才继续。

## 1. 评估当前迁移状态

在做出任何更改之前，**检查已存在的内容**：

1. **检查管线状态和分配点：**
   - 运行上面执行路径部分中的两个渲染管线检测代码片段——图形设置中的一个和每个质量级别中的一个。
   - 如果项目有质量级别，在假设项目完全切换之前，检查每个级别使用哪个渲染管线资源。
2. **盘点迁移表面：** 使用 `eval` 与 `UnityEditor.AssetDatabase.FindAssets` 或等效资源查询来盘点：
   - 材质，包括经常使用内置粒子着色器的粒子/VFX 材质
   - 植被材质，包括草、树、地形细节、SpeedTree、billboard、leaf-card、cutout 和风驱动植被材质
   - 着色器
   - 场景和重要预制件
   - URP 资源和渲染器资源（如果有）
   - 后期处理配置文件 / 音量配置文件
   - 光照设置资源、光照数据资源、光照贴图、光照探头、反射探头和混合/烘焙光照
3. **扫描渲染风险标记：** 使用可用的项目文件搜索、`AssetDatabase.FindAssets` 或简短的 `eval` 文件扫描来搜索项目中特定的渲染模式，例如：
   - `PostProcessLayer`、`PostProcessVolume`、`UnityEngine.Rendering.PostProcessing`
   - `OnRenderImage(`、`RenderWithShader`、`SetReplacementShader`
   - `#pragma surface`、`GrabPass`、`CGPROGRAM`
   - `CommandBuffer`、自定义着色器包含路径或包着色器命名空间
   - 植被标记，如 `Nature/`、`SpeedTree`、`TreeCreator`、`Grass`、`Foliage`、`_Cutoff`、`_AlphaClip`、`_Cull`、billboard 或风关键词
4. **如果 PPv2 已安装但 grep 没有找到，** 通过 Unity API 检查打开的场景和通过组件/类型分析资源。场景 YAML 和序列化包引用可能被文本搜索遗漏。
5. **确定项目结构：** 判断项目主要是 3D、主要是 2D 还是混合。
6. **总结发现：** 在提出转换之前总结当前状态。示例：
   - "项目仍在内置上，没有分配 URP 资源，包含 PPv2 引用，并包含几个使用 surface-shader 语法的自定义着色器。"
7. **如果项目已经在 URP 上，** 切换到故障排除模式而不是盲目重新运行设置。
8. **只有在管线和迁移路径明确后，** 才继续。

## 2. 收集需求

确定用户实际想要什么。如果请求不明确，请询问。

使用这些默认值来处理常见请求：

| 用户说 | 默认解释 |
|--------|----------|
| "将此项目升级到 URP" | 全项目迁移 |
| "将此 2D 项目迁移到 URP" | 内置 2D 到 URP 2D 迁移 |
| "转换这些材质" | 选中材质转换 |
| "我的材质变成了品红色" | 迁移后的着色器/材质故障排除 |
| "迁移后光照看起来不对" | 质量和视觉一致性故障排除 |
| "暂时不要更改任何东西" | 仅规划/审计 |

### 需要收集的信息

- **范围：** 全项目、选中材质或仅故障排除
- **目标渲染器：** 标准 URP 或 URP 2D
- **验证目标：** 对用户最重要的场景、预制件或相机
- **风险容忍度：** 是否可以接受有限的后续手动操作
- **渲染依赖：** 自定义着色器、商店着色器、PPv2、烘焙光照/光照贴图/探头、图像效果、命令缓冲区、替换着色器或多个质量级别
- **执行权限：** 仅规划 vs 实际项目更改

## 3. 安全门

在任何修改管线步骤之前：

1. **确认回滚安全性。**
   - 在用户确认备份、分支、存档、可丢弃副本或回滚点之前，**绝对不要**安装 URP、分配 URP 资源、运行渲染管线转换器、编辑材质或编辑迁移场景状态。
   - 如果回滚安全性缺失，不要将项目部分切换到 URP。停留在规划模式并首先请求回滚确认。
2. **将引擎升级风险与管线升级风险分开。**
   - 如果项目也在迁移到新的 Unity 版本，建议先进行引擎升级，再进行管线迁移。不要将两者视为单一的盲目操作。
3. **如果回滚安全性已确认，** 将其视为涵盖整个迁移过程。在转换器之前不要再次询问；通过设置、材质转换、PPv2 迁移、光照/探头工作、保存/重新加载验证和最终报告进行操作，除非出现新的风险决策。
4. **如果用户已授权完整可丢弃迁移，** 在常规设置或可恢复错误后不要请求权限继续。继续执行下一个不完整的迁移阶段。仅在出现新的破坏性清理决策、包/域重新加载停止执行或重复修复尝试达到验证迭代限制时才询问。
5. **如果项目已部分迁移，** 确认之前是否已确认回滚安全性。如果是，从第一个不完整项恢复。如果不是，报告部分状态并在进行其他更改前询问。

## 4. 选择迁移路径

使用适合项目的正确路径：

### 路径 A：标准 3D 内置到 URP
- 用于正常 3D 内置项目迁移到标准 URP。

### 路径 B：内置 2D 到 URP 2D
- 用于项目主要是 2D 且用户期望 URP 2D 光照或渲染器行为时。
- 不要将其视为与标准 URP 相同的工作流程。

### 路径 C：仅选中材质转换
- 仅用于项目已在 URP 上且用户希望选中材质转换时。

### 路径 D：故障排除现有迁移
- 用于项目已在 URP 上或迁移已尝试过时。
- 优先处理最高影响的破坏，而不是盲目重新运行整个迁移。

## 5. URP 设置工作流

按此精确顺序执行：

1. **确保已安装 URP。**
   - 安装 URP 可能会触发包刷新、编译和域重新加载。将其视为阶段边界。
   - 不要在 `UnityEditor.PackageManager.Client.Add` 的 `eval` 调用中无限期地自旋等待。请求安装，然后通过 `Packages/manifest.json`、包列表或 URP 类型/资源在 Unity 刷新完成后存在来验证。
   - 如果包安装导致 `eval` 调用超时或返回空，在 Unity 完成编译后在新回合中恢复。不要重新安装整个迁移或 URP；检查部分状态并从那里继续。
2. **如果不存在，创建所需的 URP 资源和渲染器资源。**
3. **在图形设置和所有相关质量级别中分配 URP 资源。**
4. **对于 2D 项目，** 在转换前创建和分配正确的 2D 渲染器资源。**
5. **如果 URP 资源已存在，** 在适当情况下检查并重用它，而不是自动创建副本。**
6. **直到 URP 实际成为目标配置的活动渲染管线，** 才继续。

## 6. 转换工作流

对于实际转换工作，请遵循 [references/migration-workflow.md](references/migration-workflow.md)。

1. **选择正确的渲染管线转换器路径：**
   - `内置渲染管线到 URP`
   - `内置渲染管线 2D 到 URP 2D`
2. **初始化转换器并检查候选更改**，然后再转换。
3. **对于标准内置到 URP 迁移，** 优先使用参考中描述的适用转换器：
   - `Rendering Settings`
   - `Material Upgrade`
   - `Animation Clip Converter`
   - `Read-only Material Converter`
   - `Post-processing Stack v2 Converter`
4. **对于选中材质转换，** 使用目标材质转换工作流，而不是转换整个项目。**
5. **转换前查看警告和失败。**
6. **只有在用户确认项目可以更改后，** 才运行转换。**
7. **验证每个材质实际落到了哪个着色器**——不要假设转换器选择了 3D 目标。`MaterialUpgrader.FetchAllUpgradersForPipeline` 返回与 3D 提供者一起设置的 2D 提供者，两者都以相同优先级声明 `Standard`，因此在 3D 项目中，普通的 `Standard` 材质可能会无声地转换为 `Universal Render Pipeline/2D/Mesh2D-Lit-Default` 而不是 `Universal Render Pipeline/Lit`。没有错误，材质不会变成品红色，所以除非你回读着色器名称——在 6000.5.8f1 上测试。**
   - 转换后读取每个转换材质的 `shader.name` 并确认它是否与映射表中的目标匹配。如果任何材质在 3D 项目中落到了 `2D/` 着色器，从回滚点恢复这些材质并使用 3D 过滤升级器列表或 [references/implementation-patterns.md](references/implementation-patterns.md) 中的手动模式进行转换。**
8. **转换后，验证保存的项目状态。**
   - 重新打开或重新查询代表性资源，而不是单独依赖命令输出。
   - 场景级编辑后保存资源并打开场景。对场景组件、相机数据、活动光照设置、反射探头和 PPv2 启用状态的变化，`AssetDatabase.SaveAssets()` 单独无法证明。
   - 确认 URP 资源在图形和目标质量级别中已分配。
   - 对于质量级别，通过重新查询 `QualitySettings.GetRenderPipelineAssetAt(i)` 或读取 `ProjectSettings/QualitySettings.asset` 中的保存 `customRenderPipeline` 条目来验证。如果它们仍然是 `{fileID: 0}`，则质量级别没有明确分配。
   - 不要调用猜测的质量 API，如 `QualitySettings.SetRenderPipelineAssetAt`；在 Unity 版本中该 API 不可用时，使用 `QualitySettings.SetQualityLevel(index)` 切换到每个目标级别，设置 `QualitySettings.renderPipeline = urpAsset`，然后恢复原始级别并验证保存的 `customRenderPipeline` 值。**
   - 确认转换材质实际引用 URP 着色器。**
   - 确认源反照率纹理的代表性材质现在具有非空的 `_BaseMap` 值。此检查必须与转换前的材质快照进行比较；不要使用转换后的 `_MainTex` 作为真实来源。**
   - 确认粒子/VFX 材质不再引用内置粒子着色器 ID 或遗留着色器名称；在适当的地方使用 URP 粒子着色器，如 `Universal Render Pipeline/Particles/Unlit`。如果材质名称或路径包含 `Particle`、`Fog`、`Smoke`、`Steam`、`VFX`、`Additive` 或类似效果术语，请保留透明/加性行为，而不是默认为 URP Lit。**
   - 确认植被材质保留 cutout/alpha 剪辑、渲染面意图、纹理、色调、法线和预期的风/billboard 行为。如果草/树卡片因为其专用着色器行为丢失而变成实心或静态，则材质转换不完整。**
   - 如果 PPv2 转换已尝试，确认保存的 URP 音量配置文件包含持续的非空 `components` 条目，并且场景/相机连接使用 URP 兼容组件。**
   - 如果存在烘焙光照，保留旧的光照数据和光照贴图作为参考数据，然后验证它们是否仍然产生可接受的 URP 视觉。如果创建了新的光照设置资源，验证保存后的场景在保存/重新加载后是否实际引用它；磁盘上存在资源并不足够。在实际通用迁移中，当陈旧的烘焙数据或反射探头影响一致性时，尝试重新烘焙/刷新；如果当前回合无法完成，报告迁移为部分并稍后从光照/探头阶段恢复。**
   - 不要声称“刷新了反射探头”来自意图。验证新或更新的探头输出、更改的保存反射探头资源或成功的探头渲染工具输出。如果现有的 EXR 文件保持不变，则说明探头被保留为参考或仍需刷新。**
   - 如果任何验证失败，报告项目为不完整/需要手动跟进，而不是已迁移。**

## 7. 着色器和材质筛选

当材质变成品红色、着色器编译失败或视觉大幅漂移时，使用 [references/custom-shader-triage.md](references/custom-shader-triage.md) 首先进行筛选。

1. **识别受影响的材质和着色器。**
   - 检查确切的材质着色器分配，而不仅仅是场景症状。
2. **在编辑着色器代码之前，先阅读控制台和检查器的错误信息。**
3. **对着色器案例进行分类：**
   - 转换器应处理的受支持的内置着色器
   - 可能安全移植的简单自定义着色器
   - 需要范围迁移计划的复杂自定义着色器
   - 需要切割、双面叶片、标志板、地形细节渲染或风行为的植被/植物着色器
   - 可能需要维护者文档、范围自定义移植或手动跟进的包拥有或Asset Store着色器
4. **对于复杂的着色器情况，使用 [references/complex-shader-situations.md](references/complex-shader-situations.md)。**
5. **优先选择最小的安全修复。**
   - 首先在代表性材质上恢复渲染。
   - 在将修复扩展到更多资源之前验证结果。
6. **除非映射明确、经过测试和范围界定，否则切勿在整个项目中批量搜索和替换着色器代码。**

## 8. 后处理、相机和渲染效果筛选

内置项目通常依赖于材质转换之外的内容。

1. **如果存在PPv2，检查转换器输出并验证生成的URP卷、配置文件和相机行为。**
   - 在转换之前，清点现有的`PostProcessVolume`、`PostProcessLayer`和PPv2的`PostProcessProfile`资源。
   - 当可用时，优先使用URP的`Post-processing Stack v2 Converter`，而不是从内存中手动构建等效配置文件。
   - 转换后，验证保存的URP的`VolumeProfile`资源是否包含持久性覆盖组件，而不是空的`components: []`配置文件或悬空的`{fileID: 0}`组件引用。
   - 如果通过脚本创建配置文件，`VolumeProfile.Add<T>()`仅创建组件对象；对于持久性配置文件资源，还调用`AssetDatabase.AddObjectToAsset(component, profile)`，标记配置文件和组件为已更改，保存资源，重新加载资源，并在报告成功之前计算保存的非空组件。如果保存的配置文件具有`{fileID: 0}`组件条目，则在声称迁移成功之前重新创建或修复配置文件。
   - 验证代表性场景是否包含预期的`Volume`对象，并且目标相机在需要时具有启用了后处理的`UniversalAdditionalCameraData`。
   - 如果源场景仍然仅序列化PPv2的`sharedProfile`引用，并且没有URP的`Volume`引用新的`VolumeProfile`，即使磁盘上存在URP配置文件资源，PPv2迁移也不完整。
   - 如果活动的URP的`Volume`引用一个空配置文件，将其视为不完整的场景布线，而不是活动的后处理。修复配置文件或报告PPv2为部分。
   - 检查旧的`PostProcessVolume` / `PostProcessLayer`组件是否仍然存在。如果它们仍然存在，解释它们是否有意保留、无害的遗留遗留物或未解决的迁移工作。
   - 如果旧的PPv2组件仅作为引用保留，而URP Volume处于活动状态，禁用旧的PPv2组件/层以进行URP视觉验证，以避免双重后处理。直到用户接受或批准清理之前，不要删除它。
   - 在清理步骤中，不要删除PPv2包、组件或配置文件，除非存在经过验证的URP替代品或用户接受这些效果将被丢弃/手动跟进。
   - 在实际迁移过程中，如果源配置文件可用，不要将常见的PPv2对等物作为模糊的手动任务留下。为常见的可映射效果（如Bloom、颜色调整/色调映射、Vignette和景深）创建持久性URP覆盖，然后验证保存的配置文件具有非空组件。
   - 将不受支持或非等效的效果标记为手动跟进是可接受的，例如PPv2屏幕空间反射或应成为渲染器功能/SSAO设置而不是直接Volume覆盖的Ambient Occlusion。
   - 如果无法可靠地创建URP Volume覆盖，则记录PPv2效果及其URP等效物，而不是声称它们已迁移。
2. **不要将瞬态工具成功视为后处理成功。**
   - 一个显示“添加了Bloom”的命令日志是不够的。重新读取保存的`VolumeProfile`资源或在保存/重新加载后检查场景。
   - 如果保存的配置文件为空，则说明PPv2设置已记录或部分准备，而不是已迁移。
3. **如果grep找到`OnRenderImage`，将其视为自定义全屏效果案例。**
   - 在URP中，自定义全屏效果应向`ScriptableRenderPass`、渲染器功能或URP自定义后处理发展，而不是留在内置图像效果路径上。
4. **如果grep找到`RenderWithShader`或`SetReplacementShader`，将其视为替换着色器案例。**
   - 这些效果通常需要一个明确的URP渲染器功能或自定义传递策略。
5. **如果效果依赖于场景颜色、深度或法线，**验证URP兼容路径，而不是假设内置方法仍然适用。
6. **如果自定义相机在内置中堆叠了效果，**在迁移后显式验证相机输出，而不是假设对等性。
7. **对于高级着色器/效果故障排除问题，提供具体的替换模式。**
   - 对于`GrabPass`，提及`_CameraOpaqueTexture` / 场景颜色、所需的URP资源设置，以及透明排序可能与内置不同的限制。
   - 对于`OnRenderImage`，提及`ScriptableRendererFeature`加上`ScriptableRenderPass`。在显示Unity 6风格的模板时，使用引用模式，并使用临时的`RTHandle`和`Blitter.BlitCameraTexture`。
   - 永远不要推荐`Blitter.BlitCameraTexture(cmd, source, source, material, pass)`或其他源到源的混合作为主要的`OnRenderImage`替换。如果你不打算显示更安全的临时目标模式，请省略代码示例并解释架构。
   - 对于表面着色器，说明`#pragma surface`没有直接URP等效物，并根据效果复杂性选择Shader Graph或URP HLSL顶点/片段重写。
   - 不要停留在“重写它”；给用户一个实际的首次移植步骤和一个验证目标。

## 9. 质量、光照和视觉对等性审查

当用户提到视觉不匹配、阴影、性能或质量设置时，使用 [references/quality-settings-map.md](references/quality-settings-map.md)。

1. **审查图形设置和每个活动的质量级别。**
   - 如果一个质量级别没有自定义URP资源，说明该级别是否有意回退到图形设置或仍然需要显式分配。
   - 不要声称所有质量级别都已迁移，除非每个相关级别都已被检查。
   - 如果使用序列化的项目设置，保存的字段通常是`customRenderPipeline`；除非保存的资源证明了分配，否则编写猜测的字段（如`renderPipelineAsset`）是不够的。
   - 如果通过脚本分配，使用与URP的渲染设置转换器相同的模式：缓存`QualitySettings.GetQualityLevel()`，为每个目标级别调用`QualitySettings.SetQualityLevel(index)`，分配`QualitySettings.renderPipeline = urpAsset`，然后恢复原始质量级别并在磁盘上验证。
2. **检查URP资源设置**，这些设置通常会影响对等性：
   - 阴影
   - 阴影距离和级联
   - MSAA
   - 渲染比例
   - 当效果依赖于它们时，HDR、不透明纹理和深度纹理设置
3. **不要承诺自动获得相同的光照。**
   - 内置和URP在光照衰减、烘焙GI外观、阴影调整、反射探头响应、色调映射、曝光和后处理行为方面可能不同。
4. **对于烘焙光照场景，**将现有的光照贴图和光照数据视为参考材料，而不是保证最终的URP输出。
   - 清点`Lightmapping.lightingSettings`、场景`LightmapSettings`、烘焙/混合灯光、光照探头、反射探头和任何现有的`LightingDataAsset`。
   - 保留烘焙数据，直到用户有视觉参考或回滚点，但如果它们使场景过曝或失真，不要将旧的内置光照贴图作为最终的URP光照解决方案保持活动状态。
   - 如果场景看起来过曝、太暗或不匹配，首先通过在URP验证期间禁用遗留PPv2来隔离后处理/曝光，然后审查URP Volume曝光/色调映射/ bloom，然后再更改灯光。
   - 如果清除烘焙数据使场景停止过曝，则将旧的光照贴图/光照数据识别为过时或与活动数据不兼容。然后在URP下使用最终的URP资源、渲染器、Volume和质量设置重新烘焙，而不是根据过时的烘焙调整灯光。
   - 如果创建或分配URP兼容的`LightingSettings`，标记光照设置和活动场景为已更改，保存场景，重新加载或重新查询，并验证保存的场景引用了预期的`.lighting`资源。`AssetDatabase.SaveAssets()`本身不会保存场景的`Lightmapping.lightingSettings`引用。如果保存的场景仍然指向Enlighten/实时GI设置资源，则不要报告“Baked GI已启用”。
   - 当视觉对等性是请求的一部分，并且从内置烘焙中保留旧的`LightingData.asset` / 反射探头EXR时，将它们视为参考数据，直到在URP下重新烘焙/刷新。不要单独声称仅凭旧烘焙数据就保留了视觉对等性。
   - 当视觉对等性重要时，建议清除/重新烘焙光照并刷新反射探头。不要声称烘焙光照已成功迁移，除非在URP设置后代表性场景已通过视觉检查，并且最好在URP烘焙后。
5. **对于2D光照项目，**确保精灵和瓦片地图在需要时使用URP兼容的照明材质。
6. **对于性能回归，**检查问题是否来自：
   - 更重的URP资源设置
   - 后处理
   - 额外的阴影成本
   - 自定义着色器移植或非批处理着色器
7. **更改URP资源设置时，**在保存后重新读取保存的资源或查询属性之前报告MSAA、附加光源限制、HDR、深度纹理或不透明纹理等值。

## 10. 验证

在设置、转换或故障排除后，验证结果：

1. **捕获场景：**捕获场景视图或代表性场景上的特定相机——见 [references/capturing-the-editor.md](references/capturing-the-editor.md)。
2. **评估结果：**
   - 除非存在未解决的自定义着色器阻塞项，否则不要出现品红色材质
   - 主要光照和阴影按预期工作
   - 烘焙GI/光照贴图、光照探头和反射探头可以接受或明确标记为重新烘焙/刷新
   - 相机渲染预期内容
   - 后处理或全屏效果仍然正确
   - 精灵、瓦片地图或2D灯光在需要时工作
3. **验证持久性项目数据，而不仅仅是视觉输出。**
   - 检查保存的URP资源、渲染器资源、场景引用、材质着色器GUID/名称、质量设置和Volume配置文件。
   - 确认打开或检查代表性场景，而不是默认/测试场景，在得出烘焙光照、PPv2或反射探头缺失的结论之前。
   - 对于材质迁移，包括粒子/VFX材质在验证中。剩余的内置粒子着色器ID或遗留粒子着色器名称意味着材质迁移不完整。
   - 对于PPv2迁移，保存的URP的`VolumeProfile`资源必须包含预期的覆盖组件，然后才能报告它们已迁移。
   - 如果工具日志报告映射的后处理，但保存的配置文件重新加载时为`components: []`，则覆盖工具日志并报告迁移失败/不完整。
   - 对于烘焙光照场景，检查光照设置、光照数据/光照贴图引用、光照探头和反射探头。编译成功并不能证明烘焙光照对等性。如果旧光照贴图导致过曝，清除活动的烘焙数据并在URP下重新烘焙，然后再判断对等性。分配新光照设置后，验证保存的场景引用，而不仅仅是新`.lighting`资源的存在。
   - 如果旧的`LightingData.asset`仍然分配，并且反射探头EXR在视觉检查后没有重新生成或明确接受，则将光照/探头分类为保留或部分，而不是刷新。
4. **使用`Unity.GetConsoleLogs`检查控制台输出**以查找着色器、渲染管线或渲染器功能错误。
5. **首先修复最高影响的问题，**然后再次验证。
6. **最多重复3次**，然后报告剩余的阻塞项或询问用户如何继续。

## 11. 故障排除决策树

如果用户报告迁移问题，请遵循此诊断流程：

### 项目在“迁移”后仍然像内置一样
1. 检查图形设置中是否分配了URP资源。
2. 检查相关质量级别是否也指向URP资源。
3. 在解决任何其他问题之前，验证活动渲染管线实际上是URP。

### 安装URP后迁移停止
1. 将此视为包刷新/域刷新边界，而不是自身失败的完整迁移。
2. 重新检查`Packages/manifest.json`和包状态。如果安装了URP，不要重新安装它。
3. 检查部分资源，如URP资源、渲染器资源、转换后的材质、空的Volume配置文件和场景组件更改。
4. 如果安装了/分配了URP，但内置材质仍然占主导地位或场景为品红色，则材质转换是立即下一个不完整的项。如果已经确认回滚安全性，不要声称URP设置完成并停止。
5. 继续从第一个不完整的验证项开始：图形/质量分配、渲染器资源有效性、材质转换、PPv2到URP Volume迁移、烘焙光照重新烘焙，然后最终验证。
6. 如果之前的聊天/导出没有最终响应，报告它为不完整的证据并继续在新的聊天/回合中。

### 后处理或全屏效果消失
1. 检查是否已将PPv2转换，以及目标相机和音量设置是否仍然有效。
2. 检查保存的URP `VolumeProfile` 资产。空配置文件表示PPv2效果实际上未被迁移。
3. 检查场景中是否仍有旧的 `PostProcessVolume` / `PostProcessLayer` 组件处于激活状态。
4. 搜索 `OnRenderImage`、自定义混合代码或替换着色器相机效果。
5. 使用与URP兼容的方法移植效果，而不是试图保持内置回调路径不变。

### 透明/折射/扭曲效果失效
1. 检查着色器是否依赖 `GrabPass` 或类似的内置屏幕复制工作流程。
2. 如果是，请使用 [references/complex-shader-situations.md](references/complex-shader-situations.md) 并选择 Scene Color / Renderer Feature / 自定义通道方法。

### 2D光源未影响精灵
1. 确认项目实际使用的是2D渲染器。
2. 确认现有的精灵材质在需要时已升级为与URP兼容的照明材质。
3. 不要假设拖入的新精灵证明了旧项目材质的正确性。

### 迁移后性能下降
1. 审查渲染比例、阴影、附加光源、MSAA、后处理、不透明/深度纹理和其他URP资产设置。
2. 检查自定义着色器端口是否丢失批处理兼容性或引入了额外通道。
3. 在假设唯一答案是回滚之前调整设置。

### 自定义着色器编译但视觉效果仍然错误
1. 判断问题是简单的参数漂移还是结构上的不兼容。
2. 如果着色器来自表面着色器、`GrabPass`、替换着色器工作流程或自定义照明路径，将其视为复杂的迁移案例。
3. 在项目范围内推广方法之前验证一个代表性材质。

## 12. 核心指导原则

- 首先检测活动的渲染管线；对于HDRP，解释不匹配并提供仅基本的比较指导。
- 在确认回滚安全性之前不要修改项目；相反，在安装URP、资产分配、转换器、材质编辑或场景编辑之前停止在规划模式。
- 不要将工具日志或创建的资产视为证据；相反，在状态声明之前保存/重新加载/重新查询 Graphics、Quality、材质、Volumes、照明、探头、Console 和代表性场景。
- 不要将部分阶段合并为项目级完成；相反，根据成功门根据 `Phase complete`、`Partial migration` 和 `Manual follow-up` 进行报告。
- 不要批量重写脆弱的渲染代码；相反，使用自定义着色器、`GrabPass`、`OnRenderImage`、替换着色器、包拥有的渲染代码和不支持的PPv2效果的限定映射。

## 13. 返回报告

总结：

- 使用了哪种迁移路径
- 项目是否仍然为内置、部分迁移或完全迁移到URP
- 运行了哪些转换器
- 自动修复了什么
- 仍需哪些手动工作
- 哪些场景、材质或相机已验证
- 哪些仍然存在风险，尤其是在复杂着色器、包效果和视觉一致性方面
- 后处理是否完全迁移、部分准备或仅记录为手动后续工作
- 质量级别是否明确分配或有意依赖图形设置回退
- 粒子/VFX材质是否已转换或仍需URP粒子着色器后续工作
- 烘焙照明/光照贴图/反射探头是否作为参考、视觉验证、重新烘焙/刷新或留作手动后续工作
- 曝光、色调映射、环境填充和相机/Volume后处理连接是否视觉平衡或仍为部分

谨慎使用完成语言。如果报告包含任何 `Partial`、`Manual follow-up`、`not validated`、`may still need` 或不支持的特性项，请声明特定完成的阶段通过，并将整体迁移称为部分/手动。不要将项目级的“完成”声明与手动后续工作要点配对。

## 参考

- [Migration Workflow](references/migration-workflow.md)
- [Custom Shader Triage](references/custom-shader-triage.md)
- [Complex Shader Situations](references/complex-shader-situations.md)
- [Quality Settings Map](references/quality-settings-map.md)
- [Implementation Patterns](references/implementation-patterns.md)

当此技能被激活时，主动读取 [references/migration-workflow.md](references/migration-workflow.md)。如果请求涉及材质、着色器、洋红色材质、自定义渲染或全屏效果，还请读取 [references/custom-shader-triage.md](references/custom-shader-triage.md) 和 [references/complex-shader-situations.md](references/complex-shader-situations.md)。如果请求涉及视觉不匹配、照明、烘焙照明、光照贴图、反射探头、阴影或迁移后的性能，还请读取 [references/quality-settings-map.md](references/quality-settings-map.md)。如果用户允许实际迁移更改或要求继续/修复部分迁移，还请读取 [references/implementation-patterns.md](references/implementation-patterns.md)。
