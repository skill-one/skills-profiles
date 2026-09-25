# three.js 材质与光照

让 three.js 表面看起来正确：选择正确的材质，照亮场景，启用阴影，并添加基于图像的光照。模式目标为 **r184**，并已针对 **r184** 进行验证（自 r155 起，光照默认为基于物理的）。

## 使用场景

- 当网格渲染为黑色或平面时，在选择材质、添加光源、启用阴影或设置环境贴图反射（IBL）时使用。
- 当代码构建 `MeshStandardMaterial`、`DirectionalLight` 等对象，或设置 `renderer.shadowMap.enabled` 或 `scene.environment` 时使用。

**不使用场景**：渲染器/相机/循环 → `threejs-scene-setup`。加载模型（其 PBR 材质与之互补）→ `threejs-gltf-loading`。自定义 GLSL/`ShaderMaterial` 是一个独立主题；关于便携式概念，请参阅 `shader-programming`。

## 核心工作流程

1. **根据需求选择材质**。`MeshStandardMaterial`（PBR：`roughness`、`metalness`，对光源/IBL 响应）用于真实感；`MeshPhysicalMaterial` 用于高光涂层/透射；`MeshBasicMaterial`（无光照，忽略光源）用于 UI/平面；`MeshNormalMaterial`/`MeshDepthMaterial` 用于调试。
2. **添加光源，否则什么也显示不出来**。有光照的材质需要一个光源和/或 `scene.environment`。将柔和的填充（`AmbientLight`/`HemisphereLight`）与主要的 `DirectionalLight` 结合使用。
3. **注意光照强度**。自 r155 起，光照基于物理；现代强度高于旧教程（一个主要的 `DirectionalLight` ≈ 1–3）。
4. **在三个地方启用阴影**。`renderer.shadowMap.enabled = true`，光源的 `castShadow = true`，以及每个网格的 `castShadow`/`receiveShadow`。然后调整光源的阴影相机以适应场景。
5. **使用环境贴图进行地面反射**。将等矩形或 PMREM 处理的纹理分配给 `scene.environment`；PBR 材质会自动拾取它。
6. **在真实光照下进行验证**——确认表面响应主要光源（高光移动），阴影落在预期位置，反射看起来合理。

## 模式

### 1. 3 个光源架下的 PBR 材质

```js
import * as THREE from 'three';

const material = new THREE.MeshStandardMaterial({
  color: 0xcc4444,
  roughness: 0.5,     // 0 = 镜面，1 = 完全哑光
  metalness: 0.0,     // 0 = 介电质（塑料/木材），1 = 金属
});
const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), material);
scene.add(mesh);

// 柔和的天空/地面填充 + 一个方向性主要光源。
scene.add(new THREE.HemisphereLight(0xbbddff, 0x443322, 1.0)); // 天空，地面，强度
const key = new THREE.DirectionalLight(0xffffff, 2.5);
key.position.set(5, 10, 7);
scene.add(key);
```

### 2. 无光照材质（不需要光源）

```js
// MeshBasicMaterial 忽略光源 — 用于平面颜色，UI，或精灵/标签。
const flat = new THREE.MeshBasicMaterial({ color: 0x44aa88 });
// 带纹理的颜色贴图应标记为 sRGB，以防止颜色失真：
const tex = new THREE.TextureLoader().load('assets/logo.png');
tex.colorSpace = THREE.SRGBColorSpace;
const logo = new THREE.MeshBasicMaterial({ map: tex, transparent: true });
```

### 3. 阴影（三个必需开关 + 相机适配）

```js
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;     // 更柔和的边缘

const sun = new THREE.DirectionalLight(0xffffff, 3);
sun.position.set(8, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);                   // 默认 512；提高以获得清晰
// DirectionalLight 使用正交相机 — 紧密适配场景：
const cam = sun.shadow.camera;
cam.near = 1; cam.far = 40;
cam.left = -15; cam.right = 15; cam.top = 15; cam.bottom = -15;
scene.add(sun);

mesh.castShadow = true;
ground.receiveShadow = true;                          // 一个平面来接收阴影
```

### 4. 材质上的 PBR 贴图

```js
const loader = new THREE.TextureLoader();
const colorMap = loader.load('assets/brick_color.jpg');
colorMap.colorSpace = THREE.SRGBColorSpace;           // 颜色贴图是 sRGB
const normalMap = loader.load('assets/brick_normal.jpg'); // 数据贴图保持线性
const roughMap  = loader.load('assets/brick_rough.jpg');

const brick = new THREE.MeshStandardMaterial({
  map: colorMap,
  normalMap,
  roughnessMap: roughMap,
  metalness: 0,
});
```

### 5. 来自 HDR 环境的基于图像的光照

```js
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

new RGBELoader().load('assets/studio.hdr', (hdr) => {
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = hdr;     // 光源 + 反射所有 PBR 材质
  scene.background = hdr;       // 可选：将其作为背景显示
});
// 可选的电影感色调曲线：
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
```

## 陷阱

- **网格完全为黑色** → 有光照的材质但没有光源和没有 `scene.environment`。
  添加光源或环境贴图；为确认几何形状，暂时切换到 `MeshBasicMaterial`/`MeshNormalMaterial`。
- **即使有光源，场景仍然太暗** → 旧教程的强度。r155+ 是基于物理的；提高强度（主要光源 ≈ 2–3）或添加环境贴图。
- **阴影不出现** → 你遗漏了三个开关之一 (`renderer.shadowMap.enabled`、`light.castShadow`、网格 `castShadow`/`receiveShadow`)。
- **阴影被截断或块状** → `DirectionalLight` 的正交 `shadow.camera` 截锥太大/太小或不覆盖场景；收紧 `left/right/top/bottom/near/far` 并提高 `shadow.mapSize`。使用 `new THREE.CameraHelper(light.shadow.camera)` 进行可视化。
- **阴影痤疮 / peter-panning** → 调整 `light.shadow.bias`（小的负值）和 `light.shadow.normalBias`。
- **颜色看起来失真 / 过亮** → 颜色（反照率）贴图需要 `texture.colorSpace = THREE.SRGBColorSpace`；法线/粗糙度/金属度贴图必须保持线性（将它们保留为 `NoColorSpace`）。
- **PointLight 阴影严重影响性能** → 一个点光源渲染场景 6 次（立方体贴图）。优先使用一个投射阴影的 `DirectionalLight`；在其他地方使用更便宜的伪造。

## 参考

- 关于材质速查表（哪种 `Mesh*Material` 对应哪种外观）、光源类型及其参数/单位、透明度与 `alphaTest` 排序，以及 `PMREMGenerator`/`RoomEnvironment` 路径（无需 HDR 文件即可实现 IBL），请阅读 `references/materials-lights-table.md`。

## 相关技能

- `threejs-scene-setup` — 渲染器、相机和循环（设置 `shadowMap`、色调映射）。
- `threejs-gltf-loading` — 模型带有 PBR 材质，此技能进行调优。
- `shader-programming` — 自定义着色器效果（引擎无关的概念）。
