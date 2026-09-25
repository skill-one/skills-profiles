> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Pruna P-视频生成

通过 [inference.sh](https://inference.sh) CLI 使用 Pruna 优化的视频模型生成视频。

![P-视频生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kkgymcjx9g2tv51m602jssn3.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run pruna/p-video --input '{"prompt": "无人机日落时分飞越森林的镜头"}'
```

## Pruna 视频模型

Pruna 优化 AI 模型以提升速度，同时不牺牲质量。

| 模型 | 应用 ID | 适用于 |
|-------|--------|----------|
| P-Video | `pruna/p-video` | 文本到视频、图像到视频（带音频） |
| WAN-T2V | `pruna/wan-t2v` | 文本到视频，480p/720p |
| WAN-I2V | `pruna/wan-i2v` | 动画图像，480p/720p |

## 示例

### 文本到视频

```bash
belt app run pruna/p-video --input '{
  "prompt": "日落时分海浪拍打海滩",
  "duration": 5,
  "resolution": "720p"
}'
```

### 图像到视频

```bash
belt app run pruna/p-video --input '{
  "prompt": "缓慢的摄像机移动，云朵飘动",
  "image": "https://your-image.jpg"
}'
```

### 带音频

P-Video 支持与视频同步的音频输入：

```bash
belt app run pruna/p-video --input '{
  "prompt": "访谈场景中的人正在说话",
  "audio": "https://your-audio.mp3"
}'
```

### WAN 文本到视频

快速且经济的文本到视频：

```bash
belt app run pruna/wan-t2v --input '{
  "prompt": "一只猫在玩毛线球",
  "resolution": "720p",
  "duration": 5
}'
```

### WAN 图像到视频

动画化任何静态图像：

```bash
belt app run pruna/wan-i2v --input '{
  "prompt": "轻柔的运动，自然动作，微弱呼吸",
  "image": "https://portrait.jpg",
  "resolution": "720p"
}'
```

### 1080p 高质量

```bash
belt app run pruna/p-video --input '{
  "prompt": "具有戏剧性云层的电影感风景",
  "resolution": "1080p",
  "duration": 5
}'
```

### 草稿模式（更快、更便宜）

```bash
belt app run pruna/p-video --input '{
  "prompt": "快速概念测试视频",
  "draft": true
}'
```

## 分辨率选项

| 模型 | 分辨率 | 定价 |
|-------|-------------|---------|
| P-Video | 720p, 1080p | 按秒计费，根据分辨率/草稿不同而变化 |
| WAN-T2V | 480p, 720p | $0.05 (480p), $0.10 (720p) 每个视频 |
| WAN-I2V | 480p, 720p | $0.05 (480p), $0.11 (720p) 每个视频 |

## 浏览所有 Pruna 应用

```bash
belt app list --namespace pruna
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 所有视频生成模型
npx skills add inference-sh/skills@ai-video-generation

# 图像到视频指南
npx skills add inference-sh/skills@image-to-video

# Pruna 图像生成
npx skills add inference-sh/skills@p-image

# 文本到语音（用于视频旁白）
npx skills add inference-sh/skills@text-to-speech
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [流式传输结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
