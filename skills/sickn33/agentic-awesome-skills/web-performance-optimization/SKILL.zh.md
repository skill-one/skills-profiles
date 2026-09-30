---
name: web-performance-optimization
description: 优化网站和 Web 应用性能，包括加载速度、核心 Web 指标、包大小、缓存策略和运行时性能
---

# Web 性能优化

## 详细指南

在执行此技能前，请阅读[详细指南](references/detailed-guide.md)。该指南保留了完整流程和参考资料。请将其安全、前提条件和验证要求视为强制性。对于专注工作，加载相关章节；对于端到端工作，完整阅读指南。

## 何时使用此技能

- 网站或应用加载缓慢时
- 优化核心 Web 指标（LCP、FID、CLS）
- 减少JavaScript包体积
- 提升交互时间（TTI）
- 优化图片和资源
- 实施缓存策略
- 调试性能瓶颈
- 准备性能审计

## 示例

### 示例 1：优化核心 Web 指标

```markdown
## 性能审计结果

### 当前指标（优化前）
- **LCP（最大内容绘制）：** 4.2s ❌（应小于 2.5s）
- **FID（首次输入延迟）：** 180ms ❌（应小于 100ms）
- **CLS（累积布局偏移）：** 0.25 ❌（应小于 0.1）
- **Lighthouse 分数：** 62/100

### 发现的问题

1. **LCP 问题：** 主视觉图片（2.5MB）加载缓慢
2. **FID 问题：** 大型 JavaScript 包（850KB）阻塞主线程
3. **CLS 问题：** 无尺寸的图片导致布局偏移

### 优化方案

#### 修复 LCP（最大内容绘制）

**问题：** 主视觉图片为 2.5MB，加载缓慢

**解决方案：**
\`\`\`html
<!-- 优化前：未优化的图片 -->
<img src="/hero.jpg" alt="主视觉">

<!-- 优化后：使用现代格式 -->
<picture>
  <source srcset="/hero.avif" type="image/avif">
  <source srcset="/hero.webp" type="image/webp">
  <img 
    src="/hero.jpg" 
    alt="主视觉"
    width="1200" 
    height="600"
    loading="eager"
    fetchpriority="high"
  >
</picture>
\`\`\`

**额外优化：**
- 压缩图片至 < 200KB
- 使用 CDN 加速传输
- 预加载主视觉图片：`<link rel="preload" as="image" href="/hero.avif">`

#### 修复 FID（首次输入延迟）

**问题：** 850KB JavaScript 包阻塞主线程

**解决方案：**

1. **代码分割：**
\`\`\`javascript
// 优化前：所有代码在一个包中
import { HeavyComponent } from './HeavyComponent';
import { Analytics } from './analytics';
import { ChatWidget } from './chat';

// 优化后：按需加载非关键代码
const HeavyComponent = lazy(() => import('./HeavyComponent'));
const ChatWidget = lazy(() => import('./chat'));

// 页面交互后加载分析代码
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    import('./analytics').then(({ Analytics }) => {
      Analytics.init();
    });
  });
}
\`\`\`

2. **移除未使用的依赖：**
\`\`\`bash
# 分析包组成
npx webpack-bundle-analyzer

# 移除未使用的包
npm uninstall moment  # 使用 date-fns 代替（体积更小）
npm install date-fns
\`\`\`

3. **延迟加载非关键脚本：**
\`\`\`html
<!-- 优化前：阻塞渲染 -->
<script src="/analytics.js"></script>

<!-- 优化后：延迟加载 -->
<script src="/analytics.js" defer></script>
\`\`\`

#### 修复 CLS（累积布局偏移）

**问题：** 无尺寸的图片导致布局偏移

**解决方案：**
\`\`\`html
<!-- 优化前：无尺寸 -->
<img src="/product.jpg" alt="产品">

<!-- 优化后：带尺寸 -->
<img 
  src="/product.jpg" 
  alt="产品"
  width="400" 
  height="300"
  style="aspect-ratio: 4/3;"
>
\`\`\`

**对于动态内容：**
\`\`\`css
/* 为后续加载的内容预留空间 */
.skeleton-loader {
  min-height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
\`\`\`

### 优化后的结果

- **LCP：** 1.8s ✅（提升 57%）
- **FID：** 45ms ✅（提升 75%）
- **CLS：** 0.05 ✅（提升 80%）
- **Lighthouse 分数：** 94/100 ✅
```

### 示例 2：减少 JavaScript 包体积

```markdown
## 包体积优化

### 当前状态
- **总包体积：** 850KB（gzip 压缩后：280KB）
- **主包体积：** 650KB
- **供应商包体积：** 200KB
- **加载时间（3G）：** 8.2s

### 分析

\`\`\`bash
# 分析包组成
npx webpack-bundle-analyzer dist/stats.json
\`\`\`

**发现：**
1. Moment.js：67KB（可替换为 date-fns：12KB）
2. Lodash：72KB（使用整个库，仅需 5 个函数）
3. 未使用的代码：约 150KB 的死代码
4. 无代码分割：所有代码在一个包中

### 优化步骤

#### 1. 替换大型依赖

\`\`\`bash
# 移除 moment.js (67KB) → 使用 date-fns (12KB)
npm uninstall moment
npm install date-fns

# 优化前
import moment from 'moment';
const formatted = moment(date).format('YYYY-MM-DD');

# 优化后
import { format } from 'date-fns';
const formatted = format(date, 'yyyy-MM-dd');
\`\`\`

**节省：** 55KB

#### 2. 有选择地使用 Lodash

\`\`\`javascript
// 优化前：导入整个库（72KB）
import _ from 'lodash';
const unique = _.uniq(array);

// 优化后：仅导入所需（5KB）
import uniq from 'lodash/uniq';
const unique = uniq(array);

// 或使用原生方法
const unique = [...new Set(array)];
\`\`\`

**节省：** 67KB

#### 3. 实施代码分割

\`\`\`javascript
// Next.js 示例
import dynamic from 'next/dynamic';

// 按需加载大型组件
const Chart = dynamic(() => import('./Chart'), {
  loading: () => <div>加载图表...</div>,
  ssr: false
});

const AdminPanel = dynamic(() => import('./AdminPanel'), {
  loading: () => <div>加载中...</div>
});

// 路由级代码分割（Next.js 自动实现）
// pages/admin.js - 仅访问 /admin 时加载
// pages/dashboard.js - 仅访问 /dashboard 时加载
\`\`\`

#### 4. 移除死代码

\`\`\`javascript
// 在 webpack.config.js 中启用 Tree Shaking
module.exports = {
  mode: 'production',
  optimization: {
    usedExports: true,
    sideEffects: false
  }
};

// 在 package.json 中
{
  "sideEffects": false
}
\`\`\`

#### 5. 优化第三方脚本

\`\`\`html
<!-- 优化前：立即加载 -->
<script src="https://analytics.com/script.js"></script>

<!-- 优化后：页面交互后加载 -->
<script>
  window.addEventListener('load', () => {
    const script = document.createElement('script');
    script.src = 'https://analytics.com/script.js';
    script.async = true;
    document.body.appendChild(script);
  });
</script>
\`\`\`

### 结果

- **总包体积：** 380KB ✅（减少 55%）
- **主包体积：** 180KB ✅
- **供应商包体积：** 80KB ✅
- **加载时间（3G）：** 3.1s ✅（提升 62%）
```

### 示例 3：图片优化策略

```markdown
## 图片优化

### 当前问题
- 15 张图片总计 12MB
- 无现代格式（WebP、AVIF）
- 无响应式图片
- 无懒加载

### 优化策略

#### 1. 转换为现代格式

\`\`\`bash
# 安装图片优化工具
npm install sharp

# 转换脚本（optimize-images.js）
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function optimizeImage(inputPath, outputDir) {
  const filename = path.basename(inputPath, path.extname(inputPath));
  
  // 生成 WebP
  await sharp(inputPath)
    .webp({ quality: 80 })
    .toFile(path.join(outputDir, \`\${filename}.webp\`));
  
  // 生成 AVIF（最佳压缩）
  await sharp(inputPath)
    .avif({ quality: 70 })
    .toFile(path.join(outputDir, \`\${filename}.avif\`));
  
  // 生成优化后的 JPEG 备用
  await sharp(inputPath)
    .jpeg({ quality: 80, progressive: true })
    .toFile(path.join(outputDir, \`\${filename}.jpg\`));
}

// 处理所有图片
const images = fs.readdirSync('./images');
images.forEach(img => {
  optimizeImage(\`./images/\${img}\`, './images/optimized');
});
\`\`\`

#### 2. 实现响应式图片

\`\`\`html
<!-- 响应式图片（带现代格式） -->
<picture>
  <!-- AVIF：支持浏览器（最佳压缩） -->
  <source 
    srcset="
      /images/hero-400.avif 400w,
      /images/hero-800.avif 800w,
      /images/hero-1200.avif 1200w
    "
    type="image/avif"
    sizes="(max-width: 768px) 100vw, 50vw"
  >
  
  <!-- WebP：支持浏览器 -->
  <source 
    srcset="
      /images/hero-400.webp 400w,
      /images/hero-800.webp 800w,
      /images/hero-1200.webp 1200w
    "
    type="image/webp"
    sizes="(max-width: 768px) 100vw, 50vw"
  >
  
  <!-- JPEG 备用 -->
  <img 
    src="/images/hero-800.jpg"
    srcset="
      /images/hero-400.jpg 400w,
      /images/hero-800.jpg 800w,
      /images/hero-1200.jpg 1200w
    "
    sizes="(max-width: 768px) 100vw, 50vw"
    alt="主视觉图片"
    width="1200"
    height="600"
    loading="lazy"
  >
</picture>
\`\`\`

#### 3. 懒加载

\`\`\`html
<!-- 原生懒加载 -->
<img 
  src="/image.jpg" 
  alt="描述"
  loading="lazy"
  width="800"
  height="600"
>

<!-- 立即加载首屏图片 -->
<img 
  src="/hero.jpg" 
  alt="首屏"
  loading="eager"
  fetchpriority="high"
>
\`\`\`

#### 4. Next.js 图片组件

\`\`\`javascript
import Image from 'next/image';

// 自动优化
<Image
  src="/hero.jpg"
  alt="主视觉"
  width={1200}
  height={600}
  priority  // 首屏图片
  quality={80}
/>

// 懒加载
<Image
  src="/product.jpg"
  alt="产品"
  width={400}
  height={300}
  loading="lazy"
/>
\`\`\`

### 结果

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 图片总大小 | 12MB | 1.8MB | 减少 85% |
| LCP | 4.5s | 1.6s | 加速 64% |
| 页面加载（3G） | 18s | 4.2s | 加速 77% |
```

## 限制

- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
