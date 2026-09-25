# TypeGPU / WebGPU 用于 HyperFrames

HyperFrames 通过其 `typegpu` 运行时适配器支持 TypeGPU 和原始 WebGPU。该适配器不拥有你的管线。它会发布 HyperFrames 时间，并分发一个 seek 事件，以便你的合成能够渲染精确的 GPU 帧。

## 契约

- 异步初始化 WebGPU（`await navigator.gpu.requestAdapter()`），但将所有 GSAP 补间动画**同步注册**——在任何 `await` 之前。HyperFrames 播放器在页面加载时立即读取时间线。
- 从 HyperFrames 时间进行渲染，而非 `performance.now()`。
- 监听 `hf-seek` 事件，并在该确切时间重新渲染。
- 防范 WebGPU 不可用环境——适配器不会为你检查。
- 对于视频渲染，在提交 GPU 工作后调用 `await device.queue.onSubmittedWorkDone()`，以确保在捕获帧之前画布已完成刷新。

适配器会设置 `window.__hfTypegpuTime`，并在每次 seek 时分发 `new CustomEvent("hf-seek", { detail: { time } })`。

## 基础模式

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

    // Build your pipeline, buffers, bind groups...
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

## 时间线注册

GSAP 补间动画若用于驱动文本、字幕或 HTML 元素，必须**同步注册**——在任何 `await` 之前：

```js
const tl = gsap.timeline({ paused: true });

// Caption tweens: synchronous, added before WebGPU init
gsap.set(".cap", { opacity: 0 });
tl.to("#cap-1", { opacity: 1, duration: 0.3 }, 1.0);
tl.to("#cap-1", { opacity: 0, duration: 0.2 }, 3.5);

window.__timelines["my-comp"] = tl;

// GPU-dependent tweens can go inside the async IIFE
(async () => {
  // ... WebGPU init ...
  const proxy = { value: 0 };
  tl.to(proxy, { value: 1, duration: 2, onUpdate: render }, 0.5);
})();
```

## 视频支持的效果（液态玻璃、形变）

将 `<video>` 用作 GPU 输入纹理时：

```js
const videoEl = document.getElementById("aroll");

// Wait for video metadata before creating the texture
await new Promise((r) => {
  if (videoEl.readyState >= 1) r();
  else videoEl.addEventListener("loadedmetadata", r, { once: true });
});

// Create texture at the video's NATIVE resolution
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
    /* frame not decoded yet */
  }
  // ... draw ...
}
```

**渲染模式注意事项：** 无头 Chrome 可能无法为 video 元素执行 `copyExternalImageToTexture`。对于生产渲染，请通过 FFmpeg 预先提取关键帧为 PNG 文件，并将其作为图像纹理加载，而非使用视频元素。

## 通过下采样 Pass 实现的霜冻模糊

单遍高斯核对于类玻璃的霜冻模糊而言太弱。请使用两遍处理方式：

1. **Pass 1 — 下采样：** 将全分辨率纹理渲染到一个小纹理（分辨率为 1/6）。下采样过程中的双线性过滤自然地对像素进行平均。
2. **Pass 2 — 玻璃合成：** 采样小纹理以获取霜冻内部效果（双线性放大 = 强烈平滑模糊），并采样全分辨率纹理以获取锐利区域和色散效果。

这与 TypeGPU 的 `textureSampleBias` mip 级别方法一致，且无需生成 mipmap。

## 透明与不透明画布

- **`alphaMode: 'opaque'`** — GPU 画布渲染完整帧（视频 + 效果）。当 GPU 管线处理所有视觉内容时使用。
- **`alphaMode: 'premultiplied'`** — GPU 画布在 alpha = 0 时为透明，使下方的 HTML 元素透出。用于在普通 `<video>` 元素之上叠加遮罩层（粒子、路径动画）。

## WGSL 全屏三角形

用于全屏效果的常规顶点着色器（无需顶点缓冲区）：

```wgsl
struct Vo { @builtin(position) pos: vec4f, @location(0) uv: vec2f }

@vertex fn vs(@builtin(vertex_index) vi: u32) -> Vo {
  let ps = array<vec2f, 3>(vec2f(-1., -1.), vec2f(3., -1.), vec2f(-1., 3.));
  let ts = array<vec2f, 3>(vec2f(0., 1.), vec2f(2., 1.), vec2f(0., -1.));
  return Vo(vec4f(ps[vi], 0., 1.), ts[vi]);
}
```

使用 `pass.draw(3)` 进行绘制——一个覆盖视口的三角形。

## 圆角矩形 SDF（液态玻璃药丸）

```wgsl
fn sdf_box(p: vec2f, half_size: vec2f, corner_radius: f32) -> f32 {
  let d = abs(p) - half_size + vec2f(corner_radius);
  return length(max(d, vec2f(0.))) + min(max(d.x, d.y), 0.) - corner_radius;
}
```

使用此函数定义玻璃效果的内部、环形和外部区域。负值位于形状内部。

## 确定性渲染

- 不使用 `Math.random()` —使用种子化 PRNG。
- 不使用 `requestAnimationFrame` 作为渲染循环——仅在响应 `hf-seek` 时进行渲染。
- 不使用 `performance.now()` 获取动画时间——读取 `window.__hfTypegpuTime` 或 `e.detail.time`。
- 在 GPU 提交后，调用 `await device.queue.onSubmittedWorkDone()` 进行渲染模式帧捕获。
