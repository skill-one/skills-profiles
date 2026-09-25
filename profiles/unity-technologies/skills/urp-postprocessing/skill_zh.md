帮助用户使用 URP 的 Volume 框架设置、配置和调试后期处理效果。

**目标：设置完成后，用户应获得一个无控制台错误的工作视觉结果。**

## 0. 前置条件：一个可以在其中运行 C# 的编辑器

Volume 配置文件、`VolumeParameter.overrideState` 以及相机的后期处理标志是
编辑器/运行时对象状态——下面的检查和编辑都在一个活动的编辑器中运行 C#。

**`unity-cli` 技能负责带你到达那里**——安装 CLI、确认连接的编辑器、添加项目的 `com.unity.pipeline` 包、告诉一个真正缺失的编辑器与卡在安全模式中的编辑器区别开来，并发现编辑器的命令目录。首先跟随它；不要在这里重新推导任何内容。你需要 `eval`，而不仅仅是一个可访问的编辑器：它的存在取决于 Pipeline 包版本，而与 CLI 无关。如果它缺失，请说明并停止。

使用连接的编辑器通过 `eval` 命令运行 C#。从 `unity command --format json` 而不是假设一个来发现其参数形状——内联形式是 `unity command eval --code '<snippet>'`，一些 Pipeline 版本还注册 `eval_file` 来从文件运行一个片段。**在触及 `eval_file` 之前检查目录；它经常是缺失的。** `unity command` 默认超时时间为 30 秒。

### 将 C# 传递给 `eval`

`eval` 编译一个**语句块，而不是文件**。有两个后果，两者都会导致编译错误而不是警告：

- **没有 `using` 指令。** 编译器将 `using UnityEngine;` 读取为资源释放语句并拒绝它 (`CS0210`)。
- **类型必须完全限定。** 一个裸的 `AssetDatabase` 或 `Volume` 无法解析 (`CS0246` / `CS0103`)，而一个裸的 `Object` 与 `object` 模棱两可 (`CS0104`)。

当下面片段以文件形式编写时——由于可读性或因为它打算保存到项目中——在传递给它之前限定类型。

## 0. 飞行前检查

配置任何效果之前，**验证所有检查**。首先修复失败。

1. **URP 是活动的渲染管线**——如果不是，通知用户并停止。
2. **URP 资产上启用了 HDR**——这对于色调映射是必需的。Bloom 在 HDR 下效果最佳；在 SDR 下它仍然工作，但 `threshold` 必须小于 1。
3. **相机启用了后期处理**——`renderPostProcessing` 必须为 `true`（默认为 `false`）。相机堆叠：只有 `CameraRenderType.Base` 相机（或堆叠中的最后一个 `Overlay`）应启用后期处理。还请验证渲染器的 PostProcessData 资产是否为 null——如果是，后期处理通道将不存在。
4. **Volume 的 GameObject 层在相机的 Camera Volume Layer Mask 中**——`volumeLayerMask` 默认为层 0 "Default" 仅。Volume 的 `GameObject.layer` 必须包含在内，否则相机会忽略它。
5. **Volume 存在，`enabled = true`，具有有效的配置文件，并且至少有一个覆盖**——`Volume` 组件必须启用，具有非空的 `profile`（或 `sharedProfile`），并且至少有一个 `VolumeComponent` 在其属性上具有 `overrideState = true`。

### 飞行前检查片段

运行此代码以按程序验证设置：

```csharp
// `eval` 编译一个语句块，而不是文件：不允许 `using` 指令，因此每个类型都是完全限定的。
var report = new System.Text.StringBuilder();

// 1. 检查 URP 是否活动——硬停止，因此抛出：它大声失败
var urpAsset = UnityEngine.Rendering.Universal.UniversalRenderPipeline.asset;
if (urpAsset == null)
    throw new System.Exception("URP 不是活动的渲染管线。");

// 2. 检查 HDR
if (!urpAsset.supportsHDR)
    report.AppendLine("警告：URP 资产上禁用了 HDR。色调映射将无法工作；Bloom 需要 threshold < 1。");

// 3. 检查相机后期处理
var cam = UnityEngine.Camera.main;
if (cam == null)
    throw new System.Exception("未找到主相机。");
if (!cam.TryGetComponent<UnityEngine.Rendering.Universal.UniversalAdditionalCameraData>(out var camData))
    throw new System.Exception("相机上缺少 UniversalAdditionalCameraData。URP 是否活动？");
if (!camData.renderPostProcessing)
    report.AppendLine("警告：相机上禁用了后期处理。通过 camData.renderPostProcessing = true 启用。");

// 4. 检查 Volume 层掩码
var volumes = UnityEngine.Object.FindObjectsByType<UnityEngine.Rendering.Volume>(UnityEngine.FindObjectsSortMode.None);
foreach (var vol in volumes)
{
    if (!vol.enabled) { report.AppendLine($"警告：Volume '{vol.name}' 已禁用。"); continue; }
    if ((camData.volumeLayerMask & (1 << vol.gameObject.layer)) == 0)
        report.AppendLine($"警告：Volume '{vol.name}' 在层 {vol.gameObject.layer} 上不在相机的 volumeLayerMask 中。");
    // 5. 检查配置文件和覆盖
    var profile = vol.sharedProfile;
    if (profile == null) { report.AppendLine($"警告：Volume '{vol.name}' 没有分配配置文件。"); continue; }
    if (profile.components.Count == 0)
        report.AppendLine($"警告：Volume '{vol.name}' 配置文件没有覆盖。");
}

// 返回结果：日志记录在编辑器控制台中，返回值返回给您
return report.Length == 0 ? "后期处理设置看起来正确。" : report.ToString();
```

## 1. Volume 设置

效果作为 **VolumeComponent 覆盖** 添加到 **VolumeProfile**（一个 `ScriptableObject`）上。

**全局 Volume**（最常见）：带有 `Volume` 组件的 GameObject，`isGlobal = true`，分配了 `profile`。它影响所有 `volumeLayerMask` 包含 Volume 的层的相机。

**局部 Volume（可选，但优先级更高）**：带有触发 `Collider` + `Volume` 组件的 GameObject，`isGlobal = false`。属性：
- `priority`（float）——值越高，在 Volume 重叠时覆盖越低。
- `blendDistance`（float）——从碰撞器边界开始混合的世界单位距离（0 = 无混合，碰撞器边界处立即过渡）。
- `weight`（float，0–1）——按比例缩放 Volume 的整体影响。

## 2. 后期处理效果

所有效果都是 `VolumeComponent` 子类，通过 `profile.Add<T>()` 添加到 `VolumeProfile` 上。检查存在性使用 `profile.Has<T>()` 或 `profile.TryGet<T>(out var t)`。移除使用 `profile.Remove<T>()`。

每个属性都是 `VolumeParameter`。您 **必须** 在设置 `value` 之前设置 `overrideState = true`，否则 Volume 系统会忽略它。

配置特定效果时，加载完整的 API 参考：
- [references/effect-reference.md](references/effect-reference.md) — 按效果的所有 VolumeComponent 属性（Bloom、色调映射、ColorAdjustments、DepthOfField、Vignette、MotionBlur、FilmGrain、ChromaticAberration、SplitToning、LensDistortion、WhiteBalance、PaniniProjection、LiftGammaGain、ShadowsMidtonesHighlights、ColorCurves、ChannelMixer）

对于代码模板：
- [references/code-templates.md](references/code-templates.md) — 全局 Volume 设置、相机后期处理和配置文件修改模板

## 3. 抗幻觉规则

### 必须的 Usings

当您将 `.cs` 文件写入项目时，这些规则适用。**传递给 `eval` 的片段不能携带它们**——相反，请限定类型（见上文的“将 C# 传递给 `eval`”）。

```csharp
using UnityEngine.Rendering;           // Volume, VolumeProfile, VolumeComponent, VolumeParameter
using UnityEngine.Rendering.Universal;  // Bloom, Tonemapping, ColorAdjustments, UniversalRenderPipeline, 等。
```

### 错误 → 正确 API 映射

| 错误 | 正确 |
|------|------|
| `PostProcessVolume` | `Volume`（来自 `UnityEngine.Rendering`） |
| `PostProcessLayer` | `UniversalAdditionalCameraData.renderPostProcessing`（bool） |
| `UnityEngine.Rendering.PostProcessing` | `UnityEngine.Rendering.Universal` |
| `profile.GetSetting<T>()` | `profile.TryGet<T>(out var t)`（返回 bool） |
| `profile.AddSettings<T>()` | `profile.Add<T>()`（返回 T；如果已存在则抛出——首先检查 `profile.Has<T>()`） |
| `volume.sharedProfile`（在运行时修改） | `volume.profile`（自动克隆资产到实例） |
| `VolumeManager.instance.stack.GetComponent<T>()` | `volume.profile.TryGet<T>(out var t)` |

### 关键事实
- **`overrideState = true`** 对您设置的每个 `VolumeParameter` 都是必需的。Volume 系统会忽略 `overrideState` 为 `false` 的参数。这是脚本编写中的第一个错误。
- **`sharedProfile`** = 返回资产本身（编辑持久化到磁盘）。**`profile`** = 如果需要，自动克隆到实例（安全用于运行时编辑）。使用 `volume.HasInstantiatedProfile()` 进行检查。
- **`profile.Add<T>(bool overrides = false)`** — 传递 `true` 以自动在添加组件的所有参数上启用 `overrideState`。

## 4. 调试检查清单

后期处理不起作用时，按顺序检查：

1. `cam.TryGetComponent<UniversalAdditionalCameraData>(out var data)` 成功并且 `data.renderPostProcessing` 为 `true`？
2. 场景中存在 Volume，并且分配了非空的 `profile`（或 `sharedProfile`）？
3. 通过 `profile.Add<T>()` 添加的覆盖 AND 每个您设置的属性上的 `overrideState = true`？
4. Volume 的 `GameObject.layer` 包含在相机的 `data.volumeLayerMask` 中？（默认掩码仅包含层 0 "Default"。）
5. `volume.isGlobal = true`（对于全局），或相机在 Volume 的触发 `Collider` 内部（对于局部）？
6. 相机 `data.renderType` 是 `CameraRenderType.Base`，而不是 `Overlay`？（Overlay 相机在 Base 相机的输出上合成。）
7. `UniversalRenderPipeline.asset.supportsHDR` 为 `true`？Bloom 和色调映射需要它。
8. 在 **Game 视图**中查看？场景视图的工具栏中有单独的后期处理切换。

## 5. 常见配方

格式：效果属性=值。Bloom 值是阈值/强度/散焦。

**电影（胶片）**：色调映射模式=ACES，ColorAdjustments 对比度=15 饱和度=-10，Bloom 阈值=0.9 强度=0.5 散焦=0.7，Vignette 强度=0.3 平滑度=0.4，FilmGrain 类型=Medium1 强度=0.2

**风格化/鲜艳**：色调映射模式=中性，ColorAdjustments 饱和度=20 对比度=10，Bloom 阈值=0.8 强度=1.5 散焦=0.6，SplitToning 高光=暖色 阴影=冷色

**恐怖/黑暗**：ColorAdjustments 后曝光=-0.5 饱和度=-30 对比度=20，Vignette 强度=0.5 平滑度=0.3 颜色=深红色，FilmGrain 类型=Large01 强度=0.4，ChromaticAberration 强度=0.15

**干净/移动**：色调映射模式=中性，ColorAdjustments 后曝光=0.2，Bloom 阈值=1.0 强度=0.3（微妙）。避免在移动设备上使用 FilmGrain、MotionBlur、DepthOfField。

## 6. 最终确认

设置完成后，向用户报告：

```
后期处理设置完成
- Volume：[全局/局部] 在 "[GameObject Name]"
- 配置文件：[资产路径]
- 效果：[带有键属性=值对的列表]
- 相机：[名称] — renderPostProcessing=true，volumeLayerMask 包含层 [N]

在 Game 视图中查看结果（不要在场景视图中查看）。
使用 Edit > Undo（Ctrl+Z）撤销所有更改。
```
