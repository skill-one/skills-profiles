**安装腰带 CLI 技能：** `npx skills add belt-sh/cli`

# AI 虚拟形象与说话头视频

通过 [inference.sh](https://inference.sh) CLI 创建 AI 虚拟形象和说话头视频。

![AI 虚拟形象与说话头视频](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg0tszs96s0n8z5gy8y5mbg7.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 推荐：P-Video-Avatar（最快、最便宜，内置 TTS）
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "欢迎参加我们的产品演示！",
  "voice": "Zephyr (Female)"
}'
```

## 可用模型

**从 P-Video-Avatar 开始** —— 相比其他方案快 18 倍，成本降低 6 倍，内置 TTS、动态背景，支持 1080p。

| 模型 | App ID | 最佳适用场景 | 内置 TTS |
|-------|--------|----------|-------------|
| **P-Video-Avatar** | `pruna/p-video-avatar` | **综合最佳：速度、成本、质量、可控性** | **是（30 个音色，10 种语言）** |
| OmniHuman 1.5 | `bytedance/omnihuman-1-5` | 多人、音频驱动 | 否 |
| Fabric 1.0 | `falai/fabric-1-0` | 图片说话带口型同步 | 是 |
| PixVerse Lipsync | `falai/pixverse-lipsync` | 高度真实的口型同步 | 否 |

### 成本与速度对比

| 模型 | 速度（每秒视频） | 每秒成本 |
|-------|-----------------|----------|
| **P-Video-Avatar** | **~1.83s/s** | **$0.025** |
| OmniHuman 1.5 | ~28s/s（慢 15 倍） | $0.16（多 6.4 倍） |
| Fabric 1.0 | ~34s/s（慢 18 倍） | $0.14（多 5.6 倍） |

## 示例

### P-Video-Avatar（推荐）

从肖像图片 + 文字脚本，使用内置 TTS 生成虚拟形象：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "欢迎参加我们的产品演示。今天我将为您展示三个关键功能。",
  "voice": "Puck (Male)",
  "voice_language": "English (US)",
  "resolution": "720p"
}'
```

使用自定义风格控制：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "voice_script": "这是一个令人兴奋的消息！",
  "voice": "Aoede (Female)",
  "voice_prompt": "充满热情、活力充沛的语气",
  "video_prompt": "此人正在舞台上进行演示，灯光戏剧性强烈",
  "resolution": "1080p"
}'
```

使用音频文件而非 TTS：

```bash
belt app run pruna/p-video-avatar --input '{
  "image": "https://portrait.jpg",
  "audio": "https://speech.mp3"
}'
```

### 完整流程：生成肖像 + 虚拟形象

使用 Pruna P-Image 生成肖像，然后创建虚拟形象：

```bash
# 1. 生成肖像图片
belt app run pruna/p-image --input '{
  "prompt": "专业年轻女性证件照肖像，中性背景，面向镜头，影棚灯光，照片级真实感",
  "aspect_ratio": "9:16"
}'

# 2. 使用内置 TTS 创建虚拟形象视频
belt app run pruna/p-video-avatar --input '{
  "image": "<来自步骤 1 的图片 URL>",
  "voice_script": "你好！让我为您详细介绍我们最新的功能。",
  "voice": "Zephyr (Female)"
}'
```

### OmniHuman 1.5（多人）

```bash
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://portrait.jpg",
  "audio_url": "https://speech.mp3"
}'
```

支持在多人图片中指定由哪个人物驱动。

### Fabric 1.0（图片说话）

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

对于没有内置 TTS 的模型（OmniHuman、PixVerse），先生成语音：

```bash
# 1. 生成语音 —— 使用 Inworld TTS-2 生成富有表现力的人物声音
belt app run inworld/text-to-speech-2 --input '{
  "text": "[友好] 欢迎参加我们的产品演示！[激动] 让我为您展示三个将改变您工作方式的功能。",
  "voice_id": "Sarah",
  "delivery_mode": "CREATIVE"
}' > speech.json

# 2. 使用生成的语音创建虚拟形象视频
belt app run bytedance/omnihuman-1-5 --input '{
  "image_url": "https://presenter-photo.jpg",
  "audio_url": "<来自步骤 1 的音频 URL>"
}'
```

> **提示**：大多数使用场景下，内置 TTS 的 P-Video-Avatar 更简单 —— 无需单独的音频生成步骤。仅在需要 OmniHuman（多人）或 PixVerse（真实口型同步）时，才使用此流程。

## 完整流程：跨语言配音

```bash
# 1. 转写原始视频
belt app run infsh/fast-whisper-large-v3 --input '{"audio_url": "https://video.mp4"}' > transcript.json

# 2. 翻译文本（手动或使用 LLM）

# 3. 生成新语言的语音
belt app run infsh/kokoro-tts --input '{"text": "<翻译后的文本>"}' > new_speech.json

# 4. 用新音频与原始视频口型同步
belt app run infsh/latentsync-1-6 --input '{
  "video_url": "https://original-video.mp4",
  "audio_url": "<新音频 URL>"
}'
```

## 虚拟形象 UGC 生成

使用 P-Video-Avatar 创建 UGC 风格内容 —— 内置 TTS，无需单独的音频步骤：

```bash
# 1. 生成具有代入感的 UGC 风格肖像
belt app run pruna/p-image --input '{
  "prompt": "年轻女性穿着舒适服装在温馨房间里的随手自拍风格照片，自然光线，面向镜头，温暖微笑，真实感",
  "aspect_ratio": "9:16"
}'

# 2. 使用内置 TTS 创建 UGC 虚拟形象视频
belt app run pruna/p-video-avatar --input '{
  "image": "<来自步骤 1 的图片 URL>",
  "voice_script": "好吧，我刚刚试了这款产品，说实话？它堪称改变游戏的利器。我还以为自己不会这么喜欢它，结果就是这样！",
  "voice": "Zephyr (Female)",
  "voice_prompt": "兴奋、随性、像对朋友说话的真实语气",
  "video_prompt": "人物在房间里对着镜头随性交谈，自然动作",
  "resolution": "1080p"
}'
```

### 为何选择 P-Video-Avatar 进行 UGC

- **一体化** —— 内置 TTS 意味着无需单独的音频生成步骤
- **30 个音色，10 种语言** —— 匹配目标受众
- **语音与视频提示** —— 独立控制语气、情绪、肢体动作和背景
- **快 18 倍，便宜 6 倍** —— 相比 Fabric/OmniHuman/HeyGen 大规模产出 UGC
- **支持 1080p** —— 从单张肖像图片生成平台级竖屏视频

### 批量 UGC：同一产品，多位出镜者

```bash
# 生成 3 位不同的出镜者
for voice in "Zephyr (Female)" "Puck (Male)" "Aoede (Female)"; do
  belt app run pruna/p-video-avatar --input "{
    \"image\": \"https://portrait.jpg\",
    \"voice_script\": \"这彻底改变了我早晨的作息。五分钟就完成了。\",
    \"voice\": \"$voice\",
    \"voice_prompt\": \"随性、真实，像真实的用户评价\",
    \"video_prompt\": \"人物在明亮的厨房中对着镜头交谈\",
    \"resolution\": \"1080p\"
  }"
done
```

## 使用场景

- **UGC 与营销**：产品演示、AI 出镜的 UGC 风格广告
- **教育**：课程视频、解说
- **本地化**：基于单张图片跨 10 种语言配音
- **社交媒体**：一致的虚拟网红内容
- **企业**：培训视频、通知
- **游戏**：角色虚拟形象、NPC 对话

## 提示

- 使用高质量肖像照片（正面、光线良好）
- 音频应清晰，背景噪音 minimal
- P-Video-Avatar 支持内置 TTS —— 无需单独的语音生成步骤
- P-Video-Avatar 的输出比例与输入图片一致
- 使用 `9:16` 比例比使用 `pruna/p-image` 生成肖像，用于竖屏视频
- OmniHuman 1.5 支持一张图片中的多人
- LatentSync 最适合将现有视频与新音频同步

## 相关技能

```bash
# 专用 P-Video-Avatar 技能
npx skills add inference-sh/skills@p-video-avatar

# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 文本转语音（为无内置 TTS 的虚拟形象模型生成音频）
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

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用的说明
- [内容流程示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
- [流式结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
