---
name: freecodecamp-curriculum
description: 为参与和与freeCodeCamp的开源代码库和课程平台合作提供全面指南
---

# freeCodeCamp 课程与平台开发

> 技能来源：[ara.so](https://ara.so) — 2026每日技能集合。

freeCodeCamp.org 是一个免费、开源的学习平台，拥有数千个交互式编程挑战、认证和全栈课程。代码库包含一个 React/TypeScript 前端、Node.js/Fastify 后端，以及基于 YAML/Markdown 的课程系统。

---

## 架构概述

```
freeCodeCamp/
├── api/                   # Fastify API 服务器 (TypeScript)
├── client/                # Gatsby/React 前端 (TypeScript)
├── curriculum/            # 所有挑战和认证 (YAML/Markdown)
│   └── challenges/
│       ├── english/
│       │   ├── responsive-web-design/
│       │   ├── javascript-algorithms-and-data-structures/
│       │   └── ...
│       └── ...
├── tools/
│   ├── challenge-helper-scripts/  # 课程创作的 CLI 工具
│   └── ui-components/             # 共享的 React 组件
├── config/                # 共享配置
└── e2e/                   # Playwright 端到端测试
```

---

## 本地开发环境设置

### 前置条件

- Node.js 20+ (使用 `nvm` 或 `fnm`)
- pnpm 9+
- MongoDB (本地或 Atlas)
- GitHub 账户 (用于 OAuth)

### 1. 分支并克隆

```bash
git clone https://github.com/<YOUR_USERNAME>/freeCodeCamp.git
cd freeCodeCamp
```

### 2. 安装依赖

```bash
pnpm install
```

### 3. 配置环境

```bash
cp sample.env .env
```

需要设置的 `.env` 变量：

```bash
# MongoDB
MONGOHQ_URL=mongodb://127.0.0.1:27017/freecodecamp

# GitHub OAuth (在 github.com/settings/developers 创建)
GITHUB_ID=$GITHUB_OAUTH_CLIENT_ID
GITHUB_SECRET=$GITHUB_OAUTH_CLIENT_SECRET

# 认证
JWT_SECRET=$YOUR_JWT_SECRET
SESSION_SECRET=$YOUR_SESSION_SECRET

# 邮件 (本地开发可选)
SENDGRID_API_KEY=$SENDGRID_API_KEY
```

### 4. 种子数据库

```bash
pnpm run seed
```

### 5. 启动开发服务器

```bash
# 启动所有服务 (API + Client)
pnpm run develop

# 或单独启动：
pnpm run develop:api      # Fastify API 在 :3000
pnpm run develop:client   # Gatsby 在 :8000
```

---

## 课程挑战结构

挑战存储在 `curriculum/challenges/` 下的 YAML/Markdown 文件中。

### 挑战文件格式

```yaml
# curriculum/challenges/english/02-javascript-algorithms-and-data-structures/basic-javascript/comment-your-javascript-code.md

---
id: bd7123c8c441eddfaeb5bdef  # 唯一的 MongoDB ObjectId 风格字符串
title: Comment Your JavaScript Code
challengeType: 1              # 1=JS, 0=HTML, 2=JSX, 3=Vanilla JS, 5=项目, 7=视频
forumTopicId: 16783
dashedName: comment-your-javascript-code
---

# --description--

注释是 JavaScript 会故意忽略的代码行。

```js
// 这是一个行内注释。
/* 这是一个多行注释 */
```

# --instructions--

尝试创建每种类型的注释。

# --hints--

hint 1

```js
assert(code.match(/(\/\/)/).length > 0);
```

hint 2

```js
assert(code.match(/(\/\*[\s\S]+?\*\/)/).length > 0);
```

# --seed--

## --seed-contents--

```js
// 您的起始代码
```

# --solutions--

```js
// 行内注释
/* 多行
   注释 */
```
```

### 挑战类型

| 类型 | 值 | 描述 |
|------|-------|-------------|
| HTML | 0 | HTML/CSS 挑战 |
| JavaScript | 1 | JS 算法挑战 |
| JSX | 2 | React 组件挑战 |
| Vanilla JS | 3 | DOM 操作 |
| Python | 7 | Python 挑战 |
| 项目 | 5 | 认证项目 |
| 视频 | 11 | 基于视频的课程 |

---

## 创建新挑战

### 使用辅助脚本

```bash
# 交互式创建新挑战
pnpm run create-challenge

# 或直接使用辅助脚本
cd tools/challenge-helper-scripts
pnpm run create-challenge --superblock responsive-web-design --block css-flexbox
```

### 手动创建

1. 在 `curriculum/challenges/english/` 下找到正确的目录
2. 创建一个带有唯一 ID 的新 `.md` 文件

```bash
# 生成一个唯一的挑战 ID
node -e "const {ObjectID} = require('mongodb'); console.log(new ObjectID().toString())"
```

3. 遵循上述挑战文件格式

### 验证您的挑战

```bash
# Lint 和验证所有课程文件
pnpm run test:curriculum

# 测试特定挑战
pnpm run test:curriculum -- --challenge <challenge-id>

# 测试特定模块
pnpm run test:curriculum -- --block basic-javascript
```

---

## 编写挑战测试

测试使用自定义断言库。在 `# --hints--` 块中：

### JavaScript 挑战

```markdown
# --hints--

`myVariable` 应使用 `let` 声明。

```js
assert.match(code, /let\s+myVariable/);
```

当传入 `42` 时，函数应返回 `true`。

```js
assert.strictEqual(myFunction(42), true);
```

DOM 应包含一个 id 为 `main` 的元素。

```js
const el = document.getElementById('main');
assert.exists(el);
```
```

### 可用的测试工具

```js
// DOM 访问 (用于 HTML 挑战)
document.querySelector('#my-id')
document.getElementById('test')

// 代码检查
assert.match(code, /regex/);          // 原始源代码字符串
assert.include(code, 'someString');

// 值断言 (Chai 风格)
assert.strictEqual(actual, expected);
assert.isTrue(value);
assert.exists(value);
assert.approximately(actual, expected, delta);

// 对于异步挑战
// 使用 __helpers 对象
const result = await fetch('/api/test');
assert.strictEqual(result.status, 200);
```

---

## API 开发 (Fastify)

### 路由结构

```typescript
// api/src/routes/example.ts
import { type FastifyPluginCallbackTypebox } from '../helpers/plugin-callback-typebox';
import { Type } from '@fastify/type-provider-typebox';

export const exampleRoutes: FastifyPluginCallbackTypebox = (
  fastify,
  _options,
  done
) => {
  fastify.get(
    '/example/:id',
    {
      schema: {
        params: Type.Object({
          id: Type.String()
        }),
        response: {
          200: Type.Object({
            data: Type.String()
          })
        }
      }
    },
    async (req, reply) => {
      const { id } = req.params;
      return reply.send({ data: `Result for ${id}` });
    }
  );

  done();
};
```

### 添加新 API 路由

```typescript
// api/src/app.ts - 注册插件
import { exampleRoutes } from './routes/example';

await fastify.register(exampleRoutes, { prefix: '/api' });
```

### 数据库访问 (Mongoose)

```typescript
// api/src/schemas/user.ts
import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  completedChallenges: [
    {
      id: String,
      completedDate: Number,
      solution: String
    }
  ]
});

export const User = mongoose.model('User', userSchema);
```

---

## 客户端 (Gatsby/React) 开发

### 添加新页面

```tsx
// client/src/pages/my-new-page.tsx
import React from 'react';
import { Helmet } from 'react-helmet';
import { useTranslation } from 'react-i18next';

const MyNewPage = (): JSX.Element => {
  const { t } = useTranslation();

  return (
    <>
      <Helmet>
        <title>{t('page-title.my-new-page')} | freeCodeCamp.org</title>
      </Helmet>
      <main>
        <h1>{t('headings.my-new-page')}</h1>
      </main>
    </>
  );
};

export default MyNewPage;
```

### 使用 Redux 存储

```tsx
// client/src/redux/selectors.ts pattern
import { createSelector } from 'reselect';
import { RootState } from './types';

export const userSelector = (state: RootState) => state.app.user;

export const completedChallengesSelector = createSelector(
  userSelector,
  user => user?.completedChallenges ?? []
);
```

```tsx
// 在组件中
import { useAppSelector } from '../redux/hooks';
import { completedChallengesSelector } from '../redux/selectors';

const MyComponent = () => {
  const completedChallenges = useAppSelector(completedChallengesSelector);
  return <div>{completedChallenges.length} 挑战已完成</div>;
};
```

### i18n 翻译

```tsx
// 向 client/i18n/locales/english/translations.json 添加键
{
  "my-component": {
    "title": "我的标题",
    "description": "我的描述，包含 {{variable}}"
  }
}

// 在组件中使用
const { t } = useTranslation();
t('my-component.title');
t('my-component.description', { variable: 'value' });
```

---

## 测试

### 单元测试 (Jest)

```bash
# 运行所有单元测试
pnpm test

# 运行特定包的测试
pnpm --filter api test
pnpm --filter client test

# 监视模式
pnpm --filter client test -- --watch
```

### 课程测试

```bash
# 验证所有挑战
pnpm run test:curriculum

# 验证特定超级块
pnpm run test:curriculum -- --superblock javascript-algorithms-and-data-structures

# Lint 挑战 Markdown
pnpm run lint:curriculum
```

### E2E 测试 (Playwright)

```bash
# 运行所有 E2E 测试
pnpm run test:e2e

# 运行特定测试文件
pnpm run test:e2e -- e2e/learn.spec.ts

# 带界面运行
pnpm run test:e2e -- --ui
```

### 编写 E2E 测试

```typescript
// e2e/my-feature.spec.ts
import { test, expect } from '@playwright/test';

test('用户可以完成挑战', async ({ page }) => {
  await page.goto('/learn/javascript-algorithms-and-data-structures/basic-javascript/comment-your-javascript-code');

  // 填写代码编辑器
  await page.locator('.monaco-editor').click();
  await page.keyboard.type('// 行内注释\n/* 块注释 */');

  // 运行测试
  await page.getByRole('button', { name: /run the tests/i }).click();

  // 检查结果
  await expect(page.getByText('Tests Passed')).toBeVisible();
});
```

---

## 主要 pnpm 脚本参考

```bash
# 开发
pnpm run develop              # 启动所有服务
pnpm run develop:api          # 仅 API
pnpm run develop:client       # 仅客户端

# 构建
pnpm run build                # 构建所有内容
pnpm run build:api            # 构建 API
pnpm run build:client         # 构建客户端 (Gatsby)

# 测试
pnpm test                     # 单元测试
pnpm run test:curriculum      # 验证课程
pnpm run test:e2e             # Playwright E2E

# Lint
pnpm run lint                 # ESLint 所有包
pnpm run lint:curriculum      # 课程 Markdown Lint

# 数据库
pnpm run seed                 # 用课程数据填充数据库
pnpm run seed:certified-user  # 填充测试认证用户

# 工具
pnpm run create-challenge     # 交互式挑战创建器
pnpm run clean                # 清理构建产物
```

---

## 超级块和模块命名规范

超级块映射到认证。目录名称使用连字符命名法：

```
responsive-web-design/
javascript-algorithms-and-data-structures/
front-end-development-libraries/
data-visualization/
relational-database/
back-end-development-and-apis/
quality-assurance/
scientific-computing-with-python/
data-analysis-with-python/
machine-learning-with-python/
coding-interview-prep/
the-odin-project/
project-euler/
```

超级块内的模块目录：

```
responsive-web-design/
├── basic-html-and-html5/
├── basic-css/
├── applied-visual-design/
├── css-flexbox/
└── css-grid/
```

---

## 常见模式与注意事项

### 挑战 ID 生成

每个挑战需要一个唯一的 24 字符十六进制 ID：

```typescript
// tools/challenge-helper-scripts/helpers/id-gen.ts
import { ObjectId } from 'bson';
export const generateId = (): string => new ObjectId().toHexString();
```

### 添加论坛链接

每个挑战需要一个 `forumTopicId` 链接到 forum.freecodecamp.org：

```yaml
forumTopicId: 301090  # 必须是真实的论坛帖子 ID
```

### 课程元文件

每个模块需要一个 `_meta.json`：

```json
{
  "name": "Basic JavaScript",
  "dashedName": "basic-javascript",
  "order": 0,
  "time": "5 小时",
  "template": "",
  "required": [],
  "isUpcomingChange": false,
  "isBeta": false,
  "isLocked": false,
  "isPrivate": false
}
```

### 使用认证进行测试

```typescript
// 在 E2E 测试中，使用测试用户固定装置
import { authedUser } from './fixtures/authed-user';

test.use({ storageState: 'playwright/.auth/user.json' });

test('认证操作', async ({ page }) => {
  // page 已经登录
  await page.goto('/settings');
  await expect(page.getByText('Account Settings')).toBeVisible();
});
```

---

## 故障排除

### MongoDB 连接问题

```bash
# 检查 MongoDB 是否运行
mongosh --eval "db.adminCommand('ping')"

# 启动 MongoDB (macOS 使用 Homebrew)
brew services start mongodb-community

# 使用内存 MongoDB 进行测试
MONGOHQ_URL=mongodb://127.0.0.1:27017/freecodecamp-test pnpm test
```

### 端口冲突

```bash
# API 在 3000，客户端在 8000
lsof -i :3000
kill -9 <PID>
```

### 课程验证失败

```bash
# 查看详细错误输出
pnpm run test:curriculum -- --verbose

# 常见问题：
# - 缺少 forumTopicId
# - 重复的挑战 ID
# - 无效的 challengeType
# - 格式错误的 YAML 前置
```

### Node/pnpm 版本不匹配

```bash
# 使用项目要求的版本
node --version   # 应匹配 .nvmrc
pnpm --version   # 应匹配 package.json 中的 packageManager

nvm use          # 切换到正确的 Node 版本
```

### 客户端构建错误

```bash
# 清除 Gatsby 缓存
pnpm --filter client run clean
pnpm run develop:client
```

---

## 贡献工作流

```bash
# 1. 创建功能分支
git checkout -b fix/challenge-typo-in-basic-js

# 2. 进行更改并测试
pnpm run test:curriculum
pnpm test

# 3. Lint
pnpm run lint

# 4. 使用常规提交提交
git commit -m "fix(curriculum): basic-javascript 挑战中的拼写错误"

# 5. 推送并打开对 main 的 PR
git push origin fix/challenge-typo-in-basic-js
```

提交消息前缀：`fix:`, `feat:`, `chore:`, `docs:`, `refactor:`, `test:`

---

## 资源

- 贡献指南：https://contribute.freecodecamp.org
- 论坛：https://forum.freecodecamp.org
- Discord：https://discord.gg/PRyKn3Vbay
- 如何报告错误：https://forum.freecodecamp.org/t/how-to-report-a-bug/19543
