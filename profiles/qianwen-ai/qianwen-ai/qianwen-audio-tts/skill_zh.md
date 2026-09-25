# Qwen Audio TTS (文本转语音)

使用 Qwen TTS 模型从文本合成自然语音。
此技能是 **QianWen-AI/qianwen-ai** 的一部分。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 目的 |
|------|------|
| `scripts/tts.py` | Qwen TTS (HTTP API) — qwen3-tts-*, qwen-audio-3.0-tts-* |
| `scripts/tts_cosyvoice.py` | CosyVoice (WebSocket / HTTP NRT) — 需要 `dashscope` SDK |
| `references/cosyvoice-guide.md` | CosyVoice 设置、声音、示例、错误 |
| `references/execution-guide.md` | 备用：curl (标准、指令、流式传输)、代码生成 |
| `references/prompt-guide.md` | 用于语音的文本格式化、指令模板、声音选择 |
| `references/api-guide.md` | API 补充 |
| `references/sources.md` | 官方文档 URL |

## 安全

**永远不要明文输出任何 API 密钥或凭证。** 始终使用变量引用 (`$DASHSCOPE_API_KEY` 在 shell 中，`os.environ["DASHSCOPE_API_KEY"]` 在 Python 中)。任何凭证检查或检测都必须是**非明文**：仅报告状态（例如 "已设置" / "未设置"，"有效" / "无效"），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，永远不要直接要求用户提供它。** 相反，请帮助创建一个 `.env` 文件，其中包含占位符 (`DASHSCOPE_API_KEY=sk-your-key-here`)，并指导用户将其替换为他们从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取的实际密钥。仅在用户明确要求时才写入实际密钥值。

## 密钥兼容性

支持 PAYG (`sk-ws-...`; 遗留 `sk-...`) 和 Token Plan (`sk-sp-...`) 密钥。检测密钥类型而不暴露密钥：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qianwen_lib import detect_api_key_type
print(detect_api_key_type('scripts/qianwen_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | Token Plan 密钥 — 仅使用 Token Plan 目录下提供的模型。 |
| `payg` | 按量付费密钥 — 可使用完整模型目录。 |
| `not-set` | 未配置密钥。 |

对于 Token Plan，获取并读取当前的 [Token Plan 模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，然后在 `scripts/tts.py` 中使用精确列出的模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-token-plan-models.md)。

### 执行前：基于密钥的模型决策

在调用 TTS 脚本之前，通过其前缀（通过 `scripts/qianwen_lib.py` 进行非明文检查）确定密钥类型，然后获取并读取当前的 [Qwen 音频 TTS 模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-audio-tts-models.md) 以进行脚本兼容性、推荐和默认设置。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-audio-tts-models.md)。

Token Plan 仅支持特定模型 — 请使用上述参考中的模型；不要猜测或探测模型可用性。对于 PAYG，请继续下方操作。

## 模型选择

在选择、推荐或默认设置模型之前，请使用上面链接的 Qwen 音频 TTS 模型目录。它包含模型列表、基本模型信息、脚本和声音兼容性、推荐和默认设置。

> **⚠️ 重要**：模型目录是一个**特定时间点的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，请始终检查[官方模型列表](https://www.qianwenai.com/models)以获取权威、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qianwenai.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果 **qianwen-model-selector** 技能或 **QianWen CLI** (`qianwen models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qianwen-usage** 技能的登录流程。

## 可用声音

使用上面链接的 Qwen 音频 TTS 模型目录以获取当前模型到声音的兼容性和默认设置。要获取完整的声音清单，请使用 [sources.md](references/sources.md) 中的官方声音列表链接。

### 自定义声音（v3.5 所需）

cosyvoice-v3.5 模型需要一个自定义声音 ID。要创建一个，请执行以下操作：
1. 访问 [声音克隆](https://platform.qianwenai.com/docs/developer-guides/speech/voice-cloning)
2. 上传一个 10-20 秒的干净语音样本
3. 获取自定义声音 ID
4. 通过 `--voice <id>` 或 `"voice": "<id>"` 在请求 JSON 中传递

## 执行

> **⚠️ 多个工件**：在单个会话中生成多个文件时，您**必须**给每个文件名添加一个数字后缀（例如 `out_1.wav`，`out_2.wav`）以防止覆盖。

### Qwen TTS (HTTP API) — `tts.py`

#### 前置条件

- **API 密钥**：使用 **密钥兼容性** 中的非明文检测器；不要用变量存在性检查来替换它。如果找不到密钥，当可用时使用 qianwen-ops-auth，或指导用户在 `.env` 中配置 `DASHSCOPE_API_KEY`/`QIANWEN_API_KEY`。技能可以独立安装。
- Python 3.9+（仅使用标准库，**不需要 pip 安装**）

#### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果找不到 `python3`，请尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，请跳转到 [execution-guide.md](references/execution-guide.md) 中的 **Path 2 (curl)**。

#### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行脚本。** 不要假设脚本位于当前工作目录中。不要在执行之前使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本 — 等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/tts.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/tts.py \
  --request '{"text":"Hello, this is a test.","voice":"longanlingxin"}' \
  --output output/qianwen-audio-tts/ \
  --print-response
```

| 参数 | 描述 |
|------|------|
| `--request '{...}'` | JSON 请求体 |
| `--file path.json` | 从文件加载请求 |
| `--output path` | 将音频和响应 JSON 保存到目录，或指定音频文件路径（例如 `speech.mp3`）；跨调用使用不同的文件名以避免覆盖 |
| `--print-response` | 将响应打印到 stdout |
| `--model ID` | 覆盖模型 |
| `--voice NAME` | 覆盖声音 |
| `--format` | Qwen-Audio-TTS NRT 模型的音频格式 (`mp3` 默认，`wav`，`pcm`) |
| `--sample-rate` | Qwen-Audio-TTS NRT 模型的采样率 (Hz) (默认：24000) |

> **模型优先级**：`--model` CLI 标志 > `"model"` 字段在 `--request` JSON 中 > 内置默认值。

#### 验证结果

- 退出代码 `0` + 输出包含有效的 JSON 且有 `output.audio` 字段 → **成功**
- 非零退出、HTTP 错误、空响应或错误 JSON → **失败**
- **执行后检查**：验证输出音频文件是否存在且大小非零 (`ls -la <output_dir>`)
- **强制 — stderr 信号检查**：在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [更新检查](#update-check-mandatory-post-execution) 中的说明执行操作。

#### 失败

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（Path 2 — 标准、指令、流式传输）、代码生成 (Path 3) 和自动解决 (Path 5)。

**如果完全找不到 Python** → 直接跳转到 [execution-guide.md](references/execution-guide.md) 中的 Path 2 (curl)。

---

### CosyVoice — `tts_cosyvoice.py`

CosyVoice 需要 `dashscope` SDK。快速入门：

```bash
pip install dashscope>=1.25.17
python3 <this-skill-dir>/scripts/tts_cosyvoice.py --text "Hello"
```

> **完整指南**：[cosyvoice-guide.md](references/cosyvoice-guide.md)（设置、声音、示例、错误）

| 错误模式 | 诊断 | 解决方案 |
|----------|------|--------|
| `command not found: python3` | Python 未在 PATH 中 | 尝试 `python` 或 `py -3`；如果缺少，请安装 Python 3.9+ |
| `Python 3.9+ required` | 脚本版本检查失败 | 升级 Python 到 3.9+ |
| `SyntaxError` near type hints | Python < 3.9 | 升级 Python 到 3.9+ |
| `QIANWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取密钥；将密钥添加到 `.env`：`echo 'DASHSCOPE_API_KEY=sk-...' >> .env`；或者如果可用，运行 **qianwen-ops-auth** |
| `HTTP 401` | 无效或匹配的密钥不正确 | 运行 **qianwen-ops-auth**（仅非明文检查）；验证密钥是否有效 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问 | 检查网络；如果使用代理，设置 `HTTPS_PROXY` |
| `HTTP 429` | 被限流 | 等待并使用退避重试 |
| `HTTP 5xx` | 服务器错误 | 使用退避重试 |
| `PermissionError` | 无法写入输出 | 使用 `--output` 指定可写目录 |

## 快速参考

### 请求字段 (Qwen3-TTS HTTP API — `tts.py`)

| 字段 | 类型 | 描述 |
|------|------|------|
| `text` | string | **必需** — 要合成的文本（最多 600 个字符） |
| `voice` | string | **必需** — 声音 ID（例如 `Cherry`，`Ethan`） |
| `model` | string | 模型 ID；检查上面模型目录中的当前默认值 |
| `language_type` | string | `Auto`，`Chinese`，`English`，`Japanese`，`Korean`，`French`，`German` 等 |
| `instructions` | string | 语气/风格指令；检查上面模型目录中的当前模型兼容性和限制 |
| `optimize_instructions` | bool | 当为 true 时，系统对 `instructions` 进行语义增强以获得更好的自然度。需要设置 `instructions`。默认：false |
| `stream` | bool | 启用流式传输（Base64 数据块） |

### 请求字段 (CosyVoice NRT API — `tts_cosyvoice.py`)

| 字段 | 类型 | 描述 |
|------|------|------|
| `text` | string | **必需** — 要合成的文本（每次调用最多 20,000 个字符） |
| `voice` | string | **必需** — 声音 ID（模型特定，请参阅声音列表） |
| `model` | string | 模型 ID；检查上面模型目录中的当前默认值 |
| `instruction` | string | 用于语音控制的自由风格指令；检查上面模型目录中的当前模型兼容性 |
| `language_hints` | list | 目标语言提示：`zh`，`en`，`fr`，`de`，`ja`，`ko`，`ru`，`pt`，`th`，`id`，`vi` 等 |
| `format` | string | 音频格式：`mp3`（默认），`wav`，`pcm`，`opus` |
| `sample_rate` | int | 采样率 (Hz)：8000，16000，22050（默认），24000，44100，48000 |

### 响应字段

| 字段 | 描述 |
|------|------|
| `audio_url` | 生成的音频 URL（有效 24 小时） |
| `audio_format` | 格式（例如 wav） |
| `sample_rate` | 采样率（例如 24000） |
| `usage` | 字符使用量 |

## 重要说明

- **text**：每次请求最多 600 个字符（Qwen3-TTS）。最多 20,000 个字符（CosyVoice/Qwen-Audio-TTS NRT）。
- **instructions / instruction 模型兼容性**：检查上面模型目录，然后使用为所选模型记录的参数形式。
- **language_type** (Qwen3-TTS)：`Auto` 用于混合语言；指定以获得更好的发音。
- **language_hints** (CosyVoice/Qwen-Audio-TTS)：指定目标语言代码 (`zh`，`en` 等) 以提高合成质量。
- **audio_url**：有效期为 24 小时 — 请立即下载。
- **实时/流式 TTS**：对于基于 WebSocket 的实时 TTS（CosyVoice，qwen3-tts-flash-realtime），需要一个 WebSocket 客户端。此技能涵盖基于 HTTP 的非实时 API。对于实时流式用例，请参考 [sources.md](references/sources.md) 中的官方文档。

## 跨技能链接

当将生成的音频传递给另一个技能（例如视频生成音频叠加）时：
- 直接传递 `audio_url` — 脚本检测 URL 前缀并通过而不重新上传
- 仅使用 `audio_file` 进行本地播放或非 API 操作

## 错误处理

| 错误 | 原因 | 操作 |
|------|------|------|
| `401 Unauthorized` | 无效或缺少 API 密钥 | 如果可用，运行 **qianwen-ops-auth**；否则提示用户设置密钥（仅非明文检查） |
| `400` | 无效参数（缺少文本/声音） | 验证请求体 |
| `429` / `5xx` | 速率限制或服务器错误 | 使用退避重试 |

> **使用和计费**：使用 **qianwen-usage** 技能检查使用情况、免费套餐配额和计费。或者，用户可以访问 QianWen 控制台：
> [使用分析](https://platform.qianwenai.com/home/analytics) |
> [按量付费计费](https://platform.qianwenai.com/home/billing/pay-as-you-go) |
> [Token Plan 订阅](https://platform.qianwenai.com/home/billing/subscription/token-plan)
>
> **永远不要编造、猜测或构造使用/计费/控制台 URL。** 仅提供此技能中列出的确切链接。如果此处未列出 URL，请不要编造一个。

## 输出位置

优先使用**当前工作目录**。默认子目录：`./output/qianwen-audio-tts/`。

**写入禁止**：永远不要将输出文件写入此技能的安装目录或任何 `skills/` 层次结构。所有生成的内容必须位于当前工作目录下的 `output/` 或用户指定路径中。

## 更新检查（执行后强制）

脚本执行后，检查 stderr 以查找操作信号。脚本自动检测更新状态并发出结构化信号。您必须对此采取行动。本节也适用于用户明确要求检查更新时。

### 信号：`[ACTION_REQUIRED] qianwen-update-check 技能未安装`

当 stderr 包含此信号时，您必须向用户展示以下选项，并**等待他们的响应后再继续**。不要无声地跳过。

> 更新检查技能未安装。它让您了解 QianWen-AI/qianwen-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何事情
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QianWen-AI/qianwen-ai --skill qianwen-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须将简短的更新通知添加到您的响应中，包括版本信息和 stderr 输出中显示的更新命令。

### stderr 中没有信号

如果 stderr 中既没有 `[ACTION_REQUIRED]` 也没有 `[UPDATE_AVAILABLE]`，则无需采取行动 — 技能已安装且是最新的（或在 24 小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如 "检查更新"，"检查版本"）时：
1. 在同级技能目录中查找 `qianwen-update-check/SKILL.md`。
2. 如果找到 — 运行：`python3 <qianwen-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到 — 显示上面的安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 备用路径（curl 标准/指令/流式传输、代码生成、自主）
- [api-guide.md](references/api-guide.md) — API 补充指南
- [sources.md](references/sources.md) — 官方文档 URL
