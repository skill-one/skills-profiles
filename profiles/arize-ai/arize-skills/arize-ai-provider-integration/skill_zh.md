# Arize AI 集成技能

> **`SPACE`** — `--space` 标志接受一个 **空间名称**（例如，`my-workspace`）或一个 base64 编码的 **空间 ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的。
> **注意：** `ai-integrations create` 不接受 `--space` — AI 集成是按账户范围设置的。仅在与 `list`、`get`、`update` 和 `delete` 一起使用 `--space`。

## 概念

- **AI 集成** = 在 Arize 中注册的存储的 LLM 提供商凭证；由评估器调用判断模型，并由其他需要代表您调用 LLM 的 Arize 功能使用
- **提供商** = 支持集成的 LLM 服务（例如，`OPEN_AI`、`ANTHROPIC`、`AWS_BEDROCK`）
- **集成 ID** = 集成的 base64 编码的全局标识符（例如，`TGxtSW50ZWdyYXRpb246MTI6YUJjRA==`）；创建评估器和其他下游操作时需要
- **作用域** = 控制哪些空间或用户可以使用集成的可见性规则
- **认证类型** = Arize 如何使用提供商进行认证：`DEFAULT`（提供商 API 密钥）、`PROXY_WITH_HEADERS`（通过自定义头进行代理）或 `BEARER_TOKEN`（bearer 令牌认证）

## 前置条件

直接执行任务 — 运行您需要的 `ax` 命令。**不要**事先检查版本、环境变量或配置文件。

如果 `ax` 命令失败，根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 检查当前配置文件。如果配置文件丢失或 API 密钥不正确，请按照 [references/ax-profiles.md](references/ax-profiles.md) 创建/更新它。如果用户没有他们的密钥，请指示他们访问 https://app.arize.com/admin > API 密钥
- 空间未知 → 运行 `ax spaces list` 通过名称选择，或询问用户
- LLM 提供商调用失败（缺少提供商凭证）→ 运行 `ax ai-integrations list --space SPACE` 检查平台管理的凭证。如果不存在：
  - **首选：** 给用户从下方支持的提供商中获取确切的 `ax ai-integrations create` 命令（参考环境变量名称，如 `$OPENAI_API_KEY`，切勿使用原始值）。指示他们在**自己的终端**中导出提供商密钥并运行该命令 — **切勿**将密钥粘贴到聊天中。除非此终端会话中已经导出了变量，否则**不要**自己运行创建命令。
  - **Bedrock/Vertex：** 使用 `--provider-metadata` 而不是 `--api-key`（见下方支持的提供商）。
- **安全：** 不要读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 用于 Arize 凭证，使用 `ax ai-integrations` 用于 LLM 提供商密钥。**不要**要求用户将秘密粘贴到聊天中。对于缺少的凭证，请参阅 [references/ax-profiles.md](references/ax-profiles.md)。

---

## 列出 AI 集成

列出空间中可访问的所有集成：

```bash
ax ai-integrations list --space SPACE
```

按名称过滤（不区分大小写的子字符串匹配）：

```bash
ax ai-integrations list --space SPACE --name "openai"
```

分页大型结果集：

```bash
# 获取第一页
ax ai-integrations list --space SPACE --limit 20 -o json

# 使用前一个响应中的游标获取下一页
ax ai-integrations list --space SPACE --limit 20 --cursor CURSOR_TOKEN -o json
```

**关键标志：**

| 标志 | 描述 |
|------|-------------|
| `--space` | 过滤集成的空间名称或 ID |
| `--name` | 集成名称的不区分大小写的子字符串过滤器 |
| `--limit` | 最大结果（1–100，默认 15） |
| `--cursor` | 来自前一个响应的分页标记 |
| `-o, --output` | 输出格式：`table`（默认）或 `json` |

**响应字段：**

| 字段 | 描述 |
|-------|-------------|
| `id` | base64 集成 ID — 复制此 ID 用于下游命令 |
| `name` | 人类可读的名称 |
| `provider` | LLM 提供商枚举（见下方支持的提供商） |
| `has_api_key` | 如果存储凭证则为 `true` |
| `model_names` | 允许的模型列表，或如果所有模型都启用则为 `null` |
| `enable_default_models` | 是否允许此提供商的默认模型 |
| `function_calling_enabled` | 是否启用工具/函数调用 |
| `auth_type` | 认证方法：`DEFAULT`、`PROXY_WITH_HEADERS` 或 `BEARER_TOKEN` |

---

## 获取特定集成

```bash
ax ai-integrations get NAME_OR_ID
ax ai-integrations get NAME_OR_ID -o json
ax ai-integrations get NAME_OR_ID --space SPACE   # 使用名称时需要
```

用于检查集成完整配置或在创建后确认其 ID。

---

## 创建 AI 集成

创建之前，始终先列出集成 — 用户可能已经有一个合适的：

```bash
ax ai-integrations list --space SPACE
```

如果不存在合适的集成，则创建一个。所需的标志取决于提供商。

### OpenAI

```bash
ax ai-integrations create \
  --name "My OpenAI Integration" \
  --provider OPEN_AI \
  --api-key $OPENAI_API_KEY
```

### Anthropic

```bash
ax ai-integrations create \
  --name "My Anthropic Integration" \
  --provider ANTHROPIC \
  --api-key $ANTHROPIC_API_KEY
```

### Azure OpenAI

```bash
ax ai-integrations create \
  --name "My Azure OpenAI Integration" \
  --provider AZURE_OPEN_AI \
  --api-key $AZURE_OPENAI_API_KEY \
  --base-url "https://my-resource.openai.azure.com/"
```

### AWS Bedrock

AWS Bedrock 使用基于 IAM 角色的认证。通过 `--provider-metadata` 提供 Arize 应用的角色 ARN：

```bash
ax ai-integrations create \
  --name "My Bedrock Integration" \
  --provider AWS_BEDROCK \
  --provider-metadata '{"role_arn": "arn:aws:iam::123456789012:role/ArizeBedrockRole"}'
```

### Vertex AI

Vertex AI 使用 GCP 服务账户凭证。通过 `--provider-metadata` 提供 GCP 项目和区域：

```bash
ax ai-integrations create \
  --name "My Vertex AI Integration" \
  --provider VERTEX_AI \
  --provider-metadata '{"project_id": "my-gcp-project", "location": "us-central1", "project_access_label": "my-access-label"}'
```

### Gemini

```bash
ax ai-integrations create \
  --name "My Gemini Integration" \
  --provider GEMINI \
  --api-key $GEMINI_API_KEY
```

### NVIDIA NIM

```bash
ax ai-integrations create \
  --name "My NVIDIA NIM Integration" \
  --provider NVIDIA_NIM \
  --api-key $NVIDIA_API_KEY \
  --base-url "https://integrate.api.nvidia.com/v1"
```

### Custom (OpenAI 兼容端点)

```bash
ax ai-integrations create \
  --name "My Custom Integration" \
  --provider CUSTOM \
  --base-url "https://my-llm-proxy.example.com/v1" \
  --api-key $CUSTOM_LLM_API_KEY
```

### LiteLLM

```bash
ax ai-integrations create \
  --name "My LiteLLM Integration" \
  --provider LITELLM \
  --base-url "https://my-litellm-proxy.example.com" \
  --api-key $LITELLM_API_KEY
```

### 支持的提供商

| 提供商 | 需要的额外标志 |
|----------|---------------------|
| `OPEN_AI` | `--api-key <key>` |
| `ANTHROPIC` | `--api-key <key>` |
| `AZURE_OPEN_AI` | `--api-key <key>`, `--base-url <azure-endpoint>` |
| `AWS_BEDROCK` | `--provider-metadata '{"role_arn": "<arn>"}'` |
| `VERTEX_AI` | `--provider-metadata '{"project_id": "<gcp-project>", "location": "<region>", "project_access_label": "<label>"}'` |
| `GEMINI` | `--api-key <key>` |
| `NVIDIA_NIM` | `--api-key <key>`, `--base-url <nim-endpoint>` |
| `CUSTOM` | `--base-url <endpoint>` |
| `LITELLM` | `--base-url <endpoint>` |

### 任何提供商的可选标志

| 标志 | 描述 |
|------|-------------|
| `--model-name` | 允许的模型名称（重复多个，例如 `--model-name gpt-4o --model-name gpt-4o-mini`）；省略以允许所有模型 |
| `--enable-default-models` | 启用提供商的默认模型列表 |
| `--function-calling-enabled` | 启用工具/函数调用支持 |
| `--auth-type` | 认证类型：`DEFAULT`、`PROXY_WITH_HEADERS`、`BEARER_TOKEN` 或 `OAUTH2_CLIENT_CREDENTIALS` |
| `--headers` | 自定义头作为 JSON 对象或文件路径（用于代理认证） |
| `--provider-metadata` | 提供商特定元数据作为 JSON 对象或文件路径 |

### 创建后

捕获返回的集成 ID（例如，`TGxtSW50ZWdyYXRpb246MTI6YUJjRA==`）— 它在创建评估器和其他下游命令时需要。如果您错过了它，请检索它：

```bash
ax ai-integrations list --space SPACE -o json
# 或直接通过名称/ID：
ax ai-integrations get NAME_OR_ID
```

---

## 更新 AI 集成

`update` 是部分更新 — 仅更改您提供的标志。省略的字段保持不变。

```bash
# 重命名
ax ai-integrations update NAME_OR_ID --name "New Name"

# 旋转 API 密钥
ax ai-integrations update NAME_OR_ID --api-key $OPENAI_API_KEY

# 更改模型列表（替换所有现有模型名称）
ax ai-integrations update NAME_OR_ID --model-name gpt-4o --model-name gpt-4o-mini

# 更新基础 URL（对于 Azure、自定义或 NIM）
ax ai-integrations update NAME_OR_ID --base-url "https://new-endpoint.example.com/v1"

# 限制特定空间的可见性（完整替换 — 列出所有应具有访问权限的空间）
ax ai-integrations update NAME_OR_ID \
  --scopings '[{"space_id": "SPACE_GLOBAL_ID", "scoping_type": "include"}]'
```

使用名称时需要添加 `--space SPACE`。`create` 接受的任何标志都可以传递给 `update`。

**`--scopings` 标志：** 控制哪些空间可以使用此集成。接受 JSON 数组形式的范围规则。更新时替换所有现有作用域。使用 `ax spaces list -o json` 查找空间全局 ID。

---

## 删除 AI 集成

**警告：** 删除是永久性的。引用此集成的评估器将无法运行。

```bash
ax ai-integrations delete NAME_OR_ID --force
ax ai-integrations delete NAME_OR_ID --space SPACE --force   # 使用名称时需要
```

省略 `--force` 以获取确认提示而不是立即删除。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `ax: command not found` | 查看 [references/ax-setup.md](references/ax-setup.md) |
| `401 Unauthorized` | API 密钥可能没有对此空间的访问权限。在 https://app.arize.com/admin > API 密钥中验证密钥和空间 ID |
| `No profile found` | 运行 `ax profiles show --expand`；设置 `ARIZE_API_KEY` 环境变量或编写 `~/.arize/config.toml` |
| `Integration not found` | 使用 `ax ai-integrations list --space SPACE` 验证 |
| `has_api_key: false` 创建后 | 凭证未保存 — 重新运行 `update` 并提供正确的 `--api-key` 或 `--provider-metadata` |
| 评估器运行时出现 LLM 错误 | 使用 `ax ai-integrations get INT_ID` 检查集成凭证；如有必要，旋转 API 密钥 |
| `provider` 不匹配 | 创建后无法更改提供商 — 删除并使用正确的提供商重新创建 |

---

## 相关技能

- **arize-evaluator**：创建使用 AI 集成的 LLM 作为判断者的评估器 → 使用 `arize-evaluator`
- **arize-experiment**：运行使用由 AI 集成支持的评估器的实验 → 使用 `arize-experiment`

---

## 保存凭证以供将来使用

参见 [references/ax-profiles.md](references/ax-profiles.md) § 保存凭证以供将来使用。
