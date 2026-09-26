> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# AI 头像与口播视频

通过 [inference.sh](https://inference.sh) CLI 创建 AI 头像和口播视频。

![AI 头像与口播视频](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0tszs96s0n8z5gy8y5mbg7.jpeg)

## 快速入门

> 需要 inference.sh CLI（belt）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 推荐：P-Video-Avatar（最快、最便宜、内置 TTS）
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "你好，欢迎来到我们的产品演示！",
  "voice": "Zephyr (Female)"
}'
```

## 可用模型

**从 P-Video-Avatar 开始** — 它比替代方案快 18 倍且便宜 6 倍，具有内置 TTS、动态背景和 1080p 支持。

| 模型 | App ID | 最佳用途 | 内置 TTS |
|-------|--------|----------|-------------|
| **P-Video-Avatar** | `pruna/p-video-avatar` | **综合最佳：速度、成本、质量、控制** | **是（30 种声音，10 种语言）** |
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多角色、音频驱动 | 否 |
| Fabric 1.0 | `falai/fabric-1-0` | 图像带口型同步 | 是 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 对现有视频进行口型同步 | 是 |

### 成本与速度对比

| 模型 | 速度（每秒视频） | 每秒成本 |
|-------|-------------------------|----------------|
| **P-Video-Avatar** | **~1.83s/s** | **$0.025** |
| OmniHuman 1.5 | ~28s/s (15 倍慢) | $0.16 (6.4 倍高) |
| Fabric 1.0 | ~34s/s (18 倍慢) | $0.14 (5.6 倍高) |

## 示例

### P-Video-Avatar（推荐）

从肖像 + 文本脚本生成头像并使用内置 TTS：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "欢迎来到我们的产品演示。今天我将向您展示三个关键功能。",
  "voice": "Puck (Male)",
  "voice_language": "English (US)",
  "resolution": "720p"
}'
```

使用自定义样式控制：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "这是令人兴奋的消息！",
  "voice": "Aoede (Female)",
  "voice_prompt": "热情且充满活力的语气",
  "video_prompt": "这个人正在舞台上演讲，灯光戏剧化",
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

### 完整工作流程：生成肖像 + 头像

使用 Pruna P-Image 生成肖像，然后创建头像：

```bash
# 1. 生成肖像图像
belt app run pruna/p-image --input '{
  "prompt": "专业头像肖像，年轻女性，中性背景，看向镜头，工作室灯光，照片级真实感",
  "aspect_ratio": "9:16"
}'

# 2. 使用内置 TTS 创建头像视频
belt app run pruna/p-video-avatar --input '{
  "image": "<步骤 1 的 image-url>",
  "voice_script": "嗨！让我带您了解我们最新的功能。",
  "voice": "Zephyr (Female)"
}'
```

### OmniHuman 1.5（多角色）

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image": "https://portrait.jpg",
  "audio": "https://speech.mp3"
}'
```

支持在多人图像中指定驱动哪个角色。

### Fabric 1.0（图像说话）

```bash
belt app run falai/fabric-1-0 --input '{
  "image": "https://face.jpg",
  "audio": "https://audio.mp3"
}'
```

### PixVerse Lipsync

```bash
belt app run falai/pixverse-lipsync --input '{
  "video": "https://talking-head.mp4",
  "audio": "https://speech.mp3"
}'
```

需要一个视频，而不是静态图像。省略 `audio` 并传递 `text`（以及可选的 `voice_id`）以使用内置 TTS。

## 完整工作流程：TTS + 头像（非 TTS 模型）

对于没有内置 TTS 的模型（OmniHuman），首先生成语音：

```bash
# 1. 生成语音 — Inworld TTS-2 用于表现力强的角色声音
belt app run inworld/text-to-speech-2 --input '{
  "text": "[友好] 欢迎来到我们的产品演示！[兴奋] 让我向您展示三个将改变您工作方式的功能。",
  "voice_id": "Sarah",
  "delivery_mode": "CREATIVE"
}' > speech.json

# 2. 使用语音创建头像视频
belt app run bytedance/omnihuman-1-5 --input '{
  "image": "https://presenter-photo.jpg",
  "audio": "<步骤 1 的 audio-url>"
}'
```

> **提示**：对于大多数用例，带有内置 TTS 的 P-Video-Avatar 更简单——无需单独的音频步骤。仅在您确实需要 OmniHuman（多角色）或 PixVerse（逼真口型同步）时使用此工作流程。

## 完整工作流程：将视频翻译成另一种语言

```bash
# 1. 转录原始视频
belt app run infsh/fast-whisper-large-v3 --input '{"audio": "https://video.mp4"}' > transcript.json

# 2. 翻译文本（手动或使用 LLM）

# 3. 在新语言中生成语音
belt app run falai/kokoro-tts --input '{"prompt": "<translated-text>"}' > new_speech.json

# 4. 使用新音频口型同步原始视频
belt app run infsh/latentsync-1-6 --input '{
  "video_path": "https://original-video.mp4",
  "audio_path": "<new-audio-url>"
}'
```

## 头像 UGC 生成

使用 P-Video-Avatar 创建 UGC 风格内容——内置 TTS，无需单独的音频步骤：

```bash
# 1. 生成一个 relatable 的 UGC 风格肖像
belt app run pruna/p-image --input '{
  "prompt": "舒适的房间中年轻女性的休闲自拍式照片，自然光线，看向镜头，温暖的微笑，真实感",
  "aspect_ratio": "9:16"
}'

# 2. 使用内置 TTS 创建 UGC 头像视频
belt app run pruna/p-video-avatar --input '{
  "image": "<步骤 1 的 image-url>",
  "voice_script": "好吧，我刚刚试了这个产品，老实说？它彻底改变了游戏规则。我没有想到会喜欢它这么多，但就是这样！",
  "voice": "Zephyr (Female)",
  "voice_prompt": "兴奋、休闲、像和朋友聊天一样的真实语气",
  "video_prompt": "这个人正在房间里随意地对着镜头说话，自然的手势",
  "resolution": "1080p"
}'
```

### 为什么选择 P-Video-Avatar 进行 UGC

- **一体化**——内置 TTS 意味着无需单独的音频生成步骤
- **30 种声音，10 种语言**——匹配您的目标受众
- **语音 + 视频提示**——独立控制语气、情绪、肢体语言和背景
- **快 18 倍，便宜 6 倍**——与 Fabric/OmniHuman/HeyGen 相比，大规模生产 UGC
- **1080p 支持**——从单个肖像图像生成平台就绪的竖屏视频

### 批量 UGC：同一产品，多个主持人

```bash
# 生成 3 个不同的主持人
for voice in "Zephyr (Female)" "Puck (Male)" "Aoede (Female)"; do
  belt app run pruna/p-video-avatar --input "{
    \"image\": \"https://portrait.jpg\",
    \"voice_script\": \"这彻底改变了我的早晨例行公事。五分钟就完成了。\",
    \"voice\": \"$voice\",
    \"voice_prompt\": \"休闲、真实，像真实的证言\",
    \"video_prompt\": \"人在明亮的厨房中对镜头说话\",
    \"resolution\": \"1080p\"
  }"
done
```

## 应用场景

- **UGC 与营销**：产品演示、UGC 风格的广告，使用 AI 主持人
- **教育**：课程视频、解释视频
- **本地化**：从一张图像将内容翻译成 10 种语言
- **社交媒体**：一致的虚拟影响者内容
- **企业**：培训视频、公告
- **游戏**：角色头像、NPC 对话

## 小贴士

- 使用高质量的肖像照片（正面、良好光线）
- 音频应清晰，背景噪音最小
- P-Video-Avatar 支持内置 TTS——无需单独的语音生成步骤
- P-Video-Avatar 输出宽高比与输入图像匹配
- 使用 `pruna/p-image` 生成肖像，使用 `9:16` 宽高比生成竖屏视频
- OmniHuman 1.5 支持一张图像中的多个人
- LatentSync 最适合将现有视频与新的音频同步

## 相关技能

```bash
# 专门的 P-Video-Avatar 技能
npx skills add inference-sh/skills@p-video-avatar

# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 文本转语音（为非 TTS 头像模型生成音频）
npx skills add inference-sh/skills@text-to-speech

# 语音转文本（用于配音）
npx skills add inference-sh/skills@speech-to-text

# 视频生成
npx skills add inference-sh/skills@ai-video-generation

# 图像生成（创建头像图像）
npx skills add inference-sh/skills@ai-image-generation
```

浏览所有视频应用：`belt app list --category video`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流程
- [实时进度更新](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
