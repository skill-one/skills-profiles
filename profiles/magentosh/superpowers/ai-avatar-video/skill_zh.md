> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 虚拟形象与出镜视频

通过 [inference.sh](https://inference.sh) CLI 创建 AI 虚拟形象与出镜视频。

![AI 虚拟形象与出镜视频](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0tszs96s0n8z5gy8y5mbg7.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 推荐：P-Video-Avatar（速度最快、成本最低、内置 TTS）
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "Hello, welcome to our product demo!",
  "voice": "Zephyr (Female)"
}'
```

## 可用模型

**从 P-Video-Avatar 开始** — 相比其他方案速度快 18 倍、成本低 6 倍，内置 TTS、动态背景，并支持 1080p。

| 模型 | App ID | 最佳适用场景 | 内置 TTS |
|-------|--------|----------|-------------|
| **P-Video-Avatar** | `pruna/p-video-avatar` | **综合最佳：速度、成本、质量、可控性** | **是（30 个音色，10 种语言）** |
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多人物、音频驱动 | 否 |
| Fabric 1.0 | `falai/fabric-1-0` | 图像出镜、唇形同步 | 是 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 高度真实的唇形同步 | 否 |

### 成本与速度对比

| 模型 | 速度（视频每秒） | 每秒成本 |
|-------|-----------------|----------------|
| **P-Video-Avatar** | **~1.83s/s** | **$0.025** |
| OmniHuman 1.5 | ~28s/s（慢 15 倍） | $0.16（贵 6.4 倍） |
| Fabric 1.0 | ~34s/s（慢 18 倍） | $0.14（贵 5.6 倍） |

## 示例

### P-Video-Avatar（推荐）

从人像 + 文本脚本，使用内置 TTS 生成虚拟形象：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "Welcome to our product walkthrough. Today I will show you three key features.",
  "voice": "Puck (Male)",
  "voice_language": "English (US)",
  "resolution": "720p"
}'
```

带有自定义风格控制：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "This is exciting news!",
  "voice": "Aoede (Female)",
  "voice_prompt": "Enthusiastic and energetic tone",
  "video_prompt": "The person is presenting on stage with dramatic lighting",
  "resolution": "1080p"
}'
```

使用音频文件代替 TTS：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "audio": "https://speech.mp3"
}'
```

### 完整流程：生成人像 + 虚拟形象

使用 Pruna P-Image 生成人像，然后创建虚拟形象：

```bash
# 1. 生成人像图片
belt app run pruna/p-image --input '{
  "prompt": "professional headshot portrait of a young woman, neutral background, looking at camera, studio lighting, photorealistic",
  "aspect_ratio": "9:16"
}'

# 2. 使用内置 TTS 创建虚拟形象视频
belt app run pruna/p-video-avatar --input '{
  "image": "<image-url-from-step-1>",
  "voice_script": "Hi there! Let me walk you through our latest features.",
  "voice": "Zephyr (Female)"
}'
```

### OmniHuman 1.5（多人物）

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

支持在多人物图像中指定驱动的角色。

### Fabric 1.0（图像出镜）

```bash
belt app run falai/fabric-1-0 --input '{
  "image_url": "https://face.jpg",
  "audio_url": "https://audio.mp3"
}'
```

### PixVerse Lipsync

```bash
belt app run falai/pixverse-lipsync --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

## 完整流程：TTS + 虚拟形象（非 TTS 模型）

对于不支持内置 TTS 的模型（OmniHuman、PixVerse），先生成语音：

```bash
# 1. 生成语音 — 使用 Inworld TTS-2 生成富有表现力的角色语音
belt app run inworld/text-to-speech-2 --input '{
  "text": "[friendly] Welcome to our product demo! [excited] Let me show you three features that will change how you work.",
  "voice_id": "Sarah",
  "delivery_mode": "CREATIVE"
}' > speech.json

# 2. 使用语音创建虚拟形象视频
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://presenter-photo.jpg",
  "audio_url": "<audio-url-from-step-1>"
}'
```

> **提示**：对于大多数用例，内置 TTS 的 P-Video-Avatar 更简单——无需单独的音频步骤。仅当您明确需要 OmniHuman（多人物）或 PixVerse（真实唇同步）时，才使用此流程。

## 完整流程：为其他语言配字幕视频

```bash
# 1. 转写原始视频
belt app run infsh/fast-whisper-large-v3 --input '{"audio_url": "https://video.mp4"}' > transcript.json

# 2. 翻译文本（手动或使用 LLM）

# 3. 生成新语言的语音
belt app run infsh/kokoro-tts --input '{"text": "<translated-text>"}' > new_speech.json

# 4. 将新音频与原始视频进行唇形同步
belt app run infsh/latentsync-1-6 --input '{
  "video_url": "https://original-video.mp4",
  "audio_url": "<new-audio-url>"
}'
```

## 虚拟形象 UGC 生成

使用 P-Video-Avatar 创建 UGC 风格内容——内置 TTS，无需单独的音频步骤：

```bash
# 1. 生成具有共鸣感的 UGC 风格人像
belt app run pruna/p-image --input '{
  "prompt": "casual selfie-style photo of a young woman in a cozy room, natural lighting, looking at camera, warm smile, authentic feel",
  "aspect_ratio": "9:16"
}'

# 2. 使用内置 TTS 创建 UGC 虚拟形象视频
belt app run pruna/p-video-avatar --input '{
  "image": "<image-url-from-step-1>",
  "voice_script": "Okay so I just tried this product and honestly? It is a game changer. I was not expecting to love it this much but here we are!",
  "voice": "Zephyr (Female)",
  "voice_prompt": "Excited, casual, authentic tone like talking to a friend",
  "video_prompt": "The person is talking casually to camera in their room, natural gestures",
  "resolution": "1080p"
}'
```

### 为何选择 P-Video-Avatar 进行 UGC

- **一站式方案** — 内置 TTS 意味着无需单独的音频生成步骤
- **30 个音色，10 种语言** — 匹配目标受众
- **音色与视频提示词** — 可独立控制语气、情绪、肢体语言和背景
- **速度更快、成本更低（18 倍/6 倍）** — 与 Fabric/OmniHuman/HeyGen 相比，可规模化生成 UGC
- **支持 1080p** — 基于单一人像图片生成适合平台的竖版视频

### 批量 UGC：同一产品，多位演示者

```bash
# 生成 3 位不同的演示者
for voice in "Zephyr (Female)" "Puck (Male)" "Aoede (Female)"; do
  belt app run pruna/p-video-avatar --input "{
    \"image\": \"https://portrait.jpg\",
    \"voice_script\": \"This changed my morning routine completely. Five minutes and I am done.\",
    \"voice\": \"$voice\",
    \"voice_prompt\": \"Casual, authentic, like a real testimonial\",
    \"video_prompt\": \"Person talking to camera in a bright kitchen\",
    \"resolution\": \"1080p\"
  }"
done
```

## 使用场景

- **UGC 与营销**：产品演示、带有 AI 演示者的 UGC 风格广告
- **教育**：课程视频、解释类视频
- **本地化**：从一张图片跨 10 种语言生成配音内容
- **社交媒体**：一致的虚拟网红内容
- **企业**：培训视频、通知
- **游戏**：角色虚拟形象、NPC 对话

## 提示

- 使用高质量人像照片（正面、光线良好）
- 音频应清晰，背景噪音最小
- P-Video-Avatar 支持内置 TTS——无需单独的语音生成步骤
- P-Video-Avatar 的输出宽高比与输入图片一致
- 使用 `pruna/p-image` 生成人像时，采用 `9:16` 宽高比以生成竖版视频
- OmniHuman 1.5 支持单张图像中的多人
- LatentSync 最适合将现有视频与新音频进行同步

## 相关技能

```bash
# 专用 P-Video-Avatar 技能
npx skills add inference-sh/skills@p-video-avatar

# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 文本转语音（为非 TTS 虚拟形象模型生成音频）
npx skills add inference-sh/skills@text-to-speech

# 语音转文本（用于配音转写）
npx skills add inference-sh/skills@speech-to-text

# 视频生成
npx skills add inference-sh/skills@ai-video-generation

# 图像生成（创建虚拟形象图片）
npx skills add inference-sh/skills@ai-image-generation
```

浏览所有视频应用：`belt app list --category video`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的方法
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
- [流式结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
