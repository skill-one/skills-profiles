# Qwen 图像生成

使用 Wan 和 Qwen 图像模型生成和编辑图像。支持文本到图像、参考图像编辑（风格迁移、主体一致性、多图像合成、文本渲染）以及交错的文本图像输出。这项技能是 **qwencloud/qwencloud-ai** 的一部分。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 目的 |
|------|------|
| `scripts/image.py` | 默认执行 — 同步/异步、上传、下载 |
| `references/execution-guide.md` | 备用：curl（同步/异步）、代码生成 |
| `references/prompt-guide.md` | 提示公式、风格关键词、negative_prompt、prompt_extend 决策 |
| `references/api-guide.md` | API 补充 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要以明文形式输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$QWENCLOUD_API_KEY`，Python 中的 `os.environ["QWENCLOUD_API_KEY"]`）。脚本接受 `QWENCLOUD_API_KEY`，然后是 `QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`。任何凭证检查或检测都必须**非明文**：仅报告状态（例如“已设置”/“未设置”、“有效”/“无效”），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符（`QWENCLOUD_API_KEY=sk-your-key-here`），并指示用户用他们从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 的实际密钥替换它。仅当用户明确要求时才写入实际密钥值。

## 密钥兼容性

脚本支持**标准 QwenCloud API 密钥**（`sk-...`）和**令牌计划密钥**（`sk-sp-...`）。令牌计划密钥会自动路由到支持图像模型的令牌计划端点 — 请参阅 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-token-plan-models.md)。

**令牌计划：不要使用 curl；始终使用捆绑的 Python 脚本。**

编码计划密钥（也具有 `sk-sp-` 前缀，但通过编码计划订阅购买）不能使用 — 图像生成模型在编码计划中不可用。脚本在启动时检测密钥类型并进行相应路由。如果安装了 qwencloud-ops-auth，请参阅其 `references/codingplan.md` 获取完整详细信息。

检测 API 密钥类型而不暴露密钥：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qwencloud_lib import detect_api_key_type
print(detect_api_key_type('scripts/qwencloud_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | 检测到令牌计划密钥（`sk-sp-` 前缀） |
| `payg` | 检测到标准 PAYG 密钥 |
| `not-set` | 环境中未找到 API 密钥 |

## 模式选择指南

选择模式之前，获取并阅读当前的 [QwenCloud 图像生成模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-image-generation-models.md)。它包含模式到模型的推荐、模型列表、基本模型信息、兼容性说明和默认模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-image-generation-models.md)。

## 模型选择

> **🚫 关键 — 绝不覆盖用户指定的参数。** 如果用户明确指定了模型（在提示或请求 JSON 中），您必须使用该模型。不要：
> - 用“更适合”或更新模型替换它（例如，因为任务“看起来像多功能工作”，用 `wan2.7-image` 替换用户的 `wan2.6-t2i`）
> - 添加用户未请求的参数（`thinking_mode`、`color_palette`、`bbox_list`、风格提示）
> - “优化”任何明确的用户选择
>
> 以下模式/模型指南仅适用于**用户未指定模型**的情况。如果用户指定的模型无法实现他们的要求（例如，由于硬 API 限制），如果可能，则按用户的选择执行；否则向用户报告限制，让他们决定 — 不要默默替换。

使用上面链接的图像生成模型目录获取当前模型系列、默认值、推荐值、兼容性和限制。

1. **用户指定了模型** → **强制：使用该确切模型** — 不要替换，不要“优化”，不要添加未请求的参数。
2. **当模型选择取决于要求、场景或定价时，请咨询 qwencloud-model-selector 技能**。
3. **未指定模型** → 从模型目录中选择当前默认值或特定任务的推荐值。如果用户的请求操作与模型的文档中记录的硬限制冲突，请解释限制并让用户决定；绝不要默默替换明确选择的模型。

> **⚠️ 重要**：模型目录是一个**时间点快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查[官方模型列表](https://www.qwencloud.com/models)以获取权威的、最新的目录。**
>
> **模型详细信息**：有关特定模型的更多信息，请将用户引导至其详细页面：`https://www.qwencloud.com/models/<model-name>`（将 `<model-name>` 替换为确切的模型 ID，例如 `wan2.7-image-pro` → https://www.qwencloud.com/models/wan2.7-image-pro）。**绝不要修改或猜测 URL 中的模型名称。**
>
> **动态模型查询**：如果 **qwencloud-model-selector** 技能或 **QwenCloud CLI**（`qwencloud models info <model>`）可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qwencloud-usage** 技能以获取登录流程。

## 执行

> **⚠️ 多个生成物**：在单个会话中生成多个文件时，您必须为每个文件名附加一个数字后缀（例如 `out_1.png`，`out_2.png`）以防止覆盖。

### 前置条件

- **API 密钥**：使用**非明文**检查仅检查 `QWENCLOUD_API_KEY`、`QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`（例如，在 shell 中：`[ -n "$QWENCLOUD_API_KEY" ]`；仅报告“已设置”或“未设置”，绝不能显示密钥值）。如果未设置：如果可用，运行 **qwencloud-ops-auth** 技能；否则，指导用户从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取密钥并通过 `.env` 文件（在项目根目录或当前目录中：`echo 'QWENCLOUD_API_KEY=sk-your-key-here' >> .env`）或环境变量设置。脚本在当前工作目录和项目根目录中搜索 `.env`。技能可以独立安装 — 不要假设 qwencloud-ops-auth 存在。
  **注意**：脚本自动从当前目录和项目根目录加载 `.env`（除了任何导出的环境变量）。显示 `$QWENCLOUD_API_KEY` 作为“未设置”的 shell 检查**并不意味着脚本会失败** — 它可能仍在 `.env` 中找到密钥。将 shell 检查视为仅供参考；权威测试是简单地运行脚本（如果没有找到任何密钥，它将退出并显示清晰的错误）。
- Python 3.9+（仅标准库，**不需要 pip 安装**）

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果 `python3` 不可用或低于 3.9，PAYG 可能使用**路径 2（curl）**；令牌计划必须安装 Python 3.9+。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行脚本。** 不要假设脚本位于当前工作目录。不要在执行之前使用 `cd` 切换目录。

**执行说明**：在**前台**运行所有脚本 — 等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/image.py --help` 以查看所有可用参数。

```bash
# 文本到图像（使用 CDN 模型目录中的默认值）
python3 <this-skill-dir>/scripts/image.py \
  --request '{"prompt":"一个舒适的鲜花店，有木门"}' \
  --output output/qwencloud-image-generation/images/out.png \
  --print-response

# 使用参考图像进行图像编辑（wan2.6-image）
python3 <this-skill-dir>/scripts/image.py \
  --model wan2.6-image \
  --request '{"prompt":"将水彩画风格应用于这张照片","reference_images":["https://img.alicdn.com/imgextra/i1/NotRealJustExample/photo.jpg"],"n":1,"size":"1K"}' \
  --output output/qwencloud-image-generation/images/out.png \
  --print-response

# z-image-turbo（仅同步，没有 n；省略 size → 服务器默认 1024*1536）
python3 <this-skill-dir>/scripts/image.py \
  --model z-image-turbo \
  --request '{"prompt":"一只坐着的小橙猫，逼真的","prompt_extend":false}' \
  --output output/qwencloud-image-generation/images/out.png \
  --print-response

# qwen-image-3.0-pro（省略 size → 自动推荐分辨率）
python3 <this-skill-dir>/scripts/image.py \
  --model qwen-image-3.0-pro \
  --request '{"prompt":"一张写着“限时特惠”的海报","enable_thinking":true}' \
  --output output/qwencloud-image-generation/images/out.png \
  --print-response

# qwen-mt-image-2.0（API 支持同步/异步；捆绑脚本使用异步）
python3 <this-skill-dir>/scripts/image.py \
  --model qwen-mt-image-2.0 \
  --request '{"image_url":"https://example.com/poster_zh.jpg","source_lang":"zh","target_lang":"en"}' \
  --output output/qwencloud-image-generation/images/out.png \
  --print-response
```

**更多示例**（交错输出、wan2.5-i2i、qwen-image-2.0-pro、qwen-image-plus）：参见 [execution-guide.md](references/execution-guide.md)

| 参数 | 描述 |
|------|------|
| `--request '{...}'` | JSON 请求正文 |
| `--file path.json` | 从文件加载请求 |
| `--async` | 强制异步模式；脚本在其实现使用异步的地方自动启用它。对于仅同步的模型（例如 `qwen-image-max`）则忽略。 |
| `--model ID` | 覆盖模型（检查上面模型目录中的当前默认值） |
| `--output path` | 将图像保存到路径（或多图像输出到目录）。当将多个图像写入同一目录时，文件将使用 OSS URL 中的唯一标识符自动命名，以防止跨运行覆盖。明确文件路径优先；跨调用使用不同的文件名以避免覆盖 |
| `--print-response` | 将响应 JSON 打印到 stdout |

### 验证结果

- 退出代码 `0` + 输出包含有效的 JSON，其中包含 `output.results` 或 `output.task_id` → **成功**
- 非零退出、HTTP 错误、空响应或错误 JSON → **失败**
- 异步：提交必须返回 `output.task_id`；轮询必须达到 `task_status: SUCCEEDED`
- **执行后检查**：确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照下面的 [执行后强制更新检查](#update-check-mandatory-post-execution) 部分的说明采取行动。

### 失败

如果脚本失败，请根据下面的诊断表匹配错误输出以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（路径 2 — 同步和异步）、代码生成（路径 3）和自主解决（路径 5）。

**如果完全无法找到 Python** → PAYG 可能使用 Path 2 (curl)；令牌计划必须安装 Python 3.9+。

| 错误模式 | 诊断 | 解决方案 |
|----------|------|----------|
| `command not found: python3` | Python 不在 PATH 中 | 尝试 `python` 或 `py -3`；如果缺少，则安装 Python 3.9+ |
| `Python 3.9+ required` | 脚本版本检查失败 | 升级 Python 到 3.9+ |
| `SyntaxError` near type hints | Python < 3.9 | 升级 Python 到 3.9+ |
| `QWENCLOUD_API_KEY/QWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取密钥；将其添加到 `.env`：`echo 'QWENCLOUD_API_KEY=sk-...' >> .env`；或者如果可用，运行 **qwencloud-ops-auth** |
| `HTTP 401` | 无效或匹配错误的密钥 | 如果可用，运行 **qwencloud-ops-auth**（仅非明文检查）；验证密钥是否有效 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问 | 检查互联网；如果通过代理，请设置 `HTTPS_PROXY` |
| `HTTP 429` | 被限速 | 等待并使用退避重试 |
| `HTTP 5xx` | 服务器错误 | 使用退避重试 |
| `PermissionError` | 无法写入输出 | 使用 `--output` 指定可写目录 |

## 快速参考

### 请求字段（常见）

| 字段 | 类型 | 描述 |
|------|------|------|
| `prompt` | string | 生成图像的文本描述（必需；不用于图像翻译） |
| `negative_prompt` | string | 图像中要避免的内容（最多 500 个字符） |
| `size` | string | 分辨率；使用模型目录以获取目录限制，或使用 API 指南或官方文档获取模型特定值（目录中未列出） |
| `seed` | int | 用于可重复性的随机种子 [0, 2147483647] |
| `model` | string | 模型 ID；检查上面模型目录以获取当前默认值和受支持的模型 |
| `prompt_extend` | bool | 启用提示重写（默认：true；仅图像编辑模式） |
| `enable_thinking` | bool | qwen-image-3.0 仅限 — 增强推理（默认：true）。仅在 `prompt_extend=true` 时有效 |
| `prompt_extend_mode` | string | qwen-image-3.0 仅限 — `direct`（DPE，默认）或 `agent`（APE；仅 t2i） |

### 请求字段（wan2.7-image-pro / wan2.7-image — 多功能）

| 字段 | 类型 | 描述 |
|------|------|------|
| `reference_images` | string[] | 0–9 图像 URL 或本地路径 |
| `reference_image` | string | 单个图像 URL/路径（简称） |
| `size` | string | `1K`（默认）、`2K`（默认）或 `4K`（pro 仅限，t2i 模式）。或像素尺寸 |
| `enable_sequential` | bool | `true`：顺序多图像模式（n=1–12）。`false`（默认）：单次/批处理模式（n=1–4） |
| `n` | int | 要生成的图像数量。顺序模式：1–12（默认 12）。非顺序：1–4（默认 4）。**按图像计费。** |
| `thinking_mode` | bool | 启用增强推理以获得更好的质量（默认：true）。仅限 t2i（无图像，非顺序） |
| `bbox_list` | List[List[List[int]]] | 交互式编辑区域。格式：`[[[x1,y1,x2,y2],...], ...]`。列表长度 = 图像数量。没有编辑的图像为空 `[]` |
| `color_palette` | array | 自定义颜色主题（3–10 种颜色）。每个：`{"hex":"#C2D1E6","ratio":"23.51%"}`。比率总和 = 100%。仅限非顺序模式 |
| `watermark` | bool | 添加“AI 生成”水印（默认：false） |

**注意**：`thinking_mode` 增加延迟但提高质量。`enable_sequential` 生成连贯的图像序列（例如，跨场景的相同角色）。

### 请求字段（wan2.6-image — 图像编辑）

| 字段 | 类型 | 描述 |
|------|------|------|
| `reference_images` | string[] | 1–4 图像 URL 或本地路径用于编辑模式；0–1 用于交错模式 |
| `reference_image` | string | 单个图像 URL/路径（简称；`reference_images` 优先） |
| `enable_interleave` | bool | `false`（默认）：图像编辑模式；`true`：交错文本图像输出 |
| `n` | int | 在编辑模式下要生成的图像数量（1–4，默认：1）。**按图像计费。** |
| `max_images` | int | 交错模式中的最大图像数量（1–5，默认：5）。**按图像计费。** |
| `watermark` | bool | 添加“AI 生成”水印（默认：false） |

### 其他模型

使用上面链接的模型目录获取当前模型列表和模型特定的兼容性差异。

### 图像翻译请求字段

对于从目录中选择的图像翻译模型，使用 `image_url`、`source_lang` 和 `target_lang`；不要发送 `prompt`。可选的 `ext` 对象包含领域/风格提示、确切匹配跳过词、术语对和图像分割设置。即使没有可翻译文本的成功任务也可能计费。

**完整参数表**：参见 [api-guide.md](references/api-guide.md#wan25-i2i-preview--general-image-editing) 获取详细参数。

### 尺寸参考（wan2.6-image）

- **编辑模式**：`1K`（默认，~1280×1280）或 `2K`（~2048×2048）
- **交错模式**：像素尺寸，总像素在 [768×768, 1280×1280]

**常见宽高比**：`1280*1280`（1:1），`960*1280`（3:4），`1280*960`（4:3），`720*1280`（9:16），`1280*720`（16:9）

### 响应字段

| 字段 | 描述 |
|------|------|
| `image_url` | 生成的图像 URL（24 小时有效）。**链接到另一个技能时使用此链接。** |
| `image_urls` | 所有图像 URL 数组（多图像输出，wan2.6-image，qwen-image-edit） |
| `image_count` | 生成的图像数量 |
| `local_path` | 下载的图像的本地文件路径。**用于用户预览或非 API 操作。** |
| `local_paths` | 本地文件路径数组（多图像输出） |
| `interleaved_content` | `{type, text/image}` 对象数组（交错模式） |
| `width` / `height` | 图像尺寸 |
| `seed` | 使用的种子 |

## API 详细信息

- **同步端点（wan2.6-t2i, wan2.6-image 编辑，qwen-image-edit 系列，qwen-image-max, z-image-turbo）**：`POST /api/v1/services/aigc/multimodal-generation/generation`
- **异步端点（wan2.6 和旧的 t2i）**：`POST /api/v1/services/aigc/image-generation/generation` with `X-DashScope-Async: enable`
- **异步端点（wan2.5-i2i-preview; 捆绑脚本路由用于 qwen-mt-image-2.0）**：`POST /api/v1/services/aigc/image2image/image-synthesis` with `X-DashScope-Async: enable`。图像翻译 API 本身支持同步和异步；`image.py` 目前实现异步提交和轮询。
- **异步端点（qwen-image-plus 和 qwen-image）**：`POST /api/v1/services/aigc/text2image/image-synthesis` with `X-DashScope-Async: enable`。`qwen-image-max` 仅同步，不得使用此路由。
- **wan2.6-t2i 分辨率**：总像素在 [1280x1280, 1440x1440]，宽高比 [1:4, 4:1]
- **wan2.6-image 分辨率**：编辑模式 [768x768, 2048x2048]; 交错模式 [768x768, 1280x1280]; 宽高比 [1:4, 4:1]
- **输入图像**（wan2.6-image）：JPEG/JPG/PNG/BMP/WEBP, 240–8000px 每个维度, ≤10MB
- **本地文件**：脚本自动上传到 DashScope 临时存储（`oss://` URL，48 小时 TTL）。直接传递本地路径 — 无需手动上传步骤。
  > **⚠️ 令牌计划限制**：令牌计划不支持本地文件上传。如果您使用令牌计划密钥（`sk-sp-...`），请将参考图像提供为公开可访问的 https:// URL，而不是本地路径。
- **生产**：默认临时存储具有 **48 小时 TTL** 和 **100 QPS 上传限制** — 不适用于生产、高并发或负载测试。要使用您自己的 OSS 存储桶，请在 `.env` 中设置 `QWEN_TMP_OSS_BUCKET` 和 `QWEN_TMP_OSS_REGION`，安装 `pip install alibabacloud-oss-v2`，并通过 `QWEN_TMP_OSS_AK_ID` / `QWEN_TMP_OSS_AK_SECRET` 或标准 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 提供凭证。使用具有最小权限的 RAM 用户（仅对目标存储桶上的 `oss:PutObject` + `oss:GetObject`）。如果安装了 qwencloud-ops-auth，请参阅其 `references/custom-oss.md` 获取完整设置指南。
- **交错同步**：需要流式传输（`X-DashScope-Sse: enable` + `stream: true`）；使用此脚本通过异步模式代替

## 跨技能链接

当使用生成的图像作为另一个技能的输入（例如，视频生成 i2v、视觉分析）时：
- **直接传递 `image_url`** — 不要下载并重新传递为本地路径
- 所有下游脚本检测 URL 前缀（`https://`, `oss://`）并直接传递，无需重新上传
- 仅在用户预览或非 API 操作（例如，在编辑器中打开）时使用 `local_path` (本地文件)

| 情景 | 使用 |
|------|------|
| 链接到另一个技能（视频生成、视觉、图像编辑） | `image_url` (URL) |
| 显示给用户 / 在编辑器中打开 | `local_path` (本地文件) |

## 错误处理

| HTTP | 含义 | 操作 |
|------|------|------|
| 401 | 无效或缺少 API 密钥 | 如果可用，运行 **qwencloud-ops-auth**；否则仅进行非明文检查后提示用户设置密钥 |
| 400 | 请求错误（无效的提示、大小） | 验证参数和约束 |
| 429 | 被限速 | 使用指数退避重试 |
| 5xx | 服务器错误 | 使用指数退避重试 |

> **使用和计费**：使用 **qwencloud-usage** 技能直接检查使用情况、免费套餐配额和计费。或者，用户可以访问 QwenCloud 控制台：
> [使用分析](https://home.qwencloud.com/analytics) |
> [按量计费](https://home.qwencloud.com/billing/pay-as-you-go) |
> [编码计划计费](https://home.qwencloud.com/billing/coding-plan)
>
> **绝对不要编造、猜测或构造使用/计费/控制台 URL。** 仅提供此技能中列出的确切链接。如果此处未列出 URL，则不要编造一个。

## 输出位置

优先使用**当前工作目录**。默认子目录：`./output/qwencloud-image-generation/`.

**写入禁止**：**绝对不要**将输出文件写入此技能的安装目录或任何 `skills/` 树状结构。所有生成内容必须位于当前工作目录的 `output/` 下或用户指定的路径。

## 令牌计划支持

支持选择图像模型的令牌计划密钥（`sk-sp-...`）。脚本自动路由到令牌计划端点。

> **⚠️ 令牌计划限制**：令牌计划不支持本地文件上传。如果您使用令牌计划密钥（`sk-sp-...`），请将参考图像提供为公开可访问的 https:// URL，而不是本地路径。

### 支持的模型

获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)，然后使用列出的确切图像生成模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qwencloud-token-plan-models.md)。

### 不支持通过令牌计划

令牌计划模型目录中未列为图像功能的模型需要 PAYG 密钥。

### 必要头

`User-Agent: qwencloud-skills` 会自动包含。

## 更新检查（强制执行后）

脚本执行后，检查 stderr 以获取操作信号。脚本自动检测更新状态并发出结构化信号。您必须采取行动。本部分也适用于用户明确要求检查更新的情况。

### 信号：`[ACTION_REQUIRED] qwencloud-update-check 技能未安装`

当 stderr 包含此信号时，您必须向用户展示以下选项并**等待他们的响应**再继续。不要默默跳过。

> 更新检查技能未安装。它让您了解 qwencloud/qwencloud-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何事
> 3) **永不提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QwenCloud/qwencloud-ai --skill qwencloud-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须将简短的更新通知附加到您的响应中，包括版本信息和 stderr 输出中显示的更新命令。

### stderr 中没有信号

如果 stderr 中既没有 `[ACTION_REQUIRED]` 也没有 `[UPDATE_AVAILABLE]`，则无需采取任何操作 — 技能已安装并更新（或 24 小时内缓存）。
