设置、诊断和修复 Unity 项目中的像素完美 2D 渲染。

---

## ⚠️ 存在两种完全独立的实现

Unity 中的像素完美渲染**不是一套系统**——它是两个独立且不兼容的实现，每个渲染管线一个。**在编写或诊断任何代码之前，始终检测渲染管线。** 

| | URP | 内置 |
|---|---|---|
| **组件** | `UnityEngine.Rendering.Universal.PixelPerfectCamera` | `UnityEngine.U2D.PixelPerfectCamera` |
| **包** | 内置于 URP — 无需额外安装 | `com.unity.2d.pixel-perfect` v6.0.0+ |
| **API 风格** | 枚举 (`gridSnapping`, `cropFrame`) | 布尔值 (`pixelSnapping`, `upscaleRT`, `cropFrameX/Y`) |

**不要在 URP 项目中安装 `com.unity.2d.pixel-perfect`。**

**→ 首先调用 `DetectPipeline()`** (`references/pipeline-detection.cs`), 然后根据结果分支您的设置、诊断和修复。

---

## 不应使用此技能的情况

- **HD 2D 或高分辨率 2D 游戏** — 像素对齐和点过滤会使平滑的艺术效果看起来不正确
- **仅 UI 场景** — 使用 Canvas Scaler
- **HDRP 项目** — Pixel Perfect Camera 不受支持

---

## 关键提示

⚠️ **首先检测渲染管线** — URP 和内置使用不同的 Pixel Perfect Camera 组件，它们不能互换。
⚠️ **Filter Mode = Point 是首要修复方法** — 双线性过滤是 Unity 的默认设置，几乎总是导致模糊的精灵。
⚠️ **必须禁用抗锯齿** — 在质量设置和相机上。AA 会主动模糊像素边缘。

## 关键原则

### 1. 渲染管线检测与相机组件选择

查看此文件顶部的双路径比较表。程序集名称说明：独立的内置包安装在 `Runtime/` 文件夹中，但 asmdef `"name"` 字段是 `Unity.2D.PixelPerfect` — 没有 `Runtime` 后缀。HDRP 不受支持 — 请参阅常见问题中的 HDRP 降级部分。

**→ 代码: `references/pipeline-detection.cs`** — `DetectPipeline()`, `GetPixelPerfectCameraType()` 和迁移不匹配检查。

### 2. 以诊断为先的方法

始终在做出更改之前进行诊断。报告发现的问题，然后只修复已损坏的部分。

### 3. 在正确的范围内工作

默认使用场景范围。仅在用户明确要求时才扫描整个项目。

---

## 诊断清单

**精灵导入设置:**
- [ ] Filter Mode = `Point (无过滤)` 在所有范围内的精灵上
- [ ] Mip Maps = 禁用
- [ ] 压缩 = `None` / 未压缩
- [ ] PPU 在场景中所有精灵之间保持一致
- [ ] 精灵轴心点设置为自定义 / 像素模式 — 奇数维度的精灵（例如 15×15）上的中心轴心点位于 7.5px，导致 0.5px 位移

**→ 代码: `references/sprite-settings.cs`** — `GetImporter()` 和 `FixSpriteImportSettings()`。

**编辑器对齐设置:**
- [ ] Grid Size = `1 / assetsPPU` 在所有轴上（例如 PPU 16 → 0.0625, PPU 100 → 0.01）
- [ ] 在网格和对齐覆盖层中启用 Grid Snapping
- [ ] 要对齐现有 GameObjects：选择它们 → Align Selected → 所有轴

**相机设置:**
- [ ] 相机投影 = 正交
- [ ] Pixel Perfect Camera 组件存在且类型正确
- [ ] `allowHDR`, `allowMSAA`, `allowDynamicResolution` 都为 `false`
- [ ] 场景视图在相机 Gizmo 上显示两个绿色边界框 — 实线 = 可见区域，虚线 = 参考分辨率

**→ 代码: `references/camera-setup-urp.cs`** — 完整的 URP 相机 + PP 相机配置。
**→ 代码: `references/camera-setup-builtin.cs`** — 独立的内置配置。

**项目质量设置:**
- [ ] Anti-Aliasing = 0 在质量设置中
- [ ] Anisotropic Filtering = 禁用

---

## API 参考

完整的属性/方法表、`GridSnapping` 和 `CropFrame` 枚举值以及推荐配置：
**→ `references/api-reference.md`** — 在编写或审查相机设置代码时阅读此内容。

快速枚举总结：

**`GridSnapping`**: `None` · `PixelSnapping` (标准) · `UpscaleRenderTexture` (逼真的低分辨率；与后期处理和 UI 文本不兼容)

**`CropFrame`**: `None` · `Pillarbox` · `Letterbox` · `Windowbox` (最安全的默认值) · `StretchFill`

---

## 参考分辨率

在构建任何资源之前选择。在资源生产开始后永远不要更改。

| 参考分辨率 | 1080p | 1440p | 4K |
|---|---|---|---|
| 320 × 180 | 6× | 8× | 12× |
| 480 × 270 | 4× | ~5.3× | 8× |
| 640 × 360 | 3× | 4× | 6× |

320×180 是最安全的通用选择。对于没有整数适配的屏幕（例如 1366×768），使用 `cropFrame = Windowbox` 添加黑边，而不是拉伸到分数比例。

---

## 迁移与兼容性

### URP 项目中使用内置独立组件

**症状**: `DetectPipeline()` 返回 URP，但相机具有 `UnityEngine.U2D.PixelPerfectCamera`。症状不明显，因为独立组件具有 `ENABLE_URP` 条件代码。

**修复**:
1. 从包管理器中删除 `com.unity.2d.pixel-perfect`
2. 从每个相机中删除 `UnityEngine.U2D.PixelPerfectCamera`
3. 添加 `UnityEngine.Rendering.Universal.PixelPerfectCamera`
4. 重新配置 — 布尔值 (`pixelSnapping`, `upscaleRT`, `cropFrameX/Y`) 变为枚举 (`gridSnapping`, `cropFrame`)

**→ 检测代码: `references/pipeline-detection.cs`** (文件底部)。

### 旧的 URP 命名空间（Unity 2022 之前 / URP 13.x 之前）

**症状**: 编译器错误引用 `UnityEngine.Experimental.Rendering.Universal`。

**修复**: 将 `using UnityEngine.Experimental.Rendering.Universal;` 替换为 `using UnityEngine.Rendering.Universal;`。更新任何限定类型字符串。`[MovedFrom]` 属性自动处理序列化 — GameObjects 上的组件在升级后仍然存在。

---

## 常见问题与解决方案

### 模糊的精灵
**修复**: 在所有范围内的精灵上设置 Filter Mode 为 Point，禁用 Mip Maps，在质量设置中禁用 AA。
**→ 代码: `references/sprite-settings.cs`**

### Tilemap 砖块之间的间隙
按顺序处理 — 类似于负数单元格间隙或 PPU = 31.99 的解决方案会在相机移动时失效。

| # | 检查 | 修复 |
|---|---|---|
| 1 | 精灵图集 Tight Packing 关闭，Padding ≥ 4，Sprite Packer 模式启用？ | 在编辑器设置中启用 Sprite Packer 模式；在图集上设置 Padding ≥ 4 并关闭 Tight Packing |
| 2 | 砖块集纹理和图集禁用 Mipmaps？ | 禁用 Generate Mip Maps |
| 3 | 相机上 AA = 0，MSAA 关闭？ | 全局禁用 AA |
| 4 | 压缩 = None？ | RGBA 32 位未压缩 |
| 5 | 所有砖块精灵都有偶数像素维度？ | 奇数维度导致 0.5px 网格偏移 |
| 6 | PPU = 砖块像素宽度？（16×16 → PPU 16） | PPU 不匹配会导致物理间隙 |
| 7 | 仅在相机移动后所有上述检查通过？ | 使用 PP 相机像素对齐；不要使用 `cellGap = -0.01f` |

### Cinemachine 冲突
**原因**: Cinemachine 和 Pixel Perfect Camera 每帧都写入正交大小。

**修复**: 通过每个虚拟相机的添加扩展下拉菜单添加 `CinemachinePixelPerfect` 扩展。不要通过代码中的 `AddComponent` 添加。

**已知限制**:
- 相机在虚拟相机之间混合时在过渡期间不是像素完美的
- `UpscaleRenderTexture` 减少了有效的像素完美正交大小，可能导致构图偏差
- Target Group + Framing Transposer 导致可见的卡顿（无修复方法）

### 使用 `upscaleRT` 的后期处理模糊
**原因**: 后期处理在 PP 相机上 upscale 渲染纹理之后运行。

**简单修复**: 禁用 `upscaleRT`。后期处理然后在原生屏幕分辨率下运行。

**高级修复（Unity 6 URP）**: 在 `RenderPassEvent2D.AfterRenderingPostProcessing` 注入 `ScriptableRendererFeature2D`。使用 2D 特定的基类 — `ScriptableRendererFeature` (3D 基类) 在 URP 2D 渲染器中会被静默忽略。

### 使用 `upscaleRT` 的模糊 UI 文本
**状态**: 已知的 Unity Bug，拒绝修复（Unity 6, 2025 年仍然存在）。

**根本原因**: (A) Canvas 渲染到低分辨率缓冲区，并随场景 upscale。 (B) TMP 的 SDF 渐变阈值在低参考分辨率下校准不正确。

**按可靠性顺序的修复方法**:
1. Canvas 上的 `Screen Space - Overlay` — 跳过相机，以原生分辨率渲染
2. 专用 UI 相机，无 PP Camera 组件，`Screen Space - Camera` 模式
3. Unity 6 仅限: `Font Material → Debug Settings → Sharpness = 1` (缓解 B，不缓解 A)

### Physics / 渲染不同步（微卡顿）
**原因**: Physics 在固定步长下运行；插值位置产生分数值，每帧对齐到不同的像素。

**修复**:
- 在物理驱动的精灵上启用 `Rigidbody2D.interpolation = RigidbodyInterpolation2D.Interpolate`
- 设置 `Time.fixedDeltaTime = 1f / 60f` 以匹配目标帧率
- 将相机跟踪保持在 `LateUpdate`，而不是 `FixedUpdate`

### 非整数缩放 / 像素减化
**原因**: 屏幕分辨率不是参考分辨率的整数倍。

**修复**: 从上表中选择参考分辨率。当不存在整数适配时使用 `cropFrame = Windowbox`。

### 缺失 URP 2D Renderer
**修复**:
1. `Assets > Create > Rendering > URP 2D Renderer Data`
2. 将其分配给 URP 资产下的 Renderer List
3. 需要 `com.unity.render-pipelines.universal` 12.0+

### HDRP 降级
Pixel Perfect Camera 在 HDRP 中不受支持。

**内置 / Unity 5.x**: 使用 `RenderTexture` + `Graphics.Blit` 并设置 `FilterMode.Point`。

**Unity 6 URP**: 使用 `ScriptableRendererFeature2D` + `ScriptableRenderPass2D` 在 `RenderPassEvent2D.AfterRendering` 注入，使用 `AddRasterRenderPass`。注意: `OnRenderImage` 和 `Graphics.Blit` 与 Unity 6 的渲染图不兼容。
