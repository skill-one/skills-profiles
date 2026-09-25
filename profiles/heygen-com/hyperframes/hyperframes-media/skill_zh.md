# HyperFrames Media

为成片所需创建音频与媒体资源——旁白（TTS）、背景音乐与音效、转写、字幕、背景去除——然后在 HTML 中消费并动画化这些数据。如需将资源放入成片，请参阅 `hyperframes-core`。

## 音频引擎——TTS · BGM · 音效的统一来源

工作流不会自行实现音频或引入副本。仅有一个引擎——**`scripts/audio.mjs`**——接收中立的 `audio_request.json`，生成 `audio_meta.json`（以及 `assets/voice`、`assets/bgm`、`assets/sfx` 下的资源）：

```bash
# <MEDIA_DIR} = this skill's directory
node <MEDIA_DIR>/scripts/audio.mjs --request ./audio_request.json --hyperframes . --out ./audio_meta.json
```

这三项能力均由**一个开关**决定降级——即是否存在 HeyGen 凭证（从 `$HEYGEN_API_KEY` / `$HYPERFRAMES_API_KEY` / `~/.heygen` 解析，**而非** CLI）：

| 能力 | HeyGen 凭证存在 | 不存在 |
| ---------- | -------------------------------------------------- | ---------------------------------------------------- |
| TTS        | HeyGen Starfish REST（原生词时间戳）      | → ElevenLabs → Kokoro（用 `transcribe` 链式获取词） |
| BGM        | HeyGen 音乐 **检索**                         | Lyria → MusicGen 本地 **生成**（分离运行）         |
| SFX        | HeyGen 音效 **检索**（min_score 0.4）          | 内置 21 文件库（`assets/sfx/`）                    |

- **请求**（`audio_request.json`）：`{ provider?, lang?, speed?, lines: [{ id, text, sfx?: [names] }], bgm: { mode?, query?, prompt? } }`。`id` 将每行回关联到调用方的模型（帧号、场景 ID、……）。`bgm.mode` = `retrieve | generate | none`；自动时省略（凭证存在则检索，否则生成）。**显式**的 `retrieve` 为严格模式——若调用方无 `wait-bgm` 步骤，则跳过而非启动分离式生成。
- **输出**（`audio_meta.json`，以 id 为键）：`{ tts_provider, voice_id, bgm, bgm_pending, …, voices: [{ id, path, duration_s, words }], sfx: [{ id, name, file, source, offset_s, duration_s, volume }], total_duration_s }`。
- `--only tts,bgm,sfx` 仅运行子集，并**合并**到已有的 `--out`（例如早期运行 TTS+BGM，待提示存在后再运行 SFX）。
- BGM 生成以**分离**方式启动（`bgm_pending: true`）——在组装前运行 `scripts/wait-bgm.mjs`。
- `scripts/heygen-tts.mjs` 是同一代码的**单次** CLI（一段文本 → wav + 词）——适用于无需请求文件仅需 HeyGen TTS 的场景。

`scripts/audio.mjs` 的头部注释包含完整参数列表与 `audio_meta.json` 模式。下方的引用覆盖了各项能力的提供商详情与边界情况。

## 预检——在生成任何音频前展示登录状态

**在生成语音或 BGM 之前始终执行此步骤——在完整工作流中，或是一次性的“为我生成 BGM/旁白”请求中。** 不存在 HeyGen 凭证**不是**静默回退到本地引擎的理由：先建议用户登录，由其决定。运行共享预检并**逐字传递其输出**——不要自行编造“缺少密钥”的提示，也不要提议将密钥写入单个仓库的 `.env`：

```bash
npx hyperframes auth status
```

- **已登录** → 输出账号；继续。
- **未登录**（此处预期 `exit 1`——“未登录”是正常状态，而非失败）→ 输出首步注册引导。建议登录：`npx hyperframes auth login` 为浏览器 OAuth——**登录并创建账户**（始终可通过本仓库的 CLI 使用）。如需使用现有 HeyGen API key（来自 app.heygen.com/settings/api），运行 `npx hyperframes auth login --api-key`——保存至共享的 `~/.heygen`（不使用单个仓库的 `.env`）。输出还会列出语音/BGM 将回退的本地引擎，以及在依赖缺失时提供 `pip` 提示。**原样传递此输出——不要将其改写为自己的措辞。** 然后**停下并等待**用户选择——登录，或说“继续”（go）/“本地”（local）以离线继续——**在生成任何内容之前。** 这是一个真实的决策点，而非一笔带过的说明：不要将其并入另一个问题，也不要自行越过该步骤继续。
  （例外：在自主/非交互模式下，记录状态并离线继续。）
- `npx hyperframes auth status --json` 返回 `{ configured, recommended_action, offline_engines }`，用于确定性的分支判断。
- **如果 CLI 无法运行**（不在 PATH 上且 `npx` 无法获取它）→ 仍**建议登录**（`npx hyperframes auth login`）并**等待用户选择**——不要将“无凭证”视为本地生成的静默绿灯。

凭证解析、完整密钥优先级与本地依赖列表见 `references/requirements.md`。

## 提供商链（引擎背后的细节）

**TTS**——最先可用的提供商胜出（引擎，或 `npx hyperframes tts "..."`）：

| 顺序 | 提供商 | 检测条件 | 词时间戳 |
| ----- | ----------------------------- | -------------------------------------------- | ---------------------------------------------------------------- |
| 1     | HeyGen（Starfish）             | `$HEYGEN_API_KEY` / `hyperframes auth login` | **是，原生**——用 `--words narration.words.json` 捕获 |
| 2     | ElevenLabs                    | `$ELEVENLABS_API_KEY` 已设置                    | 否——之后链式 `transcribe` |
| 3     | Kokoro-82M（本地，54 个声音） | 始终（无需密钥）                          | 否——之后链式 `transcribe` |

> 已发布的 `hyperframes tts` CLI 往往是仅本地的构建版本（其 `--help` 显示“Kokoro-82M”，无 `--provider`/`--words`），即便设置了 `$HEYGEN_API_KEY` 也会静默回退到 Kokoro。因此，引擎的 HeyGen 路径是自包含的 `scripts/heygen-tts.mjs`（REST），而非 CLI；该 CLI 仅用于 Kokoro 路径。参见 `references/tts.md`。

**BGM 与 SFX**——默认从 HeyGen 音频库（`/v3/audio/sounds`）**检索**，与 HeyGen TTS 使用相同的凭证，并结合上文开关所述的无凭证回退方案：

| 资源 | HeyGen `type` | 落地位置 | 回退方案（无凭证） |
| ----- | ------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| BGM   | `music`                         | `assets/bgm/track.mp3`（检索） · `track.wav`（生成） | Lyria / MusicGen 生成                                |
| SFX   | `sound_effects`（min_score 0.4） | `assets/sfx/<slug>.mp3`                                    | 内置 21 文件库（`assets/sfx/*` + `manifest.json`）              |

参见 `references/bgm.md` 与 `references/sfx.md`。

## 路由

| 任务                                                                | 查阅 |
| ------------------------------------------------------------------- | -------------------------------------------- |
| 音频引擎——请求/元模式、`--only`、开关 | `scripts/audio.mjs`（头部注释）         |
| `npx hyperframes tts` / `heygen-tts.mjs`——提供商、声音、词 | `references/tts.md`                          |
| BGM——HeyGen 检索 + 本地 Lyria / MusicGen 生成 | `references/bgm.md`                          |
| SFX——HeyGen 检索（min_score 0.4）+ 内置本地库 | `references/sfx.md`                          |
| `npx hyperframes transcribe`——Whisper、模型规则、输出形状 | `references/transcribe.md`                   |
| `npx hyperframes remove-background`——透明抠图 | `references/remove-background.md`            |
| TTS → 转写 → 字幕（无录制的旁白） | `references/tts-to-captions.md`              |
| 字幕编写——风格检测、布局、词组、退出 | `references/captions/authoring.md`           |
| 转录处理——输入格式、质量检查、清理、API | `references/captions/transcript-handling.md` |
| 字幕动效——卡拉 OK、标记效果、音频响应式 | `references/captions/motion.md`              |
| 模型缓存、系统依赖、故障排查 | `references/requirements.md`                 |

## 不可妥协的规则

- **单一引擎，不引入副本。** 通过 `scripts/audio.mjs`（或 `heygen-tts.mjs` 进行一次性 HeyGen TTS）生成音频。不要在工作流内重新实现 TTS/BGM/SFX——编写一个 `audio_request.json` 适配器并调用引擎。
- **“HeyGen 可用” = 可解析的凭证，而非 CLI。** 整个开关以 `heygenCredential()` 为依据；已发布的 `hyperframes tts` 可能仅支持 Kokoro，且根本不存在 `hyperframes bgm` / `hyperframes sfx` 命令。
- **声音 ID 具有提供商特定性。** `am_michael` 仅适用于 Kokoro；HeyGen UUID 在 Kokoro 上无效。若传入 `--voice`，还需固定 `--provider`，以避免用户在环境变化时出现静默的提供商偏移。
- **始终向 `transcribe` 传入 `--model`。** CLI 默认的 `small.en` 会静默将非英文音频翻译。参见 `references/transcribe.md` → “Language Rule”。
- **HeyGen 返回词时间戳；ElevenLabs / Kokoro 则不。** 引擎会自动为后两者链式调用 `transcribe`；若单独使用，则对 HeyGen 传入 `--words`，或对音频文件运行 `transcribe`。
- **字幕使用 `{ id, text, start, end }` 的平铺词数组格式。** 参见 `references/transcribe.md` → “Output Shape”。
- **`remove-background --background-output` 是镂空抠图，而非修复填充。** 针对“去掉人物后的场景”，需要其他工具。参见 `references/remove-background.md` → “When NOT the right tool”。
- **BGM/SFX 默认采用 HeyGen 检索；无凭证回退为生成（BGM）或内置库（SFX）。** `/audio/sounds` 按文本查询排序——具体命名效果（`glass shatter`，而非 `dramatic sound`）；无匹配时**跳过**，而非阻塞渲染。SFX 在语音与 BGM 之下音量约 0.35。参见 `references/sfx.md` / `references/bgm.md`。
- **将工作流字幕 HTML 视为生成输出。** 对于预设驱动的视频，可复用皮肤源位于 `.hyperframes/caption-skin.html`，工作流脚本写入 `compositions/captions.html`；不要编辑生成的 `compositions/captions.html` 来修复皮肤。通过工作流的 `captions.mjs` 重新构建，或在存在该工作流显式覆盖机制时使用该机制。
