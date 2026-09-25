# React Three Fiber 动画

首先检查已安装的 Fiber、Drei 和 React 版本。这些示例针对 Fiber 9 / React 19。如果项目现有的动画库已经满足需求，请保留它。

## 选择负责人

- 使用 `useFrame` 和引用（refs）进行连续的变换/统一变量；React 状态描述离散目标，如选中、打开或激活。
- 使用 Drei 的 `useAnimations` 处理编写的 GLTF 剪片。阅读 [剪辑播放](references/clips.md) 了解独立动画实例和清理。
- 使用项目的弹簧/缓动库处理协调的过渡；添加前请检查其 React 依赖项。不要为了动画网格而引入状态管理器。
- 让 Rapier 处理模拟身体变换。通过物理 API 动态目标，而不是用网格位置对抗模拟。

## 可返回空闲状态的阻尼

在 Canvas 下挂载；这也适用于 `frameloop="demand"`。点击方框可改变其目标。

```tsx
import { useEffect, useRef, useState } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { MathUtils, type Mesh } from 'three'

export default function Example() {
  const mesh = useRef<Mesh>(null)
  const [active, setActive] = useState(false)
  const invalidate = useThree((state) => state.invalidate)
  const target = active ? 1 : -1
  useEffect(() => { invalidate() }, [target, invalidate])

  useFrame((_, delta) => {
    if (!mesh.current) return
    // 限制视觉过渡的恢复跳跃，而不是物理模拟步骤。
    const x = MathUtils.damp(mesh.current.position.x, target, 6, Math.min(delta, 0.1))
    const moving = Math.abs(x - target) > 0.001
    mesh.current.position.x = moving ? x : target
    if (moving) invalidate()
  })

  return (
    <mesh ref={mesh} name="moving-box" onClick={() => setActive((value) => !value)}>
      <boxGeometry />
      <meshStandardMaterial color={active ? 'orange' : 'coral'} />
    </mesh>
  )
}
```

## 时间和性能

- `delta` 是秒。将速度积分表示为 `position += velocity * delta`；使用 `MathUtils.damp` 或 `1 - exp(-lambda * delta)` 的线性插值进行指数平滑。固定的插值分数取决于刷新率；`delta * speed` 可能会超调。
- 重用向量/四元数；避免每帧分配它们。使用四元数插值进行方向，而不是独立插值欧拉角跨边界。
- 使用一个时间线/时钟所有者。Fiber 9 仍然提供 `state.clock`；不要替换 Fiber 内部，因为 Three.js 已弃用新的独立 `Clock` 实例。对于独立的 Three.js 定时，请咨询已安装版本中的 `Timer`。
- 在按需时，外部动画系统在激活时需要无效化。在开始同步动画前无效化，如果第一帧会跳跃，则在下一帧安排开始。
- 当支持时（例如，商店的 `getState()`），直接在帧回调中读取快速外部状态；仅订阅与 UI 相关的变化。清理外部订阅。
- 不要声称正常 React 重绘会停止动画。在记忆化组件前，分析实际工作和订阅频率。
- 隐藏对象不会停止其帧回调或混合器。在适当的时候显式暂停昂贵的动画；尊重减少运动的偏好。
- 重复振荡和着色器运动可以从经过的时间派生相位；需要可重复性的模拟需要固定步长设计，而不是随意的 delta 限制。

## 验证

比较不同帧率、后台/恢复行为和重复目标变化时的运动。按需时，确认对象唤醒、达到目标并停止请求帧。对于剪辑，测试两个实例播放不同动作。

## 来源

- [Fiber 钩子](https://r3f.docs.pmnd.rs/api/hooks)、[性能陷阱](https://r3f.docs.pmnd.rs/advanced/pitfalls)、[按需渲染](https://r3f.docs.pmnd.rs/advanced/scaling-performance)。
- [MathUtils.damp](https://threejs.org/docs/#MathUtils.damp)、[Drei useAnimations](https://drei.docs.pmnd.rs/abstractions/use-animations)。
