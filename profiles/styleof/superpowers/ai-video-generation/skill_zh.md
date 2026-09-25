> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 视频生成

通过 [inference.sh](https://inference.sh) CLI 生成使用 40+ AI 模型的视频。

![AI 视频生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg2c0egyg243mnyth4y6g51q.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 使用 Veo 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "无人机飞越森林的航拍镜头"}'
```

## 可用模型

### 文本到视频

| 模型 | App ID | 最佳用途 |
|-------|--------|----------|
| Veo 3.1 Fast | `google/veo-3-1-fast` | 快速，可选配音频 |
| Veo 3.1 | `google/veo-3-1` | 最佳质量，帧插值 |
| Veo 3 | `google/veo-3` | 高质量带音频 |
| Veo 3 Fast | `google/veo-3-fast` | 带音频的快速 |
| Veo 2 | `google/veo-2` | 真实视频 |
| **P-Video** | `pruna/p-video` | 快速，经济，支持音频 |
| **WAN-T2V** | `pruna/wan-t2v` | 经济 480p/720p |
| Grok Video | `xai/grok-imagine-video` | xAI，可配置时长 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 文本/图像/参考视频同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，相同功能 |
| **HappyHorse T2V** | `alibaba/happyhorse-1-0-t2v` | 物理真实，最长 15 秒 |

### 图像到视频

| 模型 | App ID | 最佳用途 |
|-------|--------|----------|
| Wan 2.5 | `falai/wan-2-5` | 动画化任何图像 |
| Wan 2.5 I2V | `falai/wan-2-5-i2v` | 高质量图像到视频 |
| **WAN-I2V** | `pruna/wan-i2v` | 经济 480p/720p |
| **P-Video** | `pruna/p-video` | 快速图像到视频带音频 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 动画化图像同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，相同功能 |
| **HappyHorse I2V** | `alibaba/happyhorse-1-0-i2v` | 动画化图像，最高 1080P/15s |
| **HappyHorse R2V** | `alibaba/happyhorse-1-0-r2v` | 从参考中保留角色 |

### 头像 / 唇形同步

| 模型 | App ID | 最佳用途 |
|-------|--------|----------|
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多角色 |
| OmniHuman 1.0 | `bytedance/omnihuman-1-0` | 单角色 |
| Fabric 1.0 | `falai/fabric-1-0` | 图像带唇形同步 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 真实唇形同步 |

### 视频编辑

| 模型 | App ID | 最佳用途 |
|-------|--------|----------|
| HappyHorse Edit | `alibaba/happyhorse-1-0-video-edit` | 自然语言视频编辑 |

### 工具

| 工具 | App ID | 描述 |
|------|--------|-------------|
| HunyuanVideo Foley | `infsh/hunyuanvideo-foley` | 为视频添加音效 |
| Topaz Upscaler | `falai/topaz-video-upscaler` | 提升视频质量 |
| Media Merger | `infsh/media-merger` | 带转场效果合并视频 |

## 浏览所有视频应用

```bash
belt app list --category video
```

## 示例

### 使用 Veo 的文本到视频

```bash
belt app run google/veo-3-1-fast --input '{
  "prompt": "花园中花朵绽放的延时摄影"
}'
```

### Grok Video

```bash
belt app run xai/grok-imagine-video --input '{
  "prompt": "日落时海滩上拍打的海浪",
  "duration": 5
}'
```

### 使用 Wan 2.5 的图像到视频

```bash
belt app run falai/wan-2-5 --input '{
  "image_url": "https://your-image.jpg"
}'
```

### AI 头像 / 演讲者

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

### Seedance 2.0 文本到视频带音频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "爵士乐队在昏暗俱乐部表演",
  "generate_audio": true,
  "duration": 10
}'
```

### Seedance 2.0 图像到视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "image": "https://your-image.jpg",
  "prompt": "轻柔的相机移动，树叶在风中沙沙作响",
  "generate_audio": true
}'
```

### Seedance 2.0 参考到视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "一个看起来像参考的人走过花园",
  "reference_image": "https://portrait.jpg",
  "generate_audio": true
}'
```

### HappyHorse 文本到视频

```bash
belt app run alibaba/happyhorse-1-0-t2v --input '{
  "prompt": "金毛猎犬在秋叶中奔跑，慢动作",
  "duration": 10,
  "resolution": "1080P"
}'
```

### HappyHorse 视频编辑

```bash
belt app run alibaba/happyhorse-1-0-video-edit --input '{
  "video": "https://your-video.mp4",
  "prompt": "将背景改为雪山的风景"
}'
```

### PixVerse 唇形同步

```bash
belt app run falai/pixverse-lipsync --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

### 视频提升

```bash
belt app run falai/topaz-video-upscaler --input '{"video_url": "https://..."}'
```

### 添加音效（Foley）

```bash
belt app run infsh/hunyuanvideo-foley --input '{
  "video_url": "https://silent-video.mp4",
  "prompt": "砾石上的脚步声，鸟鸣"
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

# Pruna P-Video（快速且经济）
npx skills add inference-sh/skills@p-video

# Google Veo 特定
npx skills add inference-sh/skills@google-veo

# Seedance 2.0
npx skills add inference-sh/skills@seedance

# HappyHorse 1.0
npx skills add inference-sh/skills@happyhorse

# AI 头像 & 唇形同步
npx skills add inference-sh/skills@ai-avatar-video

# 文本到语音（用于视频旁白）
npx skills add inference-sh/skills@text-to-speech

# 图像生成（用于图像到视频）
npx skills add inference-sh/skills@ai-image-generation

# Twitter（发布视频）
npx skills add inference-sh/skills@twitter-automation
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用
- [实时进度更新](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
