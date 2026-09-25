# Three.js 用于 HyperFrames

HyperFrames 通过其 `three` 运行时适配器支持 Three.js。该适配器不拥有你的场景。它会发布 HyperFrames 时间，并触发 seek 事件，以便你的合成能够渲染精确的一帧。

## 契约

- 尽可能同步创建场景、相机、渲染器、材质和资源。
- 使用 HyperFrames 时间进行渲染，而非挂钟时间。
- 监听 `hf-seek` 事件，并渲染该确切时间。
- 在渲染关键 seek 之前加载模型、纹理和 HDRIs，切勿在 seek 时获取它们。
- 避免将 `requestAnimationFrame` 或 `renderer.setAnimationLoop` 作为渲染关键动态的真实依据。

适配器会在每次 seek 时设置 `window.__hfThreeTime`，并在事件对象上分发 `new CustomEvent("hf-seek", { detail: { time } })`。

## 基础模式

```html
<canvas id="three-layer"></canvas>
<script type="module">
  import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.181.2/+esm";

  const canvas = document.getElementById("three-layer");
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  // Match these to your composition's frame size.
  renderer.setSize(1920, 1080, false);
  renderer.setPixelRatio(1);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1920 / 1080, 0.1, 100);
  camera.position.set(0, 0, 6);

  const mesh = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.4, 4),
    new THREE.MeshStandardMaterial({ color: 0x64d2ff, roughness: 0.38 }),
  );
  scene.add(mesh);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x223344, 2));

  function renderAt(time) {
    mesh.rotation.y = time * 0.7;
    mesh.rotation.x = Math.sin(time * 0.6) * 0.16;
    renderer.render(scene, camera);
  }

  window.addEventListener("hf-seek", (event) => {
    renderAt(event.detail.time);
  });

  renderAt(window.__hfThreeTime || 0);
</script>
```

```css
#three-layer {
  width: 100%;
  height: 100%;
  display: block;
}
```

## AnimationMixer 模式

对于 GLTF 或原创剪辑动画，请直接 seek mixer：

```js
function renderAt(time) {
  mixer.setTime(time);
  renderer.render(scene, camera);
}
```

如果存在多个 mixer，请从相同的 `time` 中同步 seek 所有 mixer。

## 适用场景

- 确定性 3D 对象、产品旋转、基于种子数据的粒子以及着色器板。
- 由 `time` 推导得出的相机移动。
- 当资源为本地资源，且在验证完成前已加载时，可使用 GLTF 动画片段。

## 避免

- 使用 `Date.now()`、`performance.now()` 或时钟差值来更新场景状态。
- 在自由运行的动画循环中遗留渲染关键工作。
- 在渲染时加载远程模型或纹理。
- 依赖 device-pixel-ratio 的输出。为视频渲染固定渲染器尺寸和像素比。
- 依赖上一帧历史的后处理效果，除非你能根据时间重建状态。

## 验证

编辑 Three.js 合成后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考资料

- HyperFrames 适配器源码：`packages/core/src/runtime/adapters/three.ts`。
- Three.js `WebGLRenderer` 文档：https://threejs.org/docs/pages/WebGLRenderer.html
- Three.js `AnimationMixer.setTime()` 文档：https://threejs.org/docs/pages/AnimationMixer.html
