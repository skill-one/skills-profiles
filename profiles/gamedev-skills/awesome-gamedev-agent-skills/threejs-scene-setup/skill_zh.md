# three.js 场景设置

创建 three.js 应用的基础：模块加载、场景/相机/渲染器三重组合、渲染循环、响应式调整大小和相机控制。模式目标为 **r184**。在更改现有项目之前，请先读取已安装的 `three` 版本，因为示例和插件会在版本之间移动。

## 使用场景

- 在初始化 three.js 场景、修复空白/黑色画布、使画布响应式、设置动画循环或添加 `OrbitControls` 时使用。
- 当 `package.json` 依赖 `three` 且代码执行 `import * as THREE from 'three'` 时使用。

**不使用场景：** 加载 `.gltf`/`.glb` 模型或蒙皮动画 → `threejs-gltf-loading`。材质、灯光、阴影、环境贴图 → `threejs-materials-lighting`。2D 渲染 → `pixijs-rendering`。

## 核心工作流程

1. **使用导入映射将 three.js 作为 ES 模块加载。** 自 r147 起，裸指定符 `'three'` 和 `'three/addons/'` 必须映射（在 HTML 中或通过打包器）。插件（控制、加载器）位于 `three/addons/...` 下。
2. **创建三重组合。** 一个 `Scene`（图的根节点）、一个从原点向后移动的 `PerspectiveCamera(fov, aspect, near, far)` 和一个 `WebGLRenderer`，其 `domElement` 位于 DOM 中。设置大小和 `pixelRatio`。
3. **添加网格。** `new Mesh(geometry, material)` 和 `scene.add(mesh)`。对于带灯光材质，还需要一个灯光（见 `threejs-materials-lighting`）。
4. **使用 `renderer.setAnimationLoop(fn)` 驱动渲染循环。** 这是现代、WebXR-/WebGPU 安全的 `requestAnimationFrame` 手动编写的替代方案。使用 `Clock` 获取 delta 时间。
5. **处理调整大小** 以使相机宽高比和渲染器与画布匹配；更新 `camera.aspect`，调用 `updateProjectionMatrix()` 和 `renderer.setSize(...)`。
6. **添加 `OrbitControls`** 以在开发过程中进行轨道/平移/缩放。在确认实际渲染了内容（一个带灯光的立方体、控制响应）之前，不要假设成功。

## 模式

### 1. HTML 导入映射 + 模块入口（无打包器）

```html
<canvas id="c"></canvas>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.184.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.184.0/examples/jsm/"
  }
}
</script>
<script type="module" src="./main.js"></script>
```

使用打包器（Vite/webpack）时，跳过导入映射，只需 `npm i three`；相同的 `import` 语句可以解析。

### 2. 场景 + 相机 + 渲染器

```js
// main.js
import * as THREE from 'three';

const canvas = document.querySelector('#c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // 限制性能
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101018);

const camera = new THREE.PerspectiveCamera(
  60,                                   // 垂直视场（度）
  window.innerWidth / window.innerHeight, // 宽高比
  0.1,                                  // 近
  100                                   // 远
);
camera.position.set(3, 2, 5);
camera.lookAt(0, 0, 0);

const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshNormalMaterial()        // 无灯光；显示方向而不需要灯光
);
scene.add(cube);
```

### 3. 渲染循环（setAnimationLoop + Clock）

```js
const clock = new THREE.Clock();

renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();          // 上一帧以来的秒数
  cube.rotation.x += dt;                // 帧率无关
  cube.rotation.y += dt * 0.7;
  renderer.render(scene, camera);
});
// renderer.setAnimationLoop(null); // 停止循环
```

### 4. 响应式调整大小

```js
function onResize() {
  const w = window.innerWidth, h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();      // 修改宽高比后需要
  renderer.setSize(w, h);
}
window.addEventListener('resize', onResize);
```

### 5. OrbitControls（轨道 / 平移 / 缩放）

```js
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;          // 惯性感
controls.target.set(0, 0, 0);

renderer.setAnimationLoop(() => {
  controls.update();                    // 开启阻尼时每帧需要
  renderer.render(scene, camera);
});
```

## 陷阱

- **`Failed to resolve module specifier "three"`** → 缺少导入映射（或打包器配置）。映射 `"three"` 和 `"three/addons/"`；插件路径必须以 `/` 结尾。
- **黑色画布，无错误** → 相机位于原点（在对象内部/后面），或者你使用了带灯光材质（`MeshStandardMaterial`）但没有灯光。将相机向后移动；使用 `MeshNormalMaterial`/`MeshBasicMaterial` 首先验证几何体。
- **无动画** → 你从未在循环内调用 `renderer.render`，或者你调用了 `setAnimationLoop` 但在循环外渲染。
- **调整大小时视图被拉伸/挤压** → 你调整了渲染器但没有更新 `camera.aspect` + `updateProjectionMatrix()`。
- **在高 DPI 上模糊或有锯齿** → 设置 `renderer.setPixelRatio(...)`；限制它（≈2），以避免 4K/视网膜屏幕性能下降。
- **OrbitControls 感觉死板** → 开启 `enableDamping = true` 时，你必须每帧调用 `controls.update()`。
- **旧教程使用 `<script src="three.min.js">`** → 自 r147 起 three.js 仅提供 ES 模块；使用 `type="module"` + 导入映射。

## 参考

- 对于坐标约定、场景图（`Group`、父子变换、`Object3D` 添加/删除）、`OrthographicCamera` 用于 2.5D，以及丢弃几何体/材质/纹理以避免内存泄漏，请阅读 `references/scene-graph.md`。

## 相关技能

- `threejs-materials-lighting` — 使表面带灯光效果（灯光、阴影、PBR）。
- `threejs-gltf-loading` — 加载 3D 模型并播放其动画。
- `pixijs-rendering` — 浏览器中的 2D 渲染。
- `fps-shooter` — 一个 3D 类型模板，组合了 three.js 技能。
