# Wan 2.7 — RunComfy 上的专业包

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=wan-2-7) · [文本到视频](https://www.runcomfy.com/models/wan-ai/wan-2-7/text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=wan-2-7) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/wan-2-7)

Wan-AI 的 **Wan 2.7** — 标志性视频模型，具有多参考条件处理和音频驱动唇同步功能 — 部署在 **RunComfy 模型 API** 上。

```bash
npx skills add agentspace-so/runcomfy-skills --skill wan-2-7 -g
```

## 何时选择此模型（与兄弟模型对比）

| 您需要 | 使用 |
|---|---|
| 将唇同步视频与您提供的音频轨道结合 | **Wan 2.7** (`audio_url`) |
| 多参考精细运动控制 | **Wan 2.7** |
| 平滑过渡、精确运动物理 | **Wan 2.7** |
| 目前投票第一的盲选视频模型 | HappyHorse 1.0 |
| 多模态电影制作，结合图像+视频+音频参考 + 生成语音 | Seedance 2.0 Pro |
| 现有素材的电影级运动编辑 | Kling Video O1 |
| 超快迭代 | LTX 2 |

如果用户明确提到 "Wan" / "Wan 2.7" / "wan-ai" / "alibaba video"，无论何种情况都应路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `wan-ai/wan-2-7/text-to-video`

| 字段 | 类型 | 必填 | 默认值 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | — | 最大约 5000 字符 / ~1500 个 token。 |
| `audio_url` | 字符串 | 否 | — | WAV/MP3，3–30 秒，≤15MB。**驱动唇同步。** 省略 → 自动生成背景音乐。 |
| `aspect_ratio` | 枚举 | 否 | `16:9` | `16:9`，`9:16`，`1:1`，`4:3`，`3:4`。 |
| `resolution` | 枚举 | 否 | `1080p` | `720p` 或 `1080p`。 |
| `duration` | 枚举 | 否 | `5` | 2–15（秒）。 |
| `negative_prompt` | 字符串 | 否 | — | 最大 500 字符。要避免的具体问题。 |
| `enable_prompt_expansion` | 布尔值 | 否 | true | 自动重写短提示。用于精确控制时禁用。 |
| `seed` | 整数 | 否 | — | 0..2^31-1。用于生成变体时重复。 |

## 如何调用

**默认（5 秒 1080p 16:9，提示扩展）：**

```bash
runcomfy run wan-ai/wan-2-7/text-to-video \
  --input '{"prompt": "<用户提示>"}' \
  --output-dir <绝对路径>
```

**音频驱动唇同步（使用您自己的音频）：**

```bash
runcomfy run wan-ai/wan-2-7/text-to-video \
  --input '{
    "prompt": "中景拍摄发言人，柔和的影棚灯光，固定三脚架，轻微呼吸动作。",
    "audio_url": "https://.../voiceover.mp3",
    "duration": 12,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <绝对路径>
```

**精确控制（不自动扩展）：**

```bash
runcomfy run wan-ai/wan-2-7/text-to-video \
  --input '{
    "prompt": "<您想要的精确内容>",
    "enable_prompt_expansion": false,
    "negative_prompt": "无字幕，无闪烁，无扭曲的手"
  }' \
  --output-dir <绝对路径>
```

## 提示技巧 — 实际有效的内容

**用普通英语描述相机和运动。** "缓慢推镜头"，"固定三脚架，低角度"，"手持跟拍"，"从上方俯冲移动"。将拍摄场景前置。

**每个片段一个主要动作。** 不要堆叠多个竞争动作。选择节奏： "她转身，然后微笑" 而不是 "她转身 AND 微笑 AND 一辆公交车经过 AND..."。

**使用 `negative_prompt` 解决具体问题。** 好： "无字幕，无水印，无闪烁"。差（模糊）： "无不良灯光"。

**默认情况下提示扩展是开启的。** 短提示会被模型自动重写。对于简洁/精确的提示（如品牌严格广告文案），使用 `enable_prompt_expansion: false` 禁用。

**音频规格很重要。** `audio_url` 必须为 3–30 秒，≤15MB，WAV/MP3。超出范围的文件会被拒绝。匹配音频长度与片段时长。

**迭代种子。** 当您希望同一提示的不同变体保持一致输出时，重复使用相同的种子。改变种子以获得真正的多样性。

**反模式：**
- 静态帧描述 → 运动将模糊不清。
- 模糊的负面提示 ("无不良颜色") → 被忽略。
- 音频超出 3–30 秒 / 15MB / WAV-MP3 规格 → 被拒绝。
- 提示 > 5000 字符 / 1500 个 token → 输出质量下降。

## Wan 2.7 的优势

| 用例 | 为什么选择 Wan 2.7 |
|---|---|
| **带自定义配音的唇同步广告** | `audio_url` 接受您的音频轨道 |
| **多语言配音变体** | 同一提示，不同语言使用不同的 `audio_url` |
| **多参考运动控制** | 最多 5 个参考媒体（图像 / 视频 / 语音） |
| **平滑过渡 + 运动物理** | 强大的物理感知运动先验 |
| **负面提示的干净输出** | 针对性问题排除 |

## 示例提示（验证可生成强结果）

**页面示例（产品展示）：**

```
电影级中景拍摄产品在大理石表面上，柔和的影棚灯光，缓慢的微妙镜头推进，浅景深，高端商业风格，清晰的 1080p 细节
```

**唇同步发言人（带 `audio_url`）：**

```
中景拍摄自信的发言人，在柔和灯光的录音棚中，略微朝向镜头，固定三脚架，浅景深，来自镜头左侧的暖色调主光。
```

**垂直平台原生：**

```
9:16 垂直短片。咖啡师制作一杯浓缩咖啡，蒸汽升入晨光中，丰富的奶油缓慢形成。手持拍摄，浅景深，温暖的咖啡馆氛围。
```

## 限制

- **时长上限 15 秒。** 对于更长的叙事，请拼接多个调用。
- **无原生 4K** — 1080p 为上限。
- **宽高比** — 仅支持 5 个预定义值。
- **音频规格** — 3–30 秒，≤15MB，仅支持 WAV/MP3。
- **参考媒体上限 5**（图像 + 视频 + 语音组合）。
- **用于生成语音（无单独音频轨道），请使用 Seedance 2.0 Pro** — Wan 接受音频而非生成。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=wan-2-7).

## 工作原理

技能调用 `runcomfy run wan-ai/wan-2-7/text-to-video` 并传入符合模式的 JSON 正文。CLI 向 `https://model-api.runcomfy.net/v1/models/wan-ai/wan-2-7/text-to-video` 发送 POST 请求，轮询请求状态，获取结果，并将 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **Token 存储**：`runcomfy login` 将 API token 写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。在 CI / 容器中设置 `RUNCOMFY_TOKEN` 环境变量可绕过文件存储。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会对提示进行 shell 扩展；它直接将 JSON 正文通过 HTTPS 传输给模型 API。提示内容不会产生 shell 注入风险。
- **第三方内容**：您传递的图像 / 掩码 / 视频链接由 RunComfy 模型服务器获取，而非您机器上的 CLI。将外部 URL 视为不可信；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出下载白名单）。无遥测数据，无回调。
- **生成文件大小上限**：CLI 会中止任何大于 2 GiB 的单个下载，以防止恶意或失控的模型输出导致磁盘空间耗尽。
