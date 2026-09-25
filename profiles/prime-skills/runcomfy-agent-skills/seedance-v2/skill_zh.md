# Seedance 2.0 Pro — 专业包在 RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2) · [Seedance 2.0 Pro](https://www.runcomfy.com/models/bytedance/seedance-v2/pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/seedance-v2)

字节跳动 **Seedance 2.0 Pro** — 多模态电影级视频生成器，支持原生口型同步音频 — 部署在 **RunComfy 模型 API** 上。

```bash
npx skills add agentspace-so/runcomfy-skills --skill seedance-v2 -g
```

## 何时选择此模型（与兄弟模型对比）

Seedance 2.0 Pro 的独特优势是 **多模态电影级短剧**：结合角色图片 + 场景视频 + 参考音频生成一个连贯镜头。当 **对参考身份/场景的保真度要求高且需要原生口型同步** 时选择它。

| 您需要 | 使用 |
|---|---|
| 口型同步代言人/对话广告 | **Seedance 2.0 Pro** |
| 多模态参考（图片 + 视频 + 音频） | **Seedance 2.0 Pro** |
| 品牌一致的多语言叙事 | **Seedance 2.0 Pro** |
| 当前 #1 盲选视频质量 | HappyHorse 1.0 |
| 基于您自备音轨的口型同步 | Wan 2.7 (`audio_url`) |
| 现有素材的运动编辑 | Kling Video O1 |
| 超快迭代 | LTX 2 |

如果用户明确提到 "Seedance" / "Seedance 2" / "字节跳动视频"，无论何种情况都应路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `bytedance/seedance-v2/pro`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | CN ≤ 500 字符 OR EN ≤ 1000 词。 |
| `image_url` | array | 否 | `[]` | 0–9 参考图片（JPEG/PNG/WebP/BMP/TIFF/GIF）。 |
| `video_url` | array | 否 | `[]` | 0–3 片段（MP4/MOV），每段 2–15 秒。 |
| `audio_url` | array | 否 | `[]` | 0–3 音频参考（WAV/MP3），每段 2–15 秒，< 15MB。 |
| `aspect_ratio` | enum | 否 | `adaptive` | `adaptive`, `16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `21:9`。 |
| `duration` | int | 否 | 5 | 4–15（整秒）。 |
| `resolution` | enum | 否 | `720p` | `480p` 或 `720p`。 |
| `generate_audio` | bool | 否 | true | 生成同步语音 / 音效 / 音乐。 |
| `seed` | int | 否 | — | 可重复性。 |

## 如何调用

**默认（仅文本，5 秒，720p 带音频）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{"prompt": "<用户提示>"}' \
  --output-dir <绝对路径>
```

**口型同步广告（带角色参考，图片稳定，文本演变）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "中景。一位女士用温暖友好的语气解释今天的特别推荐，缓慢推进镜头，柔和的窗户光线，咖啡馆氛围。",
    "image_url": ["https://.../咖啡师头像.jpg"],
    "duration": 8,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <绝对路径>
```

**多模态（图片 + 视频 + 音频参考）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "图片 1 中的主体走过咖啡馆，步调与视频 1 匹配，语音语调与音频 1 匹配。",
    "image_url": ["https://.../主体.jpg"],
    "video_url": ["https://.../咖啡馆锁定镜头.mp4"],
    "audio_url": ["https://.../语音参考.mp3"]
  }' \
  --output-dir <绝对路径>
```

CLI 提交、轮询、获取结果，将 `*.runcomfy.net`/`*.runcomfy.com` URL 下载到 `--output-dir`。

## 提示 — 实际有效的部分

**图片与文本分割。** 这是唯一最重要的规则。稳定身份（面部、服装、品牌标志、Logo）→ 放入 `image_url`。演变叙事（动作、情绪、光线、摄像机）→ 放入 `prompt`。试图用语言详细描述面部会浪费 token 并导致漂移。

**用普通语言描述摄像机 + 运动。** "中景"、"缓慢推进镜头"、"手持跟拍"、"固定宽景" 都可以作为指令。组合使用：`"中景。3 秒内缓慢推进镜头。手持，轻微呼吸动作。"`

**带 `generate_audio: true` 的音频方向** — 描述语调：`"温暖友好的对话式"`, `"冷静指导式"`, `"清晰新闻播报式"`。用于环境音：`"轻柔咖啡馆交谈，远处交通声，无前景音乐"`。

**参考媒体规格** — 视频必须 2–15 秒；音频必须 ≤15MB 且 2–15 秒。超出范围的文件会被拒绝。将输出参考的宽高比与您的输出匹配，以避免裁剪。

**反模式：**
- 混合截然不同的美学参考（水彩 + 照片真实）→ 会导致混淆。
- 提示中存在冲突的风格提示 → 通过移除矛盾来简化。
- 用语言描述稳定身份 → 使用 `image_url`。
- 要求 >15 秒的片段 → 422；分段多次调用。

## 优势领域

| 用例 | 为什么选择 Seedance 2.0 Pro |
|---|---|
| **代言人/对话广告** | 原生口型同步，无需单独 TTS 步骤 |
| **品牌一致的多语言叙事** | 图片参考保持身份；文本驱动翻译 |
| **电影级短剧预演** | 摄像机语法 + 多模态参考 |
| **带参考音乐/VO 语调的广告创意** | 音频参考引导语音/情绪，不锁定口型同步 |
| **可重复的变体测试** | 种子控制 + 固定模式 |

## 示例提示（验证可生成强结果）

**默认游乐场示例：**

```
黄金时刻在安静的咖啡馆露台上：一位咖啡师擦拭柜台，然后抬头用友好的语气解释今天的特别推荐，自然口型同步。中景，缓慢推进镜头；温暖侧光，透过玻璃的柔和焦外，轻柔咖啡馆氛围和微妙的胶片颗粒。
```

**多模态口型同步（文本 + 图片）：**

```
与图片 1 中同一个人在柔和光线的录音棚中，靠近麦克风，说："我们刚刚发布了今年最大的更新。" 冷静对话式语调。中景，固定三脚架，浅景深，左侧主光。
```

## 限制

- **时长 4–15 秒** — 此端点不支持更长的片段。
- **分辨率上限 720p** 在游乐场变体上。
- **参考媒体规格** — 视频/音频必须 2–15 秒；音频 < 15MB。
- **口型同步质量** — 取决于提示清晰度；并非所有情况下都能保证完美。
- **无 `@`-语法角色绑定** — 依赖图片参考 + 提示对齐。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2).

## 工作原理

技能调用 `runcomfy run bytedance/seedance-v2/pro` 并传入符合模式的 JSON 正文。CLI 向 `https://model-api.runcomfy.net/v1/models/bytedance/seedance-v2/pro` 发送 POST 请求，轮询请求，获取结果，并将 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **Token 存储**：`runcomfy login` 将 API token 写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过文件，适用于 CI / 容器。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会对提示进行 shell 扩展；它直接将 JSON 正文通过 HTTPS 传输到模型 API。提示内容不会产生 shell 注入风险。
- **第三方内容**：您传递的图片/蒙版/视频 URL 由 RunComfy 模型服务器获取，而非您机器上的 CLI。将外部 URL 视为不可信；基于图片的提示注入是任何图像/视频编辑模型已知的风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出下载白名单）。无遥测数据，无回调。
- **生成文件大小上限**：CLI 会中止任何 > 2 GiB 的单个下载，以防止恶意或失控的模型输出导致磁盘填满。
