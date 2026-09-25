# UI/UX Pro Max - 设计智能

面向网页和移动应用的全面设计指南。包含50多种风格、97种配色方案、57种字体搭配、99条UX设计指南以及9种技术栈下的25种图表类型。支持基于优先级的搜索数据库。

## 何时应用

在以下情况下参考这些指南：
- 设计新的UI组件或页面
- 选择配色方案和排版
- 审查代码中的UX问题
- 构建落地页或仪表盘
- 实施无障碍要求

## 按优先级分类的规则

| 优先级 | 类别 | 影响 | 领域 |
|--------|------|------|------|
| 1 | 无障碍 | 关键 | `ux` |
| 2 | 触摸与交互 | 关键 | `ux` |
| 3 | 性能 | 高 | `ux` |
| 4 | 布局与响应式 | 高 | `ux` |
| 5 | 排版与颜色 | 中 | `typography`, `color` |
| 6 | 动画 | 中 | `ux` |
| 7 | 风格选择 | 中 | `style`, `product` |
| 8 | 图表与数据 | 低 | `chart` |

## 快速参考

### 1. 无障碍 (关键)

- `color-contrast` - 正常文本对比度至少为4.5:1
- `focus-states` - 交互元素上有可见的焦点环
- `alt-text` - 对有意义的图像提供描述性替代文本
- `aria-labels` - 图标按钮使用aria-label
- `keyboard-nav` - Tab顺序与视觉顺序一致
- `form-labels` - 使用带for属性的标签

### 2. 触摸与交互 (关键)

- `touch-target-size` - 触摸目标最小尺寸44x44px
- `hover-vs-tap` - 主要交互使用点击/轻触
- `loading-buttons` - 异步操作期间禁用按钮
- `error-feedback` - 在问题附近显示清晰的错误消息
- `cursor-pointer` - 可点击元素添加`cursor-pointer`

### 3. 性能 (高)

- `image-optimization` - 使用WebP、srcset、懒加载
- `reduced-motion` - 检查prefers-reduced-motion
- `content-jumping` - 为异步内容预留空间

### 4. 布局与响应式 (高)

- `viewport-meta` - width=device-width initial-scale=1
- `readable-font-size` - 移动端正文最小字号16px
- `horizontal-scroll` - 确保内容适配视口宽度
- `z-index-management` - 定义z-index等级（10, 20, 30, 50）

### 5. 排版与颜色 (中)

- `line-height` - 正文使用1.5-1.75的行高
- `line-length` - 每行限制65-75个字符
- `font-pairing` - 匹配标题/正文字体的风格

### 6. 动画 (中)

- `duration-timing` - 微交互使用150-300ms的时长
- `transform-performance` - 使用transform/opacity而非width/height
- `loading-states` - 使用骨架屏或加载动画

### 7. 风格选择 (中)

- `style-match` - 根据产品类型匹配风格
- `consistency` - 在所有页面使用相同风格
- `no-emoji-icons` - 使用SVG图标而非表情符号

### 8. 图表与数据 (低)

- `chart-type` - 根据数据类型选择图表类型
- `color-guidance` - 使用无障碍配色方案
- `data-table` - 为无障碍提供表格替代方案

## 如何使用

使用CLI工具搜索特定领域。

---

## 前置条件

检查Python是否已安装：

```bash
python3 --version || python --version
```

如果未安装Python，根据用户操作系统安装：

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

当用户请求UI/UX工作（设计、构建、创建、实施、审查、修复、改进）时，请遵循以下工作流程：

### 第1步：分析用户需求

从用户请求中提取关键信息：
- **产品类型**：SaaS、电商、作品集、仪表盘、落地页等
- **风格关键词**：极简、有趣、专业、优雅、暗黑模式等
- **行业**：医疗、金融科技、游戏、教育等
- **技术栈**：React、Vue、Next.js，默认为`html-tailwind`

### 第2步：生成设计系统（必填）

**始终使用`--design-system`**以获取包含推理的全面建议：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "项目名称"]
```

此命令：
1. 并行搜索5个领域（产品、风格、颜色、落地页、排版）
2. 应用`ui-reasoning.csv`中的推理规则选择最佳匹配
3. 返回完整设计系统：模式、风格、颜色、排版、效果
4. 包含需要避免的反模式

**示例：**
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 第3步：补充详细搜索（按需）

获取设计系统后，使用领域搜索获取更多细节：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <最大结果数>]
```

**何时使用详细搜索：**

| 需求 | 领域 | 示例 |
|------|------|------|
| 更多风格选项 | `style` | `--domain style "glassmorphism dark"` |
| 图表建议 | `chart` | `--domain chart "real-time dashboard"` |
| UX最佳实践 | `ux` | `--domain ux "animation accessibility"` |
| 替代字体 | `typography` | `--domain typography "elegant luxury"` |
| 落地页结构 | `landing` | `--domain landing "hero social-proof"` |

### 第4步：技术栈指南（默认：html-tailwind）

获取特定实现的最佳实践。如果用户未指定技术栈，**默认为`html-tailwind`**。

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```

可用技术栈：`html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`

---

## 搜索参考

### 可用领域

| 领域 | 用于 | 示例关键词 |
|------|------|------------|
| `product` | 产品类型建议 | SaaS, 电商, 作品集, 医疗, 美容, 服务 |
| `style` | UI风格、颜色、效果 | glassmorphism, 极简主义, 暗黑模式, 布鲁特alist |
| `typography` | 字体搭配、Google Fonts | 优雅, 有趣, 专业, 现代 |
| `color` | 按产品类型分类的配色方案 | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | 页面结构、CTA策略 | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | 图表类型、库推荐 | trend, comparison, timeline, funnel, pie |
| `ux` | 最佳实践、反模式 | animation, accessibility, z-index, loading |
| `react` | React/Next.js性能 | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | 网页界面指南 | aria, focus, keyboard, semantic, virtualize |
| `prompt` | AI提示、CSS关键词 | (风格名称) |

### 可用技术栈

| 技术栈 | 重点 |
|------|------|
| `html-tailwind` | Tailwind工具、响应式、无障碍 (默认) |
| `react` | 状态、hooks、性能、模式 |
| `nextjs` | SSR、路由、图片、API路由 |
| `vue` | Composition API、Pinia、Vue Router |
| `svelte` | Runes、stores、SvelteKit |
| `swiftui` | Views、State、导航、动画 |
| `react-native` | 组件、导航、列表 |
| `flutter` | Widgets、状态、布局、主题 |
| `shadcn` | shadcn/ui组件、主题、表单、模式 |

---

## 示例工作流程

**用户请求：** "为专业护肤服务制作落地页"

### 第1步：分析需求
- 产品类型：美容/水疗服务
- 风格关键词：优雅、专业、柔和
- 行业：美容/健康
- 技术栈：html-tailwind（默认）

### 第2步：生成设计系统（必填）

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service elegant" --design-system -p "Serenity Spa"
```

**输出：** 完整设计系统，包含模式、风格、颜色、排版、效果和反模式。

### 第3步：补充详细搜索（按需）

```bash
# 获取动画和可访问性的UX指南
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# 如有需要，获取替代排版选项
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "elegant luxury serif" --domain typography
```

### 第4步：技术栈指南

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "layout responsive form" --stack html-tailwind
```

**然后：** 综合设计系统+详细搜索并实施设计。

---

## 输出格式

`--design-system` 标志支持两种输出格式：

```bash
# ASCII框（默认）- 最佳终端显示
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown - 最佳文档显示
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## 获取更好结果的技巧

1. **关键词要具体** - "医疗SaaS仪表盘" > "应用"
2. **多次搜索** - 不同关键词会揭示不同见解
3. **组合领域** - 风格+排版+颜色=完整设计系统
4. **始终检查UX** - 搜索"动画"、"z-index"、"可访问性"以发现常见问题
5. **使用技术栈标志** - 获取特定实现的最佳实践
6. **迭代** - 如果首次搜索不匹配，尝试不同关键词

---

## 专业UI的常见规则

这些是经常被忽视的问题，使UI看起来不专业：

### 图标与视觉元素

| 规则 | 做到 | 不要 |
|------|------|------|
| **不使用表情符号图标** | 使用SVG图标（Heroicons、Lucide、Simple Icons） | 使用表情符号作为UI图标 🎨 🚀 ⚙️ |
| **稳定的悬停状态** | 使用颜色/不透明度过渡悬停 | 使用导致布局偏移的缩放变换 |
| **正确的品牌标志** | 从Simple Icons获取官方SVG | 猜测或使用错误的标志路径 |
| **一致的图标尺寸** | 使用固定viewBox（24x24）配合w-6 h-6 | 随机混合不同尺寸的图标 |

### 交互与光标

| 规则 | 做到 | 不要 |
|------|------|------|
| **光标指针** | 所有可点击/悬停卡片添加`cursor-pointer` | 留下默认光标在交互元素上 |
| **悬停反馈** | 提供视觉反馈（颜色、阴影、边框） | 没有交互元素的视觉指示 |
| **平滑过渡** | 使用`transition-colors duration-200` | 状态变化过快或过慢（>500ms） |

### 明/暗模式对比度

| 规则 | 做到 | 不要 |
|------|------|------|
| **明模式玻璃卡片** | 使用`bg-white/80`或更高不透明度 | 使用`bg-white/10`（太透明） |
| **明模式文本对比度** | 使用`#0F172A`（slate-900）作为文本 | 使用`#94A3B8`（slate-400）作为正文 |
| **明模式弱文本** | 最小使用`#475569`（slate-600） | 使用gray-400或更浅 |
| **边框可见性** | 使用`border-gray-200`在明模式下 | 使用`border-white/10`（不可见） |

### 布局与间距

| 规则 | 做到 | 不要 |
|------|------|------|
| **浮动导航栏** | 添加`top-4 left-4 right-4`间距 | 粘性导航栏到`top-0 left-0 right-0` |
| **内容填充** | 考虑固定导航栏的高度 | 让内容被固定元素遮挡 |
| **一致的容器宽度** | 使用相同的`max-w-6xl`或`max-w-7xl` | 混合不同的容器宽度 |

---

## 交付前检查清单

在交付UI代码前，验证以下项目：

### 视觉质量
- [ ] 不使用表情符号作为图标（使用SVG替代）
- [ ] 所有图标来自一致的图标集（Heroicons/Lucide）
- [ ] 品牌标志正确（从Simple Icons验证）
- [ ] 悬停状态不会导致布局偏移
- [ ] 直接使用主题颜色（bg-primary）而非var()包装

### 交互
- [ ] 所有可点击元素有`cursor-pointer`
- [ ] 悬停状态提供清晰的视觉反馈
- [ ] 过渡平滑（150-300ms）
- [ ] 焦点状态对键盘导航可见

### 明/暗模式
- [ ] 明模式文本对比度充足（至少4.5:1）
- [ ] 玻璃/透明元素在明模式下可见
- [ ] 边框在两种模式下都可见
- [ ] 交付前测试两种模式

### 布局
- [ ] 浮动元素与边缘有适当间距
- [ ] 无内容被固定导航栏遮挡
- [ ] 在375px、768px、1024px、1440px下响应式
- [ ] 无水平滚动（移动端）

### 可访问性
- [ ] 所有图像有替代文本
- [ ] 表单输入有标签
- [ ] 颜色不是唯一的指示
- [ ] 尊重`prefers-reduced-motion`
