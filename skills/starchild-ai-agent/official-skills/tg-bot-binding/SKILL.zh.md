---
name: tg-bot-binding
description: 'Telegram机器人绑定：创建机器人，连接至Starchild，验证，故障排除。


  绑定方式有两种：(1) 扫码创建（推荐，自动绑定）或 (2) 手动使用BotFather + 令牌 + 验证。


  在设置Telegram推送时使用（例如：添加我的TG机器人，绑定代码，修复“telegram未推送”，白名单TG用户名）。'
---

# Telegram Bot 绑定指南

当用户询问关于Telegram Bot绑定、设置、连接、验证或任何相关主题时，请向他们提供以下指南。**始终使用用户的语言进行回复。**

## 概述

Starchild允许您连接自己的Telegram Bot，以便直接在Telegram中与您的AI代理聊天。绑定Bot有两种方式：

1. **扫码创建Bot（推荐）** — 扫描二维码，在Telegram中确认创建，Starchild自动完成绑定。无需复制token，无需验证码。
2. **手动绑定** — 通过@BotFather创建Bot，在控制台粘贴token，然后使用代码验证所有权。

> **尽可能优先选择扫码创建方法** — 它更快，步骤更少。

---

## 方法A：扫码创建Bot（推荐）

此方法创建一个新的Bot，并在一个流程中完成绑定 — 无需token和验证码。

### 第1步：打开Telegram Bot部分

1. 前往**Starchild控制台**（网页界面）。
2. 点击页面**左下角**的**头像**。
3. 在**账户管理**弹窗中，找到**Telegram Bot**部分。
4. 点击**"扫码创建Bot"**。

### 第2步：扫描二维码

会出现一个二维码以及一个链接。执行以下任一操作：

- **使用Telegram应用扫描二维码**（相机 → 扫描），或
- 点击**"在Telegram中打开"**直接跳转到创建页面。

### 第3步：在Telegram中确认创建

Telegram打开一个Bot创建页面。**确认**您要创建Bot。

### 第4步：完成！

Starchild检测到新的Bot并**自动完成绑定**。Bot直接进入**"运行中"**状态 — 无需验证码。在Telegram中发送`/start`即可开始与您的AI代理聊天。

> **注意**：通过此方式创建的Bot由Starchild的Bot基础设施管理。稍后要删除它，请在控制台使用**"删除Bot"**操作（不要在@BotFather中删除）。

---

## 方法B：手动绑定（BotFather + Token）

如果您更喜欢通过@BotFather自己创建和拥有Bot token，请使用此流程。

### 第1步：通过BotFather创建Telegram Bot

1. 打开Telegram并搜索**@BotFather**（创建Bot的官方Telegram Bot）。
2. 向BotFather发送`/newbot`。
3. 按照提示操作：
   - 为您的Bot输入一个**显示名称**（例如，"My Starchild Agent"）。
   - 为您的Bot输入一个**用户名**（必须以`bot`结尾，例如，`my_starchild_bot`）。
4. BotFather将回复您的**Bot Token** — 一个类似`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`的字符串。**复制此token并妥善保管。** 不要公开分享。

### 第2步：在Starchild控制台添加Bot Token

1. 前往**Starchild控制台**（网页界面）。
2. 点击页面**左下角**的**头像**。
3. 在**账户管理**弹窗中，找到**Telegram Bot**部分。
4. 粘贴您的**Bot Token**并提交。
5. 系统将：
   - 使用Telegram的API（调用`getMe`）验证token。
   - 生成一个**6位验证码**（有效期为5分钟）。
   - 将Bot状态设置为**"待验证"**。
6. 您将在控制台上看到显示的验证码。**复制此验证码。**

### 第3步：在Telegram中验证Bot所有权

您有两种验证方式：

#### 选项A：深度链接（推荐）

点击控制台上提供的验证链接。它将打开您的Bot并自动提交验证码。链接格式为：

```
https://t.me/<your_bot_username>?start=verify_<CODE>
```

#### 选项B：手动验证

1. 在Telegram中打开您的Bot（搜索`@<your_bot_username>`）。
2. 发送`/start` — Bot将提示您输入验证码。
3. 输入**6位验证码**并发送。

### 第4步：完成！

验证通过后，Bot状态短暂变为**"已激活"**，然后自动过渡到**"运行中"** — 意味着您的Bot已上线并准备使用。您可以通过Telegram开始与您的AI代理聊天。发送`/start`查看欢迎消息和可用命令。

---

## Bot状态参考

| 状态 | 含义 |
|------|------|
| `pending` | 添加了Bot token，等待所有权验证（仅手动流程） |
| `active` | 所有权验证通过，正在过渡到运行中 |
| `running` | Bot已上线并准备使用 |
| `deleted` | 用户已删除Bot |

---

## 故障排除

### "验证码已过期"

验证码有效期为**5分钟**。如果过期：
- 返回控制台，点击**"刷新验证码"**生成一个新的。
- 然后在Telegram中使用新验证码进行验证。

### "尝试次数过多"

在**5次错误尝试**后，验证码因安全原因失效：
- 前往控制台，**删除Bot**，然后**重新添加**以获取一个新验证码。

### "Bot token已被其他用户注册"

每个Bot Token只能绑定到一个Starchild账户。如果您看到此错误：
- 确保您使用的是一个**新的、未使用的Bot token**。
- 如果您之前使用过此token，旧的绑定可能仍然存在。通过@BotFather创建一个新的Bot。

### "您已有一个活跃的Bot"

每个账户一次只能有一个**活跃的Bot**：
- 要切换Bot，首先从控制台**删除**当前Bot，然后添加新的Bot。
- 注意：删除Bot后，必须等待**1小时**才能添加新的Bot。

### "冷却时间激活 — 请稍后再添加新的Bot"

删除Bot后，您必须等待**1小时**才能添加新的Bot。控制台将显示冷却时间到期时间。

### "尝试次数过多。请稍等再试。"

扫码创建流程受到速率限制。如果您看到此消息，请稍等片刻，然后再次点击**"扫码创建Bot"**。

### "授权已过期。请重试。"

扫码创建的二维码/链接仅在有限时间内有效。如果过期：
- 取消当前配对，然后点击**"扫码创建Bot"**获取一个新的二维码。

### Bot在Telegram中无响应

- 检查控制台上的Bot状态 — 它应为**"运行中"**。
- 如果状态为**"待验证"**，请完成验证步骤（手动流程）。
- 尝试向Bot发送`/start`。
- 如果问题仍然存在，尝试删除并重新添加Bot（在1小时冷却时间后）。

---

## 快速参考

| 操作 | 位置 |
|------|------|
| 创建并绑定Bot（最快） | Starchild控制台 → 左下角头像 → 账户管理 → Telegram Bot → "扫码创建Bot" → 扫描二维码 → 在Telegram中确认 |
| 手动创建新的Telegram Bot | Telegram → @BotFather → `/newbot` |
| 添加Bot token | Starchild控制台 → 左下角头像 → 账户管理 → Telegram Bot |
| 验证所有权 | Telegram → 您的Bot → 输入验证码 |
| 刷新验证码 | Starchild控制台 → 账户管理 → Telegram Bot → "刷新验证码" |
| 删除Bot | Starchild控制台 → 账户管理 → Telegram Bot → "删除Bot" |
| 检查Bot状态 | Starchild控制台 → 账户管理 → Telegram Bot |

---

## 重要提示

- **推荐流程**：使用**"扫码创建Bot"** — 它自动创建并绑定Bot，无需token或验证码。
- **扫码创建的Bot由Starchild管理**：它们通过Starchild的Bot基础设施创建。从控制台删除它们，不要从@BotFather删除。
- **安全**：在手动流程中，您的Bot Token在存储前会进行加密（AES-256）。它永远不会在API响应中暴露。
- **一个Bot per账户**：您一次只能有一个活跃的Telegram Bot。
- **冷却时间**：删除Bot后，等待1小时才能添加新的Bot。
- **速率限制**：添加Bot和刷新验证码限制为每分钟3次请求。
- **验证尝试**：您有5次尝试输入正确代码的机会，之后它将被失效。
