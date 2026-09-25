# PPT生成技能

## 概述

该技能通过为每张幻灯片创建AI生成的图像，并将它们组合成一个PPTX文件来生成专业的PowerPoint演示文稿。工作流程包括规划具有一致视觉风格的演示文稿结构，按顺序生成幻灯片图像（使用前一张幻灯片作为风格一致性参考），并将它们组装成最终的演示文稿。

## 核心功能

- 规划和构建具有统一视觉风格的多张幻灯片演示文稿
- 支持多种演示文稿风格：商业、学术、极简、Apple Keynote、创意
- 使用图像生成技能为每张幻灯片生成独特的AI图像
- 通过使用前一张幻灯片作为参考图像来保持视觉一致性
- 将图像组合成专业的PPTX文件

## 演示文稿风格

在创建演示文稿计划时，选择以下风格之一：

| 风格 | 描述 | 适合场景 |
|------|------|----------|
| **glassmorphism** | 水晶玻璃面板带有模糊效果，悬浮的半透明卡片，充满活力的渐变背景，通过层叠创建深度 | 科技产品，AI/SaaS演示，未来主义提案 |
| **dark-premium** | 丰富的黑色背景(#0a0a0a)，发光的强调色，微妙的发光效果，奢华品牌美学 | 奢侈品，高管演示，高端品牌 |
| **gradient-modern** | 大胆的网格渐变，流畅的色彩过渡，现代字体设计，充满活力且精致 | 初创公司，创意代理，品牌发布 |
| **neo-brutalist** | 原始粗犷的字体设计，高对比度，故意的“丑陋”美学，反设计即设计，Memphis风格灵感 | 个性品牌，针对Gen-Z，颠覆性初创公司 |
| **3d-isometric** | 干净的等距立体插图，悬浮的3D元素，柔和阴影，科技前沿美学 | 科技解释，产品特性，SaaS演示 |
| **editorial** | 杂志级布局，精致的字体层次结构，戏剧性摄影，Vogue/Bloomberg美学 | 年度报告，奢侈品，思想领导力 |
| **minimal-swiss** | 基于网格的精确度，Helvetica风格的字体设计，大胆使用负空间，永恒的现代主义 | 建筑设计公司，设计公司，高端咨询 |
| **keynote** | 受Apple启发的美学，粗犷的字体设计，戏剧性图像，高对比度，电影感 | 主讲会，产品发布，鼓舞人心的演讲 |

## 工作流程

### 第1步：理解需求

当用户请求演示文稿生成时，识别：

- 主题/科目：演示文稿是关于什么的
- 幻灯片数量：需要多少张幻灯片（默认：5-10）
- **风格**：商业 / 学术 / 极简 / Keynote / 创意
- 宽高比：标准(16:9)或经典(4:3)
- 内容大纲：每张幻灯片的关键点
- 无需检查`/mnt/user-data`下的文件夹

### 第2步：创建演示文稿计划

在`/mnt/user-data/workspace/`中创建一个包含演示文稿结构的JSON文件。**重要**：包含`style`字段来定义整体视觉一致性。

```json
{
  "title": "演示文稿标题",
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "深黑色背景(#0a0a0a)，白色文本，单一强调色（蓝色或橙色）",
    "typography": "粗体无衬线标题（SF Pro Display风格），干净的正文文本，戏剧性的尺寸对比",
    "imagery": "高质量摄影，全屏图像，电影级构图",
    "layout": "充足的空白空间，居中焦点，每张幻灯片上的元素最少",
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "主标题",
      "subtitle": "副标题或标签",
      "visual_description": "为图像生成提供详细描述"
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "幻灯片标题",
      "key_points": ["要点1", "要点2", "要点3"],
      "visual_description": "为图像生成提供详细描述"
    }
  ]
}
```

### 第3步：按顺序生成幻灯片图像

**重要**：严格按顺序生成幻灯片，**不要**并行或批量生成图像。每张幻灯片都依赖于前一张幻灯片的输出作为参考图像。并行生成幻灯片将破坏视觉一致性，并且不被允许。

1. 阅读图像生成技能：`/mnt/skills/public/image-generation/SKILL.md`

2. **对于第一张幻灯片（幻灯片1）**，创建一个建立视觉风格的提示：

```json
{
  "prompt": "专业演示文稿幻灯片。[style_guidelines from plan]。标题：'您的标题'。[visual_description]。这张幻灯片为整个演示文稿建立了视觉语言。",
  "style": "[基于所选风格 - 例如，Apple Keynote美学，戏剧性光照，电影感]",
  "composition": "干净的布局，清晰的文本层次结构，[风格特定的构图]",
  "color_palette": "[从style_guidelines]",
  "typography": "[从style_guidelines]"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/slide-01-prompt.json \
  --output-file /mnt/user-data/outputs/slide-01.jpg \
  --aspect-ratio 16:9
```

3. **对于后续幻灯片（幻灯片2+）**，使用前一张幻灯片作为参考图像：

```json
{
  "prompt": "专业演示文稿幻灯片，继续参考图像的视觉风格。保持相同的调色板、字体风格和整体美学。标题：'幻灯片标题'。[visual_description]。保持与参考图像的视觉一致性。",
  "style": "完全匹配参考图像的风格",
  "composition": "与参考相似的布局原则，根据内容进行调整",
  "color_palette": "与参考图像相同",
  "consistency_note": "这张幻灯片必须看起来像是同一演示文稿的一部分"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/slide-02-prompt.json \
  --reference-images /mnt-user-data/outputs/slide-01.jpg \
  --output-file /mnt-user-data/outputs/slide-02.jpg \
  --aspect-ratio 16:9
```

4. **继续为所有剩余幻灯片生成**，始终参考前一张幻灯片：

```bash
# 幻灯片3参考幻灯片2
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/slide-03-prompt.json \
  --reference-images /mnt-user-data/outputs/slide-02.jpg \
  --output-file /mnt-user-data/outputs/slide-03.jpg \
  --aspect-ratio 16:9

# 幻灯片4参考幻灯片3
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/slide-04-prompt.json \
  --reference-images /mnt-user-data/outputs/slide-03.jpg \
  --output-file /mnt-user-data/outputs/slide-04.jpg \
  --aspect-ratio 16:9
```

### 第4步：组合PPT

所有幻灯片图像生成后，调用组合脚本：

```bash
python /mnt/skills/public/ppt-generation/scripts/generate.py \
  --plan-file /mnt/user-data/workspace/presentation-plan.json \
  --slide-images /mnt/user-data/outputs/slide-01.jpg /mnt/user-data/outputs/slide-02.jpg /mnt-user-data/outputs/slide-03.jpg \
  --output-file /mnt/user-data/outputs/presentation.pptx
```

参数：

- `--plan-file`：演示文稿计划JSON文件的绝对路径（必需）
- `--slide-images`：按顺序幻灯片图像的绝对路径（必需，空格分隔）
- `--output-file`：输出PPTX文件的绝对路径（必需）

[!NOTE]
**不要**读取python文件，只需使用参数调用它。

## 完整示例：Glassmorphism风格（最现代前卫）

用户请求："创建一个关于AI产品发布的演示文稿"

### 第1步：创建演示文稿计划

创建`/mnt/user-data/workspace/ai-product-plan.json`：
```json
{
  "title": "Introducing Nova AI",
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "充满活力的紫色到青色渐变背景(#667eea→#00d4ff)，15-20%不透明的水晶玻璃面板，电光强调色",
    "typography": "SF Pro Display风格，粗体700权重白色标题带有微妙的文本阴影，干净的400权重正文，玻璃上的优秀对比度",
    "imagery": "抽象3D水晶球体，悬浮的半透明几何形状，柔和发光的球体，通过层叠透明度创建深度",
    "layout": "居中悬浮的水晶玻璃卡片，32px圆角，48-64px内边距，悬浮在渐变上方，通过软阴影创建分层深度",
    "effects": "水晶玻璃面板上的背景模糊20-40px，微妙的白色边框发光，与渐变匹配的软彩色阴影，光折射效果",
    "visual_language": "Apple Vision Pro / visionOS美学，通过透明度创造奢华感，未来主义但易于接近，2024设计趋势"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "Introducing Nova AI",
      "subtitle": "Intelligence, Reimagined",
      "visual_description": "令人惊叹的渐变背景，从深紫色(#667eea)流经品红色到青色(#00d4ff)。居中：大型水晶玻璃面板，带有强烈的背景模糊，其中包含粗体白色标题'Introducing Nova AI'和较浅的副标题。周围悬浮3D水晶球体和抽象形状，创造深度。玻璃面板后面发出柔和的光芒。高端visionOS美学。水晶玻璃卡片带有微妙的白色边框(1px rgba 255,255,255,0.3)和紫色阴影。"
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "Why Nova?",
      "key_points": ["10x faster processing", "Human-like understanding", "Enterprise-grade security"],
      "visual_description": "相同的紫色-青色渐变背景。左侧：悬浮的水晶玻璃卡片，带有标题'Why Nova?'的粗体白色，三个关键点下方带有微妙的玻璃药丸徽章。右侧：抽象3D神经网络可视化，作为相互连接的水晶节点，带有柔和的青色发光。周围悬浮半透明几何形状（二十面体、环面），增加深度。一致的glassmorphism美学，与上一张幻灯片保持一致。"
    },
    {
      "slide_number": 3,
      "type": "content",
      "title": "How It Works",
      "key_points": ["Natural language input", "Multi-modal processing", "Instant insights"],
      "visual_description": "与上一张幻灯片一致的渐变背景。中央构图：三个堆叠的水晶玻璃卡片，略微倾斜，显示工作流步骤，通过软发光线连接。每个卡片都有一个抽象图标。周围悬浮玻璃球体和光粒子。标题'How It Works'在顶部以粗体显示。通过卡片层叠和透明度创建深度。"
    },
    {
      "slide_number": 4,
      "type": "content",
      "title": "Built for Scale",
      "key_points": ["1M+ concurrent users", "99.99% uptime", "Global infrastructure"],
      "visual_description": "相同的渐变背景。非对称布局：右侧有一个大型水晶玻璃面板，其中显示粗体字体的指标。左侧：由水晶面板和连接线组成的抽象3D地球，代表全球规模。悬浮的数据可视化元素作为小玻璃卡片，显示数字。整个环境中都有柔和的环境光。高端科技美学。"
    },
    {
      "slide_number": 5,
      "type": "conclusion",
      "title": "The Future Starts Now",
      "subtitle": "Join the waitlist",
      "visual_description": "戏剧性的结尾幻灯片。渐变背景的鲜艳度略有增加。中央悬浮的水晶玻璃卡片，带有粗体标题'The Future Starts Now'和行动号召副标题。后面：爆发柔和的光线束和悬浮的玻璃粒子，创造庆祝效果。多层玻璃形状创建深度。在保持风格一致性的同时，这是视觉上最具冲击力的幻灯片。"
    }
  ]
}
```

### 第2步：读取图像生成技能

读取`/mnt/skills/public/image-generation/SKILL.md`以了解如何生成图像。

### 第3步：按顺序生成幻灯片图像并参考链接

**幻灯片1 - 标题（建立视觉语言）：**

创建`/mnt/user-data/workspace/nova-slide-01.json`：
```json
{
  "prompt": "超高端演示文稿标题幻灯片，具有glassmorphism设计。背景：平滑流动的渐变，从深紫色(#667eea)流经品红色(#f093fb)到青色(#00d4ff)，柔和且充满活力。居中：大型水晶玻璃面板，带有强烈的背景模糊效果，圆角32px，包含粗体白色无衬线标题'Introducing Nova AI'(72pt, SF Pro Display风格，字体权重700)和微妙的文本阴影，副标题'Intelligence, Reimagined'在下方，较浅的权重。水晶玻璃卡片带有微妙的白色边框(1px rgba 255,255,255,0.25)和紫色阴影。周围悬浮3D水晶球体和折射，半透明的几何形状（二十面体、抽象球体），创造深度和维度。从玻璃面板后面发出柔和的光芒。小悬浮的光粒子。visionOS美学，Apple Vision Pro UI风格，高端科技产品发布感觉。专业演示文稿幻灯片，16:9宽高比。超现代，高端科技感觉。"
  "style": "Glassmorphism, visionOS美学, Apple Vision Pro UI风格, 高端科技, 2024设计趋势",
  "composition": "居中玻璃卡片作为焦点，边缘悬浮3D元素创造深度，40%负空间，清晰的视觉层次",
  "lighting": "渐变发出的柔和环境光，通过玻璃元素的光折射，3D形状的微妙边缘照明",
  "color_palette": "紫色渐变#667eea, 品红色#f093fb, 青色#00d4ff, 水晶玻璃半透明rgba(255,255,255,0.15), 纯白色文本#ffffff",
  "effects": "玻璃面板上的背景模糊，带有颜色阴影的软阴影，光折射，玻璃上的微妙噪声纹理，悬浮粒子"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/nova-slide-01.json \
  --output-file /mnt-user-data/outputs/nova-slide-01.jpg \
  --aspect-ratio 16:9
```

**幻灯片2 - 内容（必须参考幻灯片1以保持一致性）：**

创建`/mnt/user-data/workspace/nova-slide-02.json`：
```json
{
  "prompt": "演示文稿幻灯片继续精确的视觉风格。相同的紫色-青色渐变背景，相同的glassmorphism美学，相同的字体风格。左侧：带有微妙的玻璃药丸徽章的悬浮水晶玻璃卡片，包含粗体白色标题'Why Nova?'（与参考字体风格相同），三个功能点。右侧：由相互连接的水晶节点组成的抽象3D神经网络可视化，带有柔和的青色发光，悬浮在空间中。周围悬浮半透明几何形状（与参考风格相同），增加深度。水晶玻璃具有相同的处理：白色边框，紫色阴影，相同的模糊强度。关键：这张幻灯片必须看起来像是同一演示文稿的一部分 - 相同的颜色，相同的玻璃处理，相同的美学。"
  "style": "MATCH REFERENCE EXACTLY - Glassmorphism, visionOS美学, 相同的视觉语言",
  "composition": "非对称分割：左侧玻璃卡片（40%），右侧（40%），元素之间留有呼吸空间",
  "color_palette": "完全匹配参考：紫色#667eea, 青色#00d4ff渐变, 相同的玻璃模糊强度, 相同的阴影处理, 相同的字体权重和风格。观众应该立即认出这是同一演示文稿的一部分。"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/nova-slide-02.json \
  --reference-images /mnt-user-data/outputs/nova-slide-01.jpg \
  --output-file /mnt-user-data/outputs/nova-slide-02.jpg \
  --aspect-ratio 16:9
```

**幻灯片3-5：继续相同的模式，每张幻灯片都参考前一张幻灯片**

后续幻灯片的关键一致性规则：

- 在每个后续幻灯片提示中，明确声明："继续精确的视觉风格从参考图像"
- 使用"相同的", "精确的", "匹配"等关键词强调以强制一致性
- 在每个JSON提示的幻灯片1之后包含`consistency_note`字段
- 如果一张幻灯片看起来不一致，使用更强的参考强调重新生成

### 第4步：组合最终PPT

```bash
python /mnt/skills/public/ppt-generation/scripts/generate.py \
  --plan-file /mnt/user-data/workspace/nova-plan.json \
  --slide-images /mnt/user-data/outputs/nova-slide-01.jpg /mnt-user-data/outputs/nova-slide-02.jpg /mnt-user-data/outputs/nova-slide-03.jpg /mnt-user-data/outputs/nova-slide-04.jpg /mnt-user-data/outputs/nova-slide-05.jpg \
  --output-file /mnt/user-data/outputs/nova-presentation.pptx
```

## 风格特定指南

### Glassmorphism风格（推荐 - 最现代前卫）
```json
{
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "充满活力的渐变背景（紫色#667eea到粉红色#f093fb, 或青色#4facfe到蓝色#00f2fe），半透明的白色面板，20%不透明度，与渐变形成对比的强调色",
    "typography": "现代几何无衬线字体（Satoshi, General Sans, 或 Clash Display风格），可变字体权重，粗体标题（80pt+），舒适的正文（20pt）",
    "imagery": "抽象流体形状，渐变过渡，3D渲染的抽象对象，柔和的有机形状，悬浮的几何形状",
    "layout": "动态非对称构图，重叠元素带有混合模式，文本与渐变流融合，全屏背景",
    "effects": "平滑的渐变过渡，微妙的噪声纹理（3-5%以增加深度），与渐变匹配的软阴影，暗示运动的平滑模糊",
    "visual_language": "当代SaaS美学（Stripe, Linear, Vercel），充满活力但专业，前瞻性科技感觉"
  }
}
```

### Dark Premium Style
```json
{
  "style": "dark-premium",
  "style_guidelines": {
    "color_palette": "深黑色背景(#0a0a0a到#121212), 发光的强调色（电光蓝色#00d4ff, 霓虹品红色#bf5af2, 或金色#ffd700），可选：作为次要色的Memphis风格的粉彩色",
    "typography": "优雅的无衬线字体（Playfair Display, Freight, 或 Editorial New style）, 精致的字体设计（Söhne, Graphik），戏剧性的尺寸对比，粗体标题（96pt），正文（16pt），行高1.6",
    "imagery": "杂志级摄影，戏剧性裁剪，全屏图像，肖像，故意留有负空间，编辑室级光照（Vogue, Bloomberg Businessweek风格）",
    "layout": "精致的网格系统（12列），故意的非对称性，引文作为设计元素，文本围绕图像，优雅的边框和规则",
    "effects": "最小化效果 - 让摄影和字体设计发光，轻微的图像处理（轻微去饱和度，胶片颗粒），优雅的边框和规则",
    "visual_language": "高端杂志美学，知识领导力，通过设计限制提升内容"
  }
}
```

### Gradient Modern Style
```json
{
  "style": "gradient-modern",
  "style_guidelines": {
    "color_palette": "纯白色(#ffffff)或浅白色(#fafaf9)背景，纯黑色(#000000)文本，单一粗体强调色（瑞士红色#ff0000, Klein蓝色#002fa7, 或信号黄色#ffcc00）",
    "typography": "Helvetica Neue或Aktiv Grotesk, 严格的类型比例（12/16/24/48/96），中等权重正文，仅强调使用粗体",
    "imagery": "客观摄影，几何形状，干净的图标设计，数学精确性，负空间作为构图元素",
    "layout": "严格的网格遵循（基线网格在精神上可见），模块化构图，充足的空白空间（40-60%），内容对齐到不可见的网格线",
    "effects": "无 - 形式的纯粹性，没有阴影，没有渐变，没有装饰元素，偶尔使用单条发丝规则",
    "visual_language": "国际排版风格，形式服从功能，永恒的现代主义，Dieter Rams风格的简约"
  }
}
```

### Neo-Brutalist Style
```json
{
  "style": "neo-brutalist",
  "style_guidelines": {
    "color_palette": "高对比度：深黑色(#000000到#1d1d1f), 纯白色文本#ffffff, 签名蓝色(#0071e3)或渐变强调色（创意的紫色-粉红色, 技术的蓝色-青色）",
    "typography": "粗体等距字体（Impact, Druk, 或 Bebas Neue style）, 大写标题, 极端尺寸对比, 故意的'丑陋'美学, 反设计即设计, Memphis风格灵感",
    "imagery": "原始未过滤摄影, 故意视觉噪声, 半色调图案, 切割拼贴美学, 手绘元素, 贴纸和印章",
    "layout": "故意破坏网格, 重叠元素, 厚重的黑色边框（4-8px）, 可见结构, 反空白空间（密集但组织混乱）",
    "effects": "硬阴影（无模糊, 偏移8-12px）, 像素化强调, 扫描线, CRT屏幕效果, 故意的'错误'",
    "visual_language": "反企业叛逆, DIY杂志美学与数字结合, 原始真实性, 通过大胆性令人难忘"
  }
}
```

### 3D Isometric Style
```json
{
  "style": "3d-isometric",
  "style_guidelines": {
    "color_palette": "柔和的当代调色板：柔和的紫色(#8b5cf6), 蓝绿色(#14b8a6), 温暖珊瑚(#fb7185), 薄灰色背景(#fafafa)",
    "typography": "友好的几何无衬线字体（Circular, Gilroy, 或 Quicksand style）, 中等权重标题, 舒适的正文(18-24pt)",
    "imagery": "干净的等距立体插图, 一致的30°等距角度, 柔和的粘土渲染美学, 悬浮的平台和设备, 简化的抽象对象",
    "layout": "中央等距立体场景作为英雄, 文本围绕3D元素平衡, 清晰的视觉层次, 舒适的边距(64px+)",
    "effects": "20px模糊的阴影(30%不透明度)在3D对象上, 环境光遮蔽, 柔和阴影匹配渐变, 表面折射效果, 一致的灯光源（左上角）",
    "visual_language": "友好的科技插图（Slack, Notion, Asana风格）, 接近复杂性的清晰度, 通过简化实现清晰"
  }
}
```

### Editorial Style
```json
{
  "style": "editorial",
  "style_guidelines": {
    "color_palette": "精致的灰色调：米色(#f5f5f0), 黑色(#2d2d2d), 单一强调色（酒红色#7c2d12, 森林#14532d, 蓝色#1e3a5f）, 偶尔全色摄影",
    "typography": "精致的无衬线字体（Playfair Display, Freight, 或 Editorial New style）, 精致的字体设计（Söhne, Graphik）, 戏剧性的尺寸对比（96pt标题, 16pt正文）, 1.6行高",
    "imagery": "杂志级摄影, 戏剧性裁剪, 全屏图像, 肖像, 故意留有负空间, 编辑室级光照（Vogue, Bloomberg Businessweek风格）",
    "layout": "杂志级布局, 精致的字体层次结构, 戏剧性摄影, Vogue/Bloomberg Businessweek美学",
    "effects": "最小化效果 - 让摄影和字体设计发光, 轻微的图像处理（轻微去饱和度, 胶片颗粒）, 优雅的边框和规则",
    "visual_language": "高端杂志美学, 知识领导力, 通过设计限制提升内容"
  }
}
```

### Minimal Swiss Style
```json
{
  "style": "minimal-swiss",
  "style_guidelines": {
    "color_palette": "纯白色(#ffffff)或浅白色(#fafaf9)背景, 纯黑色(#000000)文本, 单一粗体强调色（瑞士红色#ff0000, Klein蓝色#002fa7, 或信号黄色#ffcc00）",
    "typography": "Helvetica Neue或Aktiv Grotesk, 基于网格的精确度, Helvetica风格的字体设计, 大胆使用负空间",
    "imagery": "客观摄影, 几何形状, 干净的图标设计, 数学精确性, 负空间作为构图元素",
    "layout": "严格的网格遵循（基线网格在精神上可见）, 模块化构图, 充足的空白空间（40-60%），内容对齐到不可见的网格线",
    "effects": "无 - 形式的纯粹性, 没有阴影, 没有渐变, 没有装饰元素, 偶尔使用单条发丝规则",
    "visual_language": "国际排版风格, 形式服从功能, 永恒的现代主义, Dieter Rams风格的简约"
  }
}
```

### Keynote Style (Apple风格)
```json
{
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "深黑色背景(#000000到#1d1d1f), 纯白色文本#ffffff, 签名蓝色(#0071e3)或渐变强调色（创意的紫色-粉红色, 技术的蓝色-青色）",
    "typography": "San Francisco Pro Display, 极端尺寸对比（粗体标题80pt+，正文轻体24pt）, 粗体标题使用负字母间距(-0.03em), 光学对齐",
    "imagery": "电影级摄影, 浅景深, 戏剧性光照（边缘光, 聚焦光）, 产品英雄照片, 反射, 全屏图像",
    "layout": "最大负空间, 单一强大图像或声明每张幻灯片, 内容居中或戏剧性偏移, 没有杂乱",
    "effects": "轻微渐变覆盖, 光线爆发和反射, 轻柔的彩色阴影匹配渐变, 光折射效果",
    "visual_language": "Apple WWDC主旨会美学, 通过简约创造自信, 每个像素都经过考虑, 戏剧性演示"
  }
}
```

## 输出处理

生成后：

- PPTX文件保存在`/mnt/user-data/outputs/`
- 使用`present_files`工具与用户共享生成的演示文稿
- 如果要求，也共享单个幻灯片图像
- 提供演示文稿的简要描述
- 如果需要，提供迭代或重新生成特定幻灯片的选项
