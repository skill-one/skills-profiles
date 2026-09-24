# 视频编辑 — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Wan 2.7 Edit-Video](https://www.runcomfy.com/models/wan-ai/wan-2-7/edit-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Kling Motion-Control Pro](https://www.runcomfy.com/models/kling/kling-2-6/motion-control-pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Lucy Edit Restyle](https://www.runcomfy.com/models/decart/lucy-edit/restyle?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/video-edit)

**基于意图的视频编辑。** 该技能不会让您局限于某一个模型——它根据用户实际的需求，从 RunComfy 目录中挑选合适的视频编辑模型：通用的风格重制、从参考片段迁移动态、或轻量级的、保持身份稳定的服装 / 背景替换。

```bash
npx skills add agentspace-so/runcomfy-skills --skill video-edit -g
```

## 根据用户意图选择模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 重新制作说话者视频 — 保留面部 / 姿势 / 口型运动 | **Wan 2.7 Edit-Video** | 身份与运动保留能力强；最高支持 1080p |
| 替换产品背景，保持镜头运动 | **Wan 2.7 Edit-Video** | 保持镜头运动；符合单方向编辑要求 |
| 使用参考图替换包装设计 | **Wan 2.7 Edit-Video** + `reference_image` | 基于参考条件的风格迁移 |
| 应用电影级调色 / 商业级优化 | **Wan 2.7 Edit-Video** | 擅长单方向的全局画面风格调整 |
| **从参考视频向目标角色精确迁移动态** | **Kling 2.6 Pro Motion Control** | 专为带有身份保持的运动映射设计 |
| 将目标角色的口型同步运动与源视频口型运动匹配 | **Kling 2.6 Pro Motion Control** | 专为紧密的时间连贯性而设计 |
| **保留身份的轻量级服装 / 服饰替换** | **Lucy Edit Restyle** | 核心优势是局部身份稳定的编辑 |
| **身份稳定的风格重制**（"沙漠中的宇航员"、"温暖的金色时刻光线"） | **Lucy Edit Restyle** | 专注于风格重制的时序一致性 |
| 未指定时默认使用 | **Wan 2.7 Edit-Video** | 最通用，分辨率最高 |

智能体读取此表，对用户意图进行分类，并选择下方对应的段落。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账号** — `runcomfy login`。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=` <token`。
4. **源视频 URL** — 格式与限制取决于所选路由。

---

## 路由 1：Wan 2.7 Edit-Video — 风格重制 / 背景 / 包装的默认方案

**模型**：`wan-ai/wan-2-7/edit-video`

### Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 以保留目标开头。每次调用仅一个编辑方向。 |
| `video` | string | 是 | — | MP4/MOV 链接，时长 2–10 秒，≤100MB。 |
| `reference_image` | string | 否 | — | URL — 仅用于直接的设计 / 外观迁移。 |
| `resolution` | enum | 否 | (输入) | `720p` 或 `1080p`。 |
| `aspect_ratio` | enum | 否 | (输入) | 宽:高。默认为输入。 |
| `duration` | int | 否 | 0 | `0` = 匹配输入；`2–10` = 从开头截断。 |
| `audio_setting` | enum | 否 | `auto` | `auto` 或 `origin`（保留源音频）。 |
| `seed` | int | 否 | — | 可复现性。 |

### 调用方式

**背景替换，身份保留，音频保留：**

```bash
runcomfy run wan-ai/wan-2-7/edit-video \
  --input '{
    "prompt": "Preserve the speaker'\''s face, pose, and lip movement; change the background to a modern office with neutral lighting.",
    "video": "https://.../speaker.mp4",
    "audio_setting": "origin"
  }' \
  --output-dir <absolute/path>
```

**使用参考图替换包装：**

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

- **以保留目标为先**：`"Preserve [面部 / 姿势 / 运动 / 取景 / 口型运动]; [然后说明修改内容]"`。
- **每次调用仅一个编辑方向。** 复合编辑在运动上会漂移。
- **仅在合理时使用 `reference_image`**（包装替换、带目标视觉的服装替换）。通用风格重制无需传递参考。
- 对于说话者视频且不想重新生成背景音乐时，使用 `audio_setting: "origin"`。
- **源视频限制**：2–10 秒，≤100MB。

---

## 路由 2：Kling 2.6 Pro Motion Control — 当核心是参考片段的运动时

**模型**：`kling/kling-2-6/motion-control-pro`

用于当用户希望将**参考视频的运动**转移至目标角色（由图片或另一视频驱动）时。这并非风格重制——而是带有身份保持的运动映射。

### Schema

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `prompt` | string | 是 | 描述目标运动 / 风格。 |
| `image` | string | 是（图像方向） | 用于角色 / 背景一致性参考。 |
| `video` | string | 是 | **运动参考**。时长取决于方向，为 10–30 秒。 |
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

- 图像参考中主体需占画面的 > 5%，以保证身份保持的清晰度。
- **空间约束有帮助**：`"角色在左侧，背景运动在右侧"`。
- 若迭代间结果漂移，则简化——去除修饰词，保留核心运动描述。
- `character_orientation: "image"` 将输出限制为 10 秒；`"video"` 允许 30 秒。

---

## 路由 3：Lucy Edit Restyle — 轻量级的身份稳定风格重制 / 服装替换

**模型**：`decart/lucy-edit/restyle`

用于当编辑属于**局部风格修改**——服装替换、场景补光、氛围风格重制——且身份保留至关重要时。相比 Wan 2.7 Edit 更轻量，最高限制为 720p。

### Schema

| 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `prompt` | string | 是 | — | 自然语言编辑指令。 |
| `video_url` | string | 是 | — | MP4/MOV/WEBM/GIF。 |
| `resolution` | enum | 否 | `720p` | 此层级仅支持 `720p`。 |

### 调用方式

**服装替换：**

```bash
runcomfy run decart/lucy-edit/restyle \
  --input '{
    "prompt": "Change outfit to professional business attire; preserve face and motion.",
    "video_url": "https://.../subject-walking.mp4"
  }' \
  --output-dir <absolute/path>
```

**氛围风格重制：**

```bash
runcomfy run decart/lucy-edit/restyle \
  --input '{
    "prompt": "Make lighting warm and golden hour; preserve face, pose, and motion.",
    "video_url": "https://.../subject-portrait.mp4"
  }' \
  --output-dir <absolute/path>
```

### 提示技巧

- **局部修改的表述更有效。** "服装"、"光线"、"背景"——选择其中一个方向。
- **保留身份目标**——`"preserve face and motion"`（保留面部与运动）即可；无需过度细化。
- **避免完全替换**（"太空中的宇航员"可行；"将主体替换为不同人物"不可行）。Lucy 是为局部风格修改而构建，而非完全的角色替换。
- **无比例控制**——输出与输入一致。若未预先匹配，裁剪由服务端完成。

---

## 局限性

- **每条路由继承其模型的限制。** Wan 2.7 Edit：2–10 秒，1080p 上限。Kling：图像方向 10 秒，视频方向 30 秒。Lucy：720p 上限，无比例控制。
- **不支持多路由混合。** 该技能每次调用仅选择一个模型。
- **针对特定品牌的覆盖**——若用户指定了特定模型，则路由至对应的品牌技能（`wan-2-7`）以获得更完整处理。

## 退出码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / Schema 不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit)。

## 工作原理

该技能根据用户意图，从 Wan 2.7 Edit-Video / Kling 2.6 Pro Motion Control / Lucy Edit Restyle 中选择一个，并使用匹配的 JSON 请求体调用 `runcomfy run <model_id>`。CLI 向模型 API 提交 POST 请求，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` 链接下载至 `--output-dir`。在退出前，`Ctrl-C` 可取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将以 0600 权限（仅所有者可读/写）将 API 令牌写入 `~/.config/runcomfy/token.json`。在 CI / 容器中设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过该文件。
- **输入边界**：用户提示通过 `--input` 以 JSON 字符串形式传给 CLI。CLI 不会对提示进行 shell 展开；它将 JSON 请求体直接通过 HTTPS 传输至模型 API。提示内容不存在 shell 注入风险。
- **第三方内容**：您传入的图像 / 遮罩 / 视频链接由 RunComfy 模型服务器获取，而非您的机器上的 CLI 获取。请将外部链接视为不可信；对于任何图像编辑 / 视频编辑模型而言，基于图像的提示注入都是已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）以及 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测，无回调。
- **生成文件大小限制**：CLI 会中止任何单个下载超过 2 GiB 的情况，以防止恶意或失控的模型输出导致磁盘填满。
