# Qwen 视频生成

使用 Wan 模型生成视频。所有任务都是**异步**的——提交后，然后轮询直到完成。
这项技能是 **qwencloud/qwencloud-ai** 的一部分。

> **⚠️ 重要参数差异：**
> - **kf2v（首帧+尾帧）**：持续时间**固定为 5 秒**——其他值将失败。输出**仅无声**。
> - **分辨率参数因模型系列而异，而不仅限于模式**：选择 `size`、`resolution` 或 `ratio` 之前，请先获取当前的模型目录。

## 技能目录

使用此技能的内部文件来执行和学习。当默认路径失败或需要详细信息时，按需加载参考文件。

| 位置 | 用途 |
|------|---------|
| `scripts/video.py` | 默认执行——自动检测模式、提交、轮询、下载 |
| `references/execution-guide.md` | 备用：所有 5 种模式的 curl，代码生成 |
| `references/request-fields.md` | 字段表和按模式处理的音频 |
| `references/workflows.md` | 持续时间扩展、多镜头、VACE 管道 |
| `references/polling-guide.md` | 轮询模式和时机 |
| `references/merge-media.md` | 连接、修剪、音频覆盖——ffmpeg/moviepy 配方 |
| `references/prompt-guide.md` | 按模式提示公式、声音描述、多镜头结构 |
| `references/examples.md` | 每种模式的完整脚本示例 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要明文输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$QWENCLOUD_API_KEY`，Python 中的 `os.environ["QWENCLOUD_API_KEY"]`）。脚本接受 `QWENCLOUD_API_KEY`，然后是 `QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`。任何凭证检查或检测都必须**非明文**：仅报告状态（例如“已设置”/“未设置”、“有效”/“无效”），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符（`QWENCLOUD_API_KEY=sk-your-key-here`），并指示用户将其替换为他们从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)获取的实际密钥。仅当用户明确要求时，才写入实际密钥值。

## 关键兼容性

脚本支持**标准 QwenCloud API 密钥**（`sk-...`）和**令牌计划密钥**（`sk-sp-...`）。令牌计划密钥会自动路由到支持视频模型的令牌计划端点——请参阅下方的 [令牌计划支持](#token-plan-support)。

**令牌计划：不要使用 curl；始终使用捆绑的 Python 脚本。**

编码计划密钥（也具有 `sk-sp-` 前缀，但通过编码计划订阅购买）不能使用——视频生成模型不在编码计划上。视频生成在标准密钥上按每秒收费。脚本在启动时检测密钥类型并进行相应路由。如果安装了 qwencloud-ops-auth，请参阅其 `references/codingplan.md` 获取完整详细信息。

在不暴露密钥的情况下检测 API 密钥类型：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qwencloud_lib import detect_api_key_type
print(detect_api_key_type('scripts/qwencloud_lib.py'))
"
```

| 输出 | 含义 |
|------|---------|
| `token-plan` | 检测到令牌计划密钥（`sk-sp-` 前缀） |
| `payg` | 检测到标准 PAYG 密钥 |
| `not-set` | 环境中未找到 API 密钥 |

对于令牌计划，获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)，然后使用列表中精确列出的模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-token-plan-models.md)。

## 模式选择指南

| 用户想要 | 模式 | 密钥字段 |
|-----------|------|-----------|
| 仅从文本描述生成视频 | **t2v** | 仅 `prompt` |
| 动画化单张图像 | **i2v** | `img_url` 或 `reference_image` |
| wan2.7 统一 i2v：首帧、首帧+尾帧、视频延续、音频同步 | **i2v** | `media`（数组）、`first_frame_url`、`first_clip_url`、`driving_audio_url` |
| 在两张图像之间过渡（**⚠️ 5 秒固定，仅无声**） | **kf2v** | `first_frame_url` + `last_frame_url` |
| 角色扮演：让角色表演新剧本 | **r2v** | `reference_urls` 或 `media`；请参阅 CDN 模型目录了解模型特定限制 |
| 视频编辑：多图像参考、重绘、本地编辑、扩展、外绘 | **vace** | `function`；请参阅 CDN 模型目录了解当前默认值 |
| 通过媒体协议进行视频编辑 | **videoedit** | `--model` + `media` 或 `video_url`；请参阅 CDN 模型目录了解支持的模型 |
| 将一个人的动作/表情从参考视频转移到角色图像 | **animate** | `--model` + `image_url` + `video_url` + `mode`；请参阅 CDN 模型目录了解支持的模型 |

### 模型选择

> **🚫 关键——绝不能覆盖用户指定的参数。** 如果用户明确指定了模型（在提示或请求 JSON 中），您必须使用**完全相同的模型**。不要：
> - 用“更适合”或更新模型替换它（例如，因为任务“看起来像是一个一站式工作”，将用户的 `wan2.6-t2v` 替换为 `wan3.0-video`）
> - 替换或重新结构化他们的输入字段（例如，将用户指定的 `img_url`/`media` 排列）除非所选模型的要求需要——如果需要转换，请保持用户的媒体顺序和内容不变
> - 添加用户未请求的参数（`prompt_extend`、`shot_type`、风格提示）——注意 `shot_type: "multi"` 需要 `prompt_extend: true`，但仅当用户实际请求多镜头时
> - “优化”任何用户明确的选择（`duration`、`size`、`resolution`、`prompt`）
>
> 以下选择指南仅适用于**用户未指定模型**时。

1. **用户指定了模型** → **强制：使用该确切模型**——不要替换，不要“优化”，不要添加未请求的参数。
2. **当模型选择取决于功能、场景或定价时，请咨询 qwencloud-model-selector 技能。**

## 模型

在选择、推荐或默认设置模型之前，获取并阅读当前的 [QwenCloud 视频生成模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-video-generation-models.md)。它包含模型列表、基本模型信息、模式推荐、兼容性说明和默认值。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-video-generation-models.md)。

> **⚠️ 重要**：模型目录是一个**特定时间的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查[官方模型列表](https://www.qwencloud.com/models)以获取权威、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qwencloud.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果可用，请使用 **qwencloud-model-selector** 技能或 **QwenCloud CLI**（`qwencloud models info <model>`）进行实时模型数据查询。CLI 需要身份验证——请参阅 **qwencloud-usage** 技能的登录流程。

## 执行

> **⚠️ 多个工件**：在单个会话中生成多个文件时，您必须将数字后缀附加到每个文件名（例如 `out_1.mp4`、`out_2.mp4`）以防止覆盖。

### 前置条件

- **API 密钥**：使用**非明文**检查检查 `QWENCLOUD_API_KEY`、`QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`（例如，在 shell 中：`[ -n "$QWENCLOUD_API_KEY" ]`）；仅报告“已设置”或“未设置”，绝不能显示密钥值）。如果未设置：如果可用，运行 *qwencloud-ops-auth*；否则，指导用户从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)获取密钥，并通过 `.env` 文件（在项目根目录或当前目录中运行 `echo 'QWENCLOUD_API_KEY=sk-your-key-here' >> .env`）或环境变量设置它。脚本在当前工作目录和项目根目录中搜索 `.env`。技能可能独立安装——不要假设 qwencloud-ops-auth 存在。
  **注意**：脚本自动从当前目录和项目根目录加载 `.env`（除了任何导出的环境变量）。显示 `$QWENCLOUD_API_KEY` 为“未设置”的 shell 检查**并不意味着脚本会失败**——它可能仍在 `.env` 中找到密钥。将 shell 检查视为仅供参考；权威测试是简单地运行脚本（如果任何地方未找到密钥，它会以清晰的错误退出）。
- Python 3.9+（仅标准库，**无需 pip 安装**）
- 对于媒体合并（连接、修剪、音频覆盖）：请参阅 [merge-media.md](references/merge-media.md) 获取适合用户环境的 ffmpeg/moviepy 配方

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果 `python3` 不可用或低于 3.9，PAYG 可能使用**路径 2（curl）**；令牌计划必须安装 Python 3.9+。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行。** 不要假设脚本在当前工作目录中。不要在执行前使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本——等待标准输出；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/video.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/video.py \
  --model wan2.6-t2v \
  --request '{"prompt":"一个侦探在雨夜的城里","size":"1280*720","duration":5}' \
  --print-response

# 图像到动画（无提示）：将舞蹈动作从参考视频转移到角色图像
python3 <this-skill-dir>/scripts/video.py \
  --model wan2.2-animate-move \
  --request '{"image_url":"https://example.com/character.jpg","video_url":"https://example.com/dance.mp4","mode":"wan-std"}' \
  --print-response
```

| 参数 | 描述 |
|------|-------------|
| `--request '{...}'` | JSON 请求正文 |
| `--file path.json` | 从文件加载请求 |
| `--mode MODE` | 覆盖自动检测的模式（t2v/i2v/kf2v/r2v/vace/videoedit/animate） |
| `--model ID` | 覆盖模型 |
| `--output dir/` | 将视频和响应 JSON 保存到目录；视频根据下载 URL 的基本名称自动命名，以防止跨运行覆盖；跨调用使用不同的文件名以避免覆盖响应数据 |
| `--print-response` | 将响应 JSON 打印到标准输出 |
| `--submit-only` | 提交后退出（打印 task_id） |
| `--task-id ID` | 对现有任务进行操作 |
| `--poll-interval N` | 轮询间隔秒数（默认：15） |
| `--timeout N` | 最大等待秒数（默认：600） |

### 验证结果

- 退出代码 `0` + 响应包含 `output.task_id` → **提交成功**
- 轮询达到 `task_status: SUCCEEDED` → **生成完成**
- 非零退出、HTTP 错误或 `FAILED` 状态 → **失败**
- **执行后检查**：确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [执行后强制更新检查](#update-check-mandatory-post-execution) 中的说明执行操作。

### 失败时

如果脚本失败，请根据下面的诊断表匹配错误输出以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：所有 5 种模式的 curl 命令（路径 2）、代码生成（路径 3）和自主解决（路径 5）。

**如果完全无法使用 Python** → PAYG 可能使用路径 2（curl）；令牌计划必须安装 Python 3.9+。

| 错误模式 | 诊断 | 解决方案 |
|---------------|-----------|------------|
| `command not found: python3` | Python 未在 PATH 中 | 尝试 `python` 或 `py -3`；如果缺少，请安装 Python 3.9+ |
| `Python 3.9+ required` | 脚本版本检查失败 | 将 Python 升级到 3.9+ |
| `SyntaxError` near type hints | Python < 3.9 | 将 Python 升级到 3.9+ |
| `QWENCLOUD_API_KEY/QWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)获取密钥；添加到 `.env`：`echo 'QWENCLOUD_API_KEY=sk-...' >> .env`；如果可用，请运行 **qwencloud-ops-auth** |
| `HTTP 401` | 无效或匹配错误的密钥 | 如果可用，请运行 **qwencloud-ops-auth**（仅非明文检查）；验证密钥是否有效 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问 | 检查互联网；如果通过代理，请设置 `HTTPS_PROXY` |
| `HTTP 429` | 被限速 | 等待并使用退避重试 |
| `HTTP 5xx` | 服务器错误 | 使用退避重试 |
| `ImportError: moviepy` | moviepy 未安装 | `pip install moviepy`，或使用系统 ffmpeg（请参阅 [merge-media.md](references/merge-media.md)） |
| `PermissionError` | 无法写入输出 | 使用 `--output` 指定可写目录 |

## 请求字段摘要

所有模式都需要 `prompt` **除了** `animate`（无提示）和 `videoedit` 对于 wan2.7（提示可选）。请参阅 [request-fields.md](references/request-fields.md) 获取每种模式的完整字段表。

### ⚠️ 按模型系列划分的分辨率参数（关键）

分辨率字段因模型系列而异。在为 `size`、`resolution` 和 `ratio` 选择之前，请检查上面的模型目录；使用错误字段会导致 API 调用失败。

### 模式特定必需字段

- 必需字段因模型系列而异。使用 [request-fields.md](references/request-fields.md) 获取有效载荷形状，并使用上面的模型目录了解当前模型特定兼容性。

## 成本估算

> 🚨 **绝对不要猜测或编造任何价格数字。** 始终将用户引导至 [官方定价页面](https://docs.qwencloud.com/developer-guides/getting-started/pricing) 获取确切费率。

成本按生成视频的每秒计费。价格因模型和分辨率而异。获取 [CDN 模型定价参考](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-pricing.md)，并使用官方定价页面获取当前确切费率。某些模型可能提供有限的免费配额——**不要假设任何调用都是免费的**；使用 **qwencloud-usage** 技能检查剩余免费层配额，或在用户的 [QwenCloud 控制台](https://home.qwencloud.com/benefits) 中验证。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-model-pricing.md)。

要检查实际使用情况和账单：使用 **qwencloud-usage** 技能，或访问控制台：
[使用分析](https://home.qwencloud.com/analytics) |
[按量付费账单](https://home.qwencloud.com/billing/pay-as-you-go) |
[编码计划账单](https://home.qwencloud.com/billing/coding-plan)

> **绝对不要编造、猜测或构造使用/账单/控制台 URL。** 仅提供此技能中列出的确切链接。如果此处未列出 URL，请不要编造一个。

## 本地文件处理

当用户提供本地文件路径（图像、视频、音频）时，直接将它们传递给脚本。脚本**自动上传**本地文件到 DashScope 临时存储（`oss://` URL，48 小时 TTL），并注入 `X-DashScope-OssResourceResolve: enable` 标头。无需手动上传步骤。

> **生产**：默认临时存储具有 **48 小时 TTL** 和 **100 QPS 上传限制**——不适合生产、高并发或负载测试。要使用您自己的 OSS 存储桶，请在 `.env` 中设置 `QWEN_TMP_OSS_BUCKET` 和 `QWEN_TMP_OSS_REGION`，安装 `pip install alibabacloud-oss-v2`，并通过 `QWEN_TMP_OSS_AK_ID` / `QWEN_TMP_OSS_AK_SECRET` 或标准的 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 提供凭证。使用具有最小权限的 RAM 用户（仅对目标存储桶上的 `oss:PutObject` + `oss:GetObject`）。如果安装了 qwencloud-ops-auth，请参阅其 `references/custom-oss.md` 获取完整设置指南。

## 跨技能链接

当使用另一个技能的输出作为输入时（例如，图像生成 → i2v，语音合成 → 音频覆盖）：
- **直接传递 URL**（例如，`"img_url": "<image_url from image-gen>"`）——不要下载并重新传递为本地路径
- 脚本检测 URL 前缀（`https://`，`oss://`）并直接传递，无需重新上传
- 仅在用户预览或非 API 操作中使用 `local_path` 从响应中获取

当将此技能的输出传递给另一个技能时（例如，vace 编辑，视觉分析）：
- **传递 `video_url` 从响应中**——不要下载并重新传递为本地路径

| 场景 | 使用 |
|----------|-----|
| 提供给另一个技能 | `video_url` / `image_url`（URL） |
| 显示给用户/本地播放 | `local_path`（本地文件） |

## 重要说明

- **仅异步**：所有视频 API 都需要 `X-DashScope-Async: enable` 标头。
- **kf2v**：使用**不同的 API 端点**。持续时间**固定为 5 秒**，**仅无声**。
- **r2v**：在提示中使用 `character1`/`character2`/...。最多 5 个参考（最多 3 个视频）。
- **vace**：必须指定 `function`。**仅无声**，输出 **≤5s**。
- **多镜头**：设置 `shot_type: "multi"` AND `prompt_extend: true`。
- **视频 URL 在 24 小时内过期**——脚本自动下载到 `--output` 目录。当链接到另一个技能（例如，vace 编辑）时，直接传递 `video_url`——不要重新下载。
- 对于高级工作流→请参阅 [workflows.md](references/workflows.md)。

## 错误处理

| 错误 | 原因 | 操作 |
|-------|-------|--------|
| `401 Unauthorized` | 无效或缺少 API 密钥 | 如果可用，请运行 **qwencloud-ops-auth**（仅非明文检查）；否则提示用户设置密钥 |
| `current user api does not support synchronous calls` | 缺少异步标头 | 添加 `X-DashScope-Async: enable` |
| `429` / `5xx` | 被限速或服务器错误 | 使用退避重试 |
| 任务 `FAILED` | 生成失败 | 检查 `output.message` 在轮询响应中 |

## 输出位置

优先使用**当前工作目录**。默认子目录：`./output/qwencloud-video-generation/`.

**写入禁止**：绝对不要将输出文件写入此技能的安装目录或任何 `skills/` 层级。所有生成内容必须位于当前工作目录的 `output/` 下或用户指定的路径。

## 令牌计划支持

令牌计划仅支持视频模型的一个子集。选择或验证模型之前，获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-token-plan-models.md)。

仅当当前令牌计划目录中具有兼容模型时，才能使用令牌计划。请求其他模式可能会返回服务错误；不要默默地切换请求的模型或模式。

对于令牌计划的 kf2v 请求，当目录中没有兼容的 kf2v 模型时，**在提交之前停止**。解释所选模型需要 PAYG，然后要求用户选择已为该请求配置的 PAYG 密钥或更改请求结果，以便令牌计划支持的模式可以完成。

> ⚠️ **积分警告**：视频生成比文本对话消耗更多的积分。单个视频可能使用数百积分，具体取决于持续时间和分辨率。生成前请检查您的剩余配额。

### 必需标头

`User-Agent: qwencloud-skills` 会自动包含。

## 更新检查（执行后强制）

脚本执行后，检查 stderr 以查找操作信号。脚本自动检测更新状态并发出结构化信号。您必须采取行动。本节也适用于用户明确要求检查更新时。

### 信号：`[ACTION_REQUIRED] qwencloud-update-check skill is not installed`

当 stderr 包含此信号时，您必须向用户展示以下选项，并**等待他们的响应后再继续**。不要默默地跳过。

> 更新检查技能未安装。它让您了解 qwencloud/qwencloud-ai 的新功能和错误修复。
>
> 1) **立即安装**——我会为您运行安装命令
> 2) **暂时跳过**——这次什么也不做
> 3) **不再提醒我**——永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QwenCloud/qwencloud-ai --skill qwencloud-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须将简短的更新通知附加到您的响应中，包括版本信息和 stderr 输出中显示的更新命令。

### stderr 中没有信号

如果 stderr 中既没有 `[ACTION_REQUIRED]` 也没有 `[UPDATE_AVAILABLE]`，则无需操作——技能已安装并是最新的（或 24 小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如，“检查更新”，“检查版本”）：
1. 在兄弟技能目录中查找 `qwencloud-update-check/SKILL.md`。
2. 如果找到——运行：`python3 <qwencloud-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到——呈现上面的安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 备用路径（所有模式的 curl，代码生成，自主）
- [request-fields.md](references/request-fields.md) — 每种模式的详细字段表 + 音频处理
- [workflows.md](references/workflows.md) — 持续时间扩展、音频解决方案、多镜头、VACE 管道
- [polling-guide.md](references/polling-guide.md) — 轮询模式和时机建议
- [merge-media.md](references/merge-media.md) — 生成合并/修剪/音频覆盖代码的指南
- [examples.md](references/examples.md) — 所有模式的完整脚本执行示例
- [sources.md](references/sources.md) — 官方文档 URL
