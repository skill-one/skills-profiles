---
name: ppt-generation
description: 当用户请求生成、创建或制作演示文稿（PPT/PPTX）时，使用此技能。通过为每张幻灯片生成图像并将它们组合成一个PowerPoint文件，创建视觉丰富的幻灯片。
---

# PPT生成技能

## 概述

该技能通过为每张幻灯片创建AI生成的图像，并将它们组合成一个PPTX文件来生成专业的PowerPoint演示文稿。工作流程包括规划演示文稿结构并保持一致的视觉风格，按顺序生成幻灯片图像（使用前一张幻灯片作为风格一致性的参考），并将它们组装成最终的演示文稿。

## 核心功能

- 规划和构建具有统一视觉风格的多张幻灯片演示文稿
- 支持多种演示文稿风格：商业、学术、极简、苹果Keynote、创意
- 使用图像生成技能为每张幻灯片生成独特的AI图像
- 通过使用前一张幻灯片作为参考图像来保持视觉一致性
- 将图像组合成专业的PPTX文件

## 演示文稿风格

创建演示文稿计划时，请从以下风格中选择一种：

| 风格 | 描述 | 适合场景 |
|------|------|----------|
| **glassmorphism** | 水晶玻璃面板带有模糊效果，悬浮的半透明卡片，充满活力的渐变背景，通过层叠产生深度 | 科技产品，AI/SaaS演示，未来主义提案 |
| **dark-premium** | 丰富的黑色背景(#0a0a0a)，明亮的强调色，微妙的发光效果，奢华品牌美学 | 奢侈品，高管演示，高端品牌 |
| **gradient-modern** | 大胆的网格渐变，流畅的色彩过渡，现代字体排版，充满活力且精致 | 初创公司，创意机构，品牌发布 |
| **neo-brutalist** | 原始粗犷的字体排版，高对比度，故意的“丑陋”美学，反设计即设计，Memphis风格灵感 | 边缘品牌，Z世代目标，颠覆性初创公司 |
| **3d-isometric** | 干净的等距立体插图，悬浮的3D元素，柔和阴影，科技前沿美学 | 科技解释，产品特性，SaaS演示 |
| **editorial** | 杂志级布局，精致的字体层级，戏剧性摄影，Vogue/Bloomberg美学 | 年度报告，奢侈品，思想领导力 |
| **minimal-swiss** | 基于网格的精确度，基于Helvetica的字体排版，大胆使用负空间，永恒的现代主义 | 建筑，设计公司，高端咨询 |
| **keynote** | 苹果风格的审美，大胆的字体排版，戏剧性图像，高对比度，电影感 | 主讲会，产品发布，鼓舞人心的演讲 |

## 工作流程

### 第1步：理解需求

当用户请求演示文稿生成时，请识别：

- 主题/科目：演示文稿是关于什么的
- 幻灯片数量：需要多少张幻灯片（默认：5-10）
- **风格**：商业 / 学术 / 极简 / Keynote / 创意
- 宽高比：标准(16:9)或经典(4:3)
- 内容大纲：每张幻灯片的关键点
- 无需检查`/mnt/user-data`下的文件夹

### 第2步：创建演示文稿计划

在`/mnt/user-data/workspace/`中创建一个包含演示文稿结构的JSON文件。**重要**：包括`style`字段来定义整体视觉一致性。

```json
{
  "title": "演示文稿标题",
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "深黑色背景，白色文本，单一强调色（蓝色或橙色）",
    "typography": "粗体无衬线标题，干净的正文文本，戏剧性的尺寸对比",
    "imagery": "高质量摄影，全出血图像，电影感构图",
    "layout": "充足的空白，居中焦点，每张幻灯片上的元素最少"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "主标题",
      "subtitle": "副标题或标语",
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

**重要**：严格按顺序**逐个**生成幻灯片。**不要**并行或批量生成图像。每张幻灯片都依赖于前一张幻灯片的输出作为参考图像。并行生成幻灯片将破坏视觉一致性，并且是不允许的。

1. 读取图像生成技能：`/mnt/skills/public/image-generation/SKILL.md`

2. **对于第一张幻灯片（幻灯片1）**，创建一个建立视觉风格的提示：

```json
{
  "prompt": "专业演示文稿幻灯片。[style_guidelines from plan]。标题：'您的标题'。[visual_description]。这张幻灯片为整个演示文稿建立视觉语言。",
  "style": "[基于所选风格 - 例如，苹果Keynote美学，戏剧性光照，电影感]",
  "composition": "干净的布局，清晰的文本层级，[风格特定的构图]",
  "color_palette": "[From style_guidelines]",
  "typography": "[From style_guidelines]"
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
  "prompt": "专业演示文稿幻灯片，延续参考图像的视觉风格。保持相同的调色板、字体风格和整体美学。标题：'幻灯片标题'。[visual_description]。保持视觉一致性。",
  "style": "完全匹配参考图像的风格",
  "composition": "与参考相似的布局原则，根据内容进行调整",
  "color_palette": "与参考图像相同",
  "consistency_note": "这张幻灯片必须看起来像是属于同一演示文稿的一部分"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/slide-02-prompt.json \
  --reference-images /mnt-user-data/outputs/slide-01.jpg \
  --output-file /mnt-user-data/outputs/slide-02.jpg \
  --aspect-ratio 16:9
```

4. **继续为所有剩余幻灯片**，始终参考前一张幻灯片：

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
  --slide-images /mnt/user-data/outputs/slide-01.jpg /mnt-user-data/outputs/slide-02.jpg /mnt-user-data/outputs/slide-03.jpg \
  --output-file /mnt/user-data/outputs/presentation.pptx
```

参数：

- `--plan-file`：演示文稿计划JSON文件的绝对路径（必需）
- `--slide-images`：按顺序幻灯片图像的绝对路径（必需，空格分隔）
- `--output-file`：输出PPTX文件的绝对路径（必需）

[!NOTE]
**不要**读取python文件，只需使用参数调用它。

## 完整示例：玻璃风格（最现代前卫）

用户请求："创建一个关于AI产品发布的演示文稿"

### 第1步：创建演示文稿计划

创建`/mnt/user-data/workspace/ai-product-plan.json`：
```json
{
  "title": "Introducing Nova AI",
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "紫色到青色的充满活力的渐变背景(#667eea→#00d4ff)，15-20%不透明的水晶玻璃面板，电光色强调",
    "typography": "SF Pro Display风格，粗体700权重白色标题带有微妙的文本阴影，干净的400权重正文文本，玻璃上对比度极好",
    "imagery": "抽象的3D水晶球，悬浮的半透明几何形状，柔和发光的球体，通过层叠透明度产生深度",
    "layout": "居中的水晶玻璃卡片带有32px圆角，48-64px内边距，悬浮在渐变之上，通过软阴影产生分层深度",
    "effects": "水晶玻璃面板上的背景模糊20-40px，微妙的白色边框发光，与渐变匹配的软彩色阴影，光折射效果",
    "visual_language": "Apple Vision Pro / visionOS美学，通过透明度产生奢华感，未来主义且易于接近，2024设计趋势"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "Introducing Nova AI",
      "subtitle": "Intelligence, Reimagined",
      "visual_description": "令人惊叹的渐变背景从深紫色(#667eea)流畅地流经品红色到青色(#00d4ff)，柔和且充满活力。中心：大型水晶玻璃面板带有强烈的背景模糊效果，包含粗体白色标题'Introducing Nova AI'（72pt，SF Pro Display风格，字体权重700）和下方的较浅重量副标题。水晶玻璃面板有微妙的白色边框（1px rgba 255,255,255,0.3）和紫色色调的阴影。悬浮在卡片周围的：3D水晶球带有折射效果，半透明几何形状（二十面体、环面）增加深度。从玻璃面板后面发出的柔和发光。小光点悬浮。苹果Vision Pro / visionOS UI美学。专业演示文稿幻灯片，16:9宽高比。超现代，高端科技产品发布感。"
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "Why Nova?",
      "key_points": ["10x更快处理", "类人理解", "企业级安全"],
      "visual_description": "与之前相同的紫色-青色渐变背景。左侧：悬浮的水晶玻璃卡片带有标题'Why Nova?'（粗体白色），下方有三个要点，带有微妙的玻璃药丸徽章。右侧：抽象3D神经网络可视化，由相互连接的水晶节点组成，带有柔和的青色发光。悬浮的半透明几何形状（二十面体、环面）增加深度。与参考幻灯片一致的玻璃morphism美学。"
    },
    {
      "slide_number": 3,
      "type": "content",
      "title": "How It Works",
      "key_points": ["自然语言输入", "多模态处理", "即时洞察"],
      "visual_description": "与之前幻灯片一致的渐变背景。中心构图：三个堆叠的水晶玻璃卡片，略微倾斜，显示工作流程步骤，由柔和发光的线连接。每个卡片都有一个抽象图标。周围悬浮着水晶球和光粒子。标题'How It Works'在顶部以粗体白色显示。通过卡片层叠和透明度创造深度。"
    },
    {
      "slide_number": 4,
      "type": "content",
      "title": "Built for Scale",
      "key_points": ["100万+并发用户", "99.99%正常运行时间", "全球基础设施"],
      "visual_description": "与之前相同的渐变背景。非对称布局：右侧是一个带有显示粗体字体的水晶玻璃面板，显示指标。左侧：由水晶面板和连接线组成的抽象3D地球，代表全球规模。左侧：作为小水晶卡片显示数字的数据可视化元素。整个环境中都有柔和的环境光。高端科技美学。"
    },
    {
      "slide_number": 5,
      "type": "conclusion",
      "title": "The Future Starts Now",
      "subtitle": "Join the waitlist",
      "visual_description": "戏剧性的结尾幻灯片。渐变背景的活力略有增加。中心：带有粗体标题'The Future Starts Now'和行动号召副标题的水晶玻璃卡片。在卡片后面：爆发柔和的光线束和悬浮的水晶粒子创造庆祝效果。多层玻璃形状创造深度。在保持风格一致性的同时，这是最具视觉冲击力的幻灯片。"
    }
  ]
}
```

### 第2步：读取图像生成技能

读取`/mnt/skills/public/image-generation/SKILL.md`以了解如何生成图像。

### 第3步：按顺序生成幻灯片图像并使用参考链

**幻灯片1 - 标题（建立视觉语言）：**

创建`/mnt/user-data/workspace/nova-slide-01.json`：
```json
{
  "prompt": "超高端演示文稿标题幻灯片，具有玻璃morphism设计。背景：从深紫色(#667eea)到品红色(#f093fb)再到青色(#00d4ff)的平滑流动渐变，柔和且充满活力。中心：大型水晶玻璃面板带有强烈的背景模糊效果，圆角32px，包含粗体白色无衬线标题'Introducing Nova AI'（72pt，SF Pro Display风格，字体权重700）和下方的较浅重量副标题。水晶玻璃面板有微妙的白色边框（1px rgba 255,255,255,0.25）和紫色色调的阴影。悬浮在卡片周围的：3D水晶球带有折射效果，半透明几何形状（二十面体、抽象形状），创造深度和维度。从玻璃面板后面发出的柔和发光。小光点悬浮。苹果Vision Pro / visionOS UI美学。专业演示文稿幻灯片，16:9宽高比。超现代，高端科技产品发布感。",
  "style": "Glassmorphism, visionOS美学，苹果Vision Pro UI风格，高端科技，2024设计趋势",
  "composition": "以居中的玻璃卡片为焦点，边缘处悬浮的3D元素创造深度，40%负空间，清晰的视觉层级",
  "lighting": "来自渐变的柔和环境光，通过玻璃元素的光折射，3D形状的微妙轮廓光",
  "color_palette": "紫色渐变#667eea，品红色#f093fb，青色#00d4ff，水晶白色rgba(255,255,255,0.15)，纯白色文本#ffffff",
  "effects": "玻璃面板上的背景模糊，软阴影带有颜色色调，光折射，玻璃上的微妙噪点纹理，悬浮粒子"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/nova-slide-01.json \
  --output-file /mnt-user-data/outputs/nova-slide-01.jpg \
  --aspect-ratio 16:9
```

**幻灯片2 - 内容（必须参考幻灯片1以保持一致性）：**

创建`/mnt-user-data/workspace/nova-slide-02.json`：
```json
{
  "prompt": "演示文稿幻灯片，延续完全的视觉风格。相同的紫色到青色渐变背景，相同的玻璃morphism美学，相同的字体风格。左侧：带有背景模糊的水晶玻璃卡片，包含标题'Why Nova?'（与参考相同的字体风格）和下方的三个要点（带有微妙的玻璃药丸徽章）。右侧：由相互连接的水晶节点组成的抽象3D神经网络可视化，带有柔和的青色发光，悬浮在空间中。悬浮的半透明几何形状（与参考风格匹配）增加深度。水晶玻璃具有相同的处理：白色边框，紫色色调的阴影，相同的模糊强度。关键：这张幻灯片必须看起来像是属于同一演示文稿的一部分 - 相同的颜色，相同的玻璃处理，相同的美学。",
  "style": "MATCH REFERENCE EXACTLY - Glassmorphism, visionOS美学，相同的视觉语言",
  "composition": "非对称分割：玻璃卡片左侧（40%），3D可视化右侧（40%），元素之间留有呼吸空间",
  "color_palette": "完全匹配参考：紫色#667eea，青色#00d4ff渐变，相同的模糊白色处理，相同的文本白色",
  "consistency_note": "关键：必须与参考图像在风格上完全一致。相同的渐变颜色，相同的玻璃模糊强度，相同的阴影处理，相同的字体权重和风格。观众应立即认出这是同一演示文稿的一部分。"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt-user-data/workspace/nova-slide-02.json \
  --reference-images /mnt-user-data/outputs/nova-slide-01.jpg \
  --output-file /mnt-user-data/outputs/nova-slide-02.jpg \
  --aspect-ratio 16:9
```

**幻灯片3-5：继续相同的模式，每张都参考前一张幻灯片**

后续幻灯片的关键一致性规则：
- 在提示中始终包含“延续参考图像的精确视觉风格”
- 指定“相同的渐变背景”、“相同的玻璃效果”、“相同的字体”
- 包含 `consistency_note` 强调风格匹配
- 参考紧邻的前一幻灯片图像

### 第 4 步：组成最终 PPT

```bash
python /mnt/skills/public/ppt-generation/scripts/generate.py \
  --plan-file /mnt/user-data/workspace/nova-plan.json \
  --slide-images /mnt/user-data/outputs/nova-slide-01.jpg /mnt/user-data/outputs/nova-slide-02.jpg /mnt/user-data/outputs/nova-slide-03.jpg /mnt/user-data/outputs/nova-slide-04.jpg /mnt/user-data/outputs/nova-slide-05.jpg \
  --output-file /mnt/user-data/outputs/nova-presentation.pptx
```

## 风格特定指南

### 玻璃态风格（推荐 - 最现代前卫）
```json
{
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "鲜艳的渐变背景（紫色 #667eea 到 粉色 #f093fb，或 青色 #4facfe 到 蓝色 #00f2fe），磨砂白面板 20% 透明度，与渐变形成对比的强调色",
    "typography": "SF Pro Display 或 Inter 字体风格，粗体 600-700 级别的标题，干净 400 级别的正文，白色文本带有微妙的阴影，在玻璃上提高可读性",
    "imagery": "漂浮在太空中的抽象 3D 形状，柔和模糊的球体，具有玻璃材质的几何基本元素，通过重叠的半透明层产生深度",
    "layout": "带有 backdrop-blur 效果的浮动卡片面板，充足的填充（48-64px），圆角（24-32px 半径），具有微妙阴影的分层深度",
    "effects": "磨砂玻璃模糊（backdrop-filter: blur 20px），微妙的白色边框（1px rgba 255,255,255,0.2），面板背后的柔和光晕，带有阴影的浮动元素",
    "visual_language": "像 Apple Vision Pro UI 的优质科技美学，通过透明度产生深度，光线折射通过玻璃表面"
  }
}
```

### 暗黑高级风格
```json
{
  "style": "dark-premium",
  "style_guidelines": {
    "color_palette": "深黑色基础（#0a0a0a 到 #121212），发光的强调色（电蓝色 #00d4ff，霓虹紫色 #bf5af2，或金色 #ffd700），用于深度的微妙灰色渐变（#1a1a1a 到 #0a0a0a）",
    "typography": "优雅的无衬线字体（Neue Haas Grotesk 或 Suisse Int'l 风格），戏剧性的尺寸对比（标题 72pt+，正文 18pt），标题的字母间距 -0.02em，纯白色（#ffffff）文本",
    "imagery": "戏剧性的工作室照明，边缘光和边缘光晕，电影感的产品拍摄，抽象的光线轨迹，优质材料纹理（拉丝金属，磨砂表面）",
    "layout": "充足的负空间（60%+），非对称平衡，内容锚定到网格但留有呼吸空间，每张幻灯片一个焦点",
    "effects": "关键元素背后的微妙环境光晕，光线泛起效果，颗粒纹理覆盖层（2-3% 透明度），边缘暗角",
    "visual_language": "奢华科技品牌美学（Bang & Olufsen，Porsche Design），通过克制展现精致，每个元素都经过精心设计"
  }
}
```

### 渐变现代风格
```json
{
  "style": "gradient-modern",
  "style_guidelines": {
    "color_palette": "大胆的网格渐变（Stripe/线性风格：紫色 #7c3aed→粉色 #ec4899→橙色 #f97316，或冷色调：青色 #06b6d4→蓝色 #3b82f6→紫色 #8b5cf6），背景强度决定白色或深色文本",
    "typography": "现代几何无衬线字体（Satoshi，General Sans，或 Clash Display 风格），可变字体粗细，超大粗体标题（80pt+），舒适的正文（20pt）",
    "imagery": "抽象流体形状，变形渐变，3D 渲染的抽象对象，柔和有机形状，漂浮的几何基本元素",
    "layout": "动态非对称构图，带有混合模式的重叠元素，文本与渐变流动集成，全出血背景",
    "effects": "平滑的渐变过渡，微妙的噪声纹理（3-5% 用于深度），与渐变匹配颜色的柔和阴影，运动模糊暗示运动",
    "visual_language": "当代 SaaS 美学（Stripe，Linear，Vercel），充满活力且专业，前瞻性科技氛围"
  }
}
```

### 新野兽派风格
```json
{
  "style": "neo-brutalist",
  "style_guidelines": {
    "color_palette": "高对比度主色：鲜明的黑色，纯白色，以及大胆的强调色（亮粉色 #ff0080，亮黄色 #ffff00，或原始红色 #ff0000），可选：Memphis 风格的粉彩色作为次要色",
    "typography": "超粗体压缩字体（Impact，Druk，或 Bebas Neue 风格），大写标题，极端尺寸对比，故意紧密或重叠的字母间距",
    "imagery": "未经过滤的原始摄影，故意的视觉噪声，点阵图案，剪贴画美学，手绘元素，贴纸和印章",
    "layout": "破损的网格，重叠的元素，粗黑边框（4-8px），可见的结构，反空白（密集但有组织的混乱）",
    "effects": "硬阴影（无模糊，偏移 8-12px），像素化强调，扫描线，CRT 屏幕效果，故意的'错误'",
    "visual_language": "反企业叛逆，DIY 传单美学与数字结合，原始真实性，通过大胆性令人难忘"
  }
}
```

### 3D 等距风格
```json
{
  "style": "3d-isometric",
  "style_guidelines": {
    "color_palette": "柔和的当代调色板：柔和的紫色（#8b5cf6），蓝绿色（#14b8a6），暖珊瑚（#fb7185），奶油色或浅灰色背景（#fafafa），元素间一致的饱和度",
    "typography": "友好的几何无衬线字体（Circular，Gilroy，或 Quicksand 风格），中等粗细标题，优秀的可读性，舒适的 24pt 正文",
    "imagery": "干净的等距 3D 插图，一致的 30° 等距角度，柔和的粘土渲染美学，漂浮的平台和设备，简化的可爱对象",
    "layout": "中央等距场景作为主角，文本围绕 3D 元素平衡，清晰的视觉层次，舒适的边距（64px+）",
    "effects": "柔和的阴影（20px 模糊，30% 透明度），3D 对象的接触阴影，表面上的微妙渐变，一致的光源（左上）",
    "visual_language": "友好的科技插图（Slack，Notion，Asana 风格），可接近的复杂性，通过简化实现清晰"
  }
}
```

### 编辑风格
```json
{
  "style": "editorial",
  "style_guidelines": {
    "color_palette": "精致的中性色：浅白（#f5f5f0），煤灰（#2d2d2d），单一强调色（酒红色 #7c2d12，森林绿 #14532d，或海军蓝 #1e3a5f），偶尔的全彩色摄影",
    "typography": "用于标题的精致衬线字体（Playfair Display，Freight，或 Editorial New 风格），干净的无衬线字体用于正文（Söhne，Graphik），戏剧性的尺寸层次（标题 96pt，正文 16pt），充足的行高 1.6",
    "imagery": "杂志级摄影，戏剧性的裁剪，全出血图像，带有故意负空间的肖像，编辑照明（Vogue，Bloomberg Businessweek 风格）",
    "layout": "精致的网格系统（12 列），故意的非对称性，作为设计元素的拉引引用，文本围绕图像，优雅的边距",
    "effects": "最小化效果 - 让摄影和排版发光，微妙的图像处理（轻微去饱和度，胶片颗粒），优雅的边框和规则",
    "visual_language": "高端杂志美学，知识分子的精致，通过设计克制提升内容"
  }
}
```

### 极简瑞士风格
```json
{
  "style": "minimal-swiss",
  "style_guidelines": {
    "color_palette": "纯白色（#ffffff）或浅白（#fafaf9）背景，纯黑色（#000000）文本，单一粗体强调色（瑞士红 #ff0000，Klein 蓝色 #002fa7，或信号黄色 #ffcc00）",
    "typography": "Helvetica Neue 或 Aktiv Grotesk，严格的类型比例（12/16/24/48/96），中等粗细正文，仅强调使用粗体，左对齐锯齿形右对齐排列",
    "imagery": "客观摄影，几何形状，干净的图标，数学精度，故意空白作为构图元素",
    "layout": "严格遵循网格（基线网格在精神上可见），模块化构图，充足的空白（40%+ 滑片），内容对齐到看不见的网格线",
    "effects": "无 - 形式的纯粹，无阴影，无渐变，无装饰元素，偶尔的单发丝规则",
    "visual_language": "国际排版风格，形式追随功能，永恒的现代主义，Dieter Rams 风格的克制"
  }
```

### 演讲风格（Apple 风格）
```json
{
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "深黑色（#000000 到 #1d1d1f），纯白色文本，标志性的蓝色（#0071e3）或渐变强调色（创意用紫色-粉色 #7c3aed→#f093fb，科技用蓝色-蓝绿色 #3b82f6→#00f2fe）",
    "typography": "San Francisco Pro Display，极端粗细对比（粗体 80pt+ 标题，浅色 24pt 正文），标题负字母间距 -0.03em，光学对齐",
    "imagery": "电影感摄影，浅景深，戏剧性照明（边缘光，聚光灯），产品英雄拍摄带有反射，全出血图像",
    "layout": "最大负空间，每张幻灯片一个强大的图像或声明，内容居中或戏剧性偏移，无杂乱",
    "effects": "微妙的渐变覆盖层，关键元素上的光线泛起和光晕，表面上的反射，平滑的渐变背景",
    "visual_language": "Apple WWDC 演讲美学，通过简洁展现自信，每个像素都经过考虑，戏剧性演示"
  }
}
```

## 输出处理

生成后：

- PPTX 文件保存在 `/mnt/user-data/outputs/`
- 使用 `present_files` 工具与用户共享生成的演示文稿
- 如有要求，也共享单个幻灯片图像
- 提供演示文稿的简要描述
- 如有需要，提供迭代或重新生成特定幻灯片的选项

## 备注

### 关键质量指南

**专业结果的提示工程：**
- 无论用户语言如何，始终使用英语进行图像提示
- 极其具体地描述视觉细节 - 模糊的提示会产生通用结果
- 包含确切的十六进制颜色代码（例如，#667eea 而不是"紫色"）
- 指定字体细节：字体粗细（400/700），尺寸层次，字母间距
- 精确描述效果："backdrop blur 20px"，"drop shadow 8px blur 30% opacity"
- 参考真实设计系统："visionOS 美学"，"Stripe 网站风格"，"Bloomberg Businessweek 布局"

**视觉一致性（最重要）：**
- **按顺序生成幻灯片** - 每张幻灯片必须参考前一张
- 第一张幻灯片至关重要 - 它为整个演示文稿建立了视觉语言
- 在每个后续幻灯片提示中，明确说明："延续参考图像的精确视觉风格"
- 在提示中强烈使用 SAME、EXACT、MATCH 关键词以强制一致性
- 在每个 JSON 提示中包含 `consistency_note` 字段（第 1 张幻灯片之后）
- 如果一张幻灯片看起来不一致，使用更强的参考强调重新生成它

**现代美学的设计原则：**
- 享受负空间 - 40-60% 空白创造高级感
- 每张幻灯片元素有限 - 一个焦点，一个信息
- 通过层叠（阴影、透明度、z-depth）产生深度
- 字体层次：巨大的标题（72pt+），舒适的正文（18-24pt）
- 颜色克制：一个主要调色板，最多 1-2 个强调色

**常见错误避免：**
- ❌ 通用提示如"专业幻灯片" - 要具体
- ❌ 每张幻灯片元素/文本过多 - 杂乱 = 不专业
- ❌ 幻灯片之间颜色不一致 - 始终参考前一张幻灯片
- ❌ 忽略参考图像参数 - 这会破坏视觉一致性
- ❌ 在一个演示文稿中使用不同的设计风格
- ❌ 并行生成幻灯片 - 幻灯片必须按顺序生成（幻灯片 1 → 2 → 3 ...），绝不能同时进行

**不同上下文推荐的风格：**
- 科技产品发布 → `glassmorphism` 或 `gradient-modern`
- 奢华/高级品牌 → `dark-premium` 或 `editorial`
- 创业公司提案 → `gradient-modern` 或 `minimal-swiss`
- 高管演示 → `dark-premium` 或 `keynote`
- 创意代理 → `neo-brutalist` 或 `gradient-modern`
- 数据/分析 → `minimal-swiss` 或 `3d-isometric`
