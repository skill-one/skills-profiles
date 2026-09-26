# 📱 飞书/企业微信绑定

连接/断开用户的飞书或企业微信账户，以便代理通过飞书/企业微信应用进行聊天。

`feishu` 工具保持内置。此 SKILL.md 是参考文档。

## 参见

- `config/context/references/messaging-channels.md` — 消息如何跨渠道路由
- `skills/wechat-binding/SKILL.md` — 类似的微信流程
- `skills/tg-bot-binding/SKILL.md` — 类似的 Telegram 流程

---

## 品牌选择

| 品牌名 | 地区 | 域名 |
|---|---|---|
| `feishu` | 中国大陆 | feishu.cn / accounts.feishu.cn |
| `lark` | 国际 | larksuite.com / accounts.larksuite.com |

询问用户他们使用哪个品牌。如果不确定，默认为 `feishu`。中文用户几乎都使用 `feishu`。

---

## 典型绑定流程

```
connect(brand) → 用户扫描二维码 / 打开链接 → poll(device_code) → 完成
```

1. **开始设备流程：** `feishu(action="connect", brand="feishu")` — 返回 `verification_uri`、`device_code`，并将二维码图片保存到工作区。
2. **向用户展示两个选项：**
   - **二维码扫描：** 使用结果中的 `markdown_image` 将二维码图片内联显示（例如 `![飞书二维码](feishu_qrcode_xxx.png)`）。用户使用飞书/企业微信应用扫描它。
   - **直接链接：** 将 `verification_url` 显示为可点击的链接。用户在浏览器中打开它，登录飞书/企业微信，并确认。
3. **等待用户确认。** 不要自动轮询 — 让他们先说“完成” / “已确认” / “已确认” / “已扫描”。
4. **轮询完成状态：** `feishu(action="poll", device_code=<来自步骤1>, brand=<相同品牌>)`。
   - `status: "done"` → 绑定完成，祝贺用户。
   - `status: "pending"` → 询问用户是否已扫描二维码或打开链接并确认。
   - `status: "expired"` → 设备流程过期（通常为5分钟）。重新开始 `connect`。
5. **向用户确认：** "飞书/企业微信已连接！现在您可以在飞书/企业微信上与代理聊天。"

---

## 操作

| 操作 | 必填参数 | 目的 |
|---|---|---|
| `status` | — | 当前飞书/企业微信应用状态。用于检查是否已连接。 |
| `connect` | `brand` (可选, 默认 "feishu") | 开始设备流程。返回验证 URL + device_code。 |
| `poll` | `device_code`, `brand` | 检查用户是否已确认授权。返回状态。 |
| `disconnect` | — | 解绑飞书/企业微信应用（破坏性 — 首先与用户确认）。 |

---

## 基于渠道的二维码/链接显示

| 用户渠道 | 如何显示 |
|---|---|
| **Web** | 在回复中包含 `file_path` (二维码图片) — 前端将其内联渲染。同时显示链接。 |
| **Telegram** | `send_to_telegram(file_path=<qr_path>, message_type="photo")` + 在标题中包含链接 |
| **WeChat** | 仅显示链接（用户无法在 WeChat 中扫描飞书的二维码） |
| **Feishu** | (用户已经在飞书 — 他们不需要绑定。告诉他们已连接或检查 `status`。) |

---

## 与 WeChat / Telegram 的关键区别

| 方面 | 飞书/企业微信 | 微信 | Telegram |
|---|---|---|---|
| 认证方法 | 设备流程 (URL) | 二维码扫描 | Bot token |
| 用户操作 | 打开 URL + 在应用中确认 | 扫描二维码 + 确认 | 通过 @BotFather 创建机器人 |
| 凭证 | 无（设备流程处理） | bot_token (来自二维码) | bot_token (来自 BotFather) |
| 品牌选择 | feishu / lark | N/A | N/A |

---

## 关键规则

- **在 `connect` 后不要自动轮询**。等待用户确认他们已打开链接并在飞书/企业微信中确认。自动轮询浪费 API 调用。
- **设备流程在 ~5 分钟后过期**。如果 `poll` 返回 `expired`，告诉用户并重新开始 `connect`。
- **`disconnect` 是破坏性的** — 调用前与用户确认。它将停止飞书/企业微信网关实例。
- **品牌很重要** — `feishu` 和 `lark` 使用不同的 API 域名。使用错误品牌将静默失败或重定向到错误的登录页面。
- **每个用户一个应用** — 用户一次只能有一个飞书/企业微信应用。如果他们想切换品牌，必须先 `disconnect`，然后使用新品牌 `connect`。

---

## 故障排除

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| `connect` 返回错误 | 用户已有活动应用 | 先调用 `status`；如果活动，询问他们是否想 `disconnect` 并重新绑定 |
| `poll` 返回 `expired` | 用户确认太慢 | 重新开始 `connect` |
| `poll` 重复返回 `pending` | 用户尚未打开 URL | 提醒他们打开验证 URL |
| 用户说“找不到链接” | URL 在之前的消息中 | 重新运行 `connect` 获取新 URL |
