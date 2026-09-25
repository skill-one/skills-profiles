# Qwen 图像生成

使用 Wan 和 Qwen 图像模型生成和编辑图像。支持文本到图像、参考图像编辑（风格迁移、主体一致性、多图像合成、文本渲染）以及交错的文本图像输出。此技能是 **QianWen-AI/qianwen-ai** 的一部分。

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

**绝对不要以明文形式输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$DASHSCOPE_API_KEY`，Python 中的 `os.environ["DASHSCOPE_API_KEY"]`）。任何凭证检查或检测都必须**非明文**：仅报告状态（例如“已设置”/“未设置”、“有效”/“无效”），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，应帮助创建一个 `.env` 文件，其中包含占位符（`DASHSCOPE_API_KEY=sk-your-key-here`），并指示用户用他们实际的密钥替换它，从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取。只有在用户明确要求时才写入实际密钥值。

## 密钥兼容性

支持 PAYG（`sk-ws-...`；遗留 `sk-...`）和 Token 计划（`sk-sp-...`）密钥。在不暴露密钥的情况下检测 API 密钥类型：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qianwen_lib import detect_api_key_type
print(detect_api_key_type('scripts/qianwen_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | Token 计划密钥 — 仅使用 Token 计划目录下提供的模型。 |
| `payg` | 按量付费密钥 — 可使用完整模型目录。 |
| `not-set` | 未配置密钥。 |

对于 Token 计划，获取并阅读当前的 [Token 计划模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，然后使用确切列出的模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-token-plan-models.md)。

Token 计划不支持本地文件上传；对于 i2i 模式，请将参考图像作为可访问的 URL（`https://` 或 `oss://`）提供，而不是本地路径。

Token 计划仅支持特定模型 — 请使用上述参考中确切的一个模型；不要猜测或探测模型可用性。对于 PAYG，请继续下方操作。

## 模式选择指南

1. **用户指定了模型** → 直接使用。
2. **当模型选择取决于需求、场景或定价时，咨询 qianwen-model-selector 技能**。

在选择模式或选择、推荐或默认模型之前，获取并阅读当前的 [Qwen 图像生成模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-image-generation-models.md)。它包含模式到模型的推荐、模型列表、基本模型信息、兼容性说明和默认模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-image-generation-models.md)。

> **⚠️ 重要**：上述模型列表是一个**时间点的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，请始终检查[官方模型列表](https://www.qianwenai.com/models)以获取权威的、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qianwenai.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果 **qianwen-model-selector** 技能或 **QianWen CLI**（`qianwen models info <model>`）可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qianwen-usage** 技能了解登录流程。

## 执行

> **⚠️ 多个生成物**：在单个会话中生成多个文件时，您**必须**将数字后缀附加到每个文件名（例如 `out_1.png`，`out_2.png`）以防止覆盖。

### 前置条件

- **API 密钥**：使用 **密钥兼容性** 中的非明文检测器；不要用变量存在性检查来替换它。如果找不到密钥，当可用时使用 qianwen-ops-auth，或指导用户在 `.env` 中配置 `DASHSCOPE_API_KEY`/`QIANWEN_API_KEY`。技能可以独立安装。
- Python 3.9+（仅标准库，**不需要 pip install**）

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果找不到 `python3`，请尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，请跳转到 [execution-guide.md](references/execution-guide.md) 中的 **Path 2 (curl)**。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用完整的绝对路径来执行脚本。** 不要假设脚本位于当前工作目录。不要在执行前使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本 — 等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/image.py --help` 以查看所有可用参数。

```bash
# 文本到图像（使用 CDN 模型目录中的默认值）
python3 <this-skill-dir>/scripts/image.py \
  --request '{"prompt":"A cozy flower shop with wooden door"}' \
  --output output/qianwen-image-generation/images/out.png \
  --print-response

# 使用参考图像进行图像编辑（wan2.6-image）
python3 <this-skill-dir>/scripts/image.py \
  --model wan2.6-image \
  --request '{"prompt":"Apply watercolor painting style to this photo","reference_images":["https://img.alicdn.com/imgextra/i1/NotRealJustExample/photo.jpg"],"n":1,"size":"1K"}' \
  --output output/qianwen-image-generation/images/out.png \
  --print-response
```

**更多示例**（交错输出、wan2.5-i2i、qwen-image-2.0-pro、qwen-image-plus）：参见 [execution-guide.md](references/execution-guide.md)

| 参数 | 描述 |
|------|------|
| `--request '{...}'` | JSON 请求体 |
| `--file path.json` | 从文件加载请求 |
| `--async` | 强制异步模式（wan2.5 及更早版本需要；qwen-image-plus/max 和交错输出自动启用） |
| `--model ID` | 覆盖模型（检查上述模型目录中的当前默认值） |
| `--output path` | 将图像保存到路径（或多图像输出时保存到目录）。当将多个图像写入同一目录时，文件会自动使用 OSS URL 中的唯一标识符命名，以防止跨运行覆盖。显式文件路径仍具有优先级；跨调用使用不同的文件名以避免覆盖 |
| `--print-response` | 将响应 JSON 打印到 stdout |

> **模型优先级**：`--model` CLI 标志 > `"model"` 字段在 `--request` JSON 中 > 内置默认值。

### 验证结果

- 退出代码 `0` + 输出包含有效的 JSON，其中包含 `output.results` 或 `output.task_id` → **成功**
- 非零退出、HTTP 错误、空响应或错误 JSON → **失败**
- 异步：提交必须返回 `output.task_id`；轮询必须达到 `task_status: SUCCEEDED`
- **执行后检查**：验证输出文件是否存在且大小非零（`ls -la <output_path>`）
- **强制 — stderr 信号检查**：在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [执行后强制更新检查](#update-check-mandatory-post-execution) 中的说明进行操作。

### 失败

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（Path 2 — 同步和异步）、代码生成（Path 3）和自主解决（Path 5）。

**如果完全找不到 Python** → 直接跳转到 [execution-guide.md](references/execution-guide.md) 中的 Path 2 (curl)。

| 错误模式 | 诊断 | 解决方案 |
|----------|------|--------|
| `command not found: python3` | Python 未在 PATH 中 | 尝试 `python` 或 `py -3`；如果缺少，则安装 Python 3.9+ |
| `Python 3.9+ required` | 脚本版本检查失败 | 升级 Python 到 3.9+ |
| `SyntaxError` near type hints | Python < 3.9 | 升级 Python 到 3.9+ |
| `QIANWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取密钥；添加到 `.env`：`echo 'DASHSCOPE_API_KEY=sk-...' >> .env`；或者如果可用，运行 **qianwen-ops-auth** |
| `HTTP 401` | 无效或匹配的密钥不匹配 | 运行 **qianwen-ops-auth**（仅非明文检查）；验证密钥是否有效 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问 | 检查网络；如果通过代理，请设置 `HTTPS_PROXY` |
| `HTTP 429` | 被限流 | 等待并使用退避重试 |
| `HTTP 5xx` | 服务器错误 | 使用退避重试 |
| `PermissionError` | 无法写入输出 | 使用 `--output` 指定可写目录 |

## 快速参考

### 请求字段（常用）

| 字段 | 类型 | 描述 |
|------|------|------|
| `prompt` | string | 要生成图像的文本描述（必需） |
| `negative_prompt` | string | 图像中要避免的内容（最多 500 个字符） |
| `size` | string | 分辨率；支持值和默认值是模型特定的，因此请阅读上述模型目录 |
| `seed` | int | 用于可重复性的随机种子 [0, 2147483647] |
| `model` | string | 模型 ID；检查上述模型目录以获取当前默认值和受支持的模型 |
| `prompt_extend` | bool | 启用提示重写（默认：true；仅图像编辑模式） |

### 请求字段（wan2.7-image-pro / wan2.7-image — 多功能）

| 字段 | 类型 | 描述 |
|------|------|------|
| `reference_images` | string[] | 0–9 图像 URL 或本地路径 |
| `reference_image` | string | 单个图像 URL/路径（简称） |
| `size` | string | `1K`（默认，~1280×1280）或 `2K`（~2048×2048）（pro 仅限，t2i 模式）。或像素尺寸 |
| `enable_sequential` | bool | `true`：顺序多图像模式（n=1–12）。`false`（默认）：单次/批处理模式（n=1–4） |
| `n` | int | 要生成的图像数量。顺序模式：1–12（默认 1）。非顺序：1–4（默认 1）。**按图像计费。** |
| `thinking_mode` | bool | 启用增强推理以获得更好的质量（默认：true）。仅用于 t2i（无图像、非顺序） |
| `bbox_list` | List[List[List[int]]] | 交互式编辑区域。格式：`[[[x1,y1,x2,y2],...], ...]`。列表长度 = 图像数量。没有编辑的图像为空 `[]` |
| `color_palette` | array | 自定义颜色主题（3–10 种颜色）。每个：`{"hex":"#C2D1E6","ratio":"23.51%"}`。比率总和 = 100%。仅非顺序模式 |
| `watermark` | bool | 添加 "AI 生成" 水印（默认：false） |

**注意**：`thinking_mode` 增加延迟但提高质量。`enable_sequential` 生成连贯的图像序列（例如，跨场景的同一角色）。

### 请求字段（wan2.6-image — 图像编辑）

| 字段 | 类型 | 描述 |
|------|------|------|
| `reference_images` | string[] | 1–4 图像 URL 或本地路径用于编辑模式；0–1 用于交错模式 |
| `reference_image` | string | 单个图像 URL/路径（简称；`reference_images` 优先） |
| `enable_interleave` | bool | `false`（默认）：图像编辑模式；`true`：交错文本图像输出 |
| `n` | int | 编辑模式下要生成的图像数量（1–4，默认：1）。**按图像计费。** |
| `max_images` | int | 交错模式中的最大图像数量（1–5，默认：5）。**按图像计费。** |
| `watermark` | bool | 添加 "AI 生成" 水印（默认：false） |

### 其他模型

使用上述模型目录获取当前模型列表和模型特定的兼容性差异。

对于固定分辨率的异步文本到图像模型，其目录条目允许多个输出，捆绑脚本目前将 `n` 限制为 1。当在一个请求中需要多个输出时，请使用 [api-guide.md](references/api-guide.md#text-to-image-models--endpoint--parameters) 中的直接 API 流。

**完整参数表**：参见 [api-guide.md](references/api-guide.md#wan25-i2i-preview--general-image-editing) 获取详细参数。

### 尺寸参考（wan2.6-image）

- **编辑模式**：`1K`（默认，~1280×1280）或 `2K`（~2048×2048）
- **交错模式**：像素尺寸，总像素在 [768×768, 1280×1280]

**常用宽高比**：`1280*1280`（1:1），`960*1280`（3:4），`1280*960`（4:3），`720*1280`（9:16），`1280*720`（16:9）

### 响应字段

| 字段 | 描述 |
|------|------|
| `image_url` | 生成的图像 URL（24 小时有效期）。**当链接到另一个技能时使用此值。** |
| `image_urls` | 所有图像 URL 的数组（多图像输出，wan2.6-image，qwen-image-edit） |
| `image_count` | 生成的图像数量 |
| `local_path` | 下载的图像的本地文件路径。**用于用户预览或非 API 操作。** |
| `local_paths` | 本地文件路径数组（多图像输出） |
| `interleaved_content` | `{type, text/image}` 对象的数组（交错模式） |
| `width` / `height` | 图像尺寸 |
| `seed` | 使用的种子 |

## API 详细信息

- **同步端点（wan2.6-t2i, wan2.6 图像编辑，qwen-image-edit 系列）**：`POST /api/v1/services/aigc/multimodal-generation/generation`
- **异步端点（wan2.6 及更早版本 t2i）**：`POST /api/v1/services/aigc/image-generation/generation` with `X-DashScope-Async: enable`
- **异步端点（wan2.5-i2i-preview）**：`POST /api/v1/services/aigc/image2image/image-synthesis` with `X-DashScope-Async: enable`
- **异步端点（qwen-image-plus, qwen-image-max）**：`POST /api/v1/services/aigc/text2image/image-synthesis` with `X-DashScope-Async: enable`
- **wan2.6-t2i 分辨率**：总像素在 [1280x1280, 1440x1440]，宽高比 [1:4, 4:1]
- **wan2.6-image 分辨率**：编辑模式 [768x768, 2048x2048]；交错模式 [768x768, 1280x1280]；宽高比 [1:4, 4:1]
- **输入图像**（wan2.6-image）：JPEG/JPG/PNG/BMP/WEBP，每维度 240–8000px，≤10MB
- **本地文件**：脚本自动上传到 DashScope 临时存储（`oss://` URL，48 小时 TTL）。直接传递本地路径 — 无需手动上传步骤。
- **生产**：默认临时存储具有 **48 小时 TTL** 和 **100 QPS 上传限制** — 不适用于生产、高并发或负载测试。要使用您自己的 OSS 存储桶，请在 `.env` 中设置 `QWEN_TMP_OSS_BUCKET` 和 `QWEN_TMP_OSS_REGION`，安装 `pip install alibabacloud-oss-v2`，并通过 `QWEN_TMP_OSS_AK_ID` / `QWEN_TMP_OSS_AK_SECRET` 或标准 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 提供凭证。使用具有最小权限的 RAM 用户（仅对目标存储桶上的 `oss:PutObject` + `oss:GetObject`）。如果安装了 qianwen-ops-auth，请参阅其 `references/custom-oss.md` 获取完整设置指南。
- **交错同步**：需要流式传输（`X-DashScope-Sse: enable` + `stream: true`）；请使用此脚本以异步模式代替

## 跨技能链接

当使用生成的图像作为另一个技能的输入（例如，video-gen i2v，vision analyze）时：
- **直接传递 `image_url`** — 绝不要下载并重新传递为本地路径
- 所有下游脚本检测 URL 前缀（`https://`，`oss://`）并将其传递，而无需重新上传
- 仅在用户预览或非 API 操作时使用 `local_path`（例如，在编辑器中打开）

| 场景 | 使用 |
|------|------|
| 链接到另一个技能（video-gen，vision，image-edit） | `image_url`（URL） |
| 显示给用户 / 打开在编辑器中 | `local_path`（本地文件） |

## 错误处理

| HTTP | 含义 | 操作 |
|------|------|------|
| 401 | 无效或缺少 API 密钥 | 如果可用，运行 **qianwen-ops-auth**；否则提示用户设置密钥（仅非明文检查） |
| 400 | 请求错误（无效的提示，大小） | 验证参数和约束 |
| 400 `The product is not activated` / `Model not subscribed` | 账户上未启用第三方模型 | 访问 [模型市场](https://www.qianwenai.com/models)，找到模型，点击“启用”/“开通” |
| 429 | 被限流 | 使用指数退避重试 |
| 5xx | 服务器错误 | 使用指数退避重试 |

> **使用和计费**：使用 **qianwen-usage** 技能检查使用情况、免费套餐配额和计费。或者，用户可以访问 QianWen 控制台：
> [使用分析](https://platform.qianwenai.com/home/analytics) |
> [按量付费计费](https://platform.qianwenai.com/home/billing/pay-as-you-go) |
> [Token 计划订阅](https://platform.qianwenai.com/home/billing/subscription/token-plan)
>
> **绝对不要编造、猜测或构造使用/计费/控制台 URL。** 仅提供此技能中列出的确切链接。如果此处未列出 URL，请不要编造。
