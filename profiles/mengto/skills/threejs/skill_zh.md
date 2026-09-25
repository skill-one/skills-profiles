# Three.js — WebGL 3D 场景技能

## 何时使用
- 真实 3D：产品旋转、交互式英雄场景、着色器/材质效果、3D 数据可视化
- 需要比“背景效果”更完全的控制
- 可以预算时间用于资源管线 + 性能调优

## 核心心智模型
- 创建：
  - `Scene`（根图）
  - `Camera`（透视/正交）
  - `Renderer`（`WebGLRenderer`）
  - `Mesh` = `Geometry` + `Material`
  - 灯光（如果使用非未光照材质）
- 渲染循环：
  - `requestAnimationFrame(animate)`
  - 更新基于时间的动画、控制、混合器，然后 `renderer.render(scene, camera)`

## 关键 API/模式
- 设置：
  - `const renderer = new THREE.WebGLRenderer({ canvas, antialias, alpha })`
  - `renderer.setSize(width, height, false)`
  - `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`
- 相机：
  - `camera.aspect = width / height; camera.updateProjectionMatrix()`
- 场景图：
  - `scene.add(object)` / `object.position/rotation/scale`
- 加载资源：
  - `GLTFLoader`（模型）、`TextureLoader`（图像）、`DRACOLoader`（压缩 glTF）
- 控制（常见）：
  - `OrbitControls`（调试/产品）、`PointerLockControls`（FPS）、自定义指针处理器
- 清理（在 SPAs 中很重要）：
  - `geometry.dispose()`，`material.dispose()`，`texture.dispose()`，`renderer.dispose()`
  - 移除事件监听器；取消 RAF。

## 常见陷阱
- 未处理调整大小 → 渲染拉伸/裁剪
- 设备像素比过高 → 移动 GPU 熔断
- 泄漏 WebGL 资源（未清理）→ 路由更改后的崩溃
- 加载巨大的纹理/模型 → 启动缓慢；使用压缩纹理、Draco/KTX2、较小的贴图
- 使用过多灯光/阴影 → 昂贵；在可能的情况下使用烘焙纹理模拟光照

## 快速配方

### 1) 最小旋转立方体
```js
import * as THREE from "three";

const canvas = document.querySelector("#c");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 0, 4);

const geom = new THREE.BoxGeometry(1, 1, 1);
const mat = new THREE.MeshStandardMaterial({ color: 0x7c3aed });
const mesh = new THREE.Mesh(geom, mat);
scene.add(mesh);

scene.add(new THREE.AmbientLight(0xffffff, 0.8));
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(2, 2, 2);
scene.add(dir);

function resize() {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

function animate(t) {
  mesh.rotation.y = t * 0.0006;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

### 2) 尊重减少运动
- 如果 `prefers-reduced-motion: reduce`，渲染静态帧（无 RAF）或缓慢更新。

## 需要询问用户的内容
- 这是装饰性（英雄）还是功能性 3D（产品查看器）？
- 目标设备：移动设备？旧款 iPhone？
- 资源格式可用性（glTF、HDRI、纹理）和文件大小限制
- 无障碍/减少运动要求
