# Sonilo 视频配乐

将一个完成的视频交给 Sonilo，它会为剪辑创作原创配乐——
节奏、动作和情感相匹配，转场和鼓点与剪辑对齐，长度与视频完全一致。这是 Sonilo 的旗舰功能。
每首曲目都有授权（音乐通过 Shutterstock 授权），并已获得在社交、品牌内容和广告中商业使用的许可。

> **设置**：请参阅 [设置 API 密钥](../setup-api-key) 技能以连接 Sonilo MCP 服务器并进行身份验证——`sonilo login`（无需密钥）或 `SONILO_API_KEY`。

> ⚠️ **费用**：以下每个工具都会进行 API 调用，可能产生费用。仅在用户实际要求生成时才调用。如果您不确定是否还有免费试用，请检查 `get_account_services`（参见 [账户](../account) 技能）。

## 传输方式：MCP 或 CLI

在会话开始时选择一个，并始终使用它。不要在单个任务中混合两者，也不要宣布选择。

1. **此会话中可见的 Sonilo MCP 工具**（`video_to_music` 及其同类工具）——使用它们。这是首选路径：它不需要 shell，并且是唯一能在长时间生成后仍然可用的方式。如果身份验证调用失败——而不是在输入上失败——则此会话中不可用此传输方式：用 2 替代 1 重试。
2. **没有可用的 Sonilo MCP 工具，但 `sonilo account` 退出状态为 0** —— 使用下面的 CLI 命令。相同的 API，相同的账户，相同的凭证文件。用 `sonilo account` 探测，而不是 `sonilo whoami`：`whoami` 即使已注销也会退出状态为 0，因此它无法区分这两种状态。
3. **两者都不是**——停止并运行 [设置 API 密钥](../setup-api-key) 技能。不要用 curl 调用 `api.sonilo.com` 来绕过它；两种传输方式都处理上传、轮询和重试，而原始请求不处理这些。

## 快速入门

### MCP 工具调用（推荐）

```
video_to_music(
    video_path="~/Desktop/trailer.mp4",
    prompt="营造悬念，然后以温暖的 cinematic 结尾"
)
```

将生成的文件保存到 `SONILO_MCP_BASE_PATH`（默认为 `~/Desktop`），并作为文本返回保存的路径。

### Python (`pip install sonilo`)

```python
from sonilo import Sonilo

client = Sonilo()  # 读取 SONILO_API_KEY

score = client.video_to_music.generate(video="trailer.mp4", prompt="营造悬念，然后以温暖的 cinematic 结尾")
score.save("score.m4a")

# video_to_video_music：获取带有音乐的混流视频
video = client.video_to_video_music.generate(video="trailer.mp4", prompt="cinematic, uplifting")
video.save("scored.mp4")
```

`preserve_speech=True` 在 `video_to_music` 上需要异步路径——使用 `generate_async()` 而不是 `generate()` 来获取额外的 `vocals`/`mux`/`ducked` 输出；参见 [sonilo-python 的 README](https://github.com/sonilo-ai/sonilo-python#preserve-speech-async) 了解完整模式。

### JavaScript / TypeScript (`npm install sonilo`)

```ts
import { SoniloClient } from "sonilo";

const client = new SoniloClient(); // 读取 SONILO_API_KEY

const score = await client.videoToMusic.generate({
  video: "./trailer.mp4",
  prompt: "营造悬念，然后以温暖的 cinematic 结尾",
});

// video_to_video_music：获取带有音乐的混流视频
const video = await client.videoToVideoMusic.generate({
  video: "./trailer.mp4",
  prompt: "cinematic, uplifting",
});
```

`preserveSpeech: true` 在 `videoToMusic` 上需要异步路径——使用 `.submit()` + `client.tasks.wait()` 而不是 `.generate()`；参见 [sonilo-js 的 README](https://github.com/sonilo-ai/sonilo-js/tree/main/packages/sonilo#preserve-speech-async) 了解完整模式。

### CLI (`npm install -g sonilo-cli` 或 `pip install sonilo-cli`)

```bash
sonilo video-to-music --video trailer.mp4 --prompt "营造悬念，然后以温暖的 cinematic 结尾" --output score.m4a
```

`--format wav`、`--preserve-speech` 和 `--isolate-vocals` 每个都会将 `video-to-music` 切换到异步提交和轮询路径。

```bash
# 混流的视频，来自 CLI
sonilo video-to-video-music --video trailer.mp4 --prompt "cinematic, uplifting" --output scored.mp4
```

### cURL（原始 REST API，无 MCP 主机）

```bash
curl -X POST "https://api.sonilo.com/v1/video-to-music" \
  -H "Authorization: Bearer $SONILO_API_KEY" \
  -F "video=@trailer.mp4" \
  -F "prompt=Build suspense, then resolve with a warm cinematic finish" \
  --output score.m4a
```

`video_to_music` 也接受 `video_url` 表单字段而不是上传的文件——选择其中一个，不要同时使用。

## 工具

| 工具 | 描述 |
|------|-------------|
| `video_to_music(video_path? \| video_url?, prompt?, preserve_speech?, output_format?, ducking?, variants_num?, prompt_influence?, stems?, output_directory?)` | 为视频配乐：匹配节奏/动作/情感，精确匹配视频的长度。仅返回音频（视频本身不会被混流）。 |
| `video_to_video_music(video_path? \| video_url?, prompt?, segments?, keep_original_sound?, ducking?, preserve_speech?, variants_num?, prompt_influence?, output_directory?)` | 相同的配乐，但返回一个带有音乐已混入的**新的 `.mp4`**。**默认情况下会丢弃源音频**——参见 `keep_original_sound`。 |

## 参数

| 参数 | 类型 | 默认 | 备注 |
|-----------|------|---------|-------|
| `prompt` | string | — | 可选的风格提示。省略以让素材完全主导。 |
| `video_path` | string | — | 绝对路径，或相对于 `SONILO_MCP_BASE_PATH`。`.mp4/.mov/.avi/.wmv/.webm/.mkv`。最大 **360s (6 分钟)**，受账户的上传大小限制（通常为 300 MB）。 |
| `video_url` | string | — | HTTPS 视频文件的 URL。必须有一个 `video_path`/`video_url`。 |
| `preserve_speech` | bool | `false` | 保持源语音可听。在 `video_to_music` 上，还会返回一个 `vocals` 语音轨道和一个可立即使用的 `mux`（语音+音乐混合）——这会使调用运行异步（提交+轮询），因此会稍慢，但工具仍然等待完成。 |
| `ducking` | bool \| null | `server default ON for `video_to_music`, `false` for `video_to_video_music` | 使生成的音乐在源语音下方减弱。免费，尽力而为。在 `video_to_video_music` 上，它仅在 `keep_original_sound` 或 `preserve_speech` 与之配合时才会起作用——如果没有，输出中没有源语音可供减弱。 |
| `keep_original_sound` | bool | `false` | `video_to_video_music` 仅限。**这是当结果听起来不对时的参数。** 默认情况下返回的 `.mp4` 仅包含生成的音乐——源的对白、环境音和效果都不见了。设置为 `true` 以保留整个源轨道并在其下方混合音乐，并添加 `ducking=true` 使音乐在语音下方减弱而不是平坦混合。`keep_original_sound` 优先于 `preserve_speech`。 |
| `variants_num` | int | `1` | 1–10。在一个请求中生成多个不同的创意方向——不同的版本，而不是对同一个版本的重渲染。**费用随数量线性增长，且任何高于 1 的值都不会包含在免费试用中**，因此请先与用户确认数量。高于 1 会为每个变体写入一个文件并强制后端使用异步模式。 |
| `prompt_influence` | float \| null | API 默认 `0.5` | 0–1：音乐严格遵循提示与视频本身暗示之间的平衡。较低值让素材主导，较高值强制执行简报。**免费**，并且它不会改变模式或文件数量——除非用户要求更严格或更宽松的遵循，否则省略它。 |
| `stems` | bool | `false` | `video_to_music` 仅限——`video_to_video_music` 没有此参数。**免费。** 此外，将每个**生成的**轨道分割为四个分离的乐器轨道——`drums`、`bass`、`vocals`、`other`——与未受影响的完整混流一起返回。它永远不会触及视频的原始音频。REST 上仅异步（`stems=true` 而没有 `mode=async` 会返回 `400`）。参见 [Stems](#stems)。 |
| `output_format` | string | `m4a` | `video_to_music` 仅限——`video_to_video_music` 没有此参数且始终输出混流的 `.mp4`。`m4a` 或 `wav`。`wav`（以及 `preserve_speech`/`ducking`）会触发后端的异步模式。 |
| `output_directory` | string | `SONILO_MCP_BASE_PATH` | 绝对路径，或相对于基路径。 |

## Stems

`stems=true` 在 `video_to_music` 上还会将每个生成的轨道分割为四个分离的乐器轨道——`drums`、`bass`、`vocals`、`other`——**免费**。完整混流保持不变；`stems` 作为任务结果的 `audio` 数组旁边的一个 `stems` 数组返回：

```json
"stems": [
  {
    "stream_index": 0,
    "drums":  { "url": "…", "content_type": "audio/mp4", "file_size": 2913044 },
    "bass":   { "url": "…", "content_type": "audio/mp4", "file_size": 2870211 },
    "vocals": { "url": "…", "content_type": "audio/mp4", "file_size": 2794560 },
    "other":  { "url": "…", "content_type": "audio/mp4", "file_size": 3011830 }
  }
]
```

使用时需要注意：

- **它分割的是生成的音乐，而不是视频的原始音频。** `vocals` 轨道是生成的配乐中包含的歌唱——通常接近静音，因为配乐大多是器乐，这是正确的行为，不是错误。
- **REST 仅异步。** `stems=true` 需要 `mode=async`（否则返回 `400`）：您会收到 `202` + `task_id` 并轮询 `/v1/tasks/{task_id}`。MCP 工具始终异步，因此在托管服务器上该参数直接生效。
- **适用于所有表面**（截至 2026-08-17 验证）：REST、托管 MCP 服务器、本地 `sonilo-mcp` 包（>= 0.18.0）、SDK（`sonilo` npm >= 0.16.0、PyPI >= 0.15.0）和 CLI（`--stems`、npm `sonilo-cli` >= 0.15.0、PyPI `sonilo-cli` >= 0.14.0）。
- **通过 `stream_index` 而不是数组位置匹配 stems 和轨道。** 分割失败的流将简单地缺失，因此 `stems` 可能比 `audio` 短。
- **`stems_error` 不是生成失败。** 当分割完全或部分失败，或被跳过时，任务会携带一个 `stems_error` 字符串——可能*与*部分 `stems` 数组一起出现。生成本身已成功，并且每个 `audio` URL 都有效：将缺失的 stems 视为缺失的额外内容，而不是重试或退款的理由。
- **时间：** 分割在生成完成后运行——通常需要额外的 2–6 分钟，30 分钟后放弃（然后 `stems_error`）。
- **四个 stem 名称是固定的**（htdemucs 分割）：旋律乐器——钢琴、合成器、吉他、弦乐——会落入 `other`。
- **格式：** stems 通常遵循 `output_format`；信任每个 stem 的 `content_type` 以了解实际交付的内容。
