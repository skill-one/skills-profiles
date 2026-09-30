---
name: qwencloud-vision
description: 使用 Qwen 视觉模型理解图像和视频。在以下情况时触发：用户希望分析、描述或从图像或视频中提取信息，OCR 文本提取，图表/表格读取，视觉推理，多图像比较，截图理解，视频理解，或明确通过名称调用此技能（例如使用 qwencloud-vision）。不触发的情况：用户希望生成/创建图像（使用 qwencloud-image-generation），生成视频（使用 qwencloud-video-generation），仅文本的任务且没有视觉输入，或非 Qwen 视觉任务。
---

# Qwen Vision (图像与视频理解)

使用 Qwen VL 和 QVQ 模型分析图像和视频。
此技能是 **qwencloud/qwencloud-ai** 的一部分。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 目的 |
|------|---------|
| `scripts/analyze.py` | 图像/视频理解，多图像，思考模式 |
| `scripts/reason.py` | 视觉推理 (QVQ，思维链，流式) |
| `scripts/ocr.py` | OCR 文本提取 |
| `scripts/vision_lib.py` | 共享辅助函数 (base64，上传，流式) |
| `references/execution-guide.md` | 备用：curl，代码生成 |
| `references/curl-examples.md` | curl 用于 base64，多图像，视频，OCR |
| `references/visual-reasoning.md` | QVQ 和思维模式详细信息 |
| `references/prompt-guide.md` | 按任务查询提示模板，思维模式决策 |
| `references/ocr.md` | OCR 参数和示例 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要以明文形式输出任何 API 密钥或凭证。** 始终使用变量引用 (`$QWENCLOUD_API_KEY` 在 shell 中，`os.environ["QWENCLOUD_API_KEY"]` 在 Python 中)。脚本接受 `QWENCLOUD_API_KEY`，然后是 `QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`。任何凭证检查或检测都必须是**非明文**的：仅报告状态（例如 "已设置" / "未设置"，"有效" / "无效"），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符 (`QWENCLOUD_API_KEY=sk-your-key-here`)，并指示用户将其替换为他们从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)获取的实际密钥。除非用户明确要求，否则绝不要写入实际密钥值。

## 关键兼容性

脚本支持**标准 QwenCloud API 密钥** (`sk-...`) 和**令牌计划密钥** (`sk-sp-...`)。令牌计划密钥会自动路由到支持的多模态模型的令牌计划端点——请参阅 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qwencloud-token-plan-models.md)。

**令牌计划：不要使用 curl；始终使用捆绑的 Python 脚本。**

编码计划密钥（也具有 `sk-sp-` 前缀，但通过编码计划订阅购买）不能用于直接 API 调用。脚本在启动时检测密钥类型并进行相应路由。如果安装了 qwencloud-ops-auth，请参阅其 `references/codingplan.md` 以获取当前模型覆盖范围、端点映射和错误详细信息。

在不暴露密钥的情况下检测 API 密钥类型：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qwencloud_lib import detect_api_key_type
print(detect_api_key_type('scripts/qwencloud_lib.py'))
"
```

| 输出 | 含义 |
|--------|---------|
| `token-plan` | 检测到令牌计划密钥 (`sk-sp-` 前缀) |
| `payg` | 检测到标准 PAYG 密钥 |
| `not-set` | 环境中未找到 API 密钥 |

## 模型选择

> **🚫 关键警告 — 绝对不要覆盖用户指定的参数。** 如果用户明确指定了模型（在提示或请求 JSON 中），您必须使用该模型。不要：
> - 用一个“更适合”或更新的模型替换它（例如，因为更新的文档“更喜欢”将用户的 `qwen3-vl-plus` 替换为 `qwen3.7-plus`/`qwen3.8-max`）
> - 添加用户未请求的参数 (`enable_thinking`, `thinking_budget`, `vl_high_resolution_images`, `detail`），除了捆绑脚本在用户请求 `json_mode`/`schema` 且省略了设置时必须发送 `enable_thinking: false`
> - “优化”任何明确用户的选择
>
> 以下选择指导仅适用于**用户未指定模型**的情况。

在选择、推荐或默认模型之前，请获取并阅读当前的 [QwenCloud 视觉模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-vision-models.md)。它包含模型列表、基本模型信息、任务推荐、兼容性说明和默认值。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qwencloud-vision-models.md)。

1. **用户指定了模型** → **强制：使用该模型**——不要替换或“优化”它。除了上述结构化输出兼容性行为外，不要添加未请求的参数；不要将仅限思考的模型替换为静默替换。
2. **当模型选择取决于需求、场景或定价时**，请咨询 qwencloud-model-selector 技能。
3. **无信号，清晰任务** → 使用模型目录中的默认值和特定任务替代方案。专用脚本默认值独立于密钥类型；令牌计划用户应在他们的计划中从目录中选择兼容模型，当默认值不可用时。

> **⚠️ 重要提示**：模型目录是一个**特定时间点的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查[官方模型列表](https://www.qwencloud.com/models)
> 以获取权威、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至其详细信息页面：`https://www.qwencloud.com/models/<model-name>`（将 `<model-name>` 替换为确切的模型 ID，例如 `qwen3.6-plus` → https://www.qwencloud.com/models/qwen3.6-plus）。绝不要修改或猜测 URL 中的模型名称。

> **动态模型查询**：如果 **qwencloud-model-selector** 技能或 **QwenCloud CLI** (`qwencloud models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证——请参阅 **qwencloud-usage** 技能以获取登录流程。

## 执行

### 前置条件

- **API 密钥**：使用**非明文**检查仅检查 `QWENCLOUD_API_KEY`，`QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`（例如在 shell 中：`[ -n "$QWENCLOUD_API_KEY" ]`）；仅报告“已设置”或“未设置”，绝不能显示密钥值）。如果未设置：如果可用，运行 *qwencloud-ops-auth* 技能；否则，指导用户从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)获取密钥，并通过 `.env` 文件（在项目根目录或当前目录中：`echo 'QWENCLOUD_API_KEY=sk-your-key-here' >> .env`）或环境变量设置。脚本在当前工作目录和项目根目录中搜索 `.env`。技能可以独立安装——不要假设 qwencloud-ops-auth 存在。
  **注意**：脚本自动从当前目录和项目根目录加载 `.env`（除了任何导出的环境变量）。显示 `$QWENCLOUD_API_KEY` 为“未设置”的 shell 检查**不意味着**脚本会失败——它可能仍在 `.env` 中找到密钥。将 shell 检查视为信息性；权威测试只是运行脚本（如果没有在任何地方找到密钥，它将退出并显示清晰的错误）。
- Python 3.9+（仅使用标准库，**不需要 pip 安装**）

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果 `python3` 不可用或低于 3.9，PAYG 可能使用**路径 2 (curl)**；令牌计划必须安装 Python 3.9+。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行脚本。** 不要假设脚本位于当前工作目录中。执行前**不要**使用 `cd` 切换目录。共享基础设施位于 `scripts/vision_lib.py`。

**执行说明**：在**前台**运行所有脚本——等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/analyze.py --help`（或 `reason.py`，`ocr.py`）以查看所有可用参数。

| 脚本 | 目的 | 默认模型 |
|--------|---------|---------------|
| `scripts/analyze.py` | 图像理解，多图像，视频，思考模式，高分辨率 | 从上面模型目录中读取当前默认值 |
| `scripts/reason.py` | 带思维链的视觉推理，视频推理（始终流式） | 从上面模型目录中读取当前默认值 |
| `scripts/ocr.py` | 从文档、收据、表格中提取 OCR 文本 | 从上面模型目录中读取当前默认值 |

**输入类型字段**（在 `--request` JSON 中使用**一个**）：

| 字段 | 用于 | 示例 |
|-------|---------|--------|
| `"image"` | 单个图像（URL 或本地路径） | `"image": "photo.jpg"` |
| `"images"` | 多图像比较（数组） | `"images": ["a.jpg", "b.jpg"]` |
| `"video"` | 视频文件（URL 或本地路径） | `"video": "clip.mp4"` |
| `"video_frames"` | 视频作为帧数组 | `"video_frames": ["f1.jpg", "f2.jpg"]` |

> **⚠️ 常见错误**：不要使用 `"image"` 用于视频文件——应使用 `"video"`。

```bash
# 图像分析
python3 <this-skill-dir>/scripts/analyze.py \
  --request '{"prompt":"What is in this image?","image":"https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"}' \
  --output output/qwencloud-vision/result.json --print-response

# 视频分析（本地文件——对于文件 >= 7 MB 添加 --upload-files）
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
|--------|-------------|
| `--request '{...}'` | JSON 请求正文 |
| `--file path.json` | 从文件加载请求 |
| `--output path` | 将响应 JSON 保存到路径 |
| `--print-response` | 将响应打印到 stdout |
| `--stream` | 启用流式传输（对于思考/QVQ 自动） |
| `--upload-files` | 将本地文件上传到临时存储（对于文件 > 7 MB） |
| `--schema path.json` | 结构化提取的 JSON Schema |

### 验证结果

- 退出码 `0` + 输出包含有效的 JSON 且具有 `choices` 字段 → **成功**
- 非零退出，HTTP 错误，空响应，或包含 `"code"`/`"message"` 错误的 JSON → **失败**
- **执行后检查**：当使用 `--output` 时，验证响应 JSON 文件是否存在并包含预期内容
- **强制 — stderr 信号检查**：在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [更新检查](#update-check-mandatory-post-execution) 中的说明进行操作。

### 失败时

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（路径 2），代码生成（路径 3）和自主解决（路径 5）。

**如果完全无法使用 Python** → PAYG 可能使用 Path 2 (curl)；令牌计划必须安装 Python 3.9+。

| 错误模式                    | 诊断                        | 解决方案                                                                                                                                                  |
|----------------------------------|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `command not found: python3`     | Python 不在 PATH               | 尝试 `python` 或 `py -3`；如果缺少，则安装 Python 3.9+                                                                                                     |
| `Python 3.9+ required`           | 脚本版本检查失败              | 升级 Python 到 3.9+                                                                                                                                      |
| `SyntaxError` near type hints    | Python < 3.9                     | 升级 Python 到 3.9+                                                                                                                                      |
| `QWENCLOUD_API_KEY/QWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)获取密钥；添加到 `.env`：`echo 'QWENCLOUD_API_KEY=sk-...' >> .env`；或者如果可用，运行 **qwencloud-ops-auth** |
| `HTTP 401`                       | 无效或匹配错误的密钥        | 运行 **qwencloud-ops-auth**（仅非明文检查）；验证密钥是否有效                                                                                  |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司）    | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量                                                                                 |
| `URLError` / `ConnectionError`   | 网络无法访问              | 检查网络；如果通过代理，请设置 `HTTPS_PROXY`                                                                                                           |
| `HTTP 429`                       | 被限速                     | 等待并重试带退避                                                                                                                                 |
| `HTTP 5xx`                       | 服务器错误                     | 带退避重试                                                                                                                                          |
| `PermissionError`                | 无法写入输出               | 使用 `--output` 指定可写目录                                                                                                                |

## 文件输入

API 接受：**HTTP/HTTPS URL**，**Base64 数据 URI** 和 **`oss://` URL**。本地文件路径**不直接支持**——脚本会自动处理转换。**直接传递本地路径；不需要手动上传步骤。**

**大文件规则：如果本地文件 >= 7 MB，始终添加 `--upload-files`。** Base64 编码会使大小增加约 33%，并将超过 10 MB 的 API 限制。小文件（包括短视频剪辑 < 7 MB）可以使用默认的 base64 路径。

| 方法 | 使用时机 | 如何 |
|--------|-------------|-----|
| **在线 URL** | 文件已托管 | 直接传递 URL ——**对于大文件首选** |
| **Base64** (默认) | 本地文件 < 7 MB (图像或短视频剪辑) | 脚本自动转换为 `data:` URI |
| **临时上传** | 本地文件 >= 7 MB | 添加 `--upload-files` 标志 → 上传到 DashScope 临时存储 (`oss://` URL，48 小时 TTL) |

> **生产环境**：默认临时存储具有 **48 小时 TTL** 和 **100 QPS 上传限制**——不适合生产、高并发或负载测试。要使用您自己的 OSS 存储桶，请在 `.env` 中设置 `QWEN_TMP_OSS_BUCKET` 和 `QWEN_TMP_OSS_REGION`，安装 `pip install alibabacloud-oss-v2`，并通过 `QWEN_TMP_OSS_AK_ID` / `QWEN_TMP_OSS_AK_SECRET` 或标准的 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` 提供凭证。使用具有最少权限的 RAM 用户（仅对目标存储桶上的 `oss:PutObject` + `oss:GetObject`）。`--upload-files` 标志仍然需要触发上传。如果安装了 qwencloud-ops-auth，请参阅其 `references/custom-oss.md` 以获取完整设置指南。

## 从其他技能获取输入

当输入文件来自其他技能的输出（例如：image-gen、video-gen）时：
- **直接传递 URL**（例如：`"image": "<来自 image-gen 的 image_url>"`）——不要先下载该 URL
- 先下载再作为本地路径传递会浪费带宽，并触发不必要的 base64 编码或 OSS 上传
- 支持所有 URL 类型：`https://`、`oss://`、`data:`

## 思考模式

使用上方链接的视觉模型目录，查看当前的思考模式默认设置和模型兼容性。除非用户明确要求更改，否则不要设置 `enable_thinking` —— 既不要因为“任务看起来复杂”而启用它，也不要因为“任务看起来简单”而禁用它。唯一的兼容性例外是结构化输出：`json_mode` 和 `schema` 需要非思考模式，因此捆绑的脚本会在未设置该参数时自动发送 `enable_thinking: false`，并拒绝显式的 `true`。仅支持思考模式的模型不能用于结构化输出。

详情参见 [visual-reasoning.md](references/visual-reasoning.md)。

## OCR

使用上方链接的视觉模型目录，查看当前的 OCR 默认设置、替代方案及模型能力。参数和示例参见 [ocr.md](references/ocr.md)。

## 输入限制

**图片**：BMP/JPEG/PNG/TIFF/WEBP/HEIC。最短边至少 10px，宽高比 <= 200:1。请检查上方模型目录中特定模型的大小限制。

**视频**：MP4/AVI/MKV/MOV/FLV/WMV。请检查上方模型目录中特定模型的时长和大小限制。fps 范围 [0.1, 10]，默认值为 2.0。

## 错误处理

| HTTP | 含义 | 操作 |
|------|------|--------|
| 401 | API 密钥无效或缺失 | 如果可用，运行 **qwencloud-ops-auth**；否则提示用户设置密钥（仅进行非明文检查） |
| 400 | 无效请求（格式错误） | 验证消息格式以及图片 URL/格式 |
| 429 | 触发速率限制 | 使用指数退避重试 |
| 5xx | 服务器错误 | 使用指数退避重试 |

> **使用量与计费**：使用 **qwencloud-usage** 技能直接检查使用量、免费额度配额和计费。或者，用户可以访问 QwenCloud 控制台：
> [使用量分析](https://home.qwencloud.com/analytics) |
> [按量计费](https://home.qwencloud.com/billing/pay-as-you-go) |
> [编码计划计费](https://home.qwencloud.com/billing/coding-plan)
>
> **切勿捏造、猜测或构建使用量/计费/控制台 URL。** 仅提供本技能中列出的精确链接。如果此处未列出某个 URL，请勿自行编造。

## 输出位置

优先使用**当前工作目录**。默认子目录：`./output/qwencloud-vision/`。

**写入禁止**：切勿将输出文件写入此技能的安装目录或任何 `skills/` 层级。所有生成的内容必须放置在当前工作目录下的 `output/` 或用户指定的路径中。

## Token Plan 支持

Token Plan 密钥（`sk-sp-...`）支持具有视觉能力的多模态模型。

### 支持的视觉模型

获取并阅读当前的 [Token Plan 模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)，然后使用列表中精确列出的支持视觉的模型。如果 CDN 访问失败，请使用 [本地回退方案](cdn/references/qwencloud-token-plan-models.md)。

这些模型使用 OpenAI 兼容的聊天 API 和包含多模态消息格式（image_url 内容类型）。

### 默认设置

当未提供模型时，每个脚本都会使用其配置的默认值，无论密钥类型如何。请检查视觉和 Token Plan 目录以了解当前的兼容性。显式提供的请求模型始终优先。

### Token Plan 不支持的情况

Token Plan 模型目录中未列为支持视觉的模型需要 PAYG 密钥。仅在用户明确同意的情况下，建议从视觉目录中选择兼容的替代方案。切勿因密钥类型限制而静默替换用户指定的模型；请列出选项并让用户选择。

### 必需的请求头

`User-Agent: qwencloud-skills` 会自动包含在内。

## 更新检查（强制执行后必选）

在脚本执行后，检查 stderr 中的操作信号。脚本会自动检测更新状态并发出结构化信号。您必须对它们作出响应。当用户明确要求检查更新时，本节同样适用。

### 信号：`[ACTION_REQUIRED] qwencloud-update-check skill is not installed`

当 stderr 包含此信号时，您必须向用户展示以下选项，并**在继续之前等待其响应**。切勿静默跳过此步骤。

> 未安装更新检查技能。它可让您及时了解 qwencloud/qwencloud-ai 的新特性和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不执行任何操作
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QwenCloud/qwencloud-ai --skill qwencloud-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须在响应末尾添加简短的更新通知，包括 stderr 输出中显示的版本信息和更新命令。

### stderr 中无信号

如果 stderr 中既没有 `[ACTION_REQUIRED]` 也没有 `[UPDATE_AVAILABLE]`，则无需采取任何操作——技能已安装且为最新版本（或在 24 小时内的缓存中）。

### 用户显式请求

当用户明确要求检查更新时（例如“检查更新”、“检查版本”）：
1. 在相邻技能目录中查找 `qwencloud-update-check/SKILL.md`。
2. 如果找到——运行：`python3 <qwencloud-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到——展示上述安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 回退路径（curl、代码生成、自主运行）
- [curl-examples.md](references/curl-examples.md) — Curl 模板（base64、多图、视频、OCR）
- [api-guide.md](references/api-guide.md) — API 补充指南
- [visual-reasoning.md](references/visual-reasoning.md) — QVQ 视觉推理指南
- [ocr.md](references/ocr.md) — Qwen-VL-OCR 文本提取指南
- [sources.md](references/sources.md) — 官方文档 URL
