# 图像转视频 — RunComfy 上的专业版

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [HappyHorse 图像转视频](https://www.runcomfy.com/models/happyhorse/happyhorse-1-0/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [Wan 2.7](https://www.runcomfy.com/models/wan-ai/wan-2-7/text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [Seedance 2.0 专业版](https://www.runcomfy.com/models/bytedance/seedance-v2/pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/image-to-video)

**图像转视频，意图路由。** 这个技能不会将你锁定在一个模型上——它会根据用户实际想要的效果，在 RunComfy 目录中挑选合适的 i2v 模型：肖像动画、自定义旁白口型同步或多模态合成。

```bash
npx skills add agentspace-so/runcomfy-skills --skill image-to-video -g
```

## 根据用户意图选择合适的模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 动画化肖像——保持身份稳定 | **HappyHorse 1.0 I2V** | 在 Artificial Analysis Arena 中排名第一（Elo 1392）；强大的面部保真度 |
| 产品发布 / 360度 / 微距运动 | **HappyHorse 1.0 I2V** | 几何保真度 + 平滑的摄像机移动 |
| 原生同步环境音效，一次处理完成 | **HappyHorse 1.0 I2V** | 一次处理中合成音频 |
| 动画化 **并** 口型同步到 **自定义旁白音轨** | **Wan 2.7 + `audio_url`** | 接受你自己的 MP3/WAV（3–30秒，≤15MB）并驱动口型同步到它 |
| 多语言配音变体（同一图像，每次调用不同音频） | **Wan 2.7 + `audio_url`** | 同一镜头，根据语言交换 `audio_url` |
| 多模态——图像 + 参考视频 + 参考音频一起 | **Seedance 2.0 专业版** | 最高可达 9 张图像参考，3 个视频参考（每个 2–15 秒），3 个音频参考 |
| 品牌一致的故事，包含角色参考 + 场景参考 + 音频参考 | **Seedance 2.0 专业版** | 图像保持身份，视频保持场景，音频保持声音 |
| 未指定时的默认选择 | **HappyHorse 1.0 I2V** | 最佳综合质量 + 原生音频 |

代理读取此表格，对用户的意图进行分类，并选择下方的匹配子部分。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>`。
4. **一个源图像 URL** — JPEG/PNG/WebP，最小 300px，≤10MB；长宽比 1:2.5 到 2.5:1（HappyHorse）——其他模型有类似规格。

---

## 路径 1：HappyHorse 1.0 I2V — 默认用于肖像 / 产品 / 一般动画

**模型**: `happyhorse/happyhorse-1-0/image-to-video` · **Arena 排名**: #1 (Elo 1392)

### Schema

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `image_url` | 字符串 | 是 | — | JPEG/JPG/PNG/WEBP。最小 300px。长宽比 1:2.5–2.5:1。≤10MB。 |
| `prompt` | 字符串 | 是 | — | ≤5000 个非中文字符或 2500 个中文字符。**动作 / 摄像机 / 照明** 描述。 |
| `resolution` | 枚举 | 否 | `1080P` | `720P` 或 `1080P`。 |
| `duration` | 整数 | 否 | 5 | 3–15 秒。 |
| `seed` | 整数 | 否 | 0 | 用于变体比较时重复。 |
| `watermark` | 布尔值 | 否 | true | 提供水印切换。 |

输出长宽比 = 输入长宽比。没有独立的重新构图。

### 调用

```bash
runcomfy run happyhorse/happyhorse-1-0/image-to-video \
  --input '{
    "image_url": "https://.../portrait.jpg",
    "prompt": "缓慢地围绕主体的脸移动摄像机，轻微的呼吸动作，身份稳定的特征，柔和的自然光。"
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **以动作动词开头**: "drift", "dolly in", "orbit", "tilt up", "reveal", "blink", "breathe"。优先考虑正在移动的内容。
- **不要重述图像** — 模型已经看到了它。专注于变化的标记。
- **明确的保存目标**: "身份稳定的特征", "包装不变", "背景几何稳定"。
- **照明演变**: "边缘光增强", "随着摄像机上升，阴影变短"。
- **每个剪辑一个节拍** — 单一主要动作（orbit OR dolly OR tilt OR 角色动作）。

---

## 路径 2：Wan 2.7 + `audio_url` — 当用户有自定义旁白时

**模型**: `wan-ai/wan-2-7/text-to-video`（不是 `/image-to-video` — Wan 2.7 的 t2v 端点接受一个 `audio_url` 来驱动口型同步）

**关于 Wan 2.7 的 i2v 注意**: Wan 2.7 的主要 i2v 动画不在此处的专用端点上。对于纯 i2v（仅通过动作提示动画化的图像），请优先选择 **HappyHorse i2v**。仅在用户有自定义音频轨道并希望将其口型同步到生成的说话头片段时，才专门使用 Wan 2.7。

### Schema (Wan 2.7 t2v 带音频)

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | — | 约 5000 个字符。描述说话头镜头：构图、照明、动作。 |
| `audio_url` | 字符串 | 是（用于口型同步） | — | WAV/MP3，3–30秒，≤15MB。**驱动口型同步。** |
| `aspect_ratio` | 枚举 | 否 | `16:9` | `16:9`, `9:16`, `1:1`, `4:3`, `3:4`。 |
| `resolution` | 枚举 | 否 | `1080p` | `720p` 或 `1080p`。 |
| `duration` | 枚举 | 否 | `5` | 2–15（整数秒）。匹配音频长度。 |
| `negative_prompt` | 字符串 | 否 | — | 要避免的具体问题（例如 "无字幕，无闪烁"）。 |
| `seed` | 整数 | 否 | — | 可重复性。 |

### 调用

```bash
runcomfy run wan-ai/wan-2-7/text-to-video \
  --input '{
    "prompt": "自信的发言人中等特写，在柔和照明的录音室中，略微朝向摄像机倾斜，三脚架固定，浅景深，来自摄像机左侧的暖色调主光。",
    "audio_url": "https://.../voiceover-en.mp3",
    "duration": 12,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **描述说话头镜头** — 构图、照明、镜头感觉。音频驱动口型同步；提示构建围绕它的视觉框架。
- **匹配 `duration` 到音频长度** — 如果太长，片段在音频结束后将保持静音。
- **使用 `negative_prompt` 指出问题**: `"无字幕，无闪烁，无扭曲的手"`.
- **多语言配音** — 相同提示，根据语言交换 `audio_url`。锁定种子以跨语言保持视觉一致性。

---

## 路径 3：Seedance 2.0 专业版 — 多模态动画（图像 + 参考视频 + 参考音频）

**模型**: `bytedance/seedance-v2/pro`

在用户希望单个片段结合：**主题图像** + **参考视频中的场景** + **参考音频中的声音语调** 时使用。

### Schema (Seedance 2.0 专业版，与 i2v 相关的字段)

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | — | 中文 ≤500 字符 OR 英文 ≤1000 词。 |
| `image_url` | 数组 | 是（用于 i2v） | `[]` | 0–9 张图像。**第一个是主要主题。** |
| `video_url` | 数组 | 否 | `[]` | 0–3 个参考片段（MP4/MOV），每个 2–15 秒。 |
| `audio_url` | 数组 | 否 | `[]` | 0–3 个参考音频（WAV/MP3），每个 2–15 秒，< 15MB。 |
| `aspect_ratio` | 枚举 | 否 | `adaptive` | `adaptive`, `16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `21:9`。 |
| `duration` | 整数 | 否 | 5 | 4–15（整数秒）。 |
| `resolution` | 枚举 | 否 | `720p` | `480p` 或 `720p`。 |
| `generate_audio` | 布尔值 | 否 | true | 一次处理中同步语音 / 音效 / 音乐。 |
| `seed` | 整数 | 否 | — | 可重复性。 |

### 调用

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "来自图像 1 的主题在视频 1 中走过咖啡馆，声音语调匹配音频 1。中等特写，缓慢推进，暖光，轻柔的环境音。",
    "image_url": ["https://.../subject.jpg"],
    "video_url": ["https://.../cafe-locked-shot.mp4"],
    "audio_url": ["https://.../voice-tone.mp3"],
    "duration": 8
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **图像与文本的划分** — 使用 `image_url` 对于必须保持稳定的元素（脸、服装、品牌）；使用 `prompt` 对于应该演变的元素（动作、情绪、照明）。
- **提示中编号参考**: `"来自图像 1 的主题，来自视频 1 的照明，来自音频 1 的声音"`。Seedance 正确路由提示。
- **参考媒体规格** — 视频 / 音频必须为 2–15 秒；音频 < 15MB。
- **不要混合截然不同的美学** — 如果图像 1 是水彩画，而视频 1 是照片逼真，输出会漂移。

---

## 限制

- **每个路径继承其模型的限制。** HappyHorse: 15 秒上限，输出长宽比 = 输入长宽比。Wan 2.7: 15 秒上限，音频 3–30 秒/15MB。Seedance: 此模板 720p 上限，15 秒上限。
- **不能混合多路径。** 此技能每次调用选择一个模型。如果用户希望在同一个片段中获取 HappyHorse 动画 + Wan 风格口型同步，那是两个调用 + 一个拼接（在此范围之外）。
- **品牌特定覆盖** — 如果用户命名了一个未列出的特定模型变体（例如 Wan 2.6，Seedance 1.5），路由到相应的品牌技能（`wan-2-7`，`seedance-v2`）而不是强制通过这里。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-to-video).

## 工作原理

技能根据用户意图选择 HappyHorse 1.0 I2V / Wan 2.7 t2v+音频 / Seedance 2.0 专业版之一，并调用 `runcomfy run <model_id>` 使用匹配的 JSON 正文。CLI 向模型 API 发送 POST 请求，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**: `runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量以在 CI / 容器中完全绕过文件。
- **输入边界**: 用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会对提示进行 shell 扩展；它直接将 JSON 正文通过 HTTPS 传输到模型 API。提示内容没有 shell 注入表面。
- **第三方内容**: 你传递的图像 / 掩码 / 视频链接由 RunComfy 模型服务器获取，而不是你的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**: 仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测，无回调。
- **生成文件大小上限**: CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
