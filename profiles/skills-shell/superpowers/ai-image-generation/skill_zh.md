**安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 图像生成

通过 [inference.sh](https://inference.sh) CLI 使用 50+ 个 AI 模型生成图像。

![AI 图像生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0v0nz7wv0qwqjtq1cam52z.jpeg)

## 快速开始

需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 使用 FLUX 生成图像
belt app run falai/flux-dev-lora --input '{"prompt": "a cat astronaut in space"}'
```

## 可用模型

| 模型 | 应用 ID | 适用场景 |
|-------|--------|----------|
| **GPT-Image-2** | `openai/gpt-image-2` | 文生图、编辑、局部重绘 |
| FLUX Dev LoRA | `falai/flux-dev-lora` | 高质量、支持自定义风格 |
| FLUX.2 Klein LoRA | `falai/flux-2-klein-lora` | 快速、支持 LoRA（4B/9B） |
| **P-Image** | `pruna/p-image` | 快速、经济实惠、支持多方向 |
| **P-Image-LoRA** | `pruna/p-image-lora` | 快速、支持预设 LoRA 风格 |
| **P-Image-Edit** | `pruna/p-image-edit` | 快速图像编辑 |
| Gemini 3 Pro | `google/gemini-3-pro-image-preview` | Google 最新 |
| Gemini 2.5 Flash | `google/gemini-2-5-flash-image` | Google 快速模型 |
| Grok Imagine | `xai/grok-imagine-image` | xAI 模型，支持多方向 |
| Seedream 4.5 | `bytedance/seedream-4-5` | 2K-4K 电影级画质 |
| Seedream 4.0 | `bytedance/seedream-4-0` | 高质量 2K-4K |
| Seedream 3.0 | `bytedance/seedream-3-0-t2i` | 文字渲染精准 |
| Reve | `falai/reve` | 自然语言编辑、文字渲染 |
| ImagineArt 1.5 Pro | `falai/imagine-art-1-5-pro-preview` | 超高清 4K |
| FLUX Klein 4B | `pruna/flux-klein-4b` | 极低价格（$0.0001/张） |
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

### 使用 FLUX 进行文生图

```bash
belt app run falai/flux-dev-lora --input '{
  "prompt": "professional product photo of a coffee mug, studio lighting"
}'
```

### 使用 FLUX Klein 快速生成

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

### Seedream 4.5（4K 质量）

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
# 全平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# Pruna P-Image（快速且经济实惠）
npx skills add inference-sh/skills@p-image

# GPT-Image-2 (OpenAI)
npx skills add inference-sh/skills@gpt-image

# 特定于 FLUX 的技能
npx skills add inference-sh/skills@flux-image

# 放大与增强
npx skills add inference-sh/skills@image-upscaling

# 背景去除
npx skills add inference-sh/skills@background-removal

# 视频生成
npx skills add inference-sh/skills@ai-video-generation

# 从图像生成 AI 头像
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的方法
- [图像生成示例](https://inference.sh/docs/examples/image-generation) - 完整的图像生成指南
- [应用概览](https://inference.sh/docs/apps/overview) - 了解应用生态
