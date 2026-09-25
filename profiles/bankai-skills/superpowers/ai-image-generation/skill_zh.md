**安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 图像生成

通过 [inference.sh](https://inference.sh) CLI，使用 50 多种 AI 模型生成图像。

![AI 图像生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0v0nz7wv0qwqjtq1cam52z.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# Generate an image with FLUX
belt app run falai/flux-dev-lora --input '{"prompt": "a cat astronaut in space"}'
```

## 可用模型

| Model | App ID | Best For |
|-------|--------|----------|
| **GPT-Image-2** | `openai/gpt-image-2` | 文生图、编辑、补绘 |
| FLUX Dev LoRA | `falai/flux-dev-lora` | 高质量，支持自定义风格 |
| FLUX.2 Klein LoRA | `falai/flux-2-klein-lora` | 快速，支持 LoRA（4B/9B） |
| **P-Image** | `pruna/p-image` | 快速、经济、多场景 |
| **P-Image-LoRA** | `pruna/p-image-lora` | 快速，支持预设 LoRA 风格 |
| **P-Image-Edit** | `pruna/p-image-edit` | 快速图像编辑 |
| Gemini 3 Pro | `google/gemini-3-pro-image-preview` | Google 最新版本 |
| Gemini 2.5 Flash | `google/gemini-2-5-flash-image` | 快速 Google 模型 |
| Grok Imagine | `xai/grok-imagine-image` | xAI 的模型，多场景 |
| Seedream 4.5 | `bytedance/seedream-4-5` | 2K-4K 电影级画质 |
| Seedream 4.0 | `bytedance/seedream-4-0` | 高质量 2K-4K |
| Seedream 3.0 | `bytedance/seedream-3-0-t2i` | 精准文本渲染 |
| Reve | `falai/reve` | 自然语言编辑，文本渲染 |
| ImagineArt 1.5 Pro | `falai/imaginate-art-1-5-pro-preview` | 超高保真 4K |
| FLUX Klein 4B | `pruna/flux-klein-4b` | 极便宜（每张 $0.0001） |
| Topaz Upscaler | `falai/topaz-image-upscaler` | 专业放大 |

## 浏览所有图像应用

```bash
belt app list --category image
```

## 示例

### GPT-Image-2

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "professional product photo of sneakers, studio lighting",
  "quality": "high"
}'
```

### GPT-Image-2 编辑

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "change the background to a beach at sunset",
  "images": ["https://your-image.jpg"]
}'
```

### FLUX 文生图

```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "professional product photo of a coffee mug, studio lighting"
}'
```

### FLUX Klein 快速生成

```bash
belt app run falai/flux-2-klein-lora --input '{"prompt": "sunset over mountains"}'
```

### Google Gemini 3 Pro

```bash
belt app run google/gemini-3-pro-image-preview --input '{
  "prompt": "photorealistic landscape with mountains and lake"
}'
```

### Grok Imagine

```bash
belt app run xai/grok-imagine-image --input '{
  "prompt": "cyberpunk city at night",
  "aspect_ratio": "16:9"
}'
```

### Reve（支持文本渲染）

```bash
belt app run falai/reve --input '{
  "prompt": "A poster that says HELLO WORLD in bold letters"
}'
```

### Seedream 4.5（4K 画质）

```bash
belt app run bytedance/seedream-4-5 --input '{
  "prompt": "cinematic portrait of a woman, golden hour lighting"
}'
```

### 图像放大

```bash
belt app run falai/topaz-image-upscaler --input '{"image_url": "https://..."}'
```

### 拼接多张图像

```bash
belt app run infsh/stitch-images --input '{
  "images": ["https://img1.jpg", "https://img2.jpg"],
  "direction": "horizontal"
}'
```

## 相关技能

```bash
# Full platform skill (all apps)
npx skills add inference-sh/skills@infsh-cli

# Pruna P-Image (fast & economical)
npx skills add inference-sh/skills@p-image

# GPT-Image-2 (OpenAI)
npx skills add inference-sh/skills@gpt-image

# FLUX-specific skill
npx skills add inference-sh/skills@flux-image

# Upscaling & enhancement
npx skills add inference-sh/skills@image-upscaling

# Background removal
npx skills add inference-sh/skills@background-removal

# Video generation
npx skills add inference-sh/skills@ai-video-generation

# AI avatars from images
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的说明
- [图像生成示例](https://inference.sh/docs/examples/image-generation) - 完整的图像生成指南
- [应用概览](https://inference.sh/docs/apps/overview) - 了解应用生态系统
