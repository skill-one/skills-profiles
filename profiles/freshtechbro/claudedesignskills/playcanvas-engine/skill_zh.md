# PlayCanvas 引擎技能

轻量级 WebGL/WebGPU 游戏引擎，具有实体-组件架构、视觉编辑器集成和以性能为中心的设计。

## 何时使用此技能

当您看到以下内容时，请触发此技能：
- "PlayCanvas 引擎"
- "WebGL 游戏引擎"
- "实体-组件系统"
- "PlayCanvas 应用"
- "3D 浏览器游戏"
- "在线 3D 编辑器"
- "轻量级 3D 引擎"
- 需要编辑器优先的工作流程

与以下进行比较：
- **Three.js**：低级别，更灵活但需要更多设置
- **Babylon.js**：功能丰富但更重，有编辑器但不够成熟
- **A-Frame**：专注于 VR，声明式 HTML 方法
- 使用 PlayCanvas 进行：游戏项目、编辑器优先的工作流程、性能关键的应用

---

## 核心概念

### 1. 应用

PlayCanvas 应用管理渲染循环。

```javascript
import * as pc from 'playcanvas';

// 创建画布
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);

// 创建应用
const app = new pc.Application(canvas, {
  keyboard: new pc.Keyboard(window),
  mouse: new pc.Mouse(canvas),
  touch: new pc.TouchDevice(canvas),
  gamepads: new pc.GamePads()
});

// 配置画布
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);

// 处理调整大小
window.addEventListener('resize', () => app.resizeCanvas());

// 启动应用
app.start();
```

---

### 2. 实体-组件系统

PlayCanvas 使用 ECS 架构：实体包含组件。

```javascript
// 创建实体
const entity = new pc.Entity('myEntity');

// 添加到场景层次结构
app.root.addChild(entity);

// 添加组件
entity.addComponent('model', {
  type: 'box'
});

entity.addComponent('script');

// 变换
entity.setPosition(0, 1, 0);
entity.setEulerAngles(0, 45, 0);
entity.setLocalScale(2, 2, 2);

// 父子层次结构
const parent = new pc.Entity('parent');
const child = new pc.Entity('child');
parent.addChild(child);
```

---

### 3. 更新循环

应用在更新循环期间触发事件。

```javascript
app.on('update', (dt) => {
  // dt 是秒数的时间差
  entity.rotate(0, 10 * dt, 0);
});

app.on('prerender', () => {
  // 渲染之前
});

app.on('postrender', () => {
  // 渲染之后
});
```

---

### 4. 组件

核心组件扩展实体的功能：

**模型组件**：
```javascript
entity.addComponent('model', {
  type: 'box',           // 'box', 'sphere', 'cylinder', 'cone', 'capsule', 'asset'
  material: material,
  castShadows: true,
  receiveShadows: true
});
```

**相机组件**：
```javascript
entity.addComponent('camera', {
  clearColor: new pc.Color(0.1, 0.2, 0.3),
  fov: 45,
  nearClip: 0.1,
  farClip: 1000,
  projection: pc.PROJECTION_PERSPECTIVE  // 或 PROJECTION_ORTHOGRAPHIC
});
```

**光源组件**：
```javascript
entity.addComponent('light', {
  type: pc.LIGHTTYPE_DIRECTIONAL,  // DIRECTIONAL, POINT, SPOT
  color: new pc.Color(1, 1, 1),
  intensity: 1,
  castShadows: true,
  shadowDistance: 50
});
```

**刚体组件**（需要物理）：
```javascript
entity.addComponent('rigidbody', {
  type: pc.BODYTYPE_DYNAMIC,  // STATIC, DYNAMIC, KINEMATIC
  mass: 1,
  friction: 0.5,
  restitution: 0.3
});

entity.addComponent('collision', {
  type: 'box',
  halfExtents: new pc.Vec3(0.5, 0.5, 0.5)
});
```

---

## 常见模式

### 模式 1：基本场景设置

创建具有相机、光源和模型的完整场景。

```javascript
import * as pc from 'playcanvas';

// 初始化应用
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);

const app = new pc.Application(canvas);
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);
window.addEventListener('resize', () => app.resizeCanvas());

// 创建相机
const camera = new pc.Entity('camera');
camera.addComponent('camera', {
  clearColor: new pc.Color(0.2, 0.3, 0.4)
});
camera.setPosition(0, 2, 5);
camera.lookAt(0, 0, 0);
app.root.addChild(camera);

// 创建方向光
const light = new pc.Entity('light');
light.addComponent('light', {
  type: pc.LIGHTTYPE_DIRECTIONAL,
  castShadows: true
});
light.setEulerAngles(45, 30, 0);
app.root.addChild(light);

// 创建地面
const ground = new pc.Entity('ground');
ground.addComponent('model', {
  type: 'plane'
});
ground.setLocalScale(10, 1, 10);
app.root.addChild(ground);

// 创建立方体
const cube = new pc.Entity('cube');
cube.addComponent('model', {
  type: 'box',
  castShadows: true
});
cube.setPosition(0, 1, 0);
app.root.addChild(cube);

// 动画化立方体
app.on('update', (dt) => {
  cube.rotate(10 * dt, 20 * dt, 30 * dt);
});

app.start();
```

---

### 模式 2：加载 GLTF 模型

使用资源管理加载外部 3D 模型。

```javascript
// 创建模型资源
const modelAsset = new pc.Asset('model', 'container', {
  url: '/models/character.glb'
});

// 添加到资源注册表
app.assets.add(modelAsset);

// 加载资源
modelAsset.ready((asset) => {
  // 从加载的模型创建实体
  const entity = asset.resource.instantiateRenderEntity();

  app.root.addChild(entity);

  // 缩放和定位
  entity.setLocalScale(2, 2, 2);
  entity.setPosition(0, 0, 0);
});

app.assets.load(modelAsset);
```

**带错误处理**：
```javascript
modelAsset.ready((asset) => {
  console.log('模型加载:', asset.name);
  const entity = asset.resource.instantiateRenderEntity();
  app.root.addChild(entity);
});

modelAsset.on('error', (err) => {
  console.error('加载模型失败:', err);
});

app.assets.load(modelAsset);
```

---

### 模式 3：材质和纹理

使用 PBR 工作流程创建自定义材质。

```javascript
// 创建材质
const material = new pc.StandardMaterial();
material.diffuse = new pc.Color(1, 0, 0);  // 红色
material.metalness = 0.5;
material.gloss = 0.8;
material.update();

// 应用于实体
entity.model.material = material;

// 带纹理
const textureAsset = new pc.Asset('diffuse', 'texture', {
  url: '/textures/brick_diffuse.jpg'
});

app.assets.add(textureAsset);
app.assets.load(textureAsset);

textureAsset.ready((asset) => {
  material.diffuseMap = asset.resource;
  material.update();
});

// PBR 材质带所有贴图
const pbrMaterial = new pc.StandardMaterial();

// 加载所有贴图
const textures = {
  diffuse: '/textures/albedo.jpg',
  normal: '/textures/normal.jpg',
  metalness: '/textures/metalness.jpg',
  gloss: '/textures/roughness.jpg',
  ao: '/textures/ao.jpg'
};

Object.keys(textures).forEach(key => {
  const asset = new pc.Asset(key, 'texture', { url: textures[key] });
  app.assets.add(asset);

  asset.ready((loadedAsset) => {
    switch(key) {
      case 'diffuse':
        pbrMaterial.diffuseMap = loadedAsset.resource;
        break;
      case 'normal':
        pbrMaterial.normalMap = loadedAsset.resource;
        break;
      case 'metalness':
        pbrMaterial.metalnessMap = loadedAsset.resource;
        break;
      case 'gloss':
        pbrMaterial.glossMap = loadedAsset.resource;
        break;
      case 'ao':
        pbrMaterial.aoMap = loadedAsset.resource;
        break;
    }
    pbrMaterial.update();
  });

  app.assets.load(asset);
});
```

---

### 模式 4：物理集成

使用 Ammo.js 进行物理模拟。

```javascript
import * as pc from 'playcanvas';

// 使用 Ammo.js 初始化
const app = new pc.Application(canvas, {
  keyboard: new pc.Keyboard(window),
  mouse: new pc.Mouse(canvas)
});

// 加载 Ammo.js
const ammoScript = document.createElement('script');
ammoScript.src = 'https://cdn.jsdelivr.net/npm/ammo.js@0.0.10/ammo.js';
document.body.appendChild(ammoScript);

ammoScript.onload = () => {
  Ammo().then((AmmoLib) => {
    window.Ammo = AmmoLib;

    // 创建静态地面
    const ground = new pc.Entity('ground');
    ground.addComponent('model', { type: 'plane' });
    ground.setLocalScale(10, 1, 10);

    ground.addComponent('rigidbody', {
      type: pc.BODYTYPE_STATIC
    });

    ground.addComponent('collision', {
      type: 'box',
      halfExtents: new pc.Vec3(5, 0.1, 5)
    });

    app.root.addChild(ground);

    // 创建动态立方体
    const cube = new pc.Entity('cube');
    cube.addComponent('model', { type: 'box' });
    cube.setPosition(0, 5, 0);

    cube.addComponent('rigidbody', {
      type: pc.BODYTYPE_DYNAMIC,
      mass: 1,
      friction: 0.5,
      restitution: 0.5
    });

    cube.addComponent('collision', {
      type: 'box',
      halfExtents: new pc.Vec3(0.5, 0.5, 0.5)
    });

    app.root.addChild(cube);

    // 施加力
    cube.rigidbody.applyForce(10, 0, 0);
    cube.rigidbody.applyTorque(0, 10, 0);

    app.start();
  });
};
```

---

### 模式 5：自定义脚本

创建可重用的脚本组件。

```javascript
// 定义脚本类
const RotateScript = pc.createScript('rotate');

// 脚本属性（编辑器暴露）
RotateScript.attributes.add('speed', {
  type: 'number',
  default: 10,
  title: '旋转速度'
});

RotateScript.attributes.add('axis', {
  type: 'vec3',
  default: [0, 1, 0],
  title: '旋转轴'
});

// 初始化方法
RotateScript.prototype.initialize = function() {
  console.log('RotateScript 初始化');
};

// 更新方法（每帧调用）
RotateScript.prototype.update = function(dt) {
  this.entity.rotate(
    this.axis.x * this.speed * dt,
    this.axis.y * this.speed * dt,
    this.axis.z * this.speed * dt
  );
};

// 清理
RotateScript.prototype.destroy = function() {
  console.log('RotateScript 销毁');
};

// 使用
const entity = new pc.Entity('旋转立方体');
entity.addComponent('model', { type: 'box' });
entity.addComponent('script');
entity.script.create('rotate', {
  attributes: {
    speed: 20,
    axis: new pc.Vec3(0, 1, 0)
  }
});
app.root.addChild(entity);
```

**脚本生命周期方法**：
```javascript
const MyScript = pc.createScript('myScript');

MyScript.prototype.initialize = function() {
  // 资源全部加载后调用一次
};

MyScript.prototype.postInitialize = function() {
  // 所有实体初始化后调用
};

MyScript.prototype.update = function(dt) {
  // 每帧渲染前调用
};

MyScript.prototype.postUpdate = function(dt) {
  // 每帧更新后调用
};

MyScript.prototype.swap = function(old) {
  // 热重载支持
};

MyScript.prototype.destroy = function() {
  // 实体销毁时清理
};
```

---

### 模式 6：输入处理

处理键盘、鼠标和触摸输入。

```javascript
// 键盘
if (app.keyboard.isPressed(pc.KEY_W)) {
  entity.translate(0, 0, -speed * dt);
}

if (app.keyboard.wasPressed(pc.KEY_SPACE)) {
  entity.rigidbody.applyImpulse(0, 10, 0);
}

// 鼠标
app.mouse.on(pc.EVENT_MOUSEDOWN, (event) => {
  if (event.button === pc.MOUSEBUTTON_LEFT) {
    console.log('左键点击于', event.x, event.y);
  }
});

app.mouse.on(pc.EVENT_MOUSEMOVE, (event) => {
  const dx = event.dx;
  const dy = event.dy;
  camera.rotate(-dy * 0.2, -dx * 0.2, 0);
});

// 触摸
app.touch.on(pc.EVENT_TOUCHSTART, (event) => {
  event.touches.forEach((touch) => {
    console.log('触摸于', touch.x, touch.y);
  });
});

// 射线投射（鼠标拾取）
app.mouse.on(pc.EVENT_MOUSEDOWN, (event) => {
  const camera = app.root.findByName('camera');
  const cameraComponent = camera.camera;

  const from = cameraComponent.screenToWorld(
    event.x,
    event.y,
    cameraComponent.nearClip
  );

  const to = cameraComponent.screenToWorld(
    event.x,
    event.y,
    cameraComponent.farClip
  );

  const result = app.systems.rigidbody.raycastFirst(from, to);

  if (result) {
    console.log('命中:', result.entity.name);
    result.entity.model.material.emissive = new pc.Color(1, 0, 0);
  }
});
```

---

### 模式 7：动画

播放骨骼动画和缓动。

**骨骼动画**：
```javascript
// 加载带动画的模型
const modelAsset = new pc.Asset('character', 'container', {
  url: '/models/character.glb'
});

app.assets.add(modelAsset);

modelAsset.ready((asset) => {
  const entity = asset.resource.instantiateRenderEntity();
  app.root.addChild(entity);

  // 获取动画组件
  entity.addComponent('animation', {
    assets: [asset],
    speed: 1.0,
    loop: true,
    activate: true
  });

  // 播放特定动画
  entity.animation.play('Walk', 0.2);  // 0.2s 混合时间

  // 之后，过渡到跑动
  entity.animation.play('Run', 0.5);
});

app.assets.load(modelAsset);
```

**属性缓动**：
```javascript
// 动画位置
entity.tween(entity.getLocalPosition())
  .to({ x: 5, y: 2, z: 0 }, 2.0, pc.SineInOut)
  .start();

// 动画旋转
entity.tween(entity.getLocalEulerAngles())
  .to({ x: 0, y: 180, z: 0 }, 1.0, pc.Linear)
  .loop(true)
  .yoyo(true)
  .start();

// 动画材质颜色
const color = material.emissive;
app.tween(color)
  .to(new pc.Color(1, 0, 0), 1.0, pc.SineInOut)
  .yoyo(true)
  .loop(true)
  .start();

// 链接缓动
entity.tween(entity.getLocalPosition())
  .to({ y: 2 }, 1.0)
  .to({ y: 0 }, 1.0)
  .delay(0.5)
  .repeat(3)
  .start();
```

---

## 集成模式

### 集成 1：React 集成

将 PlayCanvas 封装在 React 组件中。

```jsx
import React, { useEffect, useRef } from 'react';
import * as pc from 'playcanvas';

function PlayCanvasScene() {
  const canvasRef = useRef(null);
  const appRef = useRef(null);

  useEffect(() => {
    // 初始化
    const app = new pc.Application(canvasRef.current);
    appRef.current = app;

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);

    // 创建场景
    const camera = new pc.Entity('camera');
    camera.addComponent('camera', {
      clearColor: new pc.Color(0.1, 0.2, 0.3)
    });
    camera.setPosition(0, 0, 5);
    app.root.addChild(camera);

    const cube = new pc.Entity('cube');
    cube.addComponent('model', { type: 'box' });
    app.root.addChild(cube);

    const light = new pc.Entity('light');
    light.addComponent('light');
    light.setEulerAngles(45, 0, 0);
    app.root.addChild(light);

    app.on('update', (dt) => {
      cube.rotate(10 * dt, 20 * dt, 30 * dt);
    });

    app.start();

    // 清理
    return () => {
      app.destroy();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', height: '100vh' }}
    />
  );
}

export default PlayCanvasScene;
```

---

### 集成 2：编辑器导出

与 PlayCanvas 编辑器项目一起工作。

```javascript
// 从 PlayCanvas 编辑器导出
// 下载构建文件，然后在代码中加载：

import * as pc from 'playcanvas';

const app = new pc.Application(canvas);

// 加载导出的项目配置
fetch('/config.json')
  .then(response => response.json())
  .then(config => {
    // 加载场景
    app.scenes.loadSceneHierarchy(config.scene_url, (err, parent) => {
      if (err) {
        console.error('加载场景失败:', err);
        return;
      }

      // 启动应用
      app.start();

      // 通过名称查找实体
      const player = app.root.findByName('Player');
      const enemy = app.root.findByName('Enemy');

      // 访问脚本
      player.script.myScript.doSomething();
    });
  });
```

---

## 性能优化

### 1. 对象池

重用实体而不是创建/销毁。

```javascript
class EntityPool {
  constructor(app, count) {
    this.app = app;
    this.pool = [];
    this.active = [];

    for (let i = 0; i < count; i++) {
      const entity = new pc.Entity('pooled');
      entity.addComponent('model', { type: 'box' });
      entity.enabled = false;
      this.app.root.addChild(entity);
      this.pool.push(entity);
    }
  }

  spawn(position) {
    let entity = this.pool.pop();

    if (!entity) {
      // 池耗尽，创建新的
      entity = new pc.Entity('pooled');
      entity.addComponent('model', { type: 'box' });
      this.app.root.addChild(entity);
    }

    entity.enabled = true;
    entity.setPosition(position);
    this.active.push(entity);

    return entity;
  }

  despawn(entity) {
    entity.enabled = false;
    const index = this.active.indexOf(entity);
    if (index > -1) {
      this.active.splice(index, 1);
      this.pool.push(entity);
    }
  }
}

// 使用
const pool = new EntityPool(app, 100);
const bullet = pool.spawn(new pc.Vec3(0, 0, 0));

// 之后
pool.despawn(bullet);
```

---

### 2. LOD（细节层次）

为远处的对象减少几何体。

```javascript
// 手动 LOD 切换
app.on('update', () => {
  const distance = camera.getPosition().distance(entity.getPosition());

  if (distance < 10) {
    entity.model.asset = highResModel;
  } else if (distance < 50) {
    entity.model.asset = mediumResModel;
  } else {
    entity.model.asset = lowResModel;
  }
});

// 或者禁用远处的实体
app.on('update', () => {
  entities.forEach(entity => {
    const distance = camera.getPosition().distance(entity.getPosition());
    entity.enabled = distance < 100;
  });
});
```

---

### 3. 批量处理

将静态网格组合以减少绘制调用。

```javascript
// 为实体启用静态批量处理
entity.model.batchGroupId = 1;

// 批量处理具有相同组 ID 的所有实体
app.batcher.generate([entity1, entity2, entity3]);
```

---

### 4. 纹理压缩

使用压缩纹理格式。

```javascript
// 创建纹理时使用压缩格式
const texture = new pc.Texture(app.graphicsDevice, {
  width: 512,
  height: 512,
  format: pc.PIXELFORMAT_DXT5,  // GPU 压缩
  minFilter: pc.FILTER_LINEAR_MIPMAP_LINEAR,
  magFilter: pc.FILTER_LINEAR,
  mipmaps: true
});
```

---

## 常见陷阱

### 陷阱 1：未启动应用

**问题**：场景渲染但什么都没发生。

```javascript
// ❌ 错误 - 忘记启动
const app = new pc.Application(canvas);
// ... 创建实体 ...
// 什么都没发生!

// ✅ 正确
const app = new pc.Application(canvas);
// ... 创建实体 ...
app.start();  // 关键步骤！
```

---

### 陷阱 2：在更新期间修改实体

**问题**：在迭代期间修改场景图。

```javascript
// ❌ 错误 - 在迭代期间修改数组
app.on('update', () => {
  entities.forEach(entity => {
    if (entity.shouldDestroy) {
      entity.destroy();  // 修改数组!
    }
  });
});

// ✅ 正确 - 标记为销毁，之后清理
const toDestroy = [];

app.on('update', () => {
  entities.forEach(entity => {
    if (entity.shouldDestroy) {
      toDestroy.push(entity);
    }
  });
});

app.on('postUpdate', () => {
  toDestroy.forEach(entity => entity.destroy());
  toDestroy.length = 0;
});
```

---

### 陷阱 3：资源内存泄漏

**问题**：未清理加载的资源。

```javascript
// ❌ 错误 - 资源永远留在内存中
function loadModel() {
  const asset = new pc.Asset('model', 'container', { url: '/model.glb' });
  app.assets.add(asset);
  app.assets.load(asset);
  // 资源永远留在内存中
}

// ✅ 正确 - 完成后清理
function loadModel() {
  const asset = new pc.Asset('model', 'container', { url: '/model.glb' });
  app.assets.add(asset);

  asset.ready(() => {
    // 使用模型
  });

  app.assets.load(asset);

  // 清理
  return () => {
    app.assets.remove(asset);
    asset.unload();
  };
}

const cleanup = loadModel();
// 之后: cleanup();
```

---

### 陷阱 4：变换层次结构错误

**问题**：变换没有正确传播。

```javascript
// ❌ 错误 - 在子对象上设置世界变换
const parent = new pc.Entity();
const child = new pc.Entity();
parent.addChild(child);

child.setPosition(5, 0, 0);  // 局部位置
parent.setPosition(10, 0, 0);
// 子对象在世界空间位于 (15, 0, 0)

// ✅ 正确 - 理解局部与世界的区别
child.setLocalPosition(5, 0, 0);  // 显式局部
// 或者
const worldPos = new pc.Vec3(15, 0, 0);
child.setPosition(worldPos);  // 显式世界
```

---

### 陷阱 5：物理未初始化

**问题**：物理组件无法工作。

```javascript
// ❌ 错误 - Ammo.js 未加载
const entity = new pc.Entity();
entity.addComponent('rigidbody', { type: pc.BODYTYPE_DYNAMIC });
// 错误：Ammo 未定义

// ✅ 正确 - 确保 Ammo.js 已加载
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/ammo.js@0.0.10/ammo.js';
document.body.appendChild(script);

script.onload = () => {
  Ammo().then((AmmoLib) => {
    window.Ammo = AmmoLib;

    // 现在物理可以工作了
    const entity = new pc.Entity();
    entity.addComponent('rigidbody', { type: pc.BODYTYPE_DYNAMIC });
    entity.addComponent('collision', { type: 'box' });
    entity.addComponent('collision', { type: 'box', halfExtents: new pc.Vec3(5, 0.1, 5) });
  });
};
```

---

### 陷阱 6：画布尺寸问题

**问题**：画布不填充容器或无法响应调整大小。

```javascript
// ❌ 错误 - 固定尺寸画布
const canvas = document.createElement('canvas');
canvas.width = 800;
canvas.height = 600;

// ✅ 正确 - 响应式画布
const canvas = document.createElement('canvas');
const app = new pc.Application(canvas);

app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);

window.addEventListener('resize', () => app.resizeCanvas());
```

---

## 资源

- **官方 API**: https://api.playcanvas.com/
- **开发者文档**: https://developer.playcanvas.com/
- **示例**: https://playcanvas.github.io/
- **编辑器**: https://playcanvas.com/
- **GitHub**: https://github.com/playcanvas/engine
- **论坛**: https://forum.playcanvas.com/

---

## 快速参考

### 应用设置
```javascript
const app = new pc.Application(canvas);
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);
app.start();
```

### 实体创建
```javascript
const entity = new pc.Entity('name');
entity.addComponent('model', { type: 'box' });
entity.setPosition(x, y, z);
app.root.addChild(entity);
```

### 更新循环
```javascript
app.on('update', (dt) => {
  // 逻辑在此处
});
```

### 加载资源
```javascript
const asset = new pc.Asset('name', 'type', { url: '/path' });
app.assets.add(asset);
asset.ready(() => { /* 使用资源 */ });
app.assets.load(asset);
```

---

**相关技能**: 对于低级别的 WebGL 控制，参考 threejs-webgl。对于 React 集成模式，参考 react-three-fiber。对于物理密集型模拟，参考 babylonjs-engine。
