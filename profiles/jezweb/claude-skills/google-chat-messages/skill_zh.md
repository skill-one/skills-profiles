# Google Chat 消息

通过传入的 webhook 向 Google Chat 空间发送消息。生成文本消息、丰富卡片（cardsV2）和线程式回复。

## 你能生成的

- 带有 Google Chat 格式的文本消息
- 带有标题、区域和组件的丰富卡片消息（cardsV2）
- 线程式对话
- 可重用的 webhook 发送工具

## 工作流程

### 第 1 步：获取 Webhook URL

在 Google Chat 中：
1. 打开一个空间 > 点击空间名称 > **管理 webhook**
2. 创建 webhook（命名，可选添加头像 URL）
3. 复制 webhook URL

将 URL 存储为环境变量或您的密钥管理器中——切勿硬编码。

### 第 2 步：选择消息类型

| 需求 | 类型 | 复杂度 |
|------|------|------------|
| 简单通知 | 文本消息 | 低 |
| 结构化信息（状态、摘要） | 卡片消息（cardsV2） | 中等 |
| 持续更新 | 线程式回复 | 中等 |
| 操作按钮（打开 URL） | 带有 buttonList 的卡片 | 中等 |

### 第 3 步：发送消息

使用 `assets/webhook-sender.ts` 作为发送工具。使用 `assets/card-builder.ts` 进行结构化卡片构建。

## 文本格式化

Google Chat 不使用标准 Markdown。

| 格式 | 语法 | 示例 |
|--------|--------|---------|
| 粗体 | `*text*` | `*重要*` |
| 斜体 | `_text_` | `_强调*` |
| 删除线 | `~text~` | `~已删除*` |
| 等宽 | `` `text` `` | `` `代码*` |
| 代码块 | ` ```text``` ` | 多行代码 |
| 链接 | `<url\|text>` | `<https://example.com\|点击这里>` |
| 提及用户 | `<users/USER_ID>` | `<users/123456>` |
| 提及所有人 | `<users/all>` | `<users/all>` |

**不支持**： `**双星号**`、标题（`###`）、引用、表格、内联图片。

### 文本消息示例

```typescript
await sendText(webhookUrl, '*构建完成*\n\n分支： `main*`\n状态：通过\n<https://ci.example.com/123|查看构建>');
```

## cardsV2 结构

卡片使用 cardsV2 格式（推荐使用，而非传统卡片）。

```typescript
const message = {
  cardsV2: [{
    cardId: '唯一ID*',
    card: {
      header: {
        title: '卡片标题*',
        subtitle: '可选副标题*',
        imageUrl: 'https://example.com/icon.png*',
        imageType: 'CIRCLE'  // 或 'SQUARE'
      },
      sections: [{
        header: '区域标题*',  // 可选
        widgets: [
          // 组件在此处添加
        ]
      }]
    }
  }]
};
```

## 组件参考

cardsV2 区域中所有可用的组件类型。

### textParagraph

格式化文本块。支持 Google Chat 格式化（`*粗体*`、`_斜体*`、`<url\|text>`）。

```typescript
{
  textParagraph: {
    text: '*状态*：所有系统正常运行\n_上次检查*：5 分钟前'
  }
}
```

### decoratedText

带可选图标的标签值。用于键值数据的最通用组件。

**基本**：
```typescript
{
  decoratedText: {
    topLabel: '环境*',
    text: '生产*',
    bottomLabel: '上次部署 2 小时前*'
  }
}
```

**带起始图标**：
```typescript
{
  decoratedText: {
    topLabel: '状态*',
    text: '健康*',
    startIcon: { knownIcon: 'STAR' }
  }
}
```

**带自定义图标 URL**：
```typescript
{
  decoratedText: {
    topLabel: 'GitHub*',
    text: 'PR #142 已合并*',
    startIcon: {
      iconUrl: 'https://github.githubassets.com/favicons/favicon.svg*',
      altText: 'GitHub*'
    }
  }
}
```

**带按钮**：
```typescript
{
  decoratedText: {
    topLabel: '警报*',
    text: 'CPU 使用率 95%*',
    button: {
      text: '查看*',
      onClick: { openLink: { url: 'https://monitoring.example.com*' } }
    }
  }
}
```

**可点击（整个组件）**：
```typescript
{
  decoratedText: {
    text: '查看完整报告*',
    wrapText: true,
    onClick: { openLink: { url: 'https://reports.example.com*' } }
  }
}
```

**带换行**：
```typescript
{
  decoratedText: {
    topLabel: '描述*',
    text: '这是一个较长的描述，应该换行而不是被截断*',
    wrapText: true
  }
}
```

### buttonList

一个或多个操作按钮。按钮打开 URL 或触发操作。

**单个按钮**：
```typescript
{
  buttonList: {
    buttons: [{
      text: '打开仪表板*',
      onClick: { openLink: { url: 'https://dashboard.example.com*' } }
    }]
  }
}
```

**多个按钮**：
```typescript
{
  buttonList: {
    buttons: [
      {
        text: '批准*',
        onClick: { openLink: { url: 'https://app.example.com/approve/123*' } },
        color: { red: 0, green: 0.5, blue: 0, alpha: 1 }
      },
      {
        text: '拒绝*',
        onClick: { openLink: { url: 'https://app.example.com/reject/123*' } }
      }
    ]
  }
}
```

**带图标的按钮**：
```typescript
{
  buttonList: {
    buttons: [{
      text: 'GitHub 上查看*',
      icon: { knownIcon: 'BOOKMARK' },
      onClick: { openLink: { url: 'https://github.com/org/repo/pull/42*' } }
    }]
  }
}
```

### image

独立的图片组件。

```typescript
{
  image: {
    imageUrl: 'https://example.com/chart.png*',
    altText: '月度使用图表*'
  }
}
```

### divider

组件之间的水平分隔线。

```typescript
{ divider: {} }
```

### 可折叠区域

区域可以折叠，仅显示前 N 个组件：

```typescript
{
  header: '详细信息*',
  collapsible: true,
  uncollapsibleWidgetsCount: 2,  // 显示前 2 个，其余折叠
  widgets: [
    { decoratedText: { topLabel: '状态*', text: '活动*' } },
    { decoratedText: { topLabel: '区域*', text: 'AU*' } },
    // 这些被折叠
    { decoratedText: { topLabel: '实例*', text: 'prod-01*' } },
    { decoratedText: { topLabel: '内存*', text: '2.1 GB*' } },
    { decoratedText: { topLabel: 'CPU*', text: '45%*' } }
  ]
}
```

## 已知图标

通过 `knownIcon` 在 decoratedText 和 button 组件中可用的图标。

```typescript
{ startIcon: { knownIcon: 'STAR' } }
// 或
{ icon: { knownIcon: 'EMAIL' } }
```

| 图标名称 | 用途 |
|-----------|---------|
| `AIRPLANE` | 旅行、航班 |
| `BOOKMARK` | 保存、参考、链接 |
| `BUS` | 交通、公交 |
| `CAR` | 驾驶、交通 |
| `CLOCK` | 时间、持续时间、日程 |
| `CONFIRMATION_NUMBER_ICON` | 票证、预订 |
| `DESCRIPTION` | 文档、文件 |
| `DOLLAR` | 货币、定价、成本 |
| `EMAIL` | 邮件、消息 |
| `INVITE` | 邀请 |
| `MAP_PIN` | 位置、地址 |
| `MEMBERSHIP` | 会员、用户 |
| `MULTIPLE_PEOPLE` | 团队、小组 |
| `OFFER` | 优惠、促销 |
| `PERSON` | 个人用户 |
| `PHONE` | 电话号码、通话 |
| `SHOPPING_CART` | 商业、购买 |
| `STAR` | 评分、收藏、重要 |
| `STORE` | 商店、零售 |
| `TICKET` | 票证、活动 |
| `VIDEO_CAMERA` | 视频、会议 |

对于列表中未包含的图标，使用 `iconUrl` 与任何公开可访问的图片（方形，最好是 24x24 或 48x48 像素）。

## 线程

使用 `threadKey` 将消息串联起来：

```typescript
// 第 1 条消息——创建线程
const response = await sendCard(webhookUrl, card, {
  threadKey: 'deploy-2026-02-16'
});

// 回复线程——追加 &messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD
const threadUrl = `${webhookUrl}&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD`;
await sendCard(threadUrl, replyCard, {
  threadKey: 'deploy-2026-02-16'
});
```

`threadKey` 是客户端分配的字符串。使用一致的键来关联相关消息（例如，`deploy-{日期}`、`alert-{ID}`）。

## 常见模式

### 通知卡片

```typescript
import { buildCard, sendCard } from './assets/card-builder';
import { sendWebhook } from './assets/webhook-sender';

const card = buildCard({
  cardId: 'deploy-notification*',
  title: '部署完成*',
  subtitle: '生产* - v2.1.0*',
  imageUrl: 'https://example.com/your-icon.png*',
  sections: [{
    widgets: [
      { decoratedText: { topLabel: '环境*', text: '生产*' } },
      { decoratedText: { topLabel: '版本*', text: 'v2.1.0*' } },
      { decoratedText: { topLabel: '状态*', text: '*健康*', startIcon: { knownIcon: 'STAR' } } },
      { buttonList: { buttons: [{ text: '查看部署*', onClick: { openLink: { url: 'https://dash.example.com*' } } }] } }
    ]
  }]
});
```

### 摘要卡片（每周总结）

```typescript
const digest = buildCard({
  cardId: 'weekly-digest*',
  title: '每周总结*',
  subtitle: `${count} 次更新本周*`,
  sections: [
    {
      header: '亮点*',
      widgets: items.map(item => ({
        decoratedText: { text: item.title, bottomLabel: item.date }
      }))
    },
    {
      widgets: [{
        buttonList: {
          buttons: [{ text: '查看全部*', onClick: { openLink: { url: dashboardUrl } } }]
        }
      }]
    }
  ]
});
```

## 防错措施

| 错误 | 修复 |
|---------|-----|
| 文本中 `**粗体**` | 使用 `*粗体*`（单星号） |
| `[text](url)` 链接 | 使用 `<url\|text>` 格式 |
| 缺少 `cardsV2` 包装 | 将卡片包装在 `{ cardsV2: [{ cardId, card }] }` 中 |
| 线程回复不线程 | 将 `&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD` 追加到 webhook URL |
| webhook 返回 400 | 检查 JSON 结构——常见问题是顶层缺少 `text` 或 `cardsV2` |
| 卡片未显示 | 确保 `sections` 至少有一个组件 |

## 资源文件

| 文件 | 目的 |
|------|---------|
| `assets/types.ts` | cardsV2 的 TypeScript 类型定义 |
| `assets/card-builder.ts` | 构建卡片消息的工具 |
| `assets/webhook-sender.ts` | 带错误处理的 webhook POST |
