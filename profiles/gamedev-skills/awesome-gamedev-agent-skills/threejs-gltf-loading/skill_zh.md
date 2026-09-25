# three.js glTF 加载

在 three.js 中加载 `.gltf`/`.glb` 模型并播放其动画，包括压缩的几何体（DRACO/Meshopt）和纹理（KTX2）。模式目标为 **r184**；除非要求迁移，否则保留现有项目的已固定版本。

## 何时使用

- 用于导入 3D 模型，将其添加到场景中，检查其节点层次结构，并使用 `AnimationMixer` 播放烘焙/蒙皮动画片段。
- 当文件为 `.gltf`/`.glb`，或代码从 `three/addons/loaders/...` 导入 `GLTFLoader` / `DRACOLoader` / `KTX2Loader` 时使用。

**不使用的情况：** 创建渲染器/相机/循环 → `threejs-scene-setup`。调整加载模型的表面外观、灯光或阴影 → `threejs-materials-lighting`。模型的创建/导出（Blender）不在范围内；在运行时优先使用 glTF 而不是 OBJ/FBX。

## 核心工作流程

1. **为何使用 glTF。** 它是一种传输格式：二进制顶点数据、PBR 材质和动画已准备好渲染，只需最小化解析。在 Web 上优先于 OBJ（无场景图、无动画）和 FBX（重量级）。
2. **使用 `GLTFLoader` 加载。** `loader.load(url, onLoad, onProgress, onError)`。结果 `gltf` 包含 `gltf.scene`（`Object3D` 根）、`gltf.animations`（`AnimationClip[]`）、`gltf.cameras` 和 `gltf.asset`。
3. **将 `gltf.scene` 添加到您的场景** 并进行框架化。使用 `traverse` / `getObjectByName` 检查层次结构以找到您将控制的部件。
4. **使用 `AnimationMixer` 播放动画。** 每个动画根一个混音器；`mixer.clipAction(clip).play()`；每帧使用 `mixer.update(delta)` 推进。
5. **解码压缩资源。** 添加 `DRACOLoader`（和/或 `KTX2Loader` + Meshopt），以便 DRACO 网格和 KTX2 纹理加载；将解码器指向其文件。
6. **验证加载内容** — 记录场景图和 `gltf.animations`，并确认模型可见（正确比例、有光照）且片段实际播放。

## 模式

### 1. 加载模型并框架化

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load(
  'assets/robot.glb',
  (gltf) => {
    const root = gltf.scene;
    scene.add(root);
    // 检查：gltf.animations 是一个 AnimationClip 数组。
    console.log('clips:', gltf.animations.map((c) => c.name));
  },
  (event) => console.log(`${(event.loaded / event.total) * 100}% loaded`),
  (error) => console.error('glTF 加载失败:', error)
);
```

### 2. 使用 AnimationMixer 播放蒙皮动画

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let mixer;                                  // 在外部声明，以便循环可见
const clock = new THREE.Clock();

new GLTFLoader().load('assets/character.glb', (gltf) => {
  scene.add(gltf.scene);
  mixer = new THREE.AnimationMixer(gltf.scene);          // 每个动画根一个混音器
  const clip = THREE.AnimationClip.findByName(gltf.animations, 'Run')
            ?? gltf.animations[0];
  mixer.clipAction(clip).play();
});

renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();
  if (mixer) mixer.update(dt);              // 以真实秒数推进动画
  renderer.render(scene, camera);
});
```

### 3. 在两个片段之间进行交叉淡入淡出

```js
const actions = {};
mixer = new THREE.AnimationMixer(gltf.scene);
for (const clip of gltf.animations) {
  actions[clip.name] = mixer.clipAction(clip);
}
actions['Idle'].play();

function transitionTo(name, duration = 0.3) {
  const next = actions[name];
  next.reset().play();
  for (const [n, action] of Object.entries(actions)) {
    if (n !== name) action.crossFadeTo(next, duration, false);
  }
}
```

### 4. DRACO 压缩的几何体

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const draco = new DRACOLoader();
// 指向您分发的解码器文件（或相同版本的固定 CDN 副本）。
draco.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.184.0/examples/jsm/libs/draco/');

const loader = new GLTFLoader();
loader.setDRACOLoader(draco);
loader.load('assets/city-draco.glb', (gltf) => scene.add(gltf.scene));
```

### 5. 查找并动画化命名的部件

```js
new GLTFLoader().load('assets/car.glb', (gltf) => {
  scene.add(gltf.scene);
  const wheels = [];
  gltf.scene.traverse((node) => {
    if (node.name.startsWith('Wheel')) wheels.push(node);
  });
  renderer.setAnimationLoop(() => {
    const dt = clock.getDelta();
    for (const w of wheels) w.rotation.x += dt * 4;
    renderer.render(scene, camera);
  });
});
```

## 陷阱

- **模型加载但不可见** → 它具有 PBR 材质且场景中没有灯光或环境。添加灯光或 `scene.environment`（参见 `threejs-materials-lighting`），并检查比例——glTF 使用米为单位，因此 0.01 比例的资产非常小。
- **`load` 是异步的** → `gltf` 仅在回调内部存在；在回调中声明 `mixer`/引用，或在回调中分配它们，或使用 `await loader.loadAsync(url)`。
- **动画从未移动** → 您没有每帧调用 `mixer.update(delta)`，或者您传递了毫秒而不是秒（使用 `clock.getDelta()`），或者您忘记了 `action.play()`。
- **DRACO/KTX2 模型失败** → 解码器/转码器路径错误或版本不匹配。`setDecoderPath`/`setTranscoderPath` 必须指向与您的 three.js 版本匹配的文件。
- **多个混音器冲突** → 每个动画根使用 **一个** `AnimationMixer` 并从中创建所有动作；不要为每个片段创建新的混音器。
- **烘焙的变换让您惊讶** → 导出器有时将缩放/旋转烘焙到子节点上。在依赖节点的本地变换之前导出层次结构（名称 + 位置/旋转/缩放）；如果绑定不可用，请从源重新导出。
- **原点偏移** → 将部件重新父级到新的 `Object3D` 下，以获得干净的枢轴，而不是对抗烘焙的偏移。

## 参考

- 对于完整的解码/转码设置（DRACO + Meshopt + KTX2 一起）、`loadAsync` + `LoadingManager` 进度条、使用 `SkeletonUtils.clone` 重用模型以及导出器指南（应用变换、一个干净的根），请阅读 `references/loaders-and-animation.md`。

## 相关技能

- `threejs-scene-setup` — 该模型渲染到的渲染器、相机和循环。
- `threejs-materials-lighting` — 使 PBR 模型看起来正确的灯光/环境。
- `fps-shooter` — 组合 three.js 技能的 3D 类型。
