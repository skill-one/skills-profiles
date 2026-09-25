**安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 视频生成

通过 [inference.sh](https://inference.sh) CLI，使用 40+ AI 模型生成视频。

![AI 视频生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg2c0egyg243mnyth4y6g51q.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# Generate a video with Veo
belt app run google/veo-3-1-fast --input '{"prompt": "drone shot flying over a forest"}'
```

## 可用模型

### 文本转视频

| 模型 | 应用 ID | 适用场景 |
|-------|--------|----------|
| Veo 3.1 Fast | `google/veo-3-1-fast` | 快速，支持可选音频 |
| Veo 3.1 | `google/veo-3-1` | 质量最佳，支持帧插值 |
| Veo 3 | `google/veo-3` | 高质量，支持音频 |
| Veo 3 Fast | `google/veo-3-fast` | 快速，支持音频 |
| Veo 2 | `google/veo-2` | 真实感视频 |
| **P-Video** | `pruna/p-video` | 快速、经济实惠，支持音频 |
| **WAN-T2V** | `pruna/wan-t2v` | 经济实惠，支持 480p/720p |
| Grok Video | `xai/grok-imagine-video` | xAI，时长可配置 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 文本/图像/参考转视频，支持同步音频，最高支持 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速版本，功能相同 |
| **HappyHorse T2V** | `alibaba/happyhorse-1-0-t2v` | 物理真实感，最长支持 15 秒 |

### 图像转视频

| 模型 | 应用 ID | 适用场景 |
|-------|--------|----------|
| Wan 2.5 | `falai/wan-2-5` | 动画任何图像 |
| Wan 2.5 I2V | `falai/wan-2-5-i2v` | 高质量 i2v |
| **WAN-I2V** | `pruna/wan-i2v` | 经济实惠，支持 480p/720p |
| **P-Video** | `pruna/p-video` | 快速 i2v，支持音频 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 动画图像，支持同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速版本，功能相同 |
| **HappyHorse I2V** | `alibaba/happyhorse-1-0-i2v` | 动画图像，最高 1080P/15s |
| **HappyHorse R2V** | `alibaba/happyhorse-1-0-r2v` | 从参考内容保留角色特征 |

### 虚拟形象 / 唇形同步

| 模型 | 应用 ID | 适用场景 |
|-------|--------|----------|
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多角色 |
| OmniHuman 1.0 | `bytedance/omnihuman-1-0` | 单角色 |
| Fabric 1.0 | `falai/fabric-1-0` | 图像说话并实现唇形同步 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 真实唇形同步 |

### 视频编辑

| 模型 | 应用 ID | 适用场景 |
|-------|--------|----------|
| HappyHorse Edit | `alibaba/happyhorse-1-0-video-edit` | 自然语言视频编辑 |

### 工具

| 工具 | 应用 ID | 说明 |
|------|--------|------|
| HunyuanVideo Foley | `infsh/hunyuanvideo-foley` | 为视频添加音效 |
| Topaz Upscaler | `falai/topaz-video-upscaler` | 提升视频画质 |
| Media Merger | `infsh/media-merger` | 带转场的视频合并 |

## 浏览所有视频应用

```bash
belt app list --category video
```

## 示例

### 使用 Veo 的文本转视频

```bash
belt app run google/veo-3-1-fast --input '{
  "prompt": "A timelapse of a flower blooming in a garden"
}'
```

### Grok Video

```bash
belt app run xai/grok-imagine-video --input '{
  "prompt": "Waves crashing on a beach at sunset",
  "duration": 5
}'
```

### 使用 Wan 2.5 的图像转视频

```bash
belt app run falai/wan-2-5 --input '{
  "image_url": "https://your-image.jpg"
}'
```

### AI 虚拟形象 / 说话头部

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

### Fabric 唇形同步

```bash
belt app run falai/fabric-1-0 --input '{
  "image_url": "https://face.jpg",
  "audio_url": "https://audio.mp3"
}'
```

### Seedance 2.0 带音频的文本转视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "a jazz band performing in a dimly lit club",
  "generate_audio": true,
  "duration": 10
}'
```

### Seedance 2.0 图像转视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "image": "https://your-image.jpg",
  "prompt": "gentle camera movement, leaves rustling in the wind",
  "generate_audio": true
}'
```

### Seedance 2.0 参考转视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "A person who looks like the reference walking through a garden",
  "reference_image": "https://portrait.jpg",
  "generate_audio": true
}'
```

### HappyHorse 文本转视频

```bash
belt app run alibaba/happyhorse-1-0-t2v --input '{
  "prompt": "a golden retriever running through autumn leaves, slow motion",
  "duration": 10,
  "resolution": "1080P"
}'
```

### HappyHorse 视频编辑

```bash
belt app run alibaba/happyhorse-1-0-video-edit --input '{
  "video": "https://your-video.mp4",
  "prompt": "change the background to a snowy mountain landscape"
}'
```

### PixVerse 唇形同步

```bash
belt app run falai/pixverse-lipsync --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

### 视频放大

```bash
belt app run falai/topaz-video-upscaler --input '{"video_url": "https://..."}'
```

### 添加音效（Foley）

```bash
belt app run infsh/hunyuanvideo-foley --input '{
  "video_url": "https://silent-video.mp4",
  "prompt": "footsteps on gravel, birds chirping"
}'
```

### 合并视频

```bash
belt app run infsh/media-merger --input '{
  "videos": ["https://clip1.mp4", "https://clip2.mp4"],
  "transition": "fade"
}'
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# Pruna P-Video（快速且经济实惠）
npx skills add inference-sh/skills@p-video

# Google Veo 专属
npx skills add inference-sh/skills@google-veo

# Seedance 2.0
npx skills add inference-sh/skills@seedance

# HappyHorse 1.0
npx skills add inference-sh/skills@happyhorse

# AI 虚拟形象与唇形同步
npx skills add inference-sh/skills@ai-avatar-video

# 文本转语音（用于视频旁白）
npx skills add inference-sh/skills@text-to-speech

# 图像生成（用于图像转视频）
npx skills add inference-sh/skills@ai-image-generation

# Twitter（发布视频）
npx skills add inference-sh/skills@twitter-automation
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的说明
- [实时结果流](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容流水线示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
