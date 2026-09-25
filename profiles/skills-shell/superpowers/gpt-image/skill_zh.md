> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# GPT-Image-2

通过 [inference.sh](https://inference.sh) CLI 生成和编辑 OpenAI 的 GPT-Image-2 图像。

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run openai/gpt-image-2 --input '{"prompt": "一只漂浮在太空中的宇航员猫"}'
```

## 功能

GPT-Image-2 支持文本到图像生成、使用参考图像进行图像编辑以及基于掩码的修复——所有功能都通过单个模型实现。

| 功能 | 描述 |
|---------|-------------|
| 文本到图像 | 从文本提示生成图像 |
| 图像编辑 | 使用参考图像编辑图像 |
| 修复 | 基于掩码的特定区域编辑 |
| 批量生成 | 一次生成最多 10 张图像 |
| 多种格式 | PNG、JPEG、WebP 输出 |
| 灵活分辨率 | 任何 32px 倍数的尺寸（256–4096） |

## 示例

### 文本到图像

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "白色背景上的专业运动鞋产品照片，影棚灯光",
  "quality": "high"
}'
```

### 多张图像

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "咖啡店极简标志设计",
  "n": 4,
  "quality": "medium"
}'
```

### 使用参考图像进行编辑

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "将背景改为日落海滩",
  "images": ["https://your-image.jpg"]
}'
```

### 多张参考图像

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "将这两个角色合并到一个场景中",
  "images": ["https://character1.jpg", "https://character2.jpg"]
}'
```

### 基于掩码的修复

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "替换为红色跑车",
  "images": ["https://street-scene.jpg"],
  "mask": "https://car-mask.png"
}'
```

### 自定义分辨率

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "金色时刻的山脉宽屏电影风景",
  "width": 1920,
  "height": 1080,
  "quality": "high"
}'
```

### 快速草图

```bash
belt app run openai/gpt-image-2 --input '{
  "prompt": "机器人快速概念草图",
  "quality": "low"
}'
```

## 定价

| 质量 | 每张图像价格 |
|---------|-----------------|
| 低 | $0.006 |
| 中 | $0.024 |
| 高 | $0.21 |

更高分辨率的价格更高。有关完整定价详情，请查看 `belt app get openai/gpt-image-2`。

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `prompt` | 字符串 | 必填 | 描述图像的文本提示 |
| `images` | 数组 | - | 用于编辑的参考图像 |
| `mask` | 字符串 | - | 用于修复的掩码图像 |
| `n` | 整数 | 1 | 图像数量（1–10） |
| `quality` | 字符串 | - | low、medium 或 high |
| `width` | 整数 | - | 输出宽度（256–4096，32 的倍数） |
| `height` | 整数 | - | 输出高度（256–4096，32 的倍数） |
| `output_format` | 字符串 | png | png、jpeg 或 webp |
| `output_compression` | 整数 | - | jpeg/webp 的压缩级别（0–100） |

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
- [实时进度更新](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
