# TypeGPU / WebGPU for HyperFrames

HyperFrames 通过其 `typegpu` 运行时适配器支持 TypeGPU 和原始 WebGPU。适配器不拥有您的管线。它会发布 HyperFrames 时间并派发一个 seek 事件，以便您的合成可以在确切的 GPU 帧上渲染。

## 协议

- 异步初始化 WebGPU (`await navigator.gpu.requestAdapter()`)，但在任何 `await` 之前同步注册所有 GSAP 补间动画 —— HyperFrames 播放器在页面加载时立即读取时间轴。
- 从 HyperFrames 时间渲染，而不是 `performance.now()`。
- 监听 `hf-seek` 事件并在该确切时间重新渲染。
- 防止 WebGPU 不可用的环境 —— 适配器不会为您检查。
- 对于视频渲染，在提交 GPU 工作后调用 `await device.queue.onSubmittedWorkDone()` 以确保在捕获帧之前画布已刷新。

适配器设置 `window.__hfTypegpuTime` 并在每次 seek 时派发 `new CustomEvent("hf-seek", { detail: { time } })`。

## 基本模式

```html
<canvas id="gpu-layer"></canvas>
<script>
  (async () => {
    if (!navigator.gpu) return;
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) return;
    const device = await adapter.requestDevice();
    const canvas = document.getElementById("gpu-layer");
    canvas.width = 1920;
    canvas.height = 1080;
    const ctx = canvas.getContext("webgpu");
    const fmt = navigator.gpu.getPreferredCanvasFormat();
    ctx.configure({ device, format: fmt, alphaMode: "opaque" });

    // 构建您的管线、缓冲区、绑定组...
    const timeUniform = new Float32Array([0]);
    const timeBuf = device.createBuffer({
      size: 16,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });

    function render(t) {
      timeUniform[0] = t;
      device.queue.writeBuffer(timeBuf, 0, timeUniform);
      const enc = device.createCommandEncoder();
      const pass = enc.beginRenderPass({
        colorAttachments: [
          {
            view: ctx.getCurrentTexture().createView(),
            loadOp: "clear",
            clearValue: { r: 0, g: 0, b: 0, a: 1 },
            storeOp: "store",
          },
        ],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(0, bindGroup);
      pass.draw(3);
      pass.end();
      device.queue.submit([enc.finish()]);
    }

    render(0);
    window.addEventListener("hf-seek", (e) => render(e.detail.time));
  })();
</script>
```

## 时间轴注册

驱动文本、字幕或 HTML 元素的 GSAP 补间动画必须同步注册 —— 在任何 `await` 之前：

```js
const tl = gsap.timeline({ paused: true });

// 字幕补间：同步，添加在 WebGPU 初始化之前
gsap.set(".cap", { opacity: 0 });
tl.to("#cap-1", { opacity: 1, duration: 0.3 }, 1.0);
tl.to("#cap-1", { opacity: 0, duration: 0.2 }, 3.5);

window.__timelines["my-comp"] = tl;

// 依赖 GPU 的补间可以在异步 IIFE 内部
(async () => {
  // ... WebGPU 初始化...
  const proxy = { value: 0 };
  tl.to(proxy, { value: 1, duration: 2, onUpdate: render }, 0.5);
})();
```

## 视频-支持的效果（Liquid Glass、Distortion）

要使用 `<video>` 作为 GPU 输入纹理：

```js
const videoEl = document.getElementById("aroll");

// 等待视频元数据后再创建纹理
await new Promise((r) => {
  if (videoEl.readyState >= 1) r();
  else videoEl.addEventListener("loadedmetadata", r, { once: true });
});

// 在视频的 NATIVE 分辨率下创建纹理
const vw = videoEl.videoWidth,
  vh = videoEl.videoHeight;
const bgTex = device.createTexture({
  size: [vw, vh],
  format: "rgba8unorm",
  usage:
    GPUTextureUsage.COPY_DST | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.RENDER_ATTACHMENT,
});

function render(t) {
  try {
    device.queue.copyExternalImageToTexture({ source: videoEl }, { texture: bgTex }, [vw, vh]);
  } catch (_) {
    /* 帧尚未解码 */
  }
  // ... 绘制...
}
```

**渲染模式注意事项：** headless Chrome 可能会失败 `copyExternalImageToTexture` 对于视频元素。对于生产渲染，通过 FFmpeg 预提取关键帧为 PNG 并加载它们作为图像纹理。

## Frosted Blur 通过下采样通道

单通道高斯核对于玻璃般的 Frosted Blur 太弱。使用两通道方法：

1. **通道 1 — 下采样：** 将全分辨率纹理渲染到小纹理（1/6 分辨率）。在下采样过程中使用双线性过滤自然地平均像素。
2. **通道 2 — 玻璃合成：** 对小纹理进行双线性上采样（重平滑模糊）以获取 Frosted 内部，对全分辨率纹理获取锐利区域和色散折射。

这与 TypeGPU 的 `textureSampleBias` Mip-level 方法匹配，而无需生成 Mipmaps。

## 透明与不透明画布

- **`alphaMode: 'opaque'`** —— GPU 画布渲染全帧（视频 + 效果）。当 GPU 管线处理所有视觉内容时使用。
- **`alphaMode: 'premultiplied'`** —— 当 alpha = 0 时 GPU 画布透明，允许下方的 HTML 元素显示。用于在常规 `<video>` 元素上方的叠加层（粒子、路径动画）。

## WGSL 全屏三角形

全屏效果的标凈顶点着色器（无需顶点缓冲区）：

```wgsl
struct Vo { @builtin(position) pos: vec4f, @location(0) uv: vec2f }

@vertex fn vs(@builtin(vertex_index) vi: u32) -> Vo {
  let ps = array<vec2f, 3>(vec2f(-1., -1.), vec2f(3., -1.), vec2f(-1., 3.));
  let ts = array<vec2f, 3>(vec2f(0., 1.), vec2f(2., 1.), vec2f(0., -1.));
  return Vo(vec4f(ps[vi], 0., 1.), ts[vi]);
}
```

使用 `pass.draw(3)` 绘制——一个覆盖视口的三角形。

## 圆角矩形 SDF（Liquid Glass 柱）

```wgsl
fn sdf_box(p: vec2f, half_size: vec2f, corner_radius: f32) -> f32 {
  let d = abs(p) - half_size + vec2f(corner_radius);
  return length(max(d, vec2f(0.))) + min(max(d.x, d.y), 0.) - corner_radius;
}
```

用于定义玻璃效果的内部/环/外部区域。负值表示在形状内部。

## 确定性渲染

- 不使用 `Math.random()` —— 使用带种子的伪随机数生成器。
- 不使用 `requestAnimationFrame` 渲染循环 —— 仅在响应 `hf-seek` 时渲染。
- 不使用 `performance.now()` 动画时间 —— 读取 `window.__hfTypegpuTime` 或 `e.detail.time`。
- 在 GPU 提交后，调用 `await device.queue.onSubmittedWorkDone()` 以捕获渲染模式帧。
