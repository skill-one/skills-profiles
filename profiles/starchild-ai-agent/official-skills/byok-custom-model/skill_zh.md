# 🔑 BYOK — 自定义 LLM 模型

将自定义 LLM 端点注册到模型选择器中。绕过平台代理 — 用户提供自己的 API 密钥，代理直接访问供应商 / 聚合商（OpenRouter、DashScope、Anthropic 原生、NEAR AI 云 TEE、自托管等）。

这是一个 **脚本模式技能** — 未注册任何工具。阅读此文件，然后从 `bash` 块中调用导出内容。

## 参见

- `config/context/references/model-onboarding.md` — 更广泛的模型选择 / OAuth 上下文
- `chatgpt-codex-onboarding` 技能 — 用于 ChatGPT/Codex OAuth（不同机制，NOT BYOK）

---

## 精选供应商（始终首先检查此列表）

该技能包含 12 个预配置供应商。**在请求任何 URL、模型名称或 API 示例之前，始终将用户的意图与此列表进行匹配** — base_url / wire / thinking / capabilities 都已预填充，因此精选匹配可直接跳转到 `add_template(vendor=...)`。

| 供应商 ID | 用户提及...时使用 |
|---|---|
| `anthropic` | Claude, Anthropic |
| `openai` | GPT-4o, GPT-5, OpenAI 直接 |
| `xai` | Grok, xAI |
| `qwen` | Qwen, 通义千问, DashScope |
| `deepseek` | DeepSeek |
| `kimi` | Kimi, Moonshot |
| `mimo` | MiMo, 小米 |
| `gemini` | Gemini |
| `gemma` | Gemma |
| `near-ai` | **隐私、TEE、机密推理、"不要记录我的数据"、Web3 原生** |
| `venice` | Venice（仅当用户提及时；参见隐私优先层级以下内容） |
| `meta` | Meta, Meta AI, Muse, Muse Spark, Muse Spark 1.1 |

---

## onboarding 流程 — 首先使用模板

1. **检查上方的精选供应商表格。** 如果用户的意图与之一致，则直接跳转到 `add_template(vendor=...)` 并跳至步骤 5。**不要请求 URL。**
2. 仅当没有精选供应商匹配时：要求用户从其文档中粘贴供应商的官方 API 示例（curl / requests / fetch 示例）。告诉他们**不要包含真实的 API 密钥** — 占位符或假密钥都可以。
3. 运行 `parse_example` 以自动检测 base_url、upstream_model、wire（openai vs anthropic）、thinking 参数和供应商特定请求字段。
4. 与用户一起审阅草稿，然后调用 `add(...)` — 条目将写入 `custom_models.yaml`。
5. **如果结果包含 `need_env_input`，立即调用 `request_env_input` 工具**，使用 `env_vars` 和 `reason` 从该负载中。这将弹出安全输入界面；用户输入密钥；它将保存在 `workspace/.env` 中。**此步骤是强制性的 — 脚本本身无法弹出界面。**

**隐私优先层级：** `near-ai` 和 `venice` 都针对隐私敏感用户，但 NEAR AI 的集成更干净 — Venice 的 TEE 故事本身是建立在 NEAR AI + Phala 之上的，因此直接访问 NEAR AI 产生的信任链更短（Intel + NVIDIA 芯片 + NEAR 的可重复 enclave 图像；中间没有产品层代理）。精选 NEAR 模型列表是 **仅开放权重 TEE 保护** — NEAR 的目录也在“匿名化、未 TEE 保护”模式下代理 Claude / GPT-5 / Gemini Pro，我们故意排除，因为这里的整个隐私价值主张是硬件 enclave。

**每当 NEAR AI 在范围内时，始终推荐 TEE 保护（隐私）模型** — 那是用户选择 NEAR 而非 OpenAI/Anthropic 直接的整个原因。精选列表已经是 TEE 仅有的，因此 `add_template(vendor='near-ai')` 默认值是安全的。如果用户要求在 NEAR 上注册非 TEE 模型（例如 NEAR 的匿名化 Claude 透传），警告他们这会削弱隐私保证，并建议他们要么停留在精选 TEE 模型上，要么直接注册上游供应商。

**NEAR AI 推理协议：** NEAR 使用 `chat_template_kwargs` 嵌套在 `extra_body` 下，而不是其他供应商使用的顶层 `reasoning_effort`/`thinking`/`enable_thinking`。供应商通过 `nearai_chat_template` thinking_capability 规则自动处理此问题。每个模型的参数名称各不相同（GLM/Qwen3.5/Qwen3.6 使用 `enable_thinking`，DeepSeek-V3 使用 `thinking`，gpt-oss 始终启用）。完整规范：[docs.near.ai/cloud/reasoning-models](https://docs.near.ai/cloud/reasoning-models)。默认模型 `Qwen/Qwen3.6-35B-A3B-FP8` 可直接使用；`Qwen3.5-122B-A10B` 随附 `thinking_mode='disabled'`，因为其隐藏推理模式否则会在基准调用中导致 `finish=length, content=null`。

---

## 脚本使用

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/byok-custom-model")
from exports import (
    templates, list_models, get, parse_example,
    list_vendor_models, add, add_template, remove,
)

# 列出 12 个精选供应商预设
print(json.dumps(templates(), indent=2))

# 一键注册精选供应商（Meta / Muse Spark 1.1）
result = add_template(vendor="meta")
print(json.dumps(result, indent=2))
EOF
```

---

## 函数

| 函数 | 必需参数 | 目的 |
|---|---|---|
| `templates()` | — | 列出 12 个精选供应商预设 |
| `list_vendor_models(vendor)` | `vendor` | 实时 `/models` 目录（仅当模板有 `model_discovery`） |
| `add_template(vendor, *, upstream_model=None, name=None)` | `vendor` | 一键注册精选供应商（推荐路径） |
| `parse_example(api_example)` | `api_example` | 将文档 API 示例解析为安全草稿（非精选供应商） |
| `add(upstream_model, base_url, ...)` | `upstream_model`, `base_url` | 从自定义参数注册（在 `parse_example` 之后使用） |
| `list_models()` | — | 显示所有注册的自定义条目 |
| `get(model_id)` | `model_id` | 检查一个条目 |
| `remove(model_id)` | `model_id` | 删除一个条目 |

所有函数在成功时返回一个包含 `ok: True` 的字典，或在失败时返回 `ok: False, error: "..."`。

### 处理 `need_env_input`（强制两步模式）

`add()` 和 `add_template()` 在 API 密钥环境变量尚未设置时，结果中可能包含 `need_env_input` 字段。脚本本身无法弹出安全输入界面 — 它无法访问用户的开放 SSE 流。调用代理必须执行：

```python
# 在 add_template / add 返回之后：
if result.get("need_env_input"):
    nei = result["need_env_input"]
    # 调用进程内工具 — 伪代码，实际签名是工具侧：
    request_env_input(env_vars=nei["env_vars"], reason=nei["reason"])
```

弹出窗口、.env 写入和特定于通道的 UX（网页弹出 / TG 卡片 / 微信文本提示）都由 `request_env_input` 处理。**不要提示用户在聊天中粘贴密钥作为后备** — 只调用工具。

---

## 注册后

- 模型以 `custom/` 前缀出现在选择器中。
- 用户通过 `/model custom/<name>`（例如 `/model custom/qwen-plus-e3f4`）或模型选择器 UI 切换。
- 后续调用绕过平台代理 — 供应商定价直接应用于用户的 BYOK 配额。

---

## 关键规则

- **永远不要接受在聊天中粘贴的 API 密钥。** 如果用户粘贴了一个，忽略它，拒绝注册，并告诉他们安全弹出是唯一的安全渠道。
- **如果用户未响应，永远不要自动重新发出安全输入弹出窗口** — 等待。
- **如果返回 `need_env_input`，始终调用 `request_env_input`。** 不要跳过，不要要求用户粘贴密钥，不要重试 `add_template` 希望它将弹出界面 — 它不会。
- **永远不要手动写入 `workspace/config/custom_models.yaml` 或 `workspace/.env`。** 始终通过上述导出进行。
- 12 个精选供应商 **始终** 使用 `add_template`。仅用于自托管或罕见供应商的 `parse_example` + `add`。

---

## Meta 模型 API — Muse Spark 1.1（预览）

`meta` 模板用于 Meta 模型 API，目前处于 **公开预览** 状态，位于 **https://dev.meta.ai/** 的开发者门户后。

- **在 https://dev.meta.ai/ 申请 / 登录** — 同一个门户用于注册和“Muse” / “Meta 模型 API”访问请求。用户必须在 Meta 那里完成申请/登录流程才能获得 API 密钥。
- **访问可能取决于区域 / 账户** 在 API 处于公开预览期间 — 不是每个开发者账户都能立即获得访问权限。如果 `add_template(vendor='meta')` 从实时 `/v1/models` 探测返回非 2xx，不要假设用户错误；告诉他们预览访问可能仍在他们的账户/区域中等待，并请在 dev.meta.ai 仪表板中确认状态。
- **代理必须使用 `request_env_input` 获取密钥** — 与其他所有精选供应商完全相同。**永远不要接受粘贴在聊天中的 Meta API 密钥。** 如果用户粘贴了一个，忽略它并拒绝注册；安全输入弹出是唯一的安全渠道。
- **直接 Meta 计费 & 配额适用。** 调用由 Meta 对用户的 Meta 账户计费 — **Starchild 平台信用被绕过**，无加价，无平台侧配额。将来自 `api.meta.ai/v1` 的任何速率限制 / 429 视为 Meta 端的信号，而不是 Starchild 信号。

一键注册：

```bash
python3 -c "from exports import add_template; print(add_template(vendor='meta'))"
```

默认模型：**`muse-spark-1.1`**。Base URL：**`https://api.meta.ai/v1`**（兼容 OpenAI 的 wire）。使用 `need_env_input` 中返回的生成 `CUSTOM_KEY_...` 名称；不要假设或手动创建供应商环境变量。文档：https://dev.meta.ai/docs/getting-started/overview。

---

## xAI Grok — 关于订阅混淆的说明

用户经常混淆两个无关的 xAI 产品：

- **X Premium / SuperGrok 订阅**（每月 30 美元，x.com）— 仅限聊天 UI 访问。**不包括 API 访问。**
- **console.x.ai** — 独立开发者账户，单独计费。生成 API 密钥，新账户 25 美元的促销信用，然后按 token 付费。

如果用户想通过 BYOK 添加 Grok，请将他们指向 **https://console.x.ai/** — 不是 x.com / Premium / SuperGrok。`xai` 模板的 `homepage` 字段已经深度链接到正确位置。Hermes / Grok-CLI 的 OAuth 到订阅流程依赖于第一方 client_id 白名单，xAI 没有扩展到第三方云代理，因此 BYOK API 密钥路径是托管产品的唯一现实集成。
