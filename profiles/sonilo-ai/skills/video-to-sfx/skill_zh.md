# Sonilo 视频转音效

将视频交给 Sonilo，它会根据视频内容生成匹配的音效——脚步声、撞击声、环境音、UI 音效，无论场景需要什么——或者使用 `segments` 将特定音效固定在特定时刻。生成过程在后台异步运行；工具会内部轮询并返回保存的文件。

> **设置：** 请参考 [设置 API 密钥](../setup-api-key) 技能。
>
> ⚠️ **费用：** 以下每个工具都会发起 API 请求，可能产生费用。仅在明确要求时才调用。

## 传输方式：MCP 或 CLI

会话开始时选择一种方式并保持使用，不要在单个任务中混合使用这两种方式，也不要宣布选择。

1. **当前会话中可见的 Sonilo MCP 工具**（`video_to_sfx` 及相关工具）——使用它们。这是推荐的方式：无需 shell，并且是唯一能在长时间生成后仍然工作的方式。如果认证调用失败——而不是输入错误——则此会话中无法使用此传输方式：请选择 2 而不是重试。
2. **没有可用的 Sonilo MCP 工具，但 `sonilo account` 返回 0** —— 使用以下 CLI 命令。相同的 API，相同的账户，相同的凭证文件。使用 `sonilo account` 进行探测，而不是 `sonilo whoami`：`whoami` 即使未登录也会返回 0，因此无法区分这两种状态。
3. **两者都不是** —— 停止并运行 [设置 API 密钥](../setup-api-key) 技能。不要使用 curl 调用 `api.sonilo.com` 来绕过此问题；两种传输方式都处理上传、轮询和重试，而原始请求则不处理。

## 快速入门

### MCP 工具调用（推荐）

```python
video_to_sfx(
    video_path="~/Desktop/action-scene.mp4",
    prompt="碎石上的脚步声、远处交通声、关门声"
)
```

### Python (`pip install sonilo`)

```python
from sonilo import Sonilo

client = Sonilo()  # 读取 SONILO_API_KEY

foley = client.video_to_sfx.generate(video="action-scene.mp4", prompt="碎石上的脚步声、远处交通声、关门声")
foley.save("foley.wav")

# video_to_video_sfx：获取带有音效的回放视频
video = client.video_to_video_sfx.generate(video="action-scene.mp4", segments=[{"start": 0, "end": 2, "prompt": "碎石上的脚步声"}])
video.save("with_sfx.mp4")
```

### JavaScript / TypeScript (`npm install sonilo`)

```ts
import { SoniloClient } from "sonilo";

const client = new SoniloClient(); // 读取 SONILO_API_KEY

const foley = await client.videoToSfx.generate({
  video: "./action-scene.mp4",
  prompt: "碎石上的脚步声、远处交通声、关门声",
});

// video_to_video_sfx：获取带有音效的回放视频
const video = await client.videoToVideoSfx.generate({
  video: "./action-scene.mp4",
  segments: [{ start: 0, end: 2, prompt: "碎石上的脚步声" }],
});
```

### CLI (`npm install -g sonilo-cli` 或 `pip install sonilo-cli`)

```bash
sonilo video-to-sfx --video action-scene.mp4 --output foley.wav
```

底层始终异步运行——CLI 会自动提交并轮询。`--format` 接受 `wav|mp3|aac|flac`。

```bash
# 带有音效的回放视频，来自 CLI
sonilo video-to-video-sfx --video clip.mp4 --prompt "脚步声、远处雷声" --output foley.mp4
```

### cURL（原始 REST API，无 MCP 主机）

```bash
curl -X POST "https://api.sonilo.com/v1/video-to-sfx" \
  -H "Authorization: Bearer $SONILO_API_KEY" \
  -F "video=@action-scene.mp4" \
  -F "prompt=碎石上的脚步声、远处交通声、关门声"
# -> {"task_id": "..."}  轮询 GET /v1/tasks/{task_id} 直到状态为成功/失败
```

每次调用都是基于任务的：端点返回 `{"task_id": ...}`（HTTP 202），结果从 `GET /v1/tasks/{task_id}` 获取，一旦 `status` 为最终状态。MCP 工具会为你进行轮询并直接返回保存路径——只有在调用超时时才会看到 `task_id`（见 [任务恢复](../task-recovery)）。

## 工具

| 工具 | 描述 |
|------|------|
| `video_to_sfx(video_path? \| video_url?, prompt?, segments?, audio_format?, output_directory?)` | 生成与视频匹配的音效。返回 **仅音频**（不返回源视频）。 |
| `video_to_video_sfx(video_path? \| video_url?, prompt?, segments?, output_directory?)` | 相同，但返回带有音效的 **新 .mp4**。 |

## 参数

| 参数 | 类型 | 默认值 | 备注 |
|------|------|--------|------|
| `prompt` | 字符串 | — | 可选的整体描述（最多 2000 字符）——省略它让 Sonilo 自行解析视频。 |
| `video_path` | 字符串 | — | `.mp4/.mov/.webm/.m4v/.gif`（gif 必须是动画）——比音乐工具更窄的范围。最大 **180s（3 分钟）**，受账户的上传大小限制。 |
| `video_url` | 字符串 | — | HTTPS/HTTP 视频链接。`video_path`/`video_url` 必须且仅有一个。 |
| `segments` | list[dict] | — | 脚本特定时间段的音效：`[{"start": float, "end": float, "prompt": str}, ...]`。见下文规则。最多 30 个片段。 |
| `audio_format` | 字符串 | `aac`（`.m4a`） | `wav`, `mp3`, `aac`, 或 `flac`。`video_to_sfx` 仅（`video_to_video` 始终输出 `.mp4`）。 |
| `output_directory` | 字符串 | `SONILO_MCP_BASE_PATH` | 绝对路径，或相对于基本路径。 |

### `segments` 规则

在产生费用前由后端验证——无效列表会被 422/400 拒绝且不产生费用：

- 第一个片段的 `start` 必须为 `0`。
- 片段必须连续：每个 `end` 必须等于下一个片段的 `start`。
- 每个 `end` 必须大于其 `start`。
- 每个 `prompt` 必须非空，最多 200 字符。
- 最后一个 `end` 不能超过视频的实际时长。
- 最多 30 个片段。

## 提示

无需提示——模型会读取剪辑。质量来自时间分段的动作图：屏幕上是什么，由什么组成，做什么，每秒。素材是真相来源。

在付费调用前：探测确切时长和现有音频，尊重 **180 秒** 限制（超出 = 422 拒绝，不会截断），并获得批准——失败运行会自动退款，但你的重试会是一笔新费用。

- 完整预检（检查视频、限制、信用、验证）：[参考资料/预检.md](../references/preflight.md)
- 动作图制作（场景底板、音效包、材料词汇、片段规则）：[参考资料/sfx-prompting.md](../references/sfx-prompting.md)

## 工作流程提示

- **不设置 `prompt`/`segments`** 让 Sonilo 读取整个视频并自行决定；使用 `segments` 当你需要特定音效固定在特定时刻（例如 2.3 秒的拳头声，5.0 秒的门关声）。
- **需要带有音效的视频回放？** 使用 `video_to_video_sfx` 而不是 `video_to_sfx`。
- **提示：** 具体且组合元素——"雨打铁屋顶" 比 "雨" 更好。
- **不要与音乐混淆。** 对于背景音乐或配乐，使用 [视频转音乐](../video-to-music) 而不是。要生成音乐和音效，使用 [视频转音效](../video-to-sound) 在一次平衡的单次费用调用中生成。

- **没有素材？** [文本转音效](../text-to-sfx) 仅从描述生成单个片段。
- **不知道应该是什么声音？** 先运行 [视频分析](../video-analysis)：一次调用返回从素材读取的声音设计简报——按镜头大小的 `sfx_segments` 加上可用的整片段 `sfx_prompt`（以及音乐简报，除非你传递 `mode="sfx"`）——比猜测提示和重试更好。这是一个不产生结果的付费调用，因此仅在简报确实不明确时使用——而不是当用户已经告诉你他们想要什么时。

## 恢复超时的调用

这里每个工具在后台都是异步的；长时间生成仍可能超过 `TIME_OUT_SECONDS`。如果超出，错误会携带 `task_id`——任务仍在运行（且已收费）。稍后调用 `get_sfx_task(task_id)`——`get_generation_task(task_id)` 在托管服务器上——以获取结果；见 [任务恢复](../task-recovery)。

## 输出文件

- `video_to_sfx`：以请求的 `audio_format`（`.wav`/`.mp3`/`.flac`，或 `aac` 默认的 `.m4a`）保存，从提示命名（转换为短链接）或 `sfx-<任务 ID 的前 8 个字符>`。
- `video_to_video_sfx`：一个带有音效的 `.mp4`。

## 错误处理

常见错误：`401` 无效密钥，`402` 余额不足/试用用尽，`413` 文件过大，`422` 无效参数或格式化的 `segments`，`429` 速率限制。见 [账户](../account) 技能。
