# 视频编辑 — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Wan 2.7 Edit-Video](https://www.runcomfy.com/models/wan-ai/wan-2-7/edit-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Kling Motion-Control Pro](https://www.runcomfy.com/models/kling/kling-2-6/motion-control-pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Lucy Edit Restyle](https://www.runcomfy.com/models/decart/lucy-edit/restyle?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/video-edit)

**视频编辑，意图路由。** 该技能不会将你锁定在单一模型上——它会根据用户实际需求，从 RunComfy 目录中选择合适的视频编辑模型：通用重绘、从参考片段迁移动作，或轻量级的身份稳定换装 / 背景替换。

```bash
npx skills add agentspace-so/runcomfy-skills --skill video-edit -g
```

## 为用户意图选择合适的模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 重绘说话头视频——保留面部 / 姿态 / 唇部动作 | **Wan 2.7 Edit-Video** | 身份与动作保留能力强；支持最高 1080p |
| 更换产品背景，保留镜头运动 | **Wan 2.7 Edit-Video** | 保留镜头运动；遵循单向编辑 |
| 使用参考图替换包装设计 | **Wan 2.7 Edit-Video** + `reference_image` | 基于参考条件的图面设计迁移 |
| 应用电影级调色 / 商业级精修 | **Wan 2.7 Edit-Video** | 擅长单向全局观感调整 |
| **从参考视频精准迁移动作**到目标角色 | **Kling 2.6 Pro Motion Control** | 专为带身份保持的动作映射设计 |
| 将目标角色的口型动作与源视频口型同步 | **Kling 2.6 Pro Motion Control** | 专为紧密的时间连贯性设计 |
| **轻量换装**且保持身份 | **Lucy Edit Restyle** | 核心优势为局部身份稳定编辑 |
| **身份稳定的重绘**（"沙漠中的宇航员"、"温暖的黄金时刻光线"） | **Lucy Edit Restyle** | 专注重绘时的时间一致性 |
| 未指定时默认 | **Wan 2.7 Edit-Video** | 最通用，分辨率最高 |

智能体读取该表格，对用户意图进行分类，并选择下方对应的子章节。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账号** — `runcomfy login`。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>`。
4. **源视频 URL** — 格式与限制取决于所选路径。

---

## 路径 1：Wan 2.7 Edit-Video — 重绘 / 背景 / 包装的默认路径

**模型**：`wan-ai/wan-2-7/edit-video`

### Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 以保留性表述开头。每次调用仅一个编辑方向。 |
| `video` | string | 是 | — | MP4/MOV URL，2–10 秒，≤100MB。 |
| `reference_image` | string | 否 | — | URL — 仅用于直接设计 / 外观迁移。 |
| `resolution` | enum | 否 | (输入) | `720p` 或 `1080p`。 |
| `aspect_ratio` | enum | 否 | (输入) | W:H。默认使用输入。 |
| `duration` | int | 否 | 0 | `0` = 匹配输入；`2–10` = 从开头截断。 |
| `audio_setting` | enum | 否 | `auto` | `auto` 或 `origin`（保留源音频）。 |
| `seed` | int | 否 | — | 可复现性。 |

### 调用方式

**保留身份、更换背景，保留音频：**

```bash
runcomfy run wan-ai/wan-2-7/edit-video \
  --input '{
    "prompt": "Preserve the speaker'\''s face, pose, and lip movement; change the background to a modern office with neutral lighting.",
    "video": "https://.../speaker.mp4",
    "audio_setting": "origin"
  }' \
  --output-dir <absolute/path>
```

**使用参考图更换包装：**

```bash
runcomfy run wan-ai/wan-2-7/edit-video \
  --input '{
    "prompt": "Maintain the original framing and hand movement; replace the packaging design using the reference image.",
    "video": "https://.../hand-holding-package.mp4",
    "reference_image": "https://.../new-packaging.png",
    "audio_setting": "origin"
  }' \
  --output-dir <absolute/path>
```

### 提示技巧

- **以保留目标开头**：`"Preserve [face / pose / motion / framing / lip movement]; [then state the change]"`。
- **每次调用仅一个编辑方向。** 复合编辑会在动作上产生漂移。
- **仅在合理时使用 `reference_image`**（包装更换、带目标视觉的换装等）。通用重绘无需传入参考。
- **不需要重新生成原声时使用 `audio_setting: "origin"`**，例如说话头场景。
- **源视频限制**：2–10 秒，≤100MB。

---

## 路径 2：Kling 2.6 Pro Motion Control — 当从参考片段迁移动作才是重点时

**模型**：`kling/kling-2-6/motion-control-pro`

在用户希望**将参考视频的动作迁移到目标角色**（由图像或另一视频驱动）时使用。这不是重绘——而是带身份保持的动作映射。

### Schema

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `prompt` | string | 是 | 描述目标动作 / 风格。 |
| `image` | string | 是（图像方向） | 角色 / 背景一致性参考。 |
| `video` | string | 是 | **运动参考**。方向不同，时长不同。 |
| `keep_original_sound` | bool | 否 | 保留参考视频的音频。 |
| `character_orientation` | enum | 是 | `image`（输出最长 10 秒）或 `video`（输出最长 30 秒）。 |

### 调用方式

```bash
runcomfy run kling/kling-2-6/motion-control-pro \
  --input '{
    "prompt": "A young american woman dancing",
    "image": "https://.../target-character.jpg",
    "video": "https://.../motion-reference-dance.mp4",
    "character_orientation": "image",
    "keep_original_sound": true
  }' \
  --output-dir <absolute/path>
```

### 提示技巧

- **图像参考中主体占比需 > 5%**，以获得干净的 identity hold。
- **空间约束有助于效果**：`"character on left side, background motion right"`。
- **若迭代间结果漂移则简化** — 去掉形容词，保留核心动作描述。
- **`character_orientation: "image"`** 限制输出为 10 秒；`"video"` 允许 30 秒。

---

## 路径 3：Lucy Edit Restyle — 轻量身份稳定重绘 / 换装

**模型**：`decart/lucy-edit/restyle`

在编辑为**局部风格修改**——换装、场景重新打光、氛围重绘——且身份保留至关重要时使用。相较于 Wan 2.7 Edit 更轻量，上限为 720p。

### Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 自然语言编辑指令。 |
| `video_url` | string | 是 | — | MP4/MOV/WEBM/GIF。 |
| `resolution` | enum | 否 | `720p` | 该层级仅支持 `720p`。 |

### 调用方式

**换装：**

```bash
runcomfy run decart/lucy-edit/restyle \
  --input '{
    "prompt": "Change outfit to professional business attire; preserve face and motion.",
    "video_url": "https://.../subject-walking.mp4"
  }' \
  --output-dir <absolute/path>
```

**氛围重绘：**

```bash
runcomfy run decart/lucy-edit/restyle \
  --input '{
    "prompt": "Make lighting warm and golden hour; preserve face, pose, and motion.",
    "video_url": "https://.../subject-portrait.mp4"
  }' \
  --output-dir <absolute/path>
```

### 提示技巧

- **局部修改的表述更有效。** "Outfit"（服装）、"lighting"（光线）、"background"（背景）——选择其中一个类别。
- **明确身份保留目标** — `"preserve face and motion"` 即可；无需过度细化。
- **避免完全替换**（"太空中的宇航员"可用；"将主体换成另一个不同的人"不行）。Lucy 专为局部风格修改设计，而非完全的角色替换。
- **无比例控制** — 输出与输入一致。若未预先匹配，裁剪将在服务器端进行。

---

## 限制

- **每条路径继承其模型的限制。** Wan 2.7 Edit：2–10 秒，1080p 上限。Kling：图像方向 10 秒，视频方向 30 秒。Lucy：720p 上限，无比例控制。
- **不支持多路径混合。** 该技能每次调用仅选择一种模型。
- **品牌特定覆盖** — 若用户指定了具体模型，请路由到对应品牌技能（`wan-2-7`）以提供更完整的处理。

## 退出码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / schema 不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit)。

## 工作原理

该技能根据用户意图选择 Wan 2.7 Edit-Video、Kling 2.6 Pro Motion Control 或 Lucy Edit Restyle 中的一种，并以匹配的 JSON 请求体调用 `runcomfy run <model_id>`。CLI 将请求 POST 至模型 API，轮询请求，获取结果，并将任何 `.runcomfy.net` / `.runcomfy.com` URL 下载到 `--output-dir` 中。可在退出前使用 `Ctrl-C` 取消远程请求。

## 安全与隐私

- **Token 存储**：`runcomfy login` 将 API token 写入 `~/.config/runcomfy/token.json`，权限为 0600（仅属主可读/写）。在 CI / 容器中，可通过设置 `RUNCOMFY_TOKEN` 环境变量完全绕过该文件。
- **输入边界**：用户提示通过 `--input` 以 JSON 字符串传递给 CLI。CLI 不会对提示进行 shell 展开；它直接将 JSON 请求体通过 HTTPS 传输至模型 API。提示内容无 shell 注入风险。
- **第三方内容**：您传入的图像 / 蒙版 / 视频 URL 由 RunComfy 模型服务器获取，而非由本机 CLI 获取。请将外部 URL 视为不可信；图像提示注入对任何图像编辑 / 视频编辑模型而言都是已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）以及 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI 会中止任何单个下载超过 2 GiB 的情况，以防止恶意或失控的模型输出导致磁盘占满。
