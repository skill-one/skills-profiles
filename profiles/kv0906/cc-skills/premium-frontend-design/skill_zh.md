# 高级前端设计技能

这项技能指导创建**生产级的前端界面，充满活力**——不是通用的，不是复制粘贴，而是真正精心制作，让用户难忘的体验。

> “优秀界面和令人难忘界面之间的区别在于每个像素的意图性。”

---

## 依赖关系（灵活选择）

这项技能**框架灵活**。根据用户偏好和项目需求选择包。

### 核心 3D（适用于 WebGL 模板）
```bash
pnpm add three @react-three/fiber @react-three/drei
```

### 动画（根据用户偏好选择）

| 库 | 适用于 | 复杂度 | 打包大小 |
|---|--------|--------|----------|
| **CSS/Tailwind** | 简单过渡，微交互 | 低 | 0KB |
| **Framer Motion** | React-native 感觉，布局动画，手势 | 中 | ~30KB |
| **GSAP** | 复杂时间线，滚动触发，文本效果 | 高 | ~60KB |
| **GSAP + Club** | SplitText，ScrollTrigger，MorphSVG | 高 | ~80KB |

```bash
# Framer Motion (更简单，React 风格)
pnpm add framer-motion

# GSAP (强大，基于时间线)
pnpm add gsap @gsap/react
# 注意：SplitText, ScrollTrigger 需要 GSAP Club 许可证
```

**决策指南：**
- 用户说“简单”或“轻量级” → CSS + Framer Motion
- 用户说“复杂动画”或“滚动效果” → GSAP
- 用户说“文本动画”或“分割文本” → GSAP + SplitText
- 用户没有指定 → 默认使用 Framer Motion（更简单的 API）

### 可选增强功能
```bash
# 网格渐变（用于 mesh-gradient-hero）
pnpm add @paper-design/shaders-react

# 图标
pnpm add lucide-react

# 图表/火花线（用于仪表板）
pnpm add recharts
# 或轻量级: pnpm add @visx/shape @visx/scale
```

### 浏览器兼容性说明
- `backdrop-filter`: 不支持 Firefox < 103（添加后备背景）
- WebGL: 为旧设备提供 CSS 备用方案
- `@starting-style`: Chrome 117+，Safari 17.4+（渐进增强）

---

## 核心理念

### “活力”原则

当界面充满活力时：
- **它呼吸**: 轻微的环境动画、粒子或着色器效果创造持续但不会分散注意力的运动
- **它响应**: 微交互承认每个用户操作并提供令人满意的反馈
- **它有深度**: 图层、视差、玻璃效果和阴影创造维度空间
- **它惊喜**: 至少有一个元素以令人愉快的方式打破预期

### 设计思维（在编写任何代码之前）

在编写单行代码之前，回答这些问题：

1. **目的**: 这个问题解决了什么？谁使用它？
2. **语气**: 选择一个极端方向（不是混合）:
   - 极简主义
   - 极端混乱
   - 复古未来主义 / 赛博朋克
   - 有机 / 自然
   - 奢华 / 精致
   - 活泼 / 玩具风格
   - 编辑 / 杂志
   - 布鲁特alist / 原始
   - 装饰艺术 / 几何
   - 工业化 / 实用主义
   - 生物发光 / 科幻
   - 任务控制 / 技术性

**关键**: 粗体极简主义和精致极简主义都有效。关键在于**意图性，不是强度**。一个完美执行的动画胜过 50 个平庸的动画。

---

## 奇观 + 清晰框架

当简报模糊不清或需要证明设计决策时，请使用此框架。目标是**充满奇观的目的**。

### 1. 层级限制

- **1 个英雄装饰**（着色器、粒子系统或球体）。其他内容支持可读性。
- **1 个辅助装饰**（微交互、动画状态卡或发光 CTA）。不能再多了。
布局规则：`英雄 (狂野) → 内容块 (平静) → 证据 (平静) → CTA (突出显示)`。
- 如果页面有超过一个滚动长度的文本，每第二个部分应该是静态的。

### 2. 字体规范

- **最多 2 个标题字体**（显示 + 正文）。数据使用等宽字体。
- 标题字间距 ≥ -0.04em。任何更紧的会杀死可读性。
- 正文宽度目标：桌面 55-75 个字符每行，手机 35-45 个字符每行。
- 始终在大的显示文本下方配对一个简短的辅助句子，不超过 80 个字符。

### 3. 颜色和对比度规则

- 限制霓虹灯的使用到**主要 CTA + 1 个强调色**。其他所有内容都保持锌/中性调色板。
- 如果背景繁忙（着色器、渐变、粒子），在文本后面添加 `bg-black/70` 或 `bg-slate-950/70` 纹理。
- 保持正文对比度 ≥ 4.5:1，即使美学是赛博朋克。
- 在发货前添加灰度预览检查：如果看起来模糊，请减少调色板。

### 4. 动画限制

- **默认**: CSS 或 Framer Motion，持续时间 ≤ 400ms，缓动 `cubic-bezier(0.34, 1.56, 0.64, 1)`。
- **升级到 GSAP/WebGL** 仅当简报明确要求电影或交互式体验时。
- 每个视口最多 **1 个连续动画**（例如，着色器或波浪条，不能两者都有）。
- 提供“平静模式”：当 `prefers-reduced-motion` 开启或用户滚动到英雄之外时禁用非必要动画。

### 5. 当要求模糊时

| 情况 | 默认 | 可选升级 |
|-----|------|-----------|
| 用户只说“干净的 SaaS” | `mesh-gradient-hero` + `bento-grid` | 如果用户后来要求“更多能量”，将英雄背景替换为 CPPN
| 用户说“仪表板”但没有花哨 | `bento-grid` + `dashboard-widgets` + CSS 发光药丸 | 仅在数据可视化确认后添加 `digital-liquid` 着色器
| 用户说“英雄部分”但没有其他 | 文本优先布局 + CSS 渐变 | 提供着色器/球体建议，但默认不是默认的 |

如果提示中没有明确提到 WebGL，则假设**CSS 首先处理**，仅在用户接受成本时才选择着色器。

---

## 反模式（绝对不要这样做）

### 视觉反模式
❌ 白色/浅色背景作为默认值（暗模式是高级的）
❌ 通用渐变（白色到蓝色在白色上是 AI 拖累）
❌ 均匀分布、胆怯的调色板
❌ 静态、无生气的背景
❌ 千篇一律的组件布局
❌ 缺少加载/过渡状态
❌ 令人震惊的、未缓动的动画

### 字体反模式
❌ Inter, Roboto, Arial, 系统字体用于标题
❌ 同一个字体用于所有内容
❌ 默认行高和字间距
❌ 乏味、可预测的字体比例

### 代码反模式
❌ 随机分散的行内样式
❌ 没有用于主题的 CSS 变量
❌ 没有带 `will-change` 或 GPU 加速的动画
❌ 没有使用 `requestAnimationFrame` 的 Canvas/WebGL
❌ 缺少 `useEffect` 中的清理

---

## 设计系统

### 1. 颜色架构

**规则：一个主导强调色，其他都支持它。**

```typescript
// 高级暗主题（默认）
const colors = {
  // 背景（从最暗到最亮）
  bg: {
    void: '#000000',      // 真黑，最大对比度
    primary: '#050505',   // 主要背景
    elevated: '#0a0a0a',  // 卡片，模态
    subtle: '#111111',    // 悬停状态
  },
  
  // 玻璃表面
  glass: {
    bg: 'rgba(255, 255, 255, 0.03)',
    border: 'rgba(255, 255, 255, 0.08)',
    hover: 'rgba(255, 255, 255, 0.06)',
  },
  
  // 文本层次结构
  text: {
    primary: '#ffffff',
    secondary: '#a1a1aa',   // zinc-400
    muted: '#71717a',       // zinc-500
    ghost: '#3f3f46',       // zinc-700
  },
  
  // 强调色（每个项目选择一个）
  accent: '#ff4d00',  // 霓虹橙色
  // accent: '#00f3ff',  // 霓虹青色
  // accent: '#ccff00',  // 霓虹青柠
  // accent: '#F5E445',  // 高级黄色
  // accent: '#a855f7',  // 电气紫色
}

**强调色使用规则**:
- 主要操作：全强调色
- 次要元素：强调色 20% 透明度
- 边框/线条：强调色 30% 透明度
- 发光：强调色，模糊，40-60% 透明度
- 永远不要用强调色作为大面积背景区域

### 2. 字体系统

**规则：标题字体用于冲击力，正文字体用于阅读，等宽字体用于数据。**

```css
/* 级别 1：标题/大标题 - 粗体，有特色 */
--font-display: 'Chakra Petch', 'Orbitron', 'Bebas Neue', 'Playfair Display';

/* 级别 2：标题 - 几何的，现代 */
--font-heading: 'Manrope', 'Outfit', 'Syne', 'Space Grotesk';

/* 级别 3：正文 - 干净，高度可读 */
--font-body: 'Plus Jakarta Sans', 'DM Sans', 'Satoshi', 'General Sans';

/* 级别 4：数据/代码 - 始终使用等宽字体 */
--font-mono: 'JetBrains Mono', 'Fira Code', 'IBM Plex Mono';
```

**字体模式**:

```css
/* 英雄标题：巨大，紧密，激进 */
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

### 3. 间距和布局

**规则：不对称创造兴趣。网格只是起点，不是牢笼。**

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

/* 容器间距要大 */
.container {
  padding-inline: clamp(1rem, 5vw, 4rem);
}

/* 英雄部分需要呼吸空间 */
.hero {
  min-height: 100vh;
  padding-block: var(--space-32);
}
```

**Bento 网格模式（用于仪表板）**:
```css
.bento {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(150px, auto);
  gap: var(--space-4);
}

/* 特征卡片跨越 */
.card-hero { grid-column: span 2; grid-row: span 2; }
.card-wide { grid-column: span 2; }
.card-tall { grid-row: span 2; }
```

---

## 视觉效果库

### 1. 玻璃效果（正确的方式）

```css
.glass {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

/* 提升玻璃（用于模态，下拉菜单） */
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
    linear-gradient(rgba(255, 255, 255, 0.02) 1px,
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px,
    transparent 1px
  );
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
- **入场动画**: 只用一次，要值得
- **微交互**: 轻微，快速（150-300ms）
- **环境运动**: 无限，非常慢，不分散注意力
- **页面过渡**: 平滑，协调

### 选择合适的工具

| 需求 | 使用 | 原因 |
|-----|------|------|
| 悬停/焦点状态 | CSS | 零 JS，即时 |
| 简单入场 | CSS keyframes | 轻量级 |
| 布局动画 | Framer Motion | `layout` 属性魔法 |
| 基于手势 | Framer Motion | 内置拖动/平移 |
| 滚动触发 | GSAP ScrollTrigger | 最强大的 |
| 文本分割 | GSAP SplitText | 行业标准 |
| 复杂时间线 | GSAP | 精确控制 |
| SVG 变形 | GSAP MorphSVG | 没有替代方案 |

**默认使用更简单的解决方案。只有在需要时才升级到 GSAP/WebGL**。

### CSS 关键帧库

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

### 错落有致入场模式

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
/* 视图过渡入场 (Chrome 111+, Safari 18+) */
@supports (view-transition-name: none) {
  .card {
    view-transition-name: card;
  }
  
  ::view-transition-old(card),
  ::view-transition-new(card) {
    animation-duration: 0.3s;
  }
}

/* 滚动驱动动画 (Chrome 115+) */
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

/* 悬停弹簧效果 */
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
// 滚动触发时错落有致入场
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

// 文本打乱效果
const scrambleText = (el: HTMLElement, text: string) => {
  const chars = '!<>-_\\/[]{}—=+*^?#';
  let iteration = 0;
  
  const interval = setInterval(() => {
    el.innerText = text
      .split('')
      .map((char, i) => 
        i < iteration ? char : chars[Math.floor(Math.random() * chars.length)]
      .join('');
  });
    
  if (iteration >= text.length) clearInterval(interval);
  iteration += 1/3;
};

// 平滑视差
gsap.to('.parallax-bg', {
  scrollTrigger: {
    scrub: 1,
  },
  y: '-30%',
  ease: 'none',
});
```

### Framer Motion 模式

```tsx
// 页面过渡
<AnimatePresence mode="wait">
  <motion.div
    key={page}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3 }}
  />
</AnimatePresence>

// 悬停发光效果
<motion.div
  whileHover={{ 
    scale: 1.02,
    boxShadow: '0 0 30px rgba(255, 77, 0, 0.4)',
  }}
  transition={{ type: 'spring', stiffness: 300 }}
/>

// 错落有致子元素
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

## 3D & WebGL 模式

### 技术堆栈
```bash
npm install three @react-three/fiber @react-three/drei
```

### 基本场景设置

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
    {/* 你的 3D 内容 */}
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
  </Canvas>
);
```

### 粒子球体（数据球）
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
  }, [count];
  
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

### 有感知的核心（AI 大脑）
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

### 性能规则
1. 始终使用 `requestAnimationFrame` 通过 `useFrame`
2. 减少移动设备上的粒子数量（检查 `window.innerWidth`
3. 使用 `useMemo` 进行几何/位置计算
4. 在 `useEffect` 返回时清理动画
5. 设置 `transparent` 和 `opacity` 以进行深度排序

---

## 组件模式

### 1. 加载 + 页面过渡

**默认（除非用户要求否则不要这样做）**:
- 卡片/部分使用骨架占位符（见上面的闪烁模式）
- 简单的淡入淡出页面过渡使用 CSS 或 Framer Motion 路由过渡
- CSS 或 Framer Motion 路由过渡
- 简单的加载动画使用 CSS 或 Framer Motion
- CSS 渐变背景
- 文本优先布局 + CSS 渐变
- 提供着色器/球体建议，但默认不是默认的

**可选的奇观模式（仅当用户想要叙事启动序列且有时间/预算时）**:
- GSAP 预加载器，带有启动日志，文本打乱，着色器/ WebGL 背景
- 协调时间线，在数据准备好后淡入实际内容
- 使用 CSS 渐变背景
- 文本优先布局 + CSS 渐变
- 提供着色器/球体建议，但默认不是默认的

如果提示中没有明确提到 WebGL，则假设**CSS 首先处理**，只有在用户接受成本时才选择着色器。

---

## 文件结构

```
premium-frontend-skill/
├── SKILL.md                           # 这份文档
├── examples/
│   ├── 01-racing-dashboard.tsx        # 车辆遥测
│   ├── 02-cyberpunk-platform.tsx      # 开发者平台
│   ├── 03-bioluminescent-landing.tsx  # AI 机构着陆页
│   ├── 04-fintech-protocol.tsx        # DeFi 界面
│   └── 05-neural-interface.tsx        # 有感知的 AI 核心
├── templates/
│   ├── preloader.tsx                  # 启动序列加载器
│   ├── glass-components.tsx           # 玻璃效果 UI 元素
│   ├── terminal.tsx                   # 实时日志显示
│   ├── bento-grid.tsx                 # 仪表板布局系统
│   ├── dashboard-widgets.tsx          # 统计卡片，图表，指标
│   ├── hero-section.tsx               # CyberpunkHero + StarfieldScene
│   ├── cppn-hero.tsx                  # 神经网络着色器英雄
│   ├── mesh-gradient-hero.tsx         # 流体渐变英雄 (CSS 轻量级)
│   ├── wave-hero.tsx                  # 动画波浪条英雄
│   └── globe-hero.tsx                 # 3D 球体与仪表板
└── shaders/
    ├── cppn-generative.glsl.ts        # 神经图案生成器
    ├── digital-liquid.glsl.ts         # 流动噪声效果
    ├── data-grid.glsl.ts              # 矩阵/网格效果
    └── holographic.glsl.ts            # 水晶干涉
```

---

## 记住

> “目标是创建充满活力、电影感、令人难忘的界面。每个像素都应该是故意的。”

不要犹豫。当思考超出盒子并完全致力于独特的愿景时，展示真正可以创造什么。
