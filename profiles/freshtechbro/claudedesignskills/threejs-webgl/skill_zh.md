# Three.js WebGL/WebGPU 开发

## 概述

Three.js 是使用 WebGL 和 WebGPU 在网页浏览器中创建 3D 图形的行业标准 JavaScript 库。这项技能为构建高性能、交互式 3D 体验提供了全面指导，包括场景、相机、渲染器、几何体、材质、灯光、纹理和动画。

## 核心概念

### 场景图架构

Three.js 使用分层场景图，其中所有 3D 对象按树状结构组织：

```javascript
Scene
├── Camera
├── Lights
│   ├── AmbientLight
│   ├── DirectionalLight
│   └── PointLight
├── Meshes
│   ├── Mesh (Geometry + Material)
│   └── InstancedMesh
└── Groups
```

### 基本组件

每个 Three.js 应用程序都需要这些核心元素：

1. **场景**：所有 3D 对象的容器
2. **相机**：定义观察视角
3. **渲染器**：将场景绘制到画布（WebGL 或 WebGPU）
4. **几何体**：定义对象的形状
5. **材质**：定义表面外观
6. **网格**：组合几何体和材质

## 快速入门模式

### 基本场景设置

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// 场景、相机、渲染器
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x333333);

const camera = new THREE.PerspectiveCamera(
  75, // 视场角
  window.innerWidth / window.innerHeight, // 纵横比
  0.1, // 近裁剪平面
  1000 // 远裁剪平面
);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// 灯光
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// 控制器
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// 动画循环
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();

// 处理窗口大小变化
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### WebGPU 设置（现代替代方案）

```javascript
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
renderer.toneMapping = THREE.LinearToneMapping;
renderer.toneMappingExposure = 1;
document.body.appendChild(renderer.domElement);
```

## 常见模式

### 1. 使用材质创建网格

```javascript
// 基本网格
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  roughness: 0.5,
  metalness: 0.5
});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 带纹理的网格
const loader = new THREE.TextureLoader();
const texture = loader.load('texture.jpg');
texture.colorSpace = THREE.SRGBColorSpace;

const texturedMaterial = new THREE.MeshStandardMaterial({
  map: texture
});
const mesh = new THREE.Mesh(geometry, texturedMaterial);
scene.add(mesh);
```

### 2. 灯光策略

```javascript
// 三点布光设置
function setupThreePointLight(scene) {
  // 主光（主光）
  const keyLight = new THREE.DirectionalLight(0xffffff, 3);
  keyLight.position.set(5, 10, 7.5);
  keyLight.castShadow = true;
  scene.add(keyLight);

  // 填充光（柔化阴影）
  const fillLight = new THREE.DirectionalLight(0xffffff, 1);
  fillLight.position.set(-5, 5, -5);
  scene.add(fillLight);

  // 边缘光（边缘定义）
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
  rimLight.position.set(0, 5, -10);
  scene.add(rimLight);

  // 环境光（基础照明）
  const ambient = new THREE.AmbientLight(0x404040, 0.5);
  scene.add(ambient);
}

// 物理光（真实感）
const bulbLight = new THREE.PointLight(0xffee88, 1, 100, 2);
bulbLight.power = 1700; // 流明（相当于 100W 灯泡）
bulbLight.castShadow = true;
scene.add(bulbLight);

// 半球光（天空+地面）
const hemiLight = new THREE.HemisphereLight(
  0xddeeff, // 天空颜色
  0x0f0e0d, // 地面颜色
  0.02
);
scene.add(hemiLight);
```

### 3. 实例几何体（性能优化）

```javascript
// 用于高效渲染数千个相似对象
const geometry = new THREE.SphereGeometry(0.1, 16, 16);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const instancedMesh = new THREE.InstancedMesh(geometry, material, 1000);

const matrix = new THREE.Matrix4();
const color = new THREE.Color();

for (let i = 0; i < 1000; i++) {
  matrix.setPosition(
    Math.random() * 10 - 5,
    Math.random() * 10 - 5,
    Math.random() * 10 - 5
  );
  instancedMesh.setMatrixAt(i, matrix);
  instancedMesh.setColorAt(i, color.setHex(Math.random() * 0xffffff));
}

instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);
```

### 4. 加载 3D 模型（glTF）

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

// 设置加载器
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

// 加载模型
gltfLoader.load('model.glb', (gltf) => {
  const model = gltf.scene;

  // 启用阴影
  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  scene.add(model);

  // 处理动画
  if (gltf.animations.length > 0) {
    const mixer = new THREE.AnimationMixer(model);
    const action = mixer.clipAction(gltf.animations[0]);
    action.play();

    // 在动画循环中：
    // mixer.update(deltaTime);
  }
});
```

### 5. 阴影配置

```javascript
// 在渲染器上启用阴影
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // 或 VSMShadowMap

// 配置光源阴影
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
directionalLight.shadow.radius = 4;
directionalLight.shadow.blurSamples = 8;

// 对象投射/接收阴影
mesh.castShadow = true;
mesh.receiveShadow = true;
```

### 6. 光线投射（交互）

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children, true);

  if (intersects.length > 0) {
    const object = intersects[0].object;
    object.material.color.set(0xff0000);
  }
}

window.addEventListener('click', onMouseClick);
```

## 集成模式

### 使用 GSAP 进行动画

```javascript
import gsap from 'gsap';

// 相机动画
gsap.to(camera.position, {
  x: 5,
  y: 3,
  z: 10,
  duration: 2,
  ease: "power2.inOut",
  onUpdate: () => {
    camera.lookAt(scene.position);
  }
});

// 网格属性动画
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  duration: 3,
  repeat: -1,
  ease: "none"
});
```

### 与 React 集成（参考 react-three-fiber 技能）

```javascript
// Three.js 与 React Three Fiber 天然集成
// 使用 react-three-fiber 技能了解 React 集成模式
```

### 与后处理集成

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // 强度
  0.4, // 半径
  0.85 // 阈值
);
composer.addPass(bloomPass);

// 在动画循环中：
composer.render();
```

## 性能优化

### 1. 几何体重用
```javascript
// 不好：为每个网格创建新的几何体
for (let i = 0; i < 100; i++) {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
}

// 好：重用几何体
const sharedGeometry = new THREE.BoxGeometry(1, 1, 1);
for (let i = 0; i < 100; i++) {
  const mesh = new THREE.Mesh(sharedGeometry, material);
  scene.add(mesh);
}
```

### 2. 使用 InstancedMesh 处理重复对象
对于数百/数千个相同的对象，使用 `InstancedMesh`（参考上述模式）。

### 3. 纹理优化
```javascript
// 压缩纹理
texture.generateMipmaps = true;
texture.minFilter = THREE.LinearMipmapLinearFilter;
texture.magFilter = THREE.LinearFilter;

// 使用 2 的幂尺寸（512, 1024, 2048）
// 考虑使用纹理图集处理多个小纹理
```

### 4. 细节层次（LOD）
```javascript
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);    // 0-50 单位
lod.addLevel(mediumDetailMesh, 50);  // 50-100 单位
lod.addLevel(lowDetailMesh, 100);    // 100+ 单位
scene.add(lod);
```

### 5. 视锥剔除
Three.js 自动剔除相机视野外的对象。确保对象具有正确的包围球：

```javascript
mesh.geometry.computeBoundingSphere();
```

### 6. 释放资源
```javascript
function disposeScene() {
  scene.traverse((object) => {
    if (object.geometry) object.geometry.dispose();
    if (object.material) {
      if (Array.isArray(object.material)) {
        object.material.forEach(material => material.dispose());
      } else {
        object.material.dispose();
      }
    }
  });
  renderer.dispose();
}
```

## 最佳实践

### 1. 使用动画时钟实现一致的时间控制
```javascript
const clock = new THREE.Clock();

function animate() {
  const deltaTime = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  // 使用 deltaTime 实现帧无关动画
  mesh.rotation.y += deltaTime * Math.PI * 0.5; // 每秒 90°

  renderer.render(scene, camera);
}
```

### 2. 相机设置指南
- **视场角**：大多数应用 45-75°
- **近裁剪平面**：尽可能远（避免 z-fighting）
- **远裁剪平面**：尽可能近（精度）
- **纵横比**：始终匹配画布尺寸

### 3. 材质选择
- **MeshBasicMaterial**：无光照，平面颜色（调试、UI）
- **MeshLambertMaterial**：经济型漫反射光照（移动端）
- **MeshPhongMaterial**：高光（旧标准）
- **MeshStandardMaterial**：PBR，真实感（推荐）
- **MeshPhysicalMaterial**：高级 PBR（清漆、透光）

### 4. 坐标系
- Three.js 使用右手坐标系
- +Y 是向上，+Z 是朝向相机，+X 是向右
- 旋转使用弧度（Math.PI = 180°）

### 5. 场景组织
```javascript
// 组合相关对象
const building = new THREE.Group();
building.add(walls, roof, windows);
scene.add(building);

// 使用有意义的名称
mesh.name = 'player-character';
const found = scene.getObjectByName('player-character');
```

## 常见陷阱

### 1. 窗口大小变化时未更新纵横比
始终在窗口调整大小时更新相机纵横比和投影矩阵。

### 2. 在动画循环中创建新对象
```javascript
// 不好：内存泄漏
function animate() {
  const geometry = new THREE.BoxGeometry(); // 每帧创建！
  // ...
}

// 好：循环外创建一次
const geometry = new THREE.BoxGeometry();
function animate() {
  // 重用几何体
}
```

### 3. 忘记启用阴影
记得在渲染器、光源和对象上启用阴影。

### 4. Z-fighting（闪烁）
- 增加近裁剪平面距离
- 减少远裁剪平面距离
- 避免重叠共面表面
- 使用 `material.polygonOffset = true` 与 `material.polygonOffsetFactor`

### 5. 颜色空间问题
```javascript
// 始终设置纹理颜色空间
texture.colorSpace = THREE.SRGBColorSpace;

// 设置渲染器输出编码
renderer.outputColorSpace = THREE.SRGBColorSpace;
```

### 6. 忘记释放资源
始终在不再需要时调用 `.dispose()` 对几何体、材质、纹理和渲染器。

## 资源

这项技能包含捆绑资源以加速 Three.js 开发：

### references/
- `api_reference.md`：核心类（场景、相机、渲染器等）的快速 API 参考
- `materials_guide.md`：材质类型和属性的综合指南
- `optimization_checklist.md`：性能优化策略

### scripts/
- `setup_scene.py`：生成 Three.js 场景设置模板代码
- `texture_optimizer.py`：批量优化网页纹理（调整大小、压缩）
- `gltf_validator.py`：使用前验证 glTF 模型

### assets/
- `starter_scene/`：完整的 HTML/JS 模板项目
- `shaders/`：自定义 GLSL 着色器示例（顶点、片段）
- `hdri/`：PBR 照明环境贴图
- `draco/`：用于压缩模型的 DRACO 解码器

## 高级主题

### 自定义着色器（GLSL）
```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uColor: { value: new THREE.Color(0x00ff00) }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(uColor * vUv.x, 1.0);
    }
  `
});
```

### 渲染目标（渲染到纹理）
```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512);

// 将场景渲染到纹理
renderer.setRenderTarget(renderTarget);
renderer.render(scene, camera);
renderer.setRenderTarget(null);

// 使用纹理
const material = new THREE.MeshBasicMaterial({
  map: renderTarget.texture
});
```

### GPU 计算（GPGPU）
使用 `GPUComputationRenderer` 处理粒子模拟、布料物理等。

## 何时使用这项技能

在以下情况下使用这项技能：
- 构建交互式 3D 网页体验
- 创建产品配置器或可视化器
- 实现 WebGL/WebGPU 渲染
- 处理 3D 模型、场景或动画
- 优化 Three.js 性能
- 将 Three.js 与其他库（GSAP、React 等）集成
- 调试 Three.js 渲染问题

对于 React 集成，使用 **react-three-fiber** 技能。
对于动画，结合 **gsap-scrolltrigger** 技能。
对于 UI 动画，使用 **motion-framer** 技能。
