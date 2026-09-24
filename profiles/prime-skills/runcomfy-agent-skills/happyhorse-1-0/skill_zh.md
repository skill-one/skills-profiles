# HappyHorse 1.0 — RunComfy 上的专业版

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=happyhorse-1-0) · [Text-to-video](https://www.runcomfy.com/models/happyhorse/happyhorse-1-0/tagged-transformers-text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=happyhorse-1-0) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/happyhorse-1-0)

**HappyHorse 1.0** — 目前 Artificial Analysis Video Arena 排名第一（Elo 1333 t2v / 1392 i2v）— 托管于 **RunComfy Model API**。原生 1080p 视频，具备 **同流程同步音频**（对话、环境音、音效），以及多镜头角色一致性。

```bash
npx skills add agentspace-so/runcomfy-skills --skill happyhorse-1-0 -g
```

## 何时选择此模型（与同类模型对比）

| 你需要 | 使用 |
|---|---|
| 多镜头故事，角色 / 服饰保持一致 | **HappyHorse 1.0** |
| 同生成流程内原生音频 | **HappyHorse 1.0** |
| 当前盲投排名第一的视频模型 | **HappyHorse 1.0** |
| 详细唇形同步对话 + 参考视频 | Seedance 2.0 Pro |
| 精细动作控制 + 多参考条件控制 | Wan 2.7 |
| 极快迭代（单帧亚秒级） | LTX 2 |
| 对已有素材进行电影级动作剪辑 | Kling Video O1 |

若用户明确使用了“HappyHorse” / “happy horse video”，无论何种情况都应路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账号** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 使用 `RUNCOMFY_TOKEN=<token>` 替代 `runcomfy login`。

## 端点与输入 schema

### `happyhorse/happyhorse-1-0/tagged-transformers-text-to-video`

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 最多 2,500 字符，支持 6 种语言（CN/EN/JP/KR/DE/FR）。 |
| `aspect_ratio` | enum | 否 | `16:9` | 仅支持 `16:9`、`9:16`、`1:1`、`4:3`、`3:4`。 |
| `resolution` | enum | 否 | `1080P` | `720P` 或 `1080P`。 |
| `duration` | int | 否 | 5 | 3–15 秒。 |
| `seed` | int | 否 | 0 | 0 到 2^31-1 之间的整数，可用于变体对比。 |
| `watermark` | bool | 否 | true | Provider 水印。 |

## 调用方式

**默认（16:9 1080p 5 秒）：**

```bash
runcomfy run happyhorse/happyhorse-1-0/tagged-transformers-text-to-video \
  --input '{"prompt": "<user prompt>"}' \
  --output-dir <absolute/path>`
```

**垂直短（9:16，8 秒，无水印）：**

```bash
runcomfy run happyhorse/happyhorse-1-0/tagged-transformers-text-to-video \
  --input '{
    "prompt": "<user prompt>",
    "aspect_ratio": "9:16",
    "duration": 8,
    "watermark": false
  }' \
  --output-dir <absolute/path>`
```

**更经济的测试轮次（720p）：**

```bash
runcomfy run happyhorse/happyhorse-1-0/tagged-transformers-text-to-video \
  --input '{"prompt": "<user prompt>", "resolution": "720P", "duration": 3}' \
  --output-dir <absolute/path>`
```

CLI 会提交请求，每 2 秒轮询直到完成，然后将结果中的 `*.runcomfy.net` / `*.runcomfy.com` URL 下载到 `--output-dir`。标准输出为结果 JSON，标准错误为进度信息。

## Prompt 提示词 —— 真正有效的写法

**按时间顺序描述动作，而非静态画面。** “一位女士从窗户转过身，走两步到桌边，拿起杯子，抬到嘴边，喝一口” 优于 “一位女士在喝咖啡”。

**用普通英文交代镜头与机位。** 将镜头前置：`"Wide shot. ..."` / `"Tracking shot. ..."` / `"Locked tripod, low angle. ..."` 可作为真实的指令。指定镜头质感：`"35mm anamorphic"`、`"shallow DOF"`、`"crushed shadows"`。

**迭代时每段剪辑只聚焦一个视觉动作。** 不要堆叠“她走 AND 狗跑 AND 车经过”。先锁定一个动作并做到清晰，再通过多镜头提示词叠加。

**多镜头一致性** —— 描述两个动作时，在每个镜头中重新陈述锚点：`"Shot 1: tall woman in red wool coat, blue scarf, in a rainy alley. Shot 2: same woman in red coat / blue scarf, now ducking under an awning."` HappyHorse 能保持形象，但需要锚点。

**音频方向** —— 说明你希望听到什么：`"distant temple bells, footsteps on wet pavement, no dialogue"` 或 `"warm friendly tone, English"`。

**反面模式：**
- 静态画面描述（无时间性动词）→ 动作会显得模糊。
- 风格方向冲突 → 会相互抵消。
- 提示词超过 2,500 字符 → 会退化。
- 使用不支持的比例 → 返回 422。

## 适用场景与优势

| 适用场景 | HappyHorse 1.0 的优势 |
|---|---|
| **单角色多镜头品牌故事** | 原生跨镜头身份保持 |
| **需要片内旁白 + 环境音的口播讲解** | 同流程同步音频 |
| **多语言短视频广告** | 6 种提示词语言，无脚本质量下降 |
| **电影级 1080p 交付** | 原生 1080p 输出，可直接用于播出 |
| **通用视频质量的盲投领先者** | Artificial Analysis Video Arena 排名第一 |

## 示例提示词（经验证可产出优质效果）

### 来自模型页面（电影级场景）：

```
Wide shot. A lone astronaut in dusty orange suit with blue-gray harness
skis across lunar plain, leaving parallel tracks in gray regolith.
Mid-stride, poles planted, pushing in 1/6th gravity with subtle upward
drift. Fine dust haze along ski tracks. Crescent Earth above lunar
horizon, blue-white glow against black sky. Raw sunlight, crushed
shadows, no fill. 8K photorealistic.
```

**多镜头一致性：**

```
Shot 1: Medium close-up. A woman in a navy trench coat enters a
rain-slick neon-lit Tokyo alley, looks left, holds up an umbrella.
Shot 2: Same woman in same navy trench, now under the awning of a
ramen shop, shaking water off the umbrella. Warm interior glow, soft
chatter, gentle rain on metal roof in the audio.
```

**垂直平台原生：**

```
9:16 vertical short. A barista in a black apron pulls a single
espresso shot, steam rising into the morning sun, rich crema slowly
forming. Close-up handheld, shallow DOF, warm cafe ambience and the
hiss of the steam wand.
```

## 局限性

- **时长上限 15 秒** —— 对于更长的叙事，可拆分为多镜头提示词并进行拼接。
- **比例** —— 仅支持文档中列出的 5 种值；超宽电影感画面会被裁剪或拒绝。
- **音频仅同流程** —— 无法通过外部音频驱动唇形同步。需要音频驱动唇形同步时，请使用 Wan 2.7（支持 `audio_url`）或 Seedance 2.0 Pro。
- **本模板不支持免费图像转视频** —— HappyHorse 通过独立流水线支持 i2v；此处的 t2v 端点仅支持文本输入。

## 退出码

`runcomfy` CLI 使用 sysexits 风格的退出码：

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / schema 不匹配（例如 `duration: 30` 会返回 422） |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=happyhorse-1-0)。

## 工作原理

1. 该 skill 调用 `runcomfy run happyhorse/happyhorse-1-0/tagged-transformers-text-to-video`，并传入符合 schema 的 JSON 请求体。
2. CLI 使用用户的 Bearer token 向 `https://model-api.runcomfy.net/v1/models/happyhorse/happyhorse-1-0/tagged-transformers-text-to-video` POST 提交请求。
3. Model API 返回 `request_id`；CLI 每 2 秒轮询 `GET .../requests/<id>/status`。
4. 当轮询状态变为终态时，CLI 获取 `GET .../requests/<id>/result`，并将主机名以 `.runcomfy.net` 或 `.runcomfy.com` 结尾的任何 URL 下载到 `--output-dir`。其他 URL 仅列出但不会下载。
5. 轮询时按 `Ctrl-C` 会发送 `POST .../requests/<id>/cancel`，避免为已停止的 GPU 产生计费。

## 本技能非

不是自托管视频运行器。不是能力授予 —— 取决于正常的 RunComfy 账号。

## 安全与隐私

- **Token 存储**：`runcomfy login` 将 API token 以 mode 0600（仅所有者可读写）写入 `~/.config/runcomfy/token.json`。在 CI / 容器中可通过设置 `RUNCOMFY_TOKEN` 环境变量完全绕过该文件。
- **输入边界**：用户提示词通过 `--input` 作为 JSON 字符串传递给 CLI。CLI 不会进行 shell 展开，而是直接将 JSON 请求体通过 HTTPS 传输给 Model API。提示词内容不存在 shell 注入风险。
- **第三方内容**：你传入的图片 / 蒙版 / 视频 URL 由 RunComfy 模型服务器获取，而非由本机 CLI 获取。请将外部 URL 视为不可信；对于任何图像编辑 / 视频编辑模型，图像驱动的提示词注入是已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测数据，无回调。
- **生成文件大小上限**：CLI 会中止任何单个下载超过 2 GiB 的操作，以防止恶意或失控模型输出导致磁盘填充。
