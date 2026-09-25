> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 视频生成

通过 [inference.sh](https://inference.sh) CLI 使用 40+ AI 模型生成视频。

![AI 视频生成](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg2c0egyg243mnyth4y6g51q.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 使用 Veo 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "无人机拍摄飞越森林"}'
```

## 可用模型

### 文生视频

| 模型 | App ID | 适用场景 |
|-------|--------|----------|
| Veo 3.1 Fast | `google/veo-3-1-fast` | 快速生成，支持可选音频 |
| Veo 3.1 | `google/veo-3-1` | 质量最佳，支持帧插值 |
| Veo 3 | `google/veo-3` | 高质量，支持音频 |
| Veo 3 Fast | `google/veo-3-fast` | 快速生成，支持音频 |
| Veo 2 | `google/veo-2` | 真实感视频 |
| **P-Video** | `pruna/p-video` | 快速、经济，支持音频 |
| **WAN-T2V** | `pruna/wan-t2v` | 经济型 480p/720p |
| Grok Video | `xai/grok-imagine-video` | xAI，可配置时长 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 文本/图片/参考图转视频，支持同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，具备相同能力 |
| **HappyHorse T2V** | `alibaba/happyhorse-1-0-t2v` | 物理真实感，最长 15s |

### 图生视频

| 模型 | App ID | 适用场景 |
|-------|--------|----------|
| Wan 2.5 | `falai/wan-2-5` | 将任意图片动起来 |
| Wan 2.5 I2V | `falai/wan-2-5-i2v` | 高质量 I2V |
| **WAN-I2V** | `pruna/wan-i2v` | 经济型 480p/720p |
| **P-Video** | `pruna/p-video` | 快速 I2V，支持音频 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 图像动态化，支持同步音频，最高 1080p |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，具备相同能力 |
| **HappyHorse I2V** | `alibaba/happyhorse-1-0-i2v` | 图像动态化，最高 1080P/15s |
| **HappyHorse R2V** | `alibaba/happyhorse-1-0-r2v` | 基于参考的保持角色风格 |

### 数字人 / 口型同步

| 模型 | App ID | 适用场景 |
|-------|--------|----------|
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多角色 |
| OmniHuman 1.0 | `bytedance/omnihuman-1-0` | 单角色 |
| Fabric 1.0 | `falai/fabric-1-0` | 图像口型同步说话 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 真实感口型同步 |

### 视频编辑

| 模型 | App ID | 适用场景 |
|-------|--------|----------|
| HappyHorse Edit | `alibaba/happyhorse-1-0-video-edit` | 自然语言视频编辑 |

### 工具类

| 工具 | App ID | 说明 |
|------|--------|------|
| HunyuanVideo Foley | `infsh/hunyuanvideo-foley` | 为视频添加音效 |
| Topaz Upscaler | `falai/topaz-video-upscaler` | 提升视频画质 |
| Media Merger | `infsh/media-merger` | 带转场合并视频 |

## 浏览所有视频应用

```bash
belt app list --category video
```

## 示例

### Veo 文生视频

```bash
belt app run google/veo-3-1-fast --input '{
  "prompt": "花园中花朵绽放的延时摄影"
}'
```

### Grok Video

```bash
belt app run xai/grok-imagine-video --input '{
  "prompt": "日落时分海浪拍打沙滩",
  "duration": 5
}'
```

### Wan 2.5 图生视频

```bash
belt app run falai/wan-2-5 --input '{
  "image_url": "https://your-image.jpg"
}'
```

### AI 数字人 / 说话人头像

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

### Fabric 口型同步

```bash
belt app run falai/fabric-1-0 --input '{
  "image_url": "https://face.jpg",
  "audio_url": "https://audio.mp3"
}'
```

### Seedance 2.0 文生视频（带音频）

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "一支爵士乐队在昏暗的俱乐部中演奏",
  "generate_audio": true,
  "duration": 10
}'
```

### Seedance 2.0 图生视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "image": "https://your-image.jpg",
  "prompt": "轻柔的镜头运动，风中树叶沙沙作响",
  "generate_audio": true
}'
```

### Seedance 2.0 参考图转视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "一位像参考图那样的人物漫步花园",
  "reference_image": "https://portrait.jpg",
  "generate_audio": true
}'
```

### HappyHorse 文生视频

```bash
belt app run alibaba/happyhorse-1-0-t2v --input '{
  "prompt": "金毛犬在秋叶中奔跑，慢动作",
  "duration": 10,
  "resolution": "1080P"
}'
```

### HappyHorse 视频编辑

```bash
belt app run alibaba/happyhorse-1-0-video-edit --input '{
  "video": "https://your-video.mp4",
  "prompt": "将背景替换为雪山景观"
}'
```

### PixVerse Lipsync

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
  "prompt": "踩在碎石上的脚步声，鸟儿鸣叫"
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
# 全平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# Pruna P-Video（快速且经济）
npx skills add inference-sh/skills@p-video

# Google Veo 专用
npx skills add inference-sh/skills@google-veo

# Seedance 2.0
npx skills add inference-sh/skills@seedance

# HappyHorse 1.0
npx skills add inference-sh/skills@happyhorse

# AI 数字人与口型同步
npx skills add inference-sh/skills@ai-avatar-video

# 文字转语音（用于视频旁白）
npx skills add inference-sh/skills@text-to-speech

# 图像生成（用于图生视频）
npx skills add inference-sh/skills@ai-image-generation

# Twitter（发布视频）
npx skills add inference-sh/skills@twitter-automation
```

浏览所有应用：`belt app list`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [流式结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容流水线示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
