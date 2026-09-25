# Web 3D 集成模式

## 概述

这项元技能提供了将多个 3D 和动画库结合到 Web 应用中的架构模式、最佳实践和集成策略。它综合了 threejs-webgl、gsap-scrolltrigger、react-three-fiber、motion-framer 和 react-spring-physics 技能的知识，形成连贯的模式，用于构建复杂、高性能的 3D Web 体验。

**何时使用此技能：**
- 构建 结合多个库的复杂 3D 应用
- 创建 带动画编排的滚动驱动 3D 体验
- 实现 基于物理的 3D 场景交互
- 跨 3D 渲染和 UI 动画管理状态
- 优化 多库架构中的性能
- 设计 3D 应用可重用组件架构
- 在动画方法之间迁移或组合

**核心集成组合：**
1. **Three.js + GSAP** - 滚动驱动 3D 动画，时间轴编排
2. **React Three Fiber + Motion** - 基于状态的 3D 与声明式动画
3. **React Three Fiber + GSAP** - React 中的复杂 3D 序列
4. **React Three Fiber + React Spring** - 基于物理的 3D 交互
5. **Three.js + GSAP + React** - 混合命令式/声明式 3D

## 架构模式

### 模式 1：分层分离（Three.js + GSAP + React UI）

**用例：** 带有覆盖 UI 的 3D 场景，滚动驱动动画

**架构：**
```
├── 3D 层 (Three.js)
│   ├── 场景管理
│   ├── 相机控制
│   └── 渲染循环
├── 动画层 (GSAP)
│   ├── 用于 3D 属性的 ScrollTrigger
│   ├── 用于序列的时间轴
│   └── UI 过渡
└── UI 层 (React + Motion)
    ├── HTML 覆盖层
    ├── 状态管理
    └── 用户交互
```

**实现：**

```javascript
// App.jsx - React 根组件
import { useEffect, useRef } from 'react'
import { initThreeScene } from './three/scene'
import { initScrollAnimations } from './animations/scroll'
import { motion } from 'framer-motion'

function App() {
  const canvasRef = useRef()
  const sceneRef = useRef()

  useEffect(() => {
    // 初始化 Three.js 场景
    sceneRef.current = initThreeScene(canvasRef.current)

    // 初始化 GSAP ScrollTrigger 动画
    initScrollAnimations(sceneRef.current)

    // 清理
    return () => {
      sceneRef.current.dispose()
    }
  }, [])

  return (
    <div className="app">
      <canvas ref={canvasRef} />

      <motion.div
        className="overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <section className="hero">
          <h1>3D 体验</h1>
        </section>
        <section className="content">
          {/* 可滚动的内容 */}
        </section>
      </motion.div>
    </div>
  )
}
```

```javascript
// three/scene.js - Three.js 设置
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

export function initThreeScene(canvas) {
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })

  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  const controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true

  // 设置场景对象
  const geometry = new THREE.BoxGeometry(2, 2, 2)
  const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  const cube = new THREE.Mesh(geometry, material)
  scene.add(cube)

  // 灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
  directionalLight.position.set(5, 10, 7.5)
  scene.add(directionalLight)

  camera.position.set(0, 2, 5)

  // 动画循环
  function animate() {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  // 调整大小处理程序
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  })

  return { scene, camera, renderer, cube }
}
```

```javascript
// animations/scroll.js - GSAP ScrollTrigger 集成
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function initScrollAnimations(sceneRefs) {
  const { camera, cube } = sceneRefs

  // 滚动时动画相机
  gsap.to(camera.position, {
    x: 5,
    y: 3,
    z: 10,
    scrollTrigger: {
      trigger: '.content',
      start: 'top top',
      end: 'bottom center',
      scrub: 1,
      onUpdate: () => camera.lookAt(cube.position)
    }
  })

  // 动画网格旋转
  gsap.to(cube.rotation, {
    y: Math.PI * 2,
    x: Math.PI,
    scrollTrigger: {
      trigger: '.content',
      start: 'top bottom',
      end: 'bottom top',
      scrub: true
    }
  })

  // 动画材质属性
  gsap.to(cube.material, {
    opacity: 0.3,
    scrollTrigger: {
      trigger: '.content',
      start: 'top center',
      end: 'center center',
      scrub: 1
    }
  })
}
```

**优点：**
- 清晰的关注点分离
- 易于理解数据流
- 每层性能优化
- 层级独立测试

**权衡：**
- 更多样板代码
- 层级之间手动同步
- 状态管理复杂性

---

### 模式 2：统一 React 组件（React Three Fiber + Motion）

**用例：** 带有声明式 3D 和动画的 React 首先架构

**架构：**
```
React 组件树
├── <Canvas> (R3F)
│   ├── 3D 场景组件
│   ├── 灯光
│   ├── 相机
│   └── 特效
└── <motion.div> (UI 覆盖层)
    ├── HTML 内容
    └── 动画
```

**实现：**

```jsx
// App.jsx - 统一的 React 方法
import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import { motion } from 'framer-motion'
import { Scene } from './components/Scene'
import { Loader } from './components/Loader'

function App() {
  return (
    <div className="app">
      <Canvas
        camera={{ position: [0, 2, 5], fov: 75 }}
        dpr={[1, 2]}
        shadows
      >
        <Suspense fallback={<Loader />}>
          <Scene />
        </Suspense>
      </Canvas>

      <motion.div
        className="ui-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <h1>React-First 3D 体验</h1>
      </motion.div>
    </div>
  )
}
```

```jsx
// components/Scene.jsx - R3F 场景
import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'
import { motion } from 'framer-motion-3d'

export function Scene() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 7.5]} castShadow />

      <AnimatedCube />
      <Floor />

      <OrbitControls enableDamping dampingFactor={0.05} />
      <Environment preset="sunset" />
    </>
  )
}

function AnimatedCube() {
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)

  return (
    <motion.mesh
      scale={active ? 1.5 : 1}
      onClick={() => setActive(!active)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      animate={{
        rotateY: hovered ? Math.PI * 2 : 0
      }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
    >
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </motion.mesh>
  )
}

function Floor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]} receiveShadow>
      <planeGeometry args={[100, 100]} />
      <meshStandardMaterial color="#222" />
    </mesh>
  )
}
```

**优点：**
- 声明式，React 首先方法
- 统一状态管理
- 组件可重用性
- 使用 React 工具易于测试

**权衡：**
- R3F 学习曲线
- 对渲染循环控制较少
- 潜在的 React 重新渲染问题

---

### 模式 3：混合方法（R3F + GSAP 时间轴）

**用例：** 复杂动画序列与 React 状态管理

**实现：**

```jsx
// components/AnimatedScene.jsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import gsap from 'gsap'

export function AnimatedScene() {
  const groupRef = useRef()
  const timelineRef = useRef()

  useEffect(() => {
    // 创建 GSAP 时间轴用于复杂序列
    const tl = gsap.timeline({ repeat: -1, yoyo: true })

    tl.to(groupRef.current.position, {
      y: 2,
      duration: 1,
      ease: 'power2.inOut'
    })
    .to(groupRef.current.rotation, {
      y: Math.PI * 2,
      duration: 2,
      ease: 'none'
    }, 0) // 同时开始

    timelineRef.current = tl

    return () => tl.kill()
  }, [])

  return (
    <group ref={groupRef}>
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="cyan" />
      </mesh>
    </group>
  )
}
```

---

### 模式 4：基于物理的 3D（R3F + React Spring）

**用例：** 自然、基于物理的 3D 交互

**实现：**

```jsx
// components/PhysicsCube.jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useSpring, animated, config } from '@react-spring/three'

const AnimatedMesh = animated('mesh')

export function PhysicsCube() {
  const [springs, api] = useSpring(() => ({
    scale: 1,
    position: [0, 0, 0],
    config: config.wobbly
  }), [])

  const handleClick = () => {
    api.start({
      scale: 1.5,
      position: [0, 2, 0]
    })

    // 延迟后返回原始状态
    setTimeout(() => {
      api.start({
        scale: 1,
        position: [0, 0, 0]
      })
    }, 1000)
  }

  return (
    <AnimatedMesh
      scale={springs.scale}
      position={springs.position}
      onClick={handleClick}
    >
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </AnimatedMesh>
  )
}
```

---

## 常见集成模式

### 1. 滚动驱动相机移动

**Three.js + GSAP:**

```javascript
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// 平滑相机路径通过多个点
const cameraPath = [
  { x: 0, y: 2, z: 5, lookAt: { x: 0, y: 0, z: 0 } },
  { x: 5, y: 3, z: 10, lookAt: { x: 0, y: 0, z: 0 } },
  { x: -3, y: 1, z: 8, lookAt: { x: 0, y: 0, z: 0 } }
]

const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#container',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1,
    pin: true
  }
})

cameraPath.forEach((point, i) => {
  tl.to(camera.position, {
    x: point.x,
    y: point.y,
    z: point.z,
    duration: 1,
    onUpdate: () => camera.lookAt(point.lookAt.x, point.lookAt.y, point.lookAt.z)
  }, i)
})
```

**R3F + ScrollControls (Drei):**

```jsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function CameraRig() {
  const scroll = useScroll()

  useFrame((state) => {
    const offset = scroll.offset

    state.camera.position.x = Math.sin(offset * Math.PI * 2) * 5
    state.camera.position.z = Math.cos(offset * Math.PI * 2) * 5
    state.camera.lookAt(0, 0, 0)
  })

  return null
}

export function App() {
  return (
    <Canvas>
      <ScrollControls pages={3} damping={0.5}>
        <CameraRig />
        <Scroll>
          <Scene />
        </Scroll>
      </ScrollControls>
    </Canvas>
  )
}
```

### 2. 手势驱动 3D 操作

**R3F + Motion (Framer Motion 3D):**

```jsx
import { motion } from 'framer-motion-3d'

function DraggableObject() {
  return (
    <motion.mesh
      drag
      dragElastic={0.1}
      dragConstraints={{ left: -5, right: 5, top: 5, bottom: -5 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      animate={{
        rotateY: [0, Math.PI * 2],
        transition: { repeat: Infinity, duration: 4, ease: 'linear' }
      }}
    >
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="hotpink" />
    </motion.mesh>
  )
}
```

### 3. 状态同步动画

**R3F + Zustand + GSAP:**

```jsx
// store.js
import create from 'zustand'

export const useStore = create((set) => ({
  selectedObject: null,
  cameraMode: 'orbit',
  setSelectedObject: (obj) => set({ selectedObject: obj }),
  setCameraMode: (mode) => set({ cameraMode: mode })
}))
```

```jsx
// components/InteractiveObject.jsx
import { useRef, useEffect } from 'react'
import { useStore } from '../store'
import gsap from 'gsap'

export function InteractiveObject({ id }) {
  const meshRef = useRef()
  const selectedObject = useStore((state) => state.selectedObject)
  const setSelectedObject = useStore((state) => state.setSelectedObject)

  const isSelected = selectedObject === id

  useEffect(() => {
    if (isSelected) {
      gsap.to(meshRef.current.scale, {
        x: 1.2,
        y: 1.2,
        z: 1.2,
        duration: 0.3,
        ease: 'back.out'
      })
      gsap.to(meshRef.current.material, {
        emissiveIntensity: 0.5,
        duration: 0.3
      })
    } else {
      gsap.to(meshRef.current.scale, {
        x: 1,
        y: 1,
        z: 1,
        duration: 0.3,
        ease: 'power2.inOut'
      })
      gsap.to(meshRef.current.material, {
        emissiveIntensity: 0,
        duration: 0.3
      })
    }
  }, [isSelected])

  return (
    <mesh
      ref={meshRef}
      onClick={() => setSelectedObject(isSelected ? null : id)}
    >
      <boxGeometry />
      <meshStandardMaterial color="cyan" emissive="cyan" />
    </mesh>
  )
}
```

---

## 状态管理策略

### 1. Zustand 用于全局 3D 状态

**最佳用于：** 跨 3D 场景和 UI 共享状态

```javascript
// store/scene.js
import create from 'zustand'

export const useSceneStore = create((set, get) => ({
  // 状态
  camera: { position: [0, 2, 5], target: [0, 0, 0] },
  objects: {},
  selectedId: null,
  isAnimating: false,

  // 操作
  updateCamera: (updates) => set((state) => ({
    camera: { ...state.camera, ...updates }
  })),

  addObject: (id, object) => set((state) => ({
    objects: { ...state.objects, [id]: object }
  })),

  selectObject: (id) => set({ selectedId: id }),

  setAnimating: (isAnimating) => set({ isAnimating })
}))
```

**在 R3F 中使用：**

```jsx
import { useSceneStore } from '../store/scene'

function Object3D({ id }) {
  const selectedId = useSceneStore((state) => state.selectedId)
  const selectObject = useSceneStore((state) => state.selectObject)

  const isSelected = selectedId === id

  return (
    <mesh onClick={() => selectObject(id)}>
      <boxGeometry />
      <meshStandardMaterial color={isSelected ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

---

## 性能优化

### 跨库性能模式

#### 1. 渲染循环优化

**在 Three.js 和动画库之间协调渲染循环：**

```javascript
// 带有条件渲染的统一渲染循环
import { Clock } from 'three'

const clock = new Clock()
let needsRender = true

function animate() {
  requestAnimationFrame(animate)

  const delta = clock.getDelta()
  const elapsed = clock.getElapsedTime()

  // 仅在需要时渲染
  if (needsRender || controls.enabled) {
    // 更新 GSAP 动画（自动处理）

    // 更新 Three.js
    controls.update()
    renderer.render(scene, camera)

    // 重置标志
    needsRender = false
  }
}

// 滚动触发时触发重新渲染
ScrollTrigger.addEventListener('update', () => {
  needsRender = true
})
```

#### 2. 按需渲染 (R3F)

```jsx
import { Canvas } from '@react-three/fiber'

function App() {
  return (
    <Canvas
      frameloop="demand" // 仅在需要时渲染
      dpr={[1, 2]} // 自适应像素比
    >
      <Scene />
    </Canvas>
  )
}

function Scene() {
  const invalidate = useThree((state) => state.invalidate)

  // 状态变化时触发渲染
  const handleClick = () => {
    // 更新状态...
    invalidate() // 手动触发渲染
  }

  return <mesh onClick={handleClick}>...</mesh>
}
```

---

## 常见陷阱

### 1. 动画冲突

**问题：** 多个库尝试动画相同的属性

```jsx
// ❌ 错误：GSAP 和 React Spring 都在动画 position
gsap.to(meshRef.current.position, { x: 5 })
api.start({ position: [10, 0, 0] }) // 冲突!
```

**解决方案：** 每个属性使用一个库或协调时间

```jsx
// ✅ 正确：分离属性
gsap.to(meshRef.current.position, { x: 5 }) // GSAP 处理 position
api.start({ scale: 1.5 }) // Spring 处理 scale
```

### 2. 状态同步问题

**问题：** React 状态与 Three.js 场景不同步

```jsx
// ❌ 错误：未更新 Three.js 而更新 React 状态
mesh.position.x = 5 // Three.js 更新
// 但 React 状态仍然显示旧值！
```

**解决方案：** 使用引用或状态管理

```jsx
// ✅ 正确：同时更新
const updatePosition = (x) => {
  mesh.position.x = x
  setPosition(x) // 更新 React 状态
}
```

### 3. 从未清理的动画中内存泄漏

**问题：** 未在卸载时清理动画

```jsx
// ❌ 错误：无清理
useEffect(() => {
  gsap.to(meshRef.current.rotation, { y: Math.PI * 2, repeat: -1 })
}, [])
```

**解决方案：** 在 useEffect 返回中始终清理

```jsx
// ✅ 正确：卸载时清理
useEffect(() => {
  const tween = gsap.to(meshRef.current.rotation, { y: Math.PI * 2, repeat: -1 })

  return () => {
    tween.kill()
  }
}, [])
```

---

## 决策矩阵

### 何时使用哪种组合

| 用例 | 推荐堆栈 | 理由 |
|------|----------|-----------|
| 营销着陆页带滚动驱动 3D | Three.js + GSAP + React UI | GSAP 在滚动编排方面表现出色 |
| React 应用带交互式 3D 产品查看器 | R3F + Motion | 声明式，状态驱动，组件化 |
| 基于时间轴的复杂动画序列 | R3F + GSAP | GSAP 时间轴控制与 R3F 组件 |
| 基于物理的 3D 交互 | R3F + React Spring | Spring 物理感觉自然，适用于手势 |
| 高性能粒子系统 | Three.js + GSAP | 命令式控制，实例化，最小开销 |
| 快速原型设计，快速迭代 | R3F + Drei + Motion | 高级抽象，快速开发 |
| 游戏式体验带物理 | R3F + React Spring + Cannon (物理) | 物理引擎 + Spring 基于的 UI 反馈 |

---

## 资源

此技能包含用于多库集成的捆绑资源：

### references/
- `architecture_patterns.md` - 详细的架构模式和权衡
- `performance_optimization.md` - 跨栈的性能策略
- `state_management.md` - 3D 应用状态管理模式

### scripts/
- `integration_helper.py` - 生成库组合的集成样板代码
- `pattern_generator.py` - 构建常见集成模式

### assets/
- `starter_unified/` - 结合 R3F + GSAP + Motion 的完整启动模板
- `examples/` - 真实世界的集成示例

---

## 相关技能

**基础技能**（用于库特定细节）:
- **threejs-webgl** - Three.js 基础知识，场景设置，渲染
- **gsap-scrolltrigger** - GSAP 动画，ScrollTrigger，时间轴
- **react-three-fiber** - R3F 组件，钩子，Drei 辅助程序
- **motion-framer** - Motion 组件，手势，布局动画
- **react-spring-physics** - Spring 物理，React Spring 钩子

**何时参考基础技能：**
- Three.js 特定 API 问题 → `threejs-webgl`
- ScrollTrigger 语法 → `gsap-scrolltrigger`
- R3F 钩子和模式 → `react-three-fiber`
- Motion 手势处理 → `motion-framer`
- Spring 配置 → `react-spring-physics`

**此元技能涵盖：**
- 结合库的架构模式
- 跨库状态管理
- 性能优化策略
- 常见集成陷阱
- 决策框架

---

**构建复杂 3D Web 应用并集成多个动画和渲染库时使用此技能。对于库特定实现细节，参考各个基础技能。**
