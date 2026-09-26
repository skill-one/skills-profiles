# Sonilo 音频压低

自动将音乐底轨在语音轨道下方进行压低：Sonilo 会降低语音说话区域的音乐音量，并在空白处恢复音乐音量，然后返回混合结果。语音输入可以是视频——其音频轨道被用作语音，压低后的混合音轨会重新 mux 到新视频中。

> **设置：** 请参考 [设置 API 密钥](../setup-api-key) 技能。

> ⚠️ **费用：** 会发起 API 调用，可能产生费用。仅在明确要求时调用。

## 传输方式：MCP 或 CLI

在会话开始时选择一种并保持使用。不要在单个任务中混合使用这两种方式，也不要宣布选择。

1. **本会话中可见的 Sonilo MCP 工具** (`audio_ducking` 及相关工具) —— 使用它们。这是推荐路径：无需 shell，并且是唯一能在长时间生成后仍然可用的方式。如果认证调用失败——而不是在输入上失败——此会话中此传输方式不可用：请选择 2 而不是重试它。
2. **没有可用的 Sonilo MCP 工具，但 `sonilo account` 返回 0** —— 使用下面的 CLI 命令。相同的 API，相同的账户，相同的凭证文件。使用 `sonilo account` 进行探测，而不是 `sonilo whoami`：即使注销，`whoami` 也会返回 0，因此无法区分这两种状态。
3. **两者都不是** —— 停止并运行 [设置 API 密钥](../setup-api-key) 技能。不要使用 curl 调用 `api.sonilo.com` 来绕过它；两种传输方式都处理上传、轮询和重试，而纯请求不处理这些。

## 快速入门

### MCP 工具调用（推荐）

```
audio_ducking(
    voice_path="~/Desktop/interview.mp4",
    music_path="~/Desktop/background-track.wav"
)
```

### Python (`pip install "sonilo>=0.13"`)

```python
from sonilo import Sonilo

client = Sonilo()  # 读取 SONILO_API_KEY

result = client.audio_ducking.generate(
    voice="interview.mp4",  # 音频或视频；也可以使用 voice_url=
    music="background-track.wav",  # 音频仅；也可以使用 music_url=
)
result.save("ducked.mp4" if result.output_type == "video" else "ducked.wav")
```

### JavaScript / TypeScript (`npm install sonilo@>=0.14`)

```ts
import { SoniloClient, download } from "sonilo";
import { writeFile } from "node:fs/promises";

const client = new SoniloClient(); // 读取 SONILO_API_KEY

const result = await client.audioDucking.generate({
  voice: "./interview.mp4", // 音频或视频；也可以使用 voiceUrl
  musicUrl: "https://example.com/background-track.wav", // 音频仅；也可以使用 music
});
await writeFile(
  result.output_type === "video" ? "ducked.mp4" : "ducked.wav",
  await download(result.output_url!),
);
```

### CLI (`npm install -g sonilo-cli` 或 `pip install sonilo-cli`)

```bash
sonilo audio-ducking --voice interview.mp4 --music-url https://example.com/background-track.wav
```

底层始终异步——CLI 会提交并轮询。`--voice`/`--voice-url` 和 `--music`/`--music-url` 必须各选择一个。默认输出名称遵循返回的内容 (`output.wav`，或当语音输入为视频时为 `output.mp4`)；`--output` 会覆盖它。本地 `--music` 文件必须具有音频扩展名——CLI 在前端会拒绝视频，原因与 MCP 工具相同。

### cURL（原始 REST API，无 MCP 主机）

```bash
curl -X POST "https://api.sonilo.com/v1/audio-ducking" \
  -H "Authorization: Bearer $SONILO_API_KEY" \
  -F "voice_file=@interview.mp4" \
  -F "music_file=@background-track.wav"
# -> {"task_id": "..."}  轮询 GET /v1/tasks/{task_id}
```

本地文件使用 `voice_file`/`music_file` 多部分字段；远程源使用 `voice_url`/`music_url` 表单字段（两种输入可以自由混合）。

## 工具

| 工具 | 描述 |
|------|-------------|
| `audio_ducking(voice_path? \| voice_url?, music_path? \| music_url?, output_directory?)` | 在 `voice` 下混合 `music`，自动在语音说话处压低音乐。 |

## 参数

| 参数 | 类型 | 备注 |
|-----------|------|-------|
| `voice_path` | string | 绝对路径，或相对于 `SONILO_MCP_BASE_PATH`。**音频或视频**：`.wav/.mp3/.m4a/.aac/.ogg/.flac` 或 `.mp4/.mov/.avi/.wmv/.webm/.mkv`。 |
| `voice_url` | string | 语音音频/视频的 HTTPS URL。`voice_path`/`voice_url` 必须选择一个。 |
| `music_path` | string | 绝对路径，或相对于基础路径。**音频仅**——此处视频不会被特殊处理，会导致错误处理。 |
| `music_url` | string | 音乐音频的 HTTPS URL。`music_path`/`music_url` 必须选择一个。 |
| `output_directory` | string | 默认为 `SONILO_MCP_BASE_PATH`。 |

每个输入限制为 **360 秒（6 分钟）**，并由账户的上传大小限制（通常为 300 MB）限制。

## 工作流提示

- **此工具需要两个已存在的音轨**——它不会自己生成音乐或 SFX。如果你需要先生成音乐底轨，使用 [文本转音乐](../text-to-music) 或 [视频转音乐](../video-to-music) 技能 (`text_to_music`/`video_to_music`)，然后将结果作为 `music_path` 输入到这里。
- **语音输入可以是视频。** 如果用户给你一个说话头片段或访谈和单独的音乐文件，直接将视频作为 `voice_path` 传入——Sonilo 会提取其音频轨道，在下方压低音乐，并将压低后的混合音轨自动重新 mux 到新视频中。
- **优先选择 [视频转音效](../video-to-sound) 或 `video_to_music(ducking=true)`** 当音乐本身也正在为同一视频生成时——这些工具在生成过程中内部会压低，因此你不需要单独的压低调用。当音乐轨道是固定/外部时，只需要混合，请专门使用 `audio_ducking`。

## 恢复超时的调用

此工具在后台提交异步任务。如果调用超时，错误会包含 `task_id`——任务仍在运行（已收费）。稍后调用 `get_sfx_task(task_id)`（在托管服务器上为 `get_generation_task(task_id)`）；参见 [任务恢复](../task-recovery)。

## 输出文件

单个文件：如果语音输入为音频，则为 `.wav`；如果语音输入为视频，则为 `.mp4`（压低后的混合音轨重新 mux 在内）。以语音输入命名（例如 `interview.mp4` → `interview-ducked.mp4`），如果失败则回退到 `ducked-<任务 ID 的前 8 个字符`。

## 错误处理

常见错误：`401` 无效密钥，`402` 余额不足/试用用尽，`413` 文件过大，`422` 无效参数，`429` 速率限制。参见 [账户](../account) 技能。
