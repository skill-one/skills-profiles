# React Three Fiber 最佳实践

React Three Fiber 和 Poimandres 生态系统的全面指南。包含 12 类别中的 70 多条规则，按影响优先级排序。

## 来源与致谢

> 额外提示来自 [100 个 Three.js 小技巧](https://www.utsubo.com/blog/threejs-best-practices-100-tips) by [Utsubo](https://www.utsubo.com)

## 应用场景

在以下情况下参考这些指南：
- 编写新的 R3F 组件
- 优化 R3F 性能（重新渲染是首要问题）
- 正确使用 Drei 辅助工具
- 使用 Zustand 管理状态
- 实现后期处理或物理效果

## 生态系统覆盖范围

- **@react-three/fiber** - Three.js 的 React 渲染器
- **@react-three/drei** - 有用的辅助工具和抽象
- **@react-three/postprocessing** - 后期处理效果
- **@react-three/rapier** - 物理引擎
- **zustand** - 状态管理
- **leva** - 调试 GUI

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 性能 & 重新渲染 | 关键 | `perf-` |
| 2 | useFrame & 动画 | 关键 | `frame-` |
| 3 | 组件模式 | 高 | `component-` |
| 4 | Canvas & 设置 | 高 | `canvas-` |
| 5 | Drei 辅助工具 | 中高 | `drei-` |
| 6 | 加载 & Suspense | 中高 | `loading-` |
| 7 | 状态管理 | 中 | `state-` |
| 8 | 事件 & 交互 | 中 | `events-` |
| 9 | 后期处理 | 中 | `postpro-` |
| 10 | 物理 (Rapier) | 低中 | `physics-` |
| 11 | Leva (调试 GUI) | 低 | `leva-` |

## 快速参考

### 1. 性能 & 重新渲染 (关键)

- `perf-never-set-state-in-useframe` - 在 useFrame 中永远不要调用 setState
- `perf-isolate-state` - 将需要 React 状态的组件隔离
- `perf-zustand-selectors` - 使用 Zustand 选择器，而不是整个 store
- `perf-transient-subscriptions` - 使用临时订阅处理连续值
- `perf-memo-components` - 优化昂贵组件的 memoize
- `perf-keys-for-lists` - 为动态列表使用稳定的键
- `perf-avoid-inline-objects` - 避免在 JSX 中创建对象/数组
- `perf-dispose-auto` - 理解 R3F 自动销毁行为
- `perf-visibility-toggle` - 切换可见性而不是重新挂载
- `perf-r3f-perf` - 使用 r3f-perf 进行性能监控

### 2. useFrame & 动画 (关键)

- `frame-priority` - 使用优先级控制执行顺序
- `frame-delta-time` - 动画始终使用 delta 时间
- `frame-conditional-subscription` - 在不需要时禁用 useFrame
- `frame-destructure-state` - 仅解构所需内容
- `frame-render-on-demand` - 使用 invalidate() 进行按需渲染
- `frame-avoid-heavy-computation` - 将重工作移出 useFrame

### 3. 组件模式 (高)

- `component-jsx-elements` - 使用 JSX 处理 Three.js 对象
- `component-attach-prop` - 使用 attach 处理非标准属性
- `component-primitive` - 使用 primitive 处理现有对象
- `component-extend` - 使用 extend() 处理自定义类
- `component-forwardref` - 使用 forwardRef 处理可复用组件
- `component-dispose-null` - 在共享资源上设置 dispose={null}

### 4. Canvas & 设置 (高)

- `canvas-size-container` - Canvas 填充父容器
- `canvas-camera-default` - 通过属性配置相机
- `canvas-gl-config` - 配置 WebGL 上下文
- `canvas-shadows` - 在 Canvas 级别启用阴影
- `canvas-frameloop` - 选择合适的帧循环模式
- `canvas-events` - 配置事件处理
- `canvas-linear-flat` - 使用线性/平面模式确保正确颜色

### 5. Drei 辅助工具 (中高)

- `drei-use-gltf` - useGLTF 带预加载
- `drei-use-texture` - useTexture 处理纹理加载
- `drei-environment` - 环境光实现真实感照明
- `drei-orbit-controls` - 使用 Drei 的 OrbitControls
- `drei-html` - Html 处理 DOM 叠加层
- `drei-text` - Text 处理 3D 文本
- `drei-instances` - Instances 处理优化实例化
- `drei-use-helper` - useHelper 处理调试可视化
- `drei-bounds` - Bounds 处理相机适配
- `drei-center` - Center 处理对象居中
- `drei-float` - Float 处理浮动动画

### 6. 加载 & Suspense (中高)

- `loading-suspense` - 将异步组件包裹在 Suspense 中
- `loading-preload` - 使用 useGLTF.preload 预加载资源
- `loading-use-progress` - useProgress 处理加载 UI
- `loading-lazy-components` - 懒加载重组件
- `loading-error-boundary` - 处理加载错误

### 7. 状态管理 (中)

- `state-zustand-store` - 创建专注的 Zustand store
- `state-avoid-objects-in-store` - 小心处理 Three.js 对象
- `state-subscribeWithSelector` - 精细订阅
- `state-persist` - 需要时持久化状态
- `state-separate-concerns` - 按关注点分离 store

### 8. 事件 & 交互 (中)

- `events-pointer-events` - 在网格上使用 pointer events
- `events-stop-propagation` - 阻止事件冒泡
- `events-cursor-pointer` - 悬停时改变光标
- `events-raycast-filter` - 过滤射线投射
- `events-event-data` - 理解事件数据结构

### 9. 后期处理 (中)

- `postpro-effect-composer` - 使用 EffectComposer
- `postpro-common-effects` - 常见效果参考
- `postpro-selective-bloom` - 使用 SelectiveBloom 优化辉光效果
- `postpro-custom-shader` - 创建自定义效果
- `postpro-performance` - 优化后期处理

### 10. 物理 Rapier (低中)

- `physics-setup` - 基础 Rapier 设置
- `physics-body-types` - dynamic, fixed, kinematic
- `physics-colliders` - 选择合适的碰撞器
- `physics-events` - 处理碰撞事件
- `physics-api-ref` - 使用 ref 处理物理 API
- `physics-performance` - 优化物理效果

### 11. Leva (低)

- `leva-basic` - 基础 Leva 使用
- `leva-folders` - 使用文件夹组织
- `leva-conditional` - 生产环境中隐藏

## 如何使用

阅读单个规则文件获取详细解释和代码示例：

```
rules/perf-never-set-state-in-useframe.md
rules/drei-use-gltf.md
rules/state-zustand-selectors.md
```

## 完整编译文档

获取包含所有规则扩展的完整指南：`../R3F_BEST_PRACTICES.md`

## 关键模式

### 永远不要在 useFrame 中 setState

```jsx
// BAD - 每秒 60 次重新渲染！
function BadComponent() {
  const [position, setPosition] = useState(0);
  useFrame(() => {
    setPosition(p => p + 0.01); // 永远不要这样做
  });
  return <mesh position-x={position} />;
}

// GOOD - 直接修改 ref
function GoodComponent() {
  const meshRef = useRef();
  useFrame(() => {
    meshRef.current.position.x += 0.01;
  });
  return <mesh ref={meshRef} />;
}
```

### Zustand 选择器

```jsx
// BAD - 任何 store 变更都会重新渲染
const store = useGameStore();

// GOOD - 仅在 playerX 变化时重新渲染
const playerX = useGameStore(state => state.playerX);

// BETTER - 无需重新渲染，直接修改
useFrame(() => {
  const { value } = useStore.getState();
  ref.current.position.x = value;
});
```

### Drei useGLTF

```jsx
import { useGLTF } from '@react-three/drei';

function Model() {
  const { scene } = useGLTF('/model.glb');
  return <primitive object={scene} />;
}

// 预加载实现即时加载
useGLTF.preload('/model.glb');
```

### Suspense 加载

```jsx
function App() {
  return (
    <Canvas>
      <Suspense fallback={<Loader />}>
        <Model />
      </Suspense>
    </Canvas>
  );
}
```

### r3f-perf 监控

```jsx
import { Perf } from 'r3f-perf';

function App() {
  return (
    <Canvas>
      <Perf position="top-left" />
      <Scene />
    </Canvas>
  );
}
```

### 切换可见性（而不是重新挂载）

```jsx
// BAD: 重新挂载会销毁和重建
{showModel && <Model />}

// GOOD: 切换可见性，保持实例存活
<Model visible={showModel} />
```
