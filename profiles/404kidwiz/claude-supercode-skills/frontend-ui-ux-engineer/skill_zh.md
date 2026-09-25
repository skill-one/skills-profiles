# 前端 UI/UX 工程师

## 目的

提供前端设计和开发专业知识，专注于创建视觉震撼、以用户为中心的界面，无需设计原型。运用创意设计思维、高级样式、动画和可访问性最佳实践，为现代 Web 应用程序打造精美的 UI/UX。

## 使用场景

- 需要将功能型 UI 转换为视觉震撼的界面
- 不存在设计原型，但需要精美的 UI
- 视觉润色和微交互是优先事项
- 组件样式需要创意设计思维
- 需要用户体验改进，但没有专职设计师

## 快速入门

**在以下情况下调用此技能：**
- 需要将功能型 UI 转换为视觉震撼的界面
- 不存在设计原型，但需要精美的 UI
- 视觉润色和微交互优先于代码优雅性
- 组件样式需要创意设计思维
- 需要用户体验改进，但没有专职设计师

**不调用场景：**
- 需要后端逻辑或 API 开发
- 没有视觉变化的纯代码重构
- 性能优化是唯一优先事项
- 需要安全导向的开发
- 数据库或基础设施工作

---
---

## 核心工作流

### 工作流 1：将功能组件转换为惊艳 UI

**用例：** 给定一个普通的 React 组件，使其在视觉上卓越

**输入示例：**
```tsx
// 之前：功能但普通
function ProductCard({ product }: { product: Product }) {
  return (
    <div>
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button>Add to Cart</button>
    </div>
  );
}
```

**步骤：**

**1. 视觉分析（2 分钟）**
```
需要回答的问题：
- 这个界面应该唤起什么情绪？（高端？有趣？值得信赖？）
- 视觉层级是什么？（图片 > 名称 > 价格 > CTA）
- 哪些交互能让用户愉悦？（悬停效果，平滑过渡）
- 哪里需要空白区域？（元素周围的呼吸空间）
```

**2. 颜色与字体增强**
```tsx
// 之后：视觉基础已建立
import { motion } from 'framer-motion';

function ProductCard({ product }: { product: Product }) {
  return (
    <motion.div
      className="group relative overflow-hidden rounded-2xl bg-white shadow-lg transition-shadow hover:shadow-2xl"
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
    >
      {/* 图片容器带宽高比 */}
      <div className="relative aspect-square overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        {/* 渐变叠加层用于可读性 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
      </div>

      {/* 内容带适当间距 */}
      <div className="p-6 space-y-3">
        <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
          {product.name}
        </h3>
        
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-blue-600">
            ${product.price}
          </span>
          {product.compareAtPrice && (
            <span className="text-sm text-gray-500 line-through">
              ${product.compareAtPrice}
            </span>
          )}
        </div>

        {/* 增强型 CTA 按钮 */}
        <button className="w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 active:bg-blue-800 disabled:bg-gray-300 disabled:cursor-not-allowed">
          Add to Cart
        </button>
      </div>
    </motion.div>
  );
}
```

**3. 微交互与润色**
```tsx
// 最终：添加了令人愉悦的交互
function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const [isAdded, setIsAdded] = useState(false);

  const handleAddToCart = () => {
    onAddToCart(product);
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 2000);
  };

  return (
    <motion.div
      layout
      className="group relative overflow-hidden rounded-2xl bg-white shadow-lg transition-shadow hover:shadow-2xl"
      whileHover={{ y: -4 }}
    >
      <div className="relative aspect-square overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        
        {/* 销售徽章带动画 */}
        {product.onSale && (
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            className="absolute top-4 right-4 rounded-full bg-red-500 px-3 py-1 text-sm font-bold text-white shadow-lg"
          >
            SALE
          </motion.div>
        )}
      </div>

      <div className="p-6 space-y-3">
        <h3 className="text-xl font-semibold text-gray-900 line-clamp-2 transition-colors group-hover:text-blue-600">
          {product.name}
        </h3>
        
        <div className="flex items-baseline gap-2">
          <motion.span
            className="text-2xl font-bold text-blue-600"
            key={product.price} // 价格变化时重新动画
            initial={{ scale: 1.2, color: '#ef4444' }}
            animate={{ scale: 1, color: '#2563eb' }}
          >
            ${product.price}
          </motion.span>
          {product.compareAtPrice && (
            <span className="text-sm text-gray-500 line-through">
              ${product.compareAtPrice}
            </span>
          )}
        </div>

        {/* 带成功状态的按钮 */}
        <button
          onClick={handleAddToCart}
          className={`
            w-full rounded-lg px-6 py-3 font-medium text-white transition-all
            ${isAdded 
              ? 'bg-green-500 scale-105' 
              : 'bg-blue-600 hover:bg-blue-700 active:scale-95'
            }
          `}
        >
          {isAdded ? (
            <span className="flex items-center justify-center gap-2">
              <CheckIcon className="h-5 w-5" />
              Added!
            </span>
          ) : (
            'Add to Cart'
          )}
        </button>
      </div>
    </motion.div>
  );
}
```

**预期结果：**
- 视觉吸引力提升 5 倍
- 参与度指标提升 20-40%（典型值）
- 通过微交互提升用户愉悦感
- 保持可访问性（ARIA 标签，键盘导航）

---
---

## 模板与模式

### 模式 1：玻璃态卡片

**使用场景：** 现代、高端美学（与彩色背景配合效果更佳）

```tsx
function GlassCard({ children, className = '' }: GlassCardProps) {
  return (
    <div className={`
      relative overflow-hidden rounded-2xl
      backdrop-blur-xl backdrop-saturate-150
      bg-white/10 border border-white/20
      shadow-xl shadow-black/5
      ${className}
    `}>
      {/* 可选的渐变叠加层 */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent opacity-50" />
      
      <div className="relative z-10 p-6">
        {children}
      </div>
    </div>
  );
}
```

---
---

### 模式 3：带闪烁效果的骨架加载

**使用场景：** 卡片、列表的加载状态（比旋转加载器体验更好）

```tsx
function SkeletonCard() {
  return (
    <div className="relative overflow-hidden rounded-xl bg-gray-200 p-6">
      {/* 闪烁效果 */}
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/50 to-transparent" />
      
      {/* 骨架内容 */}
      <div className="space-y-4">
        <div className="h-4 w-3/4 rounded bg-gray-300" />
        <div className="h-4 w-1/2 rounded bg-gray-300" />
        <div className="h-32 w-full rounded bg-gray-300" />
      </div>
    </div>
  );
}

// Tailwind 配置（添加到 tailwind.config.js）
{
  theme: {
    extend: {
      animation: {
        shimmer: 'shimmer 2s infinite',
      },
      keyframes: {
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
}
```

---
---

### ❌ 反模式 2：忽略颜色对比

**看起来像：**
```css
/* ❌ 浅灰色文本在浅灰色背景上 = 难以阅读 */
.subtle-text {
  color: #999999;
  background: #f0f0f0;
  /* 对比度比例：2.1:1（未通过 WCAG AA 4.5:1 要求） */
}
```

**为什么失败：**
- 未通过 WCAG AA 可访问性（文本对比度需 4.5:1）
- 视觉障碍用户无法阅读内容
- 在强光下体验差（移动设备）

**正确方法：**
```css
/* ✅ 足够的对比度 */
.readable-text {
  color: #333333;
  background: #ffffff;
  /* 对比度比例：12.6:1（通过 WCAG AAA） */
}

/* 或使用设计系统变量 */
.text {
  color: var(--color-text-primary);    /* 保证 4.5:1 */
  background: var(--color-bg-surface); /* 与文本颜色对比 */
}
```

---
---

## 质量检查清单

### 视觉润色
- [ ] 色彩调板最多使用 3 种主色 + 中性色
- [ ] 字体层级清晰（3-5 种字体大小）
- [ ] 间距遵循一致的比例（4px, 8px, 16px, 24px, 32px...）
- [ ] 所有交互元素都有悬停状态
- [ ] 异步操作的加载状态
- [ ] 空状态带有帮助性信息

### 可访问性
- [ ] 文本对比度 ≥4.5:1（WCAG AA）
- [ ] 所有交互元素都有可见的焦点指示器
- [ ] 动画尊重 `prefers-reduced-motion`
- [ ] 所有图片都有替代文本
- [ ] 键盘导航正常工作（Tab, Enter, Esc）

### 响应式设计
- [ ] 移动优先方法（320px 基础）
- [ ] 断点：sm (640px), md (768px), lg (1024px), xl (1280px)
- [ ] 触摸目标 ≥44x44px（移动设备）
- [ ] 移动设备上无水平滚动
- [ ] 图片响应式（`max-width: 100%`, `height: auto`）

### 性能
- [ ] 动画使用 `transform` 和 `opacity`（GPU 加速）
- [ ] 图片优化（WebP, 懒加载）
- [ ] CSS 打包 <50KB（压缩后）
- [ ] 无布局偏移（CLS <0.1）
- [ ] 字体预加载（`<link rel="preload">`）
