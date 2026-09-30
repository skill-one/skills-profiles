---
name: r3f-physics
description: 为 React Three Fiber 添加 Rapier 的刚体、碰撞体、力、传感器和关节。用于基于碰撞的运动和模拟；使用动画指导实现纯视觉运动。
---

# React Three Fiber物理

检查已安装的Fiber、React和Rapier版本。Rapier 2针对Fiber 9 / React 19；旧项目需要使用兼容的包版本。保持渲染和模拟的拥有权分离。

## 下落和可点击的物体

在Canvas下方挂载，并包含光照。物理加载WASM是异步的；需要包含Suspense。立方体碰撞器参数是半尺寸，与BoxGeometry的全尺寸不同。

```tsx
import { Suspense, useRef } from 'react'
import { CuboidCollider, Physics, RigidBody, type RapierRigidBody } from '@react-three/rapier'

function FallingBox() {
  const body = useRef<RapierRigidBody>(null)
  return (
    <RigidBody ref={body} position={[0, 2, 0]} colliders="cuboid" restitution={0.2}>
      <mesh name="physics-box" onClick={() => body.current?.applyImpulse({ x: 0, y: 3, z: 0 }, true)}>
        <boxGeometry />
        <meshStandardMaterial color="coral" />
      </mesh>
    </RigidBody>
  )
}

export default function Example() {
  return (
    <Suspense fallback={null}>
      <Physics timeStep={1 / 60}>
        <FallingBox />
        <RigidBody type="fixed" colliders={false}>
          <CuboidCollider args={[4, 0.25, 4]} position={[0, -0.25, 0]} />
          <mesh position={[0, -0.25, 0]}>
            <boxGeometry args={[8, 0.5, 8]} />
            <meshStandardMaterial color="slategray" />
          </mesh>
        </RigidBody>
      </Physics>
    </Suspense>
  )
}
```

## 物体和碰撞器

- 动态物体响应力。固定物体代表静态表面。位置运动学物体使用`setNextKinematicTranslation/Rotation`；速度运动学物体使用线速度/角速度设置器。
- 在RigidBody上设置初始变换。不要在`useFrame`中动画模拟网格的位置；物理世界保持权威性，插值可能覆盖它。
- 优先使用简单碰撞器或复合凸形状。主要使用trimesh来处理静态凹面环境；一个包可以封闭空洞，但不能保留任意凹面。
- 当提供完整的自定义碰撞器时，设置`colliders={false}`，否则可能会添加自动碰撞器。碰撞器尺寸/变换必须与世界比例匹配；使用调试渲染来检查它们。
- 一致地选择碰撞器密度/质量，避免从重叠的自动/自定义碰撞器中意外重复质量。
- 对于许多重复的物体，InstancedRigidBodies减少渲染开销，而不是模拟每个物体的成本。保持实例键/变换稳定。

## 力和模拟时间

- 冲量是一次性的动量变化。力持续到重置；重复的`addForce`调用会累积。不要在没有显式力管理策略的情况下每帧添加相同的持续力。
- 使用`useBeforePhysicsStep`来处理必须与模拟步调对齐的输入/力。如果控制器拥有一个物体上所有的用户力，它可以每步重置并重新应用它们；在重置前与其他力源协调。
- 运动学目标应在物理步进中前进。使用`setTranslation`传送与运动学移动不同，并且可能绕过预期的碰撞响应。
- 优先使用固定步长以获得稳定行为。`timeStep="vary"`用可变步长交换可预测性；乘以渲染增量不会使物理确定性。
- 对于按需渲染，使用`Physics updateLoop="independent"`以便活动物体可以请求渲染。一个休眠的世界不应强制不必要的渲染。
- 让物体休眠；在应用需要它们时显式唤醒它们。当隧道效应值得其成本时，为快速/小物体启用CCD。

## 事件、传感器和关节

- 传感器报告交集进入/退出而不产生接触响应。使用传感器交集事件而不是期望普通碰撞事件。
- 碰撞组需要在两个碰撞器上具有兼容的成员资格/过滤掩码。除非需要格式，否则使用`interactionGroups`而不是手动构建掩码。
- 碰撞有效载荷可能缺少独立碰撞器的rigidBodyObject。安全地检查另一个碰撞器/物体；不要假设每个碰撞都是命名的网格。
- 遵循安装的Rapier回调限制。在接触过滤钩子中，在步骤之前缓存物体状态，而不是在Rust的借用模拟状态期间查询它。
- 关节使用局部锚点和轴连接物体引用，而不是世界坐标。检查钩子的确切元组形状以用于固定、旋转、球形、弹簧或绳索约束。
- 阅读[受控运动和关节](references/controllers.md)以获得与步骤对齐的运动学平台和正确对齐的铰链。
- 碰撞感知的角色控制器与移动网格或设置动态物体的位置是分开的。使用安装的Rapier角色控制器API并测试楼梯/斜坡/接地。
- 恢复世界快照需要匹配物体创建/句柄关系；它不是在现有React引用下方交换任意场景的通用方法。

## 验证

检查静止接触、碰撞器对齐、冲量、休眠/唤醒以及不同的渲染帧率。测试传感器进入/退出、快速体隧道和Strict Mode重新挂载所使用的路径。

## 来源

- [React Three Rapier](https://github.com/pmndrs/react-three-rapier)，[API参考](https://pmndrs.github.io/react-three-rapier/)。
- [Rapier刚体](https://rapier.rs/docs/user_guides/javascript/rigid_bodies)，[碰撞器](https://rapier.rs/docs/user_guides/javascript/colliders)，[角色控制器](https://rapier.rs/docs/user_guides/javascript/character_controller)。
