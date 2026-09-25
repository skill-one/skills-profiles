# Appwrite TypeScript SDK

## 安装

```bash
# Web
npm install appwrite

# React Native
npm install react-native-appwrite

# Node.js / Deno
npm install node-appwrite
```

## 设置客户端

### 客户端端（Web / React Native）

```typescript
// Web
import { Client, Account, TablesDB, Storage, ID, Query } from 'appwrite';

// React Native
import { Client, Account, TablesDB, Storage, ID, Query } from 'react-native-appwrite';

const client = new Client()
    .setEndpoint('https://<REGION>.cloud.appwrite.io/v1')
    .setProject('[PROJECT_ID]');
```

### 服务器端（Node.js / Deno）

```typescript
import { Client, Users, TablesDB, Storage, Functions, ID, Query } from 'node-appwrite';

const client = new Client()
    .setEndpoint('https://<REGION>.cloud.appwrite.io/v1')
    .setProject(process.env.APPWRITE_PROJECT_ID)
    .setKey(process.env.APPWRITE_API_KEY);
```

## 代码示例

### 认证（客户端端）

```typescript
const account = new Account(client);

// 邮箱注册
await account.create({
    userId: ID.unique(),
    email: 'user@example.com',
    password: 'password123',
    name: 'User Name'
});

// 邮箱登录
const session = await account.createEmailPasswordSession({
    email: 'user@example.com',
    password: 'password123'
});

// OAuth 登录（Web）
account.createOAuth2Session({
    provider: OAuthProvider.Github,
    success: 'https://example.com/success',
    failure: 'https://example.com/fail',
    scopes: ['repo', 'user'] // 可选 — 提供商特定范围
});

// 获取当前用户
const user = await account.get();

// 退出登录
await account.deleteSession({ sessionId: 'current' });
```

### OAuth 2 登录（React Native）

> **重要提示：** `createOAuth2Session()` 在 React Native 上**不起作用**。您必须使用 `createOAuth2Token()` 和深度链接代替。

#### 设置

安装所需的依赖项：

```bash
npx expo install react-native-appwrite react-native-url-polyfill
npm install expo-auth-session expo-web-browser expo-linking
```

在您的 `app.json` 中设置 URL 方案：

```json
{
  "expo": {
    "scheme": "appwrite-callback-[PROJECT_ID]"
  }
}
```

#### OAuth 流程

```typescript
import { Client, Account, OAuthProvider } from 'react-native-appwrite';
import { makeRedirectUri } from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';

const client = new Client()
    .setEndpoint('https://<REGION>.cloud.appwrite.io/v1')
    .setProject('[PROJECT_ID]');

const account = new Account(client);

async function oauthLogin(provider: OAuthProvider) {
    // 创建跨 Expo 环境工作的深度链接
    const deepLink = new URL(makeRedirectUri({ preferLocalhost: true }));
    const scheme = `${deepLink.protocol}//`; // 例如 'exp://' 或 'appwrite-callback-[PROJECT_ID]://''

    // 获取 OAuth 登录 URL
    const loginUrl = await account.createOAuth2Token({
        provider,
        success: `${deepLink}`,
        failure: `${deepLink}`,
    });

    // 打开浏览器并监听方案重定向
    const result = await WebBrowser.openAuthSessionAsync(`${loginUrl}`, scheme);

    if (result.type !== 'success') return;

    // 从重定向 URL 中提取凭据
    const url = new URL(result.url);
    const secret = url.searchParams.get('secret');
    const userId = url.searchParams.get('userId');

    // 使用 OAuth 凭据创建会话
    await account.createSession({ userId, secret });
}

// 使用示例
await oauthLogin(OAuthProvider.Github);
await oauthLogin(OAuthProvider.Google);
```

### 用户管理（服务器端）

```typescript
const users = new Users(client);

// 创建用户
const user = await users.create({
    userId: ID.unique(),
    email: 'user@example.com',
    password: 'password123',
    name: 'User Name'
});

// 列出用户
const list = await users.list({ queries: [Query.limit(25)] });

// 获取用户
const fetched = await users.get({ userId: '[USER_ID]' });

// 删除用户
await users.delete({ userId: '[USER_ID]' });
```

### 数据库操作

> **注意：** 对于所有新代码，请使用 `TablesDB`（而不是已弃用的 `Databases` 类）。只有当现有代码库依赖于它或用户明确要求时，才使用 `Databases`。
>
> **提示：** 对于所有 SDK 方法调用，请优先使用对象参数调用样式（例如，`{ databaseId: '...' }`）。如果现有代码库已经使用它们或用户明确要求，才使用位置参数。

```typescript
const tablesDB = new TablesDB(client);

// 创建数据库（仅限服务器端）
const db = await tablesDB.create({ databaseId: ID.unique(), name: 'My Database' });

// 创建表（仅限服务器端）
const col = await tablesDB.createTable({
    databaseId: '[DATABASE_ID]',
    tableId: ID.unique(),
    name: 'My Table'
});

// 创建行
const doc = await tablesDB.createRow({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    rowId: ID.unique(),
    data: { title: 'Hello World', content: 'Example content' }
});

// 使用查询列出行
const results = await tablesDB.listRows({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    queries: [Query.equal('status', 'active'), Query.limit(10)]
});

// 获取行
const row = await tablesDB.getRow({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    rowId: '[ROW_ID]'
});

// 更新行
await tablesDB.updateRow({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    rowId: '[ROW_ID]',
    data: { title: 'Updated Title' }
});

// 删除行
await tablesDB.deleteRow({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    rowId: '[ROW_ID]'
});
```

#### 字符串列类型

> **注意：** 遗留的 `string` 类型已弃用。对于所有新列，请使用显式列类型。

| 类型 | 最大字符数 | 索引 | 存储 |
|------|------------|------|------|
| `varchar` | 16,383 | 完全索引（如果大小 ≤ 768） | 行内存储 |
| `text` | 16,383 | 前缀索引 | 离线存储 |
| `mediumtext` | 4,194,303 | 前缀索引 | 离线存储 |
| `longtext` | 1,073,741,823 | 前缀索引 | 离线存储 |

- `varchar` 存储在行内，并计入 64 KB 行大小限制。对于短、索引字段（如名称、缩写或标识符）优先使用。
- `text`、`mediumtext` 和 `longtext` 存储在离线（行中只有 20 字节的指针），因此它们不会消耗行大小预算。`size` 对于这些类型不是必需的。

```typescript
// 创建具有显式字符串列类型的表
await tablesDB.createTable({
    databaseId: '[DATABASE_ID]',
    tableId: ID.unique(),
    name: 'articles',
    columns: [
        { key: 'title',    type: 'varchar',    size: 255, required: true  },  // 行内，完全可索引
        { key: 'summary',  type: 'text',                  required: false },  // 离线，仅前缀索引
        { key: 'body',     type: 'mediumtext',            required: false },  // 最高约 ~4 MB 字符
        { key: 'raw_data', type: 'longtext',              required: false },  // 最高约 ~1 GB 字符
    ]
});
```

#### TypeScript 泛型

```typescript
import { Models } from 'appwrite';
// 服务器端：从 'node-appwrite' 导入

// 定义您的行数据的类型化接口
interface Todo {
    title: string;
    done: boolean;
    priority: number;
}

// listRows 默认返回 Models.DocumentList<Models.Document>
// 强制转换或使用泛型以获得类型化结果
const results = await tablesDB.listRows({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    queries: [Query.equal('done', false)]
});

// 每个文档都包含内置字段以及您的数据
const doc = results.documents[0];
doc.$id;            // string — 唯一行 ID
doc.$createdAt;     // string — ISO 8601 创建时间戳
doc.$updatedAt;     // string — ISO 8601 更新时间戳
doc.$permissions;   // string[] — 权限字符串
doc.$databaseId;    // string
doc.$collectionId;  // string

// 常用模型类型
// Models.User<Preferences>  — 用户账户
// Models.Session             — 认证会话
// Models.File                — 存储文件元数据
// Models.Team                — 团队对象
// Models.Execution           — 函数执行结果
// Models.DocumentList<T>     — 分页列表，包含总数
```

### 查询方法

```typescript
// 过滤
Query.equal('field', 'value')           // field == value（或传递数组用于 IN）
Query.notEqual('field', 'value')        // field != value
Query.lessThan('field', 100)            // field < value
Query.lessThanEqual('field', 100)       // field <= value
Query.greaterThan('field', 100)         // field > value
Query.greaterThanEqual('field', 100)    // field >= value
Query.between('field', 1, 100)          // 1 <= field <= 100
Query.isNull('field')                   // field 为 null
Query.isNotNull('field')                // field 不为 null
Query.startsWith('field', 'prefix')     // 字符串以 prefix 开头
Query.endsWith('field', 'suffix')       // 字符串以 suffix 结尾
Query.contains('field', 'substring')    // 字符串/数组包含值
Query.search('field', 'keywords')       // 全文搜索（需要全文索引）

// 排序
Query.orderAsc('field')                 // 升序排序
Query.orderDesc('field')                // 降序排序

// 分页
Query.limit(25)                         // 返回的最大行数（默认 25，最大 100）
Query.offset(0)                         // 跳过 N 行
Query.cursorAfter('[ROW_ID]')           // 在此行 ID 后分页（对于大数据集更优）
Query.cursorBefore('[ROW_ID]')          // 在此行 ID 前分页

// 选择
Query.select(['field1', 'field2'])      // 仅返回指定字段

// 逻辑
Query.or([Query.equal('a', 1), Query.equal('b', 2)])   // OR 条件
Query.and([Query.greaterThan('age', 18), Query.lessThan('age', 65)])  // 显式 AND（查询默认为 AND）
```

### 文件存储

```typescript
const storage = new Storage(client);

// 上传文件（客户端端 — 从文件输入）
const file = await storage.createFile({
    bucketId: '[BUCKET_ID]',
    fileId: ID.unique(),
    file: document.getElementById('file-input').files[0]
});

// 上传文件（服务器端 — 从路径）
import { InputFile } from 'node-appwrite/file';

const file2 = await storage.createFile({
    bucketId: '[BUCKET_ID]',
    fileId: ID.unique(),
    file: InputFile.fromPath('/path/to/file.png', 'file.png')
});

// 列出文件
const files = await storage.listFiles({ bucketId: '[BUCKET_ID]' });

// 获取文件预览（图像）
const preview = storage.getFilePreview({
    bucketId: '[BUCKET_ID]',
    fileId: '[FILE_ID]',
    width: 300,
    height: 300
});

// 下载文件
const download = await storage.getFileDownload({
    bucketId: '[BUCKET_ID]',
    fileId: '[FILE_ID]'
});

// 删除文件
await storage.deleteFile({ bucketId: '[BUCKET_ID]', fileId: '[FILE_ID]' });
```

#### InputFile 工厂方法（服务器端）

```typescript
import { InputFile } from 'node-appwrite/file';

InputFile.fromPath('/path/to/file.png', 'file.png')          // 从文件系统路径
InputFile.fromBuffer(buffer, 'file.png')                       // 从 Buffer
InputFile.fromStream(readableStream, 'file.png', size)         // 从 ReadableStream（需要字节数 size）
InputFile.fromPlainText('Hello world', 'hello.txt')            // 从字符串内容
```

### 团队

```typescript
const teams = new Teams(client);

// 创建团队
const team = await teams.create({ teamId: ID.unique(), name: 'Engineering' });

// 列出团队
const list = await teams.list();

// 创建成员资格（通过邮箱邀请用户）
const membership = await teams.createMembership({
    teamId: '[TEAM_ID]',
    roles: ['editor'],
    email: 'user@example.com',
});

// 列出成员资格
const members = await teams.listMemberships({ teamId: '[TEAM_ID]' });

// 更新成员资格角色
await teams.updateMembership({
    teamId: '[TEAM_ID]',
    membershipId: '[MEMBERSHIP_ID]',
    roles: ['admin'],
});

// 删除团队
await teams.delete({ teamId: '[TEAM_ID]' });
```

> **基于角色的访问控制：** 使用 `Role.team('[TEAM_ID]')` 为所有团队成员或 `Role.team('[TEAM_ID]', 'editor')` 为特定团队角色设置权限时。

### 实时订阅（客户端端）

```typescript
import { Realtime, Channel } from 'appwrite';

const realtime = new Realtime(client);

// 订阅行更改
const subscription = await realtime.subscribe(
    Channel.tablesdb('[DATABASE_ID]').table('[TABLE_ID]').row(),
    (response) => {
        console.log(response.events);   // 例如 ['tablesdb.*.tables.*.rows.*.create']
        console.log(response.payload);  // 受影响的资源
    }
);

// 订阅特定行
await realtime.subscribe(
    Channel.tablesdb('[DATABASE_ID]').table('[TABLE_ID]').row('[ROW_ID]'),
    (response) => { /* ... */ }
);

// 订阅多个频道
await realtime.subscribe([
    Channel.tablesdb('[DATABASE_ID]').table('[TABLE_ID]').row(),
    Channel.bucket('[BUCKET_ID]').file(),
], (response) => { /* ... */ });

// 取消订阅
await subscription.close();
```

**可用频道：**

| 频道 | 描述 |
|------|------|
| `account` | 认证用户账户的更改 |
| `tablesdb.[DB_ID].tables.[TABLE_ID].rows` | 表中的所有行 |
| `tablesdb.[DB_ID].tables.[TABLE_ID].rows.[ROW_ID]` | 特定行 |
| `buckets.[BUCKET_ID].files` | 桶中的所有文件 |
| `buckets.[BUCKET_ID].files.[FILE_ID]` | 特定文件 |
| `teams` | 用户所属团队的更改 |
| `teams.[TEAM_ID]` | 特定团队的更改 |
| `memberships` | 用户的团队成员资格更改 |
| `memberships.[MEMBERSHIP_ID]` | 特定成员资格 |
| `functions.[FUNCTION_ID].executions` | 函数执行更新 |

`response` 对象包括：`events`（事件字符串数组）、`payload`（受影响的资源）、`channels`（匹配的频道）和 `timestamp`（ISO 8601）。

### 无服务器函数（服务器端）

```typescript
const functions = new Functions(client);

// 执行函数
const execution = await functions.createExecution({
    functionId: '[FUNCTION_ID]',
    body: JSON.stringify({ key: 'value' })
});

// 列出执行
const executions = await functions.listExecutions({ functionId: '[FUNCTION_ID]' });
```

#### 编写函数处理程序（Node.js 运行时）

当部署您自己的 Appwrite 函数时，入口点文件必须导出一个默认的异步函数：

```typescript
// src/main.js (或 src/main.ts)
export default async ({ req, res, log, error }) => {
    // 请求属性
    // req.body        — 原始请求正文（字符串）
    // req.bodyJson    — 解析的 JSON 正文（对象，如果没有 JSON 则为 undefined）
    // req.headers     — 请求头（对象）
    // req.method      — HTTP 方法（GET、POST、PUT、DELETE、PATCH）
    // req.path        — URL 路径（例如 '/hello'）
    // req.query       — 解析的查询参数（对象）
    // req.queryString — 原始查询字符串

    log('处理请求：' + req.method + ' ' + req.path);

    if (req.method === 'GET') {
        return res.json({ message: '来自 Appwrite 函数的问候！' });
    }

    const data = req.bodyJson;
    if (!data?.name) {
        error('缺少 name 字段');
        return res.json({ error: 'Name is required' }, 400);
    }

    // 响应方法
    return res.json({ success: true });                    // JSON（自动设置 Content-Type）
    // return res.text('Hello');                           // 纯文本
    // return res.empty();                                 // 204 No Content
    // return res.redirect('https://example.com');         // 302 重定向
    // return res.send('data', 200, { 'X-Custom': '1' }); // 自定义正文、状态、头
};
```

### 服务器端渲染（SSR）认证

SSR 应用（Next.js、SvelteKit、Nuxt、Remix、Astro）使用**服务器端 SDK**（`node-appwrite`）处理认证。您需要两个客户端：

- **管理员客户端** — 使用 API 密钥，创建会话，绕过速率限制（可重用的单例）
- **会话客户端** — 使用会话 Cookie，代表用户操作（每个请求创建，永不共享）

```typescript
import { Client, Account, OAuthProvider } from 'node-appwrite';

// 管理员客户端（可重用）
const adminClient = new Client()
    .setEndpoint('https://<REGION>.cloud.appwrite.io/v1')
    .setProject('[PROJECT_ID]')
    .setKey(process.env.APPWRITE_API_KEY);

// 会话客户端（每个请求创建）
const sessionClient = new Client()
    .setEndpoint('https://<REGION>.cloud.appwrite.io/v1')
    .setProject('[PROJECT_ID]');

const session = req.cookies['a_session_[PROJECT_ID]'];
if (session) {
    sessionClient.setSession(session);
}
```

#### 邮箱/密码登录

```typescript
app.post('/login', async (req, res) => {
    const account = new Account(adminClient);
    const session = await account.createEmailPasswordSession({
        email: req.body.email,
        password: req.body.password,
    });

    // Cookie 名称必须为 a_session_<PROJECT_ID>
    res.cookie('a_session_[PROJECT_ID]', session.secret, {
        httpOnly: true,
        secure: true,
        sameSite: 'strict',
        expires: new Date(session.expire),
        path: '/',
    });

    res.json({ success: true });
});
```

#### 认证请求

```typescript
app.get('/user', async (req, res) => {
    const session = req.cookies['a_session_[PROJECT_ID]'];
    if (!session) return res.status(401).json({ error: 'Unauthorized' });

    // 每个请求创建一个新的会话客户端
    const sessionClient = new Client()
        .setEndpoint('https://<REGION>.cloud.appwrite.io/v1')
        .setProject('[PROJECT_ID]')
        .setSession(session);

    const account = new Account(sessionClient);
    const user = await account.get();
    res.json(user);
});
```

#### OAuth2 SSR 流程

```typescript
// 第一步：重定向到 OAuth 提供商
app.get('/oauth', async (req, res) => {
    const account = new Account(adminClient);
    const redirectUrl = await account.createOAuth2Token({
        provider: OAuthProvider.Github,
        success: 'https://example.com/oauth/success',
        failure: 'https://example.com/oauth/failure',
    });
    res.redirect(redirectUrl);
});

// 第二步：处理回调 — 交换令牌以获取会话
app.get('/oauth/success', async (req, res) => {
    const account = new Account(adminClient);
    const session = await account.createSession({
        userId: req.query.userId,
        secret: req.query.secret,
    });

    res.cookie('a_session_[PROJECT_ID]', session.secret, {
        httpOnly: true, secure: true, sameSite: 'strict',
        expires: new Date(session.expire), path: '/',
    });
    res.json({ success: true });
});
```

> **Cookie 安全：** 始终使用 `httpOnly`、`secure` 和 `sameSite: 'strict'` 以防止 XSS。Cookie 名称必须为 `a_session_<PROJECT_ID>`。

> **转发用户代理：** 调用 `sessionClient.setForwardedUserAgent(req.headers['user-agent'])` 以记录最终用户的浏览器信息用于调试和安全。

## 错误处理

```typescript
import { AppwriteException } from 'appwrite';
// 服务器端：从 'node-appwrite' 导入

try {
    const doc = await tablesDB.getRow({
        databaseId: '[DATABASE_ID]',
        tableId: '[TABLE_ID]',
        rowId: '[ROW_ID]',
    });
} catch (err) {
    if (err instanceof AppwriteException) {
        console.log(err.message);   // 人类可读的错误消息
        console.log(err.code);      // HTTP 状态码（数字）
        console.log(err.type);      // Appwrite 错误类型字符串（例如 'document_not_found'）
        console.log(err.response);  // 完整响应正文（对象）
    }
}
```

**常见错误代码：**

| 代码 | 含义 |
|------|------|
| `401` | 未授权 — 缺少或无效会话/API 密钥 |
| `403` | 禁止 — 无权执行此操作 |
| `404` | 未找到 — 资源不存在 |
| `409` | 冲突 — 重复 ID 或唯一约束冲突 |
| `429` | 速率限制 — 请求过多，稍后重试 |

## 权限与角色（关键）

Appwrite 使用权限字符串来控制对资源的访问。每个权限都配对一个操作（`read`、`update`、`delete`、`create` 或 `write` 授予 create + update + delete）与一个角色目标。默认情况下，**没有用户有权访问**，除非在行/文件级别显式设置权限或从表/桶设置继承权限。权限是字符串数组，使用 `Permission` 和 `Role` 辅助程序构建。

```typescript
import { Permission, Role } from 'appwrite';
// 服务器端：从 'node-appwrite' 导入
```

### 数据库行权限

```typescript
const doc = await tablesDB.createRow({
    databaseId: '[DATABASE_ID]',
    tableId: '[TABLE_ID]',
    rowId: ID.unique(),
    data: { title: 'Hello World' },
    permissions: [
        Permission.read(Role.user('[USER_ID]')),     // 特定用户可以读取
        Permission.update(Role.user('[USER_ID]')),   // 特定用户可以更新
        Permission.read(Role.team('[TEAM_ID]')),     // 所有团队成员可以读取
        Permission.read(Role.any()),                 // 任何人（包括访客）可以读取
    ]
});
```

### 文件上传权限

```typescript
const file = await storage.createFile({
    bucketId: '[BUCKET_ID]',
    fileId: ID.unique(),
    file: document.getElementById('file-input').files[0],
    permissions: [
        Permission.read(Role.any()),
        Permission.update(Role.user('[USER_ID]')),
        Permission.delete(Role.user('[USER_ID]')),
    ]
});
```

> **何时设置权限：** 当您需要每个资源的访问控制时设置行/文件权限。如果表中的所有行共享相同的规则，请在表/桶级别配置权限，并将行权限留空。

> **常见错误：**
> - **忘记权限** — 资源对所有用户（包括创建者）都不可访问
> - **`Role.any()` 与 `write`/`update`/`delete`** — 允许任何用户，包括未认证的访客，修改或删除资源
> - **`Permission.read(Role.any())` 在敏感数据上** — 使资源公开可读
