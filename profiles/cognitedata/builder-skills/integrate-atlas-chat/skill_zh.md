# 集成 Atlas Agent Chat (异常路径)

**停止。** 除非满足所有以下条件，否则使用 **`integrate-fusion-agent`** (Atlas / EOS 侧边栏)：

1. 用户要求**应用内 / 嵌入式**聊天 — 不是“添加 Atlas” / “添加聊天”
2. 主 Atlas 侧边栏无法工作。此处**没有** manifest 字段。探测应用：
   - `@cognite/app-sdk` + `connectToHostApp` / `useHostApp` 在 Fusion/EOS 内解析成功 → 侧边栏工作；不要继续
   - 仅独立运行（主应用连接始终拒绝；应用从未在 Fusion 中加载）→ 允许应用内聊天
   - 如不确定，请询问。默认使用侧边栏
3. 用户接受此为非标准路径

然后遵循 https://docs.cognite.com/cdf/flows/guides/ai_agent_integration 并为 **$ARGUMENTS** 连接 `useAtlasChat`。保留产品 UI；不要用聊天视图替换应用。

不要将 `send()` / 聊天完成映射到 DMS 行。如果需要按项完成：**每个用户操作最多 5** 个，上限 **50**，按 `space:externalId:lastUpdatedTime` 缓存。参见 `integrate-fusion-agent`。
