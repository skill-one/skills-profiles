# Spline 交互式 - 基于浏览器的 3D 设计和动画

## 概述

Spline 是一个基于浏览器的 3D 设计和动画平台，它使创作者能够在无需代码或专业软件知识的情况下构建交互式 3D 体验。它提供了一个协作式视觉编辑器，用于设计、动画和导出跨多个平台的 3D 场景。

**主要功能**：
- 基于参数的视觉 3D 建模、挤压和布尔运算
- 基于状态动画系统，带时间轴控制
- 交互式事件系统（鼠标、键盘、碰撞、滚动）
- 多种导出选项（React 组件、Web 代码、公共 URL）
- 实时协作与团队库
- AI 驱动的生成（从文本生成 3D、纹理、风格迁移）
- 内置物理和粒子系统

**何时使用此技能**：
- 创建无需编写 Three.js 代码的 3D 网页体验
- 设计交互式产品展示或配置器
- 视觉化原型 3D UI/UX 概念
- 构建带有 3D 元素的营销页面
- 与设计师协作 3D 内容
- 导出场景用于 React 或原生 JavaScript 集成

**替代方案**：
- **Three.js** (threejs-webgl)：适用于偏好代码优先方法并需要最大控制权的开发者
- **Babylon.js** (babylonjs-engine)：适用于以游戏为重点的项目，具有内置物理
- **React Three Fiber** (react-three-fiber)：适用于希望使用 JSX 构建 3D 的 React 开发者

## 核心概念

### 1. 场景结构

Spline 将项目组织为包含以下内容的场景：
- **对象**：3D 模型、形状、文本、图像
- **灯光**：方向光、点光、聚光灯
- **相机**：轨道式、透视、正交
- **事件**：交互触发器
- **状态**：动画关键帧

### 2. 组件系统

可重用的元素，可以：
- 从任何对象或组创建
- 多次实例化
- 在所有实例中更新
- 按实例覆盖

### 3. 基于状态动画

动画定义为状态之间的转换：
- **默认状态**：初始外观
- **附加状态**：目标外观
- **事件**：触发状态转换的触发器
- **转换**：持续时间、缓动、属性

### 4. 交互模型

事件驱动系统，具有：
- **事件**：用户操作或场景触发器
- **条件**：逻辑门（如果/否则）
- **动作**：状态更改、音频、场景切换
- **变量**：来自 API 或用户输入的动态数据

### 5. 导出选项

多种部署方法：
- **公共 URL**：可直接共享的链接
- **代码导出**：React 组件或原生 JavaScript
- **Spline 查看器**：嵌入式 iframe
- **自托管**：下载并独立托管

## 常见模式

### 模式 1：基本 React 集成

**用例**：在 React 应用中嵌入 Spline 场景

**实现**：

```bash
# 安装
npm install @splinetool/react-spline @splinetool/runtime
```

```jsx
import Spline from '@splinetool/react-spline';

export default function Hero() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </div>
  );
}
```

**关键点**：
- 场景 URL 来自 Spline 导出对话框
- 组件填充父容器
- 自动处理加载和渲染

### 模式 2：事件处理和对象交互

**用例**：响应用户对特定对象的点击

**实现**：

```jsx
import Spline from '@splinetool/react-spline';

export default function InteractiveScene() {
  function onSplineMouseDown(e) {
    // 检查点击的对象是否是按钮
    if (e.target.name === 'Button') {
      console.log('按钮被点击！');

      // 获取对象属性
      console.log('位置：', e.target.position);
      console.log('旋转：', e.target.rotation);
      console.log('缩放：', e.target.scale);
    }
  }

  function onSplineMouseHover(e) {
    if (e.target.name === 'Button') {
      console.log('悬停在按钮上');
    }
  }

  return (
    <Spline
      scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
      onSplineMouseDown={onSplineMouseDown}
      onSplineMouseHover={onSplineMouseHover}
    />
  );
}
```

**可用事件处理器**：
- `onSplineMouseDown` - 对象鼠标按下
- `onSplineMouseUp` - 鼠标释放
- `onSplineMouseHover` - 鼠标悬停对象
- `onSplineKeyDown` - 键盘按下
- `onSplineKeyUp` - 键盘释放
- `onSplineStart` - 场景加载和开始
- `onSplineLookAt` - 相机看向事件
- `onSplineFollow` - 相机跟随事件
- `onSplineScroll` - 滚动事件

### 模式 3：程序化对象控制

**用例**：从 React 代码修改对象属性

**实现**：

```jsx
import { useRef } from 'react';
import Spline from '@splinetool/react-spline';

export default function ProductViewer() {
  const cube = useRef();
  const splineApp = useRef();

  function onLoad(spline) {
    // 保存 Spline 实例
    splineApp.current = spline;

    // 通过名称查找对象
    const obj = spline.findObjectByName('Product');
    // 或通过 ID
    // const obj = spline.findObjectById('8E8C2DDD-18B6-4C54-861D-7ED2519DE20E');

    cube.current = obj;
  }

  function rotateProduct() {
    if (cube.current) {
      // 绕 Y 轴旋转 45 度
      cube.current.rotation.y += Math.PI / 4;
    }
  }

  function changeColor() {
    if (cube.current) {
      // 更改材质颜色（十六进制颜色）
      cube.current.material.color.set(0xff6b6b);
    }
  }

  function moveProduct() {
    if (cube.current) {
      cube.current.position.x += 50;
      cube.current.position.y += 10;
    }
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
      <div style={{ position: 'absolute', top: 20, left: 20 }}>
        <button onClick={rotateProduct}>旋转</button>
        <button onClick={changeColor}>更改颜色</button>
        <button onClick={moveProduct}>移动</button>
      </div>
    </div>
  );
}
```

**可修改的对象属性**：
- `position` - { x, y, z }
- `rotation` - { x, y, z }（弧度）
- `scale` - { x, y, z }
- `material.color` - 十六进制颜色值
- `visible` - 布尔值

### 模式 4：触发 Spline 动画

**用例**：从 React 触发 Spline 中定义的动画

**实现**：

```jsx
import { useRef } from 'react';
import Spline from '@splinetool/react-spline';

export default function AnimatedCard() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;
  }

  function triggerHoverAnimation() {
    // 在 'Card' 对象上触发 mouseHover 事件
    splineApp.current.emitEvent('mouseHover', 'Card');
  }

  function triggerClickAnimation() {
    // 在 'Button' 对象上触发 mouseDown 事件
    splineApp.current.emitEvent('mouseDown', 'Button');
  }

  function reverseAnimation() {
    // 逆播放动画
    splineApp.current.emitEventReverse('mouseHover', 'Card');
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
      <button onClick={triggerHoverAnimation}>悬停效果</button>
      <button onClick={triggerClickAnimation}>点击效果</button>
      <button onClick={reverseAnimation}>逆播放</button>
    </div>
  );
}
```

**可用事件类型**：
- `mouseDown` - 鼠标按下
- `mouseHover` - 悬停效果
- `mouseUp` - 鼠标释放
- `keyDown` - 键盘按下
- `keyUp` - 键盘释放
- `start` - 开始事件
- `lookAt` - 相机看向
- `follow` - 相机跟随

### 模式 5：Next.js 集成与服务器端渲染

**用例**：使用 Next.js 并具有服务器端渲染优势

**实现**：

```jsx
// app/page.js (Next.js 13+ App Router)
import Spline from '@splinetool/react-spline/next';

export default function Home() {
  return (
    <main>
      <div style={{ width: '100vw', height: '100vh' }}>
        <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
      </div>
    </main>
  );
}
```

**优势**：
- SSR 期间显示占位符图像
- 更快的感知加载时间
- 使用回退内容改善 SEO

### 模式 6：懒加载以提高性能

**用例**：直到需要时才加载 Spline

**实现**：

```jsx
import React, { Suspense } from 'react';

// 动态导入 Spline
const Spline = React.lazy(() => import('@splinetool/react-spline'));

export default function LazyScene() {
  return (
    <div>
      <h1>我的页面内容</h1>

      <Suspense fallback={<div>加载 3D 场景...</div>}>
        <div style={{ width: '100%', height: '500px' }}>
          <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
        </div>
      </Suspense>

      <p>更多内容在下方</p>
    </div>
  );
}
```

**优势**：
- 减少初始包大小
- 改善页面加载性能
- 显示自定义加载 UI

### 模式 7：响应式 Spline 场景

**用例**：使 Spline 场景适应不同屏幕尺寸

**实现**：

```jsx
import Spline from '@splinetool/react-spline';
import { useState, useEffect } from 'react';

export default function ResponsiveScene() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div style={{
      width: '100%',
      height: isMobile ? '400px' : '600px'
    }}>
      <Spline
        scene={
          isMobile
            ? "https://prod.spline.design/YOUR-MOBILE-SCENE/scene.splinecode"
            : "https://prod.spline.design/YOUR-DESKTOP-SCENE/scene.splinecode"
        }
      />
    </div>
  );
}
```

**替代方法**（单个场景）：

```jsx
import Spline from '@splinetool/react-spline';
import { useRef, useEffect } from 'react';

export default function ResponsiveScene() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;
    adjustForScreenSize();
  }

  function adjustForScreenSize() {
    if (!splineApp.current) return;

    const camera = splineApp.current.findObjectByName('Camera');
    const isMobile = window.innerWidth < 768;

    if (isMobile) {
      // 移动端缩放缩小
      splineApp.current.setZoom(0.7);
      // 调整相机位置
      camera.position.z = 1500;
    }
  }

  useEffect(() => {
    window.addEventListener('resize', adjustForScreenSize);
    return () => window.removeEventListener('resize', adjustForScreenSize);
  }, []);

  return (
    <Spline
      scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
      onLoad={onLoad}
    />
  );
}
```

## 集成模式

### 与 Three.js (threejs-webgl)

对于高级用例，将 Spline 设计的资产与 Three.js 代码结合使用：

1. **从 Spline 导出**：使用 GLTF/GLB 导出
2. **在 Three.js 中导入**：使用 GLTFLoader 加载
3. **添加代码增强**：添加自定义着色器、物理或效果

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const loader = new GLTFLoader();
loader.load('spline-model.glb', (gltf) => {
  scene.add(gltf.scene);
  // 添加自定义行为
});
```

### 与 GSAP (gsap-scrolltrigger)

在滚动时触发 Spline 动画：

```jsx
import { useEffect, useRef } from 'react';
import Spline from '@splinetool/react-spline';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollAnimated() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;

    ScrollTrigger.create({
      trigger: '.scene-container',
      start: 'top center',
      onEnter: () => {
        app.emitEvent('mouseHover', 'Product');
      }
    });
  }

  return (
    <div className="scene-container">
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
    </div>
  );
}
```

### 与 Framer Motion (motion-framer)

由 Spline 处理 3D，而容器由 Framer Motion 动画化：

```jsx
import { motion } from 'framer-motion';
import Spline from '@splinetool/react-spline';

export default function AnimatedContainer() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      style={{ width: '100%', height: '600px' }}
    >
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </motion.div>
  );
}
```

## 性能优化

### 1. 启用按需渲染

仅在场景更改时渲染，而不是每帧：

```jsx
<Spline
  scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
  renderOnDemand={true} // 默认为 true
/>
```

### 2. 在 Spline 编辑器中优化场景

**在 Spline 中**：
- 减少多边形数量（使用简化）
- 压缩纹理（降低分辨率，使用 JPG 而不是 PNG）
- 限制灯光（最多 2-3 个灯光）
- 使用简单材质时
- 为远距离对象启用细节层次（LOD）

### 3. 懒加载重场景

使用 React.lazy() 如模式 6 中所示

### 4. 预加载关键场景

```jsx
import { useEffect } from 'react';
import Spline from '@splinetool/react-spline';

export default function PreloadedScene() {
  useEffect(() => {
    // 预加载场景资源
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = 'https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode';
    document.head.appendChild(link);
  }, []);

  return (
    <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
  );
}
```

### 5. 移动端优化

- 创建具有较低细节的移动端场景
- 在移动端降低画布分辨率
- 禁用阴影和反射
- 使用更简单的材质

```jsx
<Spline
  scene={isMobile ? mobileSceneUrl : desktopSceneUrl}
  style={{
    width: '100%',
    height: isMobile ? '300px' : '600px'
  }}
/>
```

## 常见陷阱和解决方案

### 陷阱 1：场景未加载

**问题**：Spline 组件渲染但场景不显示

**解决方案**：
```jsx
// ❌ 错误：无效的 scene URL
<Spline scene="my-scene.splinecode" />

// ✅ 正确：来自 Spline 导出对话框的完整 URL
<Spline scene="https://prod.spline.design/KFonZGtsoUXP-qx7/scene.splinecode" />

// 检查错误
function onLoad(app) {
  console.log('场景加载成功', app);
}

<Spline scene={sceneUrl} onLoad={onLoad} />
```

**也请检查**：
- 场景在 Spline 编辑器中已发布
- 网络标签显示成功的文件下载
- 控制台中无 CORS 错误

### 陷阱 2：对象引用在重新渲染后丢失

**问题**：对象引用在组件更新后变为未定义

**解决方案**：
```jsx
// ❌ 错误：存储对象时未使用正确的引用
let myObject;

function onLoad(spline) {
  myObject = spline.findObjectByName('Cube'); // 重新渲染时丢失
}

// ✅ 正确：使用 React 引用
const myObject = useRef();

function onLoad(spline) {
  myObject.current = spline.findObjectByName('Cube');
}
```

### 陷阱 3：移动端性能问题

**问题**：移动设备上的场景运行缓慢

**解决方案**：
```jsx
// 在 Spline 编辑器中创建移动优化的版本
// - 多边形数量少于 50k 三角形
// - 纹理尺寸较小（512x512 或更小）
// - 无阴影或反射
// - 使用简单材质

// 加载合适的版本
const isMobile = window.innerWidth < 768;
const sceneUrl = isMobile
  ? 'https://prod.spline.design/MOBILE-SCENE/scene.splinecode'
  : 'https://prod.spline.design/DESKTOP-SCENE/scene.splinecode';

<Spline scene={sceneUrl} renderOnDemand={true} />
```

### 陷阱 4：事件未触发

**问题**：点击或悬停事件未触发

**解决方案**：
```jsx
// ❌ 错误：使用错误的事件名称
<Spline onMouseDown={handler} /> // 不是 Spline 属性

// ✅ 正确：使用 Spline 事件属性
<Spline onSplineMouseDown={handler} />

// 也确保在 Spline 编辑器中对象有事件：
// 1. 在 Spline 中选择对象
// 2. 在"事件"面板中添加事件
// 3. 分配状态转换或动作
```

### 陷阱 5：程序化触发动画未工作

**问题**：`emitEvent()` 未触发动画

**解决方案**：
```jsx
// ❌ 错误：在场景加载前调用
function triggerAnimation() {
  splineApp.current.emitEvent('mouseHover', 'Button'); // 加载前出错
}

// ✅ 正确：确保场景已加载
const [isLoaded, setIsLoaded] = useState(false);

function onLoad(app) {
  splineApp.current = app;
  setIsLoaded(true);
}

function triggerAnimation() {
  if (isLoaded && splineApp.current) {
    splineApp.current.emitEvent('mouseHover', 'Button');
  }
}

// 也请验证在 Spline 编辑器中：
// - 对象具有正确的名称（'Button'）
// - mouseHover 事件已配置
// - 事件有动作（状态转换等）
```

### 陷阱 6：Next.js 水合错误

**问题**：服务器和客户端渲染不匹配

**解决方案**：
```jsx
// ❌ 错误：在 Next.js 中使用标准导入
import Spline from '@splinetool/react-spline';

// ✅ 正确：使用 Next.js 特定导入
import Spline from '@splinetool/react-spline/next';

// 或使用动态导入，ssr: false
import dynamic from 'next/dynamic';

const Spline = dynamic(
  () => import('@splinetool/react-spline'),
  { ssr: false }
);
```

## 资源

### 官方文档
- **Spline 文档**：https://docs.spline.design
- **React Spline GitHub**：https://github.com/splinetool/react-spline
- **Spline 社区**：https://spline.community

### Spline 编辑器
- **Web 应用**：https://app.spline.design
- **桌面应用**：macOS、Windows、Linux 版本可用

### 学习资源
- **教程**：https://spline.design/tutorials
- **YouTube 频道**：官方 Spline 教程
- **示例画廊**：https://spline.design/community

### 导出格式
- React 组件（通过 `@splinetool/react-spline`）
- 原生 JavaScript（Web 代码 API）
- GLTF/GLB（用于 Three.js、Babylon.js）
- USDZ（用于 Apple AR）
- STL（用于 3D 打印）
- 视频/GIF（用于营销）

## 相关技能

- **threejs-webgl**：适用于偏好代码优先方法并需要最大控制权的开发者
- **react-three-fiber**：适用于希望使用 JSX 构建 3D 的 React 开发者
- **babylonjs-engine**：替代 3D 引擎，具有编辑器工作流程
- **motion-framer**：用于动画化 Spline 容器和 UI 元素
- **gsap-scrolltrigger**：用于 Spline 滚动驱动动画
- **figma-dev-mode**：用于设计到代码的工作流程（类似视觉方法）

## 脚本

此技能包括实用脚本：
- `project_generator.py` - 生成 Spline + React 启动项目
- `component_builder.py` - 构建 Spline 组件包装器并添加事件

从技能目录运行脚本：
```bash
./scripts/project_generator.py
./scripts/component_builder.py
```

## 资产

启动模板和示例：
- `starter_spline/` - 完整的 React + Spline 模板
- `examples/` - 真实世界的集成模式
