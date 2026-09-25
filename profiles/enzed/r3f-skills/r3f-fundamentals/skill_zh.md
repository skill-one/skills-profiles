# React Three Fiber 基础知识

## 选择合适的基线

- 在选择 API 之前，检查项目的 manifest 和 lockfile。这些示例针对 Fiber 9 / React 19；Fiber 8 与 React 18 配合使用。不要为了匹配某个示例而升级项目。
- 检查已安装的 Three.js 和 Drei 版本。使用与这些版本匹配的发布文档；如果不可用，请说明不确定性，而不是编造属性。
- 除非任务要求更改，否则保留现有的渲染器。对于 WebGPU，请阅读 [渲染器选择](references/renderers.md)；Fiber 10 alpha API 不是 Fiber 9 API。

## 最小场景

此示例拥有自己的 Canvas。其父元素必须具有非零高度。

```tsx
import { useRef } from 'react'
import { Canvas, useFrame, type ThreeElements } from '@react-three/fiber'
import type { Mesh } from 'three'

function RotatingBox(props: ThreeElements['mesh']) {
  const mesh = useRef<Mesh>(null)
  useFrame((_, delta) => {
    if (mesh.current) mesh.current.rotation.y += delta * 0.5
  })
  return (
    <mesh {...props} ref={mesh}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="coral" />
    </mesh>
  )
}

export default function Example() {
  return (
    <Canvas camera={{ position: [0, 0, 5] }} dpr={[1, 2]}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[3, 4, 5]} intensity={2} />
      <RotatingBox />
    </Canvas>
  )
}
```

## 场景和类型边界

- 在 Canvas 下的组件中调用 `useThree`、`useFrame` 和加载器钩子，绝不能在创建该 Canvas 的组件中或事件回调内部调用。
- Canvas 子元素是 Three.js 对象。将 DOM UI 放置在它外面，或使用 Drei 的 `Html`。Canvas 内部的 Suspense 回退必须遵守相同规则。
- 使用 `ThreeElements['mesh']` 作为网格属性，使用 `useRef<Mesh>(null)` 作为引用。Fiber 9 使用 `ThreeElement<typeof Class>` 作为自定义元素；不要使用已移除的 `Object3DNode` 或全局 `JSX.IntrinsicElements` 扩展。
- `extend(Class)` 在 Fiber 9 中创建一个本地类型组件。当确实需要一个共享的小写 JSX 元素时，使用 `extend({ Class })` 并扩展 `@react-three/fiber` 模块。
- `args` 是构造函数参数：更改它们会重建对象。通过更新普通属性或引用进行动画；当输入未更改时，保留昂贵的形状、数组和材质。
- 几何体/材质子元素会自动附加。使用显式的 `attach` 来处理其他属性，例如 `attach="attributes-position"` 用于缓冲区属性。
- Three.js 使用弧度和局部变换。在将世界空间输入分配给 `position` 之前，将其转换为对象的父空间。

## 渲染循环决策

- 使用 React 状态进行离散的 UI 变更；通过修改拥有的引用进行每帧运动。重用暂存向量并使用秒为单位的 `delta`。不要为同一场景创建第二个动画循环。
- `useThree(state => state.camera)` 订阅相机替换，而不是 `camera.position` 的突变。在 `useFrame` 内部读取瞬时值；在强制相机投影更改后更新投影矩阵。
- 默认 `frameloop="always"` 适用于连续动画。对于可以休眠的场景，使用 `"demand"`：强制更改需要 `invalidate()`，动画必须持续无效化直到稳定。Drei 控制器会处理自己的无效化。
- 负值帧优先级按更新顺序排序，而不会接管渲染。正值的优先级禁用自动渲染：其所有者必须渲染，并且必须与任何 composer 协调。回调按优先级升序运行。
- 不要在 JSX 中重置变换并从另一个所有者动画相同的值。可见性变化不会自动停止回调或释放 GPU 资源。

## 渲染器和所有权陷阱

- 默认 WebGL Canvas 使用 sRGB 输出和 ACES 电影感色调映射。`flat` 选择 `NoToneMapping`；`linear` 更改输出颜色空间。这两者都不是解决资产褪色的通用方法。
- 在 Three.js r182+ 中，使用 `shadows="percentage"` 进行 PCF 阴影。在 Fiber 9 中，`shadows` 在此基线选择已弃用的 `PCFSoftShadowMap`。
- 从默认值开始；仅在确实需要时添加 `preserveDrawingBuffer`、更大的 DPR 或额外的渲染通道，并测量其成本。
- R3F 在卸载时声明式地释放拥有的对象。`<primitive object={...}>` 不会释放提供的对象。缓存的加载器资产和共享资源需要显式所有者；不要在另一个消费者使用它们时释放它们。
- `dispose={null}` 使子树排除自动释放；它不是通用的性能开关。R3F 的所有权范围之外的显式分配资源需要清理。
- 效果、订阅和强制式注册必须在 Strict Mode 设置/清理期间存活。在添加记忆化之前进行性能分析；普通 React 渲染不会自动重启 `useFrame` 动画。

## 验证

进行类型检查、在浏览器中渲染、检查控制台、调整大小，并卸载/重新挂载。对于按需渲染，请验证唤醒和返回空闲状态。

## 来源

- [Fiber 9 迁移](https://github.com/pmndrs/react-three-fiber/blob/v9.7.0/docs/tutorials/v9-migration-guide.mdx) — 版本敏感的类型和渲染器设置。
- [Canvas](https://r3f.docs.pmnd.rs/api/canvas)，[对象和释放](https://r3f.docs.pmnd.rs/api/objects)，[钩子](https://r3f.docs.pmnd.rs/api/hooks)。
- [性能陷阱](https://r3f.docs.pmnd.rs/advanced/pitfalls)，[按需渲染](https://r3f.docs.pmnd.rs/advanced/scaling-performance)。
