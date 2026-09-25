# Three.js 纹理

## 快速入门

```javascript
import * as THREE from "three";

// 加载纹理
const loader = new THREE.TextureLoader();
const texture = loader.load("texture.jpg");

// 应用于材质
const material = new THREE.MeshStandardMaterial({
  map: texture,
});
```

## 纹理加载

### 基本加载

```javascript
const loader = new THREE.TextureLoader();

// 带回调的异步加载
loader.load(
  "texture.jpg",
  (texture) => console.log("Loaded"),
  (progress) => console.log("Progress"),
  (error) => console.error("Error"),
);

// 同步风格（内部异步加载）
const texture = loader.load("texture.jpg");
material.map = texture;
```

### Promise 封装

```javascript
function loadTexture(url) {
  return new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(url, resolve, undefined, reject);
  });
}

// 使用
const [colorMap, normalMap, roughnessMap] = await Promise.all([
  loadTexture("color.jpg"),
  loadTexture("normal.jpg"),
  loadTexture("roughness.jpg"),
]);
```

## 纹理配置

### 色彩空间

对准确色彩再现至关重要。

```javascript
// 色彩/反照率纹理 - 使用 sRGB
colorTexture.colorSpace = THREE.SRGBColorSpace;

// 数据纹理（法线、粗糙度、金属度、AO） - 保持默认
// 不要为数据纹理设置 colorSpace（默认为 NoColorSpace）
```

### 包装模式

```javascript
texture.wrapS = THREE.RepeatWrapping; // 水平
texture.wrapT = THREE.RepeatWrapping; // 垂直

// 选项：
// THREE.ClampToEdgeWrapping - 拉伸边缘像素（默认）
// THREE.RepeatWrapping - 平铺纹理
// THREE.MirroredRepeatWrapping - 平铺带镜像翻转
```

### 重复、偏移、旋转

```javascript
// 平铺纹理 4x4
texture.repeat.set(4, 4);
texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;

// 偏移（0-1 范围）
texture.offset.set(0.5, 0.5);

// 旋转（弧度，绕中心）
texture.rotation = Math.PI / 4;
texture.center.set(0.5, 0.5); // 旋转基准点
```

### 过滤

```javascript
// 缩小（纹理大于屏幕像素）
texture.minFilter = THREE.LinearMipmapLinearFilter; // 默认，平滑
texture.minFilter = THREE.NearestFilter; // 像素化
texture.minFilter = THREE.LinearFilter; // 平滑，无 mipmap

// 放大（纹理小于屏幕像素）
texture.magFilter = THREE.LinearFilter; // 平滑（默认）
texture.magFilter = THREE.NearestFilter; // 像素化（复古游戏）

// 各向异性过滤（角度更清晰）
texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
```

### 生成 Mipmaps

```javascript
// 通常默认为 true
texture.generateMipmaps = true;

// 非幂等 2 纹理或数据纹理禁用
texture.generateMipmaps = false;
texture.minFilter = THREE.LinearFilter;
```

## 纹理类型

### 普通纹理

```javascript
const texture = new THREE.Texture(image);
texture.needsUpdate = true;
```

### 数据纹理

从原始数据创建纹理。

```javascript
// 创建渐变纹理
const size = 256;
const data = new Uint8Array(size * size * 4);

for (let i = 0; i < size; i++) {
  for (let j = 0; j < size; j++) {
    const index = (i * size + j) * 4;
    data[index] = i; // R
    data[index + 1] = j; // G
    data[index + 2] = 128; // B
    data[index + 3] = 255; // A
  }
}

const texture = new THREE.DataTexture(data, size, size);
texture.needsUpdate = true;
```

### Canvas 纹理

```javascript
const canvas = document.createElement("canvas");
canvas.width = 256;
canvas.height = 256;
const ctx = canvas.getContext("2d");

// 在 canvas 上绘制
ctx.fillStyle = "red";
ctx.fillRect(0, 0, 256, 256);
ctx.fillStyle = "white";
ctx.font = "48px Arial";
ctx.fillText("Hello", 50, 150);

const texture = new THREE.CanvasTexture(canvas);

// canvas 变化时更新
texture.needsUpdate = true;
```

### 视频 纹理

```javascript
const video = document.createElement("video");
video.src = "video.mp4";
video.loop = true;
video.muted = true;
video.play();

const texture = new THREE.VideoTexture(video);
texture.colorSpace = THREE.SRGBColorSpace;

// 无需设置 needsUpdate - 自动更新
```

### 压缩纹理

```javascript
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath("path/to/basis/");
ktx2Loader.detectSupport(renderer);

ktx2Loader.load("texture.ktx2", (texture) => {
  material.map = texture;
});
```

## 立方纹理

用于环境贴图和天空盒。

### CubeTextureLoader

```javascript
const loader = new THREE.CubeTextureLoader();
const cubeTexture = loader.load([
  "px.jpg",
  "nx.jpg", // +X, -X
  "py.jpg",
  "ny.jpg", // +Y, -Y
  "pz.jpg",
  "nz.jpg", // +Z, -Z
]);

// 作为背景
scene.background = cubeTexture;

// 作为环境贴图
scene.environment = cubeTexture;
material.envMap = cubeTexture;
```

### Equirectangular 到 Cubemap

```javascript
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

const pmremGenerator = new THREE.PMREMGenerator(renderer);
pmremGenerator.compileEquirectangularShader();

new RGBELoader().load("environment.hdr", (texture) => {
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;
  scene.environment = envMap;
  scene.background = envMap;

  texture.dispose();
  pmremGenerator.dispose();
});
```

## HDR 纹理

### RGBELoader

```javascript
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

const loader = new RGBELoader();
loader.load("environment.hdr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
  scene.background = texture;
});
```

### EXRLoader

```javascript
import { EXRLoader } from "three/examples/jsm/loaders/EXRLoader.js";

const loader = new EXRLoader();
loader.load("environment.exr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
});
```

### 背景选项

```javascript
scene.background = texture;
scene.backgroundBlurriness = 0.5; // 0-1，背景模糊
scene.backgroundIntensity = 1.0; // 亮度
scene.backgroundRotation.y = Math.PI; // 背景旋转
```

## 渲染目标

渲染到纹理以实现特效。

```javascript
// 创建渲染目标
const renderTarget = new THREE.WebGLRenderTarget(512, 512, {
  minFilter: THREE.LinearFilter,
  magFilter: THREE.LinearFilter,
  format: THREE.RGBAFormat,
});

// 渲染场景到目标
renderer.setRenderTarget(renderTarget);
renderer.render(scene, camera);
renderer.setRenderTarget(null); // 回到屏幕

// 作为纹理使用
material.map = renderTarget.texture;
```

### 深度纹理

```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512);
renderTarget.depthTexture = new THREE.DepthTexture(
  512,
  512,
  THREE.UnsignedShortType,
);

// 访问深度
const depthTexture = renderTarget.depthTexture;
```

### 多采样渲染目标

```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512, {
  samples: 4, // MSAA
});
```

## 立方相机

动态环境贴图用于反射。

```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256, {
  generateMipmaps: true,
  minFilter: THREE.LinearMipmapLinearFilter,
});

const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);

// 应用于反射材质
reflectiveMaterial.envMap = cubeRenderTarget.texture;

// 动画循环中更新（昂贵！）
function animate() {
  // 隐藏反射对象，更新环境贴图，再显示
  reflectiveObject.visible = false;
  cubeCamera.position.copy(reflectiveObject.position);
  cubeCamera.update(renderer, scene);
  reflectiveObject.visible = true;
}
```

## UV 映射

### 访问 UV

```javascript
const uvs = geometry.attributes.uv;

// 读取 UV
const u = uvs.getX(vertexIndex);
const v = uvs.getY(vertexIndex);

// 修改 UV
uvs.setXY(vertexIndex, newU, newV);
uvs.needsUpdate = true;
```

### 第二 UV 通道（用于 AO 贴图）

```javascript
// AO贴图需要
geometry.setAttribute("uv2", geometry.attributes.uv);

// 或创建自定义第二 UV
const uv2 = new Float32Array(vertexCount * 2);
// ... 填充 uv2 数据
geometry.setAttribute("uv2", new THREE.BufferAttribute(uv2, 2));
```

### 着色器中的 UV 变换

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    map: { value: texture },
    uvOffset: { value: new THREE.Vector2(0, 0) },
    uvScale: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    uniform vec2 uvOffset;
    uniform vec2 uvScale;

    void main() {
      vUv = uv * uvScale + uvOffset;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    uniform sampler2D map;

    void main() {
      gl_FragColor = texture2D(map, vUv);
    }
  `,
});
```

## 纹理图集

一个纹理中包含多个图像。

```javascript
// 4 个精灵的图集（2x2 网格）
const atlas = loader.load("atlas.png");
atlas.wrapS = THREE.ClampToEdgeWrapping;
atlas.wrapT = THREE.ClampToEdgeWrapping;

// 通过 UV 偏移/缩放选择精灵
function selectSprite(row, col, gridSize = 2) {
  atlas.offset.set(col / gridSize, 1 - (row + 1) / gridSize);
  atlas.repeat.set(1 / gridSize, 1 / gridSize);
}

// 选择左上角精灵
selectSprite(0, 0);
```

## 材质纹理映射

### PBR 纹理集

```javascript
const material = new THREE.MeshStandardMaterial({
  // 基色（sRGB）
  map: colorTexture,

  // 表面细节（线性）
  normalMap: normalTexture,
  normalScale: new THREE.Vector2(1, 1),

  // 粗糙度（线性，灰度）
  roughnessMap: roughnessTexture,
  roughness: 1, // 乘数

  // 金属度（线性，灰度）
  metalnessMap: metalnessTexture,
  metalness: 1, // 乘数

  // 环境光遮蔽（线性，使用 uv2）
  aoMap: aoTexture,
  aoMapIntensity: 1,

  // 自发光（sRGB）
  emissiveMap: emissiveTexture,
  emissive: 0xffffff,
  emissiveIntensity: 1,

  // 顶点位移（线性）
  displacementMap: displacementTexture,
  displacementScale: 0.1,
  displacementBias: 0,

  // 透明度（线性）
  alphaMap: alphaTexture,
  transparent: true,
});

// 别忘了 UV2 用于 AO
geometry.setAttribute("uv2", geometry.attributes.uv);
```

### 法线贴图类型

```javascript
// OpenGL 风格法线（默认）
material.normalMapType = THREE.TangentSpaceNormalMap;

// 对象空间法线
material.normalMapType = THREE.ObjectSpaceNormalMap;
```

## 程序化纹理

### 噪声纹理

```javascript
function generateNoiseTexture(size = 256) {
  const data = new Uint8Array(size * size * 4);

  for (let i = 0; i < size * size; i++) {
    const value = Math.random() * 255;
    data[i * 4] = value;
    data[i * 4 + 1] = value;
    data[i * 4 + 2] = value;
    data[i * 4 + 3] = 255;
  }

  const texture = new THREE.DataTexture(data, size, size);
  texture.needsUpdate = true;
  return texture;
}
```

### 渐变纹理

```javascript
function generateGradientTexture(color1, color2, size = 256) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = 1;
  const ctx = canvas.getContext("2d");

  const gradient = ctx.createLinearGradient(0, 0, size, 0);
  gradient.addColorStop(0, color1);
  gradient.addColorStop(1, color2);

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, 1);

  return new THREE.CanvasTexture(canvas);
}
```

## 纹理内存管理

### 释放纹理

```javascript
// 单个纹理
texture.dispose();

// 材质纹理
function disposeMaterial(material) {
  const maps = [
    "map",
    "normalMap",
    "roughnessMap",
    "metalnessMap",
    "aoMap",
    "emissiveMap",
    "displacementMap",
    "alphaMap",
    "envMap",
    "lightMap",
    "bumpMap",
    "specularMap",
  ];

  maps.forEach((mapName) => {
    if (material[mapName]) {
      material[mapName].dispose();
    }
  });

  material.dispose();
}
```

### 纹理池

```javascript
class TexturePool {
  constructor() {
    this.textures = new Map();
    this.loader = new THREE.TextureLoader();
  }

  async get(url) {
    if (this.textures.has(url)) {
      return this.textures.get(url);
    }

    const texture = await new Promise((resolve, reject) => {
      this.loader.load(url, resolve, undefined, reject);
    });

    this.textures.set(url, texture);
    return texture;
  }

  dispose(url) {
    const texture = this.textures.get(url);
    if (texture) {
      texture.dispose();
      this.textures.delete(url);
    }
  }

  disposeAll() {
    this.textures.forEach((t) => t.dispose());
    this.textures.clear();
  }
}
```

## 性能技巧

1. **使用幂等 2 尺寸**：256、512、1024、2048
2. **压缩纹理**：KTX2/Basis 用于网络传输
3. **使用纹理图集**：减少纹理切换
4. **启用 Mipmaps**：用于远距离对象
5. **限制纹理大小**：2048 通常足够用于网络
6. **重用纹理**：相同纹理 = 更好的批处理

```javascript
// 检查纹理内存
console.log(renderer.info.memory.textures);

// 针对移动设备优化
const maxSize = renderer.capabilities.maxTextureSize;
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
const textureSize = isMobile ? 1024 : 2048;
```

## 参考资料见

- `threejs-materials` - 将纹理应用于材质
- `threejs-loaders` - 加载纹理文件
- `threejs-shaders` - 自定义纹理采样
