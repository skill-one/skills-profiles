# Seedance 2.0 Pro — 专业包在 RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2) · [Seedance 2.0 Pro](https://www.runcomfy.com/models/bytedance/seedance-v2/pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/seedance-v2)

字节跳动 **Seedance 2.0 Pro** — 多模态电影级视频生成器，具有原生口型同步音频 — 在 **RunComfy 模型 API** 上托管。

```bash
npx skills add agentspace-so/runcomfy-skills --skill seedance-v2 -g
```

## 何时选择此模型（与兄弟模型对比）

Seedance 2.0 Pro 的独特优势是 **多模态电影级短形式**：将角色图像 + 场景视频 + 参考音频组合成一个连贯的镜头。当 **对参考身份/场景的保真度很重要且您需要原生口型同步** 时选择它。

| 您想要 | 使用 |
|---|---|
| 口型同步代言人 / 对话广告 | **Seedance 2.0 Pro** |
| 多模态参考（图像 + 视频 + 音频） | **Seedance 2.0 Pro** |
| 品牌一致的多语言叙事 | **Seedance 2.0 Pro** |
| 目前 #1 盲选视频质量 | HappyHorse 1.0 |
| 基于您自己的音轨的口型同步音频 | Wan 2.7 (`audio_url`) |
| 现有素材的运动编辑 | Kling Video O1 |
| 超快迭代 | LTX 2 |

如果用户明确提到 "Seedance" / "Seedance 2" / "字节跳动视频"，无论什么情况都将其路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开一个浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `bytedance/seedance-v2/pro`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | CN ≤ 500 字符 OR EN ≤ 1000 词。 |
| `image_url` | array | 否 | `[]` | 0–9 个参考（JPEG/PNG/WebP/BMP/TIFF/GIF）。 |
| `video_url` | array | 否 | `[]` | 0–3 个片段（MP4/MOV），每个 2–15 秒。 |
| `audio_url` | array | 否 | `[]` | 0–3 个音频参考（WAV/MP3），每个 2–15 秒，< 15MB。 |
| `aspect_ratio` | enum | 否 | `adaptive` | `adaptive`, `16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `21:9`。 |
| `duration` | int | 否 | 5 | 4–15（整秒）。 |
| `resolution` | enum | 否 | `720p` | `480p` 或 `720p`。 |
| `generate_audio` | bool | 否 | true | 在过程中同步语音 / 音效 / 音乐。 |
| `seed` | int | 否 | — | 可重复性。 |

## 如何调用

**默认（仅文本，5 秒，720p 带音频）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{"prompt": "<用户提示>"}' \
  --output-dir <绝对路径>
```

**口型同步广告（带角色参考，图像稳定，文本演变）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "中景。一位女士以温暖友好的语气解释今天的特别活动，缓慢推进，柔和的窗户光线，轻柔的咖啡馆氛围。",
    "image_url": ["https://.../咖啡师头像.jpg"],
    "duration": 8,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <绝对路径>
```

**多模态（图像 + 视频 + 音频参考）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "图像 1 中的主体走过咖啡馆，从视频 1 中，语音语调匹配音频 1。",
    "image_url": ["https://.../主体.jpg"],
    "video_url": ["https://.../咖啡馆锁定镜头.mp4"],
    "audio_url": ["https://.../语音参考.mp3"]
  }' \
  --output-dir <绝对路径>
```

CLI 提交、轮询、获取结果，将 `*.runcomfy.net`/`*.runcomfy.com` URL 下载到 `--output-dir`。

## 提示 — 实际有效的内容

**图像与文本划分。** 这是唯一最重要的规则。稳定身份（面部、服装、品牌标志、标志）→ 放入 `image_url`。演变叙事（动作、情绪、光线、摄像机）→ 放入 `prompt`。试图用语言详细描述面部会浪费 token 并产生漂移。

**用普通语言描述摄像机 + 运动。** "中景"、"缓慢推进"、"手持跟随"、"锁定广角" 都可以作为指令。组合："中景。在 3 秒内缓慢推进。手持，轻微呼吸运动。"

**带 `generate_audio: true` 的音频方向** — 描述语调："温暖友好对话"、"平静指导"、"清晰新闻播报"。对于环境："轻柔咖啡馆闲聊、远处交通、无前景音乐"。

**参考媒体规格** — 视频必须为 2–15 秒；音频必须 ≤15MB 且 2–15 秒。超出范围的文件会被拒绝。将参考的宽高比与输出匹配以避免裁剪。

**反模式：**
- 混合截然不同的美学参考（水彩 + 照片真实）→ 令人困惑。
- 提示中存在冲突的风格线索 → 通过删除矛盾来简化。
- 用语言描述稳定身份 → 使用 `image_url`。
- 要求 >15 秒的片段 → 422；分成多个调用。

## 此模型的优势

| 用例 | 为什么 Seedance 2.0 Pro |
|---|---|
| **代言人 / 对话广告** | 原生过程中口型同步，无需单独 TTS 步骤 |
| **品牌一致的多语言叙事** | 图像参考保持身份；文本驱动翻译 |
| **电影级短形式预演** | 摄像机语法 + 多模态参考 |
| **带参考音乐 / VO 语调的广告创意** | 音频参考引导声音 / 情绪，无需锁定口型同步 |
| **可重复的变体测试** | 种子控制 + 固定模式 |

## 示例提示（验证可产生强力结果）

**默认游乐场示例：**

```
黄金时刻在安静的咖啡馆露台上：一位咖啡师擦拭柜台，然后抬头以友好的语气回答今天的特别活动，自然口型同步。中景，缓慢推进；温暖侧光，透过玻璃的柔和焦外，轻柔的咖啡馆氛围和微妙的胶片颗粒。
```

**多模态口型同步（文本 + 图像）：**

```
与图像 1 中同一个人在柔和照明的录音棚中，向麦克风倾斜，说："我们刚刚发布了今年最大的更新。" 平静对话语调。中景，锁定三脚架，浅景深，左侧相机主光。
```

## 限制

- **时长 4–15 秒** — 此端点不处理更长的片段。
- **分辨率上限 720p** 在游乐场变体上。
- **参考媒体规格** — 视频 / 音频必须为 2–15 秒；音频 < 15MB。
- **口型同步质量** — 取决于提示的清晰度；在所有条件下都不保证完美。
- **无 `@`-语法用于角色绑定** — 依赖于图像参考 + 提示对齐。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 坏 CLI 参数 |
| 65 | 坏输入 JSON / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2).

## 工作原理

技能调用 `runcomfy run bytedance/seedance-v2/pro` 并使用符合模式的 JSON 正文。CLI POST 到 `https://model-api.runcomfy.net/v1/models/bytedance/seedance-v2/pro`，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **Token 存储**：`runcomfy login` 将 API token 写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量以完全绕过文件，在 CI / 容器中使用。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会对提示进行 shell 扩展；它直接将 JSON 正文通过 HTTPS 传输到模型 API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像 / 掩码 / 视频URL由 RunComfy 模型服务器获取，而不是您机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
