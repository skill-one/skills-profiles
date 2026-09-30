---
name: premium-frontend-design
description: 创建获奖级、电影感的动态前端界面。结合10年以上创意前端经验与卓越技术。专精于WebGL、自定义着色器、高端动画和独特美学，足以在Awwwards上赢得赞誉。适用于构建登陆页、仪表盘、平台或任何“平庸AI垃圾”无法接受的界面。
---

# 高级前端设计技能

这项技能指导创建**具有生命力的生产级前端界面**——不是通用的，不是复制粘贴的，而是真正精心打造的用户体验，让用户难以忘怀。

> "优秀界面与难忘界面的区别在于每个像素处的意图性。"

---

## 依赖项（灵活选择——根据需求选择）

这项技能是**框架无关的**。根据用户偏好和项目需求选择包。

### 核心 3D（适用于 WebGL 模板）
```bash
pnpm add three @react-three/fiber @react-three/drei
```

### 动画（根据用户偏好选择）

| 库 | 适用于 | 复杂度 | 打包大小 |
|---|--------|--------|----------|
| **CSS/Tailwind** | 简单过渡、微交互 | 低 | 0KB |
| **Framer Motion** | React-native 感觉、布局动画、手势 | 中 | ~30KB |
| **GSAP** | 复杂时间线、滚动触发、文本效果 | 高 | ~60KB |
| **GSAP + Club** | SplitText、ScrollTrigger、MorphSVG | 高 | ~80KB |

```bash
# Framer Motion（更简单、React 风格）
pnpm add framer-motion

# GSAP（强大、基于时间线）
pnpm add gsap @gsap/react
# 注意：SplitText、ScrollTrigger 需要 GSAP Club 许可证
```

**决策指南**：
- 用户说“简单”或“轻量级”→ CSS + Framer Motion
- 用户说“复杂动画”或“滚动效果”→ GSAP
- 用户说“文本动画”或“分割文本”→ GSAP + SplitText
- 用户未指定 → 默认使用 Framer Motion（更简单的 API）

### 可选增强功能
```bash
# 网格渐变（用于 mesh-gradient-hero）
pnpm add @paper-design/shaders-react

# 图标
pnpm add lucide-react

# 图表/Sparklines（用于仪表板）
pnpm add recharts
# 或轻量级：pnpm add @visx/shape @visx/scale
```

### 浏览器兼容性说明
- `backdrop-filter`：Firefox < 103 不支持（添加后备背景）
- WebGL：为旧设备提供 CSS 后备
- `@starting-style`：Chrome 117+、Safari 17.4+（渐进增强）

---

## 核心理念

### “有生命力”原则

当界面有生命力时：
- **它呼吸**：微妙的氛围动画、粒子或着色器效果创造持续但非分散的运动
- **它响应**：微交互承认每个用户操作并提供令人满意的反馈
- **它有深度**：图层、视差、玻璃形态和阴影创造空间维度
- **它惊喜**：至少有一个元素以令人愉快的方式打破预期

### 设计思维（在编写任何代码之前）

在编写第一行代码之前，回答这些问题：

1. **目的**：这个问题解决了什么？谁使用它？
2. **基调**：选择一个极端方向（而不是混合）：
   - 极简主义
   - 极致混乱
   - 复古未来/赛博朋克
   - 有机/自然
   - 奢华/精致
   - 滑稽/玩具般
   - 编辑/杂志
   - 布鲁特主义/原始
   - 装饰艺术/几何
   - 工业化/实用主义
   - 生物发光/科幻
   - 任务控制/技术

3. **唯一要素**：用户会记住什么？每个伟大的界面都有一个标志性时刻。

4. **限制**：框架、性能预算、无障碍性要求。

**关键**：大胆的极致主义和精致的极简主义都有效。关键在于**意图性而非强度**。一个完美执行的动画胜过 50 个平庸的动画。

---

## 娱乐与清晰度框架

当简报模糊或需要证明设计决策时，使用这个框架。目标是**娱乐性与目的性并存**。

### 1. 层级限制

- **1 个英雄装饰**（着色器、粒子系统或地球仪）。其他一切都支持可读性。
- **1 个辅助装饰**（微交互、动画统计卡或发光 CTA）。不能再多了。
- 布局规则：`英雄（狂野）→ 内容块（平静）→ 证据（平静）→ CTA（突出）`。
- 如果页面有多于一个滚动长度的文本，每隔一个部分应该是静态的。

### 2. 字体排版纪律

- **最多 2 个标题字体**（显示+正文）。数据仅使用等宽字体。
- 标题字间距 ≥ -0.04em。更紧的会杀死可读性。
- 正文宽度目标：桌面 55-75 个字符/行，移动端 35-45 个字符/行。
- 始终将大号显示文本与下方不超过 80 个字符的普通支持句搭配。

### 3. 颜色与对比度规则

- 限制霓虹灯使用到**主要 CTA + 1 个强调色**。其他一切都保持在锌/中性调色板中。
- 如果背景繁忙（着色器、渐变、粒子），在文本后面添加 `bg-black/70` 或 `bg-slate-950/70` 的遮罩。
- 即使美学是赛博朋克，也要保持对比度比例 ≥ 4.5:1 的正文副本。
- 在发货前添加灰度预览检查：如果看起来模糊，请减少调色板。

### 4. 动画限制

- **默认**：CSS 或 Framer Motion，持续时间 ≤ 400ms，缓动 `cubic-bezier(0.34, 1.56, 0.64, 1)`。
- **仅当简报明确要求电影或交互式体验时，才升级到 GSAP/WebGL**。
- 每个视口最多 1 个连续动画（例如，着色器或波浪条，不能两者都有）。
- 提供一个“平静模式”：当 `prefers-reduced-motion` 开启或用户滚动到英雄之后时禁用非必要动画。

### 5. 当要求模糊时

| 情况 | 默认 | 可选升级 |
|------|------|----------|
| 用户只说“干净的 SaaS” | `mesh-gradient-hero` + `bento-grid` | 如果他们后来要求“更多活力”，交换英雄背景为 CPPN |
| 用户说“仪表板”但没有特色 | `bento-grid` + `dashboard-widgets` + CSS 发光药丸 | 仅在数据可视化确认后添加 `digital-liquid` 着色器 |
| 用户说“英雄部分”但没有其他 | 文本优先布局 + CSS 渐变 | 提议着色器/地球仪，但永远不要作为默认值 |

如果提示没有明确提到 WebGL，则假设**CSS 优先**，仅在用户接受成本时选择着色器。

---

## 反模式（绝对不要这样做）

### 视觉反模式
❌ 默认使用白色/浅色背景（暗模式是高级的）
❌ 通用渐变（白色上的紫到蓝是 AI 拙劣之作）
❌ 均匀分布、胆怯的调色板
❌ 静态、无生气的背景
❌ 千篇一律的组件布局
❌ 缺少加载/过渡状态
❌ 令人震惊的、未缓动的动画

### 字体反模式
❌ Inter、Roboto、Arial、系统字体用于标题
❌ 所有内容使用相同字体
❌ 默认行高和字间距
❌ 乏味、可预测的字体比例

### 代码反模式
❌ 随机散布的内联样式
❌ 没有用于主题的 CSS 变量
❌ 没有 `will-change` 或 GPU 加速的动画
❌ 没有 `requestAnimationFrame` 的 Canvas/WebGL
❌ `useEffect` 中缺少清理

---

## 设计系统

### 1. 颜色架构

**规则：一个主导强调色，其他都支持它。**

```typescript
// 高级暗色主题（默认）
const colors = {
  // 背景（从最暗到最亮）
  bg: {
    void: '#000000',      // 真黑以获得最大对比度
    primary: '#050505',   // 主要背景
    elevated: '#0a0a0a',  // 卡片、模态框
    subtle: '#111111',    // 悬停状态
  },
  
  // 玻璃表面
  glass: {
    bg: 'rgba(255, 255, 255, 0.03)',
    border: 'rgba(255, 255, 255, 0.08)',
    hover: 'rgba(255, 255, 255, 0.06)',
  },
  
  // 文本层级
  text: {
    primary: '#ffffff',
    secondary: '#a1a1aa',   // zinc-400
    muted: '#71717a',       // zinc-500
    ghost: '#3f3f46',       // zinc-700
  },
  
  // 强调色（每个项目选择一个）
  accent: '#ff4d00',  // 霓虹橙色
  // accent: '#00f3ff',  // 霓虹青色
  // accent: '#ccff00',  // 霓虹酸绿
  // accent: '#F5E445',  // 高级黄色
  // accent: '#a855f7',  // 电光紫色
}
```

**强调色使用规则**：
- 主要操作：全强调色
- 次要元素：20% 不透明度的强调色
- 边框/线条：30% 不透明度的强调色
- 发光：模糊的强调色，40-60% 不透明度
- 永远不要用强调色作为大面积背景

### 2. 字体排版系统

**规则：显示字体用于冲击力，正文字体用于阅读，等宽字体用于数据。**

```css
/* 层级 1：显示/标题 - 粗体、有特色 */
--font-display: 'Chakra Petch', 'Orbitron', 'Bebas Neue', 'Playfair Display';

/* 层级 2：标题 - 几何、现代 */
--font-heading: 'Manrope', 'Outfit', 'Syne', 'Space Grotesk';

/* 层级 3：正文 - 干净、高度易读 */
--font-body: 'Plus Jakarta Sans', 'DM Sans', 'Satoshi', 'General Sans';

/* 层级 4：数据/代码 - 永远等宽 */
--font-mono: 'JetBrains Mono', 'Fira Code', 'IBM Plex Mono';
```

**排版模式**：

```css
/* 英雄标题：巨大、紧凑、激进 */
.headline {
  font-family: var(--font-display);
  font-size: clamp(3rem, 12vw, 10rem);
  font-weight: 800;
  line-height: 0.9;
  letter-spacing: -0.03em;
  text-transform: uppercase;
}

/* 章节标题 */
.section-title {
  font-family: var(--font-heading);
  font-size: clamp(1.5rem, 4vw, 3rem);
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* 技术标签 */
.label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

/* 数据显示 */
.data {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}
```

### 3. 间距与布局

**规则：不对称创造兴趣。网格只是起点，不是监狱。**

```css
/* 间距比例（一致使用） */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */

/* 容器使用大间距 */
.container {
  padding-inline: clamp(1rem, 5vw, 4rem);
}

/* 英雄部分需要呼吸空间 */
.hero {
  min-height: 100vh;
  padding-block: var(--space-32);
}
```

**Bento 网格模式**（用于仪表板）：
```css
.bento {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(150px, auto);
  gap: var(--space-4);
}

/* 特性卡片跨越 */
.card-hero { grid-column: span 2; grid-row: span 2; }
.card-wide { grid-column: span 2; }
.card-tall { grid-row: span 2; }
```

---

## 视觉效果库

### 1. 玻璃形态（正确方法）

```css
.glass {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

/* 提升玻璃（用于模态框、下拉菜单） */
.glass-elevated {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

### 2. CRT 扫描线叠加

```css
.scanlines::before {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1) 0px,
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  z-index: 9999;
}
```

### 3. 电影颗粒纹理

```css
.grain::before {
  content: '';
  position: fixed;
  inset: 0;
  opacity: 0.03;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}
```

### 4. 科技网格背景

```css
.tech-grid {
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 60px 60px;
}
```

### 5. 霓虹发光效果

```css
/* 文本发光 */
.neon-text {
  text-shadow: 
    0 0 10px currentColor,
    0 0 20px currentColor,
    0 0 40px currentColor,
    0 0 80px currentColor;
}

/* 盒子发光 */
.neon-box {
  box-shadow: 
    0 0 20px var(--accent-alpha-40),
    0 0 40px var(--accent-alpha-20),
    inset 0 0 20px var(--accent-alpha-10);
}

/* 边框发光 */
.neon-border {
  border: 1px solid var(--accent);
  box-shadow: 
    0 0 10px var(--accent-alpha-50),
    inset 0 0 10px var(--accent-alpha-20);
}
```

---

## 动画模式

### 哲学
- **进入动画**：使用一次，使其值得
- **微交互**：微妙、快速（150-300ms）
- **环境运动**：无限、非常慢、不分散
- **页面过渡**：平滑、协调

### 选择正确的工具

| 需求 | 使用 | 原因 |
|------|------|------|
| 悬停/焦点状态 | CSS | 无需 JS，即时 |
| 简单进入 | CSS keyframes | 轻量级 |
| 布局动画 | Framer Motion | `layout` 属性魔法 |
| 手势基础 | Framer Motion | 内置拖动/平移 |
| 滚动触发 | GSAP ScrollTrigger | 最强大 |
| 文本分割 | GSAP SplitText | 行业标准 |
| 复杂时间线 | GSAP | 精确控制 |
| SVG 变形 | GSAP MorphSVG | 没有替代方案 |

**默认使用更简单的解决方案。仅在需要时升级复杂性。**

### CSS Keyframes 库

```css
@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes slide-in-right {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes rotate-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes scan-line {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}
```

### 错落有致进入模式

```css
.stagger-container > * {
  opacity: 0;
  animation: fade-up 0.6s ease-out forwards;
}

.stagger-container > *:nth-child(1) { animation-delay: 0.1s; }
.stagger-container > *:nth-child(2) { animation-delay: 0.2s; }
.stagger-container > *:nth-child(3) { animation-delay: 0.3s; }
.stagger-container > *:nth-child(4) { animation-delay: 0.4s; }
.stagger-container > *:nth-child(5) { animation-delay: 0.5s; }
```

### CSS-Only 模式（零依赖）

```css
/* 视图过渡进入（Chrome 111+、Safari 18+） */
@supports (view-transition-name: none) {
  .card {
    view-transition-name: card;
  }
  
  ::view-transition-old(card),
  ::view-transition-new(card) {
    animation-duration: 0.3s;
  }
}

/* 滚动驱动动画（Chrome 115+） */
@supports (animation-timeline: scroll()) {
  .parallax-bg {
    animation: parallax linear;
    animation-timeline: scroll();
  }
  
  @keyframes parallax {
    from { transform: translateY(0); }
    to { transform: translateY(-30%); }
  }
}

/* 悬停弹簧感 */
.spring-hover {
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.spring-hover:hover {
  transform: scale(1.05);
}

/* 发光脉冲 */
.glow-pulse {
  animation: glow-pulse 2s ease-in-out infinite;
}
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 20px var(--accent-alpha-40); }
  50% { box-shadow: 0 0 40px var(--accent-alpha-60); }
}
```

### GSAP 模式（当需要力量时）

```typescript
// Stagger entrance on scroll
gsap.from('.card', {
  scrollTrigger: {
    trigger: '.cards-section',
    start: 'top 80%',
  },
  y: 60,
  opacity: 0,
  duration: 0.8,
  stagger: 0.1,
  ease: 'power3.out',
});

// Text scramble effect
const scrambleText = (el: HTMLElement, text: string) => {
  const chars = '!<>-_\\/[]{}—=+*^?#';
  let iteration = 0;
  
  const interval = setInterval(() => {
    el.innerText = text
      .split('')
      .map((char, i) => 
        i < iteration ? char : chars[Math.floor(Math.random() * chars.length)]
      )
      .join('');
    
    if (iteration >= text.length) clearInterval(interval);
    iteration += 1/3;
  }, 30);
};

// Smooth parallax
gsap.to('.parallax-bg', {
  scrollTrigger: {
    scrub: 1,
  },
  y: '-30%',
  ease: 'none',
});
```

### Framer Motion Patterns

```tsx
// Page transitions
<AnimatePresence mode="wait">
  <motion.div
    key={page}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3 }}
  />
</AnimatePresence>

// Hover glow effect
<motion.div
  whileHover={{ 
    scale: 1.02,
    boxShadow: '0 0 30px rgba(255, 77, 0, 0.4)',
  }}
  transition={{ type: 'spring', stiffness: 300 }}
/>

// Stagger children
<motion.div
  initial="hidden"
  animate="visible"
  variants={{
    hidden: {},
    visible: { transition: { staggerChildren: 0.1 } },
  }}
>
  {items.map(item => (
    <motion.div
      key={item.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 },
      }}
    />
  ))}
</motion.div>
```

---

## 3D & WebGL Patterns

### Tech Stack
```bash
npm install three @react-three/fiber @react-three/drei
```

### Basic Scene Setup

```tsx
import { Canvas } from '@react-three/fiber';
import { Stars, Float, MeshDistortMaterial } from '@react-three/drei';

const Scene = () => (
  <Canvas
    camera={{ position: [0, 0, 5], fov: 75 }}
    style={{ position: 'fixed', inset: 0, zIndex: -1 }}
  >
    <ambientLight intensity={0.2} />
    <pointLight position={[10, 10, 10]} color="#ff4d00" />
    <Stars radius={100} depth={50} count={3000} />
    {/* Your 3D content */}
  </Canvas>
);
```

### Particle Sphere (Data Globe)

```tsx
const ParticleSphere = ({ count = 3000, color = '#ff4d00' }) => {
  const ref = useRef<THREE.Points>(null);
  
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const r = 2;
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    }
    return pos;
  }, [count]);
  
  useFrame(() => {
    if (ref.current) ref.current.rotation.y += 0.001;
  });
  
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.02} color={color} transparent opacity={0.8} />
    </points>
  );
};
```

### Sentient Core (AI Brain)

```tsx
const SentientCore = () => (
  <Float speed={2} rotationIntensity={0.5}>
    <mesh>
      <sphereGeometry args={[1.5, 64, 64]} />
      <MeshDistortMaterial
        color="#00f3ff"
        wireframe
        distort={0.4}
        speed={2}
      />
    </mesh>
  </Float>
);
```

### Performance Rules
1. Always use `requestAnimationFrame` via `useFrame`
2. Reduce particle counts on mobile (check `window.innerWidth`)
3. Use `useMemo` for geometry/position calculations
4. Cleanup animations in `useEffect` return
5. Set `transparent` and `opacity` for depth sorting

---

## Component Patterns

### 1. Loading + Page Transitions

**Default (ship this unless user asks otherwise):**
- Skeleton placeholders on cards/sections (see shimmer pattern above)
- Simple fade/slide page transition using CSS or Framer Motion route transitions

**Optional Cinematic Mode (only when the user wants a narrative boot sequence and there's time/budget):**
- GSAP-powered preloader with boot logs, text scramble, shader/WebGL background
- Coordinated timeline that fades into actual content once data is ready

### 2. Glassmorphic Navbar

```tsx
<nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50">
  <div className="glass rounded-full px-6 py-3 flex items-center gap-8">
    <Logo />
    <NavLinks />
    <ThemeToggle />
    <CTA />
  </div>
</nav>
```

### 3. Live Terminal

```tsx
const Terminal = ({ logs }) => {
  const scrollRef = useRef();
  
  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [logs]);
  
  return (
    <div className="glass font-mono text-xs">
      <header className="border-b border-white/10 px-4 py-2">
        <span className="text-accent">&gt;</span> System Logs
        <span className="ml-auto w-2 h-2 bg-green-500 rounded-full animate-pulse" />
      </header>
      <div ref={scrollRef} className="h-64 overflow-y-auto p-4">
        {logs.map(log => (
          <div key={log.id}>
            <span className="text-zinc-600">{log.time}</span>
            <span className={levelColor[log.level]}>[{log.level}]</span>
            <span>{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 4. Stat Cards with Sparklines

```tsx
const StatCard = ({ icon, label, value, change, trend }) => (
  <motion.div
    whileHover={{ scale: 1.02, boxShadow: '0 0 30px var(--accent-alpha-30)' }}
    className="glass p-4"
  >
    <div className="flex justify-between">
      <div className="p-2 rounded-lg bg-accent/10 text-accent">{icon}</div>
      <span className={change > 0 ? 'text-green-400' : 'text-red-400'}>
        {change > 0 ? '+' : ''}{change}%
      </span>
    </div>
    <div className="mt-4 font-mono text-2xl font-bold">{value}</div>
    <div className="text-xs text-zinc-500 uppercase">{label}</div>
    <Sparkline data={trend} className="mt-2 h-8" />
  </motion.div>
);
```

---

## Quality Checklist

Before shipping, verify:

### Visual
- [ ] Dark mode is default and premium-feeling
- [ ] ONE dominant accent color used consistently
- [ ] Glass effects have proper blur AND borders
- [ ] Scanlines or grain overlay for texture
- [ ] No pure white text on dark (#f4f4f5 max)

### Typography
- [ ] Display font for headlines (not Inter/Roboto)
- [ ] Monospace for ALL data/code/numbers
- [ ] Proper hierarchy (3-4 distinct levels)
- [ ] Tracking adjusted for large text

### Animation
- [ ] Entrance animations on load (staggered)
- [ ] Hover states with transform AND glow
- [ ] Smooth 60fps for all canvas
- [ ] No animation without purpose

### Code
- [ ] CSS variables for all colors
- [ ] Responsive (mobile-first)
- [ ] Cleanup functions in useEffect
- [ ] Error boundaries for 3D content

---

## Accessibility (Premium ≠ Inaccessible)

Great design is inclusive. These aren't optional.

### Motion Sensitivity

```css
/* ALWAYS respect user preferences */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```tsx
// React hook for motion preference
const usePrefersReducedMotion = () => {
  const [prefersReduced, setPrefersReduced] = useState(false);
  
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mq.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  
  return prefersReduced;
};

// Usage
const shouldAnimate = !usePrefersReducedMotion();
```

### WebGL Accessibility

```tsx
// Always mark decorative 3D as hidden
<div aria-hidden="true" className="pointer-events-none">
  <Canvas>{/* decorative background */}</Canvas>
</div>

// Provide text alternatives for meaningful 3D
<div role="img" aria-label="3D visualization of global network connections">
  <Canvas>{/* data visualization */}</Canvas>
</div>
```

### Color Contrast

| Element | Minimum Ratio | Target |
|---------|---------------|--------|
| Body text | 4.5:1 | 7:1 |
| Large text (18px+) | 3:1 | 4.5:1 |
| UI components | 3:1 | 4.5:1 |
| Decorative | N/A | N/A |

```css
/* Safe text colors on dark backgrounds */
--text-primary: #ffffff;     /* ✓ 21:1 on #000 */
--text-secondary: #a1a1aa;   /* ✓ 7.2:1 on #000 */
--text-muted: #71717a;       /* ✓ 4.6:1 on #000 */
--text-ghost: #52525b;       /* ⚠ 3.2:1 - decorative only */
```

### Keyboard Navigation

```tsx
// Interactive 3D elements need keyboard support
<mesh
  tabIndex={0}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  onClick={handleClick}
/>

// Focus indicators for glass components
.glass:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

---

## Mobile & Responsive Strategy

Premium experiences adapt gracefully. Don't just shrink — reimagine.

### WebGL Fallbacks

```tsx
// Detect low-power devices
const useIsLowPowerDevice = () => {
  const [isLowPower, setIsLowPower] = useState(false);
  
  useEffect(() => {
    const isLow = 
      window.innerWidth < 768 ||
      navigator.hardwareConcurrency <= 4 ||
      /Android|iPhone|iPad/.test(navigator.userAgent);
    setIsLowPower(isLow);
  }, []);
  
  return isLowPower;
};

// Usage in hero components
const HeroBackground = () => {
  const isLowPower = useIsLowPowerDevice();
  
  if (isLowPower) {
    return <CSSGradientFallback />; // Lighter alternative
  }
  
  return <WebGLBackground />;
};
```

### Performance Budgets

| Device | JS Budget | Animation Target |
|--------|-----------|------------------|
| Desktop | < 500KB | 60fps WebGL |
| Tablet | < 300KB | 30fps or CSS-only |
| Mobile | < 150KB | CSS-only, no WebGL |

### Touch Interactions

```tsx
// Replace hover with tap/long-press on mobile
<motion.div
  whileHover={{ scale: 1.02 }}  // Desktop
  whileTap={{ scale: 0.98 }}    // Mobile
  onTouchStart={handleTouch}
/>

// Increase touch targets
.button {
  min-height: 44px;  /* Apple HIG */
  min-width: 44px;
  padding: 12px 24px;
}
```

### Responsive Typography

```css
/* Fluid type scale */
--text-hero: clamp(2.5rem, 8vw, 7rem);
--text-h1: clamp(2rem, 5vw, 4rem);
--text-h2: clamp(1.5rem, 3vw, 2.5rem);
--text-body: clamp(1rem, 2vw, 1.125rem);

/* Reduce letter-spacing on mobile */
@media (max-width: 768px) {
  .headline {
    letter-spacing: -0.02em; /* Less aggressive than desktop */
  }
}
```

---

## Loading & Error States

Premium UX handles every state beautifully.

### Skeleton Loaders

```tsx
// Glass skeleton with shimmer
const Skeleton = ({ className }: { className?: string }) => (
  <div 
    className={`relative overflow-hidden rounded-lg bg-white/5 ${className}`}
  >
    <div 
      className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent"
    />
  </div>
);

// Usage
<div className="space-y-4">
  <Skeleton className="h-8 w-3/4" />
  <Skeleton className="h-4 w-full" />
  <Skeleton className="h-4 w-5/6" />
</div>
```

```css
@keyframes shimmer {
  100% { transform: translateX(100%); }
}
```

### Error Boundaries (Styled)

```tsx
const ErrorFallback = ({ error, resetErrorBoundary }) => (
  <div className="glass p-8 text-center">
    <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-red-500/10 flex items-center justify-center">
      <AlertTriangle className="h-8 w-8 text-red-400" />
    </div>
    <h2 className="text-xl font-semibold text-white mb-2">
      Something went wrong
    </h2>
    <p className="text-zinc-400 mb-4 font-mono text-sm">
      {error.message}
    </p>
    <button 
      onClick={resetErrorBoundary}
      className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition"
    >
      Try again
    </button>
  </div>
);
```

### Empty States

```tsx
const EmptyState = ({ 
  icon: Icon, 
  title, 
  description, 
  action 
}: EmptyStateProps) => (
  <div className="flex flex-col items-center justify-center py-16 text-center">
    <div className="mb-4 rounded-full bg-white/5 p-4">
      <Icon className="h-8 w-8 text-zinc-500" />
    </div>
    <h3 className="text-lg font-medium text-white mb-1">{title}</h3>
    <p className="text-zinc-400 mb-4 max-w-sm">{description}</p>
    {action}
  </div>
);

// Usage
<EmptyState
  icon={Inbox}
  title="No messages yet"
  description="When you receive messages, they'll appear here."
  action={<Button>Send your first message</Button>}
/>
```

### Loading States for Data

```tsx
// Optimistic UI with rollback
const [items, setItems] = useState(data);
const [pending, startTransition] = useTransition();

const addItem = (newItem) => {
  // Optimistic update
  setItems(prev => [...prev, { ...newItem, pending: true }]);
  
  startTransition(async () => {
    try {
      await api.createItem(newItem);
    } catch {
      // Rollback on error
      setItems(prev => prev.filter(i => i.id !== newItem.id));
      toast.error('Failed to add item');
    }
  });
};
```

---

## Framework Integration

### Next.js App Router

```tsx
// Client boundary for WebGL components
// app/components/hero-client.tsx
'use client';

import dynamic from 'next/dynamic';

// Lazy load heavy 3D components
const WebGLHero = dynamic(() => import('./webgl-hero'), {
  ssr: false,
  loading: () => <HeroSkeleton />,
});

export default function HeroClient() {
  return <WebGLHero />;
}
```

```tsx
// Server component wrapper
// app/page.tsx
import HeroClient from './components/hero-client';

export default function Page() {
  return (
    <main>
      {/* Server-rendered SEO content */}
      <h1 className="sr-only">Your SEO Title</h1>
      
      {/* Client-side 3D hero */}
      <HeroClient />
    </main>
  );
}
```

### SEO for WebGL Content

```tsx
// WebGL isn't crawlable - always provide text alternatives
<section aria-labelledby="hero-title">
  {/* Hidden but crawlable */}
  <h1 id="hero-title" className="sr-only">
    AI-Powered Trading Platform
  </h1>
  <p className="sr-only">
    {seoDescription}
  </p>
  
  {/* Visual hero (not crawled) */}
  <div aria-hidden="true">
    <Canvas>...</Canvas>
  </div>
  
  {/* Visible text (crawled) */}
  <div className="relative z-10">
    <span className="text-7xl">{visibleTitle}</span>
  </div>
</section>
```

### Data Fetching with Loading States

```tsx
// Server Component with Suspense
import { Suspense } from 'react';

async function DashboardData() {
  const data = await fetchDashboardData();
  return <DashboardWidgets data={data} />;
}

export default function Dashboard() {
  return (
    <div className="bento-grid">
      <Suspense fallback={<WidgetSkeleton />}>
        <DashboardData />
      </Suspense>
    </div>
  );
}
```

---

## Template Quick Reference

| 模板 | 属性 | WebGL | 移动端回退 | 最佳动画库 |
|------|------|------|------------|------------|
| `cppn-hero` | `title`, `description`, `ctaButtons`, `microDetails` | 是 | CSS 渐变 | GSAP (SplitText) |
| `mesh-gradient-hero` | `colors[]`, `speed`, `distortion`, `swirl` | 否* | 原生 | Framer Motion |
| `wave-hero` | `title`, `subtitle`, `placeholder`, `onPromptSubmit` | 是 | 纯色背景 | GSAP |
| `globe-hero` | `globeImage`, `dashboardImage`, `accentColor` | 否 | 原生 | Framer Motion |
| `hero-section` | `title`, `badge`, `primaryCTA`, `accentColor` | 是 | 星空 CSS | 两者皆可 |
| `bento-grid` | `children` (卡片布局) | 否 | 原生 | CSS 或 Framer |
| `dashboard-widgets` | `value`, `change`, `trend[]` | 否 | 原生 | Framer Motion |
| `terminal` | `logs[]`, `title` | 否 | 原生 | CSS |
| `preloader` | `onComplete`, `messages[]` | 可选 | CSS 版本 | GSAP |
| `glass-components` | 各种 | 否 | 原生 | CSS |

*`mesh-gradient-hero` 使用 `@paper-design/shaders-react` (Canvas，非 WebGL)

---

## 模板操作手册 (从基础开始，有意叠加惊艳效果)

| 目标 | 基准 (清晰优先) | 可选的惊艳升级 | 如果... |
|------|-----------------|----------------|--------|
| 市场 / 等待名单 | `mesh-gradient-hero` + `glass-components` + `bento-grid` 值属性 | 交换英雄为 `cppn-hero` 或添加 `wave-hero` 社会证明带 | 文案是长篇的或产品合规性重 |
| AI / 研究着陆页 | `cppn-hero` + `dashboard-widgets` (指标) + `terminal` 日志 | 添加 `holographic` 光栅部分或 `globe-hero` 间奏 | 用户需要打印友好的交付物 |
| 加密货币 / 金融 | `globe-hero` + `bento-grid` KPI + `dashboard-widgets` + CTA 条 | 添加 `data-grid` 光栅背景或滚动行情 | 性能预算 < 200KB 或仅移动端 |
| 开发者工具 | `wave-hero` + `terminal` + `glass-components` 卡片 | 引入 `digital-liquid` 光栅或 3D 设备模拟 | 受众是企业买家需要保守的语气 |
| 产品仪表盘 | `bento-grid` + `dashboard-widgets` + `mesh-gradient-hero` (静态) | 添加迷你 WebGL 模块 (有感知的核心，粒子地球) | 数据密集，需要表格清晰度 |

### 布局流程配方

1. **英雄 (标志性华彩)** → 关键指标/值属性 (平静) → 产品证明 (屏幕) → 评价/徽标 → CTA (发光按钮).
2. **仪表盘页面**: 上方摘要 (极简) → 特性网格 (非对称) → 实时数据 (终端/火花线) → 帮助/资源 (平静).
3. **文档/平台**: 干净的标题 (`mesh-gradient-hero` 在 CSS 模式) → 导航网格 → 内容区域 (等宽字体) → CTA.

每个流程最多应有 **两个高饱和度面板**。如果您需要更多活力，请动画 CTA 或强调边框，而不是添加另一个光栅。

---

## 模板 Remix & 适应模式

| 需求 | 操作 | 备注 |
|------|------|------|
| **降级 WebGL → CSS** | 用 `mesh-gradient-hero` 替换 `cppn-hero`，保持相同文案。交换光栅背景为 `bg-gradient-to-b`。 | 当用户提到“移动优先”，“性能”或“轻量级”时使用。 |
| **升级 CSS → WebGL** | 从 `mesh-gradient-hero` 开始，然后注入 `ShaderBackground` 并重用 `cppn-hero` 的属性。 | 仅在确认客户想要“电影感”或“实验性”之后。 |
| **光栅交换** | 任何使用光栅的英雄都可以通过交换导入来切换到另一个 (例如，`holographic` ↔ `digital-liquid`)。保持统一名称一致。 | 与交换一起记录新的强调调色板。 |
| **内容密度模式** | 当设计需要承载大量文本时，保持英雄华彩，但使每个后续部分为 `bg-black` 并带有简单边框。 | 示例：顶部 `cppn-hero`，然后 `bento-grid` 在普通玻璃卡片中。 |
| **提示到模板默认值** | - “干净的 SaaS” → 网格渐变包<br> - “AI 平台” → CPPN 英雄 + 仪表盘指标<br> - “加密货币交易” → 地球英雄 + 行情<br> - “开发者 CLI” → 波浪英雄 + 终端 | 直接在响应中提及这些默认值，以便模型不会产生新的结构。 |

不确定时：**从基准开始，发布可用布局，然后作为后续建议提出一个单独的惊艳升级** (“如果我们想要更神经质的感觉，可以换成 CPPN 光栅。”)

---

## 模板 & 光栅选择指南

使用此指南根据用户的请求选择正确的模板和光栅。**不要对每个都使用相同的英雄** — 将美学与领域相匹配。

### 行业/垂直映射

| 行业 | 英雄模板 | 光栅 | 强调色 | 语气 |
|------|----------|------|--------|------|
| **AI/ML/神经** | `cppn-hero` | `cppn-generative` | 青色 `#00f3ff` / 紫色 `#a855f7` | 有机，活跃，数学 |
| **加密货币/DeFi/交易** | `globe-hero` | `data-grid` | 紫色 `#9b87f5` / 黄色 `#f59e0b` | 全球，技术，金融 |
| **开发者工具/API** | `wave-hero` | `digital-liquid` | 蓝色 `#1f3dbc` / 橙色 `#ff4d00` | 技术，动态，构建者 |
| **SaaS/B2B/产品** | `mesh-gradient-hero` | *(仅 CSS)* | 柔和的粉彩色 | 干净，专业，值得信赖 |
| **创意代理** | `hero-section` (CyberpunkHero) | `holographic` | 霓虹色 | 大胆，实验，艺术 |
| **金融科技/仪表盘** | `bento-grid` + `dashboard-widgets` | `data-grid` | 绿色 `#10b981` / 蓝色 `#3b82f6` | 数据丰富，精确，分析 |

### 关键词选择

在分析用户请求时，将关键词匹配到模板：

```
用户请求分析:
├── 包含 "AI", "神经", "智能", "学习", "模型", "GPT"
│   → cppn-hero + cppn-generative 光栅
│   → 有机，流动的背景感觉“活着”
│
├── 包含 "加密货币", "区块链", "交易", "全球", "DeFi", "web3"
│   → globe-hero + data-grid 光栅
│   → 地球图像，全球范围，金融精确
│
├── 包含 "开发者", "API", "代码", "构建", "部署", "发布"
│   → wave-hero + digital-liquid 光栅
│   → 动态条，打字动画，终端美学
│
├── 包含 "SaaS", "产品", "等待名单", "品牌", "初创公司", "发布"
│   → mesh-gradient-hero (无需 WebGL)
│   → 柔和，流动的渐变，专业感
│
├── 包含 "未来感", "赛博", "代理", "创意", "作品集"
│   → hero-section (CyberpunkHero) + holographic 光栅
│   → 粒子球，文本打乱，扫描线
│
└── 包含 "仪表盘", "分析", "指标", "数据", "监控"
    → bento-grid + dashboard-widgets + terminal
    → 统计卡片，火花线，实时数据源
```

### 性能选择

根据目标受众和设备限制进行选择：

| 性能等级 | 模板 | 适合 |
|--------|------|------|
| **高端 (WebGL)** | `cppn-hero`, `wave-hero`, `hero-section` | 桌面优先，作品集网站，创意代理 |
| **中端 (Canvas/图像)** | `globe-hero` | 营销网站，加密货币着陆页 |
| **轻量 (CSS 仅)** | `mesh-gradient-hero`, `bento-grid` | 移动优先，SaaS，B2B，关注无障碍 |

### 光栅配对指南

| 光栅 | 美学 | 与...配对良好 |
|------|------|-----------------|
| `cppn-generative` | 神经，有机，数学 | AI 产品，生成艺术，研究工具 |
| `data-grid` | 矩阵，技术，赛博朋克 | 加密货币，金融科技，开发者工具 |
| `digital-liquid` | 流动，动态，流体 | 创意工具，媒体平台 |
| `holographic` | 科幻，彩虹，未来感 | 游戏，AR/VR，实验项目 |

### 快速决策流程图

```
性能是否关键 (移动优先)?
├── 是 → mesh-gradient-hero (CSS 仅)
└── 否 → 继续...
    │
    是 AI/ML 相关吗?
    ├── 是 → cppn-hero
    └── 否 → 继续...
        │
        是加密货币/全球/金融吗?
        ├── 是 → globe-hero
        └── 否 → 继续...
            │
            是开发者聚焦吗?
            ├── 是 → wave-hero
            └── 否 → hero-section (CyberpunkHero)
```

---

## 文件结构

```
premium-frontend-skill/
├── SKILL.md                           # 本文档
├── examples/
│   ├── 01-racing-dashboard.tsx        # 赛车遥测
│   ├── 02-cyberpunk-platform.tsx      # 开发者平台
│   ├── 03-bioluminescent-landing.tsx  # AI 代理着陆页
│   ├── 04-fintech-protocol.tsx        # DeFi 界面
│   └── 05-neural-interface.tsx        # 有感知的 AI 核心
├── templates/
│   ├── preloader.tsx                  # 启动序列加载器
│   ├── glass-components.tsx           # 玻璃态 UI 元素
│   ├── terminal.tsx                   # 实时日志显示
│   ├── bento-grid.tsx                 # 仪表盘布局系统
│   ├── dashboard-widgets.tsx          # 统计卡片，图表，指标
│   ├── hero-section.tsx               # CyberpunkHero + StarfieldScene
│   ├── cppn-hero.tsx                  # 神经网络光栅英雄
│   ├── mesh-gradient-hero.tsx         # 流体渐变英雄 (CSS 轻量)
│   ├── wave-hero.tsx                  # 动画波浪条英雄
│   └── globe-hero.tsx                 # 3D 地球与仪表盘
└── shaders/
    ├── cppn-generative.glsl.ts        # 神经模式生成器
    ├── digital-liquid.glsl.ts         # 流动噪声效果
    ├── data-grid.glsl.ts              # 矩阵/网格效果
    └── holographic.glsl.ts            # 全息干扰
```

---

## 记住

> “目标是创建感觉 **活着**、**电影感** 和 **难忘** 的界面。每个像素都应该是故意的。这些不仅仅是网站——它们是体验。”

不要犹豫。当跳出盒子思考并完全致力于一个独特的愿景时，展示真正可以创造什么。
