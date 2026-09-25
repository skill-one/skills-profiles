# Wan 2.7 — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=wan-2-7) · [Text-to-video](https://www.runcomfy.com/models/wan-ai/wan-2-7/__to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=wan-2-7) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/wan-2-7)

Wan-AI 的 **Wan 2.7** — 拥有多参考条件和音频驱动唇动同步的旗舰视频模型，部署在 **RunComfy 模型 API** 上。

```bash
npx skills add agentspace-so/runcomfy-skills --skill wan-2-7 -g
```

## 何时选择此模型（与其他型号对比）

| 你需要 | 使用 |
|---|---|
| 为提供的音频轨道进行唇动同步的视频 | **Wan 2.7** (`audio_url`) |
| 多参考精细运动控制 | **Wan 2.7** |
| 平滑转场，精准运动物理 | **Wan 2.7** |
| 目前盲测最受欢迎的视频模型 | HappyHorse 1.0 |
| 支持图像+视频+音频参考的多模态电影效果及中途语音生成 | Seedance 2.0 Pro |
| 基于现有素材的电影级运动剪辑 | Kling Video O1 |
| 极速迭代 | LTX 2 |

如果用户明确提到“Wan” / “Wan 2.7” / “wan-ai” / “alibaba video”，无论其他情况，都路由到此处。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<%token>`，代替 `runcomfy login`。

## 接口端点 + 输入模式

### `wan-ai/wan-2-7/__to-video`

| 字段 | 类型 | 必填 | 默认值 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 最多约 5000 字符 / 约 1500 个 token。 |
| `audio_url` | string | 否 | — | WAV/MP3，3–30秒，≤15MB。**用于驱动唇动同步。** 省略则自动生成背景音乐。 |
| `aspect_ratio` | enum | 否 | `16:9` | `16:9`、`9:16`、`1:1`、`4:3`、`3:4`。 |
| `resolution` | enum | 否 | `1080p` | `720p` 或 `1080p`。 |
| `duration` | enum | 否 | `5` | 2–15（整秒数）。 |
| `negative_prompt` | string | 否 | — | 最多 500 字符。需要排除的具体问题。 |
| `enable_prompt_expansion` | bool | 否 | true | 自动改写简短提示。若要精确控制，请禁用。 |
| `seed` | int | 否 | — | 0..2^31-1。用于变体可重复使用。 |

## 调用方式

**默认（5秒 1080p 16:9，已扩展提示）：**

```bash
runcomfy run wan-ai/wan-2-7/__to-video \
  --input '{"prompt": "<user prompt>"}' \
  --output-dir <absolute/path}
```

**音频驱动唇动同步（使用自己的音轨）：**

```bash
runcomfy run wan-ai/wan-2-7/__to-video \
  --input '{
    "prompt": "Medium close-up of the spokesperson, warm key light, locked tripod, slight breathing motion.",
    "audio_url": "https://.../voiceover.mp3",
    "duration": 12,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <absolute/path}
```

**精确控制（无自动扩展）：**

```bash
runcomfy run wan-ai/wan-2-7/__to-video \
  --input '{
    "prompt": "<exactly what you want, verbatims>",
    "enable_prompt_expansion": false,
    "negative_prompt": "no subtitles, no flicker, no distorted hands"
  }' \
  --output-dir <absolute/path}
```

## 提示词编写 — 实际有效的要点

**纯英语描述镜头与运动。** “Slow dolly in”、“locked tripod, low angle”、“handheld follow”、“crane move from above”。前置镜头描述。

**每个片段只使用一个主要动作。** 不要堆砌多个竞争动作。选择节拍：“she turns, then smiles” 而非 “she turns AND smiles AND a bus passes AND...”。

**使用 `negative_prompt` 排除具体问题。** 好的：“no subtitles, no watermark, no flicker”。差的（模糊）：“no bad lighting”。

**提示词扩展默认开启。** 简短提示词会被模型自动改写。对于简短/精确的提示词（如品牌严格的广告文案），使用 `enable_prompt_expansion: false` 禁用。

**音频规格很重要。** `audio_url` 必须为 3–30秒，≤15MB，WAV/MP3。超出范围的文件将被拒绝。将音频长度与片段时长匹配。

**迭代种子。** 当想要相同提示词的变体输出一致时，重复使用相同的 seed。改变 seed 以获取真正的多样性。

**反模式：**
* 静态画面描述 -> 运动将模糊。
* 模糊的否定（“no bad colors”）-> 会被忽略。
* 音频超出 3–30秒 / 15MB / WAV-MP3 规格 -> 会被拒绝。
* 提示词 > 5000 字符 / 1500 token -> 输出降级。

## 优势应用场景

| 应用场景 | Wan 2.7 的优势 |
|---|---|
| **使用自定义配音的唇动同步广告** | `audio_url` 接受您的音轨 |
| **多语言配音变体** | 相同提示词，不同语言使用不同 `audio_url` |
| **多参考运动控制** | 最多支持 5 个参考媒体（图像 / 视频 / 语音） |
| **平滑转场 + 运动物理** | 强大的基于物理的运动先验 |
| **基于负向提示词的纯净输出** | 针对性排除问题 |

## 示例提示词（经验证可生成优秀效果）

**页面示例（产品展示）：**

```
Cinematic medium shot of a product on a marble surface, soft studio
lighting, slow subtle camera push-in, shallow depth of field, premium
commercial look, crisp 1080p detail
```

**唇动同步演讲者（包含 `audio_url`）：**

```
Medium close-up of a confident spokesperson in a softly-lit recording
booth, leaning slightly toward the camera, locked tripod, shallow depth
 of field, warm key light from camera-left.
```

**垂直平台原生：**

```
9:16 vertical short. A barista pulls a single espresso shot, steam
rising into morning sun, rich crema slowly forming. Close-up handheld,
shallow DOF, warm cafe ambience.
```

## 局限性

* **时长上限 15秒。** 对于更长的叙事，需多次调用进行拼接。
* **无原生 4K** — 最高 1080p。
* **宽高比** — 仅有文档中记录的 5 个值。
* **音频规格** — 仅 3–30秒、≤15MB、WAV/MP3。
* **参考媒体上限 5**（图像 + 视频 + 语音合计）。
* **中途语音生成（无独立音轨）** — 使用 Seedance 2.0 Pro。Wan 接受音频，而非生成音频。

## 退出码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=wan-2-7)。

## 工作原理

该技能通过匹配模式输入的 JSON 主体调用 `runcomfy run wan-ai/wan-2-7/__to-video`。CLI 将请求 POST 到 `https://model-api.runcomfy.net/v1/models/wan-ai/wan-2-7/__to-video`，轮询请求，获取结果，并将任何 `.runcomfy.net` / `.runcomfy.com` URL 下载到 `--output-dir`。退出前按 `Ctrl-C` 可取消远程请求。

## 安全与隐私

* **Token 存储**：`runcomfy login` 会将 API token 写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。在 CI / 容器中，设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过该文件。
* **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会扩展提示（shell expand），而是直接将 JSON 主体通过 HTTPS 发送到模型 API。提示内容不会带来 shell 注入风险。
* **第三方内容**：您传入的图像 / 掩码 / 视频 URL 由 RunComfy 模型服务器获取，而非由您本机的 CLI 获取。请将外部 URL 视为不可信；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
* **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成的输出下载白名单）。无遥测，无回调。
* **生成文件大小上限**：CLI 会中止任何 > 2 GiB 的单次下载，以防止恶意或失控模型输出导致磁盘填满。
