# HyperFrames的Three.js

HyperFrames通过其`three`运行时适配器支持Three.js。该适配器不拥有您的场景。它会发布HyperFrames时间并派发一个seek事件，以便您的合成可以渲染精确的帧。

## 协议

- 尽可能同步创建场景、相机、渲染器、材质和资源。
- 从HyperFrames时间渲染，而不是从墙上时钟时间渲染。
- 监听`hf-seek`事件并精确渲染该时间。
- 在渲染关键seek之前加载模型、纹理和HDRIs。不要在seek时间获取它们。
- 避免使用`requestAnimationFrame`或`renderer.setAnimationLoop`作为渲染关键运动的来源。

适配器会设置`window.__hfThreeTime`并在每次seek时派发`new CustomEvent("hf-seek", { detail: { time } })`。

## 基本模式

```html
<canvas id="three-layer"></canvas>
<script type="module">
  import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.181.2/+esm";

  const canvas = document.getElementById("three-layer");
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  // 匹配您合成帧的大小。
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

## AnimationMixer模式

对于GLTF或编写的剪辑动画，直接seek mixer：

```js
function renderAt(time) {
  mixer.setTime(time);
  renderer.render(scene, camera);
}
```

如果有多个mixer，从相同的`time`seek所有mixer。

## 适用场景

- 确定性的3D对象、产品旋转、具有种子数据的粒子以及着色器板。
- 由`time`派生的相机移动。
- 当资源本地且在验证完成前加载的GLTF动画剪辑。

## 避免

- 使用`Date.now()`、`performance.now()`或时钟差值来更新场景状态。
- 在自由运行动画循环内留下渲染关键工作。
- 在渲染时间加载远程模型或纹理。
- 依赖于设备像素比输出。为视频渲染固定渲染器大小和像素比。
- 除非您可以从时间重建状态，否则依赖先前帧历史的后处理步骤。

## 验证

编辑完Three.js合成后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames适配器源代码：`packages/core/src/runtime/adapters/three.ts`。
- Three.js `WebGLRenderer`文档：https://threejs.org/docs/pages/WebGLRenderer.html
- Three.js `AnimationMixer.setTime()`文档：https://threejs.org/docs/pages/AnimationMixer.html
