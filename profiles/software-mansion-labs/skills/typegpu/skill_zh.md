# TypeGPU

一个单一的模式 (`d.*`) 同时定义了 GPU 类型、CPU 缓冲区布局和 TypeScript 类型 - 无需手动对齐、类型映射或强制转换。构建插件 `unplugin-typegpu` 转换带 `'use gpu'` 标记的 TypeScript，用于运行时 WGSL 转换，实现 CPU/GPU 边界之间的类型推断和多态性。

这项技能针对 TypeGPU `0.12` 版本。如果用户的项目位于较旧的版本上，请在依赖此处的示例或推荐模式之前验证 API 的可用性。

---

## 何时阅读参考文件

**在编写几乎任何着色器或 GPU 函数之前阅读** — 这两个文件涵盖了最让人困惑的规则：
- `references/types.md` — 抽象类型解析，`d.f32()` 何时是必需的 vs. 红undant，向量构造函数重载，`tgpu.fn` 签名用到的采样器/纹理模式，CPU 端的 `TgpuBuffer`/`TgpuTexture` TypeScript 类型。**如果你跳过这个，你会遇到类型错误。**
- `references/shaders.md` — 循环 (`std.range`, `tgpu.unroll`), 条件运算符语义, `tgpu.comptime`, 外部作用域捕获规则，所有三个着色器阶段的完整内置参考, `console.log`。**对于任何非平凡的着色器逻辑，请阅读这个。**
- `references/std.md` — 完整的 `std` 函数列表（数学，比较/布尔向量，矩阵构建器，纹理，原子，打包，子组，环境探针）。在手动构建任何数学/工具函数之前参考。

**当任务特别涉及以下内容时阅读：**
- `references/pipelines.md` — 顶点缓冲区/布局, `attribs` 连接, MRT, 全屏三角形, 深度/模板, 混合模式, `fragDepth` 输出, 加载 3D 模型 (`@loaders.gl`), resolve API
- `references/matrices.md` — `wgpu-matrix` 集成, 列主序布局, 相机统一变量, `common.writeSoA`, 快速路径 CPU 写入。**对于任何 3D 工作**（视图/投影矩阵，动画变换，模型加载）
- `references/textures.md` — 纹理创建，视图，采样器，存储纹理，Mipmaps，多重采样
- `references/noise.md` — `@typegpu/noise`（随机数，分布，Perlin 2D/3D）
- `references/sdf.md` — `@typegpu/sdf`（2D/3D 原始形状，运算符，光线步进，AA 掩码）
- `references/encoders.md` — 带类型的命令编码器，多管道渲染/计算通道，渲染包，批量提交，原始 WebGPU 编码器互操作（不稳定 API，稳定行为）
- `references/timing.md` — 通过时间戳查询进行 GPU 定时：`withPerformanceCallback` vs. 共享查询集，`available` 守卫，为什么每通道定时会重叠
- `references/react.md` — `@typegpu/react` 钩子（useRoot, useFrame, useUniform, ...），React Native worklet 渲染循环
- `references/setup.md` — TypeGPU CLI，安装，`unplugin-typegpu` 构建插件，`tsover` 运算符重载，故障排除
- `references/advanced.md` — 缓冲区重解释，间接绘制/调度，ArrayBuffer IO，压缩，警告抑制，`root.unwrap`

---

## 设置

```ts
import { tgpu, d, std, common } from 'typegpu';

const root = await tgpu.init();                 // 请求一个 GPU 设备
const root = tgpu.initFromDevice({ device });   // 或者包装一个现有的 GPUDevice

const context = root.configureContext({ canvas, alphaMode: 'premultiplied' });
```

在应用启动时创建一个 root。来自不同 root 的资源无法交互。销毁：`root.destroy()` 销毁通过 root 创建的所有资源，如果 root 来自 `tgpu.init`（而不是 `initFromDevice`），还会销毁设备本身。

---

## 数据模式 (`d.*`)

一个模式定义内存布局并推断 TypeScript 类型；相同的模式用于缓冲区、着色器签名和绑定组条目。

### 标量
```ts
d.f32    d.i32    d.u32    d.f16   // f16 需要设备功能 'shader-f16'（参考 `references/setup.md`）
// d.bool 不可与主机共享 - 在缓冲区中使用 d.u32
```

### 向量和矩阵
```ts
d.vec2f  d.vec3f  d.vec4f     // f32
d.vec2i  d.vec3i  d.vec4i     // i32
d.vec2u  d.vec3u  d.vec4u     // u32
d.vec2h  d.vec3h  d.vec4h     // f16
d.vec2b  d.vec3b  d.vec4b     // bool - 仅在着色器端可用（不可与主机共享）

d.mat2x2f   d.mat3x3f   d.mat4x4f
```

实例类型：`d.vec3f()` -> `d.v3f`, `d.mat4x4f()` -> `d.m4x4f`。

**向量构造函数重载非常丰富** — 它们可以组合任何混合的标量、较小的向量和混洗，只要它们加起来得到正确的组件数量 (`d.vec4f(rgb, 1)`, `d.vec3f(v.xy, newZ)`)。优先使用它们而不是手动组件分解；完整重载列表在 `references/types.md` 中。

### 复合类型
```ts
const Particle = d.struct({
  position: d.vec2f,
  velocity: d.vec2f,
  color:    d.vec4f,
});

const ParticleArray = d.arrayOf(Particle, 1000); // 固定大小
```

**运行时大小的模式。** `d.arrayOf(Element)` 而不带计数返回一个 *函数* `(n: number) => WgslArray<Element>`。这种双重特性是关键：将函数本身（无大小）传递给绑定组布局，用计数调用它（有大小）用于缓冲区创建。

```ts
// 简单数组 - `arrayOf` 而不带计数已经是一个工厂：
const layout = tgpu.bindGroupLayout({
  data: { storage: d.arrayOf(d.f32), access: 'mutable' },  // 无大小用于布局
});
const buf = root.createBuffer(d.arrayOf(d.f32, 1024)).$usage('storage'); // 有大小用于缓冲区

// 带运行时大小最后一个字段的模式 - 用工厂函数包装：
const RuntimeStruct = (n: number) =>
  d.struct({
    counter: d.atomic(d.u32),
    items:   d.arrayOf(d.f32, n),  // 最后一个字段获得运行时大小
  });

const layout2 = tgpu.bindGroupLayout({
  runtimeData: { storage: RuntimeStruct, access: 'mutable' }, // 无大小（函数）
});
const buf2 = root.createBuffer(RuntimeStruct(1024)).$usage('storage'); // 有大小（调用）
```

你不能直接将无大小的模式传递给 `createBuffer` - 大小必须在 CPU 上已知。

---

## GPU 函数

TypeGPU 将带 `'use gpu'` 标记的 TypeScript 编译成 WGSL。

### 简单回调（多态）

没有显式签名；最适合辅助数学和灵活的工具。

```ts
const rotate = (v: d.v2f, angle: number) => {
  'use gpu';
  const c = std.cos(angle);
  const s = std.sin(angle);
  return d.vec2f(c * v.x - s * v.y, s * v.x + c * v.y);
};
```

`number` 参数和联合类型如 `d.v2f | d.v3f` 是多态的 - TypeGPU 为每个唯一的调用点类型组合生成一个 WGSL 重载。从外部作用域捕获的值被 **内联为 WGSL 字面量**；对于任何在运行时变化的值，请使用缓冲区/统一变量。

### `tgpu.fn`（显式类型）

固定 WGSL 签名。用于库代码或当你需要一个固定的 WGSL 接口时。

```ts
const rotate = tgpu.fn([d.vec2f, d.f32], d.vec2f)((v, angle) => {
  'use gpu';
  // ...
});
```

### 着色器入口点

```ts
// 计算
const myCompute = tgpu.computeFn({
  workgroupSize: [64],
  in: { gid: d.builtin.globalInvocationId },
})((input) => { 'use gpu'; /* input.gid: d.v3u */ });

// 顶点
const myVertex = tgpu.vertexFn({
  in:  { position: d.vec3f, uv: d.vec2f },
  out: { position: d.builtin.position, fragUv: d.vec2f },
})((input) => {
  'use gpu';
  return { position: d.vec4f(input.position, 1), fragUv: input.uv };
});

// 片段
const myFragment = tgpu.fragmentFn({
  in: { fragUv: d.vec2f },
  out: d.vec4f,
})((input) => { 'use gpu'; return d.vec4f(input.fragUv, 0, 1); });
```

顶点 `in` 可以包括内置值：`d.builtin.vertexIndex`, `d.builtin.instanceIndex`。

完整着色器语法，分支修剪，`std` 库，类型推断，以及惯用模式（向量操作，结构构造器，寄存器压力）：参考 `references/shaders.md`。在编写任何非平凡着色器之前阅读它 — 值与引用的处理方式就在那里，并且是最常见的 `ResolutionError` 源头。

---

## 缓冲区

### 创建

```ts
// 仅模式：
const buf = root.createBuffer(d.arrayOf(Particle, 1000)).$usage('storage');

// 带有带类型的初始值（仅当非零时 - 所有缓冲区默认都为零初始化）：
const uBuf = root.createBuffer(Config, { time: 1, scale: 2.0 }).$usage('uniform');

// 带有初始化回调 - 缓冲区仍然映射（最便宜的 CPU 路径）：
const buf = root.createBuffer(Schema, (mappedBuffer) => {
  mappedBuffer.write([10, 20], { startOffset: firstChunk.offset });
  mappedBuffer.write([30, 40], { startOffset: secondChunk.offset });
});

// 包装一个现有的 GPUBuffer（你拥有其生命周期和标志）：
const buf = root.createBuffer(d.u32, existingGPUBuffer);
buf.write(12);
```

### 使用标志

| 字面量 | 着色器访问 |
|---|---|
| `'uniform'` | `var<uniform>` |
| `'storage'` | `var<storage, read>`（或 `read_write` 与 `access: 'mutable'`） |
| `'vertex'` | 顶点输入，与 `tgpu.vertexLayout` 配对 |
| `'index'` | 索引缓冲区（仅限 `d.u16` 或 `d.u32` 数组） |
| `'indirect'` | 间接调度/绘制 |

所有缓冲区自动获得 `COPY_SRC | COPY_DST`。`$addFlags(GPUBufferUsage.X)` 添加任何未涵盖的标志。

### 写入

`.write(value)` 处理对齐。四种输入形式（最慢 → 最快）：

| 形式 | 示例 (`vec3f`) | 备注 |
|---|---|---|
| 带类型的实例 | `d.vec3f(1, 2, 3)` | 分配一个包装器 — 适用于设置/原型 |
| 普通JS数组/元组 | `[1, 2, 3]` | 无分配，自动添加填充 |
| TypedArray | `new Float32Array([1, 2, 3])` | 原封不动地复制字节 — **必须包含 WGSL 填充** |
| ArrayBuffer | `rawBytes` | 最高吞吐量，原封不动地复制字节 |

在设置时缓存普通数组或 `Float32Array` 并重复使用。有关填充规则（`vec3f` = 16 字节，`mat3x3f` 每列填充）和完整快速路径指导，参考 `references/matrices.md`。

**切片写入** - 使用 `d.memoryLayoutOf` 获取字节偏移量来更新子区域：

```ts
const layout = d.memoryLayoutOf(schema, (a) => a[3]);
buffer.write([4, 5, 6], { startOffset: layout.offset });
```

**`.patch(data)`** - 而不触及其余部分地更新特定结构字段或数组索引：

```ts
planetBuffer.patch({
  mass: 123.1,
  colors: { 2: [1, 0, 0], 4: d.vec3f(0, 0, 1) },
});
```

**`common.writeSoA(buffer, { field: Float32Array, ... })`** - 将分离的每个字段数组散布到 GPU 的 AoS 布局中，并具有正确的填充。这是粒子系统、模拟和模型加载（CPU 数据已经按字段分离）的惯用路径。有关示例和模型加载模式参考 `references/pipelines.md`。

**GPU 端复制：** `destBuffer.copyFrom(srcBuffer)`（模式必须匹配）。**清零：** `buffer.clear()`。**清理：** `buffer.destroy()`。`copyFrom` 和 `clear` 都可以接受一个可选的命令编码器 — 参考 `references/encoders.md`。

### 读取

```ts
const data = await buffer.read(); // 返回与模式匹配的类型的 JS 值
```

### 简便的“固定”资源

跳过手动绑定组 - 缓冲区在任何着色器中引用时始终绑定：

```ts
const particlesMutable = root.createMutable(d.arrayOf(Particle, 1000));  // var<storage, read_write>
const configUniform    = root.createUniform(Config);                     // var<uniform>
const bufReadonly      = root.createReadonly(d.arrayOf(d.f32, N));       // var<storage, read>
```

在着色器中通过 `particles.$`, `config.$` 访问。默认情况下优先使用固定资源；当您需要在每帧之间切换资源，管理 `@group` 索引，或跨管道共享布局时，切换到手动绑定组。

手动创建的缓冲区使用 `buffer.as('uniform' | 'readonly' | 'mutable')`（需要匹配的 `$usage`）转换为相同类型的绑定 — 当您持有 `TgpuBuffer` 但需要在着色器中访问 `.$` 时使用它。

---

## 绑定组布局（手动绑定）

```ts
const layout = tgpu.bindGroupLayout({
  config:    { uniform: ConfigSchema },
  particles: { storage: d.arrayOf(Particle), access: 'mutable' },
  mySampler: { sampler: 'filtering' },   // 'filtering' | 'non-filtering' | 'comparison'
  myTexture: { texture: d.texture2d(d.f32) },
});

// 在着色器中：layout.$.config, layout.$.particles, ...

const bindGroup = root.createBindGroup(layout, {
  config:    configBuffer,
  particles: particleBuffer,
  mySampler: tgpuSampler,
  myTexture: textureOrView,
});

pipeline.with(bindGroup).dispatchWorkgroups(N);
```

来自 `createUniform`/`createMutable`/`createReadonly` 的缓冲区绑定可以直接作为条目使用（无需解包为缓冲区）。

显式 `@group` 索引（仅在需要与硬编码组索引的原始 WGSL 集成时需要）：`layout.$idx(0)`。

---

## 计算 pipelines

```ts
// 标准 - 你控制工作组大小
const pipeline = root.createComputePipeline({ compute: myComputeFn });
pipeline.with(bindGroup).dispatchWorkgroups(Math.ceil(N / 64));

// 受保护 - TypeGPU 自动处理工作组大小和边界检查。
// 回调的参数数量设置维度（0D 到 3D）：
const p0 = root.createGuardedComputePipeline(() => { 'use gpu'; /* 运行一次 */ });
const p1 = root.createGuardedComputePipeline((x: number) => { 'use gpu'; });
const p2 = root.createGuardedComputePipeline((x: number, y: number) => { 'use gpu'; });
const p3 = root.createGuardedComputePipeline((x: number, y: number, z: number) => { 'use gpu'; });

// dispatchThreads 匹配回调的参数数量 - 传递线程计数，而不是工作组计数。
// TypeGPU 内部选择工作组大小并注入边界守卫，因此请求范围之外的线程是 no-ops。
p2.with(bindGroup).dispatchThreads(width, height);

// WGSL 内置值如 globalInvocationId 不可用 - 使用回调参数代替。
```

---

## WebGPU 坐标约定

WebGPU 匹配 DirectX/Metal，**不是** OpenGL/WebGL — 直径教程逐字复制会导致细微错误：

- **NDC z: `[0, 1]`**, 不是 `[-1, 1]`。复制粘贴的 `gluPerspective` 会裁剪近平面。使用 `wgpu-matrix` 的 `mat4.perspective`（已经针对 `[0, 1]`），或者 `mat4.perspectiveReverseZ` 以获得更好的深度精度。
- **帧缓冲区 `(0, 0)` 是左上角**，`+y` 向下 — 与 OpenGL 相反。`d.builtin.position.xy` 在片段着色器中是像素空间，原点与此相同。
- **纹理 UV `(0, 0)` 是左上角**。不要预翻转 `v` — `createImageBitmap` 已经匹配这个。
- **矩阵是列主序**：`d.mat4x4f(c0, c1, c2, c3)` 接受列。在着色器中使用 `mat.columns[c][r]`；普通的 `mat[i]` 被拒绝。组合：`projection * view * model * position`。参考 `references/matrices.md`。

---

## 渲染 pipelines

```ts
const pipeline = root.createRenderPipeline({
  vertex:   myVertex,
  fragment: myFragment,
  targets:  { format: presentationFormat }, // 单一目标 - 简写
  primitive?:    GPUPrimitiveState,
  depthStencil?: GPUDepthStencilState,
  multisample?:  GPUMultisampleState,
});

pipeline
  .with(bindGroup)
  .withColorAttachment({
    view: context,
    // loadOp/storeOp/clearValue 有默认值
  })
  .withDepthStencilAttachment({ /* ... */ })
  .withIndexBuffer(indexBuffer)  // 启用 .drawIndexed()
  .draw(vertexCount, instanceCount /* 可选 */);
```

没有外壳的内置顶点/片段 lambda 对于简单情况也是有效的。

### 多重渲染目标 (MRT)

使用一个**命名的记录**用于片段 `out`，管道 `targets` 和 `withColorAttachment` — TypeScript 强制匹配键。键直接成为 WGSL 结构字段名；没有 `$` 前缀。内置值 (`fragDepth`) 出现在 `out` 中，但**不会**出现在 `targets` 或 `withColorAttachment` 中。

完整的 MRT 示例，每个目标的混合/写掩码配置，以及 `fragDepth` 的危险武器：参考 `references/pipelines.md`。

### 缓存绑定组和视图

`root.createBindGroup(...)` 和 `texture.createView(...)` 每次调用都会分配新的 GPU 对象。适用于原型；对于任何您关心的内容，请在设置时创建一次（靠近它们包装的资源），将句柄存储在 `const` 中并重复使用。每帧分配不是慢的，但它会提高 GC 压力并引入卡顿。当视图或绑定组确实每帧变化时，缓存您循环的较小集合。

对于顶点缓冲区布局，`attribs` 展开技巧，和 `common.fullScreenTriangle` 辅助函数：`references/pipelines.md`。

### 批量工作

`draw()`/`dispatchWorkgroups()` 每次记录和提交它们自己的单一管道通道。要运行几个管道在一个通道中（共享附件）或将几个通道批量提交到一个提交中，使用带类型的命令编码器 — `root['~unstable'].createCommandEncoder()` → `beginRenderPass`/`beginComputePass` → `pipeline.with(pass).draw(...)` → `pass.end()` → `encoder.submit()`。渲染包和原始 WebGPU 编码器互操作：参考 `references/encoders.md`。

管道在首次使用时惰性初始化；`pipeline.initSync()` / `await pipeline.initAsync()` 将成本转移到加载屏幕（参考 `references/pipelines.md`）。

---

## GPU 范围变量

`tgpu.workgroupVar(schema)` — 在计算中共享所有线程的工作组（仅限计算）。`tgpu.privateVar(schema)` — 线程私有。`tgpu.const(schema, value)` — 编译时嵌入为 WGSL 字面量。所有通过 `.$` 访问。完整示例在 `references/shaders.md` 中。

---

## Slots

`tgpu.slot<T>()` 是一个类型化占位符；在 root 范围（创建管道之前）或函数范围填充 `.with(slot, value)` — 管道不接受 `.with()` 中的 slots。任何类型都适用：GPU 值，函数，回调。Slots 是构建可配置/可重用着色器的惯用方式。

```ts
const distFnSlot = tgpu.slot<(pos: d.v3f) => number>();

const rayMarcher = tgpu.computeFn({
  workgroupSize: [64],
  in: { gid: d.builtin.globalInvocationId },
})(({ gid }) => {
  'use gpu';
  const dist = distFnSlot.$(d.vec3f(gid)); // 调用注入的函数
});

root
  .with(distFnSlot, (pos) => {
    'use gpu';
    return std.length(pos - d.vec3f(0, 0, -5)) - 1.0; // 球体 SDF
  })
  .createComputePipeline({ compute: rayMarcher });
```

标量/向量 slot 带默认值：

```ts
const colorSlot = tgpu.slot(d.vec4f(1, 0, 0, 1));
root.with(colorSlot, d.vec4f(0, 1, 0, 1)).createRenderPipeline({ ... });
```

---

## Accessors

`tgpu.accessor(schema, initial?)` 是模式感知的 - 值可以是缓冲区绑定，常量，字面量，或带 `'use gpu'` 的函数返回一个。着色器对值如何来源一无所知。如果它们可以干净地使用，它们应该优先于 slots。

```ts
const colorAccess = tgpu.accessor(d.vec3f);

// 用统一缓冲区填充：
root.with(colorAccess, colorUniform).createComputePipeline(...)

// 用字面量填充（内联）：
root.with(colorAccess, d.vec3f(1, 0, 0)).createComputePipeline(...)

// 用 GPU 函数填充：
root.with(colorAccess, () => { 'use gpu'; return computeColor(); }).createComputePipeline(...)
```

写入访问：`tgpu.mutableAccessor(schema, initial?)`.

---

## 类型工具

`d.InferInput<typeof Schema>` — CPU 端 `.write()` 接受的类型。`d.InferGPU<typeof Schema>` — `'use gpu'` 函数内的类型。`d.AnyData`（也导自 `'typegpu/data'`） — 通用约束最宽的模式。完整缓冲区/纹理 TypeScript 类型 (`TgpuBuffer`, `TgpuUniform`, `TgpuTexture`, 使用标志）：`references/types.md`。

---

## 常见陷阱

1. **数字字面量**: `1.0` 可能移除 -> `abstractInt`。使用 `d.f32(1)`。参考 `types.md`。
2. **外部作用域捕获是常量**: 不可在运行时修改。使用 `createUniform`/`createMutable`。参考 `shaders.md`。
3. **TypedArray/ArrayBuffer 对齐**: 原封不动地复制字节。`vec3f` 元素是 16 字节（12 + 4 填充）。普通数组处理填充；typed arrays 必须包含填充。
4. **整数除法**: `a / b` 在原语上是 `f32`。使用 `d.i32()`/`d.u32()` 以获得整数语义。参考 `types.md`。
5. **未初始化的变量**: `let x;` 是无效的 - 始终初始化以便推断类型：`let x = d.f32(0)`。
6. **三元运算符**: 运行时三元运算符编译为 WGSL `select` — 两个分支总是评估，因此分支必须是副作用为空且标量/向量值的（没有结构/数组/矩阵；使用 `if`/`else` 那些）。条件为编译时已知的分支完全修剪。参考 `shaders.md`。
7. **片段输出始终是 4 分量** (`d.vec4f`; `d.vec4i`/`d.vec4u` 用于整数格式），即使对于较少通道的格式。带有 `format: 'r8unorm'` 或 `'rg16float'` 的管道仍然需要 `out: d.vec4f` 和 `return d.vec4f(...)`。WebGPU 会丢弃未使用的通道。

---

## 伴随包

- **`@typegpu/noise`** - 真实 PRNG (`randf`), 分布（均匀，正态，半球，...）和 Perlin 噪声 (`perlin2d`/`perlin3d`) 带可选的预计算梯度缓存 (~10x 加速）。优先于手工编写的哈希。参考 `references/noise.md`。

- **`@typegpu/sdf`** - 2D/3D 符号距离原语 (`sdDisk`, `sdBox2d`, `sdRoundedBox2d`, `sdBezier`, `sdSphere`, `sdBox3d`, `sdCapsule`, `sdPlane`, ...) 和运算符 (`opUnion`, `opSmoothUnion`, `opSmoothDifference`, `opExtrudeX/Y/Z`). 所有 `tgpu.fn` 带固定类型，可以直接从 `'use gpu'` 调用。用于光线步进，UI 掩码，AA 向量绘制。参考 `references/sdf.md`。

- **`@typegpu/react`** - React 和 React Native 中的 `@typegpu/react` 钩子 (`useRoot`, `useFrame`, `useUniform`, ...), 包括 UI 线程渲染循环 via `react-native-worklets`。参考 `references/react.md`。

- **TypeGPU CLI** - `npx typegpu@latest` 模板化新项目；`--enhance` 将 TypeGPU 迁移到现有项目。参考 `references/setup.md`。

- **[`wgpu-matrix`](https://github.com/greggman/wgpu-matrix)** - TypeGPU 的标准数学库。TypeGPU 向量/矩阵可以作为 `dst` 传递给 `wgpu-matrix` 调用以避免分配。参考 `references/matrices.md` 中的完整集成模式。
