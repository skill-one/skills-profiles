# Godot 着色器 (4.x)

使用 Godot 着色器语言编写 `canvas_item` (2D) 和 `spatial` (3D) 着色器，使用 `TIME`/`UV` 进行动画，暴露 `uniform`，并读取屏幕。目标 **Godot 4.7**。

## 何时使用

- 当编写 `.gdshader` 代码或使用 `ShaderMaterial` 时使用：2D 特效（轮廓、溶解、闪烁、水波），3D 表面着色器（边缘光、卡通风格、滚动 UV），或屏幕空间后处理效果。

**不使用时**：跨引擎的着色概念（UV、顶点/片元理论）→ `shader-programming`；粒子/VFX 节点 → 一般 3D；非着色器视觉效果。

## 核心工作流程

1. **在第一行选择着色器类型**：`shader_type canvas_item;` 用于 2D（Sprite2D、TextureRect、任何 `CanvasItem`）或 `shader_type spatial;` 用于 3D 材质。(`particles`、`sky`、`fog` 也存在。)
2. **通过 `ShaderMaterial` 进行附加**。创建 `ShaderMaterial`，分配你的 `.gdshader`，并将其放在节点的 `material` 上。Uniforms 会出现在 Inspector 中。
3. **编写 `fragment()`** 来设置输出：`COLOR` (2D) 或 `ALBEDO`/`EMISSION`/`ALPHA` (3D)。可选地 `vertex()` 来移动几何体，`light()` 用于自定义光照。
4. **将可调参数暴露为 `uniform`** 并使用提示 (`source_color`, `hint_range`) 以便它们可编辑并正确进行色彩管理。
5. **使用内置的 `TIME` 进行动画**，并使用 `texture(tex, UV)` 采样纹理。
6. **通过代码设置 uniforms** 使用 `material.set_shader_parameter("name", value)`。

## 模式

### 1. 2D (canvas_item)：色调 + 滚动 UV

```glsl
shader_type canvas_item;

uniform vec4 tint : source_color = vec4(1.0);     // source_color = sRGB-correct 颜色
uniform float scroll_speed : hint_range(0.0, 2.0) = 0.3;

void fragment() {
    vec2 uv = UV;
    uv.x += TIME * scroll_speed;                  // 随时间水平滚动
    COLOR = texture(TEXTURE, uv) * tint;          // TEXTURE = 节点的纹理
}
```

### 2. 2D 使用噪声阈值进行溶解

```glsl
shader_type canvas_item;

uniform sampler2D noise : repeat_enable;          // 一个 NoiseTexture2D
uniform float amount : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float n = texture(noise, UV).r;
    if (n < amount) {
        discard;                                  // 删除像素
    }
    COLOR = tex;
}
```

### 3. 3D (spatial)：自发光边缘光

```glsl
shader_type spatial;

uniform vec4 base_color : source_color = vec4(0.2, 0.5, 1.0, 1.0);
uniform vec3 rim_color : source_color = vec3(0.6, 0.8, 1.0);
uniform float rim_power : hint_range(0.5, 8.0) = 3.0;

void fragment() {
    ALBEDO = base_color.rgb;
    // VIEW 和 NORMAL 是视图空间内置变量；边缘光在掠射角时很强。
    float rim = pow(1.0 - dot(NORMAL, VIEW), rim_power);
    EMISSION = rim_color * rim;
}
```

### 4. 屏幕读取后处理效果 (4.x 提示，不是 SCREEN_TEXTURE)

```glsl
shader_type canvas_item;

// 4.x: 将屏幕声明为 uniform 并使用 hint_screen_texture。
uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float blur : hint_range(0.0, 4.0) = 1.0;

void fragment() {
    vec2 px = SCREEN_PIXEL_SIZE * blur;
    vec4 c = texture(screen_tex, SCREEN_UV);
    c += texture(screen_tex, SCREEN_UV + vec2(px.x, 0.0));
    c += texture(screen_tex, SCREEN_UV - vec2(px.x, 0.0));
    COLOR = c / 3.0;
}
```

从 GDScript 设置 uniform：

```gdscript
$Sprite2D.material.set_shader_parameter("amount", 0.7)
```

## 陷阱

- **3.x → 4.x 重命名**。`SCREEN_TEXTURE` 已移除 — 声明 `uniform sampler2D x : hint_screen_texture;` 并使用 `SCREEN_UV` 采样。颜色提示 `hint_color`→`source_color`；`hint_albedo`/`hint_white`→`source_color`；`hint_range` 保持不变。深度/法线使用 `hint_depth_texture` / `hint_normal_roughness_texture`。
- **错误的输出变量**。在 `canvas_item` 中写 `COLOR`；在 `spatial` 中写 `ALBEDO`（和 `EMISSION`、`ALPHA`、`ROUGHNESS`、`METALLIC`）。在空间着色器中写 `COLOR` 无效。
- **没有 `source_color` 的颜色 uniforms** 被视为原始线性值且看起来不正确（发灰/发暗），因为 Godot 不会将它们 sRGB 转换。
- **透明度需要选择加入 (3D)**。对于 `ALPHA < 1.0` 要混合，添加渲染模式或设置材质透明度；否则它是完全不透明/切割的。
- **在 [0,1] UV 外采样** 没有 `repeat_enable` 会钳位。在采样 uniform 中添加 `: repeat_enable` 以进行平铺/滚动。
- **`TIME` 是自开始以来的秒数** 并不断增长 — 使用 `fract()`/`mod()` 进行周期性效果以避免精度漂移。
- **`discard` 在某些硬件上很昂贵** 并会破坏早期-Z；当可以时，优先设置 `ALPHA`/`COLOR.a`。

## 参考

- 关于每个着色器类型的内置变量、渲染模式、`varying`、自定义 `light()`、`vertex()` 位移以及视觉着色器图，请阅读 `references/shading-language.md`。

## 相关技能

- `shader-programming` — 引擎无关的着色概念 (GLSL/HLSL)。
- `godot-3d-essentials` — 材质、环境和空间着色器所在位置。
- `godot-ui-control` — 将着色器应用于 UI 以实现特效。
