---
name: discord
description: 通过OpenClaw的消息工具进行Discord消息工作流程。
---

# Discord

使用 `message` 工具并指定 `channel: "discord"`。该工具的架构描述了当前账号的 `channels.discord.actions.*` 门控所启用的操作；不要假设某些操作不可用。

## 工作流程

- 优先使用来自上下文的稳定 `guildId`、`channelId`、`messageId` 和 `userId` 值。当可能涉及多个 Discord 账号时，请传递 `accountId`。
- 在用户引用不明确时，编辑、删除、置顶、管理或回复消息前，必须先解析出确切的消息。
- 将线程回复保留在原线程中。论坛父级无法接收组件；请将组件发送到创建的论坛线程中。
- 对于破坏性或管理操作，除非用户已明确指定确切目标和操作，否则需要确认。

## 交互组件

`components` 必须是结构化对象或原生组件数组，不能是占位符字符串。不要将组件 v2 与传统的 `embeds` 结合使用。

```json
{
  "action": "send",
  "channel": "discord",
  "to": "channel:123",
  "message": "请选择一个选项",
  "components": {
    "blocks": [
      {
        "type": "actions",
        "buttons": [
          { "label": "批准", "style": "success", "callbackData": "approve" },
          { "label": "拒绝", "style": "danger", "callbackData": "decline" }
        ]
      }
    ]
  }
}
```

Discord 提及语法、组件可用性和表单提示会自动注入。请遵循当前的提示和工具架构，而不是重复的操作目录。
