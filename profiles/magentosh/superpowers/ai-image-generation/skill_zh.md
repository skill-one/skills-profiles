> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 图像生成

通过 [inference.sh](https://inference.sh) CLI 生成 50+ 种 AI 模型的图像。

![AI 图像生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0v0nz7wv0qwqjtq1cam52z.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 使用 FLUX 生成图像
belt app run falai/flux-dev-lora --input '{"prompt": "space cat astronaut"}'
```

## 可用模型

| 模型 | 应用 ID | 适合场景 |
|-------|--------|----------|
| **GPT-Image-2** | `openai/gpt-image-2` | 文本到图像、编辑、修复 |
| FLUX Dev LoRA | `falai/flux-dev-lora` | 高质量并支持自定义风格 |
| FLUX.2 Klein LoRA | `falai/flux-2-klein-lora` | 支持LoRA快速生成 (4B/9B) |
| **P-Image** | `pruna/p-image` | 快速、经济、多角度 |
| **P-Image-LoRA** | `pruna/p-image-lora` | 支持预设LoRA风格的快速生成 |
| **P-Image-Edit** | `pruna/p-image-edit` | 快速图像编辑 |
| Gemini 3 Pro | `google/gemini-3-pro-image-preview` | Google 最新模型 |
| Gemini 2.5 Flash | `google/gemini-2-5-flash-image` | 快速 Google 模型 |
| Grok Imagine | `xai/grok-imagine-image` | xAI 模型，多角度 |
| Seedream 4.5 | `bytedance/seedream-4-5` | 2K-4K 电影级质量 |
| Seedream 4.0 | `bytedance/seedream-4-0` | 高质量 2K-4K |
| Seedream 3.0 | `bytedance/seedream-3-0-t2i` | 精确文本渲染 |
| Reve | `falai/reve` | 自然语言编辑、文本渲染 |
| ImagineArt 1.5 Pro | `falai/imagine-art-1-5-pro-preview` | 超高保真度 4K |
| FLUX Klein 4B | `pruna/flux-klein-4b` | 超低价格 ($0.0001/图像) |
| Topaz Upscaler | `falai/topaz-image-upscaler` | 专业图像放大 |

## 浏览所有图像应用

```bash
belt app list --category image
```

## 示例

### GPT-Image-2

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "专业运动鞋产品照片，影棚灯光",
  "quality": "high"
}'
```

### GPT-Image-2 编辑

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "将背景改为日落海滩",
  "images": ["https://your-image.jpg"]
}'
```

### FLUX 文本到图像

```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "专业咖啡杯产品照片，影棚灯光"
}'
```

### FLUX Klein 快速生成

```bash
belt app run falai/flux-2-klein-lora --input '{"prompt": "山脉日落"}'
```

### Google Gemini 3 Pro

```bash
belt app run google/gemini-3-pro-image-preview --input '{
  "prompt": "山脉湖泊的写实风景"
}'
```

### Grok Imagine

```bash
belt app run xai/grok-imagine-image --input '{
  "prompt": "夜晚的赛博朋克城市",
  "aspect_ratio": "16:9"
}'
```

### Reve (带文本渲染)

```bash
belt app run falai/reve --input '{
  "prompt": "一张写着 HELLO WORLD 的海报，加粗字体"
}'
```

### Seedream 4.5 (4K 质量)

```bash
belt app run bytedance/seedream-4-5 --input '{
  "prompt": "女性电影肖像，黄金时刻灯光"
}'
```

### 图像放大

```bash
belt app run falai/topaz-image-upscaler --input '{"image_url": "https://..."}'
```

### 多图像拼接

```bash
belt app run infsh/stitch-images --input '{
  "images": ["https://img1.jpg", "https://img2.jpg"],
  "direction": "horizontal"
}'
```

## 相关技能

```bash
# 完整平台技能 (所有应用)
npx skills add inference-sh/skills@infsh-cli

# Pruna P-Image (快速且经济)
npx skills add inference-sh/skills@p-image

# GPT-Image-2 (OpenAI)
npx skills add inference-sh/skills@gpt-image

# FLUX 专用技能
npx skills add inference-sh/skills@flux-image

# 放大与增强
npx skills add inference-sh/skills@image-upscaling

# 背景移除
npx skills add inference-sh/skills@background-removal

# 视频生成
npx skills add inference-sh/skills@ai-video-generation

# 从图像生成 AI 头像
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的方法
- [图像生成示例](https://inference.sh/docs/examples/image-generation) - 完整图像生成指南
- [应用概览](https://inference.sh/docs/apps/overview) - 理解应用生态系统
