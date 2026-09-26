# A-Frame WebXR 技能

## 何时使用此技能
- 用最少的 JavaScript 构建 VR/AR 体验
- 创建跨平台 WebXR 应用（桌面、移动端、头显）
- 使用 HTML 原语快速原型化 3D 场景
- 实现 VR 控制器交互
- 以声明式方式向网页添加 3D 内容
- 构建 360° 图片/视频体验
- 开发带命中标测的 AR 体验

## 核心概念

### 1. 实体-组件-系统（ECS）

A-Frame 采用实体-组件-系统架构，其中：
- **实体**是容器（类似于 HTML 中的 `<div>`）
- **组件**为实体添加功能/外观
- **系统**提供全局功能

```html
<!-- 带组件的实体 -->
<a-entity
  geometry="primitive: box; width: 2"
  material="color: red; metalness: 0.5"
  position="0 1.5 -3"
  rotation="0 45 0">
</a-entity>
```

**原语**是常见实体 + 组件组合的快捷方式：

```html
<!-- 原语（简写形式） -->
<a-box color="red" position="0 1.5 -3" rotation="0 45 0" width="2"></a-box>

<!-- 等价的实体-组件形式 -->
<a-entity
  geometry="primitive: box; width: 2"
  material="color: red"
  position="0 1.5 -3"
  rotation="0 45 0">
</a-entity>
```

### 2. 场景设置

每个 A-Frame 应用都从 `<a-scene>` 开始：

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
  </head>
  <body>
    <a-scene>
      <!-- 实体放在这里 -->
      <a-box position="-1 0.5 -3" color="#4CC3D9"></a-box>
      <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E"></a-sphere>
      <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D"></a-cylinder>
      <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#7BC8A4"></a-plane>
      <a-sky color="#ECECEC"></a-sky>
    </a-scene>
  </body>
</html>
```

场景会自动注入：
- 默认摄像机（位置：`0 1.6 0`）
- 查看控制（鼠标拖拽）
- WASD 控制（键盘移动）

### 3. 摄像机系统

**默认摄像机**（未指定时自动注入）：

```html
<a-entity camera="active: true" look-controls wasd-controls position="0 1.6 0"></a-entity>
```

**自定义摄像机**：

```html
<a-camera position="0 2 5" look-controls wasd-controls="acceleration: 50"></a-camera>
```

**摄像机 rigs**（用于独立的移动和旋转）：

```html
<a-entity id="rig" position="0 0 0">
  <!-- 用于头部追踪的摄像机 -->
  <a-camera look-controls></a-camera>

  <!-- 移动应用到 rig 上，而非摄像机 -->
</a-entity>
```

**带控制器的 VR 摄像机 rig**：

```html
<a-entity id="rig" position="0 0 0">
  <!-- 位于眼高的摄像机 -->
  <a-camera position="0 1.6 0"></a-camera>

  <!-- 左手控制器 -->
  <a-entity
    hand-controls="hand: left"
    laser-controls="hand: left">
  </a-entity>

  <!-- 右手控制器 -->
  <a-entity
    hand-controls="hand: right"
    laser-controls="hand: right">
  </a-entity>
</a-entity>
```

### 4. 光照

**环境光**（全局照明）：

```html
<a-entity light="type: ambient; color: #BBB; intensity: 0.5"></a-entity>
```

**平行光**（类似阳光）：

```html
<a-entity light="type: directional; color: #FFF; intensity: 0.8" position="1 2 1"></a-entity>
```

**点光源**（向所有方向辐射）：

```html
<a-entity light="type: point; color: #F00; intensity: 2; distance: 50" position="0 3 0"></a-entity>
```

**聚光灯**（锥形光束）：

```html
<a-entity light="type: spot; angle: 45; intensity: 1.5" position="0 5 0" rotation="-90 0 0"></a-entity>
```

### 5. 材质和纹理

**标准材质**：

```html
<a-sphere
  material="color: #FF0000; metalness: 0.5; roughness: 0.3"
  position="0 1 -3">
</a-sphere>
```

**纹理材质**：

```html
<a-assets>
  <img id="woodTexture" src="wood.jpg">
</a-assets>

<a-box material="src: #woodTexture" position="0 1 -3"></a-box>
```

**扁平着色**（无光照）：

```html
<a-plane material="shader: flat; color: #4CC3D9"></a-plane>
```

### 6. 动画

**属性动画**：

```html
<a-box
  position="0 1 -3"
  animation="property: rotation; to: 0 360 0; loop: true; dur: 5000">
</a-box>
```

**多个动画**（使用 `animation__*` 命名）：

```html
<a-sphere
  position="0 1 -3"
  animation__position="property: position; to: 0 3 -3; dir: alternate; loop: true; dur: 2000"
  animation__rotation="property: rotation; to: 360 360 0; loop: true; dur: 4000"
  animation__scale="property: scale; to: 1.5 1.5 1.5; dir: alternate; loop: true; dur: 1000">
</a-sphere>
```

**基于事件的动画**：

```html
<a-box
  color="blue"
  animation__mouseenter="property: scale; to: 1.2 1.2 1.2; startEvents: mouseenter"
  animation__mouseleave="property: scale; to: 1 1 1; startEvents: mouseleave"
  animation__click="property: rotation; from: 0 0 0; to: 0 360 0; startEvents: click">
</a-box>
```

### 7. 资源管理

预加载资源以获得更好的性能：

```html
<a-scene>
  <a-assets>
    <!-- 图片 -->
    <img id="texture1" src="texture.jpg">
    <img id="skyTexture" src="sky.jpg">

    <!-- 视频 -->
    <video id="video360" src="360video.mp4" autoplay loop></video>

    <!-- 音频 -->
    <audio id="bgMusic" src="music.mp3" preload="auto"></audio>

    <!-- 模型 -->
    <a-asset-item id="tree" src="tree.gltf"></a-asset-item>

    <!-- Mixin（可复用的组件集合） -->
    <a-mixin id="redMaterial" material="color: red; metalness: 0.7"></a-mixin>
  </a-assets>

  <!-- 使用资源 -->
  <a-entity gltf-model="#tree" position="2 0 -5"></a-entity>
  <a-sphere mixin="redMaterial" position="0 1 -3"></a-sphere>
  <a-sky src="#skyTexture"></a-sky>
</a-scene>
```

### 8. 自定义组件

注册自定义组件以封装逻辑：

```javascript
AFRAME.registerComponent('rotate-on-click', {
  // 组件模式（配置）
  schema: {
    speed: {type: 'number', default: 1}
  },

  // 生命周期：组件挂载时调用一次
  init: function() {
    this.el.addEventListener('click', () => {
      this.rotating = !this.rotating;
    });
  },

  // 生命周期：每帧调用
  tick: function(time, timeDelta) {
    if (this.rotating) {
      var rotation = this.el.getAttribute('rotation');
      rotation.y += this.data.speed;
      this.el.setAttribute('rotation', rotation);
    }
  }
});
```

```html
<a-box rotate-on-click="speed: 2" position="0 1 -3"></a-box>
```

## 常见模式

### 模式 1：VR 控制器交互

**问题**：在 VR 中实现物体的抓取和操作

**解决方案**：使用 hand-controls 和自定义抓取组件

```html
<a-scene>
  <!-- VR 摄像机 rig -->
  <a-entity id="rig">
    <a-camera position="0 1.6 0"></a-camera>

    <a-entity
      id="leftHand"
      hand-controls="hand: left"
      laser-controls="hand: left">
    </a-entity>

    <a-entity
      id="rightHand"
      hand-controls="hand: right"
      laser-controls="hand: right">
    </a-entity>
  </a-entity>

  <!-- 可抓取的物体 -->
  <a-box class="grabbable" position="-1 1.5 -3" color="#4CC3D9"></a-box>
  <a-sphere class="grabbable" position="1 1.5 -3" color="#EF2D5E"></a-sphere>
</a-scene>

<script>
AFRAME.registerComponent('grabbable', {
  init: function() {
    var el = this.el;

    el.addEventListener('triggerdown', function(evt) {
      console.log('Grabbed by', evt.detail.hand);
      el.setAttribute('color', 'green');
    });

    el.addEventListener('triggerup', function(evt) {
      el.setAttribute('color', 'blue');
    });

    el.addEventListener('gripdown', function(evt) {
      // 将物体附加到控制器
      var controllerEl = evt.detail.controller;
      controllerEl.object3D.attach(el.object3D);
    });

    el.addEventListener('gripup', function(evt) {
      // 从控制器分离
      var sceneEl = el.sceneEl.object3D;
      sceneEl.attach(el.object3D);
    });
  }
});

// 应用可抓取组件
document.querySelectorAll('.grabbable').forEach(el => {
  el.setAttribute('grabbable', '');
});
</script>
```

### 模式 2：360° 图片画廊

**问题**：创建一个可交互的 360° 照片查看器

**解决方案**：使用 sky 原语和可点击的缩略图

```html
<a-scene>
  <a-assets>
    <img id="city" src="city.jpg">
    <img id="forest" src="forest.jpg">
    <img id="beach" src="beach.jpg">
    <img id="city-thumb" src="city-thumb.jpg">
    <img id="forest-thumb" src="forest-thumb.jpg">
    <img id="beach-thumb" src="beach-thumb.jpg">
    <audio id="click-sound" src="click.mp3"></audio>
  </a-assets>

  <!-- 360 度图片球体 -->
  <a-sky id="image-360" src="#city" rotation="0 -130 0"></a-sky>

  <!-- 缩略图菜单 -->
  <a-entity id="menu" position="0 1.6 -2">
    <a-entity class="link"
      geometry="primitive: plane; width: 0.7; height: 0.7"
      material="shader: flat; src: #city-thumb"
      position="-1 0 0"
      sound="on: click; src: #click-sound"
      event-set__mouseenter="scale: 1.2 1.2 1"
      event-set__mouseleave="scale: 1 1 1"
      event-set__click="_target: #image-360; material.src: #city">
    </a-entity>

    <a-entity class="link"
      geometry="primitive: plane; width: 0.7; height: 0.7"
      material="shader: flat; src: #forest-thumb"
      position="0 0 0"
      sound="on: click; src: #click-sound"
      event-set__mouseenter="scale: 1.2 1.2 1"
      event-set__mouseleave="scale: 1 1 1"
      event-set__click="_target: #image-360; material.src: #forest">
    </a-entity>

    <a-entity class="link"
      geometry="primitive: plane; width: 0.7; height: 0.7"
      material="shader: flat; src: #beach-thumb"
      position="1 0 0"
      sound="on: click; src: #click-sound"
      event-set__mouseenter="scale: 1.2 1.2 1"
      event-set__mouseleave="scale: 1 1 1"
      event-set__click="_target: #image-360; material.src: #beach">
    </a-entity>
  </a-entity>

  <!-- 带光标用于视线交互的摄像机 -->
  <a-camera>
    <a-cursor raycaster="objects: .link"></a-cursor>
  </a-camera>
</a-scene>
```

### 模式 3：AR 命中标测（在现实世界中放置物体）

**问题**：将虚拟物体放置在检测到的现实世界表面上

**解决方案**：使用 ar-hit-test 组件

```html
<a-scene
  webxr="optionalFeatures: hit-test, dom-overlay; overlayElement: #overlay"
  ar-hit-test="target: #furniture; type: footprint">

  <a-assets>
    <a-asset-item id="chair" src="chair.gltf"></a-asset-item>
  </a-assets>

  <!-- 要放置的物体 -->
  <a-entity id="furniture" gltf-model="#chair" scale="0.5 0.5 0.5"></a-entity>

  <!-- AR 操作说明叠加层 -->
  <div id="overlay" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
                           background: rgba(0,0,0,0.7); color: white; padding: 15px;
                           border-radius: 8px; font-family: sans-serif;">
    <p id="message">Tap to enter AR mode</p>
  </div>
</a-scene>

<script>
const sceneEl = document.querySelector('a-scene');
const message = document.getElementById('message');

sceneEl.addEventListener('enter-vr', function() {
  if (this.is('ar-mode')) {
    message.textContent = '';

    this.addEventListener('ar-hit-test-start', function() {
      message.innerHTML = 'Scanning environment, finding surface.';
    }, { once: true });

    this.addEventListener('ar-hit-test-achieved', function() {
      message.innerHTML = 'Tap on the screen to place the object.';
    }, { once: true });

    this.addEventListener('ar-hit-test-select', function() {
      message.textContent = 'Object placed!';
      setTimeout(() => message.textContent = '', 2000);
    }, { once: true });
  }
});

sceneEl.addEventListener('exit-vr', function() {
  message.textContent = 'Tap to enter AR mode';
});
</script>
```

### 模式 4：鼠标/视线交互

**问题**：启用桌面鼠标或 VR 视线的点击交互

**解决方案**：使用 cursor 组件和射线检测器

```html
<a-scene>
  <!-- 可交互物体 -->
  <a-box
    class="interactive"
    position="-1 1.5 -3"
    color="#4CC3D9"
    event-set__mouseenter="color: yellow"
    event-set__mouseleave="color: #4CC3D9"
    event-set__click="scale: 1.5 1.5 1.5">
  </a-box>

  <a-sphere
    class="interactive"
    position="1 1.5 -3"
    color="#EF2D5E"
    event-set__click="color: orange; scale: 2 2 2">
  </a-sphere>

  <a-plane position="0 0 -4" rotation="-90 0 0" width="10" height="10" color="#7BC8A4"></a-plane>

  <!-- 带光标的摄像机 -->
  <a-camera position="0 1.6 0">
    <!-- 射线检测器目标为 .interactive 类 -->
    <a-cursor
      raycaster="objects: .interactive"
      fuse="true"
      fuse-timeout="1500">
    </a-cursor>
  </a-camera>
</a-scene>

<script>
// 使用 JavaScript 进行高级点击处理
document.querySelectorAll('.interactive').forEach(el => {
  el.addEventListener('click', function(evt) {
    console.log('Clicked:', this.id || this.tagName);
    console.log('Intersection point:', evt.detail.intersection.point);
  });
});
</script>
```

### 模式 5：动态场景生成

**问题**：以编程方式创建和操作实体

**解决方案**：使用 JavaScript DOM 操作

```html
<a-scene>
  <a-camera position="0 1.6 5"></a-camera>
  <a-entity light="type: ambient; color: #888"></a-entity>
  <a-entity light="type: directional; color: #FFF" position="1 2 1"></a-entity>
</a-scene>

<script>
const scene = document.querySelector('a-scene');

// 创建球体
function createSphere(x, y, z, color) {
  const entity = document.createElement('a-entity');

  entity.setAttribute('geometry', {
    primitive: 'sphere',
    radius: 0.5
  });

  entity.setAttribute('material', {
    color: color,
    metalness: 0.5,
    roughness: 0.3
  });

  entity.setAttribute('position', {x, y, z});

  // 添加动画
  entity.setAttribute('animation', {
    property: 'position',
    to: `${x} ${y + 1} ${z}`,
    dir: 'alternate',
    loop: true,
    dur: 2000
  });

  scene.appendChild(entity);
  return entity;
}

// 生成球体网格
for (let x = -3; x <= 3; x += 1.5) {
  for (let z = -5; z <= -2; z += 1.5) {
    const color = `#${Math.floor(Math.random()*16777215).toString(16)}`;
    createSphere(x, 1, z, color);
  }
}

// 监听组件变化
scene.addEventListener('componentchanged', function(evt) {
  console.log('Component changed:', evt.detail.name);
});

// 直接访问 Three.js 对象
setTimeout(() => {
  const entities = document.querySelectorAll('a-entity[geometry]');
  entities.forEach(el => {
    el.object3D.visible = true; // 直接操作 Three.js
  });
}, 1000);
</script>
```

### 模式 6：环境和天空盒

**问题**：快速创建沉浸式环境

**解决方案**：使用社区组件和 360 度图片

```html
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@fern-solutions/aframe-sky-background/dist/sky-background.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-extras@7.5.0/dist/aframe-extras.min.js"></script>
  </head>
  <body>
    <a-scene>
      <!-- 渐变天空 -->
      <a-sky-background
        top-color="#4A90E2"
        bottom-color="#87CEEB">
      </a-sky-background>

      <!-- 或使用纹理天空 -->
      <!-- <a-sky src="sky.jpg" rotation="0 -130 0"></a-sky> -->

      <!-- 海洋 -->
      <a-entity
        ocean="density: 20; width: 50; depth: 50; speed: 4"
        material="color: #9CE3F9; opacity: 0.75; metalness: 0; roughness: 1"
        rotation="-90 0 0">
      </a-entity>

      <!-- 用于营造氛围的粒子系统 -->
      <a-entity
        particle-system="preset: snow; particleCount: 2000; color: #FFF">
      </a-entity>

      <a-entity light="type: ambient; color: #888"></a-entity>
      <a-entity light="type: directional; color: #FFF; intensity: 0.7" position="1 2 1"></a-entity>
    </a-scene>
  </body>
</html>
```

### 模式 7：GLTF 模型加载

**问题**：加载和显示 3D 模型

**解决方案**：使用 gltf-model 组件配合资源管理

```html
<a-scene>
  <a-assets>
    <a-asset-item id="robot" src="robot.gltf"></a-asset-item>
    <a-asset-item id="building" src="building.glb"></a-asset-item>
  </a-assets>

  <!-- 加载模型 -->
  <a-entity
    gltf-model="#robot"
    position="0 0 -3"
    scale="0.5 0.5 0.5"
    animation="property: rotation; to: 0 360 0; loop: true; dur: 10000">
  </a-entity>

  <!-- 带额外资源（动画）加载 -->
  <a-entity
    gltf-model="#building"
    position="5 0 -10"
    animation-mixer="clip: *; loop: repeat">
  </a-entity>

  <a-camera position="0 1.6 5"></a-camera>
  <a-entity light="type: ambient; intensity: 0.5"></a-entity>
  <a-entity light="type: directional; intensity: 0.8" position="2 4 2"></a-entity>
</a-scene>

<script>
// 处理模型加载事件
document.querySelector('[gltf-model="#robot"]').addEventListener('model-loaded', (evt) => {
  console.log('Model loaded:', evt.detail.model);

  // 访问 Three.js 对象
  const model = evt.detail.model;
  model.traverse(node => {
    if (node.isMesh) {
      console.log('Mesh found:', node.name);
    }
  });
});

document.querySelector('[gltf-model="#robot"]').addEventListener('model-error', (evt) => {
  console.error('Model loading error:', evt.detail);
});
</script>
```

## 集成模式

### 与 Three.js 集成

访问底层的 Three.js 对象：

```javascript
// 获取 Three.js 场景
const scene = document.querySelector('a-scene').object3D;

// 获取实体的 Three.js 对象
const box = document.querySelector('a-box');
const threeObject = box.object3D;

// 直接操作 Three.js
threeObject.position.set(1, 2, 3);
threeObject.rotation.y = Math.PI / 4;

// 添加自定义 Three.js 对象
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

### 与 GSAP（动画）集成

使用 GSAP 对 A-Frame 实体进行动画：

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script>
const box = document.querySelector('a-box');

// 动画化位置
gsap.to(box.object3D.position, {
  x: 3,
  y: 2,
  z: -5,
  duration: 2,
  ease: 'power2.inOut'
});

// 动画化旋转
gsap.to(box.object3D.rotation, {
  y: Math.PI * 2,
  duration: 3,
  repeat: -1,
  ease: 'none'
});

// 动画化属性
gsap.to(box.components.material.material, {
  opacity: 0.5,
  duration: 1
});
</script>
```

### 与 React 集成

在 React 组件中集成 A-Frame：

```jsx
import React, { useEffect, useRef } from 'react';
import 'aframe';

function VRScene() {
  const sceneRef = useRef(null);

  useEffect(() => {
    const scene = sceneRef.current;

    // 动态创建实体
    const entity = document.createElement('a-sphere');
    entity.setAttribute('position', '0 1.5 -3');
    entity.setAttribute('color', '#EF2D5E');
    scene.appendChild(entity);

    // 监听事件
    scene.addEventListener('enter-vr', () => {
      console.log('Entered VR mode');
    });
  }, []);

  return (
    <a-scene ref={sceneRef}>
      <a-box position="-1 0.5 -3" rotation="0 45 0" color="#4CC3D9" />
      <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E" />
      <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D" />
      <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#7BC8A4" />
      <a-sky color="#ECECEC" />
    </a-scene>
  );
}

export default VRScene;
```

## 性能最佳实践

### 1. 使用资源管理

预加载资源以避免阻塞：

```html
<a-assets>
  <img id="texture1" src="large-texture.jpg">
  <video id="video360" src="360video.mp4" preload="auto"></video>
  <a-asset-item id="model" src="complex-model.gltf"></a-asset-item>
</a-assets>
```

### 2. 实体池化

重用实体而非创建/销毁：

```javascript
AFRAME.registerComponent('bullet-pool', {
  init: function() {
    this.pool = [];
    this.used = [];

    // 预创建子弹
    for (let i = 0; i < 20; i++) {
      const bullet = document.createElement('a-sphere');
      bullet.setAttribute('radius', 0.1);
      bullet.setAttribute('visible', false);
      this.el.sceneEl.appendChild(bullet);
      this.pool.push(bullet);
    }
  },

  getBullet: function() {
    if (this.pool.length > 0) {
      const bullet = this.pool.pop();
      bullet.setAttribute('visible', true);
      this.used.push(bullet);
      return bullet;
    }
  },

  returnBullet: function(bullet) {
    bullet.setAttribute('visible', false);
    const index = this.used.indexOf(bullet);
    if (index > -1) {
      this.used.splice(index, 1);
      this.pool.push(bullet);
    }
  }
});
```

### 3. 优化几何体

使用低多边形模型和 LOD：

```html
<!-- 远处物体使用低多边形 -->
<a-sphere radius="1" segments-width="8" segments-height="6"></a-sphere>

<!-- 近处物体使用高多边形 -->
<a-sphere radius="1" segments-width="32" segments-height="32"></a-sphere>
```

### 4. 限制绘制调用

对重复物体使用实例化：

```javascript
AFRAME.registerComponent('instanced-trees', {
  init: function() {
    // 对重复几何体使用 Three.js InstancedMesh
    const scene = this.el.sceneEl.object3D;
    const geometry = new THREE.ConeGeometry(0.5, 2, 8);
    const material = new THREE.MeshStandardMaterial({ color: 0x228B22 });
    const mesh = new THREE.InstancedMesh(geometry, material, 100);

    // 定位实例
    for (let i = 0; i < 100; i++) {
      const matrix = new THREE.Matrix4();
      matrix.setPosition(
        Math.random() * 20 - 10,
        0,
        Math.random() * 20 - 10
      );
      mesh.setMatrixAt(i, matrix);
    }

    scene.add(mesh);
  }
});
```

### 5. 节流 tick() 函数

如果非必要，不要每帧都更新：

```javascript
AFRAME.registerComponent('throttled-update', {
  init: function() {
    this.lastUpdate = 0;
    this.updateInterval = 100; // 毫秒
  },

  tick: function(time, timeDelta) {
    if (time - this.lastUpdate >= this.updateInterval) {
      // 在此处执行昂贵操作
      this.lastUpdate = time;
    }
  }
});
```

### 6. 使用 Stats 组件进行监控

```html
<a-scene stats>
  <!-- 显示 FPS 和性能指标 -->
</a-scene>
```

## 常见陷阱与解决方案

### 陷阱 1：实体未显示

**问题**：实体已添加但不可见

**原因**：
- 实体位于摄像机后方
- 缩放为 0 或非常小
- 材质不透明度为 0
- 实体在摄像机视锥体之外

**解决方案**：

```javascript
// 等待场景加载完成
const scene = document.querySelector('a-scene');
scene.addEventListener('loaded', () => {
  const entity = document.createElement('a-box');
  entity.setAttribute('position', '0 1.5 -3'); // 在摄像机前方
  entity.setAttribute('color', 'red');
  scene.appendChild(entity);
});

// 调试：检查实体位置
console.log(entity.getAttribute('position'));

// 调试：检查实体是否在场景中
console.log(entity.parentNode); // 应该是 <a-scene>
```

### 陷阱 2：事件未触发

**问题**：点击/mouseenter 事件未触发

**原因**：缺少射线检测器或光标

**解决方案**：

```html
<!-- 在摄像机上添加光标 -->
<a-camera>
  <a-cursor raycaster="objects: .interactive"></a-cursor>
</a-camera>

<!-- 为可交互物体添加类 -->
<a-box class="interactive" position="0 1 -3"></a-box>

<!-- 或直接使用射线检测器 -->
<a-entity raycaster="objects: [geometry]" cursor></a-entity>
```

### 陷阱 3：性能下降

**问题**：实体数量多时 FPS 低

**原因**：
- 过多绘制调用
- 复杂几何体
- 未优化的纹理
- 过多 tick() 更新

**解决方案**：

```javascript
// 1. 使用对象池（参见性能部分）
// 2. 简化几何体
// 3. 优化纹理（减小尺寸，使用压缩）
// 4. 节流更新

AFRAME.registerComponent('optimize-far-entities', {
  tick: function() {
    const camera = this.el.sceneEl.camera;
    const entities = document.querySelectorAll('[geometry]');

    entities.forEach(el => {
      const distance = el.object3D.position.distanceTo(camera.position);

      // 隐藏远处的实体
      el.object3D.visible = distance < 50;
    });
  }
});
```

### 陷阱 4：Z 轴冲突（表面重叠）

**问题**：表面重叠时出现闪烁

**原因**：两个表面处于相同位置

**解决方案**：

```html
<!-- 将表面稍微偏移 -->
<a-plane position="0 0.01 0" rotation="-90 0 0"></a-plane>
<a-plane position="0 0.02 0" rotation="-90 0 0"></a-plane>

<!-- 或使用 renderOrder -->
<a-entity
  geometry="primitive: plane"
  material="src: #texture1; transparent: true"
  class="has-render-order">
</a-entity>

<script>
document.querySelector('.has-render-order').object3D.renderOrder = 1;
</script>
```

### 陷阱 5：移动端 VR 性能

**问题**：移动端 VR 性能低

**解决方案**：

```html
<!-- 减小渲染器最大画布尺寸 -->
<a-scene renderer="maxCanvasWidth: 1920; maxCanvasHeight: 1920">

<!-- 使用低多边形模型 -->
<a-sphere radius="1" segments-width="8" segments-height="6"></a-sphere>

<!-- 限制光源数量（移动端代价高） -->
<a-entity light="type: ambient; intensity: 0.6"></a-entity>
<a-entity light="type: directional; intensity: 0.4" position="1 2 1"></a-entity>

<!-- 必要时禁用抗锯齿 -->
<a-scene renderer="antialias: false">
</a-scene>
```

### 陷阱 6：资源加载问题

**问题**：资源未加载或 CORS 错误

**解决方案**：

```html
<!-- 使用 crossorigin 属性 -->
<a-assets>
  <img id="texture" src="https://example.com/texture.jpg" crossorigin="anonymous">
</a-assets>

<!-- 等待资源加载完成 -->
<script>
const assets = document.querySelector('a-assets');
assets.addEventListener('loaded', () => {
  console.log('All assets loaded');
  // 现在可以安全使用资源
});

assets.addEventListener('timeout', () => {
  console.error('Asset loading timeout');
});
</script>

<!-- 处理加载错误 -->
<script>
const img = document.querySelector('img#texture');
img.addEventListener('error', () => {
  console.error('Failed to load texture');
  // 使用备用方案
  img.src = 'fallback-texture.jpg';
});
</script>
```

## 资源

- [A-Frame 文档](https://aframe.io/docs/)
- [A-Frame GitHub](https://github.com/aframevr/aframe)
- [A-Frame School](https://aframe.io/school/)
- [A-Frame 社区组件](https://github.com/c-frame)
- [WebXR 设备 API](https://www.w3.org/TR/webxr/)
- [Three.js 文档](https://threejs.org/docs/)（A-Frame 基于 Three.js 构建）

## 相关技能

- **threejs-webgl**：用于在 A-Frame 声明式 API 之外进行高级 Three.js 控制
- **babylonjs-engine**：具有不同架构的替代 3D 引擎
- **gsap-scrolltrigger**：用于使用 GSAP 为 A-Frame 实体添加动画
- **react-three-fiber**：React 方式操作 Three.js（与 A-Frame 的 HTML 方式对比）
