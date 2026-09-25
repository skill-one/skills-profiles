# React Three Fiber光照

首先检查已安装的Three.js、Fiber和Drei版本以及渲染器。本示例针对Fiber 9 / React 19、Three.js r185和WebGL。

## 从刻意设置光照开始

- 使用环境光照进行PBR反射/填充，使用直接光照进行方向和实时阴影。更多的环境光无法恢复缺失的金属反射。
- 场景背景和`scene.environment`具有不同的用途。Drei的`Environment`用于分配光照；`background`额外使其在场景后方可见。
- 生产环境中优先使用自有的HDR/EXR资源。Drei预设适用于原型设计，但依赖于外部托管。选择新格式前请检查加载器支持情况。
- `Sky`是可见的天空几何体，不自动匹配太阳光或环境。当视觉一致性重要时，需对齐天空、直接光和环境。

## 阴影场景

在`<Canvas shadows="percentage">`内部挂载。Three.js r182+后，PCFShadowMap为柔和阴影；Fiber 9的裸`shadows`选择已弃用的PCFSoftShadowMap。

```tsx
export default function Example() {
  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[3, 5, 3]}
        intensity={3}
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-camera-left={-4}
        shadow-camera-right={4}
        shadow-camera-top={4}
        shadow-camera-bottom={-4}
        shadow-camera-near={0.5}
        shadow-camera-far={15}
        shadow-normalBias={0.02}
      />
      <mesh castShadow position={[0, 0.5, 0]}>
        <boxGeometry />
        <meshStandardMaterial color="coral" />
      </mesh>
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[8, 8]} />
        <meshStandardMaterial color="silver" />
      </mesh>
    </>
  )
}
```

上述偏移和视锥值适用于此小场景；根据实际尺寸重新调整。

## 阴影和光照目标

- 阴影映射需要启用渲染器阴影、阴影投射光源、投射网格以及接收材质/网格。环境光和半球光不投射阴影。
- 在提高贴图分辨率前，将阴影相机紧缩到有用区域。使用CameraHelper检查其视锥；偏移应解决麻点问题，同时避免阴影与物体分离。
- 点光源阴影渲染六个方向。限制阴影投射光源和大型贴图；成本取决于受影响的几何体和通道，而不仅限于光源数量。
- 移动方向/聚光灯的目标需要目标Object3D，其世界矩阵会更新。向场景图添加自定义目标；仅更改分离目标的位置可能导致其世界变换过时。
- 使用WebGL时，RectAreaLight影响Standard/Physical材质，不投射内置阴影。在使用需要原生光照路径时，初始化`RectAreaLightUniformsLib`。
- Object/camera层在WebGLRenderer中不是通用每光源材质掩码。不要承诺匹配光源层到网格就能实现选择性照明。

## 环境和辅助成本

- Drei `Lightformer`是捕获到环境的发光几何体；它不是普通实时光源，不投射直接光阴影。
- 为真正静态的环境捕获或ContactShadows设置`frames={1}`。动画对象/光照需要重新捕获；冻结的捕获会保持过时。
- ContactShadows渲染离屏深度/模糊近似。它不是免费的，也无法替代所有方向阴影。
- AccumulativeShadows跨样本收敛；更改场景可能需要重置/重新累积。BakeShadows冻结更新，而不是生成可移植的烘焙光照贴图。
- SoftShadows修补WebGL着色器代码。在添加前，请针对安装的Three.js阴影实现进行验证，尤其是在渲染器升级后。
- 调整光照时保持色调映射/曝光一致性。当前基于物理的光照强度不应盲目与旧版遗留光照教程混合。

## 验证

检查阴影接触、麻点、裁剪、加载模型投射/接收标志以及移动对象。比较静态与动画捕获行为，并在目标设备上测量总渲染通道。

## 来源

- [Drei Environment](https://drei.docs.pmnd.rs/staging/environment), [ContactShadows](https://drei.docs.pmnd.rs/staging/contact-shadows).
- [Three.js shadows](https://threejs.org/manual/en/shadows.html), [RectAreaLight](https://threejs.org/docs/#RectAreaLight), [DirectionalLight](https://threejs.org/docs/#DirectionalLight).
- [Migration guide](https://github.com/mrdoob/three.js/wiki/Migration-Guide) — r182中的PCF变更和r184中的环境旋转变更。
