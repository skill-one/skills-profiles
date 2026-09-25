# 🟢 xAI OAuth 登录引导

使用任何活跃的 **xAI 账户** — X Premium、X Premium+、SuperGrok 或 SuperGrok Heavy — 用于 `grok-4.3`、`grok-build-0.1`、`grok-4.20-*` 和多智能体模型。无需单独的 API 密钥。

这是 **标准 OAuth 2.0** (RFC 8628 设备授权授予)，不是供应商自定义流程。

## 等级 → 模型访问

`auth.x.ai` 发行的 JWT 包含 `tier` 声明；更高的等级解锁更多 `/v1/models` 中的模型。观察到的映射（xAI 未正式发布）：

| 等级 | 订阅 | 大致模型访问 |
|---|---|---|
| 1 | X Premium ($8/月) | grok-4.3 基线 |
| 2 | X Premium+ ($16/月) | + grok-4.20-0309 变体 |
| 3 | SuperGrok ($30/月) | + 推理模型 |
| 4 | SuperGrok Heavy ($300/月) | + grok-build-0.1 + 多智能体 |

`status()` 报告用户的等级，以便他们知道哪些模型将可用。

这是一个 **脚本模式技能** — 未注册任何工具。阅读此文件，然后从 `bash` 块中调用导出。

## 参见

- `byok-custom-model` 技能 — 用于供应商密钥 BYOK 设置（从 console.x.ai 获取 xAI API 密钥，不同机制 — 按令牌计费，不是订阅支持）
- `chatgpt-codex-onboarding` 技能 — 相同模式，用于 ChatGPT/Codex 订阅
- `config/context/references/model-onboarding.md` — 整体模型选择格局

## 后端兼容性

此技能依赖于平台镜像中的 `core.xai_grok` Python 包（发布于 2026-05-22）。在旧镜像上，技能加载正常，但每个公共函数返回：

```json
{
  "ok": false,
  "error": "xai_oauth_backend_unavailable",
  "detail": "ModuleNotFoundError: core.xai_grok not found in any of: [/app, /data/workspace/starchild-clawd]",
  "hint": "更新平台镜像 OR 转回 byok-custom-model 并使用 xAI API 密钥。"
}
```

如果看到此响应，**不要重试** — 平台本身需要更新。要么等待镜像刷新，要么引导用户使用 `byok-custom-model` 并从 console.x.ai 获取 API 密钥。

---

## 何时使用此技能

✅ **使用** 当用户明确说以下之一：
- "使用我的 Grok / SuperGrok 账户登录"
- "使用我的 SuperGrok / X Premium 订阅"
- "连接 SuperGrok Heavy"
- "使用 xAI / Grok 登录"
- "使用我的 Grok Heavy 订阅"

❌ **不要使用** 用于：
- "通过 API 密钥添加 Grok" / "我有 xAI API 密钥" → 使用 `byok-custom-model`（xAI 模板）
- 其他供应商（Anthropic、OpenAI、Gemini、Qwen 等）→ 使用 `byok-custom-model`
- "添加 Grok 模型" 而未提及订阅 → 询问用户他们想选择哪条路径（订阅 OAuth vs. API 密钥 BYOK）

这两条路径在计费上是互斥的。订阅 OAuth 使用用户的月度配额；BYOK API 密钥使用 console.x.ai 按令牌计费信用。

---

## 关键预检查 — 账户门禁意识

xAI 有一个已知的后端门禁，**即使有活跃的 SuperGrok 订阅，也会拒绝某些账户的 OAuth 授权**。这是上游 xAI 行为，不是客户端错误。症状：

- 验证页面加载，但点击 "Approve" 从令牌端点返回 `access_denied`
- Hermes Agent 在 [issue #26847](https://github.com/NousResearch/hermes-agent/issues/26847) 中记录了相同问题

如果 `poll()` 返回 `AccountAccessDenied`：
1. 验证用户的 SuperGrok 订阅是否活跃（grok.com / 设置）
2. 建议他们在已登录的浏览器中尝试验证 URL（不是新的隐身模式）
3. 如果仍然被拒绝 → 转回 BYOK API 密钥路径（`byok-custom-model` 技能，xAI 模板，密钥来自 https://console.x.ai）

**不要无声重试** — 门禁是按账户确定的，重试会浪费时间。

---

## 流程

流程有 4 个用户可见步骤。按以下方式驱动：

### 1. start() — 生成验证 URL

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, '/data/workspace/skills/xai-grok-onboarding')
from exports import start
print(json.dumps(start(), indent=2))
EOF
```

返回 `verification_url_with_code` — 告知用户在浏览器中打开它，登录（如果需要），然后点击 Approve。

⚠️ **在调用 poll() 之前等待明确的用户确认**。过早轮询会为“仍然挂起”的状态消耗令牌。

### 2. poll() — 确认批准（用户说“完成”后）

```bash
python3 - <<'EOF'
import json, sys
sys.path.insert(0, '/data/workspace/skills/xai-grok-onboarding')
from exports import poll
print(json.dumps(poll(), indent=2))
EOF
```

三个终端结果：
- `status="connected"` → 成功；显示用户 `default_model_id` 以切换
- `status="pending"` → 用户尚未批准；在重新轮询之前询问他们确认
- `ok=false` with `access_denied` → 见“账户门禁”部分上述
- `ok=false` with `expired` → 设备代码超时（15 分钟）；调用 `start()` 重新

### 3. 成功连接后 — 告知用户

当 `poll()` 返回 `status='connected'` 时，你必须做的第一件事是告诉用户：

> "连接成功。请刷新你的浏览器页面 — 一旦它重新加载，新的 `xai-grok/*` 模型将出现在模型选择器中。"

Web 前端在客户端缓存模型列表，并在 OAuth 连接完成后**不会**自动刷新。没有手动刷新，用户将看不到他们新可用的模型，并会认为连接失败。始终在回复中包含此说明 — 不要假设选择器会自动更新。

刷新后，默认模型是 `xai-grok/grok-4.3`。其他可用模型取决于订阅等级（SuperGrok Heavy 解锁 `grok-build-0.1`）。

切换：`/model xai-grok/grok-4.3` 或使用选择器。

---

## 函数参考

| 函数 | 参数 | 返回 |
|---|---|---|
| `status()` | — | 当前凭证状态 + 可用模型 + 过期 |
| `start()` | — | 设备代码提示：`{verification_url_with_code, user_code, expires_in_seconds}` |
| `poll(pending_id=None)` | 可选 `pending_id` | `{status: connected/pending}` + 凭证信息 |
| `logout()` | — | 删除凭证 + 冲刷代理缓存 |
| `refresh()` | — | 强制刷新访问令牌（调试；通常自动） |
| `models(force=False)` | — | 从 OAuth 端点列出可用模型 |

`force=True` 在 `models` 上绕过缓存 TTL。

所有函数在成功时返回带有 `ok: True` 的字典，或在失败时返回 `ok: False, error: "..."`。

---

## 连接后

模型以 `xai-grok/` 前缀出现：
- `xai-grok/grok-4.3` — 主要聊天模型（默认）
- `xai-grok/grok-build-0.1` — Grok Build 编码模型（SuperGrok Heavy 等级仅限）
- `xai-grok/grok-4.20-0309-reasoning` — 推理变体
- `xai-grok/grok-4.20-0309-non-reasoning` — 更快，无推理
- `xai-grok/grok-4.20-multi-agent-0309` — 多智能体变体（内部使用 `/v1/responses`）

用户通过 `/model xai-grok/grok-4.3` 或模型选择器 UI 切换。

### 路径路由（透明）

提供商会根据模型 ID 自动路由：
- 多智能体模型 → `https://api.x.ai/v1/responses`（响应 API）
- 所有其他 Grok 模型 → `https://api.x.ai/v1/chat/completions`（OpenAI 兼容）

用户不需要知道每个模型使用哪种方言 — 传递标准的 `messages=[...]` 形状对两者都有效。对于多智能体，可选的 `thinking={"effort": "low"|"medium"|"high"}` 控制多少智能体协作。

后续聊天调用直接使用 OAuth 带宽访问 `https://api.x.ai/v1`，绕过平台代理。**订阅使用限制适用**（不是平台信用余额）。图像/视频模型（`grok-imagine-*`）在聊天选择器中被过滤，但可通过图像生成工具访问。

---

## xAI 的 OAuth 允许列表 — 最常见的“前端拒绝我的登录”原因

**关键背景（2026-05 从独立实现验证）**：xAI 的后端在 OAuth API 表面维护一个内部允许列表，并频繁返回 `HTTP 403` 到 OAuth 令牌，即使用户的订阅是活跃的并且设备代码流程本身成功。这是 Hermes Agent 记录的（[他们的 xAI OAuth 故障排除](https://hermes-agent.nousresearch.com/docs/guides/xai-grok-oauth#http-403-after-a-successful-login-tier--entitlement)）并由独立 OpenCode 插件作者确认。**这不是我们适配器中的错误 — 切换到 PKCE 流程不会绕过它（两种授权类型都命中相同的允许列表）。**

### 订阅等级 ↔ OAuth 可用性（观察到的，不保证）

| 订阅 | 价格 | OAuth 典型结果 |
|---|---|---|
| X Premium (X.com 仅限) | $8 /月 | ❌ 常常被拒绝 — 权益不足 |
| X Premium+ (链接的 X 账户) | $16 /月 | ✅ 通常工作 — xAI 通过 X 账户自动链接 |
| SuperGrok (grok.com 直接) | $30 /月 | ⚠️ 混合 — 一些用户被阻止，一些通过 |
| SuperGrok Heavy | $300 /月 | ✅ 可靠地工作 |

### 开始流程前的预检查

如果用户有 **独立的 X Premium** 订阅（不是 Premium+）或 **SuperGrok 基础** 订阅并遇到前端拒绝，告诉他们按以下顺序首先执行：

1. 前往 https://grok.com → 设置 → 账户 → **“连接您的 X 账户”**（将两个身份链接起来，以便 xAI 验证订阅状态）
2. 确保链接的 X 账户是携带 Premium / Premium+ 标签的那个
3. 链接后，在 https://accounts.x.ai 退出 + 重新登录（刷新权限）
4. 重试设备代码流程

大量报告的“OAuth 登录失败 / 设备代码从未接受”案例可追溯到**缺少 X 账户链接** — xAI 后端无法在没有链接的情况下验证 Premium 状态，并且前端会无声拒绝设备代码。

### OAuth 仍然失败后 → 建议使用 BYOK

社区的标准解决方案（Hermes、OpenCode 插件等）是**停止与 OAuth 作战，切换到 API 密钥**：

- `XAI_API_KEY` 路径使用不同的 xAI 后端（console.x.ai 按令牌计费）**不受到 OAuth 允许列表的限制**。
- 告知用户在 https://console.x.ai 获取密钥，然后引导他们使用 `byok-custom-model` 技能和 xAI 模板。设置只需两分钟。
- 权衡：BYOK 从单独的钱包按令牌计费，而不是使用订阅配额 — 清楚解释，以便用户有意识地选择。

### 我们不做什么

- ❌ 模拟引用者 / 伪装成另一个已知客户端（Hermes、grok-cli 等）— 绕过权益违反 ToS，xAI 可能会进一步收紧允许列表
- ❌ 在 `access_denied` 上重试设备代码流程 — 它会持续失败；建议预检查或 BYOK
- ❌ 告知用户这是 Starchild 错误 — 这是 xAI 账户门禁决定，我们无法覆盖

---

## 限制与 BYOK 回退

xAI **不** 发布精确的每日上限或 RPM，像 OpenAI 那样。OAuth 支持的 Grok 使用的实际现实：

- **没有发布的硬数字**。限制基于公平使用 — 如果你在短时间内生成大量流量，xAI 会暂时限制。
- **等级很重要**。Heavy ($300/月) 提供最高的消费者上限 — 显着高于 SuperGrok ($30) 或 X Premium+。标准文本/聊天在正常到重负载的日常使用中很少达到上限。
- **图像/视频/语音有更严格的配额**。例如，Heavy 用户在 12 小时内获得约 80+ 视频生成，但这些在高峰负载期间仍可能被限制。
- **软上限信号**：如果用户开始看到来自 xAI 的 `429` 或“速率限制超出”消息，他们已达到该功能的公平使用上限。等待它（限制在滚动窗口中重置，而不是固定时钟）或切换计费模式。

### 何时建议切换到 BYOK

如果用户想要**可预测的、按量付费**的高容量访问 — 或者如果他们经常遇到限制 — 他们可以切换到常规 xAI API 密钥：

1. 在 https://console.x.ai 获取密钥（按令牌计费，与订阅分开）
2. 使用 `byok-custom-model` 技能和 xAI 模板
3. BYOK 模型与 OAuth 模型一起出现在选择器中 — 每次切换

两条路径可以共存；用户每次请求选择。OAuth = 订阅配额（良好默认）。BYOK = 更清晰的速率限制 + 按令牌计费（适用于重自动化或当您想要成本透明时）。

### 错误 → 操作表

| 症状 | 原因 | 操作 |
|---|---|---|
| `429` / "速率限制超出" 在聊天上 | OAuth 公平使用上限被击中 | 等待软重置，或切换此请求到 BYOK |
| `403` / `access_denied` 在 OAuth 时 | xAI 账户门禁 | 使用 BYOK（见预检查部分上述） |
| `401` 在 `refresh()` 后重复 | 令牌被撤销 / 订阅已取消 | `logout()` + 重新启动，或切换到 BYOK |
| `503` / 5xx 上游 | xAI 基础设施问题 | 短暂后重试。BYOK 使用相同的上游，不会帮助 |

---

## 重新认证

令牌通过 `refresh_token` 自动刷新（6 小时访问令牌 TTL — 相对于 Codex 的 1 小时更慷慨）。如果出现 401：

1. `refresh()` — 尝试手动刷新路径
2. 如果仍然失败，`logout()` + 重新启动，从 `start()` 开始

---

## 关键规则

- **永远不要将 user_code 粘贴到验证 URL 字段中给用户**。URL `accounts.x.ai/oauth2/device?user_code=XXXX` 已经嵌入代码 — 直接打开它。
- **永远不要在没有明确用户请求的情况下开始流程**。“我想使用 Grok”需要后续问题关于订阅 vs. API 密钥；“使用我的 SuperGrok 订阅”就足够了。
- **在 `start` 和 `poll` 之间等待用户确认**。自动轮询会浪费 API 调用并产生陈旧的“挂起”响应。
- **在 `access_denied` 上，不要盲目重试**。解释门禁，建议 BYOK 回退。
- **永远不要记录或回显 access_token / refresh_token**。它们是持久凭证。导出从不包括它们在返回值中。
