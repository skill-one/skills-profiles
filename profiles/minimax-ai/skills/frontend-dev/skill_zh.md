# 前端工作室

通过协调 5 项专门能力来构建完整的、可用于生产的前端页面：设计工程、动效系统、AI 生成资产、有说服力的文案和生成式艺术。

## 调用方式

```
/frontend-dev <请求>
```

用户以自然语言提供他们的请求（例如："为音乐流媒体应用构建一个落地页"）。

## 技能结构

```
frontend-dev/
├── SKILL.md                      # 核心技能（此文件）
├── scripts/                      # 资产生成脚本
│   ├── minimax_tts.py            # 文本转语音
│   ├── minimax_music.py          # 音乐生成
│   ├── minimax_video.py          # 视频生成（异步）
│   └── minimax_image.py          # 图片生成
├── references/                   # 详细指南（按需阅读）
│   ├── minimax-cli-reference.md  # CLI 标志快速参考
│   ├── asset-prompt-guide.md     # 资产提示工程规则
│   ├── minimax-tts-guide.md      # TTS 使用和语音
│   ├── minimax-music-guide.md    # 音乐提示和歌词格式
│   ├── minimax-video-guide.md    # 相机指令和模型
│   ├── minimax-image-guide.md    # 比例和批量生成
│   ├── minimax-voice-catalog.md  # 所有语音 ID
│   ├── motion-recipes.md         # 动画代码片段
│   ├── env-setup.md              # 环境设置
│   └── troubleshooting.md        # 常见问题
├── templates/                    # 视觉艺术模板
│   ├── viewer.html               # p5.js 交互式艺术基础
│   └── generator_template.js     # p5.js 代码参考
└── canvas-fonts/                 # 静态艺术字体（TTF + 许可证）
```

## 项目结构

### 资产（通用）

所有框架都使用相同的资产组织方式：

```
assets/
├── images/
│   ├── hero-landing-1710xxx.webp
│   ├── icon-feature-01.webp
│   └── bg-pattern.svg
├── videos/
│   ├── hero-bg-1710xxx.mp4
│   └── demo-preview.mp4
└── audio/
    ├── bgm-ambient-1710xxx.mp3
    └── tts-intro-1710xxx.mp3
```

**资产命名：** `{类型}-{描述符}-{时间戳}.{扩展名}`

### 按框架划分

| 框架        | 资产位置        | 组件位置      |
|-------------|-----------------|---------------|
| **纯 HTML** | `./assets/`     | N/A (内联或 `./js/`) |
| **React/Next.js** | `public/assets/` | `src/components/` |
| **Vue/Nuxt** | `public/assets/` | `src/components/` |
| **Svelte/SvelteKit** | `static/assets/` | `src/lib/components/` |
| **Astro**   | `public/assets/` | `src/components/` |

### 纯 HTML

```
project/
├── index.html
├── assets/
│   ├── images/
│   ├── videos/
│   └── audio/
├── css/
│   └── styles.css
└── js/
    └── main.js           # 动画 (GSAP/vanilla)
```

### React / Next.js

```
project/
├── public/assets/        # 静态资产
├── src/
│   ├── components/
│   │   ├── ui/           # 按钮、卡片、输入框
│   │   ├── sections/     # 英雄区、功能区、CTA
│   │   └── motion/       # RevealSection、StaggerGrid
│   ├── lib/
│   ├── styles/
│   └── app/              # 页面
└── package.json
```

### Vue / Nuxt

```
project/
├── public/assets/
├── src/                  # 或 Nuxt 根目录
│   ├── components/
│   │   ├── ui/
│   │   ├── sections/
│   │   └── motion/
│   ├── composables/      # 共享逻辑
│   ├── pages/
│   └── assets/           # 处理后的资产 (可选)
└── package.json
```

### Astro

```
project/
├── public/assets/
├── src/
│   ├── components/       # .astro, .tsx, .vue, .svelte
│   ├── layouts/
│   ├── pages/
│   └── styles/
└── package.json
```

**组件命名：** PascalCase (`HeroSection.tsx`, `HeroSection.vue`, `HeroSection.astro`)

---

## 合规性

**本技能中的所有规则都是强制性的。违反任何规则都会导致阻止性错误——在继续或交付之前修复。**

---

## 工作流程
### 第一阶段：设计架构
1. 分析请求——确定页面类型和上下文
2. 根据页面类型设置设计旋钮
3. 规划布局区域并确定资产需求

### 第二阶段：动效架构
1. 根据每个区域选择动画工具（参见工具选择矩阵）
2. 遵循性能守则规划动效序列

### 第三阶段：资产生成
使用 `scripts/` 生成所有图像/视频/音频资产。**绝对不要**使用占位符 URL（unsplash、picsum、placeholder.com、via.placeholder、placehold.co 等）或外部 URL。

1. 解析资产需求（类型、风格、规格、用途）
2. 编写优化的提示，向用户展示并确认后再生成
3. 通过脚本执行，保存到项目——在所有资产本地保存之前**不要**进入第五阶段

### 第四阶段：文案和内容
遵循文案框架（AIDA、PAS、FAB）来编写所有文本内容。**绝对不要**使用 "Lorem ipsum"——编写真实的文案。

### 第五阶段：构建 UI
搭建项目并遵循设计和动效规则构建每个区域。集成生成的资产和文案。所有 `<img>`、`<video>`、`<source>` 和 CSS `background-image` 必须引用第三阶段生成的本地资产。

### 第六阶段：质量门禁
运行最终清单（参见质量门禁部分）。

---

# 1. 设计工程

## 1.1 基线配置

| 旋钮        | 默认值 | 范围     |
|-------------|--------|----------|
| DESIGN_VARIANCE | 8     | 1=对称, 10=非对称 |
| MOTION_INTENSITY | 6     | 1=静态, 10=电影感 |
| VISUAL_DENSITY | 4     | 1=稀疏, 10=密集 |

根据用户请求动态调整。

## 1.2 架构约定
- **依赖验证：** 在导入任何库之前检查 `package.json`。如果缺失，输出安装命令。
- **框架：** React/Next.js。默认使用服务器组件。交互式组件必须是隔离的 `"use client"` 叶组件。
- **样式：** Tailwind CSS。检查 `package.json` 中的版本——**绝对不要**混合 v3/v4 语法。
- **反表情符号政策：** **绝对不要**在任何地方使用表情符号。仅使用 Phosphor 或 Radix 图标。
- **视口：** 使用 `min-h-[100dvh]` 而不是 `h-screen`。使用 CSS Grid 而不是 flex 百分比数学。
- **布局：** `max-w-[1400px] mx-auto` 或 `max-w-7xl`。

## 1.3 设计规则
| 规则        | 指令     |
|-------------|----------|
| 字体        | 标题：`text-4xl md:text-6xl tracking-tighter`。正文：`text-base leading-relaxed max-w-[65ch]`。**绝对不要**使用 Inter——使用 Geist/Outfit/Satoshi。**绝对不要**在仪表板上使用衬线字体。 |
| 颜色        | 最大 1 个强调色，饱和度 < 80%。**绝对不要**使用 AI 紫色/蓝色。坚持使用一个调色板。 |
| 布局        | **绝对不要**在 VARIANCE > 4 时使用居中英雄区。强制使用分屏或非对称布局。 |
| 卡片        | **绝对不要**在 DENSITY > 7 时使用通用卡片。使用 `border-t`、`divide-y` 或间距。 |
| 状态        | **始终**实现：加载（骨架屏）、空、错误、触觉反馈（`scale-[0.98]`）。 |
| 表单        | 标签在输入框上方。错误在下方。`gap-2` 用于输入块。 |

## 1.4 反滑技术

- **液体玻璃：** `backdrop-blur` + `border-white/10` + `shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`
- **磁性按钮：** 使用 `useMotionValue`/`useTransform`——**绝对不要**使用 `useState` 进行连续动画
- **持续动效：** 当 INTENSITY > 5 时，添加无限微动画（脉冲、漂浮、闪烁）
- **布局过渡：** 使用 Framer `layout` 和 `layoutId` 属性
- **交错：** 使用 `staggerChildren` 或 CSS `animation-delay: calc(var(--index) * 100ms)`

## 1.5 禁止模式
| 类别        | 禁止     |
|-------------|----------|
| 视觉        | 氛围灯、纯黑色 (#000)、过度饱和强调色、标题上的渐变文本、自定义光标 |
| 字体        | Inter 字体、过大的 H1、仪表板上的衬线 |
| 布局        | 3 列等宽卡片行、间距不自然的悬浮元素 |
| 组件        | 默认 shadcn/ui 而未进行定制 |

## 1.6 创意武器库

| 类别        | 模式     |
|-------------|----------|
| 导航        | 锚点放大、磁性按钮、粘性菜单、动态岛、径向菜单、快速拨号、巨型菜单 |
| 布局        | Bento 网格、马赛克、Chroma 网格、分屏滚动、窗帘揭示 |
| 卡片        | 视差倾斜、高亮边框、玻璃态、全息镀层、滑动堆栈、变形模态 |
| 滚动        | 粘性堆栈、水平劫持、Locomotive 序列、缩放视差、进度路径、液体滑动 |
| 画廊        | 球顶画廊、Coverflow、拖动平移、手风琴滑块、悬停轨迹、故障效果 |
| 文本        | 动态字幕、文本遮罩揭示、打乱效果、圆形路径、渐变描边、动态网格 |
| 微动效      | 粒子爆炸、下拉刷新、骨架闪烁、方向性悬停、涟漪点击、SVG 绘制、网格渐变、镜头模糊 |

## 1.7 Bento 范式

- **调色板：** 背景 `#f9fafb`，卡片纯白色带 `border-slate-200/50`
- **表面：** `rounded-[2.5rem]`，扩散阴影
- **字体：** Geist/Satoshi，`tracking-tight` 标题
- **标签：** 卡片内外
- **动画：** 弹簧物理 (`stiffness: 100, damping: 20`)，无限循环，`React.memo` 隔离

**5 卡原型：**
1. 智能列表——使用 `layoutId` 的自动排序
2. 命令输入——打字机效果 + 闪烁光标
3. 实时状态——呼吸指示器
4. 宽数据流——无限水平轮播
5. 上下文 UI——交错高亮 + 漂浮工具栏

## 1.8 品牌覆盖

当品牌样式激活时：
- 暗色：`#141413`，亮色：`#faf9f5`，中等：`#b0aea5`，微妙：`#e8e6dc`
- 强调色：橙色 `#d97757`，蓝色 `#6a9bcc`，绿色 `#788c5d`
- 字体：Poppins（标题），Lora（正文）

---

# 2. 动效引擎

## 2.1 工具选择矩阵

| 需求        | 工具     |
|-------------|----------|
| UI 进入/退出/布局 | **Framer Motion** — `AnimatePresence`、`layoutId`、弹簧 |
| 滚动叙事（固定、滚动） | **GSAP + ScrollTrigger** — 帧精确控制 |
| 循环图标    | **Lottie** — 懒加载 (~50KB) |
| 3D/WebGL   | **Three.js / R3F** — 隔离的 `<Canvas>`，自己的 `"use client"` 边界 |
| 悬停/焦点状态 | **纯 CSS** — 零 JS 成本 |
| 本地滚动驱动 | **CSS** — `animation-timeline: scroll()` |

**冲突规则 [强制执行]：**
- **绝对不要**在同一个组件中混合 GSAP + Framer Motion
- R3F 必须存在于隔离的 Canvas 包装器中
- **始终**懒加载 Lottie、GSAP、Three.js

## 2.2 强度等级

| 等级        | 技术     |
|-------------|----------|
| 1-2 微妙    | 仅 CSS 过渡，150-300ms |
| 3-4 平滑    | CSS 关键帧 + Framer animate，交错 ≤3 项 |
| 5-6 流畅    | `whileInView`、磁性悬停、视差倾斜 |
| 7-8 电影感  | GSAP ScrollTrigger、固定区域、水平劫持 |
| 9-10 沉浸式 | 完全滚动序列、Three.js 粒子、WebGL 着色器 |

## 2.3 动效配方

参见 `references/motion-recipes.md` 获取完整代码。摘要：

| 配方        | 工具     | 用于     |
|-------------|----------|----------|
| 滚动揭示    | Framer   | 视口进入时的淡出+滑动 |
| 交错网格    | Framer   | 顺序列表动画 |
| 固定时间线  | GSAP     | 水平滚动固定 |
| 倾斜卡片    | Framer   | 鼠标跟踪 3D 透视 |
| 磁性按钮    | Framer   | 光标吸引按钮 |
| 文本打乱    | 纯 CSS   | 矩阵风格解码效果 |
| SVG 路径绘制 | CSS     | 滚动链接路径动画 |
| 水平滚动    | GSAP     | 垂直到水平劫持 |
| 粒子背景    | R3F      | 装饰性 WebGL 粒子 |
| 布局变形    | Framer   | 卡片到模态扩展 |

## 2.4 性能规则
**仅 GPU 属性（仅动画这些）：** `transform`、`opacity`、`filter`、`clip-path`

**绝对不要**动画：`width`、`height`、`top`、`left`、`margin`、`padding`、`font-size`——如果你需要这些效果，使用 `transform: scale()` 或 `clip-path` 代替。

**隔离：**
- 持续动画必须在 `React.memo` 叶组件中
- `will-change: transform` 仅在动画期间
- `contain: layout style paint` 在重型容器上

**移动端：**
- **始终**尊重 `prefers-reduced-motion`
- **始终**在 `pointer: coarse` 上禁用视差/3D
- 粒子数量限制：桌面 800，平板 300，手机 100
- 在移动端 < 768px 时禁用 GSAP 固定

**清理：** 每个 `useEffect` 带有 GSAP/观察者的 `return () => ctx.revert()`

## 2.5 弹簧和缓动

| 感觉        | Framer 配置 |
|-------------|--------------|
| 快速        | `stiffness: 300, damping: 30` |
| 平滑        | `stiffness: 150, damping: 20` |
| 弹性        | `stiffness: 100, damping: 10` |
| 重型        | `stiffness: 60, damping: 20` |

| CSS 缓动    | 值         |
|-------------|------------|
| 平滑减速    | `cubic-bezier(0.16, 1, 0.3, 1)` |
| 平滑加速    | `cubic-bezier(0.7, 0, 0.84, 0)` |
| 弹性        | `cubic-bezier(0.34, 1.56, 0.64, 1)` |

## 2.6 可访问性
- **始终**在 `prefers-reduced-motion` 检查中包装动效
- **绝对不要**让内容闪烁 > 3 次/秒（癫痫风险）
- **始终**提供可见的焦点环（使用 `outline` 而不是 `box-shadow`）
- **始终**为动态显示的内容添加 `aria-live="polite"`
- **始终**包含自动播放动画的暂停按钮

## 2.7 依赖项

```bash
npm install framer-motion           # UI (保持在最顶层)
npm install gsap                    # 滚动 (懒加载)
npm install lottie-react            # 图标 (懒加载)
npm install three @react-three/fiber @react-three/drei  # 3D (懒加载)
```

---

# 3. 资产生成

## 3.1 脚本

| 类型        | 脚本         | 模式     |
|-------------|--------------|----------|
| TTS        | `scripts/minimax_tts.py` | 同步     |
| 音乐        | `scripts/minimax_music.py` | 同步     |
| 视频        | `scripts/minimax_video.py` | 异步 (创建→轮询→下载) |
| 图片        | `scripts/minimax_image.py` | 同步     |

环境：`MINIMAX_API_KEY`（必需）。

## 3.2 工作流程
1. **解析：** 类型、数量、风格、规格、用途
2. **编写提示：** 具体说明（构图、光照、风格）。**绝对不要**在图像提示中包含文本。
3. **执行：** 向用户展示提示，**必须**在生成前确认，然后运行脚本
4. **保存：** `<项目>/public/assets/{images,videos,audio}/` 作为 `{类型}-{描述符}-{时间戳}.{扩展名}` — **必须**本地保存
5. **后处理：** 图片 → WebP，视频 → ffmpeg 压缩，音频 → 归一化
6. **交付：** 文件路径 + 代码片段 + CSS 建议

## 3.3 快捷键预设

| 快捷键      | 规格     |
|-------------|----------|
| `hero`      | 16:9, 电影感, 文本安全 |
| `thumb`     | 1:1, 居中主体 |
| `icon`      | 1:1, 平面, 干净背景 |
| `avatar`    | 1:1, 纪念, 圆形裁剪准备 |
| `banner`    | 21:9, OG/社交 |
| `bg-video`  | 768P, 6s, `[静态镜头]` |
| `video-hd`  | 1080P, 6s |
| `bgm`       | 30s, 无人声, 可循环 |
| `tts`       | MiniMax HD, MP3 |

## 3.4 参考

- `references/minimax-cli-reference.md` — CLI 标志
- `references/asset-prompt-guide.md` — 提示规则
- `references/minimax-voice-catalog.md` — 语音 ID
- `references/minimax-tts-guide.md` — TTS 使用
- `references/minimax-music-guide.md` — 音乐生成（提示、歌词、结构标签）
- `references/minimax-video-guide.md` — 相机指令
- `references/minimax-image-guide.md` — 比例, 批量

---

# 4. 文案

## 4.1 核心任务

1. 吸引注意力 → 2. 创造欲望 → 3. 移除摩擦 → 4. 提示行动

## 4.2 框架

**AIDA**（落地页、邮件）:
```
ATTENTION:  粗体标题 (承诺或痛苦)
INTEREST:   详细说明问题 ("是的，就是我")
DESIRE:     展示转变
ACTION:     清晰的 CTA
```

**PAS**（痛苦驱动产品）:
```
PROBLEM:    清晰说明
AGITATE:    制造紧迫感
SOLUTION:   你的产品
```

**FAB**（产品差异化）:
```
FEATURE:    它的功能
ADVANTAGE:  它为什么重要
BENEFIT:    客户获得什么
```

## 4.3 标题

| 公式        | 示例     |
|-------------|----------|
| 承诺        | "30 天内翻倍打开率" |
| 提问        | "仍然浪费 10 小时/周?" |
| 如何做      | "如何自动化你的管道" |
| 数字        | "7 个导致转化率下降的错误" |
| 负面        | "停止失去线索" |
| 好奇        | "唯一能将预订量翻三倍的改变" |
| 转变        | "从 50 到 500 条线索" |

具体。以结果开头，而不是方法。

## 4.4 CTA

**不好：** 提交, 点击这里, 了解更多

**好：** "开始我的免费试用", "立即获取模板", "预约我的策略咨询"

**公式：** [动词] + [他们能得到什么] + [紧迫感/便利性]

位置：页眉以上, 值之后, 长页面上的多个 CTA。

## 4.5 情感触发器

| 触发器      | 示例     |
|-------------|----------|
| FOMO        | "仅剩 3 个名额" |
| 恐惧损失    | "每天不使用这个，你将损失 $X" |
| 地位        | "加入 10,000+ 顶级机构" |
| 便利        | "设置一次，永远忘记。" |
| 沮丧        | "厌倦了毫无价值的工具?" |
| 希望        | "是的，你可以达到 $10K MRR" |

## 4.6 反驳处理

| 反驳        | 响应     |
|-------------|----------|
| 太贵        | 展示 ROI: "2 周内收回成本" |
| 不适合我    | 类似客户的社交证明 |
| 没时间      | "设置只需 10 分钟" |
| 会失败      | "30 天退款保证" |
| 需要考虑    | 紧迫感/稀缺性 |

位置：FAQ、客户评价、CTA 附近。

## 4.7 证明类型

客户评价（带姓名/头衔）、案例研究、数据/指标、社交证明、认证

---

# 5. 视觉艺术

以哲学为先的工作流程。两种输出模式。

## 5.1 输出模式

| 模式        | 输出     | 使用场景     |
|-------------|----------|--------------|
| 静态        | PDF/PNG  | 海报、印刷、设计资产 |
| 交互式      | HTML (p5.js) | 生成式艺术、可探索的变化 |

## 5.2 工作流程

### 第一步：哲学创建
命名运动（1-2 个词）。阐述哲学（4-6 段话），涵盖：
- 静态：空间、形式、颜色、比例、节奏、层次
- 交互式：计算、涌现、噪声、参数化变化

### 第二步：概念种子
识别微妙的、专业的参考——高级的，而不是字面的。爵士音乐家引用另一首歌。

### 第三步：创作

**静态模式：**
- 单页，高度视觉化，设计导向
- 重复图案，完美的形状
- 稀疏的 `canvas-fonts/` 字体
- 任何东西都不重叠，适当的边距
- 输出：`.pdf` 或 `.png` + 哲学 `.md`

**交互式模式：**
1. 首先阅读 `templates/viewer.html`
2. 保持固定的区域（页眉、侧边栏、种子控制）
3. 替换可变区域（算法、参数）
4. 种子随机性：`randomSeed(seed); noiseSeed(seed);`
5. 输出：单个自包含 HTML

### 第四步：精炼
精炼，不要添加。让它变得清晰。打磨成杰作。

---

# 质量门禁
**设计：**
- [ ] 移动布局折叠 (`w-full`, `px-4`) 对于高 VARIANCE 设计
- [ ] `min-h-[100dvh]` 不是 `h-screen`
- [ ] 提供空、加载、错误状态
- [ ] 在空间足够时省略卡片

**动效：**
- [ ] 每个工具选择矩阵的正确工具
- [ ] 同一组件中**绝对不要**混合 GSAP + Framer Motion
- [ ] 所有 `useEffect` 都有清理返回
- [ ] 尊重 `prefers-reduced-motion`
- [ ] 持续动画在 `React.memo` 叶组件中
- [ ] 仅 GPU 属性进行动画
- [ ] 重型库懒加载

**通用：**
- [ ] 在 `package.json` 中验证依赖项
- **不要使用占位符 URL** — 在输出中搜索 `unsplash`, `picsum`, `placeholder`, `placehold`, `via.placeholder`, `lorem.space`, `dummyimage`。如果找到**任何**，停止并使用生成的资产替换，然后再交付。
- **所有媒体资产都是项目的 assets 目录中的本地文件**
- **在生成前与用户确认资产提示**

---

*React 和 Next.js 是 Meta Platforms, Inc. 和 Vercel, Inc. 的商标，分别。Vue.js 是 Evan You 的商标。Tailwind CSS 是 Tailwind Labs Inc. 的商标。Svelte 和 SvelteKit 是各自所有者的商标。GSAP/GreenSock 是 GreenSock Inc. 的商标。Three.js、Framer Motion、Lottie、Astro 和所有其他产品名称都是各自所有者的商标。*
