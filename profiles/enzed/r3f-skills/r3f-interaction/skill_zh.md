# React Three Fiber 交互

首先检查已安装的 Fiber、Drei 和输入库的版本。示例针对 Fiber 9 / React 19。在连接处理程序之前，选择相机移动、对象移动和 UI 输入所有者。

## 可选择对象

在 Canvas 下方挂载。将重要的操作的可访问 DOM 控件保持在 Canvas 外部；仅使用网格指针处理程序无法提供键盘访问。

```tsx
import { useState } from 'react'
import { OrbitControls } from '@react-three/drei'

export default function Example() {
  const [selected, setSelected] = useState(false)
  return (
    <>
      <mesh
        name="selectable-box"
        onClick={(event) => {
          event.stopPropagation()
          setSelected((value) => !value)
        }}
      >
        <boxGeometry />
        <meshStandardMaterial color={selected ? 'gold' : 'coral'} />
      </mesh>
      <OrbitControls makeDefault />
    </>
  )
}
```

## 事件语义

- R3F 使用射线投射对象并处理带有处理程序的物体，按距离递送命中，然后通过祖先节点冒泡。`event.object` 是命中对象；`event.eventObject` 是拥有处理程序的对象。
- `stopPropagation()` 会阻止向更远的命中以及祖先节点传递。它会改变事件传递方式；它不会避免已经执行的射线投射。调用它可以立即触发命中背后先前悬停对象的 pointerout。
- `event.point` 是世界空间。在保留值之前克隆它们，并转换为父级的本地空间再分配本地变换。需要平面交点或深度参考将 2D 拖拽映射到 3D。
- 处理 Canvas 的 `onPointerMissed` 以实现背景取消选择；使用事件的运动信息和应用的手势策略区分点击和拖拽。
- 指针捕获在 R3F 中是命中测试的附加功能。通过 `event.target.setPointerCapture(event.pointerId)` 和匹配的释放方法进行捕获/释放；同时处理取消/丢失捕获。
- 相机在静止指针下方移动可能需要 `state.events.update()` 以刷新悬停结果。仅在需要时调用它，而不是每帧都进行额外的射线投射。
- 对于昂贵的拾取，使用更简单的命中代理或层过滤。不要仅依赖视觉透明度来防止相交。

## 控制和拖拽所有权

- 使用 OrbitControls 进行环绕；当需要脚本过渡和更丰富的相机行为时使用 CameraControls。在复制属性或方法之前检查已安装的 Drei/底层控制版本。
- Drei 控制程序管理帧更新并要求失效。避免在同一个相机上挂载多个活动的控制程序而没有明确的协调。
- `makeDefault` 会向与之协调的辅助程序暴露控制实例。TransformControls 在拖拽时可以暂停默认控制；验证自定义控制是否正确禁用/恢复。
- 对于对象拖拽，根据所需的约束选择 Drei DragControls/PivotControls/TransformControls。区分受控矩阵和自动变换；不要将两者同时应用于同一对象。
- 对于自定义拖拽，存储初始变换，捕获指针，投影到选定平面，并在 pointerup、取消和卸载时恢复相机控制。在实际事件目标上尊重 touch-action 要求。
- 共享的 DOM 事件源需要一个与事件目标和画布矩形一致的坐标前缀。测试滚动和覆盖层；盲目选择 `client` 坐标可能会引入偏移。

## 键盘和连续输入

- Drei KeyboardControls 提供命名动作。在 `useFrame` 内部读取其 getter 以实现移动；仅订阅离散事件并清理订阅。
- 如果速度必须保持恒定，请规范化对角线移动；将视觉移动乘以 delta。对于物理体，将输入发送到物理步进逻辑，而不是直接移动其网格。
- 在失去焦点时清除持有的输入并尊重文本字段焦点。指针锁定/全屏/音频可能需要明确用户手势。
- 使用 refs 存储高频指针位置，使用 React state 存储语义事件。避免仅为了节流一个处理程序而添加 lodash 或存储；如果需要节流，请清理计时器。
- ScrollControls 创建一个滚动上下文；`useScroll` 属于其下方。其规范化偏移/增量不是像素距离。

## 验证

测试重叠网格、嵌套组、背景取消选择、画布外拖拽、触摸、取消、失去焦点和键盘替代方案。验证相机控制在拖拽后恢复。

## 来源

- [Fiber 事件](https://r3f.docs.pmnd.rs/api/events), [Drei 控制程序](https://drei.docs.pmnd.rs/controls/introduction).
- [DragControls](https://drei.docs.pmnd.rs/gizmos/drag-controls), [KeyboardControls](https://drei.docs.pmnd.rs/controls/keyboard-controls), [ScrollControls](https://drei.docs.pmnd.rs/controls/scroll-controls).
