# 社交媒体发布

通过 [SocialClaw](https://getsocialclaw.com) 实现以代理为中心的社交媒体发布。一个工作区 API 密钥，13 个平台，零每个平台的 OAuth 设置。

## 何时使用此技能

当用户想要时，使用此技能：
- 在多个社交媒体平台上发布或安排帖子
- 协调跨平台内容活动
- 上传并附加媒体到社交媒体帖子
- 检索帖子级别的互动分析
- 程序化管理内容日历

## 支持的平台

| 平台 | 备注 |
|------|------|
| X (Twitter) | 个人资料帖子、线程 |
| LinkedIn | 个人资料帖子 + 公司页面 |
| Instagram | 商业账户 + 独立账户 |
| Facebook Pages | 带链接预览的页面帖子 |
| TikTok | 视频描述 |
| Discord | 频道定位、嵌入 |
| Telegram | 频道/群组消息 |
| YouTube | 视频描述和元数据 |
| Reddit | 带标签的子版块帖子 |
| WordPress | 带 SEO 元数据的博客帖子 |
| Pinterest | 带板块定位的图钉 |

## 设置

```bash
# 通过 npx 安装
npx skills add ndesv21/socialclaw

# 或者作为包安装
npm install socialclaw@0.1.12

# 设置您的工作区 API 密钥
export SOCIALCLAW_API_KEY=your_key_here
```

在工作区获取 API 密钥 [getsocialclaw.com](https://getsocialclaw.com)。

## 工作流程

### 第 1 步：定义活动
指定平台、消息内容、计划以及任何媒体附件。

### 第 2 步：草拟平台变体
Claude 为每个渠道生成平台优化的文案（字符限制、标签规范、语气）。

### 第 3 步：上传媒体（可选）
上传一次图像或视频 — SocialClaw 将它们存储起来以供跨平台重复使用。

### 第 4 步：验证计划
Claude 在提交前检查平台特定的定时规则和速率限制。

### 第 5 步：发布或安排
帖子通过 SocialClaw API 排队。接收帖子 ID 和计划时间以供确认。

### 第 6 步：分析
发布后 24-48 小时内提取互动指标（展示量、点击量、反应）。

## 使用示例

### 单平台帖子
```
发布到我们公司的 LinkedIn 页面：
"很兴奋地宣布我们 Q2 产品路线图 — 以下是即将推出的内容。
[路线图图片]"
```

### 多平台活动
```
在 X、LinkedIn、Instagram 和 Discord 上宣布我们的 Beta 发布。
消息："我们的 Beta 已上线！100 个名额 — 在 example.com 注册 #发布"
计划为明天太平洋时间 9 点
```

### 内容系列
```
为我们的功能发布周创建一个 5 天的滴灌活动。
平台：X 和 LinkedIn。
我将为每天提供文案。
```

## 指南

1. **一个密钥，所有平台** — SOCIALCLAW_API_KEY 在所有连接的账户中验证
2. **平台原生文案** — 为每个平台调整语气和格式，而不是复制粘贴
3. **验证时间** — 提交前始终确认计划以避免速率限制错误
4. **媒体重复使用** — 上传一次资产并在多个帖子中通过 ID 引用

## 限制

- 需要一个活跃的 SocialClaw 账户和连接的社交媒体账户
- 平台可用性取决于工作区层级
- 某些平台需要视频内容以获得最佳覆盖（TikTok、YouTube、Instagram Reels）
