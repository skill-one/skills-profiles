# 语音通话

使用语音通话插件开始或检查通话（Twilio、Telnyx、Plivo 或模拟）。

## 命令行界面 (CLI)

```bash
openclaw voicecall call --to "+15555550123" --message "来自 OpenClaw 的问候"
openclaw voicecall status --call-id <id>
```

## 工具

使用 `voice_call` 进行代理发起的通话。

操作：

- `initiate_call` (message, to?, mode?)
- `continue_call` (callId, message)
- `speak_to_user` (callId, message)
- `end_call` (callId)
- `get_status` (callId)

注意事项：

- 需要启用语音通话插件。
- 插件配置位于 `plugins.entries.voice-call.config` 下。
- Twilio 配置：`provider: "twilio"` + `twilio.accountSid/authToken` + `fromNumber`。
- Telnyx 配置：`provider: "telnyx"` + `telnyx.apiKey/connectionId` + `fromNumber`。
- Plivo 配置：`provider: "plivo"` + `plivo.authId/authToken` + `fromNumber`。
- 开发回退：`provider: "mock"`（无网络）。
