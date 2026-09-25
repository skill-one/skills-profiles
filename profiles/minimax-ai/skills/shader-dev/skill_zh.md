# Shader Craft

一个涵盖 36 种 GLSL 着色器技术（ShaderToy 兼容）的统一技能，用于实时视觉特效。

## 调用方式

```
/shader-dev <请求>
```

`$ARGUMENTS` 包含用户的请求（例如："创建一个使用光线追踪的 SDF 场景，带有柔和阴影"）。

## 技能结构

```
shader-dev/
├── SKILL.md                      # 核心技能（此文件）
├── techniques/                   # 实现指南（根据路由表阅读）
│   ├── ray-marching.md           # 使用 SDF 的球体追踪
│   ├── sdf-3d.md                 # 3D 符号距离函数
│   ├── lighting-model.md         # PBR、Phong、卡通着色
│   ├── procedural-noise.md       # Perlin、Simplex、FBM
│   └── ...                       # 34 个其他技术文件
└── reference/                    # 详细指南（按需阅读）
    ├── ray-marching.md           # 数学推导 & 高级模式
    ├── sdf-3d.md                 # 扩展 SDF 理论
    ├── lighting-model.md         # 光照数学深入解析
    ├── procedural-noise.md       # 噪声函数理论
    └── ...                       # 34 个其他参考文件
```

## 使用方法

1. 阅读 **技术路由表**（见下文），以确定哪些技术匹配用户的请求
2. 从 `techniques/` 中阅读相关文件 — 每个文件包含核心原理、实现步骤和完整的代码模板
3. 如果需要更深入的理解（数学推导、高级模式），请遵循每个技术文件底部的参考链接到 `reference/`
4. 在生成独立的 HTML 页面时，应用 **WebGL2 适配规则**（见下文）

## 技术路由表

| 用户想要创建... | 主要技术 | 结合使用 |
|---|---|---|
| 从数学创建 3D 对象/场景 | [ray-marching](techniques/ray-marching.md) + [sdf-3d](techniques/sdf-3d.md) | lighting-model, shadow-techniques |
| 复杂 3D 形状（布尔运算、混合） | [csg-boolean-operations](techniques/csg-boolean-operations.md) | sdf-3d, ray-marching |
| 3D 中无限重复的图案 | [domain-repetition](techniques/domain-repetition.md) | sdf-3d, ray-marching |
| 有机/扭曲的形状 | [domain-warping](techniques/domain-warping.md) | procedural-noise |
| 流体/烟雾/墨水效果 | [fluid-simulation](techniques/fluid-simulation.md) | multipass-buffer |
| 粒子效果（火焰、火花、雪花） | [particle-system](techniques/particle-system.md) | procedural-noise, color-palette |
| 基于物理的模拟 | [simulation-physics](techniques/simulation-physics.md) | multipass-buffer |
| 游戏生命/反应扩散 | [cellular-automata](techniques/cellular-automata.md) | multipass-buffer, color-palette |
| 海洋/水面 | [water-ocean](techniques/water-ocean.md) | atmospheric-scattering, lighting-model |
| 地形/景观 | [terrain-rendering](techniques/terrain-rendering.md) | atmospheric-scattering, procedural-noise |
| 云/雾/体积火焰 | [volumetric-rendering](techniques/volumetric-rendering.md) | procedural-noise, atmospheric-scattering |
| 天空/日落/大气层 | [atmospheric-scattering](techniques/atmospheric-scattering.md) | volumetric-rendering |
| 真实光照（PBR、Phong） | [lighting-model](techniques/lighting-model.md) | shadow-techniques, ambient-occlusion |
| 阴影（柔和/硬） | [shadow-techniques](techniques/shadow-techniques.md) | lighting-model |
| 环境光遮蔽 | [ambient-occlusion](techniques/ambient-occlusion.md) | lighting-model, normal-estimation |
| 路径追踪/全局光照 | [path-tracing-gi](techniques/path-tracing-gi.md) | analytic-ray-tracing, multipass-buffer |
| 精确光线几何相交 | [analytic-ray-tracing](techniques/analytic-ray-tracing.md) | lighting-model |
| 体积世界（类似 Minecraft） | [voxel-rendering](techniques/voxel-rendering.md) | lighting-model, shadow-techniques |
| 噪声/FBM 纹理 | [procedural-noise](techniques/procedural-noise.md) | domain-warping |
| 平铺 2D 图案 | [procedural-2d-pattern](techniques/procedural-2d-pattern.md) | polar-uv-manipulation |
| Voronoi/单元图案 | [voronoi-cellular-noise](techniques/voronoi-cellular-noise.md) | color-palette |
| 分形（Mandelbrot、Julia、3D） | [fractal-rendering](techniques/fractal-rendering.md) | color-palette, polar-uv-manipulation |
| 色彩分级/调色板 | [color-palette](techniques/color-palette.md) | — |
| 软件晕影/色调映射/故障 | [post-processing](techniques/post-processing.md) | multipass-buffer |
| 多通道乒乓缓冲区 | [multipass-buffer](techniques/multipass-buffer.md) | — |
| 纹理/采样技术 | [texture-sampling](techniques/texture-sampling.md) | — |
| 相机/矩阵变换 | [matrix-transform](techniques/matrix-transform.md) | — |
| 表面法线 | [normal-estimation](techniques/normal-estimation.md) | — |
| 极坐标/万花筒 | [polar-uv-manipulation](techniques/polar-uv-manipulation.md) | procedural-2d-pattern |
| 2D 形状/UI 从 SDF | [sdf-2d](techniques/sdf-2d.md) | color-palette |
| 程序化音频/音乐 | [sound-synthesis](techniques/sound-synthesis.md) | — |
| SDF 技巧/优化 | [sdf-tricks](techniques/sdf-tricks.md) | sdf-3d, ray-marching |
| 抗锯齿渲染 | [anti-aliasing](techniques/anti-aliasing.md) | sdf-2d, post-processing |
| 景深/运动模糊/镜头效果 | [camera-effects](techniques/camera-effects.md) | post-processing, multipass-buffer |
| 高级纹理映射/无平铺纹理 | [texture-mapping-advanced](techniques/texture-mapping-advanced.md) | terrain-rendering, texture-sampling |
| WebGL2 着色器错误/调试 | [webgl-pitfalls](techniques/webgl-pitfalls.md) | — |

## 技术索引

### 几何 & SDF
- **sdf-2d** — 用于形状、UI、抗锯齿渲染的 2D 符号距离函数
- **sdf-3d** — 用于实时隐式表面建模的 3D 符号距离函数
- **csg-boolean-operations** — 构造实体几何：并集、差集、交集（平滑混合）
- **domain-repetition** — 无限空间重复、折叠和有限平铺
- **domain-warping** — 使用噪声扭曲域，用于有机、流动的形状
- **sdf-tricks** — SDF 优化、包围体、二分搜索细化、空心、分层边缘、调试可视化

### 光线投射 & 光照
- **ray-marching** — 使用 SDF 的球体追踪，用于 3D 场景渲染
- **analytic-ray-tracing** — 封闭形式的光线-基元相交（球体、平面、盒子、环面）
- **path-tracing-gi** — 使用蒙特卡洛路径追踪的光线追踪全局光照
- **lighting-model** — Phong、Blinn-Phong、PBR（Cook-Torrance）和卡通着色
- **shadow-techniques** — 硬阴影、软阴影（半影估计）、级联阴影
- **ambient-occlusion** — 基于 SDF 的 AO、屏幕空间 AO 近似
- **normal-estimation** — 有限差分法线、四面体技术

### 模拟 & 物理
- **fluid-simulation** — Navier-Stokes 流体求解器：对流、扩散、压力投影
- **simulation-physics** — 基于 GPU 的物理：弹簧、布料、N 体重力、碰撞
- **particle-system** — 无状态和有状态粒子系统（火焰、雨、火花、星系）
- **cellular-automata** — 游戏生命、反应扩散（图灵图案）、沙模拟

### 自然现象
- **water-ocean** — Gerstner 波浪、FFT 海洋、衍射、水下雾
- **terrain-rendering** — 高度场光线追踪、FBM 地形、侵蚀
- **atmospheric-scattering** — Rayleigh/Mie 散射、神光、SSS 近似
- **volumetric-rendering** — 体积光线追踪：云、雾、火焰、爆炸

### 程序化生成
- **procedural-noise** — 值噪声、Perlin、Simplex、Worley、FBM、锯齿噪声
- **procedural-2d-pattern** — 砖块、六边形、Truchet、伊斯兰几何图案
- **voronoi-cellular-noise** — Voronoi 图、Worley 噪声、裂缝地球、晶体
- **fractal-rendering** — Mandelbrot、Julia 集、3D 分形（Mandelbox、Mandelbulb）
- **color-palette** — 余弦调色板、HSL/HSV/Oklab、动态色彩映射

### 后处理 & 基础设施
- **post-processing** — 软件晕影、色调映射（ACES、Reinhard）、暗角、色差、故障
- **multipass-buffer** — 乒乓 FBO 设置、跨帧状态持久化
- **texture-sampling** — 双线性、双三次、mipmap、程序化纹理查找
- **matrix-transform** — 相机看向、投影、旋转、轨道控制
- **polar-uv-manipulation** — 极坐标/对数极坐标、万花筒、螺旋映射
- **anti-aliasing** — SSAA、SDF 解析 AA、时间抗锯齿（TAA）、FXAA 后处理
- **camera-effects** — 景深（薄透镜）、运动模糊、镜头畸变、胶片颗粒、暗角
- **texture-mapping-advanced** — 双平面映射、避免纹理重复、光线微分过滤

### 音频
- **sound-synthesis** — GLSL 中的程序化音频：振荡器、包络、滤波器、FM 合成

### 调试 & 验证
- **webgl-pitfalls** — 常见 WebGL2/GLSL 错误：`fragCoord`、`main()` 包装器、函数顺序、宏限制、uniform 为空

## WebGL2 适配规则

所有技术文件使用 ShaderToy GLSL 风格。在生成独立的 HTML 页面时，应用以下适配：

### 着色器版本 & 输出
- 使用 `canvas.getContext("webgl2")`
- 着色器第一行：`#version 300 es`，片段着色器添加 `precision highp float;`
- 片段着色器必须声明：`out vec4 fragColor;`
- 顶点着色器：`attribute` → `in`，`varying` → `out`
- 片段着色器：`varying` → `in`，`gl_FragColor` → `fragColor`，`texture2D()` → `texture()`

### 片段坐标
- **使用 `gl_FragCoord.xy`** 而不是 `fragCoord`（WebGL2 没有内置 `fragCoord`）
```glsl
// 错误
vec2 uv = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
// 正确
vec2 uv = (2.0 * gl_FragCoord.xy - iResolution.xy) / iResolution.y;
```

### ShaderToy 模板 main() 包装器
- ShaderToy 使用 `void mainImage(out vec4 fragColor, in vec2 fragCoord)`
- WebGL2 需要 `void main()` 入口点 — 始终包装 mainImage：
```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // 着色器代码...
    fragColor = vec4(col, 1.0);
}

void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}
```

### 函数声明顺序
- GLSL 要求函数在使用前声明 — 要么在使用前声明，要么重新排序：
```glsl
// 错误 — getAtmosphere() 在 getSunDirection() 定义之前调用
vec3 getAtmosphere(vec3 dir) { return getSunDirection(); } // 错误!
vec3 getSunDirection() { return normalize(vec3(1.0)); }

// 正确 — 先定义被调用者
vec3 getSunDirection() { return normalize(vec3(1.0)); }
vec3 getAtmosphere(vec3 dir) { return getSunDirection(); } // 正常工作
```

### 宏限制
- `#define` 不能使用函数调用 — 使用 `const` 代替：
```glsl
// 错误
#define SUN_DIR normalize(vec3(0.8, 0.4, -0.6))

// 正确
const vec3 SUN_DIR = vec3(0.756, 0.378, -0.567); // 预先计算归一化值
```

### 脚本标签提取
- 提取着色器源代码时，确保 `#version` 是**第一个字符** — 使用 `.trim()`：
```javascript
const fs = document.getElementById('fs').text.trim();
```

### 常见陷阱
- **未使用的 uniform**：编译器可能优化掉未使用的 uniform，导致 `gl.getUniformLocation()` 返回 `null` — 始终以编译器无法优化的方式使用 uniform
- **循环索引**：在循环中使用运行时常量，而不是某些 ES 版本中的 `#define` 宏
- **地形函数**：像 `terrainM(vec2)` 这样的函数需要 XZ 分量 — 使用 `terrainM(pos.xz + offset)` 而不是 `terrainM(pos + offset)`

## HTML 页面设置

生成独立 HTML 页面时：

- Canvas 填满整个视口，窗口调整大小时自动调整大小
- 页面背景黑色，无滚动条：`body { margin: 0; overflow: hidden; background: #000; }`
- 实现 ShaderToy 兼容的 uniform：`iTime`、`iResolution`、`iMouse`、`iFrame`
- 对于多通道效果（Buffer A/B），使用 WebGL2 framebuffer + 乒乓（见 multipass-buffer 技术）

## 常见陷阱

### JS 变量声明顺序（TDZ — 导致白屏崩溃）

`let`/`const` 变量必须在**顶部**的 `<script>` 块中声明，在引用它们的任何函数之前：

```javascript
// 1. 状态变量 FIRST
let frameCount = 0;
let startTime = Date.now();

// 2. Canvas/GL 初始化，着色器编译，FBO 创建
const canvas = document.getElementById('canvas');
const gl = canvas.getContext('webgl2');
// ...

// 3. 函数和事件绑定 LAST
function resize() { /* 现在可以安全引用 frameCount */ }
function render() { /* ... */ }
window.addEventListener('resize', resize);
```

原因：`let`/`const` 有一个时间死区 — 在声明之前引用它们会抛出 `ReferenceError`，导致白屏。

### GLSL 编译错误（编写着色器后自我检查）

- **函数签名不匹配**：调用必须与定义完全匹配参数数量和类型。如果定义为 `float fbm(vec3 p)`，不能调用 `fbm(uv)` 使用 `vec2`
- **保留字作为变量名**：不要使用：`patch`、`cast`、`sample`、`filter`、`input`、`output`、`common`、`partition`、`active`
- **严格类型匹配**：`vec3 x = 1.0` 是非法的 — 使用 `vec3 x = vec3(1.0)`；不能使用 `.z` 访问 `vec2`
- **结构上不能使用三元运算符**：ESSL 不允许对结构类型使用三元运算符 — 使用 `if`/`else` 代替

### 性能预算

部署环境可能使用无头软件渲染，GPU 功率有限。保持在以下限制内：

- 光线追踪主循环：≤ 128 步
- 体积采样/光照内循环：≤ 32 步
- FBM 八度：≤ 6 层
- 每个像素的嵌套循环迭代总数：≤ 1000（超过此限制会冻结浏览器）

## 快速配方

常见效果组合 — 从技术模块组装的完整渲染管线。

### 照片级真实 SDF 场景
1. **几何**：sdf-3d（扩展基元）+ csg-boolean-operations（立方/四次 smin）
2. **渲染**：ray-marching + normal-estimation（四面体方法）
3. **光照**：lighting-model（户外三光源模型）+ shadow-techniques（改进软阴影）+ ambient-occlusion
4. **大气层**：atmospheric-scattering（基于高度的雾，带太阳色调）
5. **后处理**：post-processing（ACES 色调映射）+ anti-aliasing（2x SSAA）+ camera-effects（暗角）

### 有机/生物形态
1. **几何**：sdf-3d（扩展基元+变形算子：扭曲、弯曲）+ csg-boolean（梯度感知 smin 用于材质混合）
2. **细节**：procedural-noise（带导数的 FBM）+ domain-warping
3. **表面**：lighting-model（次表面散射近似通过半-Lambert）

### 程序化地形
1. **地形**：terrain-rendering + procedural-noise（带导数的侵蚀 FBM）
2. **纹理**：texture-mapping-advanced（双平面映射+无平铺）
3. **天空**：atmospheric-scattering（Rayleigh/Mie + 高度雾）
4. **水面**：water-ocean（Gerstner 波浪）+ lighting-model（菲涅尔反射）

### 风格化 2D 艺术
1. **形状**：sdf-2d（扩展库）+ sdf-tricks（分层边缘、空心）
2. **色彩**：color-palette（余弦调色板）+ polar-uv-manipulation（万花筒）
3. **润色**：anti-aliasing（SDF 解析 AA）+ post-processing（软件晕影、色差）

## 着色器调试技巧

可视化调试方法 — 暂时替换输出以诊断问题。

| 检查内容 | 代码 | 查找内容 |
|---|---|---|
| 表面法线 | `col = nor * 0.5 + 0.5;` | 平滑渐变 = 正确的法线；条带 = epsilon 太大 |
| 光线追踪步数 | `col = vec3(float(steps) / float(MAX_STEPS));` | 红色热点 = 性能瓶颈；均匀 = 浪费迭代 |
| 深度/距离 | `col = vec3(t / MAX_DIST);` | 验证正确的命中距离 |
| UV 坐标 | `col = vec3(uv, 0.0);` | 检查坐标映射 |
| SDF 距离场 | `col = (d > 0.0 ? vec3(0.9,0.6,0.3) : vec3(0.4,0.7,0.85)) * (0.8 + 0.2*cos(150.0*d));` | 可视化 SDF 带和零交叉 |
| 检查器图案（UV） | `col = vec3(mod(floor(uv.x*10.)+floor(uv.y*10.), 2.0));` | 验证 UV 扭曲、接缝 |
| 仅光照 | `col = vec3(shadow);` 或 `col = vec3(ao);` | 隔离阴影/AO 贡献 |
| 材质 ID | `col = palette(matId / maxMatId);` | 验证材质分配 |
