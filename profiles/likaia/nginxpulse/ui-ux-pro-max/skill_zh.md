# UI/UX Pro Max - 设计智能

一个可搜索的 UI 风格、调色板、字体搭配、图表类型、产品推荐、UX 指南和特定技术栈最佳实践的数据库。

## 前置条件

检查是否已安装 Python：

```bash
python3 --version || python --version
```

如果未安装 Python，根据用户的操作系统进行安装：

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install python3
```

**Windows:**
```powershell
winget install Python.Python.3.12
```

---

## 如何使用此技能

当用户请求 UI/UX 工作（设计、构建、创建、实施、审查、修复、改进）时，请遵循以下工作流程：

### 第 1 步：分析用户需求

从用户请求中提取关键信息：
- **产品类型**：SaaS、电子商务、作品集、仪表板、着陆页等。
- **风格关键词**：极简、有趣、专业、优雅、暗黑模式等。
- **行业**：医疗保健、金融科技、游戏、教育等。
- **技术栈**：React、Vue、Next.js 或默认为 `html-tailwind`

### 第 2 步：搜索相关领域

多次使用 `search.py` 收集全面信息，直到获得足够的上下文。

```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**推荐搜索顺序：**

1. **产品** - 获取产品类型的风格推荐
2. **风格** - 获取详细的风格指南（颜色、效果、框架）
3. **排版** - 获取带有 Google Fonts 引入的字体搭配
4. **颜色** - 获取调色板（主色、辅色、CTA、背景、文本、边框）
5. **着陆页** - 获取页面结构（如果是着陆页）
6. **图表** - 获取图表推荐（如果是仪表板/分析）
7. **UX** - 获取最佳实践和反模式
8. **技术栈** - 获取特定技术栈的指南（默认：html-tailwind）

### 第 3 步：技术栈指南（默认：html-tailwind）

如果用户未指定技术栈，**默认为 `html-tailwind`**。

```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```

可用技术栈：`html-tailwind`、`react`、`nextjs`、`vue`、`svelte`、`swiftui`、`react-native`、`flutter`

---

## 搜索参考

### 可用领域

| 领域 | 用途 | 示例关键词 |
|------|------|------------|
| `product` | 产品类型推荐 | SaaS、电子商务、作品集、医疗保健、美容、服务 |
| `style` | UI 风格、颜色、效果 | glassmorphism、极简主义、暗黑模式、 brutalism |
| `typography` | 字体搭配、Google Fonts | 优雅、有趣、专业、现代 |
| `color` | 按产品类型划分的调色板 | saas、ecommerce、healthcare、beauty、fintech、service |
| `landing` | 页面结构、CTA 策略 | hero、hero-centric、testimonial、pricing、social-proof |
| `chart` | 图表类型、库推荐 | trend、comparison、timeline、funnel、pie |
| `ux` | 最佳实践、反模式 | animation、accessibility、z-index、loading |
| `prompt` | AI 提示、CSS 关键词 | (风格名称) |

### 可用技术栈

| 技术栈 | 重点 |
|------|------|
| `html-tailwind` | Tailwind 工具、响应式、a11y (默认) |
| `react` | 状态、hooks、性能、模式 |
| `nextjs` | SSR、路由、图片、API 路由 |
| `vue` | Composition API、Pinia、Vue Router |
| `svelte` | Runes、stores、SvelteKit |
| `swiftui` | Views、状态、导航、动画 |
| `react-native` | 组件、导航、列表 |
| `flutter` | Widgets、状态、布局、主题 |

---

## 示例工作流程

**用户请求：** "为专业护肤服务制作着陆页"

**AI 应该：**

```bash
# 1. 搜索产品类型
python3 .shared/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --domain product

# 2. 搜索风格（基于行业：美容、优雅）
python3 .shared/ui-ux-pro-max/scripts/search.py "elegant minimal soft" --domain style

# 3. 搜索排版
python3 .shared/ui-ux-pro-max/scripts/search.py "elegant luxury" --domain typography

# 4. 搜索调色板
python3 .shared/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --domain color

# 5. 搜索着陆页结构
python3 .shared/ui-ux-pro-max/scripts/search.py "hero-centric social-proof" --domain landing

# 6. 搜索 UX 指南
python3 .shared/ui-ux-pro-max/scripts/search.py "animation" --domain ux
python3 .shared/ui-ux-pro-max/scripts/search.py "accessibility" --domain ux

# 7. 搜索技术栈指南（默认：html-tailwind）
python3 .shared/ui-ux-pro-max/scripts/search.py "layout responsive" --stack html-tailwind
```

**然后：** 综合所有搜索结果并实施设计。

---

## 获取更好结果的技巧

1. **使用具体的关键词** - "医疗保健 SaaS 仪表板" > "app"
2. **多次搜索** - 不同的关键词会揭示不同的见解
3. **组合领域** - 风格 + 排版 + 颜色 = 完整的设计系统
4. **始终检查 UX** - 搜索 "animation"、"z-index"、"accessibility" 以解决常见问题
5. **使用技术栈标志** - 获取特定实现的最佳实践
6. **迭代** - 如果第一次搜索不匹配，尝试不同的关键词
7. **拆分为多个文件** - 为更好的可维护性：
   - 将组件拆分为单个文件（例如，`Header.tsx`、`Footer.tsx`）
   - 将可重用样式提取到专用文件
   - 保持每个文件专注且不超过 200-300 行

---

## 专业 UI 的常见规则

这些是经常被忽视的问题，使 UI 看起来不专业：

### 图标和视觉元素

| 规则 | 做 | 不要 |
|------|----|-----|
| **不要使用表情符号图标** | 使用 SVG 图标（Heroicons、Lucide、Simple Icons） | 使用 🎨 🚀 ⚙️ 等表情符号作为 UI 图标 |
| **稳定的悬停状态** | 在悬停时使用颜色/不透明度过渡 | 使用缩放变换导致布局偏移 |
| **正确的品牌标志** | 从 Simple Icons 研究官方 SVG | 猜测或使用错误的标志路径 |
| **一致的图标尺寸** | 使用固定的 viewBox (24x24) 并配合 w-6 h-6 | 随机混合不同的图标尺寸 |

### 交互和光标

| 规则 | 做 | 不要 |
|------|----|-----|
| **光标指针** | 为所有可点击/可悬停的卡片添加 `cursor-pointer` | 留下默认光标在交互元素上 |
| **悬停反馈** | 提供视觉反馈（颜色、阴影、边框） | 没有指示元素可交互 |
| **平滑过渡** | 使用 `transition-colors duration-200` | 状态变化瞬间或过慢 (>500ms) |

### 亮/暗模式对比度

| 规则 | 做 | 不要 |
|------|----|-----|
| **亮模式玻璃卡片** | 使用 `bg-white/80` 或更高不透明度 | 使用 `bg-white/10`（太透明） |
| **亮模式文本对比度** | 使用 `#0F172A`（slate-900）作为文本 | 使用 `#94A3B8`（slate-400）作为正文 |
| **亮模式弱文本** | 使用 `#475569`（slate-600）作为最小值 | 使用 gray-400 或更浅 |
| **边框可见性** | 在亮模式下使用 `border-gray-200` | 使用 `border-white/10`（不可见） |

### 布局和间距

| 规则 | 做 | 不要 |
|------|----|-----|
| **浮动导航栏** | 添加 `top-4 left-4 right-4` 间距 | 将导航栏固定在 `top-0 left-0 right-0` |
| **内容填充** | 考虑固定导航栏的高度 | 让内容被固定元素遮挡 |
| **一致的容器宽度** | 使用相同的 `max-w-6xl` 或 `max-w-7xl` | 混合不同的容器宽度 |

---

## 交付前检查清单

在交付 UI 代码之前，请验证以下项目：

### 视觉质量
- [ ] 未使用表情符号作为图标（使用 SVG 代替）
