# Vite Flare 快速启动

克隆并配置包含所有功能的 Cloudflare 快速启动模板为一个独立项目。生成一个完全重新品牌化、可部署的全栈应用程序。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React, Vite, Tailwind CSS, shadcn/ui | 19, 6.x, v4, 最新版 |
| 后端 | Hono (基于 Cloudflare Workers) | 4.x |
| 数据库 | D1 (边缘 SQLite) + Drizzle ORM | 0.38+ |
| 认证 | better-auth (Google OAuth + 邮箱/密码) | 最新版 |
| 存储 | R2 (S3 兼容对象存储) | — |
| AI | Workers AI 绑定 | — |
| 数据获取 | TanStack Query | v5 |

### Cloudflare 绑定

| 绑定 | 类型 | 目的 |
|------|------|------|
| `DB` | D1 数据库 | 主要应用程序数据库 |
| `AVATARS` | R2 Bucket | 用户头像存储 |
| `FILES` | R2 Bucket | 一般文件上传 |
| `AI` | Workers AI | AI 模型推理 |

### 项目结构

```
src/
├── client/                 # React 前端
│   ├── components/         # UI 组件
│   ├── hooks/              # 自定义钩子 + TanStack Query
│   ├── pages/              # 路由页面
│   ├── lib/                # 工具 (认证客户端等)
│   └── main.tsx            # 应用程序入口
├── server/                 # Hono 后端
│   ├── index.ts            # Worker 入口
│   ├── routes/             # API 路由
│   ├── middleware/          # 认证、CORS 等
│   └── db/                 # Drizzle 模式 + 查询
└── shared/                 # 客户端/服务器之间共享的类型
```

### 关键命令

| 命令 | 目的 |
|------|------|
| `pnpm dev` | 启动本地开发服务器 |
| `pnpm build` | 生产构建 |
| `pnpm deploy` | 部署到 Cloudflare |
| `pnpm db:migrate:local` | 本地应用迁移 |
| `pnpm db:migrate:remote` | 生产环境应用迁移 |
| `pnpm db:generate` | 根据模式变更生成迁移 |

## 工作流程

### 第 1 步：收集项目信息

收集以下信息：

| 必填 | 可选 |
|------|------|
| 项目名称 (kebab-case) | 管理员邮箱 |
| 描述 (一句话) | Google OAuth 凭证 |
| Cloudflare 账户 | 自定义域名 |

### 第 2 步：克隆和配置

#### 2a. 克隆和清理

```bash
git clone https://github.com/jezweb/vite-flare-starter.git PROJECT_DIR --depth 1
cd PROJECT_DIR
rm -rf .git
git init
```

#### 2b. 查找替换目标

在这些位置将 `vite-flare-starter` 替换为项目名称：

| 文件 | 目标 | 替换为 |
|------|------|-------|
| `wrangler.jsonc` | `"vite-flare-starter"` (worker 名称) | `"PROJECT_NAME"` |
| `wrangler.jsonc` | `vite-flare-starter-db` | `PROJECT_NAME-db` |
| `wrangler.jsonc` | `vite-flare-starter-avatars` | `PROJECT_NAME-avatars` |
| `wrangler.jsonc` | `vite-flare-starter-files` | `PROJECT_NAME-files` |
| `package.json` | `"name": "vite-flare-starter"` | `"name": "PROJECT_NAME"` |
| `package.json` | `vite-flare-starter-db` | `PROJECT_NAME-db` |
| `index.html` | `<title>` 内容 | 应用程序显示名称 (Title Case) |

在 `wrangler.jsonc` 中：
- **移除**硬编码的 `account_id` 行 (让 wrangler 提示或使用环境变量)
- **替换** `database_id` 值为 `REPLACE_WITH_YOUR_DATABASE_ID`

将 `package.json` 版本重置为 `"0.1.0"`。

使用编辑工具进行替换 (优于 sed 以避免 macOS/GNU 差异)。

#### 2c. 生成认证密钥

```bash
BETTER_AUTH_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
```

#### 2d. 创建 .dev.vars

将 kebab-case 项目名称转换为 Display `My Cool App`, ID `my_cool_app`。

```
# 本地开发环境变量
# 不要将此文件提交到 Git

# 认证 (better-auth)
BETTER_AUTH_SECRET=<生成的>
BETTER_AUTH_URL=http://localhost:5173

# Google OAuth (可选)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# 邮箱认证控制 (默认禁用)
# ENABLE_EMAIL_LOGIN=true
# ENABLE_EMAIL_SIGNUP=true

# 应用程序配置
APP_NAME=<显示名称>
VITE_APP_NAME=<显示名称>
VITE_APP_ID=<app_id>
VITE_TOKEN_PREFIX=<app_id>_
VITE_GITHUB_URL=
VITE_FOOTER_TEXT=

NODE_ENV=development
```

#### 2e. 创建 Cloudflare 资源 (可选)

```bash
npx wrangler d1 create PROJECT_NAME-db
# 从输出中提取 database_id, 更新 wrangler.jsonc

npx wrangler r2 bucket create PROJECT_NAME-avatars
npx wrangler r2 bucket create PROJECT_NAME-files
```

#### 2f. 安装和迁移

```bash
pnpm install
pnpm run db:migrate:local
```

#### 2g. 初始提交

```bash
git add -A
git commit -m "从 vite-flare-starter 初始提交"
```

### 第 3 步：手动配置

1. **Google OAuth** (如果使用): 前往 Google Cloud Console, 创建 OAuth 2.0 客户端 ID, 添加重定向 URI `http://localhost:5173/api/auth/callback/google`, 复制客户端 ID 和密钥到 `.dev.vars`
2. **Favicon**: 替换 `public/favicon.svg`
3. **CLAUDE.md**: 更新项目描述, 移除 vite-flare-starter 引用
4. **index.html**: 更新 `<title>` 和元描述

### 第 4 步：本地验证

```bash
pnpm dev
```

检查: http://localhost:5173 加载, 显示 YOUR 应用名称, 注册/登录工作 (如果配置了 OAuth)。

### 第 5 步：部署到生产

```bash
# 设置生产密钥
openssl rand -base64 32 | npx wrangler secret put BETTER_AUTH_SECRET
echo "https://PROJECT_NAME.SUBDOMAIN.workers.dev" | npx wrangler secret put BETTER_AUTH_URL
echo "http://localhost:5173,https://PROJECT_NAME.SUBDOMAIN.workers.dev" | npx wrangler secret put TRUSTED_ORIGINS

# 如果使用 Google OAuth
echo "your-client-id" | npx wrangler secret put GOOGLE_CLIENT_ID
echo "your-client-secret" | npx wrangler secret put GOOGLE_CLIENT_SECRET

# 迁移远程数据库
pnpm run db:migrate:remote

# 构建和部署
pnpm run build && pnpm run deploy
```

**关键**: 首次部署后, 更新 BETTER_AUTH_URL 为您的实际 Worker URL。将生产 URL 添加到 Google OAuth 重定向 URI。

## 安全指纹

更改所有这些, 以防止攻击者识别您的网站使用此快速启动模板:

| 位置 | 默认值 | 如何更改 |
|------|--------|----------|
| 页面标题 | "Vite Flare Starter" | `index.html` |
| UI 中的应用名称 | "Vite Flare Starter" | `VITE_APP_NAME` 环境变量 |
| localStorage 键 | `vite-flare-starter-theme` | `VITE_APP_ID` 环境变量 |
| API 令牌 | `vfs_` 前缀 | `VITE_TOKEN_PREFIX` 环境变量 |
| GitHub 链接 | starter 仓库 | `VITE_GITHUB_URL` (设置为空以隐藏) |
| Worker 名称 | `vite-flare-starter` | `wrangler.jsonc` |
| 数据库名称 | `vite-flare-starter-db` | `wrangler.jsonc` |
| R2 Bucket | `vite-flare-starter-*` | `wrangler.jsonc` |

## 环境变量

### 品牌化 (VITE_ 前缀 = 前端可用)

| 变量 | 目的 | 示例 |
|------|------|------|
| `VITE_APP_NAME` | UI 中显示的名称 | "My Cool App" |
| `VITE_APP_ID` | localStorage 前缀, Sentry | "mycoolapp" |
| `VITE_TOKEN_PREFIX` | API 令牌前缀 | "mca_" |
| `VITE_GITHUB_URL` | GitHub 链接 (为空 = 隐藏) | "" |
| `VITE_FOOTER_TEXT` | 页脚版权文本 | "2026 My Company" |
| `APP_NAME` | 服务器端应用名称 | "My Cool App" |

### 认证

| 变量 | 目的 | 备注 |
|------|------|------|
| `BETTER_AUTH_SECRET` | 会话加密 | `openssl rand -hex 32` |
| `BETTER_AUTH_URL` | 认证基础 URL | 必须与实际 URL 完全匹配 |
| `TRUSTED_ORIGINS` | 允许的来源 | 逗号分隔, 包含 localhost + 生产 |
| `GOOGLE_CLIENT_ID` | Google OAuth | 来自 Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | 来自 Google Cloud Console |
| `ENABLE_EMAIL_LOGIN` | 启用邮箱/密码 | "true" 以启用 |
| `ENABLE_EMAIL_SIGNUP` | 启用邮箱注册 | 需要 ENABLE_EMAIL_LOGIN |

### 邮箱 (可选)

| 变量 | 目的 | 备注 |
|------|------|------|
| `EMAIL_FROM` | 发送者地址 | 用于验证/密码重置 |
| `EMAIL_API_KEY` | 邮件服务 API 密钥 | Resend 推荐使用 |

## 常见定制

### 添加新的数据库表
1. 在 `src/server/db/schema.ts` 中添加模式
2. 生成迁移: `pnpm db:generate`
3. 本地应用迁移: `pnpm db:migrate:local`
4. 生产环境应用迁移: `pnpm db:migrate:remote`

### 添加新的 API 路由
1. 在 `src/server/routes/` 中创建路由文件
2. 在 `src/server/index.ts` 中注册
3. 在 `src/client/hooks/` 中添加 TanStack Query 钩子

### 更改认证提供者
编辑 `src/server/auth.ts`: 添加提供者到 `socialProviders`, 添加凭证到 `.dev.vars` 和生产密钥, 更新客户端登录按钮。

### 功能开关
通过环境变量控制功能: `VITE_FEATURE_STYLE_GUIDE=true`, `VITE_FEATURE_COMPONENTS=true`. 在 `src/client/lib/features.ts` 中添加您自己的。

## 故障排除

| 症状 | 原因 | 解决方法 |
|------|------|----------|
| 认证重定向到主页静默无声 | 缺少 TRUSTED_ORIGINS | 设置 TRUSTED_ORIGINS 包含所有有效 URL |
| 部署时显示 "Not authorized" | 错误的 account_id | 从 wrangler.jsonc 中移除 account_id 或设置您的 |
| 数据库 500 错误 | 缺少迁移 | 运行 `pnpm db:migrate:local` 和 `pnpm db:migrate:remote` |
| localStorage 显示 "vite-flare-starter" | 缺少 VITE_APP_ID | 在 .dev.vars 中设置 `VITE_APP_ID=yourapp` |
| 认证在生产环境中失败 | BETTER_AUTH_URL 不匹配 | 必须与实际 Worker URL 完全匹配 (https, 无尾随斜杠) |
| Google 登录时显示 "redirect_uri_mismatch" | OAuth 重定向 URI 缺失 | 将生产 URL 添加到 Google Cloud Console OAuth 重定向 URI |
| 密钥更改没有效果 | 未重新部署 | `wrangler secret put` 不重新部署。运行 `pnpm deploy` 后 |

## 生产部署检查清单

- [ ] `BETTER_AUTH_SECRET` 设置 (不同于开发!)
- [ ] `BETTER_AUTH_URL` 匹配实际 Worker URL
- [ ] `TRUSTED_ORIGINS` 包含所有有效 URL
- [ ] Google OAuth 重定向 URI 包含生产 URL
- [ ] 远程数据库迁移 (`pnpm db:migrate:remote`)
- [ ] 配置文件中无 `vite-flare-starter` 引用
- [ ] Favicon 已替换
- [ ] CLAUDE.md 已更新
- [ ] `.dev.vars` 未提交 (检查 `.gitignore`)
