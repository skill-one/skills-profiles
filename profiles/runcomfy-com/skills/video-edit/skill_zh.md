# 视频编辑 — 专业版包 on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Wan 2.7 Edit-Video](https://www.runcomfy.com/models/wan-ai/wan-2-7/edit-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Kling Motion-Control Pro](https://www.runcomfy.com/models/kling/kling-2-6/motion-control-pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [Lucy Edit Restyle](https://www.runcomfy.com/models/decart/lucy-edit/restyle?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/video-edit)

**视频编辑，意图路由。** 这个技能不会将你锁定在一个模型上——它会根据用户实际想要的内容，在RunComfy目录中选择正确的视频编辑模型：一般重制、从参考片段中转移动作，或轻量级的身份稳定服装/背景替换。

```bash
npx skills add agentspace-so/runcomfy-skills --skill video-edit -g
```

## 根据用户意图选择合适的模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 重制访谈视频——保留面部/姿势/唇部动作 | **Wan 2.7 Edit-Video** | 强大的身份+动作保留；支持高达1080p |
| 交换产品背景，保留相机运动 | **Wan 2.7 Edit-Video** | 保留相机运动；单向编辑得到尊重 |
| 使用参考图像替换包装设计 | **Wan 2.7 Edit-Video** + `reference_image` | 参考条件下的设计转移 |
| 应用电影色彩分级/商业润色 | **Wan 2.7 Edit-Video** | 擅长单方向全局外观变化 |
| **精确转移动作**从参考视频到目标角色 | **Kling 2.6 Pro Motion Control** | 设计用于身份保持的动作映射 |
| 目标角色的唇部动作与源视频的唇部运动同步 | **Kling 2.6 Pro Motion Control** | 建立于紧密的时间一致性之上 |
| **轻量级服装/服装替换**与身份保留 | **Lucy Edit Restyle** | 核心优势是局部身份稳定的编辑 |
| **身份稳定的重制**（“宇航员在沙漠中”，“温暖的黄金时刻光照”） | **Lucy Edit Restyle** | 专门用于重制的时序一致性 |
| 未指定时默认 | **Wan 2.7 Edit-Video** | 最通用，最高分辨率 |

代理读取此表格，对用户的意图进行分类，并选择下方的匹配子部分。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy账户** — `runcomfy login`.
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>`.
4. **一个源视频URL** — 格式和限制取决于所选路线。

---

## 路线 1：Wan 2.7 Edit-Video — 默认用于重制/背景/包装

**模型**: `wan-ai/wan-2-7/edit-video`

### Schema

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | — | 首先强调保留。每次调用一个编辑方向。 |
| `video` | 字符串 | 是 | — | MP4/MOV URL，2–10秒，≤100MB。 |
| `reference_image` | 字符串 | 否 | — | URL——仅用于直接设计/外观转移。 |
| `resolution` | 枚举 | 否 | (输入) | `720p` 或 `1080p`。 |
| `aspect_ratio` | 枚举 | 否 | (输入) | W:H。默认为输入。 |
| `duration` | 整数 | 否 | 0 | `0` = 匹配输入；`2–10` = 从开始截断。 |
| `audio_setting` | 枚举 | 否 | `auto` | `auto` 或 `origin`（保留源音频）。 |
| `seed` | 整数 | 否 | — | 可重复性。 |

### 调用

**背景替换，身份保留，音频保留:**

```bash
runcomfy run wan-ai/wan-2-7/edit-video \
  --input '{
    "prompt": "保留说话者的面部、姿势和唇部动作；将背景更改为具有中性光照的现代办公室。",
    "video": "https://.../speaker.mp4",
    "audio_setting": "origin"
  }' \
  --output-dir <绝对路径>
```

**包装替换与参考图像:**

```bash
runcomfy run wan-ai/wan-2-7/edit-video \
  --input '{
    "prompt": "保持原始构图和手部动作；使用参考图像替换包装设计。",
    "video": "https://.../手持包装.mp4",
    "reference_image": "https://.../新包装.png",
    "audio_setting": "origin"
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **保留目标优先**: `"保留[面部 / 姿势 / 动作 / 构图 / 唇部动作]; [然后声明更改]"`.
- **每次调用一个编辑方向。** 复合编辑在动作上漂移。
- **`reference_image` 仅在合理时使用**（包装替换、目标视觉的服装替换）。不要为一般重制传递参考。
- **`audio_setting: "origin"`** 对于不需要重新生成配乐的访谈视频。
- **源视频限制**: 2–10秒，≤100MB。

---

## 路线 2：Kling 2.6 Pro Motion Control — 当参考片段的动作是重点时

**模型**: `kling/kling-2-6/motion-control-pro`

在用户想要将参考视频的动作转移到目标角色上时使用（由图像或另一个视频驱动）。这不是重制——它是带有身份保持的动作映射。

### Schema

| 字段 | 类型 | 必填 | 备注 |
|---|---|---|---|
| `prompt` | 字符串 | 是 | 描述目标动作 / 风格。 |
| `image` | 字符串 | 是（图像方向） | 参考角色 / 背景一致性。 |
| `video` | 字符串 | 是 | **动作参考**。 10–30秒，取决于方向。 |
| `keep_original_sound` | 布尔 | 否 | 保留参考视频的音频。 |
| `character_orientation` | 枚举 | 是 | `image`（最大10秒输出）或 `video`（最大30秒输出）。 |

### 调用

```bash
runcomfy run kling/kling-2-6/motion-control-pro \
  --input '{
    "prompt": "一个年轻的美国女性跳舞",
    "image": "https://.../目标角色.jpg",
    "video": "https://.../动作参考-舞蹈.mp4",
    "character_orientation": "image",
    "keep_original_sound": true
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **主体必须在图像参考中占> 5%的帧**以获得干净的身份保持。
- **空间限制有帮助**: `"角色在左侧，背景动作在右侧"`.
- **简化**如果结果在迭代之间漂移——删除形容词，保留核心动作描述。
- **`character_orientation: "image"`** 限制输出为10秒；`"video"` 允许30秒。

---

## 路线 3：Lucy Edit Restyle — 轻量级身份稳定的重制 / 服装替换

**模型**: `decart/lucy-edit/restyle`

在编辑是**局部风格修改**时使用——服装替换、场景重光、氛围重制——并且身份保留至关重要。比Wan 2.7 Edit轻量；限制在720p。

### Schema

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | — | 自然语言编辑指令。 |
| `video_url` | 字符串 | 是 | — | MP4/MOV/WEBM/GIF。 |
| `resolution` | 枚举 | 否 | `720p` | `720p` 仅在此级别。 |

### 调用

**服装替换:**

```bash
runcomfy run decart/lucy-edit/restyle \
  --input '{
    "prompt": "将服装更改为专业的商务服装；保留面部和动作。",
    "video_url": "https://.../主体行走.mp4"
  }' \
  --output-dir <绝对路径>
```

**氛围重制:**

```bash
runcomfy run decart/lucy-edit/restyle \
  --input '{
    "prompt": "使光照温暖并具有黄金时刻；保留面部、姿势和动作。",
    "video_url": "https://.../主体肖像.mp4"
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **局部更改短语获胜。** "服装"、"光照"、"背景"——选择一个桶。
- **保留身份目标** — `"保留面部和动作"` 足够；不要过度指定。
- **避免完全替换**（“宇航员在太空中”有效；“替换主体为不同的人”无效）。Lucy是用于局部风格修改的，不是完全角色替换。
- **没有宽高比控制** — 输出匹配输入。如果预先不匹配，服务器端会发生裁剪。

---

## 限制

- **每个路线继承其模型的限制。** Wan 2.7 Edit: 2–10秒，1080p上限。Kling: 10秒（图像方向）或30秒（视频方向）。Lucy: 720p上限，无宽高比控制。
- **没有多路线混合。** 此技能每次调用选择一个模型。
- **品牌特定覆盖** — 如果用户指定了特定模型，路由到相应的品牌技能（`wan-2-7`）以获得更全面的处理。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 坏CLI参数 |
| 65 | 坏输入JSON / 模式不匹配 |
| 69 | 上游5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=video-edit).

## 工作原理

该技能根据用户意图选择Wan 2.7 Edit-Video / Kling 2.6 Pro Motion Control / Lucy Edit Restyle中的一个，并调用 `runcomfy run <model_id>` 与匹配的JSON正文。CLI POST到模型API，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL下载到 `--output-dir`。 `Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**: `runcomfy login` 将API令牌写入 `~/.config/runcomfy/token.json`，模式为0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量以在CI / 容器中绕过文件。
- **输入边界**: 用户提示作为JSON字符串通过 `--input` 传递给CLI。CLI**不会**展开提示；它将JSON正文直接通过HTTPS传输到模型API。提示内容没有shell注入表面。
- **第三方内容**: 你传递的图像 / 掩码 / 视频URL由RunComfy模型服务器获取，而不是你的机器上的CLI。将外部URL视为不受信任；基于图像的提示注入是任何图像编辑/视频编辑模型的已知风险。
- **出站端点**: 仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。没有遥测，没有回调。
- **生成文件大小上限**: CLI中止任何单个下载> 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
