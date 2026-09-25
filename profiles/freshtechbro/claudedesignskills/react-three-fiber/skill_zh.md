# React Three Fiber

## 概述

React Three Fiber (R3F) 是一个用于 Three.js 的 React 渲染器，它将声明式、基于组件的 3D 开发带到 React 应用程序中。与命令式地创建和管理 Three.js 对象不同，您使用 JSX 组件构建 3D 场景，这些组件直接映射到 Three.js 对象。

**何时使用此技能**：
- 在 React 应用程序中构建 3D 体验
- 创建交互式产品配置器或展示
- 开发 3D 作品集、画廊或故事讲述体验
- 在 React 中构建游戏或模拟
- 向现有的 React 项目添加 3D 元素
- 当您需要使用 3D 图形进行状态管理和 React 钩子时
- 当您正在使用 React 框架（Next.js、Gatsby、Remix）时

**主要优势**：
- **声明式**：像 React 组件一样编写 3D 场景
- **React 集成**：完全访问钩子、上下文、状态管理
- **可重用性**：创建和共享 3D 组件库
- **性能**：自动渲染优化和调和
- **生态系统**：可与 Drei 辅助程序、Zustand、Framer Motion 等配合使用
- **TypeScript 支持**：Three.js 对象的完整类型安全

---

## 核心概念

### 1. Canvas 组件

`<Canvas>` 组件设置 Three.js 场景、相机、渲染器和渲染循环。

```jsx
import { Canvas } from '@react-three/fiber'

function App() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 75 }}
      gl={{ antialias: true }}
      dpr={[1, 2]}
    >
      {/* 3D 内容放在这里 */}
    </Canvas>
  )
}
```

**Canvas 属性**：
- `camera` - 相机配置（位置、fov、near、far）
- `gl` - WebGL 渲染器设置
- `dpr` - 设备像素比（默认：[1, 2]）
- `shadows` - 启用阴影映射（默认：false）
- `frameloop` - "always"（默认）、"demand" 或 "never"
- `flat` - 禁用颜色管理以获得更简单的颜色
- `linear` - 使用线性颜色空间而不是 sRGB

### 2. 声明式 3D 对象

使用 kebab-case 属性的 JSX 创建 Three.js 对象：

```jsx
// THREE.Mesh + THREE.BoxGeometry + THREE.MeshStandardMaterial
<mesh position={[0, 0, 0]} rotation={[0, Math.PI / 4, 0]}>
  <boxGeometry args={[1, 1, 1]} />
  <meshStandardMaterial color="hotpink" />
</mesh>
```

**属性映射**：
- `position` → `object.position.set(x, y, z)`
- `rotation` → `object.rotation.set(x, y, z)`
- `scale` → `object.scale.set(x, y, z)`
- `args` → 几何体/材质的构造函数参数
- `attach` → 附加到父属性（例如，`attach="material"`）

**简写符号**：
```jsx
// 完整符号
<mesh position={[1, 2, 3]} />

// 指定轴的（短横线符号）
<mesh position-x={1} position-y={2} position-z={3} />
```

### 3. useFrame 钩子

在每个帧（动画循环）上执行代码：

```jsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function RotatingBox() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    // 每个帧旋转网格
    meshRef.current.rotation.x += delta
    meshRef.current.rotation.y += delta * 0.5

    // 访问场景状态
    const time = state.clock.elapsedTime
    meshRef.current.position.y = Math.sin(time) * 2
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

**useFrame 参数**：
- `state` - 场景状态（相机、场景、gl、时钟等）
- `delta` - 自上次帧以来的时间（用于帧率独立性）
- `xrFrame` - XR 帧数据（用于 VR/AR）

**重要**：切勿在 `useFrame` 内部使用 `setState` - 它会导致不必要的重新渲染！

### 4. useThree 钩子

访问场景状态和方法：

```jsx
import { useThree } from '@react-three/fiber'

function CameraInfo() {
  const { camera, gl, scene, size, viewport } = useThree()

  // 选择性订阅（仅在大小变化时重新渲染）
  const size = useThree((state) => state.size)

  // 非反应式地获取状态
  const get = useThree((state) => state.get)
  const freshState = get() // 最新状态而不会触发重新渲染

  return null
}
```

**可用状态**：
- `camera` - 默认相机
- `scene` - Three.js 场景
- `gl` - WebGL 渲染器
- `size` - 画布尺寸
- `viewport` - 3D 单位中的视口尺寸
- `clock` - Three.js 时钟
- `pointer` - 归一化的鼠标坐标
- `invalidate()` - 手动触发渲染
- `setSize()` - 手动调整画布大小

### 5. useLoader 钩子

加载资源并自动集成 Suspense：

```jsx
import { Suspense } from 'react'
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { TextureLoader } from 'three'

function Model() {
  const gltf = useLoader(GLTFLoader, '/model.glb')
  return <primitive object={gltf.scene} />
}

function TexturedMesh() {
  const texture = useLoader(TextureLoader, '/texture.jpg')
  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}

function App() {
  return (
    <Canvas>
      <Suspense fallback={<LoadingIndicator />}>
        <Model />
        <TexturedMesh />
      </Suspense>
    </Canvas>
  )
}
```

**加载多个资源**：
```jsx
const [texture1, texture2, texture3] = useLoader(TextureLoader, [
  '/tex1.jpg',
  '/tex2.jpg',
  '/tex3.jpg'
])
```

**加载器扩展**：
```jsx
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'

useLoader(GLTFLoader, '/model.glb', (loader) => {
  const dracoLoader = new DRACOLoader()
  dracoLoader.setDecoderPath('/draco/')
  loader.setDRACOLoader(dracoLoader)
})
```

**预加载**：
```jsx
// 在组件挂载前预加载资源
useLoader.preload(GLTFLoader, '/model.glb')
```

---

## 常见模式

### 模式 1：基本场景设置

```jsx
import { Canvas } from '@react-three/fiber'

function Scene() {
  return (
    <>
      {/* 灯光 */}
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />

      {/* 对象 */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="hotpink" />
      </mesh>
    </>
  )
}

function App() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
      <Scene />
    </Canvas>
  )
}
```

### 模式 2：交互式对象（点击、悬停）

```jsx
import { useState } from 'react'

function InteractiveBox() {
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)

  return (
    <mesh
      scale={active ? 1.5 : 1}
      onClick={() => setActive(!active)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

### 模式 3：使用 useFrame 的动画组件

```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function AnimatedSphere() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    // 旋转
    meshRef.current.rotation.y += delta

    // 振荡位置
    const time = state.clock.elapsedTime
    meshRef.current.position.y = Math.sin(time) * 2
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="cyan" />
    </mesh>
  )
}
```

### 模式 4：加载 GLTF 模型

```jsx
import { Suspense } from 'react'
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

function Model({ url }) {
  const gltf = useLoader(GLTFLoader, url)

  return (
    <primitive
      object={gltf.scene}
      scale={0.5}
      position={[0, 0, 0]}
    />
  )
}

function App() {
  return (
    <Canvas>
      <Suspense fallback={<LoadingPlaceholder />}>
        <Model url="/model.glb" />
      </Suspense>
    </Canvas>
  )
}

function LoadingPlaceholder() {
  return (
    <mesh>
      <boxGeometry />
      <meshBasicMaterial wireframe />
    </mesh>
  )
}
```

### 模式 5：多个灯光

```jsx
function Lighting() {
  return (
    <>
      {/* 环境光用于基础照明 */}
      <ambientLight intensity={0.3} />

      {/* 带阴影的方向光 */}
      <directionalLight
        position={[5, 5, 5]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />

      {/* 点光用于强调 */}
      <pointLight position={[-5, 5, -5]} intensity={0.5} color="blue" />

      {/* 聚焦照明的聚光灯 */}
      <spotLight
        position={[10, 10, 10]}
        angle={0.3}
        penumbra={1}
        intensity={1}
      />
    </>
  )
}
```

### 模式 6：实例化（许多对象）

```jsx
import { useMemo, useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'

function Particles({ count = 1000 }) {
  const meshRef = useRef()

  // 生成随机位置
  const particles = useMemo(() => {
    const temp = []
    for (let i = 0; i < count; i++) {
      const t = Math.random() * 100
      const factor = 20 + Math.random() * 100
      const speed = 0.01 + Math.random() / 200
      const x = Math.random() * 2 - 1
      const y = Math.random() * 2 - 1
      const z = Math.random() * 2 - 1
      temp.push({ t, factor, speed, x, y, z, mx: 0, my: 0 })
    }
    return temp
  }, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  useFrame(() => {
    particles.forEach((particle, i) => {
      let { t, factor, speed, x, y, z } = particle
      t = particle.t += speed / 2
      const a = Math.cos(t) + Math.sin(t * 1) / 10
      const b = Math.sin(t) + Math.cos(t * 2) / 10
      const s = Math.cos(t)

      dummy.position.set(
        x + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        y + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        z + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      )
      dummy.scale.set(s, s, s)
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)
    })
    meshRef.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshBasicMaterial color="white" />
    </instancedMesh>
  )
}
```

### 模式 7：组和嵌套

```jsx
function Robot() {
  return (
    <group position={[0, 0, 0]}>
      {/* 身体 */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 2, 1]} />
        <meshStandardMaterial color="gray" />
      </mesh>

      {/* 头部 */}
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial color="silver" />
      </mesh>

      {/* 手臂 */}
      <group position={[-0.75, 0.5, 0]}>
        <mesh>
          <cylinderGeometry args={[0.1, 0.1, 1.5]} />
          <meshStandardMaterial color="darkgray" />
        </mesh>
      </group>

      <group position={[0.75, 0.5, 0]}>
        <mesh>
          <cylinderGeometry args={[0.1, 0.1, 1.5]} />
          <meshStandardMaterial color="darkgray" />
        </mesh>
      </group>
    </group>
  )
}
```

---

## 与 Drei 辅助程序集成

[Drei](https://github.com/pmndrs/drei) 是 R3F 的必备辅助库，提供现成的组件：

### OrbitControls

```jsx
import { OrbitControls } from '@react-three/drei'

<Canvas>
  <OrbitControls
    makeDefault
    enableDamping
    dampingFactor={0.05}
    minDistance={3}
    maxDistance={20}
  />
  <Box />
</Canvas>
```

### 环境 & 灯光

```jsx
import { Environment, ContactShadows } from '@react-three/drei'

<Canvas>
  {/* HDRI 环境贴图 */}
  <Environment preset="sunset" />

  {/* 或自定义 */}
  <Environment files="/hdri.hdr" />

  {/* 柔和接触阴影 */}
  <ContactShadows
    opacity={0.5}
    scale={10}
    blur={1}
    far={10}
    resolution={256}
  />

  <Model />
</Canvas>
```

### 文本

```jsx
import { Text, Text3D } from '@react-three/drei'

// 2D Billboard 文本
<Text
  position={[0, 2, 0]}
  fontSize={1}
  color="white"
  anchorX="center"
  anchorY="middle"
>
  Hello World
</Text>

// 3D 拉伸文本
<Text3D
  font="/fonts/helvetiker_regular.typeface.json"
  size={1}
  height={0.2}
>
  3D Text
  <meshNormalMaterial />
</Text3D>
```

### useGLTF 钩子（Drei）

```jsx
import { useGLTF } from '@react-three/drei'

function Model() {
  const { scene, materials, nodes } = useGLTF('/model.glb')

  return <primitive object={scene} />
}

// 预加载
useGLTF.preload('/model.glb')
```

### Center & Bounds

```jsx
import { Center, Bounds, useBounds } from '@react-three/drei'

// 自动居中对象
<Center>
  <Model />
</Center>

// 自动适配相机到边界
<Bounds fit clip observe margin={1.2}>
  <Model />
</Bounds>
```

### HTML 叠加层

```jsx
import { Html } from '@react-three/drei'

<mesh>
  <boxGeometry />
  <meshStandardMaterial />

  <Html
    position={[0, 1, 0]}
    center
    distanceFactor={10}
  >
    <div className="annotation">
      这是一个盒子
    </div>
  </Html>
</mesh>
```

### 滚动控制

```jsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function AnimatedScene() {
  const scroll = useScroll()
  const meshRef = useRef()

  useFrame(() => {
    const offset = scroll.offset // 0-1 归一化滚动位置
    meshRef.current.position.y = offset * 10
  })

  return <mesh ref={meshRef}>...</mesh>
}

<Canvas>
  <ScrollControls pages={3} damping={0.5}>
    <Scroll>
      <AnimatedScene />
    </Scroll>

    {/* HTML 叠加层 */}
    <Scroll html>
      <div style={{ height: '100vh' }}>
        <h1>可滚动的内容</h1>
      </div>
    </Scroll>
  </ScrollControls>
</Canvas>
```

---

## 与其他库集成

### 与 GSAP

```jsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import gsap from 'gsap'

function AnimatedBox() {
  const meshRef = useRef()

  useEffect(() => {
    // GSAP 时间轴动画
    const tl = gsap.timeline({ repeat: -1, yoyo: true })

    tl.to(meshRef.current.position, {
      y: 2,
      duration: 1,
      ease: 'power2.inOut'
    })
    .to(meshRef.current.rotation, {
      y: Math.PI * 2,
      duration: 2,
      ease: 'none'
    }, 0)

    return () => tl.kill()
  }, [])

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

### 与 Framer Motion

```jsx
import { motion } from 'framer-motion-3d'

function AnimatedSphere() {
  return (
    <motion.mesh
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 1 }}
    >
      <sphereGeometry />
      <meshStandardMaterial color="hotpink" />
    </motion.mesh>
  )
}
```

### 与 Zustand（状态管理）

```jsx
import create from 'zustand'

const useStore = create((set) => ({
  color: 'orange',
  setColor: (color) => set({ color })
}))

function Box() {
  const color = useStore((state) => state.color)
  const setColor = useStore((state) => state.setColor)

  return (
    <mesh onClick={() => setColor('hotpink')}>
      <boxGeometry />
      <meshStandardMaterial color={color} />
    </mesh>
  )
}
```

---

## 性能优化

### 1. 按需渲染

```jsx
<Canvas frameloop="demand">
  {/* 仅在需要时渲染 */}
</Canvas>

// 手动触发渲染
function MyComponent() {
  const invalidate = useThree((state) => state.invalidate)

  return (
    <mesh onClick={() => invalidate()}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### 2. 实例化

使用 `<instancedMesh>` 渲染许多相同的对象：

```jsx
function Particles({ count = 10000 }) {
  const meshRef = useRef()

  useEffect(() => {
    const temp = new THREE.Object3D()

    for (let i = 0; i < count; i++) {
      temp.position.set(
        Math.random() * 10 - 5,
        Math.random() * 10 - 5,
        Math.random() * 10 - 5
      )
      temp.updateMatrix()
      meshRef.current.setMatrixAt(i, temp.matrix)
    }

    meshRef.current.instanceMatrix.needsUpdate = true
  }, [count])

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshBasicMaterial color="white" />
    </instancedMesh>
  )
}
```

### 3. 视锥剔除

相机视图外的对象会自动剔除。

```jsx
// 禁用始终可见的对象
<mesh frustumCulled={false}>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>
```

### 4. 细节层次（LOD）

```jsx
import { Detailed } from '@react-three/drei'

<Detailed distances={[0, 10, 20]}>
  {/* 近距离时的高细节 */}
  <mesh geometry={highPolyGeometry} />

  {/* 中等细节 */}
  <mesh geometry={mediumPolyGeometry} />

  {/* 远距离时的低细节 */}
  <mesh geometry={lowPolyGeometry} />
</Detailed>
```

### 5. 自适应性能

```jsx
import { AdaptiveDpr, AdaptiveEvents, PerformanceMonitor } from '@react-three/drei'

<Canvas>
  {/* 当性能下降时减少 DPR */}
  <AdaptiveDpr pixelated />

  {/* 减少射线投射频率 */}
  <AdaptiveEvents />

  {/* 监控并响应性能 */}
  <PerformanceMonitor
    onIncline={() => console.log('性能提升')}
    onDecline={() => console.log('性能下降')}
  >
    <Scene />
  </PerformanceMonitor>
</Canvas>
```

### 6. 选择性重新渲染

使用 `useThree` 选择器避免不必要的重新渲染：

```jsx
// ❌ 不良：任何状态变化都会重新渲染
const state = useThree()

// ✅ 仅在大小变化时重新渲染
const size = useThree((state) => state.size)

// ✅ 仅在相机变化时重新渲染
const camera = useThree((state) => state.camera)
```

---

## 常见陷阱和解决方案

### ❌ 陷阱 1：在 useFrame 中使用 setState

```jsx
// ❌ 不良：每帧触发 React 重新渲染
const [x, setX] = useState(0)
useFrame(() => setX((x) => x + 0.1))
return <mesh position-x={x} />
```

✅ **解决方案**：直接修改引用

```jsx
// ✅ 好：直接修改，不重新渲染
const meshRef = useRef()
useFrame((state, delta) => {
  meshRef.current.position.x += delta
})
return <mesh ref={meshRef} />
```

### ❌ 陷阱 2：在渲染中创建对象

```jsx
// ❌ 不良：每渲染都创建新的 Vector3
<mesh position={new THREE.Vector3(1, 2, 3)} />
```

✅ **解决方案**：使用数组或 useMemo

```jsx
// ✅ 好：使用数组符号
<mesh position={[1, 2, 3]} />

// 或 useMemo 用于复杂对象
const position = useMemo(() => new THREE.Vector3(1, 2, 3), [])
<mesh position={position} />
```

### ❌ 陷阱 3：不使用 useLoader 缓存

```jsx
// ❌ 不良：每渲染都加载纹理
function Component() {
  const [texture, setTexture] = useState()
  useEffect(() => {
    new TextureLoader().load('/texture.jpg', setTexture)
  }, [])
  return texture ? <meshBasicMaterial map={texture} /> : null
}
```

✅ **解决方案**：使用 useLoader（自动缓存）

```jsx
// ✅ 好：缓存并重用
function Component() {
  const texture = useLoader(TextureLoader, '/texture.jpg')
  return <meshBasicMaterial map={texture} />
}
```

### ❌ 陷阱 4：条件挂载（昂贵）

```jsx
// ❌ 不良：卸载和重新挂载（昂贵）
{stage === 1 && <Stage1 />}
{stage === 2 && <Stage2 />}
{stage === 3 && <Stage3 />}
```

✅ **解决方案**：使用可见性属性

```jsx
// ✅ 好：组件保持挂载，只是隐藏
<Stage1 visible={stage === 1} />
<Stage2 visible={stage === 2} />
<Stage3 visible={stage === 3} />

function Stage1({ visible, ...props }) {
  return <group {...props} visible={visible}>...</group>
}
```

### ❌ 陷阱 5：在 Canvas 外部使用 useThree

```jsx
// ❌ 不良：使用 Three.js 对象崩溃 - useThree 必须在 Canvas 内部
function App() {
  const { size } = useThree()
  return <Canvas>...</Canvas>
}
```

✅ **解决方案**：在 Canvas 子元素内使用钩子

```jsx
// ✅ 好：在 Canvas 子元素内使用 useThree
function CameraInfo() {
  const { size } = useThree()
  return null
}

function App() {
  return (
    <Canvas>
      <CameraInfo />
    </Canvas>
  )
}
```

### ❌ 陷阱 6：不释放资源

```jsx
// ❌ 不良：内存泄漏 - 纹理未释放
const texture = useLoader(TextureLoader, '/texture.jpg')
```

✅ **解决方案**：R3F 自动处理资源释放，但要注意手动 Three.js 对象

```jsx
// ✅ 好：当需要时手动清理
useEffect(() => {
  const geometry = new THREE.SphereGeometry(1)
  const material = new THREE.MeshBasicMaterial()

  return () => {
    geometry.dispose()
    material.dispose()
  }
}, [])
```

---

## 最佳实践

### 1. 组件组合

将场景分解为可重用的组件：

```jsx
function Lights() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} />
    </>
  )
}

function Scene() {
  return (
    <>
      <Lights />
      <Model />
      <Ground />
      <Effects />
    </>
  )
}

<Canvas>
  <Scene />
</Canvas>
```

### 2. 暂停加载重型资源

始终用 Suspense 包裹异步操作：

```jsx
<Canvas>
  <Suspense fallback={<Loader />}>
    <Model />
    <Environment />
  </Suspense>
</Canvas>
```

### 3. 使用 TypeScript

```typescript
import { ThreeElements } from '@react-three/fiber'

function Box(props: ThreeElements['mesh']) {
  return (
    <mesh {...props}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### 4. 按功能组织

```
src/
  components/
    3d/
      Scene.tsx
      Lights.tsx
      Camera.tsx
    models/
      Robot.tsx
      Character.tsx
    effects/
      PostProcessing.tsx
```

### 5. 使用 React DevTools Profiler 进行测试

监控重新渲染并优化导致性能问题的组件。

---

## 资源

### 参考
- `references/api_reference.md` - 完整 R3F & Drei API 文档
- `references/hooks_guide.md` - 详细钩子使用和模式
- `references/drei_helpers.md` - 全面 Drei 库指南

### 脚本
- `scripts/component_generator.py` - 生成 R3F 组件模板
- `scripts/scene_setup.py` - 使用常见模式初始化 R3F 场景

### 资产
- `assets/starter_r3f/` - 完整 R3F + Vite 启动模板
- `assets/examples/` - 真实世界的 R3F 组件示例

### 外部资源
- [官方文档](https://docs.pmnd.rs/react-three-fiber)
- [Drei 文档](https://github.com/pmndrs/drei)
- [Three.js 文档](https://threejs.org/docs/)
- [R3F Discord](https://discord.gg/ZZjjNvJ)
- [Poimandres (pmnd.rs)](https://pmnd.rs/) - 生态系统概述
