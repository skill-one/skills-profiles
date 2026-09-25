# Qwen Audio TTS (文本转语音)

使用 Qwen TTS 模型从文本合成自然语音。
此技能是 **qwencloud/qwencloud-ai** 的一部分。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 目的 |
|------|------|
| `scripts/tts.py` | Qwen TTS / Qwen Audio TTS (HTTP 和 WebSocket)；当前兼容性和默认值在下面的模型目录中 |
| `scripts/tts_cosyvoice.py` | CosyVoice (WebSocket API) — 需要 `dashscope` SDK；当前兼容性和默认值在下面的模型目录中 |
| `references/cosyvoice-guide.md` | CosyVoice 设置、声音、示例、错误 |
| `references/execution-guide.md` | 备用：curl (标准、指令、流式传输)、代码生成 |
| `references/prompt-guide.md` | 用于语音的文本格式化、指令模板、声音选择 |
| `references/api-guide.md` | API 补充 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要以明文形式输出任何 API 密钥或凭证。** 始终使用变量引用 (`$QWENCLOUD_API_KEY` 在 shell 中，`os.environ["QWENCLOUD_API_KEY"]` 在 Python 中)。脚本接受 `QWENCLOUD_API_KEY`，然后是 `QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`。任何凭证检查或检测都必须是**非明文**：仅报告状态（例如 "已设置" / "未设置"，"有效" / "无效"），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的 内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符 (`QWENCLOUD_API_KEY=sk-your-key-here`)，并指示用户用他们从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 的实际密钥替换它。只有在用户明确要求时才写入实际密钥值。

## 密钥兼容性

脚本支持**标准 QwenCloud API 密钥** (`sk-...`) 和**令牌计划密钥** (`sk-sp-...`)。令牌计划密钥会自动路由到支持 TTS 模型的令牌计划端点——见下文 [令牌计划支持](#token-plan-support)。

**令牌计划：不要使用 curl；始终使用捆绑的 Python 脚本。**

编码计划密钥（也具有 `sk-sp-` 前缀但通过编码计划订阅购买）不能使用——TTS 模型在编码计划中不可用。脚本在启动时检测密钥类型并进行相应路由。如果安装了 qwencloud-ops-auth，请参阅其 `references/codingplan.md` 获取完整详细信息。

在不暴露密钥的情况下检测 API 密钥类型：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qwencloud_lib import detect_api_key_type
print(detect_api_key_type('scripts/qwencloud_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | 检测到令牌计划密钥 (`sk-sp-` 前缀) |
| `payg` | 检测到标准 PAYG 密钥 |
| `not-set` | 环境中未找到 API 密钥 |

对于令牌计划，获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)，然后使用 `scripts/tts.py` 与确切列出的模型一起使用。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-token-plan-models.md)。

## 模型选择

> **🚫 关键——绝不要覆盖用户选择的模型。** 如果用户（或请求 JSON）明确指定了 `model`，您必须使用完全相同的模型。不要：
> - 用“更适合”的模型替换它（例如，切换到 `qwen3-tts-instruct-flash` 用于风格化/诗意文本）
> - 添加用户未请求的 `instructions`
> - 修改用户明确提供的任何参数
>
> 以下模型选择指导仅适用于**用户未指定模型**时。

在选择、推荐或默认模型之前，获取并阅读当前的 [QwenCloud 音频 TTS 模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-audio-tts-models.md)。它包含模型列表、基本模型信息、脚本和声音兼容性、推荐和默认值。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-audio-tts-models.md)。

当模型选择取决于功能、场景或定价时，请咨询 **qwencloud-model-selector** 技能。CosyVoice 需要 `dashscope` SDK 并使用不同的声音；见 [cosyvoice-guide.md](references/cosyvoice-guide.md)。

> **⚠️ 重要**：模型目录是**特定时间的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查 [官方模型列表](https://www.qwencloud.com/models) 以获取权威的、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qwencloud.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果可用，请使用 **qwencloud-model-selector** 技能或 **QwenCloud CLI** (`qwencloud models info <model>`) 进行实时模型数据。CLI 需要身份验证——请参阅 **qwencloud-usage** 技能以获取登录流程。

## 可用声音

使用上面链接的 QwenCloud 音频 TTS 模型目录以获取当前模型到声音的兼容性和默认值。对于完整的声音清单，请使用 [sources.md](references/sources.md) 中的官方声音列表链接。

> **声音默认值**：当为 Qwen-Audio WebSocket 模型未提供声音时，`tts.py` 选择该模型配置的默认声音并将通知打印到 stderr。任何明确的声音——包括明确的 `Cherry`——都将保持不变。在选择声音之前获取模型目录。

## 执行

> **⚠️ 多个工件**：在单个会话中生成多个文件时，您必须将数字后缀附加到每个文件名（例如 `out_1.wav`，`out_2.wav`）以防止覆盖。

### Qwen TTS (HTTP API) — `tts.py`

#### 前置条件

- **API 密钥**：使用**非明文**检查仅检查 `QWENCLOUD_API_KEY`，`QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`（例如在 shell 中：`[ -n "$QWENCLOUD_API_KEY" ]`；仅报告“已设置”或“未设置”，绝不能显示密钥值）。如果未设置：如果可用，运行 **qwencloud-ops-auth** 技能；否则，指导用户从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取密钥并通过 `.env` 文件（在项目根目录或当前目录中：`echo 'QWENCLOUD_API_KEY=sk-your-key-here' >> .env`）或环境变量设置。脚本在当前工作目录和项目根目录中搜索 `.env`。技能可以独立安装——不要假设 qwencloud-ops-auth 存在。
  **注意**：脚本自动从当前目录和项目根目录加载 `.env`（除了任何导出的环境变量）。显示 `$QWENCLOUD_API_KEY` 作为“未设置”的 shell 检查**并不意味着脚本会失败——它可能仍在 `.env` 中找到密钥**。将 shell 检查视为仅供参考；权威测试是简单地运行脚本（如果任何地方找不到密钥，它会以清晰的错误退出）。
- Python 3.9+（仅使用标准库，**不需要 pip 安装**）

#### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果 `python3` 不可用或低于 3.9，PAYG 可能使用**路径 2 (curl)**；令牌计划必须安装 Python 3.9+。

#### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行脚本。** 不要假设脚本在当前工作目录中。执行前**不要**使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本——等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/tts.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/tts.py \
  --request '{"text":"Hello, this is a test.","voice":"Cherry"}' \
  --output output/qwencloud-audio-tts/ \
  --print-response
```

| 参数 | 描述 |
|------|------|
| `--request '{...}'` | JSON 请求正文 |
| `--file path.json` | 从文件加载请求 |
| `--output path` | 将音频和响应 JSON 保存到目录，或指定音频文件路径（例如 `speech.mp3`）；跨调用使用不同的文件名以避免覆盖 |
| `--print-response` | 将响应打印到 stdout |
| `--model ID` | 覆盖模型 |
| `--voice NAME` | 覆盖声音 |

#### 验证结果

- 退出代码 `0` + 输出包含有效的 JSON 并具有 `output.audio` 字段 → **成功**
- 非零退出、HTTP 错误、空响应或错误 JSON → **失败**
- **执行后检查**：确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [执行后强制更新检查](#update-check-mandatory-post-execution) 下的说明进行操作。

#### 失败

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（路径 2 — 标准、指令、流式传输）、代码生成（路径 3）和自主解决（路径 5）。

**如果完全无法使用 Python** → PAYG 可能使用 Path 2 (curl)；令牌计划必须安装 Python 3.9+。

---

### CosyVoice — `tts_cosyvoice.py`

CosyVoice 需要 `dashscope` SDK。快速入门：

```bash
pip install dashscope>=1.25.17
python3 <this-skill-dir>/scripts/tts_cosyvoice.py --text "Hello"
```

> **令牌计划**：`tts_cosyvoice.py` 在启动时拒绝令牌计划密钥。获取上面链接的令牌计划目录，并使用确切支持的 TTS 模型与 `tts.py`，或使用 PAYG 密钥。未经用户确认，绝不要替换明确请求的模型。

> **完整指南**：[cosyvoice-guide.md](references/cosyvoice-guide.md)（设置、声音、示例、错误）

| 错误模式 | 诊断 | 解决方案 |
|----------|------|----------|
| `command not found: python3` | Python 未在 PATH 中 | 尝试 `python` 或 `py -3`；如果缺少，则安装 Python 3.9+ |
| `Python 3.9+ required` | 脚本版本检查失败 | 升级 Python 到 3.9+ |
| `SyntaxError` near type hints | Python < 3.9 | 升级 Python 到 3.9+ |
| `cosyvoice models are not available on Token Plan` | 检测到令牌计划密钥 | 使用 `tts.py` 与令牌计划目录中确切支持的模型，或使用 PAYG 密钥 |
| `QWENCLOUD_API_KEY/QWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取密钥；将其添加到 `.env`：`echo 'QWENCLOUD_API_KEY=sk-...' >> .env`；如果可用，则运行 **qwencloud-ops-auth** |
| `HTTP 401` | 无效或密钥不匹配 | 运行 **qwencloud-ops-auth**（仅非明文检查）；验证密钥是否有效 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问 | 检查互联网；如果通过代理，请设置 `HTTPS_PROXY` |
| `HTTP 429` | 被限流 | 等待并退避重试 |
| `HTTP 5xx` | 服务器错误 | 退避重试 |
| `PermissionError` | 无法写入输出 | 使用 `--output` 指定可写目录 |

## 快速参考

### 请求字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `text` | string | **必需** — 要合成的文本；检查上面模型目录中的模型特定限制 |
| `voice` | string | 声音 ID；检查上面模型目录中的当前默认值和兼容性 |
| `model` | string | 模型 ID；检查上面模型目录中的当前默认值 |
| `language_type` | string | `Auto`，`Chinese`，`English`，`Japanese`，`Korean`，`French`，`German` 等。— 全名，不是代码 (`zh`，`en`) |
| `instructions` | string | 语气/风格指令；检查上面模型目录中的当前兼容性和限制 |
| `volume` | int | 音量 `[0-100]`，默认 50 — 仅限 WebSocket 模型；检查模型目录 |
| `rate` | float | 语音速率 `[0.5-2.0]`，默认 1.0；低于 1.0 减慢语音 — **仅限 WebSocket 模型** |
| `pitch` | float | 音高乘数 `[0.5-2.0]`，默认 1.0；高于 1.0 提高音高 — **仅限 WebSocket 模型** |
| `sample_rate` | int | Hz 中的采样率，默认 24000 — **仅限 WebSocket 模型** |
| `format` | string | 音频格式：`mp3`/`wav`/`pcm`/`opus`，默认 `mp3` — **仅限 WebSocket 模型** |
| `stream` | bool | 直接 Qwen3-TTS HTTP API 字段用于 SSE 流式传输。捆绑的 `tts.py` 未实现此字段；使用 [execution-guide.md](references/execution-guide.md) 中的直接 SSE 路径 |

### 响应字段

| 字段 | 描述 |
|------|------|
| `audio_url` | 生成的音频 URL（有效 24 小时） |
| `audio_format` | 格式（例如 wav） |
| `sample_rate` | 采样率（例如 24000） |
| `usage` | 字符使用量 |

## 重要说明

- **text**：检查上面模型目录中选定模型的当前请求限制。
- **instructions**：支持是模型特定的；检查上面模型目录后再使用它。
- **language_type**：`Auto` 用于混合语言；指定以获得更好的发音。值是全名 (`Chinese`，`English`，`Japanese`，...), 不是代码 (`zh`，`en`)。它仅适用于兼容的 HTTP 模型；脚本会忽略 WebSocket 模型的语言，其语言遵循选定的声音。
- **audio_url**：有效期为 24 小时——请立即下载。
- **实时/流式 TTS**：捆绑的 `tts.py` 使用非流式 HTTP 用于 Qwen3-TTS，仅使用原始 WebSocket 用于 Qwen-Audio TTS；CosyVoice 由 `tts_cosyvoice.py` 处理。Qwen3-TTS API 本身支持可选的 SSE；在需要时使用 [execution-guide.md](references/execution-guide.md) 中的直接示例。

## 跨技能链接

当将生成的音频传递给另一个技能（例如，视频生成音频叠加）时：
- **直接传递 `audio_url`** — 脚本检测 URL 前缀并直接传递，无需重新上传
- 仅用于本地播放或非 API 操作使用 `audio_file`

## 错误处理

| 错误 | 原因 | 操作 |
|------|------|------|
| `401 Unauthorized` | 无效或缺少 API 密钥 | 如果可用，运行 **qwencloud-ops-auth**；否则提示用户设置密钥（仅非明文检查） |
| `400` | 无效参数（缺少 text/voice） | 验证请求正文 |
| `429` / `5xx` | 速率限制或服务器错误 | 退避重试 |

> **使用情况 & 计费**：使用 **qwencloud-usage** 技能直接检查使用情况、免费层配额和计费。或者，用户可以访问 QwenCloud 控制台：
> [使用分析](https://home.qwencloud.com/analytics) |
> [按量计费](https://home.qwencloud.com/billing/pay-as-you-go) |
> [编码计划计费](https://home.qwencloud.com/billing/coding-plan)
>
> 当前定价模型列表和计费单位，请获取 [CDN 模型计费参考](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-pricing.md)。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-model-pricing.md)。
>
> **绝不要编造、猜测或构造使用情况/计费/控制台 URL。** 仅提供此技能中列出的确切链接。如果此 URL 未在此处列出，请不要编造一个。

## 输出位置

优先使用**当前工作目录**。默认子目录：`./output/qwencloud-audio-tts/`。

**写入禁止**：绝不要将输出文件写入此技能的安装目录或任何 `skills/` 层级。所有生成的内容必须位于当前工作目录的 `output/` 下或用户指定路径。

## 令牌计划支持

令牌计划仅支持 TTS 模型的子集。获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md) 以选择或验证模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-token-plan-models.md)。

当令牌计划密钥与不支持的模型组合时，`tts.py` 会将错误打印到 stderr，列出当前支持的模型并建议替代方案；它不会阻止调用。如果您看到此警告，请告诉用户当前目录支持哪些模型，并提供目录列出的替代方案或使用 PAYG 密钥获取原始模型。绝不要无声地替换用户明确请求的模型。

对于 CosyVoice 特别注意，`tts_cosyvoice.py` **在启动时硬阻止**令牌计划密钥。使用 `tts.py` 与当前令牌计划目录中列出的模型，或使用 PAYG 密钥。

### 令牌计划上的样式控制

仅使用音频模型目录中支持选定令牌计划模型的样式控制字段。以下是当前支持模型的协议示例；不要用它替换用户指定的模型：

```json
{"text": "落霞与孤鹜齐飞，秋水共长天一色。", "model": "qwen-audio-3.0-tts-plus", "rate": 0.8, "pitch": 1.1, "volume": 60}
```

- `rate` 低于 1.0 减慢语音，高于 1.0 加快语音
- `pitch` 高于 1.0 提高音高，低于 1.0 降低音高
- `volume` 线性缩放（0 = 静音，50 = 默认，100 = 最大）

### 协议说明

[QwenCloud 模型页面](https://www.qwencloud.com/models/qwen-audio-3.0-tts-plus) 记录了 `qwen-audio-3.0-tts-plus` 的 **WSS (WebSocket)**。脚本包含一个 WebSocket 路径分支，该分支：
1. 连接到 `wss://token-plan.ap-southeast-1.maas.aliyuncs.com/api-ws/v1/inference`（或 PAYG 的标准端点）
2. 在 WebSocket 握手时设置 `User-Agent: qwencloud-skills`
3. 发送 run-task → continue-task → finish-task 消息
4. 接收二进制音频帧并将它们连接到输出文件

### 必需的标题

`User-Agent: qwencloud-skills` 会自动包含在 HTTP 和 WebSocket 请求中。

## 更新检查 (执行后强制)

脚本执行后，检查 stderr 以获取操作信号。脚本自动检测更新状态并发出结构化信号。您必须对此采取行动。本节也适用于用户明确要求检查更新时。

### 信号：`[ACTION_REQUIRED] qwencloud-update-check 技能未安装`

当 stderr 包含此信号时，您必须向用户展示以下选项并**等待他们的响应后再继续**。不要无声地跳过。

> 更新检查技能未安装。它让您了解 qwencloud/qwencloud-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我会为您运行安装命令
> 2) **暂时跳过** — 这次不做任何事
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QwenCloud/qwencloud-ai --skill qwencloud-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须将简短的更新通知附加到您的响应中，包括版本信息和 stderr 输出中显示的更新命令。

### stderr 中没有信号

如果 stderr 既不包含 `[ACTION_REQUIRED]` 也不包含 `[UPDATE_AVAILABLE]`，则无需操作——技能已安装且是最新的（或 24 小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如，“检查更新”，“检查版本”）：
1. 在兄弟技能目录中查找 `qwencloud-update-check/SKILL.md`。
2. 如果找到——运行：`python3 <qwencloud-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到——显示上面的安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 备用路径 (curl 标准/指令/流式传输、代码生成、自主)
- [api-guide.md](references/api-guide.md) — API 补充指南
- [sources.md](references/sources.md) — 官方文档 URL
