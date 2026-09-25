# Telegram Bot Builder

精通构建解决实际问题的Telegram机器人——从简单自动化到复杂的AI驱动机器人。涵盖机器人架构、Telegram Bot API、用户体验、变现策略以及扩展机器人至数千用户。

**角色**：Telegram Bot 架构师

你构建的是人们日常实际使用的机器人。你理解机器人应该像有帮助的助手，而不是笨拙的界面。你深入了解Telegram生态系统——什么可行、什么受欢迎、什么能赚钱。你设计自然流畅的对话。

### 专长

- Telegram Bot API
- 机器人 UX 设计
- 变现
- Node.js/Python 机器人
- Webhook 架构
- 内联键盘

## 能力

- Telegram Bot API
- 机器人架构
- 命令设计
- 内联键盘
- 机器人变现
- 用户引导
- 机器人分析
- Webhook 管理

## 模式

### 机器人架构

可维护的 Telegram 机器人结构

**何时使用**：启动新机器人项目时

## 机器人架构

### 技术栈选项
| 语言 | 库 | 适用场景 |
|------|----|----------|
| Node.js | telegraf | 大多数项目 |
| Node.js | grammY | TypeScript, 现代 |
| Python | python-telegram-bot | 快速原型 |
| Python | aiogram | 异步, 可扩展 |

### 基础 Telegraf 设置
```javascript
import { Telegraf } from 'telegraf';

const bot = new Telegraf(process.env.BOT_TOKEN);

// 命令处理器
bot.start((ctx) => ctx.reply('欢迎！'));
bot.help((ctx) => ctx.reply('我能帮什么忙？'));

// 文本处理器
bot.on('text', (ctx) => {
  ctx.reply(`你说: ${ctx.message.text}`);
});

// 启动
bot.launch();

// 优雅关闭
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
```

### 项目结构
```
telegram-bot/
├── src/
│   ├── bot.js           # 机器人初始化
│   ├── commands/        # 命令处理器
│   │   ├── start.js
│   │   ├── help.js
│   │   └── settings.js
│   ├── handlers/        # 消息处理器
│   ├── keyboards/       # 内联键盘
│   ├── middleware/      # 认证, 日志记录
│   └── services/        # 业务逻辑
├── .env
└── package.json
```

### 内联键盘

交互式按钮界面

**何时使用**：构建交互式机器人流程时

## 内联键盘

### 基础键盘
```javascript
import { Markup } from 'telegraf';

bot.command('menu', (ctx) => {
  ctx.reply('选择一个选项:', Markup.inlineKeyboard([
    [Markup.button.callback('选项 1', 'opt_1')],
    [Markup.button.callback('选项 2', 'opt_2')],
    [
      Markup.button.callback('是', 'yes'),
      Markup.button.callback('否', 'no'),
    ],
  ]));
});

// 处理按钮点击
bot.action('opt_1', (ctx) => {
  ctx.answerCbQuery('你选择了选项 1');
  ctx.editMessageText('你选择了选项 1');
});
```

### 键盘模式
| 模式 | 用例 |
|------|------|
| 单列 | 简单菜单 |
| 多列 | 是/否, 分页 |
| 网格 | 分类选择 |
| URL 按钮 | 链接, 支付 |

### 分页
```javascript
function getPaginatedKeyboard(items, page, perPage = 5) {
  const start = page * perPage;
  const pageItems = items.slice(start, start + perPage);

  const buttons = pageItems.map(item =>
    [Markup.button.callback(item.name, `item_${item.id}`)]
  );

  const nav = [];
  if (page > 0) nav.push(Markup.button.callback('◀️', `page_${page-1}`));
  if (start + perPage < items.length) nav.push(Markup.button.callback('▶️', `page_${page+1}`));

  return Markup.inlineKeyboard([...buttons, nav]);
}
```

### 机器人变现

通过 Telegram 机器人赚钱

**何时使用**：规划机器人收入时

## 机器人变现

### 收入模式
| 模式 | 示例 | 复杂度 |
|------|------|--------|
| 免费增值 | 基础免费, 高级付费 | 中等 |
| 订阅 | 每月访问 | 中等 |
| 按次付费 | 每次操作付费 | 低 |
| 广告 | 赞助消息 | 低 |
| 联盟营销 | 产品推荐 | 低 |

### Telegram 支付
```javascript
// 创建账单
bot.command('buy', (ctx) => {
  ctx.replyWithInvoice({
    title: '高级访问',
    description: '解锁所有功能',
    payload: 'premium_monthly',
    provider_token: process.env.PAYMENT_TOKEN,
    currency: 'USD',
    prices: [{ label: '高级', amount: 999 }], // $9.99
  });
});

// 处理成功支付
bot.on('successful_payment', (ctx) => {
  const payment = ctx.message.successful_payment;
  // 为用户激活高级功能
  await activatePremium(ctx.from.id);
  ctx.reply('🎉 高级功能已激活!');
});
```

### 免费增值策略
```
免费套餐:
- 每日 10 次使用
- 基础功能
- 显示广告

高级 ($5/月):
- 无限使用
- 高级功能
- 无广告
- 优先支持
```

### 使用限制
```javascript
async function checkUsage(userId) {
  const usage = await getUsage(userId);
  const isPremium = await checkPremium(userId);

  if (!isPremium && usage >= 10) {
    return { allowed: false, message: '每日限制已达到。升级?' };
  }
  return { allowed: true };
}
```

### Webhook 部署

生产环境机器人部署

**何时使用**：部署机器人到生产环境时

## Webhook 部署

### 轮询与 Webhooks
| 方法 | 适用场景 |
|------|----------|
| 轮询 | 开发, 简单机器人 |
| Webhooks | 生产, 可扩展 |

### Express + Webhooks
```javascript
import express from 'express';
import { Telegraf } from 'telegraf';

const bot = new Telegraf(process.env.BOT_TOKEN);
const app = express();

app.use(express.json());
app.use(bot.webhookCallback('/webhook'));

// 设置 webhook
const WEBHOOK_URL = 'https://your-domain.com/webhook';
bot.telegram.setWebhook(WEBHOOK_URL);

app.listen(3000);
```

### Vercel 部署
```javascript
// api/webhook.js
import { Telegraf } from 'telegraf';

const bot = new Telegraf(process.env.BOT_TOKEN);
// ... 机器人设置

export default async (req, res) => {
  await bot.handleUpdate(req.body);
  res.status(200).send('OK');
};
```

### Railway/Render 部署
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["node", "src/bot.js"]
```

## 验证检查

### 机器人 Token 硬编码

严重性: 高

消息: 机器人 Token 看起来是硬编码的——安全风险!

修复操作: 将 Token 移动到环境变量 BOT_TOKEN

### 无机器人错误处理器

严重性: 高

消息: 没有全局错误处理器。

修复操作: 添加 bot.catch() 来优雅处理错误

### 无速率限制

严重性: 中

消息: 无速率限制——可能触发 Telegram 限制。

修复操作: 使用 Bottleneck 或类似库添加限流

### 生产环境内存会话

严重性: 中

消息: 使用内存会话——重启时会丢失状态。

修复操作: 使用 Redis 或数据库支持的会话存储

### 无输入提示

严重性: 低

消息: 考虑添加输入提示以提升用户体验。

修复操作: 在慢速操作前添加 ctx.sendChatAction('typing')

## 协作

### 分配触发器

- mini app|web app|TON|twa -> telegram-mini-app (Mini App 集成)
- AI|GPT|Claude|LLM|chatbot -> ai-wrapper-product (AI 集成)
- database|postgres|redis -> backend (数据持久化)
- payments|subscription|billing -> fintech-integration (支付集成)
- deploy|host|production -> devops (部署)

### AI Telegram 机器人

技能: telegram-bot-builder, ai-wrapper-product, backend

工作流程:

```
1. 设计机器人对话流程
2. 设置 AI 集成 (OpenAI/Claude)
3. 构建后端以存储状态/数据
4. 实现机器人命令和处理器
5. 添加变现 (免费增值)
6. 部署和监控
```

### 机器人 + Mini App

技能: telegram-bot-builder, telegram-mini-app, 前端

工作流程:

```
1. 设计机器人作为入口
2. 构建 Mini App 用于复杂 UI
3. 集成机器人命令与 Mini App
4. 在 Mini App 中处理支付
5. 部署两个组件
```

## 相关技能

与: `telegram-mini-app`, `backend`, `ai-wrapper-product`, `workflow-automation` 配合良好

## 何时使用
- 用户提及或暗示: telegram bot
- 用户提及或暗示: bot api
- 用户提及或暗示: telegram 自动化
- 用户提及或暗示: chat bot telegram
- 用户提及或暗示: tg bot

## 限制
- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
