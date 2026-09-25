# 🔐 ChatGPT / Codex OAuth 引导

使用用户现有的 **ChatGPT 或 Codex 订阅**，无需 API 密钥即可访问 `gpt-5-codex`、`gpt-5`、`gpt-5-mini`。

这是一个 **脚本模式技能** — 未注册任何工具。阅读此文件，然后从 `bash` 块中调用导出内容。

## 参见

- `byok-custom-model` 技能 — 用于供应商密钥 BYOK 设置（不同机制，非 OAuth）
- `config/context/references/model-onboarding.md` — 整体模型选择格局

---

## 何时使用此技能

✅ **使用** 当用户明确说出以下之一时：
- "使用我的 ChatGPT 账户登录"
- "使用我的 Codex 订阅"
- "连接我的 ChatGPT Plus / Pro / Team / 企业版"
- "使用 OpenAI / ChatGPT 登录"

❌ **不要使用** 用于：
- BYOK / 基于API密钥的设置 ("添加 OpenAI API 密钥", "我有 OpenAI 密钥")
- 听起来相似的供应商（Anthropic、Gemini、Qwen 等）→ 使用 `byok-custom-model`
- 无订阅上下文的情况下 "添加 OpenAI 模型" — 先询问用户是否希望 OAuth（订阅）或 BYOK（API 密钥）

⚠️ 听起来相似的供应商名称（Codex、OpenAI、GPT）**不是**自行启动 OAuth 的信号。只有用户明确提到 "订阅 / 登录 / 使用 ChatGPT" 才符合条件。

---

## 引导流程

1. **status** — 检查是否已存在凭证（继续使用 vs 重新开始）。
2. **start** — 从 OpenAI 获取验证 URL + 用户代码；持久化到磁盘。
3. 告知用户：在浏览器中打开 URL，登录他们的 ChatGPT / Codex 账户，并输入代码。**不要自动轮询**。
4. 等待用户确认他们已批准设备。
5. **poll** — 完成OAuth握手；成功后，新模型即可使用。

如果轮询返回 `status='pending'`，用户尚未完成 — 等待他们，然后再次轮询。不要自动轮询。

---

## 脚本使用

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/chatgpt-codex-onboarding")
from exports import status, start, poll, logout, refresh, models, usage

# 检查当前状态
print(json.dumps(status(), indent=2))

# 开始流程
result = start()
print(f"打开: {result['verification_url']}\n代码: {result['user_code']}")
EOF
```

用户批准后：

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/chatgpt-codex-onboarding")
from exports import poll
print(json.dumps(poll(), indent=2))
EOF
```

---

## 函数

| 函数 | 必需参数 | 目的 |
|---|---|---|
| `status()` | — | 检查当前 OAuth 状态、过期时间、模型列表 |
| `start()` | — | 开始设备码流程 → `verification_url` + `user_code` |
| `poll(pending_id=None)` | — | 检查授权（用户确认批准后调用） |
| `logout()` | — | 断开连接 + 移除凭证 |
| `refresh()` | — | 强制刷新访问令牌（调试；通常自动） |
| `models(force=False)` | — | 列出 OAuth 端点提供的可用模型 |
| `usage(force=False)` | — | 订阅使用统计 |

`models` / `usage` 上的 `force=True` 跳过缓存 TTL。

所有函数成功时返回包含 `ok: True` 的字典，失败时返回 `ok: False, error: "..."`。

---

## 连接后

当 `poll()` 返回 `status='connected'` 时，**你必须首先告知用户**：

> "连接成功。请刷新您的浏览器页面 — 一旦重新加载，新的 `openai-codex/*` 模型将出现在模型选择器中。"

Web 前端在客户端缓存模型列表，OAuth 连接完成后不会自动刷新。没有手动刷新，用户将看不到新可用的模型，并会认为连接失败。始终在回复中包含此说明 — 不要假设选择器会自动更新。

模型带有 `openai-codex/` 前缀：
- `openai-codex/gpt-5-codex` — 主要
- `openai-codex/gpt-5` — 完整 GPT-5
- `openai-codex/gpt-5-mini` — 更小 / 更快

刷新后，用户通过 `/model openai-codex/gpt-5-codex` 或模型选择器 UI 切换。

后续调用直接使用 OAuth 令牌访问 OpenAI — 跳过平台代理。适用订阅使用限制（非平台的信用余额）。

---

## 重新授权

通过 `refresh_token` 自动刷新令牌。如果出现 401：
1. `refresh()` — 尝试手动刷新路径。
2. 如果仍然失败，`logout()` + 从 `start()` 重新开始。

---

## 关键规则

- **切勿将 user_code 粘贴到 verification_url 中。** 它们是分开的 — 用户必须在打开 URL 后手动输入代码。
- **切勿在未明确用户请求的情况下启动流程。** "我想使用 ChatGPT" 足够；"我有 OpenAI 密钥" 是**不**的（那是 BYOK）。
- **在 `start` 和 `poll` 之间等待用户确认。** 自动轮询浪费 API 调用并给出陈旧的 "pending" 响应。
