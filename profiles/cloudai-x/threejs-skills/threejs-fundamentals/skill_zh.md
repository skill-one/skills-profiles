# Three.js 基础知识

## 快速入门

```javascript
import * as THREE from "three";

// 创建场景、相机、渲染器
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000,
);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// 添加网格
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 添加光源
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

camera.position.z = 5;

// 动画循环
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();

// 处理窗口大小变化
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## 核心类

### Scene

所有3D对象、光源和相机的容器。

```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000); // 纯色
scene.background = texture; // 天空盒纹理
scene.background = cubeTexture; // 立方体贴图
scene.environment = envMap; // PBR环境贴图
scene.fog = new THREE.Fog(0xffffff, 1, 100); // 线性雾
scene.fog = new THREE.FogExp2(0xffffff, 0.02); // 指数雾
```

### Cameras

**PerspectiveCamera** - 最常用，模拟人眼视角。

```javascript
// PerspectiveCamera(fov, aspect, near, far)
const camera = new THREE.PerspectiveCamera(
  75, // 视野(度)
  window.innerWidth / window.innerHeight, // 纵横比
  0.1, // 近裁剪面
  1000, // 远裁剪面
);

camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);
camera.updateProjectionMatrix(); // 改变fov、aspect、near、far后调用
```

**OrthographicCamera** - 无透视畸变，适合2D/等距视图。

```javascript
// OrthographicCamera(left, right, top, bottom, near, far)
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 10;
const camera = new THREE.OrthographicCamera(
  (frustumSize * aspect) / -2,
  (frustumSize * aspect) / 2,
  frustumSize / 2,
  frustumSize / -2,
  0.1,
  1000,
);
```

**ArrayCamera** - 多个视口带子相机。

```javascript
const cameras = [];
for (let i = 0; i < 4; i++) {
  const subcamera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  subcamera.viewport = new THREE.Vector4(
    Math.floor(i % 2) * 0.5,
    Math.floor(i / 2) * 0.5,
    0.5,
    0.5,
  );
  cameras.push(subcamera);
}
const arrayCamera = new THREE.ArrayCamera(cameras);
```

**CubeCamera** - 渲染环境贴图用于反射。

```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256);
const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);

// 用于反射
material.envMap = cubeRenderTarget.texture;

// 每帧更新(消耗性能!)
cubeCamera.position.copy(reflectiveMesh.position);
cubeCamera.update(renderer, scene);
```

### WebGLRenderer

```javascript
const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector("#canvas"), // 可选现有画布
  antialias: true, // 平滑边缘
  alpha: true, // 透明背景
  powerPreference: "high-performance", // GPU提示
  preserveDrawingBuffer: true, // 用于截图
});

renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// 亮度映射
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// 色彩空间(Three.js r152+)
renderer.outputColorSpace = THREE.SRGBColorSpace;

// 阴影
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// 清除颜色
renderer.setClearColor(0x000000, 1);

// 渲染
renderer.render(scene, camera);
```

### Object3D

所有3D对象的基类。Mesh、Group、Light、Camera都继承自Object3D。

```javascript
const obj = new THREE.Object3D();

// 变换
obj.position.set(x, y, z);
obj.rotation.set(x, y, z); // 欧拉角(弧度)
obj.quaternion.set(x, y, z, w); // 四元数旋转
obj.scale.set(x, y, z);

// 局部与世界变换
obj.getWorldPosition(targetVector);
obj.getWorldQuaternion(targetQuaternion);
obj.getWorldDirection(targetVector);

// 层级结构
obj.add(child);
obj.remove(child);
obj.parent;
obj.children;

// 可见性
obj.visible = false;

// 层级(用于选择性渲染/raycasting)
obj.layers.set(1);
obj.layers.enable(2);
obj.layers.disable(0);

// 遍历层级
obj.traverse((child) => {
  if (child.isMesh) child.material.color.set(0xff0000);
});

// 矩阵更新
obj.matrixAutoUpdate = true; // 默认: 自动更新矩阵
obj.updateMatrix(); // 手动矩阵更新
obj.updateMatrixWorld(true); // 递归更新世界矩阵
```

### Group

组织对象的空容器。

```javascript
const group = new THREE.Group();
group.add(mesh1);
group.add(mesh2);
scene.add(group);

// 整体变换
group.position.x = 5;
group.rotation.y = Math.PI / 4;
```

### Mesh

结合几何体和材质。

```javascript
const mesh = new THREE.Mesh(geometry, material);

// 多个材质(每个几何体组一个)
const mesh = new THREE.Mesh(geometry, [material1, material2]);

// 有用属性
mesh.geometry;
mesh.material;
mesh.castShadow = true;
mesh.receiveShadow = true;

// 视锥剔除
mesh.frustumCulled = true; // 默认: 如果在相机视图外则跳过

// 渲染顺序
mesh.renderOrder = 10; // 更高 = 渲染更晚
```

## 坐标系

Three.js使用**右手坐标系**：

- **+X** 指向右侧
- **+Y** 指向上方
- **+Z** 指向观察者(屏幕外)

```javascript
// 坐标轴辅助
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper); // 红=X, 绿=Y, 蓝=Z
```

## 数学工具

### Vector3

```javascript
const v = new THREE.Vector3(x, y, z);
v.set(x, y, z);
v.copy(otherVector);
v.clone();

// 操作(原地修改)
v.add(v2);
v.sub(v2);
v.multiply(v2);
v.multiplyScalar(2);
v.divideScalar(2);
v.normalize();
v.negate();
v.clamp(min, max);
v.lerp(target, alpha);

// 计算(返回新值)
v.length();
v.lengthSq(); // 比length()更快
v.distanceTo(v2);
v.dot(v2);
v.cross(v2); // 修改v
v.angleTo(v2);

// 变换
v.applyMatrix4(matrix);
v.applyQuaternion(q);
v.project(camera); // 世界到NDC
v.unproject(camera); // NDC到世界
```

### Matrix4

```javascript
const m = new THREE.Matrix4();
m.identity();
m.copy(other);
m.clone();

// 构建变换
m.makeTranslation(x, y, z);
m.makeRotationX(theta);
m.makeRotationY(theta);
m.makeRotationZ(theta);
m.makeRotationFromQuaternion(q);
m.makeScale(x, y, z);

// 组合/分解
m.compose(position, quaternion, scale);
m.decompose(position, quaternion, scale);

// 操作
m.multiply(m2); // m = m * m2
m.premultiply(m2); // m = m2 * m
m.invert();
m.transpose();

// 相机矩阵
m.makePerspective(left, right, top, bottom, near, far);
m.makeOrthographic(left, right, top, bottom, near, far);
m.lookAt(eye, target, up);
```

### Quaternion

```javascript
const q = new THREE.Quaternion();
q.setFromEuler(euler);
q.setFromAxisAngle(axis, angle);
q.setFromRotationMatrix(matrix);

q.multiply(q2);
q.slerp(target, t); // 球面插值
q.normalize();
q.invert();
```

### Euler

```javascript
const euler = new THREE.Euler(x, y, z, "XYZ"); // 顺序很重要!
euler.setFromQuaternion(q);
euler.setFromRotationMatrix(m);

// 旋转顺序: 'XYZ', 'YXZ', 'ZXY', 'XZY', 'YZX', 'ZYX'
```

### Color

```javascript
const color = new THREE.Color(0xff0000);
const color = new THREE.Color("red");
const color = new THREE.Color("rgb(255, 0, 0)");
const color = new THREE.Color("#ff0000");

color.setHex(0x00ff00);
color.setRGB(r, g, b); // 0-1范围
color.setHSL(h, s, l); // 0-1范围

color.lerp(otherColor, alpha);
color.multiply(otherColor);
color.multiplyScalar(2);
```

### MathUtils

```javascript
THREE.MathUtils.clamp(value, min, max);
THREE.MathUtils.lerp(start, end, alpha);
THREE.MathUtils.mapLinear(value, inMin, inMax, outMin, outMax);
THREE.MathUtils.degToRad(degrees);
THREE.MathUtils.radToDeg(radians);
THREE.MathUtils.randFloat(min, max);
THREE.MathUtils.randInt(min, max);
THREE.MathUtils.smoothstep(x, min, max);
THREE.MathUtils.smootherstep(x, min, max);
```

## 常见模式

### 正确清理

```javascript
function dispose() {
  // 清理几何体
  mesh.geometry.dispose();

  // 清理材质
  if (Array.isArray(mesh.material)) {
    mesh.material.forEach((m) => m.dispose());
  } else {
    mesh.material.dispose();
  }

  // 清理纹理
  texture.dispose();

  // 从场景移除
  scene.remove(mesh);

  // 清理渲染器
  renderer.dispose();
}
```

### Clock用于动画

```javascript
const clock = new THREE.Clock();

function animate() {
  const delta = clock.getDelta(); // 帧间隔时间(秒)
  const elapsed = clock.getElapsedTime(); // 总时间(秒)

  mesh.rotation.y += delta * 0.5; // 不论帧率如何保持一致速度

  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
```

### 响应式画布

```javascript
function onWindowResize() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
}
window.addEventListener("resize", onWindowResize);
```

### 加载管理器

```javascript
const manager = new THREE.LoadingManager();

manager.onStart = (url, loaded, total) => console.log("开始加载");
manager.onLoad = () => console.log("全部加载完成");
manager.onProgress = (url, loaded, total) => console.log(`${loaded}/${total}`);
manager.onError = (url) => console.error(`加载错误 ${url}`);

const textureLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);
```

## 性能技巧

1. **限制绘制调用**: 合并几何体、使用实例化、纹理图集
2. **视锥剔除**: 默认开启，确保包围盒正确
3. **细节层次(LOD)**: 使用`THREE.LOD`进行距离基于的网格切换
4. **对象池**: 重用对象而非创建/销毁
5. **避免循环中调用`getWorldPosition`**: 缓存结果

```javascript
// 合并静态几何体
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
const merged = mergeGeometries([geo1, geo2, geo3]);

// LOD
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);
lod.addLevel(medDetailMesh, 50);
lod.addLevel(lowDetailMesh, 100);
scene.add(lod);
```

## 参考资料见

- `threejs-geometry` - 几何体创建和操作
- `threejs-materials` - 材质类型和属性
- `threejs-lighting` - 光源类型和阴影
