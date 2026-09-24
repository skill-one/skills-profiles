# Image-to-Video — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [HappyHorse I2V](https://www.runcomfy.com/models/happyhorse/happyhorse-1-0/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [Wan 2.7](https://www.runcomfy.com/models/wan-ai/wan-2-7/ text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [Seedance 2.0 Pro](https://www.runcomfy.com/models/bytedance/seedance-v2/pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/image-to-video)

**意图驱动的 Image-to-Video。** 该技能不会将你锁定在某个模型上——它会根据用户的实际需求，在 RunComfy 目录中选择合适的 i2v 模型：包括人像动画、自定义配音口型同步、多模态组合等。

```bash
npx skills add agentspace-so/runcomfy-skills --skill image-to-video -g
```

## 根据用户意图选择合适模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 动画化人像——保持身份稳定 | **HappyHorse 1.0 I2V** | 人工智能分析竞技场（Artificial Analysis Arena）排名 #1（Elo 1392）；面部保真度高 |
| 产品发布 / 360° / 微距运镜 | **HappyHorse 1.0 I2V** | 几何形变保持 + 流畅的镜头运动 |
| 单次生成原生同步的环境音 | **HappyHorse 1.0 I2V** | 生成过程中的音频合成 |
| **同时**动画化并**与自定义配音轨口型同步** | **Wan 2.7 + `audio_url`** | 接收你提供的 MP3/WAV（3–30 秒，≤15MB）并驱动口型同步 |
| 多语言配音变体（同图、每次调用不同音频） | **Wan 2.7 + `audio_url`** | 相同画面，按语言更换 `audio_url` |
| 多模态——图像 + 参考视频 + 参考音频一并合成 | **Seedance 2.0 Pro** | 最多 9 张图像参考、3 个视频参考（各 2–15 秒）、3 个音频参考 |
| 品牌一致叙事（含角色参考 + 场景参考 + 声音参考） | **Seedance 2.0 Pro** | 图像承载身份，视频承载场景，音频承载声音 |
| 未指定时的默认选项 | **HappyHorse 1.0 I2V** | 综合质量最佳 + 原生音频 |

代理程序会读取此表格，分类用户意图，并选择下方相应的子章节。

## 前置要求

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账号** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=...`
4. **源图 URL** — JPEG/PNG/WebP，最小 300px，≤10MB；比例 1:2.5 至 2.5:1（HappyHorse）——其他模型规格相似。

---

## 路线 1：HappyHorse 1.0 I2V —— 人像/产品/通用动画的默认选择

**模型**：`happyhorse/happyhorse-1-0/image-to-video` · **竞技场排名**：#1（Elo 1392）

### Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `image_url` | string | 是 | — | JPEG/JPG/PNG/WEBP。最小 300px。比例 1:2.5–2.5:1。≤10MB。 |
| `prompt` | string | 是 | — | ≤5000 个非中文字符或 2500 个中文字符。**运动 / 镜头 / 灯光**描述。 |
| `resolution` | enum | 否 | `1080P` | `720P` 或 `1080P`。 |
| `duration` | int | 否 | 5 | 3–15 秒。 |
| `seed` | int | 否 | 0 | 用于变体对比复用。 |
| `watermark` | bool | 否 | true | 提供方水印开关。 |

输出比例 = 输入比例。不支持独立重新构图。

### Invoke

```bash
runcomfy run happyhorse/happyhorse-1-0/image-to-video \
  --input '{
    "image_url": "https://.../portrait.jpg",
    "prompt": "Gentle camera drift around the subject'\''s face, subtle breathing motion, identity-stable features, soft natural light."
  }' \
  --output-dir <absolute/path/
```

### Prompting tips

- **以运动动词开头**："drift"、"dolly in"、"orbit"、"tilt up"、"reveal"、"blink"、"breathe"。优先描述**正在发生运动**的内容。
- **不要复述图片**——模型已经看到了。将注意力放在变化的部分上。
- **明确保留目标**："identity-stable features"、"packaging unchanged"、"background geometry stable"。
- **灯光演变**："rim light intensifying"、"shadows shortening as camera rises"。
- **每个片段一个动作节拍**——单一主要运动（orbit OR dolly OR tilt OR 角色动作）。

---

## 路线 2：Wan 2.7 + `audio_url` —— 用户拥有自定义配音时使用

**模型**：`wan-ai/wan-2-7/ text-to-video`（非 `/image-to-video`——Wan 2.7 的 t2v 端点接受 `audio_url` 驱动口型同步）

**关于 Wan 2.7 的 i2v 说明**：Wan 2.7 的 i2v 动画在此处没有专门的端点。对于纯 i2v（仅凭运动提示词驱动图片动画），建议使用 **HappyHorse i2v**。仅在用户有自定义音频轨道，需要将其口型同步到生成的说话人画面时，才使用 Wan 2.7。

### Schema（Wan 2.7 t2v 含音频）

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 最多约 5000 字符。描述说话人画面：构图、灯光、运动。 |
| `audio_url` | string | 是（用于口型同步） | — | WAV/MP3，3–30 秒，≤15MB。**驱动口型同步。** |
| `aspect_ratio` | enum | 否 | `16:9` | `16:9`、`9:16`、`1:1`、`4:3`、`3:4`。 |
| `resolution` | enum | 否 | `1080p` | `720p` 或 `1080p`。 |
| `duration` | enum | 否 | `5` | 2–15（整秒数）。与音频长度匹配。 |
| `negative_prompt` | string | 否 | — | 需避免的具体问题（例如"无字幕、无闪烁"）。 |
| `seed` | int | 否 | — | 可复现性。 |

### Invoke

```bash
runcomfy run wan-ai/wan-2-7/ text-to-video \
  --input '{
    "prompt": "Medium close-up of a confident spokesperson in a softly-lit recording booth, leaning slightly toward the camera, locked tripod, shallow DOF, warm key light from camera-left.",
    "audio_url": "https://.../voiceover-en.mp3",
    "duration": 12,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <absolute/path/
```

### Prompting tips

- **描述说话人画面**——构图、灯光、镜头质感。音频驱动口型同步；提示词围绕它构建视觉画面。
- **将 `duration` 与音频长度匹配**——若时长过长，超出音频的部分画面会静音。
- **使用 `negative_prompt` 规避问题**：`"no subtitles, no flicker, no distorted hands"`。
- **多语言配音**——使用相同提示词，每次调用更换 `audio_url`。固定 `seed` 以保证各语言视觉一致性。

---

## 路线 3：Seedance 2.0 Pro —— 多模态动画（图像 + 参考视频 + 参考音频）

**模型**：`bytedance/seedance-v2/pro`

当用户需要单条合成内容，同时包含：**主体图像** + **参考视频中的场景** + **参考音频中的声音语气** 时使用。

### Schema（Seedance 2.0 Pro，与 i2v 相关的字段）

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 中文 ≤500 字符或英文 ≤1000 词。 |
| `image_url` | array | 是（用于 i2v） | `[]` | 0–9 张图像。**第一张为主体。** |
| `video_url` | array | 否 | `[]` | 0–3 个参考片段（MP4/MOV），各 2–15 秒。 |
| `audio_url` | array | 否 | `[]` | 0–3 个参考音频（WAV/MP3），各 2–15 秒，单个 < 15MB。 |
| `aspect_ratio` | enum | 否 | `adaptive` | `adaptive`、`16:9`、`9:16`、`4:3`、`3:4`、`1:1`、`21:9`。 |
| `duration` | int | 否 | 5 | 4–15（整秒数）。 |
| `resolution` | enum | 否 | `720p` | `480p` 或 `720p`。 |
| `generate_audio` | bool | 否 | true | 生成过程中的同步语音 / 音效 / 音乐。 |
| `seed` | int | 否 | — | 可复现性。 |

### Invoke

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "Subject from image 1 walks through the café in video 1, voice tone matches audio 1. Medium close-up, slow push-in, warm light, gentle ambience.",
    "image_url": ["https://.../subject.jpg"],
    "video_url": ["https://.../cafe-locked-shot.mp4"],
    "audio_url": ["https://.../voice-tone.mp3"],
    "duration": 8
  }' \
  --output-dir <absolute/path/
```

### Prompting tips

- **图像与文本区分**——用 `image_url` 处理必须保持不变的内容（面部、服装、品牌）；用 `prompt` 处理应变化的内容（动作、氛围、灯光）。
- **在提示词中标注参考来源**：`"subject from image 1, lighting from video 1, voice from audio 1"`。Seedance 会正确路由提示线索。
- **参考媒体规格**——视频 / 音频需为 2–15 秒；音频 < 15MB。
- **不要混合截然不同的美学风格**——若图像 1 是水彩、视频 1 是写实风格，输出会偏移。

---

## 局限性

- **各路线继承对应模型的限制。** HappyHorse：最长 15 秒，输出比例 = 输入比例。Wan 2.7：最长 15 秒，音频 3–30 秒 / 15MB。Seedance：此模板上限 720p，最长 15 秒。
- **不支持多路线混合。** 该技能每次调用仅选择一种模型。如果用户想要 HappyHorse 动画与 Wan 式口型同步合为同一片段，需要两次调用 + 拼接（此处不在范围内）。
- **品牌特定覆盖** —— 若用户指定了未列出的特定模型变体（如 Wan 2.6、Seedance 1.5），应路由到对应的品牌技能（`wan-2-7`、`seedance-v2`），而非在此处强制调用。

## 退出码

| code | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video)。

## 工作原理

该技能根据用户意图从 HappyHorse 1.0 I2V / Wan 2.7 t2v+音频 / Seedance 2.0 Pro 中选择一种，并以匹配的 JSON 请求体调用 `runcomfy run <model_id>`。CLI 向 Model API 发送 POST 请求，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。退出前可通过 `Ctrl-C` 取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 会将 API 令牌以模式 0600（仅所有者可读/写）写入 `~/.config/runcomfy/token.json`。在 CI / 容器中可通过设置 `RUNCOMFY_TOKEN` 环境变量完全绕过该文件。
- **输入边界**：用户提示词通过 `--input` 作为 JSON 字符串传给 CLI。CLI **不会**对提示词进行 shell 展开；它将 JSON 请求体直接通过 HTTPS 传输至 Model API。提示词内容无 shell 注入风险。
- **第三方内容**：你传入的图像 / 蒙版 / 视频 URL 由 RunComfy 模型服务器获取，而非由你本机的 CLI 获取。请将外部 URL 视为不可信；图像提示词注入是任何图像编辑 / 视频编辑模型已知的风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）以及 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测、无回调。
- **生成文件大小限制**：CLI 将中止任何单次下载超过 2 GiB 的操作，以防止恶意或失控模型输出导致磁盘满载。
