# Seedance 2.0 Pro — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2) · [Seedance 2.0 Pro](https://www.runcomfy.com/models/bytedance/seedance-v2/pro?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/seedance-v2)

ByteDance **Seedance 2.0 Pro** — 具备原生唇形同步音频的多模态电影感视频生成器 — 运行在 **RunComfy Model API** 上。

```bash
npx skills add agentspace-so/runcomfy-skills --skill seedance-v2 -g
```

## 选择此模型（与同类对比）

Seedance 2.0 Pro 的独特优势是**多模态电影感短视频**：将人物图像、场景视频与参考音频整合为一致的镜头。当**对参考身份/场景的还原度有要求且需要原生唇形同步**时选择它。

| 你需要 | 使用 |
|---|---|
| 带唇形同步的解说 / 对话广告 | **Seedance 2.0 Pro** |
| 多模态参考（图像 + 视频 + 音频） | **Seedance 2.0 Pro** |
| 品牌一致的多语言叙事 | **Seedance 2.0 Pro** |
| 当前盲评视频质量第一 | HappyHorse 1.0 |
| 使用自有曲目驱动的唇形同步 | Wan 2.7 (`audio_url`) |
| 现有素材的运动剪辑 | Kling Video O1 |
| 极速迭代 | LTX 2 |

若用户明确提及 "Seedance" / "Seedance 2" / "ByteDance 视频"，无论何种情况，均路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账号** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 在 CI / 容器中设置 `RUNCOMFY_TOKEN= <token>`，替代 `runcomfy login`。

## 接口端点与输入模式

### `bytedance/seedance-v2/pro`

| 字段 | 类型 | 是否必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | yes | — | 中文 ≤ 500 字符，或英文 ≤ 1000 词。 |
| `image_url` | array | no | `[]` | 0–9 条参考（JPEG/PNG/WebP/BMP/TIFF/GIF）。 |
| `video_url` | array | no | `[]` | 0–3 段素材（MP4/MOV），每段 2–15 秒。 |
| `audio_url` | array | no | `[]` | 0–3 条音频参考（WAV/MP3），2–15 秒，每条 < 15MB。 |
| `aspect_ratio` | enum | no | `adaptive` | `adaptive`、`16:9`、`9:16`、`4:3`、`3:4`、`1:1`、`21:9`。 |
| `duration` | int | no | 5 | 4–15（整秒）。 |
| `resolution` | enum | no | `720p` | `480p` 或 `720p`。 |
| `generate_audio` | bool | no | true | 生成过程中同步的语音 / 音效 / 音乐。 |
| `seed` | int | no | — | 可复现性。 |

## 调用方式

**默认（仅文本，5 秒，720p 带音频）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{"prompt": "<user prompt>"}' \
  --output-dir <absolute/path/
```

**带人物参考的唇形同步广告（图像稳定、文本演变）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "Medium close-up. The woman explains today'\''s special in a warm friendly tone, slow push-in, soft window light, gentle cafe ambience.",
    "image_url": ["https://.../barista-headshot.jpg"],
    "duration": 8,
    "aspect_ratio": "9:16"
  }' \
  --output-dir <absolute/path/
```

**多模态（图像 + 视频 + 音频参考）：**

```bash
runcomfy run bytedance/seedance-v2/pro \
  --input '{
    "prompt": "Subject from image 1 walks through the café from video 1, voice tone matches audio 1.",
    "image_url": ["https://.../subject.jpg"],
    "video_url": ["https://.../cafe-locked-shot.mp4"],
    "audio_url": ["https://.../voice-ref.mp3"]
  }' \
  --output-dir <absolute/path/
```

The CLI 提交请求、轮询、获取结果，并将 `*.runcomfy.net` / `*.runcomfy.com` URL 下载到 `--output-dir`。

## 提示词 — 实际有效的写法

**图像与文本的划分。** 这是最重要的一条规则。稳定的身份（面部、服装、品牌标识、logo）→ 放入 `image_url`。演变的叙事（动作、情绪、光线、镜头）→ 放入 `prompt`。用文字详细描述面部会浪费 token 并产生偏移。

**镜头与运动用通俗语言。** "Medium close-up"（中近景）、"slow push-in"（缓慢推镜）、"handheld follow"（手持跟随）、"locked-off wide"（固定广角）均可作为指令。组合使用：`"Medium close-up. Slow push-in over 3 seconds. Handheld, slight breathing motion."`

**`generate_audio: true` 下的音频方向** — 说明语气：`"warm friendly conversational"`（温暖友好的对话）、`"calm instructional"`（平静的指导）、`"crisp newsroom delivery"`（清晰的播报语气）。环境音效：`"gentle cafe chatter, distant traffic, no foreground music"`（轻柔的咖啡馆交谈、远处的交通声、无前景音乐）。

**参考素材规格** — 视频必须为 2–15 秒；音频必须 ≤15MB 且 2–15 秒。超出范围的素材将被拒绝。将参考素材的比例与输出比例匹配，以避免裁剪。

**反模式（应避免的做法）：**
- 混合极不相同的审美参考（水彩 + 写实）→ 会混淆。
- 提示词中存在冲突的风格线索 → 通过移除矛盾来简化。
- 试图用文字描述稳定的身份 → 改用 `image_url`。
- 要求 >15 秒的素材 → 422；需拆分多次调用。

## 优势场景

| 使用场景 | Seedance 2.0 Pro 的优势原因 |
|---|---|
| **解说 / 对话广告** | 原生在生成过程中的唇形同步，无需额外的 TTS 步骤 |
| **品牌一致的多语言叙事** | 图像参考保持身份，文本驱动翻译 |
| **电影感短视频电影预演** | 镜头语法 + 多模态参考 |
| **带有参考音乐 / 配音语调的广告创意** | 音频参考指导声音 / 氛围，且不锁定唇形同步 |
| **可复现的变体测试** | 种子控制 + 固定模式 |

## 示例提示词（经验证可产出优质结果）

**默认演示示例：**

```
Golden hour on a quiet cafe terrace: a barista wipes the counter, then
looks up and explains today's special in a friendly tone, natural
lip-sync. Medium close-up, slow push-in; warm side light, soft bokeh
through glass, gentle cafe ambience and subtle film grain.
```

**多模态唇形同步（文本 + 图像）：**

```
Same person as image 1 in a softly-lit recording booth, leaning into
the mic, says: "We just shipped the biggest update of the year."
Calm conversational tone. Medium close-up, locked tripod, shallow DOF,
warm key light from camera-left.
```

## 限制

- **时长 4–15 秒** — 此接口不支持更长时长的素材。
- **Playground 版本的清晰度上限为 720p。**
- **参考素材规格** — 视频 / 音频必须为 2–15 秒；音频 < 15MB。
- **唇形同步质量** — 取决于提示词清晰度，并非在所有条件下都能保证完美。
- **不使用 `@` 语法绑定角色** — 依赖图像参考与提示词对齐。

## 退出码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或 token 被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=seedance-v2)。

## 工作原理

该技能调用 `runcomfy run bytedance/seedance-v2/pro`，并传入符合模式的结构化 JSON 请求体。CLI 向 `https://model-api.runcomfy.net/v1/models/bytedance/seedance-v2/pro` POST 请求，轮询请求，获取结果，并将任何 `.runcomfy.net` / `.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 可在退出前取消远程请求。

## 安全与隐私

- **Token 存储**：`runcomfy login` 会将 API token 写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者读写）。在 CI / 容器中设置 `RUNCOMFY_TOKEN` 环境变量，可完全绕过该文件。
- **输入边界**：用户提示词通过 `--input` 以 JSON 字符串的形式传递给 CLI。CLI 不会对提示词进行 shell 展开；它会直接将 JSON 请求体通过 HTTPS 传输到 Model API。提示词内容不存在 shell 注入风险。
- **第三方内容**：您传入的图像 / 掩码 / 视频 URL 由 RunComfy 模型服务器获取，而非由您本机上的 CLI 获取。请将外部 URL 视为不可信；对于任何图像编辑 / 视频编辑模型而言，基于图像的提示词注入都是已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）以及 `*.runcomfy.net` / `*.runcomfy.com`（生成结果的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI 会中止任何单个超过 2 GiB 的下载，以防止恶意或失控模型输出导致磁盘占满。
