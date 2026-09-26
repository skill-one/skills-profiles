# Babylon.js 引擎技能

## 相关技能
- threejs-webgl：替代 3D 引擎
- react-three-fiber：用于 3D 的 React 集成
- gsap-scrolltrigger：动画库
- motion-framer：UI 动画

## 核心概念

### 1. 引擎和场景初始化

**基本设置**
```javascript
// 获取 canvas 元素
const canvas = document.getElementById('renderCanvas');

// 创建引擎
const engine = new BABYLON.Engine(canvas, true, {
  preserveDrawingBuffer: true,
  stencil: true
});

// 创建场景
const scene = new BABYLON.Scene(engine);

// 渲染循环
engine.runRenderLoop(() => {
  scene.render();
});

// 处理调整大小
window.addEventListener('resize', () => {
  engine.resize();
});
```

**ES6/TypeScript 设置**
```typescript
import { Engine } from '@babylonjs/core/Engines/engine';
import { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { CreateSphere } from '@babylonjs/core/Meshes/Builders/sphereBuilder';

const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement;
const engine = new Engine(canvas);
const scene = new Scene(engine);

// 相机设置
const camera = new FreeCamera('camera1', new Vector3(0, 5, -10), scene);
camera.setTarget(Vector3.Zero());
camera.attachControl(canvas, true);

// 灯光
const light = new HemisphericLight('light1', new Vector3(0, 1, 0), scene);
light.intensity = 0.7;

// 创建网格
const sphere = CreateSphere('sphere1', { segments: 16, diameter: 2 }, scene);
sphere.position.y = 2;

// 渲染
engine.runRenderLoop(() => {
  scene.render();
});
```

**场景配置选项**
```javascript
const scene = new BABYLON.Scene(engine, {
  // 优化用于大型网格数量
  useGeometryUniqueIdsMap: true,
  useMaterialMeshMap: true,
  useClonedMeshMap: true
});
```

### 2. 相机系统

**自由相机（FPS 风格）**
```javascript
const camera = new BABYLON.FreeCamera('camera1', new BABYLON.Vector3(0, 5, -10), scene);
camera.setTarget(BABYLON.Vector3.Zero());
camera.attachControl(canvas, true);

// 移动设置
camera.speed = 0.5;
camera.angularSensibility = 2000;
camera.keysUp = [87]; // W
camera.keysDown = [83]; // S
camera.keysLeft = [65]; // A
camera.keysRight = [68]; // D
```

**弧旋转相机（轨道）**
```javascript
const camera = new BABYLON.ArcRotateCamera(
  'camera',
  -Math.PI / 2,        // alpha (水平旋转)
  Math.PI / 2.5,       // beta (垂直旋转)
  15,                  // 半径 (距离)
  new BABYLON.Vector3(0, 0, 0), // 目标
  scene
);
camera.attachControl(canvas, true);

// 限制
camera.lowerRadiusLimit = 5;
camera.upperRadiusLimit = 50;
camera.lowerBetaLimit = 0.1;
camera.upperBetaLimit = Math.PI / 2;
```

**通用相机（高级）**
```javascript
const camera = new BABYLON.UniversalCamera('camera', new BABYLON.Vector3(0, 5, -10), scene);
camera.setTarget(BABYLON.Vector3.Zero());
camera.attachControl(canvas, true);

// 碰撞检测
camera.checkCollisions = true;
camera.applyGravity = true;
camera.ellipsoid = new BABYLON.Vector3(1, 1, 1);
```

### 3. 灯光系统

**半球光（环境光）**
```javascript
const light = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0, 1, 0), scene);
light.intensity = 0.7;
light.diffuse = new BABYLON.Color3(1, 1, 1);
light.specular = new BABYLON.Color3(1, 1, 1);
light.groundColor = new BABYLON.Color3(0, 0, 0);
```

**方向光（类似太阳）**
```javascript
const light = new BABYLON.DirectionalLight('dirLight', new BABYLON.Vector3(-1, -2, -1), scene);
light.position = new BABYLON.Vector3(20, 40, 20);
light.intensity = 0.5;

// 阴影设置
const shadowGenerator = new BABYLON.ShadowGenerator(1024, light);
shadowGenerator.useExponentialShadowMap = true;
```

**点光源（全向）**
```javascript
const light = new BABYLON.PointLight('pointLight', new BABYLON.Vector3(0, 10, 0), scene);
light.intensity = 0.7;
light.diffuse = new BABYLON.Color3(1, 0, 0);
light.specular = new BABYLON.Color3(0, 1, 0);

// 范围和衰减
light.range = 100;
light.radius = 0.1;
```

**聚光灯（聚焦）**
```javascript
const light = new BABYLON.SpotLight(
  'spotLight',
  new BABYLON.Vector3(0, 10, 0),      // 位置
  new BABYLON.Vector3(0, -1, 0),      // 方向
  Math.PI / 3,                        // 角度
  2,                                  // 指数
  scene
);
light.intensity = 0.8;
```

**灯光优化（仅影响特定网格）**
```javascript
// 仅影响特定网格
light.includedOnlyMeshes = [mesh1, mesh2, mesh3];

// 或者排除特定网格
light.excludedMeshes = [mesh4, mesh5];
```

### 4. 网格创建

**内置形状**
```javascript
// 立方体
const box = BABYLON.MeshBuilder.CreateBox('box', {
  size: 2,
  width: 2,
  height: 2,
  depth: 2
}, scene);

// 球体
const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {
  diameter: 2,
  segments: 32,
  diameterX: 2,
  diameterY: 2,
  diameterZ: 2,
  arc: 1,
  slice: 1
}, scene);

// 圆柱体
const cylinder = BABYLON.MeshBuilder.CreateCylinder('cylinder', {
  height: 3,
  diameter: 2,
  tessellation: 24
}, scene);

// 平面
const plane = BABYLON.MeshBuilder.CreatePlane('plane', {
  size: 5,
  width: 5,
  height: 5
}, scene);

// 地面
const ground = BABYLON.MeshBuilder.CreateGround('ground', {
  width: 10,
  height: 10,
  subdivisions: 2
}, scene);

// 从高度图创建地面
const ground = BABYLON.MeshBuilder.CreateGroundFromHeightMap('ground', 'heightmap.png', {
  width: 100,
  height: 100,
  subdivisions: 100,
  minHeight: 0,
  maxHeight: 10
}, scene);

// 圆环
const torus = BABYLON.MeshBuilder.CreateTorus('torus', {
  diameter: 3,
  thickness: 1,
  tessellation: 16
}, scene);

// 圆环结
const torusKnot = BABYLON.MeshBuilder.CreateTorusKnot('torusKnot', {
  radius: 2,
  tube: 0.6,
  radialSegments: 64,
  tubularSegments: 8,
  p: 2,
  q: 3
}, scene);
```

**网格变换**
```javascript
// 位置
mesh.position = new BABYLON.Vector3(0, 5, 10);
mesh.position.x = 5;
mesh.position.y = 2;

// 旋转（弧度）
mesh.rotation = new BABYLON.Vector3(0, Math.PI / 2, 0);
mesh.rotation.y = Math.PI / 4;

// 缩放
mesh.scaling = new BABYLON.Vector3(2, 2, 2);
mesh.scaling.x = 1.5;

// 朝向
mesh.lookAt(new BABYLON.Vector3(0, 0, 0));

// 父子关系
childMesh.parent = parentMesh;
```

**网格属性**
```javascript
// 可见性
mesh.isVisible = true;
mesh.visibility = 0.5; // 0 = 不可见, 1 = 完全可见

// 挑选
mesh.isPickable = true;
mesh.checkCollisions = true;

// 排除
mesh.cullingStrategy = BABYLON.AbstractMesh.CULLINGSTRATEGY_BOUNDINGSPHERE_ONLY;

// 接收阴影
mesh.receiveShadows = true;
```

### 5. 材质

**标准材质**
```javascript
const material = new BABYLON.StandardMaterial('material', scene);

// 颜色
material.diffuseColor = new BABYLON.Color3(1, 0, 1);
material.specularColor = new BABYLON.Color3(0.5, 0.6, 0.87);
material.emissiveColor = new BABYLON.Color3(0, 0, 0);
material.ambientColor = new BABYLON.Color3(0.23, 0.98, 0.53);

// 纹理
material.diffuseTexture = new BABYLON.Texture('diffuse.png', scene);
material.specularTexture = new BABYLON.Texture('specular.png', scene);
material.emissiveTexture = new BABYLON.Texture('emissive.png', scene);
material.ambientTexture = new BABYLON.Texture('ambient.png', scene);
material.bumpTexture = new BABYLON.Texture('normal.png', scene);
material.opacityTexture = new BABYLON.Texture('opacity.png', scene);

// 属性
material.alpha = 0.8;
material.backFaceCulling = true;
material.wireframe = false;
material.specularPower = 64;

// 应用到网格
mesh.material = material;
```

**PBR 材质（基于物理的渲染）**
```javascript
const pbr = new BABYLON.PBRMaterial('pbr', scene);

// 金属工作流
pbr.albedoColor = new BABYLON.Color3(1, 1, 1);
pbr.albedoTexture = new BABYLON.Texture('albedo.png', scene);
pbr.metallic = 1.0;
pbr.roughness = 0.5;
pbr.metallicTexture = new BABYLON.Texture('metallic.png', scene);

// 或者高光工作流
pbr.albedoTexture = new BABYLON.Texture('albedo.png', scene);
pbr.reflectivityTexture = new BABYLON.Texture('reflectivity.png', scene);

// 环境
pbr.environmentTexture = BABYLON.CubeTexture.CreateFromPrefilteredData('environment.dds', scene);

// 其他贴图
pbr.bumpTexture = new BABYLON.Texture('normal.png', scene);
pbr.ambientTexture = new BABYLON.Texture('ao.png', scene);
pbr.emissiveTexture = new BABYLON.Texture('emissive.png', scene);

mesh.material = pbr;
```

**多材质**
```javascript
const multiMat = new BABYLON.MultiMaterial('multiMat', scene);
multiMat.subMaterials.push(material1);
multiMat.subMaterials.push(material2);
multiMat.subMaterials.push(material3);

mesh.material = multiMat;
mesh.subMeshes = [];
mesh.subMeshes.push(new BABYLON.SubMesh(0, 0, verticesCount, 0, indicesCount1, mesh));
mesh.subMeshes.push(new BABYLON.SubMesh(1, 0, verticesCount, indicesCount1, indicesCount2, mesh));
```

### 6. 模型加载

**GLTF/GLB 导入**
```javascript
// 追加到场景
BABYLON.SceneLoader.Append('path/to/', 'model.gltf', scene, function(scene) {
  console.log('模型加载');
});

// 导入网格
BABYLON.SceneLoader.ImportMesh('', 'path/to/', 'model.gltf', scene, function(meshes) {
  const mesh = meshes[0];
  mesh.position.y = 5;
});

// 异步版本
const result = await BABYLON.SceneLoader.ImportMeshAsync(
  null,  // 所有网格
  'https://assets.babylonjs.com/meshes/',
  'village.glb',
  scene
);
console.log('加载的网格:', result.meshes);

// 从二进制加载
const result = await BABYLON.SceneLoader.AppendAsync(
  '',
  'data:' + arrayBuffer,
  scene
);
```

**资源管理器（批量加载）**
```javascript
const assetsManager = new BABYLON.AssetsManager(scene);

// 添加网格任务
const meshTask = assetsManager.addMeshTask('model', '', 'path/to/', 'model.gltf');
meshTask.onSuccess = function(task) {
  task.loadedMeshes[0].position = new BABYLON.Vector3(0, 0, 0);
};

// 添加纹理任务
const textureTask = assetsManager.addTextureTask('texture', 'texture.png');
textureTask.onSuccess = function(task) {
  material.diffuseTexture = task.texture;

// 加载所有
assetsManager.onFinish = function(tasks) {
  console.log('所有资源加载');
  engine.runRenderLoop(() => scene.render());
};

assetsManager.load();
```

### 7. 物理引擎

**Havok 物理设置**
```javascript
// 导入 Havok
import HavokPhysics from '@babylonjs/havok';

// 初始化
const havokInstance = await HavokPhysics();
const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);

// 启用物理
scene.enablePhysics(new BABYLON.Vector3(0, -9.8, 0), havokPlugin);

// 为网格创建物理聚合
const sphereAggregate = new BABYLON.PhysicsAggregate(
  sphere,
  BABYLON.PhysicsShapeType.SPHERE,
  { mass: 1, restitution: 0.75 },
  scene
);

// 地面（静态）
const groundAggregate = new BABYLON.PhysicsAggregate(
  ground,
  BABYLON.PhysicsShapeType.BOX,
  { mass: 0 }, // mass 0 = 静态
  scene
);
```

**物理形状**
```javascript
// 可用形状
BABYLON.PhysicsShapeType.SPHERE
BABYLON.PhysicsShapeType.BOX
BABYLON.PhysicsShapeType.CAPSULE
BABYLON.PhysicsShapeType.CYLINDER
BABYLON.PhysicsShapeType.CONVEX_HULL
BABYLON.PhysicsShapeType.MESH
BABYLON.PhysicsShapeType.HEIGHTFIELD
```

**物理身体控制**
```javascript
// 获取身体
const body = aggregate.body;

// 施加力
body.applyForce(
  new BABYLON.Vector3(0, 10, 0),    // 力
  new BABYLON.Vector3(0, 0, 0)      // 施加点
);

// 施加冲量
body.applyImpulse(
  new BABYLON.Vector3(0, 5, 0),
  new BABYLON.Vector3(0, 0, 0)
);

// 设置速度
body.setLinearVelocity(new BABYLON.Vector3(0, 5, 0));
body.setAngularVelocity(new BABYLON.Vector3(0, 1, 0));

// 属性
body.setMassProperties({ mass: 2 });
body.setCollisionCallbackEnabled(true);
```

### 8. 动画

**直接动画**
```javascript
// 动画属性
BABYLON.Animation.CreateAndStartAnimation(
  'anim',
  mesh,
  'position.y',
  30,                    // FPS
  120,                   // 总帧数
  mesh.position.y,       // 从
  10,                    // 到
  BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE
);
```

**动画类**
```javascript
const animation = new BABYLON.Animation(
  'myAnimation',
  'position.x',
  30,
  BABYLON.Animation.ANIMATIONTYPE_FLOAT,
  BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE
);

// 关键帧
const keys = [
  { frame: 0, value: 0 },
  { frame: 30, value: 10 },
  { frame: 60, value: 0 }
];
animation.setKeys(keys);

// 绑定到网格
mesh.animations.push(animation);

// 开始
scene.beginAnimation(mesh, 0, 60, true);
```

**动画组**
```javascript
const animationGroup = new BABYLON.AnimationGroup('group', scene);
animationGroup.addTargetedAnimation(animation1, mesh1);
animationGroup.addTargetedAnimation(animation2, mesh2);

// 控制
animationGroup.play();
animationGroup.pause();
animationGroup.stop();
animationGroup.speedRatio = 2.0;

// 事件
animationGroup.onAnimationEndObservable.add(() => {
  console.log('动画完成');
});
```

**骨骼动画（从导入的模型）**
```javascript
// 从导入的模型获取骨骼
const skeleton = result.skeletons[0];

// 获取动画范围
const ranges = skeleton.getAnimationRanges();

// 播放动画范围
scene.beginAnimation(skeleton, 0, 100, true);

// 或者使用动画组
result.animationGroups[0].play();
result.animationGroups[0].setWeightForAllAnimatables(0.5);
```

## 常见模式

### 模式 1：默认环境场景设置

```javascript
const createScene = function() {
  const scene = new BABYLON.Scene(engine);

  // 快速设置
  scene.createDefaultCameraOrLight(true, true, true);
  const env = scene.createDefaultEnvironment({
    createGround: true,
    createSkybox: true,
    skyboxSize: 150,
    groundSize: 50
});

  // 你的网格
const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);
sphere.position.y = 1;

return scene;
};
```

### 模式 2：异步场景加载

```javascript
const createScene = async function() {
  const scene = new BABYLON.Scene(engine);

  const camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, BABYLON.Vector3.Zero(), scene);
  camera.attachControl(canvas, true);

  const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);

  const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);
  sphere.position.y = 1;

  // 加载模型
  const result = await BABYLON.SceneLoader.ImportMeshAsync(
    null,
    'https://assets.babylonjs.com/meshes/',
    'village.glb',
    scene
  );

  // 设置物理
  const havokInstance = await HavokPhysics();
  const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);
  scene.enablePhysics(new BABYLON.Vector3(0, -9.8, 0), havokPlugin);

return scene;
};

createScene().then(scene => {
  engine.runRenderLoop(() => scene.render());
});
```

### 模式 3：交互式挑选

```javascript
scene.onPointerDown = function(evt, pickResult) {
  if (pickResult.hit) {
    console.log('挑选的网格:', pickResult.pickedMesh.name);
    console.log('挑选点:', pickResult.pickedPoint);

    // 高亮挑选的网格
    pickResult.pickedMesh.material.emissiveColor = new BABYLON.Color3(1, 0, 0);
  }
};

// 或者使用动作管理器
mesh.actionManager = new BABYLON.ActionManager(scene);
mesh.actionManager.registerAction(
  new BABYLON.ExecuteCodeAction(
    BABYLON.ActionManager.OnPickTrigger,
    function() {
      console.log('网格点击');
    }
  )
);
```

### 模式 4：后处理效果

```javascript
// 默认渲染管线
const pipeline = new BABYLON.DefaultRenderingPipeline('pipeline', true, scene, [camera]);
pipeline.samples = 4;
pipeline.fxaaEnabled = true;
pipeline.bloomEnabled = true;
pipeline.bloomThreshold = 0.8;
pipeline.bloomWeight = 0.5;
pipeline.bloomKernel = 64;

// 景深
pipeline.depthOfFieldEnabled = true;
pipeline.depthOfFieldBlurLevel = BABYLON.DepthOfFieldEffectBlurLevel.Low;
pipeline.depthOfField.focusDistance = 2000;
pipeline.depthOfField.focalLength = 50;

// 发光层
const glowLayer = new BABYLON.GlowLayer('glow', scene);
glowLayer.intensity = 0.5;

// 高亮层
const highlightLayer = new BABYLON.HighlightLayer('highlight', scene);
highlightLayer.addMesh(mesh, BABYLON.Color3.Green());
```

### 模式 5：GUI（2D UI）

```javascript
import { AdvancedDynamicTexture, Button, TextBlock, Rectangle } from '@babylonjs/gui';

// 全屏 UI
const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('UI');

// 按钮
const button = BABYLON.GUI.Button.CreateSimpleButton('button', '点击我');
button.width = '150px';
button.height = '40px';
button.color = 'white';
button.background = 'green';
button.onPointerUpObservable.add(() => {
  console.log('按钮点击');
});
advancedTexture.addControl(button);

// 文本
const text = new BABYLON.GUI.TextBlock();
text.text = 'Hello World';
text.color = 'white';
text.fontSize = 24;
advancedTexture.addControl(text);

// 3D 网格 UI
const plane = BABYLON.MeshBuilder.CreatePlane('plane', {size: 2}, scene);
const advancedTexture3D = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(plane);
const button3D = BABYLON.GUI.Button.CreateSimpleButton('button3D', '点击我');
advancedTexture3D.addControl(button3D);
```

### 模式 6：阴影映射

```javascript
const light = new BABYLON.DirectionalLight('light', new BABYLON.Vector3(-1, -2, -1), scene);
light.position = new BABYLON.Vector3(20, 40, 20);

// 创建阴影生成器
const shadowGenerator = new BABYLON.ShadowGenerator(1024, light);
shadowGenerator.useExponentialShadowMap = true;
shadowGenerator.usePoissonSampling = true;

// 添加阴影投射器
shadowGenerator.addShadowCaster(sphere);
shadowGenerator.addShadowCaster(box);

// 启用阴影接收
ground.receiveShadows = true;
```

### 模式 7：粒子系统

```javascript
const particleSystem = new BABYLON.ParticleSystem('particles', 2000, scene);
particleSystem.particleTexture = new BABYLON.Texture('particle.png', scene);

// 发射器
particleSystem.emitter = new BABYLON.Vector3(0, 5, 0);
particleSystem.minEmitBox = new BABYLON.Vector3(-1, 0, 0);
particleSystem.maxEmitBox = new BABYLON.Vector3(1, 0, 0);

// 颜色
particleSystem.color1 = new BABYLON.Color4(0.7, 0.8, 1.0, 1.0);
particleSystem.color2 = new BABYLON.Color4(0.2, 0.5, 1.0, 1.0);
particleSystem.colorDead = new BABYLON.Color4(0, 0, 0.2, 0.0);

// 大小
particleSystem.minSize = 0.1;
particleSystem.maxSize = 0.5;

// 生命周期
particleSystem.minLifeTime = 0.3;
particleSystem.maxLifeTime = 1.5;

// 发射速率
particleSystem.emitRate = 1500;

// 方向
particleSystem.direction1 = new BABYLON.Vector3(-1, 8, 1);
particleSystem.direction2 = new BABYLON.Vector3(1, 8, -1);

// 重力
particleSystem.gravity = new BABYLON.Vector3(0, -9.81, 0);

// 开始
particleSystem.start();
```

## 集成模式

### 模式 1：React 集成

```jsx
import { useEffect, useRef } from 'react';
import * as BABYLON from '@babylonjs/core';

function BabylonScene() {
  const canvasRef = useRef(null);
  const engineRef = useRef(null);
  const sceneRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // 初始化
    const engine = new BABYLON.Engine(canvasRef.current, true);
    engineRef.current = engine;

    const scene = new BABYLON.Scene(engine);
    sceneRef.current = scene;

    // 设置场景
    const camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, BABYLON.Vector3.Zero(), scene);
    camera.attachControl(canvasRef.current, true);

    const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);

    const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);

    // 渲染循环
engine.runRenderLoop(() => {
      scene.render();
    });

    // 调整大小处理
    const handleResize = () => engine.resize();
    window.addEventListener('resize', handleResize);

    // 清理
    return () => {
      window.removeEventListener('resize', handleResize);
      scene.dispose();
      engine.dispose();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', height: '100vh' }}
    />
  );
}
```

### 模式 2：WebXR（VR/AR）

```javascript
const createScene = async function() {
  const scene = new BABYLON.Scene(engine);

  const camera = new BABYLON.FreeCamera('camera', new BABYLON.Vector3(0, 5, -10), scene);
  camera.attachControl(canvas, true);

  const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);

  const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);
  sphere.position.y = 1;

  const env = scene.createDefaultEnvironment();

  // 启用 WebXR
  const xrHelper = await scene.createDefaultXRExperienceAsync({
    floorMeshes: [env.ground],
    disableTeleportation: false
  });

  // XR 控制器输入
  xrHelper.input.onControllerAddedObservable.add((controller) => {
    controller.onMotionControllerInitObservable.add((motionController) => {
      const trigger = motionController.getMainComponent();
      trigger.onButtonStateChangedObservable.add(() => {
        if (trigger.pressed) {
          console.log('Trigger pressed');
        }
      });
    });
  });

  return scene;
};
```

### 模式 3：Node Material（视觉着色器编辑器）

```javascript
// 从片段创建
const nodeMaterial = await BABYLON.NodeMaterial.ParseFromSnippetAsync('#SNIPPET_ID', scene);

// 应用到网格
nodeMaterial.build();
mesh.material = nodeMaterial;

// 或者程序化创建
const nodeMaterial = new BABYLON.NodeMaterial('node', scene);

const positionInput = new BABYLON.InputBlock('position');
positionInput.setAsAttribute('position');

const worldPos = new BABYLON.TransformBlock('worldPos');
nodeMaterial.addOutputNode(worldPos);
```

## 高级主题

### 1. 自定义着色器

```javascript
BABYLON.Effect.ShadersStore['customVertexShader'] = `
  precision highp float;
  attribute vec3 position;
  attribute vec2 uv;
  uniform mat4 worldViewProjection;
  varying vec2 vUV;

  void main(void) {
    gl_Position = worldViewProjection * vec4(position, 1.0);
    vUV = uv;
  }
`;

BABYLON.Effect.ShadersStore['customFragmentShader'] = `
  precision highp float;
  varying vec2 vUV;
  uniform sampler2D textureSampler;

  void main(void) {
    gl_FragColor = texture2D(textureSampler, vUV);
  }
`;

const shaderMaterial = new BABYLON.ShaderMaterial('shader', scene, {
  vertex: 'custom',
  fragment: 'custom'
}, {
  attributes: ['position', 'uv'],
  uniforms: ['worldViewProjection']
});
```

### 2. 计算着色器

```javascript
const computeShader = new BABYLON.ComputeShader('compute', engine, {
  computeSource: `
    #version 450
    layout (local_size_x = 8, local_size_y = 8, local_size_z = 1) in;
    layout(std430, binding = 0) buffer OutputBuffer { vec4 data[]; } outputBuffer;

    void main() {
      uint index = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y * 8u;
      outputBuffer.data[index] = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `
});
```

### 3. 过程纹理

```javascript
const noiseTexture = new BABYLON.NoiseProceduralTexture('noise', 256, scene);
noiseTexture.octaves = 4;
noiseTexture.persistence = 0.8;
noiseTexture.animationSpeedFactor = 5;

material.emissiveTexture = noiseTexture;
```

## 调试

```javascript
// 显示检查器
scene.debugLayer.show();

// 显示边界框
scene.forceShowBoundingBoxes = true;

// 显示线框
material.wireframe = true;

// 记录 FPS
setInterval(() => {
  console.log('FPS:', engine.getFps());
}, 1000);

// 仪器化
const instrumentation = new BABYLON.SceneInstrumentation(scene);
instrumentation.captureFrameTime = true;
console.log('帧时间:', instrumentation.frameTimeCounter.average);
```

## 资源

- [官方文档](https://doc.babylonjs.com/)
- [Playground](https://playground.babylonjs.com/)
- [论坛](https://forum.babylonjs.com/)
- [示例](https://doc.babylonjs.com/examples/)
- [NPM 包](https://www.npmjs.com/package/@babylonjs/core)

## 版本说明

此技能基于 Babylon.js 7.x。如需最新功能，请参考官方文档。
