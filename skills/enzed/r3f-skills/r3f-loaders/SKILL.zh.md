---
name: r3f-loaders
description: 在 React Three Fiber 中使用 useGLTF、useLoader、Suspense 和预加载来加载和重用 3D 资产。可用于模型加载、解码器设置、缓存、克隆或加载/错误 UI。
---

# React Three Fiber 加载器

首先检查已安装的 Fiber、Drei、Three.js 和 React 版本。示例使用 Fiber 9 / React 19。请验证实际资源路径、节点名称、格式和压缩方式；不要凭空编造模型结构。

## 加载和重用模型

在 Canvas 下方挂载。在应用程序中提供 `/models/robot.glb`。这些克隆具有独立的对象变换，但有意共享缓存的几何体/材质。

```tsx
import { Suspense } from 'react'
import { Clone, useGLTF } from '@react-three/drei'

function Models() {
  const { scene } = useGLTF('/models/robot.glb')
  return (
    <group dispose={null}>
      <Clone object={scene} position={[-1.2, 0, 0]} />
      <Clone object={scene} position={[1.2, 0, 0]} />
    </group>
  )
}

export default function Example() {
  return (
    <Suspense fallback={null}>
      <Models />
    </Suspense>
  )
}
```

## 加载决策

- 对于 glTF/GLB 优先使用 `useGLTF`；对于其他格式使用 `useLoader` 配合对应的 Three.js 加载器。Fiber 9 在需要配置隔离时也接受外部拥有的加载器实例。
- 加载器钩子会挂起。将需要一起显示的资源放在边界内；为独立加载的资源设置独立的边界。在交互前预加载可能需要的资源，而不是整个目录。
- 预加载会发起请求，但不保证即时显示或 GPU 着色器编译。资源解码和首次渲染仍可能耗时。
- 条件加载意味着条件性地挂载调用钩子的子组件。不要传递假 URL 或条件性调用钩子。
- Three.js 插件使用如 `three/addons/loaders/GLTFLoader.js` 的路径。检查已安装的导出以确认重命名后的加载器；现代 Three.js 使用 `HDRLoader` 而非旧示例中的 `RGBELoader`。
- 当暴露命名节点/材质有用时使用 gltfjsx 并查看生成结果。对于包装器使用 `ThreeElements['group']`，而不是已移除的全局 JSX 类型命名空间。

## 缓存、克隆和生命周期

- 将缓存的加载结果视为共享。在两个父级下挂载一个 Object3D 会将其移动；重复放置时克隆图。
- Drei Clone 支持普通图复制和骨骼感知克隆。对于独立动画混合器，稳定的 `SkeletonUtils.clone` 根节点使所有权明确。
- 图克隆通常共享几何体、纹理和材质。在实例化编辑前克隆特定材质/纹理；深度克隆所有内容会浪费内存。
- 防止单个消费者处置共享缓存资源（在共享子树上设置 `dispose={null}`）。应用程序缓存所有者只有在所有消费者消失后才能释放它们。
- 基本元素不会由 R3F 自动处置。`useGLTF.clear(url)` 或 `useLoader.clear(...)` 也不是完整的 GPU 清理操作。
- 渲染期间不要清理缓存，也不要作为本地设置快捷方式修改缓存场景的变换/材质。

## 解码器和失败路径

- `useGLTF` 集成了 Draco/Meshopt 支持，但解码器 URL 和加载器配置必须与资源和托管策略匹配。加载 KTX2 纹理前需配置具有渲染器能力检测的 KTX2Loader。
- 预加载和实际加载使用相同的加载器/解码器设置。在请求开始前配置；后续变更不会回溯解析已缓存的结果。
- 避免在每次渲染或加载回调中创建新的解码器工作池。为自定义加载器/解码器实例指定明确的拥有者和清理逻辑。
- Suspense 处理挂起工作，而非拒绝请求。使用具有明确重试/重挂载策略的错误边界；重试的缓存清除属于用户操作或受控恢复路径。
- 在 Canvas 内使用 Three.js 回退或 Drei Html。Drei Loader 是 DOM 覆盖层，应位于 Canvas 外部。
- `useProgress` 反映加载管理器的活动，而非单个资源精确的字节完成度。避免将不可用的 Content-Length 视为可信的分母。
- 测试网络错误、CORS、解码器/转码器托管和实际压缩资源。未压缩的 GLB 烟测不验证所有解码路径。

## 来源

- [Fiber useLoader](https://r3f.docs.pmnd.rs/api/hooks#useloader), [Drei useGLTF](https://drei.docs.pmnd.rs/loaders/gltf-use-gltf), [Clone](https://drei.docs.pmnd.rs/abstractions/clone).
- [GLTFLoader](https://threejs.org/docs/#GLTFLoader), [KTX2Loader](https://threejs.org/docs/#KTX2Loader), [SkeletonUtils](https://threejs.org/docs/#SkeletonUtils).
