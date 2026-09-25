# GSAP & ScrollTrigger 开发

## 概述

GSAP（GreenSock 动画平台）是业界领先的 JavaScript 动画库，用于创建高性能、生产级的动画。ScrollTrigger 是 GSAP 的强大插件，用于滚动驱动的动画。两者结合，可以实现从简单的 UI 过渡到复杂的基于滚动的叙事体验。

## 核心概念

### 基础：补间动画（Tweens）

**补间动画**是指从 A 点到 B 点的单个动画。

```javascript
// 从当前状态动画到目标状态（默认从当前状态开始）
gsap.to(".box", {
  x: 200,
  rotation: 360,
  duration: 1,
  ease: "power2.inOut"
});

// 从目标状态动画到当前状态
gsap.from(".box", {
  opacity: 0,
  y: -50,
  duration: 0.8
});

// 从当前状态到目标状态（定义起始和结束状态）
gsap.fromTo(".box",
  { opacity: 0, scale: 0.5 }, // 从当前状态
  { opacity: 1, scale: 1, duration: 1 } // 到目标状态
);
```

### 时间轴：动画序列

**时间轴**用于按顺序或重叠组织多个补间动画。

```javascript
const tl = gsap.timeline();

// 默认按顺序执行
tl.to(".box1", { x: 100, duration: 1 })
  .to(".box2", { y: 100, duration: 1 })
  .to(".box3", { rotation: 360, duration: 1 });

// 带标签进行组织
tl.addLabel("start")
  .to(".hero", { opacity: 1, duration: 1 })
  .addLabel("reveal")
  .to(".content", { y: 0, duration: 0.8 }, "reveal") // 从 "reveal" 标签开始
  .to(".cta", { scale: 1, duration: 0.5 }, "reveal+=0.5"); // 在 "reveal" 后 0.5 秒开始
```

### 位置参数（时间轴时间）

控制动画在时间轴中的开始时间：

```javascript
const tl = gsap.timeline();

// 默认：一个接一个
tl.to(".box1", { x: 100 })
  .to(".box2", { x: 100 }); // 在 box1 完成后开始

// 同时开始
tl.to(".box1", { x: 100 })
  .to(".box2", { y: 100 }, 0); // 在 0 秒开始

// 相对定位
tl.to(".box1", { x: 100, duration: 2 })
  .to(".box2", { y: 100 }, "-=1"); // 在 box1 结束前 1 秒开始
  .to(".box3", { rotation: 360 }, "+=0.5"); // 在 box2 结束后 0.5 秒开始

// 在特定时间开始
tl.to(".box1", { x: 100 }, 2.5); // 在 2.5 秒开始
```

## ScrollTrigger 基础

### 基本滚动动画

```javascript
gsap.registerPlugin(ScrollTrigger);

gsap.to(".box", {
  x: 500,
  scrollTrigger: {
    trigger: ".box",
    start: "top center", // 当触发器顶部到达视口中心时
    end: "bottom center",
    markers: true, // 仅开发时显示 - 显示开始/结束位置
    scrub: true, // 将动画与滚动条关联
    toggleActions: "play none none reverse" // onEnter onLeave onEnterBack onLeaveBack
  }
});
```

### 开始和结束位置

格式：`"[触发器位置] [视口位置]"`

```javascript
// 常见模式
start: "top top"      // 触发器顶部到达视口顶部
start: "top center"   // 触发器顶部到达视口中心（默认）
start: "top bottom"   // 触发器顶部到达视口底部
start: "center center" // 触发器中心到达视口中心

// 带偏移量
start: "top top+=100"   // 视口顶部下方 100px
start: "top 80%"        // 视口下方 80%
end: "+=500"            // 开始位置后 500px
end: "bottom top"       // 触发器底部到达视口顶部
```

### 滚动同步动画（Scrubbing）

```javascript
// 布尔值：直接与滚动条关联（立即）
scrub: true

// 数字：平滑延迟时间（秒）
scrub: 1  // 需要 1 秒才能"追赶"滚动条
scrub: 0.5 // 更快，更紧密的感觉
```

### 切换动作（Toggle Actions）

在四个滚动点控制动画：

```javascript
toggleActions: "play pause resume reset"
// onEnter | onLeave | onEnterBack | onLeaveBack

// 动作：play, pause, resume, restart, reset, complete, reverse, none
```

常见模式：
```javascript
toggleActions: "play none none none"       // 进入时播放一次
toggleActions: "play none none reverse"    // 正向播放，反向返回
toggleActions: "play complete reverse reset" // 完全控制
toggleActions: "restart pause resume pause"  // 每次进入时重启
```

## 常见模式

### 1. 滚动时淡入

```javascript
gsap.from(".fade-in", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".fade-in",
    start: "top 80%",
    end: "top 50%",
    scrub: 1,
    once: true // 仅动画一次
  }
});
```

### 2. 滚动时固定元素

```javascript
ScrollTrigger.create({
  trigger: ".panel",
  start: "top top",
  end: "+=500", // 滚动 500px 固定
  pin: true,
  pinSpacing: true // 添加间距（默认为 true）
});
```

### 3. 水平滚动区域

```javascript
const sections = gsap.utils.toArray(".panel");

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".container").offsetWidth
  }
});
```

### 4. 视差效果

```javascript
// 较慢移动（背景层）
gsap.to(".bg", {
  y: 200,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// 较快移动（前景层）
gsap.to(".fg", {
  y: -100,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

### 5. 滚动触发的动画时间轴

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".container",
    start: "top top",
    end: "+=500",
    scrub: 1,
    pin: true,
    snap: {
      snapTo: "labels", // 对齐时间轴标签
      duration: { min: 0.2, max: 3 },
      delay: 0.2,
      ease: "power1.inOut"
    }
  }
});

tl.addLabel("start")
  .from(".title", { scale: 0.3, rotation: 45, autoAlpha: 0 })
  .addLabel("color")
  .from(".box", { backgroundColor: "#28a92b" })
  .addLabel("spin")
  .to(".box", { rotation: 360 })
  .addLabel("end");
```

### 6. 批量动画（多个元素）

```javascript
// 遍历多个元素
gsap.utils.toArray(".box").forEach((box, i) => {
  gsap.from(box, {
    y: 100,
    opacity: 0,
    scrollTrigger: {
      trigger: box,
      start: "top 80%",
      end: "top 50%",
      scrub: 1
    }
  });
});

// 或使用 ScrollTrigger.batch
ScrollTrigger.batch(".box", {
  onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.15 }),
  onLeave: batch => gsap.set(batch, { opacity: 0 }),
  start: "top 80%",
  once: true
});
```

### 7. 错开动画

```javascript
gsap.from(".item", {
  y: 50,
  opacity: 0,
  duration: 0.8,
  stagger: 0.1, // 每个元素间隔 0.1 秒
  scrollTrigger: {
    trigger: ".grid",
    start: "top 80%"
  }
});

// 高级错开
gsap.from(".item", {
  scale: 0,
  duration: 1,
  stagger: {
    each: 0.1,
    from: "center", // "start", "center", "end", "edges", 或索引号
    grid: "auto", // 用于网格布局
    ease: "power2.inOut"
  }
});
```

## 集成模式

### 与 Three.js / WebGL 集成

```javascript
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// 动画相机
gsap.to(camera.position, {
  x: 5,
  y: 3,
  z: 10,
  scrollTrigger: {
    trigger: "#section2",
    start: "top top",
    end: "bottom top",
    scrub: 1,
    onUpdate: () => camera.lookAt(scene.position)
  }
});

// 动画网格旋转
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  scrollTrigger: {
    trigger: "#section3",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// 动画材质属性
gsap.to(material, {
  opacity: 0,
  scrollTrigger: {
    trigger: "#section4",
    start: "top center",
    end: "center center",
    scrub: 1
  }
});
```

### 与 React 集成（useGSAP Hook）

```javascript
import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function Component() {
  const container = useRef();
  const box = useRef();

  useGSAP(() => {
    gsap.to(box.current, {
      x: 200,
      scrollTrigger: {
        trigger: box.current,
        start: "top center",
        end: "bottom center",
        scrub: true,
        markers: true
      }
    });
  }, { scope: container }); // 作用域用于清理

  return (
    <div ref={container}>
      <div ref={box} className="box">动画框</div>
    </div>
  );
}
```

### 在 React 中共享时间轴

```javascript
function App() {
  const [tl, setTl] = useState();

  useGSAP(() => {
    const timeline = gsap.timeline();
    setTl(timeline);
  }, []);

  return (
    <div>
      <Box timeline={tl} index={0} />
      <Circle timeline={tl} index={1} />
    </div>
  );
}

function Box({ timeline, index }) {
  const ref = useRef();

  useGSAP(() => {
    timeline && timeline.to(ref.current, { x: 100 }, index * 0.1);
  }, [timeline, index]);

  return <div ref={ref} className="box" />;
}
```

### Locomotive Scroll 集成

```javascript
import LocomotiveScroll from 'locomotive-scroll';

const scroller = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});

ScrollTrigger.scrollerProxy("[data-scroll-container]", {
  scrollTop(value) {
    return arguments.length ? scroller.scrollTo(value, 0, 0) : scroller.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {top: 0, left: 0, width: window.innerWidth, height: window.innerHeight};
  },
  pinType: document.querySelector("[data-scroll-container]").style.transform ? "transform" : "fixed"
});

ScrollTrigger.addEventListener("refresh", () => scroller.update());
ScrollTrigger.refresh();
```

## 高级技巧

### 图像序列滚动

```javascript
const canvas = document.querySelector("canvas");
const context = canvas.getContext("2d");

const images = [];
const imageCount = 147;
const currentFrame = { value: 0 };

for (let i = 0; i < imageCount; i++) {
  const img = new Image();
  img.src = `./frames/frame_${i.toString().padStart(4, '0')}.jpg`;
  images.push(img);
}

images[0].onload = () => {
  canvas.width = images[0].width;
  canvas.height = images[0].height;
  render();
};

function render() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(images[Math.floor(currentFrame.value)], 0, 0);
}

gsap.to(currentFrame, {
  value: imageCount - 1,
  snap: "value",
  ease: "none",
  scrollTrigger: {
    trigger: canvas,
    start: "top top",
    end: "+=500%",
    scrub: true,
    pin: true
  },
  onUpdate: render
});
```

### 平滑滚动到元素

```javascript
gsap.registerPlugin(ScrollToPlugin);

// 滚动到元素
gsap.to(window, {
  duration: 1,
  scrollTo: "#section2",
  ease: "power2.inOut"
});

// 带偏移量
gsap.to(window, {
  duration: 1.5,
  scrollTo: { y: "#section2", offsetY: 50 },
  ease: "expo.inOut"
});

// 水平滚动
gsap.to(".container", {
  duration: 2,
  scrollTo: { x: 1000, autoKill: true }
});
```

### 条件动画（媒体查询）

```javascript
ScrollTrigger.matchMedia({
  // 桌面版
  "(min-width: 800px)": function() {
    gsap.to(".box", {
      x: 500,
      scrollTrigger: {
        trigger: ".box",
        start: "top center",
        end: "bottom top",
        scrub: true
      }
    });
  },

  // 移动版
  "(max-width: 799px)": function() {
    gsap.to(".box", {
      y: 200,
      scrollTrigger: {
        trigger: ".box",
        start: "top 80%",
        scrub: 1
      }
    });
  }
});
```

## 性能最佳实践

### 1. 使用 CSS `will-change`

```css
.animated-element {
  will-change: transform, opacity;
}
```

### 2. 限制重绘

```javascript
// 良好：动画 transform/opacity（GPU 加速）
gsap.to(".box", { x: 100, opacity: 0.5 });

// 避免：动画布局属性
// gsap.to(".box", { width: 500, height: 300 }); // 导致重排
```

### 3. 释放 ScrollTriggers

```javascript
// 释放单个触发器
const trigger = ScrollTrigger.create({ /* ... */ });
trigger.kill();

// 释放所有触发器
ScrollTrigger.getAll().forEach(t => t.kill());

// 在 React 中进行清理
useGSAP(() => {
  const tween = gsap.to(".box", { /* ... */ });

  return () => {
    tween.kill();
  };
}, []);
```

### 4. 防抖调整大小

ScrollTrigger 会自动处理，但自定义调整大小逻辑：

```javascript
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    ScrollTrigger.refresh();
  }, 250);
});
```

### 5. 使用 `invalidateOnRefresh`

对于在调整大小时变化的动态值：

```javascript
gsap.to(".box", {
  x: () => window.innerWidth / 2, // 动态值
  scrollTrigger: {
    trigger: ".box",
    start: "top center",
    invalidateOnRefresh: true // 调整大小时重新计算 x
  }
});
```

## 常见陷阱

### 1. 同一元素上使用多个补间动画

```javascript
// 问题：第二个补间与第一个冲突
gsap.to('h1', { x: 100, scrollTrigger: { /* ... */ } });
gsap.to('h1', { x: 200, scrollTrigger: { /* ... */ } }); // 跳跃！

// 解决方案 1：使用 fromTo
gsap.fromTo('h1', { x: 100 }, { x: 200, scrollTrigger: { /* ... */ } });

// 解决方案 2：使用 immediateRender: false
gsap.to('h1', { x: 200, immediateRender: false, scrollTrigger: { /* ... */ } });

// 解决方案 3：将 ScrollTrigger 应用于时间轴
const tl = gsap.timeline({ scrollTrigger: { /* ... */ } });
tl.to('h1', { x: 100 })
  .to('h1', { x: 200 });
```

### 2. 未使用循环处理多个元素

```javascript
// 错误：一次性动画所有元素
gsap.to('.section', {
  y: -100,
  scrollTrigger: { trigger: '.section', scrub: true }
});

// 正确：为每个元素设置单独触发器
gsap.utils.toArray('.section').forEach(section => {
  gsap.to(section, {
    y: -100,
    scrollTrigger: { trigger: section, scrub: true }
  });
});
```

### 3. 忘记注册插件

```javascript
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollToPlugin } from 'gsap/ScrollToPlugin';

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin); // 必须注册!
```

### 4. 时间轴中的嵌套 ScrollTriggers

```javascript
// 错误：时间轴中每个补间动画的 ScrollTrigger
const tl = gsap.timeline();
tl.to('.box1', { x: 100, scrollTrigger: { /* ... */ } }) // 不要这样做!
  .to('.box2', { y: 100, scrollTrigger: { /* ... */ } });

// 正确：在父时间轴上使用 ScrollTrigger
const tl = gsap.timeline({
  scrollTrigger: { /* ... */ }
});
tl.to('.box1', { x: 100 })
  .to('.box2', { y: 100 });
```

## 缓动函数参考

```javascript
// 力度缓动（最常见）
ease: "power1.out"  // 缓和减速
ease: "power2.inOut" // 平滑加速/减速
ease: "power3.in"   // 强加速
ease: "power4.out"  // 非常强的减速

// 特殊缓动
ease: "elastic.out"  // 弹性过冲
ease: "back.out"     // 轻微过冲
ease: "bounce.out"   // 弹跳效果
ease: "circ.inOut"   // 圆形运动感
ease: "expo.inOut"   // 指数（戏剧性）

// 线性（用于滚动同步动画）
ease: "none"
```

## ScrollTrigger 方法

```javascript
// 刷新所有 ScrollTriggers（DOM 变化后）
ScrollTrigger.refresh();

// 获取所有 ScrollTriggers
const triggers = ScrollTrigger.getAll();

// 获取特定 ID 的触发器
const st = ScrollTrigger.getById("myTrigger");

// 释放触发器
st.kill();

// 更新触发器
st.scroll(500); // 程序设置滚动位置
st.enable();
st.disable();

// 全局 ScrollTrigger 配置
ScrollTrigger.config({
  limitCallbacks: true, // 提高性能
  syncInterval: 15 // 滚动检查节流（毫秒）
});

// 调试模式
ScrollTrigger.defaults({
  markers: true // 在所有触发器上显示标记
});
```

## 资源

此技能包含捆绑资源：

### references/
- `api_reference.md`: 快速 API 参考（补间方法、时间轴方法、ScrollTrigger 属性）
- `easing_guide.md`: 视觉缓动参考及使用案例
- `common_patterns.md`: 常见场景的复制粘贴模式

### scripts/
- `generate_animation.py`: 生成 GSAP 代码模板
- `timeline_builder.py`: 交互式时间轴序列构建器

### assets/
- `starter_scroll/`: 完整滚动驱动网站模板
- `easings/`: 缓动可视化 HTML 工具
- `examples/`: 真实世界的 ScrollTrigger 示例

## 何时使用此技能

使用此技能当：
- 创建平滑的 Web 动画
- 构建滚动驱动体验
- 实现视差效果
- 序列化复杂动画
- 动画 DOM、SVG、Canvas 或 WebGL
- 与 Three.js 或 React 集成动画
- 构建滚动叙事网站
- 创建交互式 UI 过渡

对于 Three.js 特定动画，也参考 **threejs-webgl** 技能。
对于具有内置动画的 React 组件，参考 **motion-framer** 技能。
