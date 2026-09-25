# 📱 微信绑定

连接/重新连接/断开用户的微信账号，以便代理可以通过 `send_to_wechat` 推送消息。

`wechat` 工具保持内置。此 SKILL.md 是参考文档。

## 参见
- `config/context/references/messaging-channels.md` — 绑定后如何实际发送消息
- `skills/tg-bot-binding/SKILL.md` — 类似的 Telegram 流程

---

## 典型绑定流程

```
qrcode → 用户扫描 → qrcode_status(qrcode=...) → connect(bot_token=...)
```

1. **生成二维码：** `wechat(action="qrcode")` — 将图像保存到工作区，返回 `qrcode`（id）+ `file_path`。
2. **向用户展示二维码。** 在网页频道：包含 `file_path` 以便前端内联渲染图像。在 TG/微信频道：通过 `send_to_telegram` 发送图像，附带 `file_path`。
3. **等待用户扫描并在微信中确认。** 不要自动轮询 — 先让用户说“已扫描”/“完成”。
4. **轮询完成状态：** `wechat(action="qrcode_status", qrcode=<来自步骤1的id>)`。扫描+确认完成后返回 `bot_token`。
5. **连接：** `wechat(action="connect", bot_token=<来自步骤4的值>)`。可选：`ilink_bot_id`，`ilink_user_id`（如果用户有多个微信账号）。
6. **向用户确认：** “微信已连接。您现在可以使用 send_to_wechat 推送消息。”

---

## 操作

| 操作 | 必填 | 目的 |
|---|---|---|
| `status` | — | 当前微信连接状态。在重新连接前、验证绑定时使用。 |
| `qrcode` | — | 生成二维码图像（保存到工作区）。返回 `qrcode` id + `file_path`。 |
| `qrcode_status` | `qrcode` | 轮询用户是否已扫描+确认。成功时返回 `bot_token`。 |
| `connect` | `bot_token` | 完成新的微信连接（在首次扫描二维码后）。可选：`ilink_bot_id`，`ilink_user_id`。 |
| `disconnect` | — | 终止当前微信会话（解除关联）。 |
| `reconnect` | `bot_token` | 重新建立先前绑定的微信（来自新二维码扫描的 token）。 |

---

## connect 与 reconnect 的区别

- **`connect`** — 首次绑定。用户以前从未绑定过这个微信。
- **`reconnect`** — 用户之前已连接，连接中断（例如 ilink 会话过期），并且他们刚刚扫描了新的二维码。

不确定时，先调用 `status`：
- `connected: false` + 无先前历史 → `connect`
- `connected: false` + 存在先前历史 → `reconnect`

---

## 基于频道的二维码展示

| 用户频道 | 如何展示二维码 |
|---|---|
| **网页** | 在回复中包含 `file_path` — 前端内联渲染它 |
| **Telegram** | `send_to_telegram(file_path=<qr_path>, message_type="photo")` |
| **微信** | （您不能 — 他们正在尝试绑定微信。告诉他们打开网页应用。） |

---

## 关键规则

- **不要自动轮询** `qrcode_status` 后 `qrcode`。等待用户确认他们在微信中扫描+确认。自动轮询会污染上游 API。
- **每次 `qrcode` 调用都会生成新图像。** 不要用新图像重新使用旧的 `qrcode` id — 上游会话与 id 绑定。
- **永远不要在聊天中粘贴 `bot_token`。** 它是凭证。一旦从 `qrcode_status` 获取它，立即将其传递给 `connect` / `reconnect`，不要将其回显给用户。
- **`disconnect` 是破坏性的** — 调用它前先与用户确认。
