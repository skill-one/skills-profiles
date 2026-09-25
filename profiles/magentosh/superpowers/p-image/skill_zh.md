> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Pruna P-Image 生成

通过 [inference.sh](https://inference.sh) CLI 使用 Pruna 优化的 P-Image 模型生成图像。

![P-Image 生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kkgym0yqys16pqrg9h8ctk2y.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run pruna/p-image --input '{"prompt": "一个日落时分的未来城市景观"}'
```

## P-Image 模型

Pruna 优化 AI 模型以提高速度，同时不牺牲质量。

| 模型 | 应用 ID | 适用于 |
|-------|--------|----------|
| P-Image | `pruna/p-image` | 快速文本到图像，多种宽高比 |
| P-Image-LoRA | `pruna/p-image-lora` | 使用预设 LoRAs 的自定义风格 |
| P-Image-Edit | `pruna/p-image-edit` | 支持多图像的图像编辑 |
| P-Image-Edit-LoRA | `pruna/p-image-edit-lora` | 带有风格的图像编辑 |

## 示例

### 文本到图像

```bash
belt app run pruna/p-image --input '{
  "prompt": "专业运动鞋照片，影棚灯光",
  "aspect_ratio": "1:1"
}'
```

### 使用 LoRA 预设

P-Image-LoRA 包含内置风格预设：

```bash
belt app run pruna/p-image-lora --input '{
  "prompt": "金色光线中的女性肖像",
  "lora_preset": "photos-realism"
}'
```

可用预设：`photos-realism`，`pixel-art`，`japanese-modern-look`，`cinematic-movie-style`，`graffiti-splash`，`neon-punk`，`anime-2-5d`，`ethereal-portrait`，`retro-90s-style`，`ink-sketchbook`，`paper-cut`

### 图像编辑

```bash
belt app run pruna/p-image-edit --input '{
  "prompt": "将背景改为海滩",
  "images": ["https://your-image.jpg"]
}'
```

### 多图像合成

```bash
belt app run pruna/p-image-edit --input '{
  "prompt": "将这些图像合成拼贴",
  "images": ["https://img1.jpg", "https://img2.jpg", "https://img3.jpg"]
}'
```

### 自定义宽高比

```bash
belt app run pruna/p-image --input '{
  "prompt": "山地风景",
  "aspect_ratio": "16:9"
}'
```

支持的宽高比：`1:1`，`16:9`，`9:16`，`4:3`，`3:4`，`3:2`，`2:3`，或使用宽度/高度自定义

## 其他 Pruna 模型

Pruna 提供流行模型的优化版本：

```bash
# FLUX Dev (优化版)
belt app run pruna/flux-dev --input '{"prompt": "..."}'

# FLUX Klein 4B (极快，$0.0001/图像)
belt app run pruna/flux-klein-4b --input '{"prompt": "..."}'

# Qwen 图像
belt app run pruna/qwen-image --input '{"prompt": "..."}'

# Z-Image Turbo (超快)
belt app run pruna/z-image-turbo --input '{"prompt": "..."}'

# WAN 图像 Small (批量生成)
belt app run pruna/wan-image-small --input '{"prompt": "..."}'
```

## 浏览所有 Pruna 应用

```bash
belt app list --namespace pruna
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 所有图像生成模型
npx skills add inference-sh/skills@ai-image-generation

# Pruna 视频生成
npx skills add inference-sh/skills@p-video

# FLUX 模型
npx skills add inference-sh/skills@flux-image
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的方法
- [图像生成示例](https://inference.sh/docs/examples/image-generation) - 完整图像生成指南
- [流式传输结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
