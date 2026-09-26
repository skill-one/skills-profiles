> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# GPT-Image

使用 OpenAI 的 GPT-Image-2.5 和 GPT-Image-2 通过 [inference.sh](https://inference.sh) CLI 生成和编辑图像。

## 模型

| 模型 | 应用 ID | 选择它用于 |
|-------|--------|-------------|
| **GPT-Image-2.5 Flare** | `openai/gpt-image-2-5-flare` | 默认。比 GPT-Image-2 质量更高，延迟降低 50% |
| **GPT-Image-2.5 Sunburst** | `openai/gpt-image-2-5-sunburst` | 高级编辑：保持主体和构图，跨多轮编辑的更精确控制 |
| GPT-Image-2 | `openai/gpt-image-2` | 前一代 |

这三个模型共享相同的输入模式。2.5 模型增加了 `xhigh` 和 `max` 质量等级。

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run openai/gpt-image-2-5-flare --input '{"prompt": "一只漂浮在太空中的宇航员猫"}'
```

## 功能

每个 GPT-Image 应用都支持文本到图像生成、使用参考图像的图像编辑以及基于蒙版的修复功能。

| 功能 | 描述 |
|---------|-------------|
| 文本到图像 | 从文本提示生成图像 |
| 图像编辑 | 使用参考图像编辑图像 |
| 修复 | 基于蒙版的特定区域编辑 |
| 批量生成 | 一次生成最多 10 张图像 |
| 多种格式 | PNG、JPEG、WebP 输出 |
| 透明背景 | Alpha 通道的 PNG/WebP 输出，用于贴纸、图标、产品切割 |
| 灵活分辨率 | 任何 16 像素增量的大小 (256–3840)，宽高比最高 3:1 |

## 示例

### 文本到图像

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "白色背景上的专业运动鞋产品照片，影棚灯光",
  "quality": "high"
}'
```

### 多张图像

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "咖啡店的最小化标志设计",
  "n": 4,
  "quality": "medium"
}'
```

### 使用参考图像编辑

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "将背景改为日落海滩",
  "images": ["https://your-image.jpg"]
}'
```

### 使用 Sunburst 进行精确编辑

Sunburst 的设计是为了只改变你要求的部分，并保留其余部分。

```bash
belt app run openai/gpt-image-2-5-sunburst --input '{
  "prompt": "将夹克改为红色皮革，保持人物、姿势和背景不变",
  "images": ["https://your-photo.jpg"],
  "quality": "high"
}'
```

### 最大细节

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "蜻蜓翅膀的微距照片，复杂的脉络，清晨的露珠",
  "quality": "max"
}'
```

### 多张参考图像

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "将这两个角色结合成一个场景",
  "images": ["https://character1.jpg", "https://character2.jpg"]
}'
```

### 基于蒙版的修复

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "替换为红色跑车",
  "images": ["https://street-scene.jpg"],
  "mask": "https://car-mask.png"
}'
```

### 透明背景

提示一个孤立的主题——描述场景或背景会使模型绘制一个。需要 `png`（默认）或 `webp` 输出。

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "一个带有绿色叶子的红色苹果，孤立主题",
  "background": "transparent"
}'
```

### 自定义分辨率

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "宽电影感风景，黄金时刻的山脉",
  "width": 1920,
  "height": 1080,
  "quality": "high"
}'
```

### 快速草图

```bash
belt app run openai/gpt-image-2-5-flare --input '{
  "prompt": "机器人的快速概念草图",
  "quality": "low"
}'
```

## 定价

每 1024x1024 图像的大致价格。Flare 和 Sunburst 的价格相同。

| 质量 | GPT-Image-2.5 | GPT-Image-2 |
|---------|---------------|-------------|
| 低 | $0.006 | $0.006 |
| 中 | $0.013 | $0.053 |
| 高 | $0.053 | $0.21 |
| xhigh | $0.094 | – |
| max | $0.21 | – |

更大分辨率的价格更高。编辑大约增加每张参考图像 0.008 美元。有关完整定价详情，请查看 `belt app get openai/gpt-image-2-5-flare`。

## 参数

| 参数 | 类型 | 默认 | 描述 |
|-----------|------|---------|-------------|
| `prompt` | string | required | 描述图像的文本提示 |
| `images` | array | - | 用于编辑的参考图像 |
| `mask` | string | - | 用于修复的蒙版图像 |
| `n` | integer | 1 | 图像数量 (1–10) |
| `quality` | string | auto | low, medium, high, xhigh, max (xhigh/max 仅限 2.5) |
| `width` | integer | 1024 | 输出宽度 (256–3840，16 的倍数，比例 ≤ 3:1) |
| `height` | integer | 1024 | 输出高度 (256–3840，16 的倍数，比例 ≤ 3:1) |
| `output_format` | string | png | png、jpeg 或 webp |
| `output_compression` | integer | - | jpeg/webp 的压缩级别 (0–100) |
| `background` | string | auto | auto、transparent 或 opaque (transparent 需要 png/webp) |

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 所有图像生成模型
npx skills add inference-sh/skills@ai-image-generation

# FLUX 模型
npx skills add inference-sh/skills@flux-image

# Pruna P-Image（快速且经济）
npx skills add inference-sh/skills@p-image
```

浏览所有图像应用：`belt app list --category image`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的说明
- [实时进度更新](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
