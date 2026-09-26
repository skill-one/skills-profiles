# Three.js 开发

使用 Three.js（一个跨浏览器的 WebGL/WebGPU 库）构建高性能的 3D 网页应用。

## 何时使用这项技能

在以下工作中使用：
- 3D 场景、模型、动画或可视化
- WebGL/WebGPU 渲染和图形编程
- 交互式 3D 体验（游戏、配置器、数据可视化）
- 相机控制、光照、材质或着色器
- 加载 3D 资产（GLTF、FBX、OBJ）或纹理
- 后处理效果（泛光、景深、SSAO）
- 物理模拟、VR/XR 体验或空间音频
- 性能优化（实例化、LOD、视锥剔除）

## 逐步学习路径

### 第 1 级：入门
- 加载 `references/00-fundamentals.md` - 基础知识
- 加载 `references/01-getting-started.md` - 场景设置、基本几何体、材质、光照、渲染循环

### 第 2 级：常见任务
- **资产加载**：`references/02-loaders.md` - GLTF、FBX、OBJ、纹理加载器
- **纹理**：`references/03-textures.md` - 类型、映射、包裹、过滤
- **相机**：`references/04-cameras.md` - 透视、正交、控制
- **光照**：`references/05-lights.md` - 类型、阴影、辅助工具
- **动画**：`references/06-animations.md` - 片段、混合器、关键帧
- **数学**：`references/07-math.md` - 向量、矩阵、四元数、曲线
- **几何体**：`references/18-geometry.md` - 内置形状、BufferGeometry、自定义几何体、实例化
- **材质**：`references/11-materials.md` - PBR、基础、Phong、Lambert、物理、卡通、法线、深度、原始、着色器材质、材质属性

### 第 3 级：交互与特效
- **交互**：`references/08-interaction.md` - 光线投射、拾取、变换
- **后处理**：`references/09-postprocessing.md` - 渲染通道、泛光、SSAO、SSR
- **控制（插件）**：`references/10-controls.md` - 轨道、变换、第一人称

### 第 4 级：高级渲染
- **高级材质**：`references/11-materials-advanced.md` - PBR、自定义着色器
- **性能**：`references/12-performance.md` - 实例化、LOD、批处理、剔除
- **节点材质（TSL）**：`references/13-node-materials.md` - 着色器图、计算

### 第 5 级：专业
- **物理**：`references/14-physics-vr.md` - Ammo、Rapier、Jolt、VR/XR
- **高级加载器**：`references/15-specialized-loaders.md` - SVG、VRML、特定领域
- **WebGPU**：`references/16-webgpu.md` - 现代后端、计算着色器
- **着色器**：`references/17-shader.md` - GLSL、ShaderMaterial、uniforms、自定义效果

## 快速入门模板

```javascript
// 1. 场景、相机、渲染器
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 2. 添加对象
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 3. 添加光照
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

// 4. 动画循环
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
```

## 外部资源

- 官方文档：https://threejs.org/docs/
- 示例：https://threejs.org/examples/
- 编辑器：https://threejs.org/editor/
- Discord：https://discord.gg/56GBJwAnUS
