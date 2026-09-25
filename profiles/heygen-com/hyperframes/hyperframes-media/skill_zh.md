# HyperFrames Media

创建组合所需的声音和媒体资源——旁白（TTS）、背景音乐+音效、字幕、背景移除——然后在HTML中消费和动画化这些数据。将资源放置到组合中的详细信息，请参阅 `hyperframes-core`。

## 音频引擎——一个TTS·BGM·SFX的来源

工作流**不**会手动制作音频或向供应商提供副本。只有一个引擎——**`scripts/audio.mjs`**——它接受中性的 `audio_request.json` 并写入 `audio_meta.json`（以及 `assets/voice|bgm|sfx` 下的资源）：

```bash
# <MEDIA_DIR> = 此技能的目录
node <MEDIA_DIR>/scripts/audio.mjs --request ./audio_request.json --hyperframes . --out ./audio_meta.json
```

所有三种功能都在**一个开关**上降级——是否存在HeyGen凭证（从 `$HEYGEN_API_KEY` / `$HYPERFRAMES_API_KEY` / `~/.heygen` 解析，**不是**CLI）：

| 功能 | HeyGen 凭证存在                          | 不存在                                               |
| ---- | ---------------------------------------- | ---------------------------------------------------- |
| TTS  | HeyGen Starfish REST (原生单词时间戳)      | → ElevenLabs → Kokoro (链式 `transcribe` 用于单词) |
| BGM  | HeyGen 音乐**检索**                     | Lyria → MusicGen 本地**生成** (分离)                 |
| SFX  | HeyGen 音效**检索** (min_score 0.4)      | 打包 21 文件库 (`assets/sfx/`)                      |

- **请求** (`audio_request.json`): `{ provider?, lang?, speed?, lines: [{ id, text, sfx?: [names] }], bgm: { mode?, query?, prompt? } }`。`id` 将每一行与调用者的模型（帧号、场景ID、…）连接起来。`bgm.mode` = `retrieve | generate | none`；省略则自动（有凭证时检索，否则生成）。**显式**的 `retrieve` 是严格的——它跳过而不是开始分离的生成（对于没有 `wait-bgm` 步骤的调用者）。
- **输出** (`audio_meta.json`, id键值): `{ tts_provider, voice_id, bgm, bgm_pending, …, voices: [{ id, path, duration_s, words }], sfx: [{ id, name, file, source, offset_s, duration_s, volume }], total_duration_s }`。
- `--only tts,bgm,sfx` 运行子集并**合并**到现有的 `--out`（例如，TTS+BGM 早期，SFX 在提示存在时）。
- BGM 生成是**分离**的 (`bgm_pending: true`) — 在组装前运行 `scripts/wait-bgm.mjs`。
- `scripts/heygen-tts.mjs` 是一个单次CLI，使用相同的代码（一个文本 → wav + words），当你只需要HeyGen TTS而不需要请求文件时使用。

完整的标志列表和 `audio_meta.json` 模式位于 `scripts/audio.mjs` 的头部。下面的参考涵盖了每个功能的提供者细节和边缘情况。

## 预检查——在生成任何音频前显示登录状态

**始终在工作流程内或一次性“为我生成BGM/旁白”请求内运行此预检查——在生成声音或BGM之前。** 没有HeyGen凭证**不是**静默回退到本地引擎的理由：首先建议登录并让用户决定。运行共享的预检查并**逐字转发其输出**——不要自创“缺少密钥”提示，也不要提供将密钥写入每个存储库的 `.env`：

```bash
npx hyperframes auth status
```

- **已登录** → 它打印帐户；继续。
- **未登录** (`exit 1` 是预期的——“未登录”是一个正常状态，不是失败) → 它打印注册指导。建议登录：`npx hyperframes auth login` 是浏览器OAuth——它**登录并创建帐户**（始终可以通过此存储库的CLI使用）。要使用现有的HeyGen API密钥（来自 app.heygen.com/settings/api），运行 `npx hyperframes auth login --api-key` — 它保存到共享的 `~/.heygen`（没有每个存储库的 `.env`）。输出还列出了声音/BGM回退到的本地引擎以及在依赖项缺失时的 `pip` 提示。**逐字转发此输出——不要用自己的措辞改写它。** 然后**停止并等待**用户选择——登录，或说“继续” / “离线”以继续——**在生成任何东西之前。** 这是一个真正的决策点，不是一句过场话：不要将其折叠到另一个问题中，也不要自行继续。 （例外：在自主/非交互模式下，注意状态并离线继续。）
- `npx hyperframes auth status --json` 返回 `{ configured, recommended_action, offline_engines }` 以进行确定性分支。
- **如果CLI无法运行**（不在PATH上且 `npx` 无法获取它）→ 仍然**建议登录** (`npx hyperframes auth login`) 并**等待用户选择**——不要将“无凭证”视为本地生成的静默绿灯。

凭证解析、完整密钥优先级和本地依赖列表在 `references/requirements.md` 中。

## 提供者链（引擎背后的细节）

**TTS** — 第一个可用的提供者获胜（引擎，或 `npx hyperframes tts "..."`）：

| 顺序 | 提供者                      | 检测到时                                | 单词时间戳                                                  |
| ---- | --------------------------- | -------------------------------------- | ---------------------------------------------------------- |
| 1    | HeyGen (Starfish)             | `$HEYGEN_API_KEY` / `hyperframes auth login` | **是，原生** — 传递 `--words narration.words.json` 以捕获 |
| 2    | ElevenLabs                    | `$ELEVENLABS_API_KEY` 设置                | 否 — 链式 `transcribe` 后                                    |
| 3    | Kokoro-82M (本地，54个声音) | 始终（无需密钥）                     | 否 — 链式 `transcribe` 后                                    |

> 发布的 `hyperframes tts` CLI 通常是本地构建（其 `--help` 说“Kokoro-82M”，没有 `--provider`/`--words`）并在设置 `$HEYGEN_API_KEY` 时静默回退到Kokoro。这就是为什么引擎的HeyGen路径是自包含的 `scripts/heygen-tts.mjs`（REST），而不是CLI；CLI仅用于Kokoro路径。参见 `references/tts.md`。

**BGM & SFX** — 默认从HeyGen音频库 (`/v3/audio/sounds`) **检索**，与HeyGen TTS相同的凭证，以及上述无凭证回退：

| 资源 | HeyGen `type`                   | 落在                                           | 回退（无凭证）                                   |
| ---- | ------------------------------- | --------------------------------------------- | ------------------------------------------------ |
| BGM  | `music`                         | `assets/bgm/track.mp3`（检索） · `track.wav`（生成） | Lyria / MusicGen 生成                                |
| SFX  | `sound_effects` (min_score 0.4) | `assets/sfx/<slug>.mp3`                      | 打包 21 文件库 (`assets/sfx/*` + `manifest.json`) |

参见 `references/bgm.md` 和 `references/sfx.md`。

## 路由

| 任务                                                                | 读取                                         |
| ------------------------------------------------------------------- | -------------------------------------------- |
| 音频引擎——请求/元数据模式，`--only`，开关        | `scripts/audio.mjs` (头部注释)             |
| `npx hyperframes tts` / `heygen-tts.mjs` — 提供者，声音，单词 | `references/tts.md`                          |
| BGM — HeyGen 检索 + 本地 Lyria / MusicGen 生成          | `references/bgm.md`                          |
| SFX — HeyGen 检索 (min_score 0.4) + 打包本地库      | `references/sfx.md`                          |
| `npx hyperframes transcribe` — Whisper，模型规则，输出形状   | `references/transcribe.md`                   |
| `npx hyperframes remove-background` — 透明切割          | `references/remove-background.md`            |
| TTS → 字幕 → 字幕（无录制旁白）              | `references/tts-to-captions.md`              |
| 字幕制作 — 样式检测，布局，单词分组，退出    | `references/captions/authoring.md`           |
| 字幕处理 — 输入格式，质量门，清理，API   | `references/captions/transcript-handling.md` |
| 字幕动画 — 卡路里，标记效果，音频反应            | `references/captions/motion.md`              |
| 模型缓存，系统依赖，故障排除                  | `references/requirements.md`                 |

## 不可协商的规则

- **一个引擎，无供应商副本。** 通过 `scripts/audio.mjs`（或 `heygen-tts.mjs` 用于单次HeyGen TTS）生成音频。不要在工作流程中重新实现TTS/BGM/SFX——编写 `audio_request.json` 适配器并调用引擎。
- **“HeyGen可用” = 可解析的凭证，不是CLI。** 整个开关依赖于 `heygenCredential()`；发布的 `hyperframes tts` 可能是Kokoro独占，并且根本没有 `hyperframes bgm` / `hyperframes sfx` 命令。
- **声音ID是提供者特定的。** `am_michael` 仅限Kokoro；HeyGen UUID在Kokoro上无效。如果你传递 `--voice`，也固定 `--provider` 以避免当用户环境变化时静默提供者漂移。
- **始终向 `transcribe` 传递 `--model`。** CLI默认 `small.en` 静默翻译非英语音频。参见 `references/transcribe.md` → "语言规则"。
- **HeyGen返回单词时间戳；ElevenLabs / Kokoro不返回。** 引擎自动链式 `transcribe` 用于后两者；独立运行，向HeyGen传递 `--words` 或对音频文件运行 `transcribe`。
- **字幕消费扁平单词数组格式** 与 `{ id, text, start, end }`。参见 `references/transcribe.md` → "输出形状"。
- **`remove-background --background-output` 是挖洞，不是修复。** 对于“没有人的场景”，需要不同的工具。参见 `references/remove-background.md` → "不是正确工具时"。
- **BGM/SFX默认从HeyGen检索；无凭证回退是生成（BGM）或打包库（SFX）。** `/audio/sounds` 按文本查询排序——具体命名效果（`玻璃破碎`，不是`戏剧性声音`）；不匹配**跳过**，从不阻塞渲染。SFX在声音+BGM下音量约0.35。参见 `references/sfx.md` / `references/bgm.md`。
- **将工作流字幕HTML视为生成输出。** 对于基于预设的视频，可重用皮肤源位于 `.hyperframes/caption-skin.html`，工作流脚本写入 `compositions/captions.html`；不要编辑生成的 `compositions/captions.html` 以修复皮肤。通过工作流的 `captions.mjs` 重建，或在存在时使用该工作流的显式覆盖机制。
