---
name: lottie-animations
description: 用于网页和React应用程序的After Effects动画渲染。在实现Lottie动画、JSON矢量动画、交互式动画图标、微交互或加载动画时使用此技能。适用于涉及Lottie、lottie-web、lottie-react、dotLottie、After Effects JSON导出、bodymovin、动画SVG替代方案或设计师创建的动画的任务。与GSAP ScrollTrigger和Framer Motion结合，用于滚动驱动和交互式动画。
---

# Lottie 动画

## 概述

Lottie 是一个用于在 Web、iOS、Android 和 React Native 上实时渲染 After Effects 动画的库。由 Airbnb 创建，它允许设计师像发送静态资源一样轻松发送动画。动画通过 Bodymovin 插件从 After Effects 导出为 JSON 文件，然后使用本机渲染，性能开销极小。

**何时使用 Lottie：**
- 需要像素级精确度的设计师创建的动画
- 复杂的动画图标和微交互
- 加载动画和进度指示器
- 欢迎序列和教程动画
- 营销动画和推广内容
- GIF/视频的替代方案，具有更小的文件大小和可扩展性

**主要优势：**
- 基于矢量（可缩放而不损失质量）
- 比 GIF 或视频小得多
- 可在运行时编辑（颜色、速度、片段）
- 通过 After Effects 完全由设计师控制
- 跨平台渲染一致性
- 交互式控件（播放、暂停、跳转、循环）

## 核心概念

### Lottie 格式类型

**1. JSON Lottie (.json)**
- 原始 Lottie 格式
- 通过 Bodymovin 插件从 After Effects 导出
- 人类可读的 JSON 结构
- 文件较大（未压缩）
- 在所有平台上广泛支持

**2. dotLottie (.lottie)**
- 现代压缩格式
- ZIP 存档，包含 JSON + 资源
- 支持一个文件中的多个动画和主题
- 文件较小（最高可减少 90%）
- 推荐用于生产

### 库选项

**lottie-web**（原始库）:
```javascript
import lottie from 'lottie-web';

lottie.loadAnimation({
  container: document.getElementById('lottie-container'),
  renderer: 'svg', // 或 'canvas', 'html'
  loop: true,
  autoplay: true,
  path: 'animation.json' // 或 animationData: jsonData
});
```

**@lottiefiles/dotlottie-web**（现代，推荐）:
```javascript
import { DotLottie } from '@lottiefiles/dotlottie-web';

new DotLottie({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true
});
```

**@lottiefiles/dotlottie-react**（React 集成）:
```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

<DotLottieReact
  src="animation.lottie"
  loop
  autoplay
  style={{ height: 300 }}
/>
```

**lottie-react**（替代 React 封装）:
```jsx
import Lottie from 'lottie-react';
import animationData from './animation.json';

<Lottie animationData={animationData} loop={true} />
```

### 动画数据源

**1. LottieFiles** (lottie.host)
- 10 万多个免费动画
- 直接 URL 嵌入
- CDN 托管

**2. 本地 JSON/dotLottie 文件**
- 随应用程序打包
- 更好的性能（无需网络请求）
- 友好的版本控制

**3. After Effects 导出**
- 定制设计师动画
- 需要 Bodymovin 插件
- 导出设置对文件大小至关重要

## 常见模式

### 1. 使用 dotLottie-web 的基本 HTML 集成

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    #canvas {
      width: 400px;
      height: 400px;
    }
  </style>
</head>
<body>
  <canvas id="canvas"></canvas>

  <script type="module">
    import { DotLottie } from 'https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web/+esm';

    new DotLottie({
      canvas: document.getElementById('canvas'),
      src: 'https://lottie.host/4db68bbd-31f6-4cd8-84eb-189de081159a/IGmMCqhzpt.lottie',
      autoplay: true,
      loop: true
    });
  </script>
</body>
</html>
```

### 2. 带控制的 React 组件

```jsx
import React from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const AnimatedButton = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  const handlePlay = () => dotLottie?.play();
  const handlePause = () => dotLottie?.pause();
  const handleStop = () => dotLottie?.stop();
  const handleSeek = (frame) => dotLottie?.setFrame(frame);

  return (
    <div>
      <DotLottieReact
        src="button-animation.lottie"
        loop
        autoplay={false}
        dotLottieRefCallback={setDotLottie}
        style={{ height: 200 }}
      />

      <div>
        <button onClick={handlePlay}>播放</button>
        <button onClick={handlePause}>暂停</button>
        <button onClick={handleStop}>停止</button>
        <button onClick={() => handleSeek(30)}>跳转到第 30 帧</button>
      </div>
    </div>
  );
};
```

### 3. 事件监听器和生命周期钩子

```jsx
import React, { useEffect } from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const EventDrivenAnimation = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  useEffect(() => {
    if (!dotLottie) return;

    const onLoad = () => console.log('动画加载');
    const onPlay = () => console.log('动画开始');
    const onPause = () => console.log('动画暂停');
    const onComplete = () => console.log('动画完成');
    const onFrame = ({ currentFrame }) => console.log('帧:', currentFrame);

    dotLottie.addEventListener('load', onLoad);
    dotLottie.addEventListener('play', onPlay);
    dotLottie.addEventListener('pause', onPause);
    dotLottie.addEventListener('complete', onComplete);
    dotLottie.addEventListener('frame', onFrame);

    return () => {
      dotLottie.removeEventListener('load', onLoad);
      dotLottie.removeEventListener('play', onPlay);
      dotLottie.removeEventListener('pause',.onPause);
      dotLottie.removeEventListener('complete', onComplete);
      dotLottie.removeEventListener('frame', onFrame);
    };
  }, [dotLottie]);

  return (
    <DotLottieReact
      src="animation.lottie"
      loop
      autoplay
      dotLottieRefCallback={setDotLottie}
    />
  );
};
```

### 4. 使用 lottie-react 的滚动触发动画

```jsx
import Lottie from 'lottie-react';
import robotAnimation from './robot.json';

const ScrollAnimation = () => {
  const interactivity = {
    mode: 'scroll',
    actions: [
      {
        visibility: [0, 0.2],
        type: 'stop',
        frames: [0]
      },
      {
        visibility: [0.2, 0.45],
        type: 'seek',
        frames: [0, 45]
      },
      {
        visibility: [0.45, 1.0],
        type: 'loop',
        frames: [45, 60]
      }
    ]
  };

  return (
    <Lottie
      animationData={robotAnimation}
      style={{ height: 300 }}
      interactivity={interactivity}
    />
  );
};
```

### 5. 悬停触发片段播放

```jsx
import { useLottie, useLottieInteractivity } from 'lottie-react';
import likeButton from './like-button.json';

const HoverAnimation = () => {
  const lottieObj = useLottie({
    animationData: likeButton
  });

  const Animation = useLottieInteractivity({
    lottieObj,
    mode: 'cursor',
    actions: [
      {
        position: { x: [0, 1], y: [0, 1] },
        type: 'loop',
        frames: [45, 60]
      },
      {
        position: { x: -1, y: -1 },
        type: 'stop',
        frames: [45]
      }
    ]
  });

  return <div style={{ height: 300, border: '2px solid black' }}>{Animation}</div>;
};
```

### 6. 多动画和主题支持

```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';
import React, { useState, useEffect } from 'react';

const ThemedAnimation = () => {
  const [dotLottie, setDotLottie] = useState(null);
  const [animations, setAnimations] = useState([]);
  const [themes, setThemes] = useState([]);
  const [currentAnimationId, setCurrentAnimationId] = useState('');
  const [currentThemeId, setCurrentThemeId] = useState('');

  useEffect(() => {
    if (!dotLottie) return;

    const onLoad = () => {
      setAnimations(dotLottie.manifest.animations || []);
      setThemes(dotLottie.manifest.themes || []);
      setCurrentAnimationId(dotLottie.activeAnimationId);
      setCurrentThemeId(dotLottie.activeThemeId);
    };

    dotLottie.addEventListener('load', onLoad);
    return () => dotLottie.removeEventListener('load', onLoad);
  }, [dotLottie]);

  return (
    <div>
      <DotLottieReact
        src="multi-animation.lottie"
        dotLottieRefCallback={setDotLottie}
        animationId={currentAnimationId}
        themeId={currentThemeId}
      />

      {themes.length > 0 && (
        <select value={currentThemeId} onChange={(e) => setCurrentThemeId(e.target.value)}>
          {themes.map((theme) => (
            <option key={theme.id} value={theme.id}>{theme.id}</option>
          ))}
        </select>
      )}

      {animations.length > 0 && (
        <select value={currentAnimationId} onChange={(e) => setCurrentAnimationId(e.target.value)}>
          {animations.map((anim) => (
            <option key={anim.id} value={anim.id}>{anim.id}</option>
          ))}
        </select>
      )}
    </div>
  );
};
```

### 7. 使用 Web Worker 进行性能优化 (DotLottieWorker)

```javascript
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

// 将动画渲染卸载到 Web Worker
new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-1' // 通过 worker 分组多个动画
});

// 在单独的 workers 中使用多个动画
new DotLottieWorker({
  canvas: document.getElementById('canvas-2'),
  src: 'animation-2.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-2'
});
```

## 集成模式

### 与 GSAP ScrollTrigger 集成

```jsx
import Lottie from 'lottie-react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
import animationData from './animation.json';

gsap.registerPlugin(ScrollTrigger);

const GSAPLottieIntegration = () => {
  const lottieRef = React.useRef();

  React.useEffect(() => {
    const anim = lottieRef.current;
    if (!anim) return;

    // 同步 Lottie 与滚动
    gsap.to(anim, {
      scrollTrigger: {
        trigger: '#animation-section',
        start: 'top center',
        end: 'bottom center',
        scrub: 1,
        onUpdate: (self) => {
          const frame = Math.floor(self.progress * (anim.totalFrames - 1));
          anim.goToAndStop(frame, true);
        }
      }
    });
  }, []);

  return (
    <div id="animation-section" style={{ height: '200vh' }}>
      <Lottie
        lottieRef={lottieRef}
        animationData={animationData}
        autoplay={false}
        loop={false}
      />
    </div>
  );
};
```

### 与 Framer Motion 集成

```jsx
import { motion } from 'framer-motion';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const MotionLottie = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <DotLottieReact
        src="animation.lottie"
        loop
        autoplay
        style={{ height: 400 }}
      />
    </motion.div>
  );
};
```

### Vue 3 集成

```vue
<script setup>
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';
</script>

<template>
  <DotLottieVue
    style="height: 500px; width: 500px"
    autoplay
    loop
    src="https://path-to-animation.lottie"
  />
</template>
```

### Svelte 集成

```svelte
<script lang="ts">
  import { DotLottieSvelte } from '@lottiefiles/dotlottie-svelte';
  import type { DotLottie } from '@lottiefiles/dotlottie-svelte';

  let dotLottie: DotLottie | null = null;

  function play() {
    dotLottie?.play();
  }
</script>

<DotLottieSvelte
  src="animation.lottie"
  loop={true}
  autoplay={true}
  dotLottieRefCallback={(ref) => dotLottie = ref}
/>

<button on:click={play}>播放</button>
```

## 性能优化

### 文件大小优化

**1. After Effects 导出设置：**
- 启用 "跳过未使用的图像"
- 在可能的情况下使用 "字形" 而不是字体
- 简化路径（减少 Illustrator 中的点）
- 避免创建大型数据的特效（粒子、噪声）
- 使用形状图层而不是矢量图层

**2. 压缩：**
- 使用 dotLottie 格式 (.lottie) 进行自动压缩
- 通过 Lottie 优化工具运行 JSON
- 删除不必要的元数据

**3. 懒加载：**
```jsx
const LazyLottie = () => {
  const [shouldLoad, setShouldLoad] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setShouldLoad(true);
      }
    });

    observer.observe(document.getElementById('lottie-trigger'));
    return () => observer.disconnect();
  }, []);

  return (
    <div id="lottie-trigger">
      {shouldLoad && <DotLottieReact src="animation.lottie" loop autoplay />}
    </div>
  );
};
```

### 运行时性能

**1. 渲染器选择：**
```javascript
// SVG：最佳质量，复杂动画渲染较慢
// Canvas：更好的性能，光栅化
// HTML：支持有限，仅用于简单的动画

// 对于复杂动画，优先使用 canvas
new DotLottie({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true,
  renderConfig: {
    devicePixelRatio: window.devicePixelRatio || 1
  }
});
```

**2. Web Workers：**
```javascript
// 将渲染卸载到 worker 以处理重动画
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true
});
```

**3. 移动端优化：**
```javascript
// 在移动端降低质量
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

new DotLottie({
  canvas: document.getElementById('canvas'),
  src: isMobile ? 'animation-low.lottie' : 'animation-high.lottie',
  autoplay: true,
  loop: true,
  renderConfig: {
    devicePixelRatio: isMobile ? 1 : window.devicePixelRatio
  }
});
```

## 常见陷阱

### 1. 由于清理不当导致的内存泄漏

**问题：** 组件卸载时未销毁 Lottie 实例。

**解决方案：**
```jsx
const SafeAnimation = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  React.useEffect(() => {
    return () => {
      // 总是在卸载时销毁实例
      dotLottie?.destroy();
    };
  }, [dotLottie]);

  return <DotLottieReact src="animation.lottie" dotLottieRefCallback={setDotLottie} />;
};
```

### 2. 事件监听器清理

**问题：** 未移除事件监听器，导致多个处理器。

**解决方案：**
```jsx
useEffect(() => {
  if (!dotLottie) return;

  const handleComplete = () => console.log('完成');
  dotLottie.addEventListener('complete', handleComplete);

  // 必须返回清理函数
  return () => {
    dotLottie.removeEventListener('complete', handleComplete);
  };
}, [dotLottie]);
```

### 3. 文件过大

**问题：** 简单动画的 JSON 文件为 500KB+。

**解决方案：**
- 简化 After Effects 合成（减少图层、关键帧）
- 使用 dotLottie 格式进行压缩
- 检查 Bodymovin 导出设置（如果不需要，禁用 "包含表达式"）
- 导出前删除未使用的资源
- 使用 Lottie 优化工具：https://lottiefiles.com/tools/lottie-editor

### 4. 动画性能问题

**问题：** 动画卡顿或帧丢失。

**解决方案：**
- 从 SVG 切换到 Canvas 渲染器
- 使用 `DotLottieWorker` 进行 Web Worker 渲染
- 在 After Effects 中降低复杂性（更少的图层、更简单的形状）
- 在移动端降低 devicePixelRatio
- 避免同时动画化太多属性

### 5. 路径/URL 引用错误

**问题：** 由于 CORS 或路径错误导致动画无法加载。

**解决方案：**
```jsx
// 使用 animationData 进行本地导入（捆绑应用程序的最佳方案）
import animationData from './animation.json';
<Lottie animationData={animationData} />

// 或者使用路径进行外部 URL（需要 CORS 标头）
<DotLottieReact src="https://example.com/animation.lottie" />

// 对于 Next.js，放在 public/ 文件夹中
<DotLottieReact src="/animations/animation.lottie" />
```

### 6. After Effects 导出兼容性

**问题：** 一些 After Effects 功能无法导出到 Lottie。

**不支持的特性：**
- 图层效果（投影、辉光） - 请使用形状图层替代
- 混合模式（有限支持）
- 3D图层
- 表达式（部分支持）
- 跟踪遮罩（部分支持）

**解决方案：**
- 尽早并频繁地进行导出测试
- 在导出前使用LottieFiles预览
- 检查Bodymovin兼容性：https://airbnb.io/lottie/#/supported-features
- 尽可能将效果转换为形状

## 资源

此技能包含：

### scripts/
- `generate_lottie_component.py` - 生成React/Vue/Svelte Lottie组件模板
- `optimize_lottie.py` - 优化Lottie JSON文件大小

### references/
- `api_reference.md` - lottie-web、lottie-react和dotlottie-web的完整API文档
- `after_effects_export.md` - 从After Effects导出动画的指南
- `performance_guide.md` - 详细的性能优化策略

### assets/
- `starter_lottie/` - 带有Lottie示例的完整React + Vite启动模板
- `examples/` - 真实世界的Lottie动画模式和用例

## 相关技能

- **gsap-scrolltrigger** - 用于与页面滚动同步的滚动驱动Lottie动画
- **motion-framer** - 与Framer Motion结合，用于包装Lottie的布局动画
- **animated-component-libraries** - 可能包含Lottie动画的预构建组件库
- **threejs-webgl** - 用于Lottie 2D能力之外的3D动画
- **react-three-fiber** - 复杂3D动画场景的替代方案
