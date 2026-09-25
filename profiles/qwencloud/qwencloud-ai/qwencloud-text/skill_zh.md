# Qwen 文本聊天 (兼容 OpenAI)

通过兼容 OpenAI 的 API 使用 Qwen 模型生成文本、进行对话、编写代码和调用工具。
这项技能是 **qwencloud/qwencloud-ai** 的一部分。

## 技能目录

使用这项技能的内部文件来执行和学习。当默认路径失败或需要详细信息时，按需加载参考文件。

| 位置                          | 目的                                                                                   |
|-------------------------------|--------------------------------------------------------------------------------------|
| `scripts/text.py`             | 默认执行 — 聊天/补全请求、流式传输、输出保存                                             |
| `references/execution-guide.md` | 备用方案：curl、Python SDK、函数调用、思考模式                                           |
| `references/api-guide.md`     | API 补充和完整代码示例                                                               |
| `references/prompt-guide.md` | 提示工程：CO-STAR 框架、CoT、少样本、任务步骤                                             |
| `references/sources.md`       | 官方文档 URL（仅手动查找）                                                             |

## 安全

**绝对不要明文输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$QWENCLOUD_API_KEY`，Python 中的 `os.environ["QWENCLOUD_API_KEY"]`）。脚本接受 `QWENCLOUD_API_KEY`，然后是 `QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`。任何凭证检查或检测都必须是**非明文的**：仅报告状态（例如“已设置”/“未设置”，“有效”/“无效”），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的 内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，应帮助创建一个 `.env` 文件，其中包含占位符（`QWENCLOUD_API_KEY=sk-your-key-here`），并指示用户用他们从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 的实际密钥替换它。仅当用户明确要求时才写入实际密钥值。

## 密钥兼容性

脚本支持**标准 QwenCloud API 密钥**（`sk-...`）和**令牌计划密钥**（`sk-sp-...`）。令牌计划密钥会自动路由到令牌计划端点 — 查看令牌计划模型目录 [Token Plan model catalog](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md) 以获取支持的模型。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qwencloud-token-plan-models.md)。

**令牌计划：不要使用 curl；始终使用捆绑的 Python 脚本。**

编码计划密钥（也具有 `sk-sp-` 前缀，但通过编码计划订阅购买）仅用于交互式编码工具，在这些脚本上会失败。如果安装了 qwencloud-ops-auth，请查看其 `references/codingplan.md` 以了解密钥类型、端点映射和错误代码的详细信息。

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
| `token-plan` | 检测到令牌计划密钥（`sk-sp-` 前缀） |
| `payg` | 检测到标准 PAYG 密钥 |
| `not-set` | 环境中未找到 API 密钥 |

## 模型选择

> **🚫 关键 — 绝不覆盖用户指定的参数。** 如果用户在提示或请求 JSON 中明确指定了模型，您必须使用该模型。不要：
> - 用“更适合”或更新的模型替换它（例如，因为任务“看起来像推理”而将用户的 `qwen3.7-max` 替换为思考模型）
> - 添加用户未请求的参数（`enable_thinking`、`enable_search`、样式提示）
> - “优化”任何用户明确的选择
>
> 以下选择指导仅适用于**用户未指定模型**的情况。

在选择之前，建议或默认使用模型之前，请获取并阅读当前的 [QwenCloud 文本模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-text-models.md)。它包含最近的 Qwen 通用模型、基本模型信息、建议和默认模型。对于编码、翻译或第三方系列，请咨询 qwencloud-model-selector 或 QwenCloud CLI。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qwencloud-text-models.md)。

1. **用户指定了模型** → **强制：使用该模型** — 不要替换，不要“优化”，不要添加未请求的参数。
2. **当模型选择取决于需求、场景或定价时**，请咨询 qwencloud-model-selector 技能。
3. **无信号，任务清晰** → 使用模型目录中的默认值。

> **⚠️ 重要**：模型目录是一个**特定时间的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，始终检查[官方模型列表](https://www.qwencloud.com/models)以获取权威的、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至其详情页面：`https://www.qwencloud.com/models/<model-name>`（将 `<model-name>` 替换为确切的模型 ID，例如 `qwen3.6-plus` → https://www.qwencloud.com/models/qwen3.6-plus）。绝不要修改或猜测 URL 中的模型名称。

> **动态模型查询**：如果 **qwencloud-model-selector** 技能或 **QwenCloud CLI** (`qwencloud models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证 — 请参阅 **qwencloud-usage** 技能了解登录流程。

## 执行

### 前置条件

- **API 密钥**：使用**非明文**检查仅检查 `QWENCLOUD_API_KEY`、`QWEN_API_KEY`，然后是 `DASHSCOPE_API_KEY`（例如，在 shell 中：`[ -n "$QWENCLOUD_API_KEY" ]`；仅报告“已设置”或“未设置”，绝不能报告密钥值）。如果未设置：如果可用，运行 *qwencloud-ops-auth* 技能；否则，指导用户从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取密钥，并通过 `.env` 文件设置（在项目根目录或当前目录中运行 `echo 'QWENCLOUD_API_KEY=sk-your-key-here' >> .env`）或环境变量。脚本在当前工作目录和项目根目录中搜索 `.env`。技能可以独立安装 — 不要假设 qwencloud-ops-auth 存在。
  **注意**：脚本自动从当前目录和项目根目录加载 `.env`（除了任何导出的环境变量）。显示 `$QWENCLOUD_API_KEY` 为“未设置”的 shell 检查**并不意味着脚本会失败** — 它可能仍在 `.env` 中找到密钥。将 shell 检查视为仅供参考；权威测试是简单地运行脚本（如果任何地方未找到密钥，它会以清晰的错误退出）。
- Python 3.9+（仅使用标准库，脚本执行**不需要 pip 安装**）

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果找不到 `python3`，请尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，
PAYG 可能使用**路径 2（curl）**；令牌计划必须安装 Python 3.9+。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用脚本的完整绝对路径来执行脚本。** 不要假设脚本位于当前工作目录。不要在执行之前使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本 — 等待 stdout；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/text.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/text.py \
  --request '{"messages":[{"role":"user","content":"Hello!"}],"model":"qwen3.7-plus"}' \
  --output output/qwencloud-text/ --print-response
```

对于流式传输（推荐用于交互式使用）：

```bash
python3 <this-skill-dir>/scripts/text.py \
  --request '{"messages":[{"role":"user","content":"Write a poem about the sea"}],"model":"qwen3.7-plus"}' \
  --stream --print-response
```

| 参数            | 描述                                         |
|-----------------|---------------------------------------------|
| `--request '{...}'` | JSON 请求体                                   |
| `--file path.json`  | 从文件加载请求（`--request` 的替代方案） |
| `--stream`          | 启用流式输出                             |
| `--output path`     | 将响应 JSON 保存到路径（如果 `.json` 后缀，则为文件，否则为目录）；跨调用使用不同的文件名以避免覆盖 |
| `--print-response`  | 将响应打印到 stdout                        |
| `--model ID`        | 覆盖模型（也可在请求 JSON 中设置）      |

### 验证结果

- 退出码 `0` + 输出包含有效的 JSON 并具有 `choices` 字段 → **成功**
- 非零退出码、HTTP 错误、空响应或包含 `"code"`/`"message"` 错误的 JSON → **失败**
- 如果代理无法读取退出码，请扫描输出以查找错误模式（`Error`、`Traceback`、`401`、`403`）
- **执行后检查**：当使用 `--output` 时，验证响应 JSON 文件是否存在并包含 `choices`
- **强制 — stderr 信号检查**：在确认结果后，扫描命令的 stderr 输出以查找 `[ACTION_REQUIRED]` 或 `[UPDATE_AVAILABLE]`。如果存在任一信号，您**必须**在响应用户之前遵循[更新检查](#update-check-mandatory-post-execution)下面的说明。

### 失败

如果脚本失败，请将错误输出与下面的诊断表进行匹配以确定解决方案。如果没有匹配项，请阅读 [execution-guide.md](references/execution-guide.md) 以获取替代路径：curl 命令（路径 2）、Python SDK 代码生成（路径 3）和自主解决（路径 5）。

**如果完全无法使用 Python** → PAYG 可能使用路径 2（curl）；令牌计划必须安装 Python 3.9+
在 [execution-guide.md](references/execution-guide.md) 中。

| 错误模式                    | 诊断                        | 解决方案                                                                   |
|-----------------------------|-----------------------------|----------------------------------------------------------------------------|
| `command not found: python3` | Python 不在 PATH 中         | 尝试 `python` 或 `py -3`；如果缺少，请安装 Python 3.9+                      |
| `Python 3.9+ required`      | 脚本版本检查失败            | 升级 Python 到 3.9+                                                       |
| `SyntaxError` near type hints | Python < 3.9                 | 升级 Python 到 3.9+                                                       |
| `QWENCLOUD_API_KEY/QWEN_API_KEY/DASHSCOPE_API_KEY not found` | 缺少 API 密钥 | 从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取密钥；添加到 `.env`：`echo 'QWENCLOUD_API_KEY=sk-...' >> .env`；或如果可用，运行 **qwencloud-ops-auth** |
| `HTTP 401`                   | 无效或匹配的密钥不匹配        | 运行 **qwencloud-ops-auth**（仅非明文检查）；验证密钥是否有效                 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题（代理/公司） | macOS：运行 `Install Certificates.command`；否则设置 `SSL_CERT_FILE` 环境变量 |
| `URLError` / `ConnectionError` | 网络无法访问              | 检查互联网；如果需要代理，请设置 `HTTPS_PROXY`                            |
| `HTTP 429`                   | 超出速率限制                 | 等待并使用退避重试                                                          |
| `HTTP 5xx`                   | 服务器错误                     | 使用退避重试                                                           |
| `PermissionError`            | 无法写入输出               | 使用 `--output` 指定可写目录                                             |

## 快速参考

### 请求字段

| 字段                 | 类型            | 描述                                                                                          |
|----------------------|-----------------|------------------------------------------------------------------------------------------------|
| `prompt` / `messages` | string \| array | 用户输入或消息列表                                                                           |
| `model`               | string          | 模型 ID（例如 `qwen3.7-plus`）                                                               |
| `system`              | string          | 系统提示（可选）                                                                             |
| `temperature`         | float           | 0–2，控制随机性                                                                             |
| `max_tokens`          | int             | 最大输出令牌                                                                                    |
| `tools`               | array           | 用于工具调用的函数定义                                                                    |
| `stream`              | bool            | 启用流式传输（推荐用于交互式使用）                                                           |
| `enable_thinking`     | bool            | 覆盖思考模式。模型默认值各不相同；请查看上面的模型目录。除非用户明确要求更改默认值，否则不要设置此字段。 |

### 响应字段

| 字段        | 描述                                    |
|-------------|-----------------------------------------|
| `text`      | 生成的文本内容                         |
| `model`     | 使用的模型                             |
| `usage`     | 令牌使用情况（prompt_tokens、completion_tokens） |
| `tool_calls` | 如果使用工具，则函数调用请求             |

## 高级功能

这些是通过请求参数支持的 API 级功能。所有功能都使用相同的 `chat/completions` 端点。

| 功能               | 如何启用                                                    | 备注                                          |
|-------------------|------------------------------------------------------------------|------------------------------------------------|
| **结构化输出**     | `response_format: {"type": "json_schema", "json_schema": {...}}` | 强制 JSON 输出符合模式         |
| **网络搜索**        | `enable_search: true`                                            | 实时网络搜索增强响应       |
| **深度思考**     | `enable_thinking: true`                                          | 扩展推理；仅当用户请求时 |
| **函数调用**      | `tools: [...]`                                                   | 定义用于工具的函数                  |
| **上下文缓存**     | 自动针对重复的前缀；或显式基于会话       | 减少重复上下文的成本              |
| **部分模式**      | `partial_mode: "prefix"`                                         | 继续完成前缀                     |
| **批量推理**      | 异步批量 API，使用 JSONL 输入                                 | 50% 成本折扣                              |

有关每个功能的详细用法，请参阅 [api-guide.md](references/api-guide.md) 和 [sources.md](references/sources.md)。

## 错误处理

| 错误                   | 原因                               | 操作                                                                                     |
|------------------------|-------------------------------------|--------------------------------------------------------------------------------------------|
| `401 Unauthorized`      | 无效或缺少 API 密钥              | 运行 **qwencloud-ops-auth** 如果可用；否则提示用户设置密钥（仅非明文检查） |
| `429 Too Many Requests` | 速率限制超出                 | 使用退避重试                                                                         |
| `500` / `502` / `503`   | 服务器错误                        | 重试；检查状态页面                                                                   |
| `Invalid model`         | 模型 ID 未找到                  | 将 ID 与上面的模型目录进行验证                                               |
| `Invalid parameter`     | 请求体错误                    | 验证 JSON 和字段类型                                                              |
| `TypeError: ...proxies` | openai SDK 与 httpx 不兼容     | `pip install --upgrade openai` (>=1.55.0)；或使用脚本（纯标准库）                     |

> **使用和计费**：使用 **qwencloud-usage** 技能直接检查使用情况、免费套餐配额和计费。或者，用户可以访问 QwenCloud 控制台：
> [使用分析](https://home.qwencloud.com/analytics) |
> [按量计费](https://home.qwencloud.com/billing/pay-as-you-go) |
> [编码计划计费](https://home.qwencloud.com/billing/coding-plan)
>
> **绝对不要编造、猜测或构造使用/计费/控制台 URL。** 仅提供此技能中列出的确切链接。如果此 URL 未在此处列出，请不要编造一个。

## 输出位置

优先使用**当前工作目录**进行所有输出。当使用 `--output` 时，默认子目录：
`./output/qwencloud-text/`。

**写入禁止**：绝对不要将输出文件写入此技能的安装目录或任何 `skills/` 层级。所有生成的内容必须位于当前工作目录下的 `output/` 或用户指定的路径。

## 令牌计划支持

令牌计划密钥（`sk-sp-...`）完全支持。当检测到令牌计划密钥时，脚本会自动路由到令牌计划端点（`token-plan.ap-southeast-1.maas.aliyuncs.com`）。

### 支持的模型

获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)，然后使用列出的文本模型。如果 CDN 访问失败，请使用 [本地备用方案](cdn/references/qwencloud-token-plan-models.md)。

### 行为

- **令牌计划密钥 + 支持的模型** → 自动路由到令牌计划端点，正常运行
- **令牌计划密钥 + 不支持的模型** → 请求可能在 TP 端点失败；参考上面的目录，然后建议切换到支持的模型或使用 PAYG 密钥
- **编码计划密钥** → 脚本不是编码代理；调用将失败。使用标准的 PAYG 密钥或令牌计划密钥代替。

### 必要的标题

`User-Agent: qwencloud-skills` 会自动包含在所有请求中。

## 更新检查（执行后强制）

脚本执行后，检查 stderr 以获取操作信号。脚本自动检测更新状态并发出结构化信号。您必须采取行动。本节也适用于用户明确要求检查更新时。

### 信号：`[ACTION_REQUIRED] qwencloud-update-check 技能未安装`

当 stderr 包含此信号时，您必须向用户展示以下选项，并**等待他们的响应后再继续**。不要无声地跳过。

> 更新检查技能未安装。它让您了解 qwencloud/qwencloud-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何事
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：

- 用户选择 **1** → 运行：
  `npx skills add QwenCloud/qwencloud-ai --skill qwencloud-update-check -y`，然后运行：
  `python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行： `python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行： `python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

### 信号：`[UPDATE_AVAILABLE]`

当 stderr 包含此信号时，您必须将简短的更新通知附加到您的响应中，包括版本信息和 stderr 输出中显示的更新命令。

### stderr 中没有信号

如果 stderr 既不包含 `[ACTION_REQUIRED]` 也不包含 `[UPDATE_AVAILABLE]`，则无需采取任何操作 — 技能已安装并是最新的（或在 24 小时内缓存）。

### 明确的用户请求

当用户明确要求检查更新（例如“检查更新”、“检查版本”）时：

1. 在兄弟技能目录中查找 `qwencloud-update-check/SKILL.md`。
2. 如果找到 — 运行： `python3 <qwencloud-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。
3. 如果未找到 — 显示上面的安装选项。

## 参考

- [execution-guide.md](references/execution-guide.md) — 备用路径（curl、SDK、自主），函数调用，
  思考模式
- [api-guide.md](references/api-guide.md) — API 补充指南，包含完整代码示例
- [sources.md](references/sources.md) — 官方文档 URL
