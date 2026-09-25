自定义着色器通过 `Shader.from({ gl, gpu, resources })` 将 GLSL 和 WGSL 程序绑定到场景对象。统一变量存储在类型化的 `UniformGroup` 中，纹理作为单独的资源传递，同一个着色器可以同时针对 WebGL 和 WebGPU。

## 快速入门

```ts
const uniforms = new UniformGroup({
  uTime: { value: 0, type: "f32" },
});

const shader = Shader.from({
  gl: { vertex: vertexSrc, fragment: fragmentSrc },
  resources: { uniforms },
});

const geometry = new MeshGeometry({
  positions: new Float32Array([0, 0, 100, 0, 100, 100, 0, 100]),
  uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
  indices: new Uint32Array([0, 1, 2, 0, 2, 3]),
});

const mesh = new Mesh({ geometry, shader });
app.stage.addChild(mesh);

app.ticker.add(() => {
  shader.resources.uniforms.uniforms.uTime = performance.now() / 1000;
});
```

**相关技能：** `pixijs-filters`（内置滤镜）、`pixijs-scene-mesh`（自定义几何体）、`pixijs-performance`（批处理优化）、`pixijs-migration-v8`（从 v7 迁移着色器 API）。

## 核心模式

### 双渲染器着色器（WebGL + WebGPU）

```ts
import { Shader, GlProgram, GpuProgram, UniformGroup } from "pixi.js";

const glVertex = `...`; // GLSL 顶点（如果需要 WebGL2/GLSL ES 3.0，请自行编写 `#version 300 es`）
const glFragment = `...`; // GLSL 片段
const wgslSource = `...`; // WGSL 源代码

const shader = Shader.from({
  gl: { vertex: glVertex, fragment: glFragment },
  gpu: {
    // 入口点名称是任意的；它们必须与 WGSL 源中的 @vertex / @fragment 函数名称匹配。PixiJS 提供使用 'mainVert' / 'mainFrag' 的示例，但 `main` 同样有效。
    vertex: { entryPoint: "mainVert", source: wgslSource },
    fragment: { entryPoint: "mainFrag", source: wgslSource },
  },
  resources: {
    myUniforms: new UniformGroup({
      uColor: { value: new Float32Array([1, 0, 0, 1]), type: "vec4<f32>" },
      uMatrix: { value: new Float32Array(16), type: "mat4x4<f32>" },
    }),
  },
});
```

如果只提供 `gl`，着色器仅适用于 WebGL。如果只提供 `gpu`，着色器仅适用于 WebGPU。`compatibleRenderers` 位掩码会自动设置。

`GlProgram` **不会**自动注入 `#version 300 es`。如果自行编写 `#version 300 es`，PixiJS 会保留它并将着色器视为 GLSL ES 3.0；否则它会注入 WebGL1 兼容宏（`#define in varying`、`#define texture texture2D`）并以 WebGL1 风格的 GLSL 运行。`GlProgram` 总是会注入默认精度（顶点 `highp`、片段 `mediump`）和程序名称。对于 GLSL ES 3.0，使用 `in`/`out` 而不是 `attribute`/`varying`、`texture()` 而不是 `texture2D()`、以及 `out vec4` 而不是 `gl_FragColor`。

### 纹理作为资源

纹理是资源，不是统一变量。分别传递纹理的 `source` 和 `style`：

```ts
import { Shader, UniformGroup, Texture, Assets } from "pixi.js";

const texture = await Assets.load("myImage.png");

const shader = Shader.from({
  gl: { vertex: vertSrc, fragment: fragSrc },
  resources: {
    uTexture: texture.source,
    uSampler: texture.source.style,
    myUniforms: new UniformGroup({
      uAlpha: { value: 1.0, type: "f32" },
    }),
  },
});

// 运行时切换纹理
shader.resources.uTexture = otherTexture.source;
```

资源是一个扁平的键值映射。键必须与着色器源中的统一变量/绑定名称匹配。

资源也可以是普通对象（自动封装为 `UniformGroup`）：

```ts
const shader = Shader.from({
  gl: { vertex: vertSrc, fragment: fragSrc },
  resources: {
    myUniforms: {
      uTime: { value: 0, type: "f32" },
    },
  },
});
```

### UBO 模式（统一变量缓冲区对象）

UBO 模式将统一变量打包到单个 GPU 缓冲区中。对 WebGPU 是必需的；对 WebGL（WebGL2+）是可选的。

```ts
import { UniformGroup } from "pixi.js";

const ubo = new UniformGroup(
  {
    uProjection: { value: new Float32Array(16), type: "mat4x4<f32>" },
    uAlpha: { value: 1.0, type: "f32" },
  },
  { ubo: true, isStatic: true },
);

// 当 isStatic 为 true 时，必须手动调用 update()
ubo.uniforms.uAlpha = 0.5;
ubo.update();
```

UBO 规则：

- 仅支持基于 `f32` 和 `i32` 的类型（不支持 `u32`）。矩阵只能是浮点数。
- 采样器/纹理不能放在 UBO 中。
- 资源中的 `UniformGroup` 名称必须与着色器中的 UBO 块名称完全匹配。
- 结构和顺序必须与着色器布局完全匹配。
- UBO 同步使用 `new Function` 在底层实现。在严格 CSP 环境中（没有 `unsafe-eval`），在启动时导入一次 `pixi.js/unsafe-eval` 以切换到备用同步路径；否则，基于 UBO 的着色器（因此 WebGPU）在首次使用时将抛出错误。

### 自定义滤镜

`Filter.from({ gl, resources })` 是简写。只需传递片段着色器；PixiJS 会提供默认的顶点着色器来处理输出帧的定位。

```ts
import { Filter } from "pixi.js";

const filter = Filter.from({
  gl: {
    fragment: `
            in vec2 vTextureCoord;
            out vec4 finalColor;
            uniform sampler2D uTexture;
            uniform float uStrength;

            void main(void) {
                vec4 color = texture(uTexture, vTextureCoord);
                finalColor = mix(color, vec4(1.0 - color.rgb, color.a), uStrength);
            }
        `,
  },
  resources: {
    filterUniforms: {
      uStrength: { value: 0.5, type: "f32" },
    },
  },
});

filter.resources.filterUniforms.uniforms.uStrength = 1.0;
```

对于自定义顶点着色器，使用 `new Filter({ glProgram: new GlProgram({ vertex, fragment }), resources })`。

#### 滤镜着色器约定（GLSL ES 3.0）

- `in vec2 vTextureCoord;` 而不是 `varying vec2 vTextureCoord;`
- `out vec4 finalColor;` 而不是 `gl_FragColor`
- `texture(uTexture, uv)` 而不是 `texture2D(uTexture, uv)`
- 默认顶点着色器暴露 `uInputSize`、`uOutputFrame`、`uOutputTexture` 以及辅助函数 `filterVertexPosition()` / `filterTextureCoord()`

#### 采样滤镜后面的渲染目标

设置 `blendRequired: true` 并在片段着色器中采样 `uBackTexture`。PixiJS 在运行滤镜之前将目标像素复制到该统一变量中：

```ts
const blendFilter = Filter.from({
  gl: { fragment: blendFragSrc },
  resources: { uniforms: { uAmount: { value: 0.5, type: "f32" } } },
  blendRequired: true,
});
```

仅在需要时启用 `blendRequired`；它会强制每帧进行额外的 GPU 复制。

### 运行时更新统一变量

```ts
// 通过 resources 访问 UniformGroup
shader.resources.myUniforms.uniforms.uTime = performance.now() / 1000;

// 对于 isStatic UBO，更改值后调用 update()
shader.resources.myUniforms.update();
```

### 高级 GPU 功能

参见 [references/advanced-gpu.md](references/advanced-gpu.md) 获取完整示例，包括：

- **部分缓冲区更新**：`buffer.update(sizeInBytes, offsetInBytes)` 仅上传更改的字节范围。
- **顶点和索引计数、 winding、剔除**：`geometry.vertexCount`（已弃用的 `getSize()` 替代）、`geometry.indexCount` 以绘制共享索引缓冲区的前缀、`state.clockwiseFrontFace` 和 `cullMode`。
- **WGSL 覆盖常量**（WebGPU）：`Shader.from({ gpu, resources, overrides: { STEPS: 8 } })`；每个不同的集合编译自己的管道。
- **自定义绑定组布局**（WebGPU）：使用 `generateGpuLayoutGroups(extractStructAndGroups(source))` 生成默认布局，编辑它，并将其作为 `gpuLayout` 传递。
- **使用 `TextureView` 进行深度采样**（WebGPU）：在目标的深度附件为 `depthReadOnly` 时，将 `new TextureView(depth, { aspect: "depth-only" })` 作为资源绑定。
- **渲染包**（WebGPU）：使用 `encoder.beginBundle()` / `endBundle()` 一次记录绘制，并使用 `executeBundle()` 在 `isBundleValid()` 保持时重放。
- **池化暂存纹理**：`TexturePool.getOptimalTexture({ width, height, resolution, antialias })` 和 `returnTexture()`。

### 统一变量类型参考

参见 [references/uniform-types.md](references/uniform-types.md) 获取完整表格，包括支持的类型、它们的 WGSL/GLSL 等价物和值格式。

### 自定义批处理器（基于扩展）

`Batcher` 抽象类支持自定义批处理以进行特殊渲染。继承它并通过扩展注册：

```ts
import { Batcher, extensions, ExtensionType } from "pixi.js";
import type {
  BatcherOptions,
  BatchableMeshElement,
  BatchableQuadElement,
  Geometry,
  Shader,
} from "pixi.js";

class MyBatcher extends Batcher {
  public static extension = {
    type: [ExtensionType.Batcher],
    name: "my-batcher",
  };

  public name = "my-batcher";
  protected vertexSize = 6; // 每个顶点的浮点数
  public geometry: Geometry;
  public shader: Shader;

  constructor(options: BatcherOptions) {
    super(options);
    // 初始化几何体和着色器
  }

  public packAttributes(
    element: BatchableMeshElement,
    float32View: Float32Array,
    uint32View: Uint32Array,
    index: number,
    textureId: number,
  ): void {
    // 将网格顶点属性打包到批处理缓冲区
  }

  public packQuadAttributes(
    element: BatchableQuadElement,
    float32View: Float32Array,
    uint32View: Uint32Array,
    index: number,
    textureId: number,
  ): void {
    // 将四边形顶点属性打包到批处理缓冲区
  }
}

extensions.add(MyBatcher);
```

元素通过 `batcherName` 引用批处理器。`BatchableElement` 接口要求：`batcherName`、`texture`、`blendMode`、`indexSize`、`attributeSize`、`topology` 和 `packAsQuad`。

一个自定义的 `InstructionPipe`，按 `InstructionSet`（`BatcherPipe` 保留批处理器的方式）缓存状态，应实现 `destroyInstructionSet(instructionSet)`。渲染器在拥有渲染组被销毁时调用它，以便缓存 GPU 对象随之一并释放，而不是泄漏。

```ts
public destroyInstructionSet(instructionSet: InstructionSet): void {
  this._cache[instructionSet.uid]?.destroy();
  delete this._cache[instructionSet.uid];
}
```

## 常见错误

### [关键] 旧的 `Shader.from(vertex, fragment, uniforms)` 构造函数

错误：

```ts
const shader = Shader.from(vertex, fragment, { uTime: 1 });
```

正确：

```ts
const shader = Shader.from({
  gl: { vertex, fragment },
  resources: {
    uniforms: new UniformGroup({
      uTime: { value: 1, type: "f32" },
    }),
  },
});
```

v8 要求使用包含 `gl`/`gpu` 程序和 `resources` 的选项对象。位置 API 已被移除。

### [关键] 没有 `type` 注解的 `UniformGroup`

错误：

```ts
new UniformGroup({ uTime: 1 });
```

正确：

```ts
new UniformGroup({ uTime: { value: 1, type: "f32" } });
```

每个统一变量都需要显式的 `{ value, type }` 对。省略类型会导致运行时错误：`"Uniform type undefined is not supported."`。

### [高] UBO 使用不支持的类型或结构错误

UBO 模式支持基于 `f32` 和 `i32` 的类型（标量和向量）。`u32` 不在支持的 `UniformGroup` 类型列表中，会抛出错误。矩阵只能是浮点数（`mat*<f32>`）。采样器不能放在 UBO 中。

结构名称和字段顺序必须与着色器中的 UBO 声明完全匹配。不匹配会导致渲染混乱，但没有错误。

### [高] 将纹理放在 `UniformGroup` 中

错误：

```ts
new UniformGroup({
  uTexture: { value: texture, type: "f32" },
});
```

正确：

```ts
const shader = Shader.from({
  gl: { vertex, fragment },
  resources: {
    uTexture: texture.source,
    uSampler: texture.source.style,
    myUniforms: new UniformGroup({
      uAlpha: { value: 1.0, type: "f32" },
    }),
  },
});
```

纹理是资源，不是统一变量。作为顶级资源条目传递 `texture.source`（`TextureSource`）和 `texture.source.style`（`TextureStyle`）。

### [高] 对不同的渲染目标重放渲染包

错误：

```ts
const bundle = encoder.endBundle();
// 后续，在每一帧，无论绑定的是什么
encoder.executeBundle(bundle);
```

正确：

```ts
if (!bundle || !encoder.isBundleValid(bundle)) {
  bundle = record();
}
encoder.executeBundle(bundle);
```

包烘焙了它被记录时的附件和 winding，以及它被记录的设备。在不同的目标下重放它要么会导致整个帧的 WebGPU 验证失败，要么会无声地反向渲染；在设备丢失后重放它会被直接拒绝。

### [中] 读取 `geometry.getSize()`

`geometry.getSize()` 自 8.20.0 起已弃用，并会记录警告。使用 `geometry.vertexCount`，它是缓存的，只有在缓冲区或属性更改时才会重新计算。
