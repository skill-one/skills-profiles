---
name: r3f-postprocessing
description: 配置 React Three Fiber 的后处理效果，包括辉光、选择、环境光遮蔽和景深。用于合成器管线和屏幕空间效果，而不是网格材质着色器。
---

# React Three Fiber 后处理

首先检查实际渲染器和包的 peer 依赖项。本示例针对 Fiber 9.7 / React 19，使用 `@react-three/postprocessing` 3.1 和 `postprocessing` 6.39 在 WebGL 上运行。不要随意组合最新的包版本或无声地升级项目。

## 选择管线

- 此处的 React 后处理合成器适用于 WebGL。Three.js WebGPURenderer 在 r183+ 上使用节点效果和 `RenderPipeline`；请单独验证后端。
- 让一个所有者渲染最终场景。EffectComposer 使用正面的帧优先级；额外的手动 `gl.render` 可以覆盖或复制其输出。
- 普通的 Bloom 可以通过 HDR 阈值隔离亮表面。仅在需要实际对象选择时才使用 SelectiveBloom；它会增加工作量。

## 实际选择对象 bloom

挂载在 Canvas 下方。点击左侧框可切换选择。两个框都很亮，但只有选中的对象会贡献到这个 bloom 遍。

```tsx
import { useMemo, useRef, useState } from 'react'
import { EffectComposer, Select, Selection, SelectiveBloom, ToneMapping } from '@react-three/postprocessing'
import { ToneMappingMode } from 'postprocessing'
import type { DirectionalLight } from 'three'

export default function Example() {
  const light = useRef<DirectionalLight>(null)
  const lights = useMemo(() => [light], [])
  const [selected, setSelected] = useState(true)
  return (
    <Selection>
      <directionalLight ref={light} position={[0, 3, 5]} intensity={2} />
      <Select enabled={selected}>
        <mesh name="bloom-selected" position={[-1.2, 0, 0]} onClick={() => setSelected((value) => !value)}>
          <boxGeometry args={[0.7, 0.7, 0.7]} />
          <meshStandardMaterial color="black" emissive="white" emissiveIntensity={3} />
        </mesh>
      </Select>
      <mesh name="bloom-control" position={[1.2, 0, 0]}>
        <boxGeometry args={[0.7, 0.7, 0.7]} />
        <meshStandardMaterial color="black" emissive="white" emissiveIntensity={3} />
      </mesh>
      <EffectComposer multisampling={0}>
        <SelectiveBloom lights={lights} luminanceThreshold={0} intensity={2} mipmapBlur />
        <ToneMapping mode={ToneMappingMode.ACES_FILMIC} />
      </EffectComposer>
    </Selection>
  )
}
```

## 颜色、选择和引用

- Selection/Select 为支持它的效果（如 Outline 和 SelectiveBloom）提供选择。将普通 Bloom 包裹在 Selection 中并不能让 Bloom 尊重选中的对象。
- 提供 SelectiveBloom 的相关灯光，并保持选择层与其他层使用协调。测试一个同样亮的未选择对象，而不仅仅是暗背景。
- Bloom 在最终色调映射之前基于亮度运行。使用发射/HDR 值和一个有意义的阈值；不要将整个场景扁平化以强制产生辉光。
- 此合成器禁用了渲染器色调映射；使用 ToneMapping 效果以获得预期的最终外观。保持 bloom/HDR 效果在色调映射之前，并避免重复输出转换。
- `ref.current` 变为非空不会触发 React 渲染。不要仅依赖引用分配来阻止效果的初始挂载；在需要反应性对象时使用支持的引用或回调引用状态。

## 深度和特定效果要求

- 此包装器中的 SSAO 需要 `<EffectComposer enableNormalPass>`；仅对需要它们的效应启用额外缓冲区。如果文档和行为不一致，请检查已安装效应的源/类型。
- DepthOfField `target` 是一个世界位置（向量/元组），而不是网格引用。`focusDistance={0}` 不是一个通用的自动对焦开关；使用支持的目标或 Autofocus 辅助程序。
- 某些效应属性接受 Three.js Vector2/Vector3 实例，而不是元组。根据已安装的包装器进行类型检查；不要将 JSX 强制转换假设转移到任意的 React 组件。
- Alpha 混合表面、深度、选择和多采样相互作用。测试实际的透明/透射场景，而不是依赖不透明框截图。

## 性能和自定义效果

- 从少量效应和适度的 DPR/分辨率开始。有意选择抗锯齿策略；避免盲目堆叠 MSAA、SMAA 和 FXAA。
- 效应数量与通道数量并不相同：兼容的效应可以合并。卷积/深度效应和辅助缓冲区仍然可能很昂贵；测量 GPU 成本。
- 优先使用支持的包装器组件。对于自定义后处理 Effect，遵循 `mainImage`/`mainUv`、uniforms、输入缓冲区和效应属性契约；需要 UV 变化的效应需要适当的卷积声明。
- 为自定义 Effect 实例明确分配清理所有权。不要在没有所有者的情况下使用 `dispose={null}`，或从一个消费者处释放共享效应。
- 更新后检查动态属性支持：仅构造设置可能会重新创建效应。不要每帧重建合成器以动画化 uniform。

## 验证

渲染完整管线，切换效应/选择，调整大小，并在 Strict Mode 下卸载/重新挂载。确认仅选择的行为和最终颜色输出；TypeScript 无法证明这两点。

## 来源

- [Selection](https://react-postprocessing.docs.pmnd.rs/selection)，[SelectiveBloom](https://react-postprocessing.docs.pmnd.rs/effects/selective-bloom)，[Bloom](https://react-postprocessing.docs.pmnd.rs/effects/bloom)。
- [已发布的包装器源代码](https://github.com/pmndrs/react-postprocessing/tree/v3.1.1/src) — 合成器、SSAO、引用和目标类型。
- [Postprocessing](https://github.com/pmndrs/postprocessing)，[Three.js 迁移指南](https://github.com/mrdoob/three.js/wiki/Migration-Guide)。
