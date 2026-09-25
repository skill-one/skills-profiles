# Qwen 文本聊天 (兼容 OpenAI)

通过兼容 OpenAI 的 API 使用 Qwen 模型生成文本、进行对话、编写代码和调用工具。
这项技能是 **QianWen-AI/qianwen-ai** 的一部分。

## 技能目录

使用这项技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置                          | 用途                                                                             |
|-------------------------------|----------------------------------------------------------------------------------|
| `scripts/text.py`             | 默认执行 — 聊天/补全请求、流式传输、输出保存                                          |
| `references/execution-guide.md` | 备用方案：curl、Python SDK、函数调用、思考模式                                       |
| `references/api-guide.md`     | API 补充和完整代码示例                                                         |
| `references/prompt-guide.md`  | 提示工程：CO-STAR 框架、CoT、少样本、任务步骤                                       |
| `references/sources.md`       | 官方文档 URL（仅手动查找）                                                     |

## 安全

**绝对不要明文输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$DASHSCOPE_API_KEY`，Python 中的 `os.environ["DASHSCOPE_API_KEY"]`）。任何凭证检查或检测都必须**非明文**：仅报告状态（例如“已设置”/“未设置”，“有效”/“无效”），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符（`DASHSCOPE_API_KEY=sk-your-key-here`），并指导用户将其替换为他们从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取的实际密钥。只有在用户明确要求时才写入实际密钥值。

## 密钥兼容性

同时支持 PAYG (`sk-ws-...`；遗留 `sk-...`) 和 Token 计划 (`sk-sp-...`) 密钥。检测 API 密钥类型而不暴露密钥：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qianwen_lib import detect_api_key_type
print(detect_api_key_type('scripts/qianwen_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | Token 计划密钥 — 仅使用 Token 计划目录下列出的模型。 |
| `payg` | 按量付费密钥 — 可使用完整模型目录。 |
| `not-set` | 未配置密钥。 |

对于 Token 计划，获取并阅读当前的 [Token 计划模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，然后使用上面列出的确切模型。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qianwen-token-plan-models.md)。

Token 计划仅支持特定模型 — 使用上面参考中的确切模型；不要猜测或探测模型可用性。对于 PAYG，继续向下阅读。

## 模型选择

在选择、推荐或默认模型之前，获取并阅读当前的 [Qwen 文本模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-text-models.md)。它包含模型列表、基本模型信息、推荐和默认模型。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qianwen-text-models.md)。

1. **用户指定了模型** → 直接使用。
2. **当模型选择取决于需求、场景或定价时，咨询 qianwen-model-selector 技能**。
3. **无信号，清晰任务** → 使用模型目录中的默认值。对于最强的推理/编码，使用其推荐的具有高能力的选项。

> **⚠️ 重要**：模型目录是一个**特定时间点的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查[官方模型列表](https://www.qianwenai.com/models)以获取权威的、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qianwenai.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果 **qianwen-model-selector** 技能或 **QianWen CLI** (`qianwen models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qianwen-usage** 技能的登录流程。

## 执行

### 前置条件

- **API 密钥**：在 **密钥兼容性** 中使用非明文检测器；不要用变量存在性检查替换它。如果找不到密钥，在可用时使用 qianwen-ops-auth，或指导用户在 `.env` 中配置 `DASHSCOPE_API_KEY`/`QIANWEN_API_KEY`。技能可以独立安装。
- Python 3.9+（仅标准库，**脚本执行不需要 pip 安装**）

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果 `python3` 未找到，尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，跳转到 [execution-guide.md](references/execution-guide.md) 中的 *Path 2 (curl)*。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行。** 不要假设脚本位于当前工作目录中。不要在执行前使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本 — 等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/text.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/text.py \
  --request '{"messages":[{"role":"user","content":"Hello!"}],"model":"qwen3.7-plus"}' \
  --output output/qianwen-text/ --print-response
```

对于流式传输（推荐用于交互式使用）：

```bash
python3 <this-skill-dir>/scripts/text.py \
  --request '{"messages":[{"role":"user","content":"写一首关于大海的诗"}],"model":"qwen3.7-plus"}' \
  --stream --print-response
```

| 参数            | 描述                                         |
|-----------------|---------------------------------------------|
| `--request '{...}'` | JSON 请求体                                   |
| `--file path.json`  | 从文件加载请求（`--request` 的替代方案） |
| `--stream`          | 启用流式输出                             |
| `--output path`     | 将响应 JSON 保存到路径（如果 `.json` 后缀，则为文件，否则为目录）；跨调用使用不同的文件名以避免覆盖 |
| `--print-response`  | 将响应打印到 stdout                         |
| `--model ID`        | 覆盖模型（也可以在请求 JSON 中设置）      |

> **模型优先级**：`--model` CLI 标志 > `"model"` 字段在 `--request` JSON 中 > 内置默认值。

### 验证结果

- 退出码 `0` + 输出包含有效的 JSON 且具有 `choices` 字段 → **成功**
- 非零退出码、HTTP 错误、空响应或包含 `"code"`/`"message"` 错误的 JSON → **失败**
- 如果代理无法读取退出码，扫描输出以查找错误模式（`Error`、`Traceback`、`401`、`403`）
- **执行后检查**：当使用 `--output` 时，验证响应 JSON 文件是否存在并包含 `choices`
- **强制 — stderr 信号检查**：在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前按照 [执行后强制更新检查](#update-check-mandatory-post-execution) 下的说明进行操作。

### 失败

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（Path 2）、Python SDK 代码生成（Path 3）和自主解决（Path 5）。

**如果完全无法使用 Python** → 直接跳转到 [execution-guide.md](references/execution-guide.md) 中的 Path 2 (curl)。

| 错误模式                    | 诊断                        | 解决方案                                                                   |
|-----------------------------|-----------------------------|----------------------------------------------------------------------------|
| `command not found: python3`     | Python 不在 PATH 上         | 尝试 `python` 或 `py -3`；如果缺少，请安装 Python 3.9+                      |
| `Python 3.9+ required`           | 脚本版本检查失败            | 升级 Python 到 3.9+                                                       |
| `SyntaxError` near type hints    | Python < 3.9                 | 升级 Python 到 3.9+                                                       |
| `QIANWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys) 获取密钥；添加到 `.env`：`echo 'DASHSCOPE_API_KEY=sk-...' >> .env`；或者如果可用，运行 **qianwen-ops-auth** |
| `HTTP 401`                       | 无效或密钥不匹配            | 运行 **qianwen-ops-auth**（仅非明文检查）；验证密钥是否有效                 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError`   | 网络无法访问              | 检查互联网；如果通过代理，设置 `HTTPS_PROXY`                            |
| `HTTP 429`                       | 超出速率限制                 | 等待并重试，使用退避策略                                                  |
| `HTTP 5xx`                       | 服务器错误                     | 重试；检查状态页面                                                           |
| `PermissionError`                | 无法写入输出               | 使用 `--output` 指定可写目录                                               |

## 快速参考

### 请求字段

| 字段                 | 类型            | 描述                                                                                          |
|----------------------|-----------------|------------------------------------------------------------------------------------------------|
| `prompt` / `messages` | string \| array | 用户输入或消息列表                                                                           |
| `model`               | string          | 模型 ID（例如 `qwen3.7-plus`）                                                                       |
| `system`              | string          | 系统提示（可选）                                                                             |
| `temperature`         | float           | 0–2，控制随机性                                                                             |
| `max_tokens`          | int             | 最大输出 token 数量                                                                          |
| `tools`               | array           | 用于工具调用的函数定义                                                                      |
| `stream`              | bool            | 启用流式传输（推荐用于交互式使用）                                                               |
| `enable_thinking`     | bool            | 启用思考模式。模型默认值各不相同；在覆盖它们之前，请检查上面的模型目录。对实时任务增加了延迟。 |

### 响应字段

| 字段        | 描述                                    |
|-------------|-----------------------------------------|
| `text`      | 生成的文本内容                         |
| `model`     | 使用的模型                             |
| `usage`     | token 使用情况（prompt_tokens、completion_tokens） |
| `tool_calls` | 函数调用请求（如果使用了工具）         |

## 高级功能

这些是通过请求参数支持的 API 级功能。所有功能都使用相同的 `chat/completions` 端点。

| 功能               | 如何启用                                                    | 备注                                          |
|-------------------|------------------------------------------------------------------|------------------------------------------------|
| **结构化输出**     | `response_format: {"type": "json_schema", "json_schema": {...}}` | 强制 JSON 输出符合模式                     |
| **网络搜索**        | `enable_search: true`                                            | 实时网络搜索增强响应                       |
| **深度思考**     | `enable_thinking: true`                                          | 扩展推理；仅在用户请求时使用               |
| **函数调用**      | `tools: [...]`                                                   | 定义用于工具使用的函数                     |
| **上下文缓存**     | 自动针对重复的前缀；或显式基于会话                           | 减少重复上下文的成本                      |
| **部分模式**      | 最后一条消息：`{"role": "assistant", "content": "prefix…", "partial": true}` | 继续或完成前缀                     |
| **批量推理**      | 异步批量 API，使用 JSONL 输入                                 | 成本降低 50%                              |

有关每个功能的详细用法，请参阅 [api-guide.md](references/api-guide.md) 和 [sources.md](references/sources.md)。

## 错误处理

| 错误                   | 原因                               | 操作                                                                                     |
|------------------------|-------------------------------------|--------------------------------------------------------------------------------------------|
| `401 Unauthorized`      | 无效或缺少 API 密钥              | 如果可用，运行 **qianwen-ops-auth**；否则提示用户设置密钥（仅非明文检查）                 |
| `429 Too Many Requests` | 速率限制超出                 | 重试，使用退避策略                                                                         |
| `500` / `502` / `503`   | 服务器错误                        | 重试；检查状态页面                                                                   |
| `Invalid model`         | 模型 ID 未找到                  | 将 ID 与上面的模型目录进行验证 |
| `Invalid parameter`     | 请求体错误                    | 验证 JSON 和字段类型                                                              |
| `TypeError: ...proxies` | openai SDK 与 httpx 不兼容     | `pip install --upgrade openai` (>=1.55.0)；或使用脚本（纯标准库）                     |

> **使用情况 & 账单**：使用 **qianwen-usage** 技能直接检查使用情况、免费套餐配额和账单。或者，用户可以访问 QianWen 控制台：
> [使用分析](https://platform.qianwenai.com/home/analytics) |
> [按量付费账单](https://platform.qianwenai.com/home/billing/pay-as-you-go) |
> [Token 计划订阅](https://platform.qianwenai.com/home/billing/subscription/token-plan)
>
> **绝对不要编造、猜测或构造使用情况/账单/控制台 URL。** 仅提供此技能中列出的确切链接。如果此处未列出 URL，请不要编造一个。

## 输出位置

所有输出都优先使用**当前工作目录**。当使用 `--output` 时，默认子目录：
`./output/qianwen-text/`。

**写入禁止**：绝对不要将输出文件写入此技能的安装目录或任何 `skills/` 层次结构。所有生成的内容必须位于当前工作目录的 `output/` 下或用户指定的路径。

## 更新检查（执行后强制）

脚本执行后，检查 stderr 以查找操作信号。脚本自动检测更新状态并发出结构化信号。您必须对此采取行动。本节也适用于用户明确要求检查更新时。

### 信号：`[ACTION_REQUIRED] qianwen-update-check 技能未安装`

当 stderr 包含此信号时，您必须向用户展示以下选项，并在**等待其响应后**再继续。不要无声地跳过。

> 更新检查技能未安装。它让您了解 QianWen-AI/qianwen-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何事情
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：

- 用户选择 **1** → 运行：
  `npx skills add QianWen-AI/qianwen-ai --skill qianwen-update-check -y`，然后运行：
  `python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行： `python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行： `python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须将简短的更新通知附加到您的响应中，包括版本信息和 stderr 输出中显示的更新命令。

### stderr 中没有信号

如果 stderr 既不包含 `[ACTION_REQUIRED]` 也不包含 `[UPDATE_AVAILABLE]`，则无需采取任何操作 — 技能已安装且是最新的（或在 24 小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如“检查更新”、“检查版本”）时：

1. 在兄弟技能目录中查找 `qianwen-update-check/SKILL.md`。
2. 如果找到 — 运行： `python3 <qianwen-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到 — 显示上面的安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 备用路径（curl、SDK、自主），函数调用、思考模式
- [api-guide.md](references/api-guide.md) — API 补充指南，包含完整代码示例
- [sources.md](references/sources.md) — 官方文档 URL
