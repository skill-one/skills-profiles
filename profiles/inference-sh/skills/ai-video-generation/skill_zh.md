> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 视频生成

通过 [inference.sh](https://inference.sh) CLI 使用 40+ AI 模型生成视频。

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

| 模型 | App ID | 适合场景 |
|-------|--------|----------|
| Veo 3.1 Fast | `google/veo-3-1-fast` | 快速，可选配音频 |
| Veo 3.1 | `google/veo-3-1` | 最佳画质，帧插值 |
| **P-Video** | `pruna/p-video` | 快速，经济型，支持音频 |
| **WAN-T2V** | `pruna/wan-t2v` | 经济型 480p/720p |
| Grok Video | `xai/grok-imagine-video` | xAI，可配置时长 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 文本/图像/参考视频同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，相同功能 |
| **HappyHorse T2V** | `alibaba/happyhorse-1-0-t2v` | 物理真实感，最长 15 秒 |

### 图像到视频

| 模型 | App ID | 适合场景 |
|-------|--------|----------|
| Wan 2.5 | `falai/wan-2-5` | 动画化任何图像 |
| Wan 2.5 I2V | `falai/wan-2-5-i2v` | 高质量图像到视频 |
| **WAN-I2V** | `pruna/wan-i2v` | 经济型 480p/720p |
| **P-Video** | `pruna/p-video` | 快速图像到视频，支持音频 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 动画化图像同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，相同功能 |
| **HappyHorse I2V** | `alibaba/happyhorse-1-0-i2v` | 动画化图像，最高 1080P/15s |
| **HappyHorse R2V** | `alibaba/happyhorse-1-0-r2v` | 从参考中保留角色 |

### 虚拟形象 / 唇形同步

| 模型 | App ID | 适合场景 |
|-------|--------|----------|
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多角色 |
| OmniHuman 1.0 | `bytedance/omnihuman-1-0` | 单角色 |
| Fabric 1.0 | `falai/fabric-1-0` | 图像唇形同步 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 真实唇形同步 |

### 视频编辑

| 模型 | App ID | 适合场景 |
|-------|--------|----------|
| HappyHorse Edit | `alibaba/happyhorse-1-0-video-edit` | 自然语言视频编辑 |

### 工具

| 工具 | App ID | 描述 |
|------|--------|-------------|
| MMAudio | `infsh/mmaudio` | 为视频添加音效 |
| Topaz Upscaler | `falai/topaz-video-upscaler` | 提升视频画质 |
| Media Merger | `infsh/media-merger` | 带转场效果合并视频 |

## 浏览所有视频应用

```bash
belt app list --category video
```

## 示例

### 使用 Veo 进行文本到视频

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

### 使用 Wan 2.5 进行图像到视频

```bash
belt app run falai/wan-2-5-i2v --input '{
  "image": "https://your-image.jpg",
  "prompt": "缓慢的摄像机推进"
}'
```

### AI 虚拟形象 / 演讲头

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image": "https://portrait.jpg",
  "audio": "https://speech.mp3"
}'
```

### Fabric 唇形同步

```bash
belt app run falai/fabric-1-0 --input '{
  "image": "https://face.jpg",
  "audio": "https://audio.mp3"
}'
```

### Seedance 2.0 文本到视频（带音频）

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "昏暗俱乐部中演奏的爵士乐队",
  "generate_audio": true,
  "duration": 10
}'
```

### Seedance 2.0 图像到视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "image": "https://your-image.jpg",
  "prompt": "轻柔的摄像机移动，树叶在风中沙沙作响",
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
  "video": "https://talking-head.mp4",
  "audio": "https://speech.mp3"
}'
```

输入视频，而非静态图像。省略 `audio` 并传递 `text`（可选 `voice_id`）以使用内置的 TTS。

### 视频提升

```bash
belt app run falai/topaz-video-upscaler --input '{"video": "https://..."}'
```

### 添加音效（拟音）

```bash
belt app run infsh/mmaudio --input '{
  "video_input": "https://silent-video.mp4",
  "prompt": "砾石上的脚步声，鸟鸣"
}'
```

### 合并视频

```bash
belt app run infsh/media-merger --input '{
  "media_files": [
    {"file": "https://clip1.mp4", "transition_type": "crossfade"},
    {"file": "https://clip2.mp4"}
  ]
}'
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# Pruna P-Video（快速且经济型）
npx skills add inference-sh/skills@p-video

# Google Veo 特定
npx skills add inference-sh/skills@google-veo

# Seedance 2.0
npx skills add inference-sh/skills@seedance

# HappyHorse 1.0
npx skills add inference-sh/skills@happyhorse

# AI 虚拟形象 & 唇形同步
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
