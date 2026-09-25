# ElevenLabs 音乐生成

从文本提示生成音乐 - 支持纯器乐曲目、带歌词的歌曲，以及通过作曲计划进行细粒度控制。

> **设置**：请参阅[安装指南](references/installation.md)。对于 JavaScript，仅使用 `@elevenlabs/*` 包。

以下所有示例默认使用 `music_v2`，即当前的生成模型。仅在明确要求时才传递 `model_id="music_v1"`。

## 快速入门

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.compose(
    prompt="一段轻松的低保真嘻哈节拍，带有爵士钢琴和弦",
    music_length_ms=30000,
    model_id="music_v2",
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";

const client = new ElevenLabsClient();
const audio = await client.music.compose({
  prompt: "一段轻松的低保真嘻哈节拍，带有爵士钢琴和弦",
  musicLengthMs: 30000,
  modelId: "music_v2",
});
audio.pipe(createWriteStream("output.mp3"));
```

### CLI

```bash
elevenlabs music compose \
  --prompt "一段轻松的低保真节拍" \
  --music-length-ms 30000 \
  --model-id music_v2 \
  --output output.mp3
```

## 方法

| 方法 | 描述 |
|--------|-------------|
| `music.compose` | 从提示或作曲计划生成音频 |
| `music.stream` | 作为生成时流式传输音频块（付费计划） |
| `music.composition_plan.create` | 生成用于细粒度控制的结构化计划 |
| `music.compose_detailed` | 生成音频+作曲计划+元数据；传递 `store_for_inpainting=True` 以启用修复 |
| `music.compose_detailed_stream` | 流式传输音频+作曲计划、元数据以及可选的单词时间戳作为服务器发送事件 |
| `music.video_to_music` | 从一个或多个上传的视频文件生成背景音乐 |
| `music.upload` | 上传音频文件以供后续修复工作流使用，可选提取其作曲计划或单词级时间戳 |
| `music.finetunes.list` | 列出可访问的音乐微调 |
| `music.finetunes.create` | 从上传的音频训练音乐微调 |
| `music.finetunes.get` | 检索微调状态和元数据 |
| `music.finetunes.update` | 更新微调元数据或可见性 |
| `music.finetunes.delete` | 删除音乐微调 |

有关完整参数详情，请参阅[API 参考](references/api_reference.md)。

`music.upload` 可供具有修复功能访问权限的企业客户使用。

## 音乐微调

使用
[`POST /v1/music/finetunes`](https://elevenlabs.io/docs/api-reference/music/finetunes/create)
创建微调，然后轮询[获取端点](https://elevenlabs.io/docs/api-reference/music/finetunes/get)直到其状态为 `completed`。在生成音乐时将返回的 `id` 作为 `finetune_id` 传递。

使用[列表](https://elevenlabs.io/docs/api-reference/music/finetunes/list)、[更新](https://elevenlabs.io/docs/api-reference/music/finetunes/update)和
[删除](https://elevenlabs.io/docs/api-reference/music/finetunes/delete)端点管理可访问的微调。

## 视频转音乐

通过
[`POST /v1/music/video-to-music`](https://elevenlabs.io/docs/api-reference/music/video-to-music)
(`client.music.video_to_music`)从上传的视频片段生成背景音乐。这与基于提示的
[`music.compose`](https://elevenlabs.io/docs/api-reference/music/compose) (`POST /v1/music`)不同。

API 按顺序组合视频，接受可选的自然语言描述，并允许您使用最多 10 个标签（如 `upbeat` 或 `cinematic`）来引导风格。此端点仍然默认为 `music_v1`；传递 `model_id="music_v2"` 以使用较新的模型。

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.video_to_music(
    videos=["trailer.mp4"],
    description="营造悬念，然后以温暖的影视结尾解决。",
    tags=["cinematic", "suspenseful", "uplifting"],
    model_id="music_v2",
)

with open("video-score.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audio = await client.music.videoToMusic({
  videos: [createReadStream("trailer.mp4")],
  description: "营造悬念，然后以温暖的影视结尾解决。",
  tags: ["cinematic", "suspenseful", "uplifting"],
  modelId: "music_v2",
});

audio.pipe(createWriteStream("video-score.mp3"));
```

### CLI

```bash
elevenlabs music video_to_music \
  --videos trailer.mp4 \
  --description "营造悬念，然后以温暖的影视结尾解决。" \
  --tags cinematic \
  --model-id music_v2 \
  --output video-score.mp3
```

CLI 目前接受每个请求一个 `--videos` 文件和一个 `--tags` 值；使用 Python 或 TypeScript SDK 发送多个视频或标签。

当前 API 模式的约束：

- 每个请求上传 1-10 个视频文件
- 保持总组合上传大小在 200 MB 或以下
- 保持总组合视频时长在 600 秒或以下
- 使用 `description` 进行高级音乐方向指引，使用 `tags` 进行简洁的风格提示

## 作曲计划

`music_v2` 作曲计划是一个有序的 `chunks` 列表。每个块指定自己的 `text`（部分标签、歌词、内联提示）、`duration_ms`、`positive_styles`、`negative_styles` 和 `context_adherence`（`low`、`medium` 或 `high`，默认 `high`）。每个计划最多 30 个块，每个块 3,000–120,000 ms，总长度 3 秒到 10 分钟。

首先生成计划，然后编辑，最后作曲：

```python
plan = client.music.composition_plan.create(
    prompt="一段史诗级的管弦乐，逐渐达到高潮",
    music_length_ms=60000,
    model_id="music_v2",
)

# 原地编辑块
plan["chunks"][0]["text"] = "[Intro]\n轻柔的弦乐渐强"

audio = client.music.compose(
    composition_plan=plan,
    model_id="music_v2",
)
```

```typescript
const plan = await client.music.compositionPlan.create({
  prompt: "一段史诗级的管弦乐，逐渐达到高潮",
  musicLengthMs: 60000,
  modelId: "music_v2",
});

plan.chunks[0].text = "[Intro]\n轻柔的弦乐渐强";

const audio = await client.music.compose({
  compositionPlan: plan,
  modelId: "music_v2",
});
```

或者手动构建计划以控制每个部分的歌词和风格：

```python
composition_plan = {
    "chunks": [
        {
            "text": "[Verse]\n走在一条空荡荡的街道上",
            "duration_ms": 15000,
            "positive_styles": ["流行", "欢快", "女声", "原声吉他"],
            "negative_styles": ["黑暗", "缓慢"],
            "context_adherence": "high",
        },
        {
            "text": "[Chorus]\n这是我的时刻",
            "duration_ms": 15000,
            "positive_styles": ["强大的声音", "完整乐队"],
            "negative_styles": [],
            "context_adherence": "high",
        },
    ]
}

audio = client.music.compose(composition_plan=composition_plan, model_id="music_v2")
```

```typescript
const compositionPlan = {
  chunks: [
    {
      text: "[Verse]\n走在一条空荡荡的街道上",
      durationMs: 15000,
      positiveStyles: ["流行", "欢快", "女声", "原声吉他"],
      negativeStyles: ["黑暗", "缓慢"],
      contextAdherence: "high",
    },
    {
      text: "[Chorus]\n这是我的时刻",
      durationMs: 15000,
      positiveStyles: ["强大的声音", "完整乐队"],
      negativeStyles: [],
      contextAdherence: "high",
    },
  ],
};

const audio = await client.music.compose({
  compositionPlan,
  modelId: "music_v2",
});
```

将更广泛的特征（流派、乐器、人声风格）放在 `positive_styles` 中，而不是放在 `text` 中。第一个块的样式设定整体基调——在那里包含 6–7 个样式。

## 输出格式

在 compose、detailed compose 或 stream 请求上使用 `output_format` 查询参数来选择生成的音频格式。`auto` 选择适合模型的 MP3 格式；对于 `music_v2`，它选择 `mp3_48000_192`。更高比特率的 MP3 选项包括 `mp3_48000_240` 和 `mp3_48000_320`。

## 流式传输

对于付费计划，流式传输生成的音频块，而不是等待完整文件：

```python
from io import BytesIO

stream = client.music.stream(
    prompt="一段驱动力的合成器浪潮曲目，带有琶音主音",
    music_length_ms=30000,
    model_id="music_v2",
)

buffer = BytesIO()
for chunk in stream:
    if chunk:
        buffer.write(chunk)
```

```typescript
const stream = await client.music.stream({
  prompt: "一段驱动力的合成器浪潮曲目，带有琶音主音",
  musicLengthMs: 30000,
  modelId: "music_v2",
});

const chunks: Buffer[] = [];
for await (const chunk of stream) {
  chunks.push(chunk);
}
```

### 详细流式传输

当应用程序在音频仍在到达时需要生成的音乐元数据时，使用详细流式传输。`POST /v1/music/detailed/stream` 接受与 detailed compose 相同的提示或作曲计划正文，流式传输 `text/event-stream`，并且可以通过 `with_timestamps` 包含单词时间戳。

```bash
elevenlabs music compose_detailed_stream \
  --prompt "一段明亮的独立流行钩子，带有温暖的吉他" \
  --music-length-ms 30000 \
  --model-id music_v2 \
  --with-timestamps true \
  --output-format auto
```

## 修复

修复通过在单个作曲计划中混合**音频参考块**（存储歌曲的不变切片）和新的**生成块**来编辑或扩展存储的歌曲。

步骤 1 — 获取 `song_id`，可以通过存储新的生成或上传现有音频来获取：

```python
# 选项 A：保留生成以供后续编辑
result = client.music.compose_detailed(
    prompt="一段欢快的流行歌曲，有主歌和副歌",
    music_length_ms=60000,
    model_id="music_v2",
    store_for_inpainting=True,
)
song_id = result.song_id

# 选项 B：上传现有曲目并提取其计划
uploaded = client.music.upload(
    file=open("my-song.mp3", "rb"),
    extract_composition_plan="music_v2",
)
song_id = uploaded.song_id
composition_plan = uploaded.composition_plan
```

```typescript
import { createReadStream } from "fs";

// 选项 A：保留生成以供后续编辑
const result = await client.music.composeDetailed({
  prompt: "一段欢快的流行歌曲，有主歌和副歌",
  musicLengthMs: 60000,
  modelId: "music_v2",
  storeForInpainting: true,
});
let songId = result.songId;

// 选项 B：上传现有曲目并提取其计划
const uploaded = await client.music.upload({
  file: createReadStream("my-song.mp3"),
  extractCompositionPlan: "music_v2",
});
songId = uploaded.songId;
const compositionPlan = uploaded.compositionPlan;
```

步骤 2 — 构建一个计划，该计划引用存储的音频并重新生成您想要更改的部分：

```python
plan = {
    "chunks": [
        {"song_id": song_id, "range": {"start_ms": 0, "end_ms": 30000}},
        {
            "text": "[Chorus]\n我们今晚崛起",
            "duration_ms": 30000,
            "positive_styles": ["更大的鼓", "分层人声", "史诗般的"],
            "negative_styles": ["稀疏"],
            "context_adherence": "high",
        },
    ]
}

audio = client.music.compose(composition_plan=plan, model_id="music_v2")
```

```typescript
const plan = {
  chunks: [
    { songId, range: { startMs: 0, endMs: 30000 } },
    {
      text: "[Chorus]\n我们今晚崛起",
      durationMs: 30000,
      positiveStyles: ["更大的鼓", "分层人声", "史诗般的"],
      negativeStyles: ["稀疏"],
      contextAdherence: "high",
    },
  ],
};

const audio = await client.music.compose({
  compositionPlan: plan,
  modelId: "music_v2",
});
```

要匹配存储切片的感觉而不复制它，将一个 `conditioning_ref`（最多 30,000 ms）加上 `condition_strength` 为 `low`、`medium`、`high` 或 `xhigh` 连接到生成块。放在第一个块上的条件会影响所有后续块。

有关完整修复参数列表，请参阅[API 参考](references/api_reference.md)。

## 内容限制

- 不能引用特定艺术家、乐队或受版权保护的歌词
- `bad_prompt` 错误包括一个 `prompt_suggestion`，其中包含替代措辞
- `bad_composition_plan` 错误包括一个 `composition_plan_suggestion`

## 错误处理

```python
try:
    audio = client.music.compose(prompt="...", music_length_ms=30000)
except Exception as e:
    print(f"API 错误: {e}")
```

```typescript
try {
  const audio = await client.music.compose({
    prompt: "...",
    musicLengthMs: 30000,
  });
} catch (err) {
  console.error("API 错误:", err);
}
```

常见错误：401（无效密钥）、422（无效参数）、429（速率限制）。

## 参考

- [安装指南](references/installation.md)
- [API 参考](references/api_reference.md)
