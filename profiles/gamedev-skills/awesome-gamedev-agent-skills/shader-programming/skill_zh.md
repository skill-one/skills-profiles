# 着色器编程（跨引擎）

着色器是运行在 GPU 上，**每个顶点**和**每个像素**的小程序。
这些概念——渲染管线、坐标系、UV 值以及常见效果的构建方式——可以在不同引擎间移植；只有语言方言和内置变量名称会发生变化。本技能通过 GLSL 介绍这些可移植的基础知识，并提供 HLSL 等价方案；使用 `godot-shaders`（或 Unity/Unreal 材质文档）来获取特定引擎的语法和内置函数。

## 使用场景

- 用于理解或编写顶点/片元着色器，并思考 UV 值、坐标系和 GPU 渲染管线。
- 用于构建常见效果：色调调整/重新上色、滚动纹理、溶解、轮廓线、菲涅尔/边缘光、暗角、色彩分级。
- 用于在 GLSL 和 HLSL 之间，或在不同引擎之间转换着色器概念。

**不适用场景：** 若要使用特定引擎的着色器语言和内置函数，请使用 `godot-shaders`（Godot 着色器语言）或引擎的材质文档。对于完整的粒子 VFX 系统，请参考 `unreal-niagara`。对于后处理 *堆栈*，请参考引擎的渲染器设置。

## 核心工作流程

1. **明确当前阶段。** 顶点着色器将每个顶点转换到裁剪空间，并传递数据（UV 值、法线）给下一阶段；片元/像素着色器针对每个光栅化像素运行并输出颜色。大多数游戏效果都存在于片元阶段。
2. **跟踪坐标系。** 位置从模型空间→世界空间→视图空间→裁剪空间移动；法线属于世界空间或视图空间。混合坐标系是最常见的错误来源。
3. **使用 UV 值和时间控制效果。** UV 值是 `0..1` 的纹理坐标；偏移、缩放或扭曲它们，并使用 `time` uniform 进行动画。
4. **逐像素处理，避免分支。** 尽可能使用 `mix`、`step`、`smoothstep` 和 `clamp` 而非 `if`；GPU 以同步方式运行像素，不喜欢单分支。
5. **通过 uniform（每绘制一次的常量）和 varying（顶点→片元插值）传递数据。** 保持纹理采样数量较少；它们是成本的主要来源。
6. **在目标硬件上进行可视化和验证。** 在桌面端看起来正确的着色器可能在移动端失效（精度问题、缺失特性）。在发布目标平台测试。

## 模式

GLSL 风格的片元代码片段（接近 Godot 的 `canvas_item`/`spatial` 着色器和 OpenGL）。参考 `references/effects.md` 获取 HLSL 等价方案和完整的轮廓线/菲涅尔/暗角着色器。

### 1. 片元基础：采样、色调调整和组合

```glsl
// 逐像素：在当前 UV 处读取纹理，乘以颜色（色调调整），保留 alpha。
uniform sampler2D tex;
uniform vec4 tint;          // 例如 (1,0,0,1) 使其变红；乘法是非破坏性的
in vec2 uv;                 // 插值 0..1 纹理坐标（一个 "varying"）
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);   // HLSL: tex.Sample(samp, uv)
    frag = c * tint;             // 分量乘法进行色调调整，不裁剪
}
```

### 2. 滚动 UV（动画纹理）——帧率无关

```glsl
// 在 UV 中添加时间 * 速度以滚动。fract() 将其包装到 0..1，使其平铺。
uniform sampler2D tex;
uniform float time;          // 秒，由引擎提供
uniform vec2 scroll_speed;   // 每秒 UV 单位，例如 (0.1, 0.0)
in vec2 uv;
out vec4 frag;
void main() {
    vec2 scrolled = fract(uv + scroll_speed * time);  // HLSL: frac(...)
    frag = texture(tex, scrolled);
}
// 使用真实时间 uniform 而非每帧累积器，以保持速度稳定。
```

### 3. 溶解（对噪声图进行阈值处理，边缘发光）

```glsl
// 隐藏噪声值小于阈值的像素；在边界处为发光边缘着色。
uniform sampler2D tex;
uniform sampler2D noise_tex;     // 灰度噪声，0..1
uniform float amount;            // 0 = 完全可见，1 = 完全溶解
uniform float edge = 0.05;       // 发光边缘带的宽度
uniform vec4 edge_color;
in vec2 uv;
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);
    float n = texture(noise_tex, uv).r;
    if (n < amount) discard;                 // 删除溶解的像素
    float e = smoothstep(amount, amount + edge, n);  // 边缘处为 0 -> 内部为 1
    frag = mix(edge_color, c, e);            // HLSL: lerp(edge_color, c, e)
}
```

### 4. 菲涅尔边缘光（3D）——增强掠射角度

```glsl
// Rim = 1 当表面背向相机时（剪影发光）。
in vec3 world_normal;        // 归一化，世界空间（来自顶点阶段）
in vec3 view_dir;            // 归一化，表面→相机，世界空间
uniform float power = 3.0;
uniform vec3 rim_color;
out vec4 frag;
void main() {
    float f = pow(1.0 - clamp(dot(world_normal, view_dir), 0.0, 1.0), power);
    frag = vec4(rim_color * f, 1.0);   // 添加到光照；f 在剪影处达到峰值
}
// 正确性：法线和视图方向必须在同一空间且归一化。
```

## 陷阱

- **混合坐标系**（用世界空间法线对视图空间光源进行光照）会导致轻微错误的着色。选择一个空间，并将所有内容转换到该空间。
- **忘记归一化**插值法线/方向：插值会缩短向量，导致 `dot()` 结果漂移。在片元阶段使用 `normalize()`。
- **跨引擎的 UV 假设。** 某些引擎会翻转 V（左上角 vs 左下角原点）；纹理可能颠倒。了解你的引擎约定。
- **大量分支 / 动态循环** 会阻塞 GPU。优先使用 `step`/`smoothstep`/`mix`；将 `if`/`discard` 用于真正的廉价提前退出。
- **`discard` 会破坏早期 Z**，并可能影响分块移动端 GPU 的性能；尽可能使用 alpha 混合。
- **移动端精度**：`highp` vs `mediump` 很重要；低精度中的大 UV 值或时间值会闪烁。为坐标和时间使用适当的精度。
- **假设 GLSL == HLSL。** `mix`↔`lerp`，`fract`↔`frac`，`texture()`↔`.Sample()`，`vec2`↔`float2`，列主序 vs 行主序矩阵。参考 `references/effects.md` 中的映射表。

## 参考

- `references/effects.md` — 完整的轮廓线（2D 图标 + 3D）、暗角和色彩分级着色器；GLSL↔HLSL 函数/类型映射表；各引擎注意事项（Godot `canvas_item`/`spatial`，Unity ShaderLab/HLSL，Unreal 材质节点）。

## 相关技能

- `godot-shaders` — Godot 着色器语言语法、内置函数和屏幕阅读。
- `unreal-niagara` — GPU 粒子 VFX（不同的着色器使用方式）。
- `procedural-gen` — 驱动溶解和程序化纹理的噪声。
