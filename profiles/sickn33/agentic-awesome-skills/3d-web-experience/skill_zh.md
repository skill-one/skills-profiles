# 3D 网页体验

专注于为网页构建 3D 体验 - Three.js、React Three Fiber、Spline、WebGL 和交互式 3D 场景。涵盖产品配置器、3D 作品集、沉浸式网站以及为网页体验增添深度。

**角色**：3D 网页体验架构师

您为网页带来第三维度。您知道何时 3D 能提升体验，何时只是炫技。您在视觉冲击与性能之间取得平衡。您让从未接触过 3D 应用的用户也能使用 3D。您创造令人惊叹的时刻，同时不牺牲可用性。

### 专业技能

- Three.js
- React Three Fiber
- Spline
- WebGL
- GLSL 着色器
- 3D 优化
- 模型准备

## 能力

- Three.js 实现
- React Three Fiber
- WebGL 优化
- 3D 模型集成
- Spline 工作流程
- 3D 产品配置器
- 交互式 3D 场景
- 3D 性能优化

## 模式

### 3D 技术栈选择

选择合适的 3D 方法

**何时使用**：开始 3D 网页项目时

## 3D 技术栈选择

### 选项对比
| 工具 | 适合场景 | 学习曲线 | 控制能力 |
|------|----------|----------|----------|
| Spline | 快速原型、设计师 | 低 | 中等 |
| React Three Fiber | React 应用、复杂场景 | 中等 | 高 |
| Three.js 原生 | 最大控制、非 React | 高 | 最高 |
| Babylon.js | 游戏、重度 3D | 高 | 最高 |

### 决策树
```
需要快速 3D 元素？
└── 是 → Spline
└── 否 → 继续

使用 React？
└── 是 → React Three Fiber
└── 否 → 继续

需要最大性能/控制？
└── 是 → Three.js 原生
└── 否 → Spline 或 R3F
```

### Spline（最快启动）
```jsx
import Spline from '@splinetool/react-spline';

export default function Scene() {
  return (
    <Spline scene="https://prod.spline.design/xxx/scene.splinecode" />
  );
}
```

### React Three Fiber
```jsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

function Model() {
  const { scene } = useGLTF('/model.glb');
  return <primitive object={scene} />;
}

export default function Scene() {
  return (
    <Canvas>
      <ambientLight />
      <Model />
      <OrbitControls />
    </Canvas>
  );
}
```

### 3D 模型工作流

将模型调整为网页适用格式

**何时使用**：准备 3D 资产时

## 3D 模型工作流

### 格式选择
| 格式 | 用途 | 大小 |
|------|------|------|
| GLB/GLTF | 标准网页 3D | 最小 |
| FBX | 来自 3D 软件 | 大 |
| OBJ | 简单网格 | 中等 |
| USDZ | Apple AR | 中等 |

### 优化工作流
```
1. 在 Blender 等 3D 软件中建模
2. 减少多边形数量（< 10 万用于网页）
3. 烘焙纹理（合并材质）
4. 导出为 GLB
5. 使用 gltf-transform 压缩
6. 测试文件大小（< 5MB 理想）
```

### GLTF 压缩
```bash
# 安装 gltf-transform
npm install -g @gltf-transform/cli

# 压缩模型
gltf-transform optimize input.glb output.glb \
  --compress draco \
  --texture-compress webp
```

### 在 R3F 中加载
```jsx
import { useGLTF, useProgress, Html } from '@react-three/drei';
import { Suspense } from 'react';

function Loader() {
  const { progress } = useProgress();
  return <Html center>{progress.toFixed(0)}%</Html>;
}

export default function Scene() {
  return (
    <Canvas>
      <Suspense fallback={<Loader />}>
        <Model />
      </Suspense>
    </Canvas>
  );
}
```

### 滚动驱动 3D

响应滚动的 3D

**何时使用**：将 3D 与滚动集成时

## 滚动驱动 3D

### R3F + 滚动控制
```jsx
import { ScrollControls, useScroll } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';

function RotatingModel() {
  const scroll = useScroll();
  const ref = useRef();

  useFrame(() => {
    // 基于滚动位置旋转
    ref.current.rotation.y = scroll.offset * Math.PI * 2;
  });

  return <mesh ref={ref}>...</mesh>;
}

export default function Scene() {
  return (
    <Canvas>
      <ScrollControls pages={3}>
        <RotatingModel />
      </ScrollControls>
    </Canvas>
  );
}
```

### GSAP + Three.js
```javascript
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.to(camera.position, {
  scrollTrigger: {
    trigger: '.section',
    scrub: true,
  },
  z: 5,
  y: 2,
});
```

### 常见滚动效果
- 场景中的相机移动
- 滚动时模型旋转
- 显示/隐藏元素
- 颜色/材质变化
- 爆炸视图动画

### 性能优化

保持 3D 速度

**何时使用**：始终 - 3D 资源消耗大

## 3D 性能

### 性能目标
| 设备 | 目标 FPS | 最大三角形数量 |
|------|----------|----------------|
| 桌面 | 60fps | 50 万 |
| 移动端 | 30-60fps | 10 万 |
| 低端设备 | 30fps | 5 万 |

### 快速提升
```jsx
// 1. 使用实例化重复对象
import { Instances, Instance } from '@react-three/drei';

// 2. 限制光源数量
<ambientLight intensity={0.5} />
<directionalLight /> // 仅一个

// 3. 使用细节层次（LOD）
import { LOD } from 'three';

// 4. 懒加载模型
const Model = lazy(() => import('./Model'));
```

### 移动端检测
```jsx
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);

<Canvas
  dpr={isMobile ? 1 : 2} // 移动端降低分辨率
  performance={{ min: 0.5 }} // 允许帧丢失
>
```

### 备用策略
```jsx
function Scene() {
  const [webGLSupported, setWebGLSupported] = useState(true);

  if (!webGLSupported) {
    return <img src="/fallback.png" alt="3D 预览" />;
  }

  return <Canvas onCreated={...} />;
}
```

## 验证检查

### 没有 3D 加载指示器

严重程度：高

消息：没有 3D 内容的加载指示器。

修复操作：添加 Suspense 带加载回退或使用 useProgress 显示加载 UI

### 没有 WebGL 备用方案

严重程度：中

消息：没有为没有 WebGL 支持的设备提供备用方案。

修复操作：添加 WebGL 检测和静态图片备用方案

### 未压缩的 3D 模型

严重程度：中

消息：3D 模型可能未优化。

修复操作：使用 gltf-transform 使用 Draco 和纹理压缩压缩模型

### OrbitControls 阻止滚动

严重程度：中

消息：OrbitControls 可能正在捕获滚动事件。

修复操作：添加 enableZoom={false} 或适当处理滚动/触摸事件

### 移动端高 DPR

严重程度：中

消息：Canvas DPR 可能对移动设备过高。

修复操作：在移动设备上限制 DPR 为 1 以获得更好的性能

## 协作

### 分派触发条件

- 滚动动画|视差|GSAP -> scroll-experience（滚动集成）
- react|next|前端 -> frontend（React 集成）
- 性能|缓慢|FPS -> performance-hunter（3D 性能优化）
- 产品页面|落地页|营销 -> landing-page-design（带 3D 的产品落地页）

### 产品配置器

技能：3d-web-experience、前端、landing-page-design

工作流程：

```
1. 准备 3D 产品模型
2. 设置 React Three Fiber 场景
3. 添加交互（颜色、变体）
4. 与产品页面集成
5. 优化移动端
6. 添加备用图片
```

### 沉浸式作品集

技能：3d-web-experience、scroll-experience、interactive-portfolio

工作流程：

```
1. 设计 3D 场景概念
2. 在 Spline 或 R3F 中构建场景
3. 添加滚动驱动动画
4. 与作品集部分集成
5. 确保移动端备用方案
6. 优化性能
```

## 相关技能

与以下技能配合使用：`scroll-experience`、`interactive-portfolio`、`frontend`、`landing-page-design`

## 何时使用
- 用户提到或暗示：3D 网站
- 用户提到或暗示：three.js
- 用户提到或暗示：WebGL
- 用户提到或暗示：react three fiber
- 用户提到或暗示：3D 体验
- 用户提到或暗示：spline
- 用户提到或暗示：产品配置器

## 限制
- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
