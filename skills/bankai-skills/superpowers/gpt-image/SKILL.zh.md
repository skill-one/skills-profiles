---
name: gpt-image
description: 通过 inference.sh 命令行界面使用 OpenAI GPT-Image-2 生成和编辑图像。模型：GPT-Image-2。功能：文本到图像、图像编辑、修复、基于蒙版的编辑、多图像参考、批量生成。用途：产品原型图、营销视觉、图像编辑、概念艺术、修复、照片处理。触发词：gpt image、gpt-image-2、openai image、chatgpt image、dall-e、dalle、openai image generation、gpt image edit、gpt inpainting、openai dall-e、gpt 4o image
---

> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# GPT-Image-2

通过 [inference.sh](https://inference.sh) CLI 使用 OpenAI 的 GPT-Image-2 生成和编辑图像。

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run openai/gpt-image-2 --input '{"prompt": "a cat astronaut floating in space"}'
```

## 功能

GPT-Image-2 支持文生图、使用参考图像进行图像编辑以及基于蒙版的修复——所有这些功能都通过单个模型实现。

| 功能 | 描述 |
|---------|-------------|
| 文生图 | 根据文本提示词生成图像 |
| 图像编辑 | 使用参考图像编辑图片 |
| 修复（Inpainting） | 对特定区域进行基于蒙版的编辑 |
| 批量生成 | 一次最多生成 10 张图像 |
| 多种格式 | 支持 PNG、JPEG、WebP 输出 |
| 灵活分辨率 | 32 像素增量内的任意尺寸（256–4096） |

## 示例

### 文生图

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "professional product photo of sneakers on a white background, studio lighting",
  "quality": "high"
}'
```

### 多张图像

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "minimalist logo design for a coffee shop",
  "n": 4,
  "quality": "medium"
}'
```

### 使用参考图像编辑

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "change the background to a beach at sunset",
  "images": ["https://your-image.jpg"]
}'
```

### 多图参考

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "combine these two characters into one scene",
  "images": ["https://character1.jpg", "https://character2.jpg"]
}'
```

### 使用蒙版修复

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "replace with a red sports car",
  "images": ["https://street-scene.jpg"],
  "mask": "https://car-mask.png"
}'
```

### 自定义分辨率

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "wide cinematic landscape, mountains at golden hour",
  "width": 1920,
  "height": 1080,
  "quality": "high"
}'
```

### 快速草稿

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "quick concept sketch of a robot",
  "quality": "low"
}'
```

## 定价

| 质量 | 单张图像大约价格 |
|---------|-----------------|
| 低 | $0.006 |
| 中 | $0.024 |
| 高 | $0.21 |

更高分辨率的费用更高。请参见 `belt app get openai/gpt-image-2` 以获取完整的定价详情。

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `prompt` | string | 必填 | 描述图像的文本提示词 |
| `images` | array | - | 用于编辑的参考图像 |
| `mask` | string | - | 用于修复的蒙版图像 |
| `n` | integer | 1 | 图像数量（1–10） |
| `quality` | string | - | low、medium 或 high |
| `width` | integer | - | 输出宽度（256–4096，32 的倍数） |
| `height` | integer | - | 输出高度（256–4096，32 的倍数） |
| `output_format` | string | png | png、jpeg 或 webp |
| `output_compression` | integer | - | jpeg/webp 的压缩级别（0–100） |

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

- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [流式结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
