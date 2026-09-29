---
name: qianwen-video-generation
description: 使用 Wan 和 HappyHorse 模型生成视频。支持文本转视频、图像转视频、首尾帧生成、参考式角色扮演以及视频编辑（VACE）。触发条件：当用户想要创建、生成或编辑视频内容，提及视频生成/动画/视频片段/Wan/HappyHorse 模型，或明确调用此技能名称（例如使用 qianwen-video-generation）。不触发条件：当用户想要生成图像（使用 qianwen-image-generation）、理解/分析现有视频（使用 qianwen-vision），或仅涉及文本的任务。
---

# Qwen 视频生成

使用 Wan 和 HappyHorse 模型生成视频。所有任务都是 **异步** 的 — 提交后轮询直到完成。
这项技能是 **QianWen-AI/qianwen-ai** 的一部分。

> **⚠️ 关键参数差异:**
> - **kf2v (首帧+尾帧)**: 持续时间固定为 **5 秒** — 其他值将失败。输出为 **仅静音**。
> - **分辨率参数因模型系列而异，而非仅因模式而异**: 选择 `size`、`resolution` 或 `ratio` 之前，请检查当前的模型目录。例如，`happyhorse-1.1-t2v` 使用 `resolution` + `ratio`，而 `wan2.6-t2v` 使用 `size`。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 用途 |
|------|------|
| `scripts/video.py` | 默认执行 — 自动检测模式、提交、轮询、下载 |
| `references/execution-guide.md` | 备用：对所有 5 种模式使用 curl，代码生成 |
| `references/request-fields.md` | 字段表格和按模式音频处理 |
| `references/workflows.md` | 持续时间扩展、多帧、VACE 管道 |
| `references/polling-guide.md` | 轮询模式和定时 |
| `references/merge-media.md` | 连接、修剪、音频覆盖 — ffmpeg/moviepy 配方 |
| `references/prompt-guide.md` | 按模式的提示公式、声音描述、多帧结构 |
| `references/examples.md` | 按模式的完整脚本示例 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要明文输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$DASHSCOPE_API_KEY`，Python 中的 `os.environ["DASHSCOPE_API_KEY"]`）。任何凭证检查或检测都必须 **非明文**: 仅报告状态（例如 "已设置" / "未设置"、"有效" / "无效"），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的 内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符（`DASHSCOPE_API_KEY=sk-your-key-here`），并指导用户用他们实际的密钥从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys) 替换它。只有在用户明确要求时才写入实际密钥值。

## 密钥兼容性

支持 PAYG (`sk-ws-...`; 遗留 `sk-...`) 和 Token Plan (`sk-sp-...`) 密钥。检测 API 密钥类型而不暴露密钥：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qianwen_lib import detect_api_key_type
print(detect_api_key_type('scripts/qianwen_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | Token Plan 密钥 — 仅使用 Token Plan 目录中的模型。 |
| `payg` | 按量付费密钥 — 可使用完整模型目录。 |
| `not-set` | 未配置密钥。 |

对于 Token Plan，获取并阅读当前的 [Token Plan 模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，然后使用确切列出的模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-token-plan-models.md)。

Token Plan 不支持本地文件上传；对于 i2v/r2v/kf2v 模式，请将参考图像/视频作为可访问的 URL（`https://` 或 `oss://`）提供，而不是本地路径。

Token Plan 仅支持特定模型 — 请使用上述参考中的确切模型；不要猜测或探测模型可用性。对于 PAYG，请继续下方操作。

## 模式选择指南

| 用户需求 | 模式 | 密钥字段 |
|---------|------|----------|
| 仅从文本描述生成视频 | **t2v** | 仅 `prompt` |
| 动画化单张图像 | **i2v** | `img_url` 或 `reference_image` |
| wan2.7 统一 i2v：首帧、首帧+尾帧、视频延续、音频同步 | **i2v** | `media[]`、`first_frame_url`、`first_clip_url`、`driving_audio_url` |
| 在两张图像之间过渡（**⚠️ 5 秒固定，仅静音**） | **kf2v** | `first_frame_url` + `last_frame_url` |
| 角色扮演：让角色表演新剧本 | **r2v** | `reference_urls` 或 `media`；请阅读 CDN 模型目录以了解模型特定的限制 |
| 视频编辑：多图像参考、重绘、本地编辑、扩展、外绘 | **vace** | `function`；请阅读 CDN 模型目录以了解当前默认值 |
| 视频编辑（无 `function` 字段，使用媒体数组） | **videoedit** | `model`；请阅读 CDN 模型目录以了解支持的模型 |

### 模型选择

1. **用户指定了模型** → 直接使用。
2. **当模型选择取决于功能、场景或定价时，请咨询 qianwen-model-selector 技能。**

在选择、推荐或默认模型之前，获取并阅读当前的 [Qwen 视频生成模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-video-generation-models.md)。它包含模型列表、基本模型信息、模式推荐、兼容性说明和默认值。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-video-generation-models.md)。

端点：`/services/aigc/video-generation/video-synthesis`。

> **⚠️ 重要提示**: 上述模型列表是一个 **特定时间点的快照**，可能已过时。模型的可用性经常变化。**在做出模型决策之前，请始终检查 [官方模型列表](https://www.qianwenai.com/models) 以获取权威的、最新的目录。**

> **模型详细信息**: 如需了解特定模型的更多信息，请将用户引导至 `https://www.qianwenai.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**: 如果 **qianwen-model-selector** 技能或 **QianWen CLI** (`qianwen models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qianwen-usage** 技能的登录流程。

## 执行

> **⚠️ 多个生成物**: 在单个会话中生成多个文件时，您 **必须** 为每个文件名添加数字后缀（例如 `out_1.mp4`、`out_2.mp4`），以防止覆盖。

### 前置条件

- **API 密钥**: 使用 **Key 兼容性** 中的非明文检测器；不要用变量存在性检查替换它。如果没有找到密钥，当可用时使用 qianwen-ops-auth，或指导用户在 `.env` 中配置 `DASHSCOPE_API_KEY`/`QIANWEN_API_KEY`。技能可以独立安装。
- Python 3.9+（仅标准库，**无需 pip 安装**）
- 对于媒体合并（连接、修剪、音频覆盖）：请参阅 [merge-media.md](references/merge-media.md) 以获取适合用户环境的 ffmpeg/moviepy 配方

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果找不到 `python3`，请尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，请跳转到 [execution-guide.md](references/execution-guide.md) 中的 **路径 2 (curl)**。

### 默认：运行脚本

**脚本路径**: 脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用完整的绝对路径来执行脚本。** 不要假设脚本位于当前工作目录中。执行前不要使用 `cd` 切换目录。

**执行说明**: 所有脚本都在 **前台** 运行 — 等待 stdout；不要后台运行。

**发现**: 首先运行 `python3 <this-skill-dir>/scripts/video.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/video.py \
  --request '{"model":"happyhorse-1.1-t2v","prompt":"一个雨夜的城市中的侦探","resolution":"720P","ratio":"16:9","duration":5}' \
  --print-response
```

| 参数 | 描述 |
|------|------|
| `--request '{...}'` | JSON 请求体 |
| `--file path.json` | 从文件加载请求 |
| `--mode MODE` | 覆盖自动检测的模式 (t2v/i2v/kf2v/r2v) |
| `--model ID` | 覆盖模型 |
| `--output path` | 目录或文件路径。如果路径以视频扩展名（.mp4/.mov/.webm/.mkv/.m4v 等）结尾，则用作输出文件名（自动创建父目录）。否则视为目录 — 视频将根据 OSS URL 基名自动命名，以防止跨运行覆盖；跨调用使用不同的文件名以避免覆盖响应数据 |
| `--print-response` | 将响应 JSON 打印到 stdout |
| `--submit-only` | 提交并退出（打印 task_id） |
| `--task-id ID` | 对现有任务进行操作 |
| `--poll-interval N` | 轮询间隔秒数（默认：15） |
| `--timeout N` | 最大等待秒数（默认：600） |

> **模型优先级**: `--model` CLI 标志 > `"model"` 字段在 `--request` JSON 中 > 配置的默认值。当未指定模型且未指定时，将使用配置的默认值，但不一定是最新或最强的模型。

### 验证结果

- 退出码 `0` + 响应包含 `output.task_id` → **提交成功**
- 轮询达到 `task_status: SUCCEEDED` → **生成完成**
- 非零退出码、HTTP 错误或 `FAILED` 状态 → **失败**
- **执行后检查**: 验证输出视频文件是否存在且大小非零 (`ls -la <output_dir>`)
- **强制 — stderr 信号检查**: 在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任何信号，您 **必须** 在响应用户之前按照 [更新检查](#update-check-mandatory-post-execution) 中的说明进行操作。

### 失败时

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（路径 2 — 所有 5 种模式）、代码生成（路径 3）和自动解决（路径 5）。

**如果完全找不到 Python** → 直接跳转到 [execution-guide.md](references/execution-guide.md) 中的 **路径 2 (curl)**。

| 错误模式 | 诊断 | 解决方案 |
|---------|------|----------|
| `command not found: python3` | Python 未在 PATH 中 | 尝试 `python` 或 `py -3`；如果缺少，请安装 Python 3.9+ |
| `Python 3.9+ required` | 脚本版本检查失败 | 升级 Python 到 3.9+ |
| `SyntaxError` near type hints | Python < 3.9 | 升级 Python 到 3.9+ |
| `QIANWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys) 获取密钥；添加到 `.env`：`echo 'DASHSCOPE_API_KEY=sk-...' >> .env`；或如果可用，运行 **qianwen-ops-auth** |
| `HTTP 401` | 无效或匹配的密钥不匹配 | 运行 **qianwen-ops-auth**（仅非明文检查）；验证密钥是否有效 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问 | 检查互联网；如果使用代理，请设置 `HTTPS_PROXY` |
| `HTTP 429` | 被限流 | 等待并使用退避重试 |
| `HTTP 5xx` | 服务器错误 | 使用退避重试 |
| `ImportError: moviepy` | 未安装 moviepy | `pip install moviepy`，或使用系统 ffmpeg（请参阅 [merge-media.md](references/merge-media.md)） |
| `PermissionError` | 无法写入输出 | 使用 `--output` 指定可写目录 |

## 请求字段摘要

所有模式都需要 `prompt`。请参阅 [request-fields.md](references/request-fields.md) 以获取每种模式的完整字段表。

### ⚠️ 按模型系列区分的分辨率参数（关键）

分辨率字段因模型系列而异。在在 `size`、`resolution` 和 `ratio` 之间选择之前，请检查上述模型目录；使用错误的字段会导致 API 调用失败。

### 模式特定必需字段

- 必需字段因模型系列而异。使用 [request-fields.md](references/request-fields.md) 获取有效负载形状，并使用上述模型目录获取当前模型特定的兼容性。

## 成本估算

> 🚨 **绝对不要猜测或编造任何价格数字。** 始终将用户引导至 [官方定价页面](https://platform.qianwenai.com/docs/developer-guides/getting-started/pricing) 以获取确切费率。

成本按生成视频的秒数计费。价格因模型和分辨率而异。获取 [CDN 模型定价参考](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-pricing.md)，并使用官方定价页面获取确切当前费率。某些模型可能提供有限的免费配额 — **不要假设任何调用都是免费的**；使用 **qianwen-usage** 技能检查剩余免费层配额，或在用户的 [QianWen 控制台](https://platform.qianwenai.com/home/benefits) 中验证。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-model-pricing.md)。

要检查实际使用量和账单：使用 **qianwen-usage** 技能，或访问控制台：
[使用分析](https://platform.qianwenai.com/home/analytics) |
[按量付费账单](https://platform.qianwenai.com/home/billing/pay-as-you-go) |
[Token Plan 订阅](https://platform.qianwenai.com/home/billing/subscription/token-plan)

> **绝对不要编造、猜测或构造使用量/账单/控制台 URL。** 仅提供此处列出的确切链接。如果此处未列出 URL，请不要编造一个。

## 本地文件处理

当用户提供本地文件路径（图像、视频、音频）时，直接将它们传递给脚本。脚本 **自动上传** 本地文件到 DashScope 临时存储（`oss://` URL，48 小时 TTL），并注入 `X-DashScope-OssResourceResolve: enable` 标头。无需手动上传步骤。

> **生产**: 默认临时存储具有 **48 小时 TTL** 和 **100 QPS 上传限制** — 不适用于生产、高并发或负载测试。要使用您自己的 OSS 存储桶，请在 `.env` 中设置 `QWEN_TMP_OSS_BUCKET` 和 `QWEN_TMP_OSS_REGION`，安装 `pip install alibabacloud-oss-v2`，并通过 `QWEN_TMP_OSS_AK_ID` / `QWEN_TMP_OSS_AK_SECRET` 或标准的 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 提供凭证。使用具有最小权限的 RAM 用户（仅对目标存储桶上的 `oss:PutObject` + `oss:GetObject`）。如果安装了 qianwen-ops-auth，请参阅其 `references/custom-oss.md` 以获取完整的设置指南。

## 跨技能链接

当使用另一个技能的输出作为输入（例如，图像生成 → i2v，音频合成 → 音频覆盖）时：
- **直接传递 URL**（例如，`"img_url": "<image_url from image-gen>"`） — 不要下载并重新传递为本地路径
- 脚本检测 URL 前缀（`https://`，`oss://`）并通过而不重新上传
- 仅使用响应中的 `local_path` 进行用户预览或非 API 操作

当将此技能的输出传递给另一个技能（例如，vace 编辑，视觉分析）时：
- **传递响应中的 `video_url`** — 不要下载并重新传递为本地路径

| 场景 | 使用 |
|------|------|
| 传递给另一个技能 | `video_url` / `image_url` (URL) |
| 显示给用户 / 本地播放 | `local_path` (本地文件) |

## 重要说明

- **仅异步**: 所有视频 API 需要设置 `X-DashScope-Async: enable` 标头。
- **kf2v**: 使用 **不同的 API 端点**。持续时间 **固定为 5 秒**，**仅静音**。
- **r2v**: 在提示中使用 `character1`/`character2`/...。最多 5 个参考（最多 3 个视频）。
- **vace**: 必须指定 `function`。**仅静音**，输出 **≤5 秒**。
- **多帧**: 设置 `shot_type: "multi"` AND `prompt_extend: true`。
- **视频 URL 在 24 小时内过期** — 脚本自动下载到 `--output` 目录。当链接到另一个技能（例如，vace 编辑）时，直接传递 `video_url` — 不要重新下载。
- 对于高级工作流 → 请参阅 [workflows.md](references/workflows.md)。

## 错误处理

| 错误 | 原因 | 操作 |
|------|------|------|
| `401 Unauthorized` | API密钥无效或缺失 | 若可用，运行 **qianwen-ops-auth**；否则提示用户设置密钥（仅进行非明文检查） |
| `current user api does not support synchronous calls` | 缺少异步请求头 | 添加 `X-DashScope-Async: enable` |
| `429` / `5xx` | 速率限制或服务器错误 | 带退避重试 |
| `The product is not activated` / `Model not subscribed` | 账户未启用第三方模型 | 访问 [模型市场](https://www.qianwenai.com/models)，找到模型，点击“启用” / “开通” |
| 任务 `FAILED` | 生成失败 | 检查轮询响应中的 `output.message` |

## 输出位置

优先选择 **当前工作目录**。默认子目录：`./output/qianwen-video-generation/`。

**写入禁止**：绝对不能将输出文件写入此技能的安装目录或任何 `skills/` 层级。所有生成内容必须放置在当前工作目录下的 `output/` 或用户指定路径中。

## 更新检查（执行后强制）

脚本执行后，检查标准错误输出以获取操作信号。脚本自动检测更新状态并发出结构化信号。你必须响应它们。此部分也适用于用户明确要求检查更新时。

### 信号：`[ACTION_REQUIRED] qianwen-update-check 技能未安装`

当标准错误输出包含此信号时，你必须向用户展示以下选项，并在他们响应前**等待其反馈**。不要无声地跳过。

> 更新检查技能未安装。它将让你了解 QianWen-AI/qianwen-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我将为你运行安装命令
> 2) **暂时跳过** — 这次不做任何操作
> 3) **不再提醒** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QianWen-AI/qianwen-ai --skill qianwen-update-check -y`，然后运行：`python3 <此技能脚本目录>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <此技能脚本目录>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <此技能脚本目录>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当标准错误输出包含此信号时，你必须将简短的更新通知追加到你的响应中，包括版本信息和标准错误输出中显示的更新命令。

### 标准错误输出中无信号

如果标准错误输出既不包含 `[ACTION_REQUIRED]` 也不包含 `[UPDATE_AVAILABLE]`，则无需操作 — 技能已安装且为最新（或在24小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如，“检查更新”、“检查版本”）：
1. 在同级技能目录中查找 `qianwen-update-check/SKILL.md`。
2. 若找到 — 运行：`python3 <qianwen-update-check目录>/scripts/check_update.py --print-response` 并报告结果。
3. 若未找到 — 展示上述安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 备用路径（所有模式使用 curl，代码生成，自主）
- [request-fields.md](references/request-fields.md) — 按模式详细字段表 + 音频处理
- [workflows.md](references/workflows.md) — 持续时长扩展，音频解决方案，多轮对话，VACE 管道
- [polling-guide.md](references/polling-guide.md) — 轮询模式和时序建议
- [merge-media.md](references/merge-media.md) — 生成合并/裁剪/音频叠加代码指南
- [examples.md](references/examples.md) — 所有模式的完整脚本执行示例
- [sources.md](references/sources.md) — 官方文档 URL
