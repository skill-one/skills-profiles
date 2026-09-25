# ClawDirect-Dev

使用 ATXP 基于的认证构建面向代理的网页体验。

**参考实现**: https://github.com/napoleond/clawdirect

## 什么是 ATXP？

ATXP（代理交易协议）使 AI 代理能够认证并支付服务费用。在构建面向代理的网站时，ATXP 提供以下功能：

- **代理身份**: 知道是哪个代理在进行请求
- **支付**: 对高级操作进行收费（可选）
- **MCP 集成**: 暴露代理可以编程调用的工具

有关完整 ATXP 详细信息: https://skills.sh/atxp-dev/cli/atxp

## 代理如何交互

代理通过两种方式与您的网站交互：

1. **浏览器**: 代理使用浏览器自动化工具访问您的网站，点击按钮，填写表单，导航——就像人类一样
2. **MCP 工具**: 代理直接调用您的 MCP 端点进行程序化操作（认证、支付等）

基于 cookie 的认证模式连接了这些方式：代理通过 MCP 获取认证 cookie，然后在浏览时使用它。

**重要提示**: 代理浏览器通常无法直接设置 HTTP-Only cookie。推荐的模式是代理将 cookie 值传递在查询字符串中（例如，`?myapp_cookie=XYZ`），然后服务器设置 cookie 并重定向到干净的 URL。

## 架构概述

```
┌──────────────────────────────────────────────────────────────────┐
│                         AI 代理                                 │
│  ┌─────────────────────┐         ┌─────────────────────────┐    │
│  │   浏览器工具      │         │   MCP 客户端            │    │
│  │   (访问网站)      │         │   (调用工具)         │    │
│  └─────────┬───────────┘         └───────────┬─────────────┘    │
└────────────┼─────────────────────────────────┼──────────────────┘
             │                                 │
             ▼                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    您的应用程序                             │
│  ┌─────────────────────┐    ┌─────────────────────────┐        │
│  │   Web 服务器        │    │   MCP 服务器            │        │
│  │   (Express)         │    │   (@longrun/turtle)     │        │
│  │                     │    │                         │        │
│  │   - 提供 UI       │    │   - yourapp_cookie      │        │
│  │   - Cookie 认证     │    │   - yourapp_action      │        │
│  └─────────┬───────────┘    └───────────┬─────────────┘        │
│            │                            │                       │
│            └──────────┬─────────────────┘                       │
│                       ▼                                         │
│              ┌─────────────────┐                                │
│              │     SQLite      │                                │
│              │   auth_cookies  │                                │
│              └─────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## 构建步骤

1. **创建 MCP 服务器** 与您的网站一起
2. **在 MCP 服务器中实现 cookie 工具**
3. **在您的 Web API 中使用 cookie 进行认证**
4. **为您的网站发布一个代理技能**

## 第 1 步：项目设置

使用所需的堆栈初始化 Node.js 项目：

```bash
mkdir my-agent-app && cd my-agent-app
npm init -y
npm install @longrun/turtle @atxp/server @atxp/express better-sqlite3 express cors dotenv zod
npm install -D typescript @types/node @types/express @types/cors @types/better-sqlite3 tsx
```

创建 `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

创建 `.env`:

```
FUNDING_DESTINATION_ATXP=<your_atxp_account>
PORT=3001
```

## 第 2 步：带 Cookie 认证的数据库

创建 `src/db.ts`:

```typescript
import Database from 'better-sqlite3';
import crypto from 'crypto';

const DB_PATH = process.env.DB_PATH || './data.db';
let db: Database.Database;

export function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');

    // 认证 cookie 表 - 将 cookie 映射到 ATXP 账户
    db.exec(`
      CREATE TABLE IF NOT EXISTS auth_cookies (
        cookie_value TEXT PRIMARY KEY,
        atxp_account TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 在这里添加您应用的表
  }
  return db;
}

export function createAuthCookie(atxpAccount: string): string {
  const cookieValue = crypto.randomBytes(32).toString('hex');
  getDb().prepare(`
    INSERT INTO auth_cookies (cookie_value, atxp_account)
    VALUES (?, ?)
  `).run(cookieValue, atxpAccount);
  return cookieValue;
}

export function getAtxpAccountFromCookie(cookieValue: string): string | null {
  const result = getDb().prepare(`
    SELECT atxp_account FROM auth_cookies WHERE cookie_value = ?
  `).get(cookieValue) as { atxp_account: string } | undefined;
  return result?.atxp_account || null;
}
```

## 第 3 步：带 Cookie 工具的 MCP 工具

创建 `src/tools.ts`:

```typescript
import { defineTool } from '@longrun/turtle';
import { z } from 'zod';
import { requirePayment, atxpAccountId } from '@atxp/server';
import BigNumber from 'bignumber.js';
import { createAuthCookie } from './db.js';

// Cookie 工具 - 代理调用此工具以获取浏览器认证
export const cookieTool = defineTool(
  'myapp_cookie',  // 将 'myapp' 替换为您的应用名称
  '获取用于浏览器使用的认证 cookie。在使用 Web 界面时设置此 cookie 进行认证。',
  z.object({}),
  async () => {
    // 免费，但需要 ATXP 认证
    const accountId = atxpAccountId();
    if (!accountId) {
      throw new Error('认证需要');
    }

    const cookie = createAuthCookie(accountId);

    return JSON.stringify({
      cookie,
      instructions: '要在浏览器中认证，请导航到 https://your-domain.com?myapp_cookie=<cookie_value> - 服务器将设置 HTTP-only cookie 并重定向。或者，如果您的浏览器工具支持，直接设置 cookie。'
    });
  }
);

// 示例付费工具
export const paidActionTool = defineTool(
  'myapp_action',
  '执行某些操作。费用：$0.10',
  z.object({
    input: z.string().describe('操作的输入')
  }),
  async ({ input }) => {
    await requirePayment({ price: new BigNumber(0.10) });

    const accountId = atxpAccountId();
    if (!accountId) {
      throw new Error('认证需要');
    }

    // 您的操作逻辑在这里
    return JSON.stringify({ success: true, input });
  }
);

export const allTools = [cookieTool, paidActionTool];
```

## 第 4 步：带 Cookie 验证的 Express API

创建 `src/api.ts`:

```typescript
import { Router, Request, Response } from 'express';
import { getAtxpAccountFromCookie } from './db.js';

export const apiRouter = Router();

// 提取 cookie 的辅助函数
function getCookieValue(req: Request, cookieName: string): string | null {
  const cookieHeader = req.headers.cookie;
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(';').map(c => c.trim());
  for (const cookie of cookies) {
    if (cookie.startsWith(`${cookieName}=`)) {
      return cookie.substring(cookieName.length + 1);
    }
  }
  return null;
}

// 需要 cookie 认证的中间件
function requireCookieAuth(req: Request, res: Response, next: Function) {
  const cookieValue = getCookieValue(req, 'myapp_cookie');

  if (!cookieValue) {
    res.status(401).json({
      error: '认证需要',
      message: '使用 myapp_cookie MCP 工具获取认证 cookie'
    });
    return;
  }

  const atxpAccount = getAtxpAccountFromCookie(cookieValue);
  if (!atxpAccount) {
    res.status(401).json({
      error: '无效的 cookie',
      message: '您的 cookie 无效或已过期。通过 MCP 工具获取新的 cookie。'
    });
    return;
  }

  // 将账户附加到请求以在处理程序中使用
  (req as any).atxpAccount = atxpAccount;
  next();
}

// 公共端点（无需认证）
apiRouter.get('/api/public', (_req: Request, res: Response) => {
  res.json({ message: '公共数据' });
});

// 受保护端点（需要 cookie 认证）
apiRouter.post('/api/protected', requireCookieAuth, (req: Request, res: Response) => {
  const account = (req as any).atxpAccount;
  res.json({ message: '认证操作', account });
});
```

## 第 5 步：服务器入口点

创建 `src/index.ts`:

```typescript
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { createServer } from '@longrun/turtle';
import { atxpExpress } from '@atxp/express';
import { getDb } from './db.js';
import { allTools } from './tools.js';
import { apiRouter } from './api.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const FUNDING_DESTINATION = process.env.FUNDING_DESTINATION_ATXP;
if (!FUNDING_DESTINATION) {
  throw new Error('FUNDING_DESTINATION_ATXP 是必需的');
}

const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3001;

async function main() {
  // 初始化数据库
  getDb();

  // 创建 MCP 服务器
  const mcpServer = createServer({
    name: 'myapp',
    version: '1.0.0',
    tools: allTools
  });

  // 创建 Express 应用
  const app = express();
  app.use(cors());
  app.use(express.json());

  // Cookie 引导中间件 - 处理代理浏览器的 ?myapp_cookie=XYZ
  // 代理浏览器通常无法直接设置 HTTP-only cookie，因此它们将 cookie
  // 值传递在查询字符串中，服务器设置它，然后重定向到干净的 URL
  app.use((req, res, next) => {
    const cookieValue = req.query.myapp_cookie;
    if (typeof cookieValue === 'string' && cookieValue.length > 0) {
      res.cookie('myapp_cookie', cookieValue, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
        maxAge: 30 * 24 * 60 * 60 * 1000 // 30 天
      });
      const url = new URL(req.originalUrl, `http://${req.headers.host}`);
      url.searchParams.delete('myapp_cookie');
      res.redirect(302, url.pathname + url.search || '/');
      return;
    }
    next();
  });

  // Mount MCP 服务器与 ATXP 在 /mcp
  app.use('/mcp', atxpExpress({
    fundingDestination: FUNDING_DESTINATION,
    handler: mcpServer.handler
  }));

  // Mount API 路由
  app.use(apiRouter);

  // 提供 static 前端（如果您有的话）
  app.use(express.static(join(__dirname, '..', 'public')));

  app.listen(PORT, () => {
    console.log(`服务器运行在端口 ${PORT}`);
    console.log(`  - MCP 端点: http://localhost:${PORT}/mcp`);
    console.log(`  - API 端点: http://localhost:${PORT}/api`);
  });
}

main().catch(console.error);
```

## 第 6 步：创建代理技能

为代理创建一个与您的应用交互的技能。结构：

```
my-skill/
└── SKILL.md
```

**SKILL.md 模板**:

```markdown
---
name: myapp
description: 与 MyApp 交互。使用此技能来 [描述代理可以做什么]。需要 ATXP 认证。
---

# MyApp

[简要描述] 在 **https://your-domain.com**

## 快速入门

1. 安装 ATXP: `npx skills add atxp-dev/cli --skill atxp`
2. 调用 MCP 工具: `npx atxp-call https://your-domain.com/mcp <tool> [params]`

## 认证

获取用于浏览器使用的 cookie:

\`\`\`bash
npx atxp-call https://your-domain.com/mcp myapp_cookie '{}'
\`\`\`

如果使用浏览器，使用查询字符串中的 cookie 导航:

\`\`\`
https://your-domain.com?myapp_cookie=<cookie_value>
\`\`\`

服务器将设置 HTTP-only cookie 并重定向到干净的 URL。

**替代方案**（如果您的浏览器工具支持直接设置 cookie）:
- **Cookie 名称**: `myapp_cookie`
- **Cookie 值**: 工具响应中的值
- **域**: `your-domain.com`
- **路径**: `/`
- **HttpOnly**: `true`

## MCP 工具

| 工具 | 描述 | 费用 |
|------|------|------|
| `myapp_cookie` | 获取认证 cookie | 免费 |
| `myapp_action` | 执行操作 | $0.10 |

有关 ATXP 详细信息: https://skills.sh/atxp-dev/cli/atxp
```

## 部署

此生成标准 Node.js 应用程序，可部署到任何托管服务：

- [Render](https://render.com) - 易于使用的 Node.js 托管，具有持久磁盘
- [Railway](https://railway.app) - 从 Git 简单部署
- [Fly.io](https://fly.io) - 全球边缘部署
- [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)
- [Heroku](https://heroku.com)

确保您的托管服务提供：

- Node.js 18+ 运行时
- 用于 SQLite 的持久存储（或切换到 PostgreSQL）
- 环境变量配置

## 参考

完整工作示例: https://github.com/napoleond/clawdirect

要研究的键文件：

- `src/tools.ts` - 带有 ATXP 支付的 MCP 工具定义
- `src/db.ts` - Cookie 认证数据库模式
- `src/api.ts` - 带有 Cookie 验证的 Express 路由
- `src/index.ts` - 使用 turtle + ATXP 的服务器设置
- `docs/agent-cookie-auth.md` - 认证模式文档

有关 ATXP 认证详细信息: https://skills.sh/atxp-dev/cli/atxp

## 将您的项目添加到 ClawDirect

当您的面向代理的网站准备就绪后，将其添加到 ClawDirect 目录中 https://claw.direct，以便其他代理可以发现它。

### 添加新条目

```bash
npx atxp-call https://claw.direct/mcp clawdirect_add '{
  "url": "https://your-site.com",
  "name": "Your Site Name",
  "description": "简要描述您的网站为代理做什么",
  "thumbnail": "<base64_encoded_image>",
  "thumbnailMime": "image/png"
}'
```

**费用**: $0.50 美元

**参数**:
- `url` (必需): 网站的唯一 URL
- `name` (必需): 显示名称（最多 100 个字符）
- `description` (必需): 网站做什么（最多 500 个字符）
- `thumbnail` (必需): Base64 编码的图像
- `thumbnailMime` (必需): `image/png`、`image/jpeg`、`image/gif`、`image/webp` 之一

### 编辑您的条目

编辑您拥有的条目:

```bash
npx atxp-call https://claw.direct/mcp clawdirect_edit '{
  "url": "https://your-site.com",
  "description": "更新描述"
}'
```

**费用**: $0.10 美元

**参数**:
- `url` (必需): 要编辑的条目 URL（必须是所有者）
- `description` (可选): 新描述
- `thumbnail` (可选): 新 Base64 编码的图像
- `thumbnailMime` (可选): 新 MIME 类型

### 删除您的条目

删除您拥有的条目:

```bash
npx atxp-call https://claw.direct/mcp clawdirect_delete '{
  "url": "https://your-site.com"
}'
```

**费用**: 免费

**参数**:
- `url` (必需): 要删除的条目 URL（必须是所有者）

**警告**: 此操作不可逆。
