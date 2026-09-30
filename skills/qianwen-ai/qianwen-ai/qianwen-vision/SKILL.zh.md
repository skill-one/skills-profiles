---
name: qianwen-vision
description: 使用 Qwen 视觉模型理解图像和视频。触发条件：当用户需要分析、描述或从图像或视频中提取信息，进行 OCR 文本提取、图表/表格读取、视觉推理、多图像比较、截图理解、视频理解，或明确调用此技能（例如使用 qianwen-vision）时。不触发条件：当用户需要生成/创建图像（使用 qianwen-image-generation）、生成视频（使用 qianwen-video-generation）、仅涉及文本的任务且无视觉输入，或非 Qwen 视觉任务时。
---

# Qwen Vision (图像与视频理解)

使用 Qwen VL 和 QVQ 模型分析图像和视频。
此技能是 **QianWen-AI/qianwen-ai** 的一部分。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 用途 |
|------|------|
| `scripts/analyze.py` | 图像/视频理解、多图像、思考模式 |
| `scripts/reason.py` | 视觉推理 (QVQ、思维链、流式处理) |
| `scripts/ocr.py` | OCR 文本提取 |
| `scripts/vision_lib.py` | 共享辅助工具 (base64、上传、流式处理) |
| `references/execution-guide.md` | 备用：curl、代码生成 |
| `references/curl-examples.md` | curl 用于 base64、多图像、视频、OCR |
| `references/visual-reasoning.md` | QVQ 和思维模式的详细信息 |
| `references/prompt-guide.md` | 按任务查询提示模板、思维模式决策 |
| `references/ocr.md` | OCR 参数和示例 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要明文输出任何 API 密钥或凭证。** 始终使用变量引用 (`$DASHSCOPE_API_KEY` 在 shell 中，`os.environ["DASHSCOPE_API_KEY"]` 在 Python 中)。任何凭证检查或检测都必须是**非明文**的：仅报告状态（例如 "已设置" / "未设置"，"有效" / "无效"），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符 (`DASHSCOPE_API_KEY=sk-your-key-here`)，并指导用户将其替换为他们从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取的实际密钥。仅在用户明确要求时才写入实际密钥值。

## 密钥兼容性

支持 PAYG (`sk-ws-...`；遗留 `sk-...`) 和 Token Plan (`sk-sp-...`) 密钥。检测密钥类型而不暴露密钥：

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
| `payg` | PAYG 密钥 — 可使用完整模型目录。 |
| `not-set` | 未配置密钥。 |

对于 Token Plan，获取并阅读当前的 [Token Plan 模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，然后使用列出的具有视觉能力的精确模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-token-plan-models.md)。

Token Plan 仅支持特定模型 — 使用上述参考中的确切模型；不要猜测或探测模型可用性。对于 PAYG，继续下方操作。

> **Token Plan 用户**：当任务默认值不在 Token Plan 上时，使用下方的 Qwen 视觉模型目录获取当前兼容的替代品。

## 模型选择

在选择、推荐或默认设置模型之前，获取并阅读当前的 [Qwen 视觉模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-vision-models.md)。它包含模型列表、基本模型信息、任务推荐、兼容性说明和默认值。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-vision-models.md)。

1. **用户指定了模型** → 直接使用。
2. **当模型选择取决于需求、场景或定价时，咨询 qianwen-model-selector 技能**。
3. **无信号，任务明确** → 使用模型目录中的默认值和任务特定替代方案。

> **⚠️ 重要提示**：模型目录是一个 **特定时间点的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查 [官方模型列表](https://www.qianwenai.com/models) 以获取权威、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qianwenai.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果 **qianwen-model-selector** 技能或 **QianWen CLI** (`qianwen models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qianwen-usage** 技能了解登录流程。

## 执行

### 前置条件

- **API 密钥**：使用 **密钥兼容性** 中的非明文检测器；不要用变量存在性检查替换它。如果找不到密钥，当可用时使用 qianwen-ops-auth，或指导用户在 `.env` 中配置 `DASHSCOPE_API_KEY`/`QIANWEN_API_KEY`。技能可以独立安装。
- Python 3.9+（仅使用标准库，**不需要 pip 安装**）

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果找不到 `python3`，尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，跳转到 [execution-guide.md](references/execution-guide.md) 中的 **Path 2 (curl)**。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用完整的绝对路径来执行脚本。** 不要假设脚本位于当前工作目录中。不要在执行前使用 `cd` 切换目录。共享基础设施位于 `scripts/vision_lib.py`。

**执行说明**：在 **前台** 运行所有脚本 — 等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/analyze.py --help`（或 `reason.py`，`ocr.py`）以查看所有可用参数。

| 脚本 | 用途 | 默认模型 |
|------|------|----------|
| `scripts/analyze.py` | 图像理解、多图像、视频、思考模式、高分辨率 | 从上方的模型目录中读取当前默认值 |
| `scripts/reason.py` | 带思维链的视觉推理、视频推理（始终流式处理） | 从上方的模型目录中读取当前默认值 |
| `scripts/ocr.py` | 从文档、收据、表格中提取 OCR 文本 | 从上方的模型目录中读取当前默认值 |

**输入类型字段**（在 `--request` JSON 中使用**一个**）：

| 字段 | 用于 | 示例 |
|------|------|------|
| `"image"` | 单个图像（URL 或本地路径） | `"image": "photo.jpg"` |
| `"images"` | 多图像比较（数组） | `"images": ["a.jpg", "b.jpg"]` |
| `"video"` | 视频文件（URL 或本地路径） | `"video": "clip.mp4"` |
| `"video_frames"` | 视频作为帧数组 | `"video_frames": ["f1.jpg", "f2.jpg"]` |

> **⚠️ 常见错误**：不要使用 `"image"` 用于视频文件 — 使用 `"video"` 而不是。

```bash
# 图像分析
python3 <this-skill-dir>/scripts/analyze.py \
  --request '{"prompt":"What is in this image?","image":"https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"}' \
  --output output/qianwen-vision/result.json --print-response

# 视频分析（本地文件 — 添加 --upload-files 用于文件 >= 7 MB）
python3 <this-skill-dir>/scripts/analyze.py \
  --request '{"prompt":"Describe what happens in this video","video":"clip.mp4"}' \
  --upload-files --print-response

python3 <this-skill-dir>/scripts/reason.py \
  --request '{"prompt":"Solve this math problem step by step","image":"problem.png"}' \
  --print-response

python3 <this-skill-dir>/scripts/ocr.py \
  --request '{"image":"invoice.jpg"}' \
  --print-response
```

| 参数 | 描述 |
|------|------|
| `--request '{...}'` | JSON 请求体 |
| `--file path.json` | 从文件加载请求 |
| `--output path` | 将响应 JSON 保存到路径 |
| `--print-response` | 将响应打印到 stdout |
| `--stream` | 启用流式处理（思维/QVQ 自动启用） |
| `--upload-files` | 将本地文件上传到临时存储（用于文件 > 7 MB） |
| `--model ID` | 覆盖模型（每个脚本的默认值：见上表） |
| `--schema path.json` | 结构化提取的 JSON Schema |

> **模型优先级**：`--model` CLI 标志 > `"model"` 字段在 `--request` JSON 中 > 内置默认值。

### 验证结果

- 退出码 `0` + 输出包含有效的 JSON 且有 `choices` 字段 → **成功**
- 非零退出、HTTP 错误、空响应或包含 `"code"`/`"message"` 错误的 JSON → **失败**
- **执行后检查**：当使用 `--output` 时，验证响应 JSON 文件是否存在并包含预期内容
- **强制 — stderr 信号检查**：在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [更新检查](#update-check-mandatory-post-execution) 中的说明进行操作。

### 失败时

如果脚本失败，将错误输出与下方的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（Path 2）、代码生成（Path 3）和自主解决（Path 5）。

**如果 Python 完全不可用** → 直接跳转到 [execution-guide.md](references/execution-guide.md) 中的 Path 2 (curl)。

| 错误模式                    | 诊断                        | 解决方案                                                                                                                                                |
|-----------------------------|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `command not found: python3` | Python 未在 PATH 上         | 尝试 `python` 或 `py -3`；如果缺少，则安装 Python 3.9+                                                                                              |
| `Python 3.9+ required`      | 脚本版本检查失败            | 升级 Python 到 3.9+                                                                                                                                      |
| `SyntaxError` near type hints | Python < 3.9                 | 升级 Python 到 3.9+                                                                                                                                      |
| `QIANWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys) 获取密钥；添加到 `.env`：`echo 'DASHSCOPE_API_KEY=sk-...' >> .env`；或如果可用，运行 **qianwen-ops-auth** |
| `HTTP 401`                  | 无效或匹配错误的密钥        | 运行 **qianwen-ops-auth**（仅非明文检查）；验证密钥是否有效                                                                                              |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量                                                                             |
| `URLError` / `ConnectionError` | 网络无法访问              | 检查互联网；如果使用代理，设置 `HTTPS_PROXY`                                                                                                           |
| `HTTP 429`                  | 被限速                     | 等待并重试，使用退避                                                                                                                                      |
| `HTTP 5xx`                  | 服务器错误                  | 重试，使用退避                                                                                                                                          |
| `PermissionError`           | 无法写入输出                | 使用 `--output` 指定可写目录                                                                                                                             |

## 文件输入

API 接受：**HTTP/HTTPS URL**、**Base64 数据 URI** 和 **`oss://` URL**。本地文件路径**不直接支持** — 脚本会自动转换。**直接传递本地路径；不需要手动上传步骤。**

**大文件规则：如果本地文件 >= 7 MB，始终添加 `--upload-files`。** Base64 编码会使大小增加约 33%，并将超过 10 MB 的 API 限制。小文件（包括短视频剪辑 < 7 MB）可以使用默认的 base64 路径。

> **Token Plan (`sk-sp-...`) 例外**：`--upload-files` 临时上传端点对 Token Plan 密钥不可用，并将以友好的错误进行阻止。Token Plan 用户应使用默认 base64 路径用于本地文件；对于文件 >= 7 MB，传递可访问的 URL (`https://` 或 `oss://`) 而不是 `--upload-files`。

| 方法 | 使用场景 | 如何 |
|------|----------|------|
| **在线 URL** | 文件已托管 | 直接传递 URL — **对于大文件首选** |
| **Base64**（默认） | 本地文件 < 7 MB（图像或短视频剪辑） | 脚本自动转换为 `data:` URI |
| **临时上传** | 本地文件 >= 7 MB | 添加 `--upload-files` 标志 → 上传到 DashScope 临时存储 (`oss://` URL，48h TTL) |

> **生产**：默认临时存储有 **48h TTL** 和 **100 QPS 上传限制** — 不适用于生产、高并发或负载测试。要使用您自己的 OSS 存储桶，请在 `.env` 中设置 `QWEN_TMP_OSS_BUCKET` 和 `QWEN_TMP_OSS_REGION`，安装 `pip install alibabacloud-oss-v2`，并通过 `QWEN_TMP_OSS_AK_ID` / `QWEN_TMP_OSS_AK_SECRET` 或标准的 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 提供凭证。使用具有最小权限的 RAM 用户（仅对目标存储桶上的 `oss:PutObject` + `oss:GetObject`）。`--upload-files` 标志仍然需要用于视觉脚本以触发上传。如果安装了 qianwen-ops-auth，请参阅其 `references/custom-oss.md` 以获取完整设置指南。

## 来自其他技能的输入

当输入文件来自另一个技能的输出（例如，图像生成、视频生成）时：
- **直接传递 URL**（例如，`"image": "<image_url from image-gen>"`） — 不要先下载 URL
- 下载并重新传递为本地路径会浪费带宽并触发不必要的 base64 编码或 OSS 上传
- 所有 URL 类型都受支持：`https://`、`oss://`、`data:`

## 思考模式

使用上述链接的 Qwen 视觉模型目录获取当前思考默认值和模型兼容性。有关执行详细信息，请参阅 [visual-reasoning.md](references/visual-reasoning.md)。

## OCR

使用上述链接的 Qwen 视觉模型目录获取当前 OCR 默认值、替代方案和模型功能。有关参数和示例，请参阅 [ocr.md](references/ocr.md)。

## 输入限制

**图像**：BMP/JPEG/PNG/TIFF/WEBP/HEIC。最小边长 10px，宽高比 <= 200:1。检查上方的模型目录以获取模型特定的尺寸限制。

**视频**：MP4/AVI/MKV/MOV/FLV/WMV。检查上方的模型目录以获取模型特定的时长和尺寸限制。fps 范围 [0.1, 10]，默认 2.0。

## 错误处理

| HTTP | 含义 | 操作 |
|------|------|------|
| 401 | 无效或缺少 API 密钥 | 如果可用，运行 **qianwen-ops-auth**；否则提示用户设置密钥（仅非明文检查） |
| 400 | 请求错误（格式无效） | 验证消息格式和图像 URL/格式 |
| 429 | 被限速 | 使用指数退避重试 |
| 5xx | 服务器错误 | 使用指数退避重试 |

> **使用与计费**：使用 **qianwen-usage** 技能直接检查使用情况、免费套餐配额和计费信息。或者，用户可以访问 QianWen 控制台：
> [使用分析](https://platform.qianwenai.com/home/analytics) |
> [按量计费](https://platform.qianwenai.com/home/billing/pay-as-you-go) |
> [令牌计划订阅](https://platform.qianwenai.com/home/billing/subscription/token-plan)
>
> **绝对不要编造、猜测或构造使用情况/计费/控制台 URL。** 仅提供本技能中列出的确切链接。如果此处未列出 URL，则不要自行编造。

## 输出位置

优先选择 **当前工作目录**。默认子目录：`./output/qianwen-vision/`。

**写入禁止**：绝对不要将输出文件写入此技能的安装目录或任何 `skills/` 层级结构。所有生成内容必须放置在当前工作目录下的 `output/` 或用户指定路径中。

## 更新检查（执行后强制）

执行脚本后，检查标准错误输出以获取操作信号。脚本会自动检测更新状态并发出结构化信号。你必须根据这些信号采取行动。当用户明确要求检查更新时，本节同样适用。

### 信号：`[ACTION_REQUIRED] qianwen-update-check 技能未安装`

当标准错误输出包含此信号时，你必须向用户展示以下选项，并在他们响应之前**等待其反馈**。不要无声地跳过此步骤。

> 更新检查技能未安装。它将向您提供有关 QianWen-AI/qianwen-ai 新功能和错误修复的信息。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何操作
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QianWen-AI/qianwen-ai --skill qianwen-update-check -y`，然后运行：`python3 <此技能脚本目录>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <此技能脚本目录>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <此技能脚本目录>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当标准错误输出包含此信号时，你必须将简短的更新通知追加到你的响应中，包括版本信息和标准错误输出中显示的更新命令。

### 标准错误输出中无信号

如果标准错误输出既不包含 `[ACTION_REQUIRED]` 也不包含 `[UPDATE_AVAILABLE]`，则无需采取行动——技能已安装且为最新版本（或在 24 小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如，“检查更新”、“检查版本”）时：
1. 在同级技能目录中查找 `qianwen-update-check/SKILL.md`。
2. 如果找到——运行：`python3 <qianwen-update-check 目录>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到——展示上述安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 回退路径（curl、代码生成、自主）
- [curl-examples.md](references/curl-examples.md) — curl 模板（base64、多图像、视频、OCR）
- [api-guide.md](references/api-guide.md) — API 补充指南
- [visual-reasoning.md](references/visual-reasoning.md) — QVQ 视觉推理指南
- [ocr.md](references/ocr.md) — Qwen-VL-OCR 文本提取指南
- [sources.md](references/sources.md) — 官方文档 URL
