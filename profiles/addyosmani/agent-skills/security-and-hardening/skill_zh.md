# 安全与加固

## 概述

面向 Web 应用的安全优先开发实践。将所有外部输入视为敌意，将所有秘密视为神圣，将所有授权检查视为强制。安全不是一个阶段——它是对接触用户数据、身份验证或外部系统的每一行代码的约束。

## 使用场景

- 构建任何接受用户输入的应用
- 实现身份验证或授权
- 存储或传输敏感数据
- 集成外部 API 或服务
- 添加文件上传、Webhook 或回调
- 处理支付或个人身份信息 (PII) 数据

## 流程：威胁模型优先

没有威胁模型的控制是猜测。在加固之前，花五分钟像攻击者一样思考：

1. **绘制信任边界。** 未受信任的数据在哪里进入您的系统？HTTP 请求、表单字段、文件上传、Webhook、第三方 API、消息队列和 **LLM 输出**——加上看起来是内部的本地值，因为操作系统将它们交给您：另一个进程的命令行或环境、共享卷上的文件名、作业负载中的路径。信任遵循谁 *编写* 了值，而不是哪个通道交付了它。每个边界都是攻击面。
2. **命名资产。** 什么值得窃取或破坏？凭证、PII、支付数据、管理员操作、资金流动。
3. **对每个边界运行 STRIDE** —— 这是一个快速镜头，而不是一个仪式：

| 威胁 | 提问 | 典型缓解措施 |
|---|---|---|
| **S**poofing | 有人能冒充用户/服务吗？ | 身份验证、签名验证 |
| **T**ampering | 数据能在传输或静止时被篡改吗？ | 完整性检查、参数化查询、HTTPS |
| **R**epudiation | 之后能否认操作吗？ | 安全事件审计日志 |
| **I**nformation disclosure | 数据会泄露吗？ | 加密、字段允许列表、通用错误 |
| **D**enial of service | 能被压垮吗？ | 速率限制、输入大小限制、超时 |
| **E**levation of privilege | 用户能获得他们不应有的权限吗？ | 授权检查、最小权限 |

4. **在用例旁边编写滥用案例。** 对于每个功能，问“我会如何滥用这个？”——然后将其作为您的第一个测试。

如果您无法命名一个功能的信任边界，您还没有准备好保护它。这是 OWASP **A04：不安全设计**——大多数漏洞始于设计，而不是代码。

## 三层边界系统

### 总是做（没有例外）

- **在系统边界（API 路由、表单处理程序）验证所有外部输入**
- **参数化所有数据库查询**——永远不要将用户输入连接到 SQL
- **对输出进行编码**以防止跨站脚本攻击 (XSS)（使用框架自动转义，不要绕过它）
- **对所有外部通信使用 HTTPS**
- **使用 bcrypt/scrypt/argon2 哈希密码**（永远不要存储明文）
- **设置安全标头**（CSP、HSTS、X-Frame-Options、X-Content-Type-Options）
- **使用 httpOnly、secure、sameSite cookie 进行会话**
- **在每次发布之前，使用检测到的包管理器的原生审计针对提交的锁文件运行**

### 需要先询问（需要人工批准）

- 添加新的身份验证流程或更改身份验证逻辑
- 存储新的敏感数据类别（PII、支付信息）
- 添加新的外部服务集成
- 更改 CORS 配置
- 添加文件上传处理程序
- 修改速率限制或限流
- 授予提升权限或角色

### 永远不要做

- **永远不要将秘密提交到版本控制**（API 密钥、密码、令牌）
- **永远不要记录敏感数据**（密码、令牌、完整的信用卡号）
- **永远不要信任客户端验证**作为安全边界
- **永远不要为了方便而禁用安全标头**
- **永远不要使用 `eval()` 或 `innerHTML`** 与用户提供的數據
- **永远不要将会话存储在客户端可访问的存储**（用于身份验证令牌的 localStorage）
- **永远不要向用户暴露堆栈跟踪**或内部错误详细信息

## OWASP Top 10 预防模式

这些是预防模式，而不是排名。有关 2021 年的排序，请参阅 `../../references/security-checklist.md` 中的快速参考表。

### 注入（SQL、NoSQL、操作系统命令）

```typescript
// BAD: 通过字符串连接进行 SQL 注入
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// GOOD: 参数化查询
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// GOOD: 使用 ORM 进行参数化输入
const user = await prisma.user.findUnique({ where: { id: userId } });
```

### 身份验证故障

```typescript
// 密码哈希
import { hash, compare } from 'bcrypt';

const SALT_ROUNDS = 12;
const hashedPassword = await hash(plaintext, SALT_ROUNDS);
const isValid = await compare(plaintext, hashedPassword);

// 会话管理
app.use(session({
  secret: process.env.SESSION_SECRET,  // 来自环境变量，而不是代码
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,     // 无法通过 JavaScript 访问
    secure: true,       // 仅限 HTTPS
    sameSite: 'lax',    // CSRF 保护
    maxAge: 24 * 60 * 60 * 1000,  // 24 小时
  },
}));
```

### 跨站脚本 (XSS)

```typescript
// BAD: 将用户输入作为 HTML 渲染
element.innerHTML = userInput;

// GOOD: 使用框架自动转义（React 默认这样做）
return <div>{userInput}</div>;

// 如果您必须渲染 HTML，请先进行清理
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

### 访问控制故障

```typescript
// 始终检查授权，而不仅仅是身份验证
app.patch('/api/tasks/:id', authenticate, async (req, res) => {
  const task = await taskService.findById(req.params.id);

  // 检查认证用户是否拥有此资源
  if (task.ownerId !== req.user.id) {
    return res.status(403).json({
      error: { code: 'FORBIDDEN', message: '无权修改此任务' }
    });
  }

  // 继续更新
  const updated = await taskService.update(req.params.id, req.body);
  return res.json(updated);
});
```

### 安全配置错误

```typescript
// 安全标头（使用 helmet for Express）
import helmet from 'helmet';
app.use(helmet());

// 内容安全策略
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],  // 如果可能，请收紧
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'"],
  },
}));

// CORS —— 限制为已知来源
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true,
}));
```

### 敏感数据暴露

```typescript
// 永远不要在 API 响应中返回敏感字段
function sanitizeUser(user: UserRecord): PublicUser {
  const { passwordHash, resetToken, ...publicFields } = user;
  return publicFields;
}

// 使用环境变量存储秘密
const API_KEY = process.env.STRIPE_API_KEY;
if (!API_KEY) throw new Error('STRIPE_API_KEY 未配置');
```

### 服务器端请求伪造 (SSRF)

每当服务器获取用户影响的 URL 时——Webhook、“从 URL 导入”、图像代理、链接预览——攻击者可以将其指向内部服务（云元数据、`localhost`、私有 IP）。

```typescript
// BAD: 获取用户给定的任何 URL
await fetch(req.body.webhookUrl);

// GOOD: 允许列表方案 + 主机，如果任何解析 IP 是私有的，则拒绝，禁止重定向
import { lookup } from 'node:dns/promises';
import ipaddr from 'ipaddr.js';

const ALLOWED_HOSTS = new Set(['hooks.example.com']);

async function assertSafeUrl(raw: string): Promise<URL> {
  const url = new URL(raw);
  if (url.protocol !== 'https:') throw new Error('仅限 HTTPS');
  if (!ALLOWED_HOSTS.has(url.hostname)) throw new Error('主机不允许');
  // 解析所有记录；单个私有/保留地址使检查失败。
  const addrs = await lookup(url.hostname, { all: true });
  if (addrs.some((a) => ipaddr.parse(a.address).range() !== 'unicast') {
    throw new Error('私有/保留 IP');
  }
  return url;
}

await fetch(await assertSafeUrl(req.body.webhookUrl), { redirect: 'error' });
```

`range() !== 'unicast'` 检查涵盖了回环、链路本地 `169.254.169.254`（云元数据，第一个 SSRF 目标）、私有和唯一本地范围，跨越 IPv4 和 IPv6。

**注意——这仍然有一个时序攻击 (TOCTOU) 间隙。** `fetch` 在检查后再次解析 DNS，因此攻击者可以使用短 TTL 记录在验证和连接之间重新绑定到内部 IP。对于高风险表面，解析一次并连接到固定的 IP，或者在前面放置一个过滤代理（`request-filtering-agent` / `ssrf-req-filter`）。

## 输入验证模式

### 边界处的模式验证

```typescript
import { z } from 'zod';

const CreateTaskSchema = z.object({
  title: z.string().min(1).max(200).trim(),
  description: z.string().max(2000).optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  dueDate: z.string().datetime().optional(),
});

// 在路由处理程序处验证
app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: '输入无效',
        details: result.error.flatten(),
      },
    });
  }
  // result.data 现在是类型化和验证的
  const task = await taskService.create(result.data);
  return res.status(201).json(task);
});
```

### 文件上传安全

```typescript
// 限制文件类型和大小
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

function validateUpload(file: UploadedFile) {
  if (!ALLOWED_TYPES.includes(file.mimetype)) {
    throw new ValidationError('不允许的文件类型');
  }
  if (file.size > MAX_SIZE) {
    throw new ValidationError('文件太大（最大 5MB）');
  }
  // 不要信任文件扩展名——如果关键，请检查魔术字节
}
```

### 对派生路径进行破坏性操作

删除、移动或覆盖的安全性仅取决于命名目标的值。从内核、作业负载或兄弟服务中读取该值证明了它 *来自哪里*，而不是谁 *编写* 了它——另一个进程的命令行与表单字段一样受攻击者控制。形状检查（“绝对路径，至少在根目录下一级”）证明了格式正确性，并会被误认为是授权；这就是清理例程删除根而不是叶子的原因。

在执行破坏性调用之前，要求所有三个：解析的目标位于 **允许列表的根** 下（在解析符号链接后比较，永远不要在原始字符串上），它在根目录下至少 **下一级**，所以根本身永远不会是目标，并且它携带 **属于您的证据**，在操作之前和任何移除它的清理操作之前读取——否则“缺失”和“不是我的”无法区分。在拒绝时，记录被拒绝的目标并停止：回退到更广泛的默认路径的清理例程是这种保护要防止的失败。在 `../../references/security-checklist.md` 中有工作示例。

两个限制，因为检查比它读取的更强大。树中的标记是自我证明——任何可以写入那里的人都可以写入标记——所以预期的所有者必须来自经过身份验证的状态，并且标记在计入授权之前需要完整性保护（限制所有权，或使用 MAC）。并且解析路径后在 *名称* 上操作是一个检查/使用竞争，无论不受信任的过程是否可以交换祖先：在共享卷上，通过描述符持有目标，并使用无跟随操作，或在根目录下操作，或确保在持续时间內层次结构不会改变。

## 依赖项审计结果分类

包管理器审计报告已知漏洞；它们不能证明包是值得信赖的，也不能证明易受攻击的代码是可访问的。使用此决策树：

```
原生包管理器审计报告漏洞
├── 严重性：关键或高
│   ├── 漏洞代码在运行时、构建、测试或部署路径中是否可访问？
│   │   ├── 是 --> 立即修复（更新、修补或替换依赖项）
│   │   └── 否（确认未使用这些路径）--> 稍后修复，但不是障碍
│   └── 是否有修复可用？
│       ├── 是 --> 更新到已修补版本
│       └── 否 --> 检查解决方案，考虑替换依赖项，或添加到允许列表并设置审查日期
├── 严重性：中等
│   ├── 是否在生产环境中可访问？ --> 在下一个发布周期内修复
│   └── 仅限开发？ --> 在方便时修复，跟踪在待办事项列表中
└── 严重性：低
    └── 在常规依赖项更新期间跟踪和修复
```

**关键问题：**
- 易受攻击的函数是否实际调用在您的代码路径中？
- 依赖项是运行时依赖项还是仅限开发？
- 给定您的部署上下文（例如，客户端应用程序中的服务器端漏洞），漏洞是否可利用？

当您推迟修复时，记录原因并设置审查日期。

### 供应链卫生

不要假设 npm 或将最近的清单视为安装根。应用此顺序：

1. **找到安装边界和管理器。** 使用拥有锁文件的工 作区根，或者仅在它位于该工作区之外时才使用独立的嵌套项目。在那里，核实 `packageManager`（如果存在）、锁文件和 CI；在出现分歧或竞争锁文件时停止。固定管理器版本并使用 `../../references/security-checklist.md` 中的矩阵。
2. **在第一次执行之前阻止依赖项脚本。** 使用禁用脚本或记录的关闭策略启动，检查挂起的脚本源，仅批准最少的必需包，提交策略，然后使用干净的冻结/不可变安装进行验证。永远不要无差别地批准脚本。

审计仅查找已知漏洞；它们无法捕获新恶意或拼写劫持的包。因此：

- **永远不要自动应用强制审计补救措施** (`npm audit fix --force` 或等效)。预览补救措施，阅读变更日志，并测试每个结果升级；强制修复可能会跨越声明的依赖范围。
- **在支持的情况下验证注册表签名和来源** (`npm audit signatures`, `pnpm audit signatures`)，并将缺失视为需要调查的信号，而不是自动证明妥协。
- **一起审查新依赖项、锁文件差异和脚本策略更改**——所有权、维护、发布年龄、来源和拼写劫持，例如 `cross-env` 与 `crossenv`（OWASP **A06**、**LLM03**）。

## 速率限制

```typescript
import rateLimit from 'express-rate-limit';

// 一般 API 速率限制
app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100,                   // 每个窗口 100 个请求
  standardHeaders: true,
  legacyHeaders: false,
}));

// 对身份验证端点使用更严格的限制
app.use('/api/auth/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,  // 每 15 分钟 10 次尝试
}));
```

**在存在多个进程时使用共享存储进行计数。** `express-rate-limit` 默认情况下将其计数器保存在进程内存中。在负载均衡器后面，每个实例都持有自己的计数，因此有效限制是 `max × 实例数`；在服务器端或边缘运行时，每次调用都从零开始，因此上面的身份验证限制可能永远不会触发。传递一个共享的 `store`（通过 `rate-limit-redis` 的 Redis），或者使用一个 HTTP-based 限制器，它在没有持久 TCP 连接的地方工作（例如 `@upstash/ratelimit`）：

```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const authLimiter = new Ratelimit({
  redis: Redis.fromEnv(),                       // UPSTASH_REDIS_REST_URL + _TOKEN
  limiter: Ratelimit.slidingWindow(10, '15 m'), // 每 15 分钟 10 次尝试，跨所有实例
});
const { success } = await authLimiter.limit(`login:${req.ip}`);
if (!success) return res.status(429).end();
```

## 秘密管理

```
.env 文件:
  ├── .env.example  → 提交（模板，包含占位符值）
  ├── .env          → 不提交（包含真实的秘密）
  └── .env.local    → 不提交（本地覆盖）

.gitignore 必须包含:
  .env
  .env.local
  .env.*.local
  *.pem
  *.key
```

**提交之前始终检查：**
```bash
# 检查意外提交的秘密
git diff --cached | grep -i "password\|secret\|api_key\|token"
```

**如果秘密被提交，请旋转它。** 删除该行或重写历史记录是不够的——一旦它到达远程，就假设它已泄露。首先撤销并重新发布密钥，然后从历史记录中清除它。

## 数据隐私与合规

保护数据是“攻击者能读取它吗？”隐私是“我们是否应该持有它，以及持有多长时间？”——这是一个独立的问题，加固无法回答。保护成本最低、泄露和合规最便宜的数据是您从未收集的数据。将个人数据视为要最小化的负债，而不是要囤积的资产。

**了解您持有的是什么。** 如果您无法找到数据，您无法保护或尊重删除请求。在添加字段时，将字段分类：

| 类别 | 示例 | 处理方式 |
|---|---|---|
| **非个人** | 汇总，匿名计数 | 正常处理 |
| **个人 (PII)** | 姓名、电子邮件、IP、设备/用户 ID | 最小化，访问控制，包括在导出/删除中 |
| **敏感** | 健康、财务、位置、生物识别、政府 ID、任何关于未成年人的内容 | 额外的收集基础，更严格的访问控制，通常加密 + 审计日志 |

**操作规则：**
- **最小化并设定目的。** 仅针对声明用途收集字段。“它可能以后有用”不是一个目的——这是潜在的泄露范围。不要将 PII 记录到遥测（`observability-and-instrumentation` 技能从操作方面提出了相同的观点）。
- **事先设定保留期，然后实际删除。** 每个个人数据存储都需要一个 TTL 和一个可工作的删除路径——包括备份、缓存、搜索索引和分析副本。没有过期期的数据是计划中的泄露。
- **支持您所在司法管辖区要求的数据主体权利**（GDPR/CCPA 和同类）：导出、更正和删除请求。这些都是工程功能——设计数据结构，以便用户的数据是 *可查找* 和 *可删除* 的，而不是不可撤销地分散在系统中。
- **在收集或与第三方共享之前获取同意**，并使其可审计。将 PII 发送到分析/广告/LLM 供应商而没有同意或数据处理协议是“共享”——用户的决定控制它，供应商需要一个数据处理协议。
- **本地化默认值，不要硬编码一个地区的法律。** 数据驻留和规则因用户位置而异；使策略成为一个可配置的边界，而不是一个假设。

当数据跨越信任边界时，将其视为未受信任的输入（见上文输入验证）；当隐私事件暴露个人数据时，泄露通知时钟是事后分析的一部分——遵循 `debugging-and-error-recovery` 技能。

## 保护 AI / LLM 功能

如果您的应用程序调用 LLM——聊天机器人、摘要器、代理、RAG——它继承了新的攻击面。将其映射到 [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/)：

- **将所有模型输出视为未受信任的输入 (LLM05: Improper Output Handling).** 永远不要将 LLM 输出直接传递到 `eval`、SQL、外壳、`innerHTML` 或文件路径。像对待原始用户输入一样验证和编码它。
- **假设提示可以被劫持 (LLM01: Prompt Injection).** 未受信任的文本在上下文窗口中——用户消息、获取的网页、PDF——可以携带指令。系统提示不是一个安全边界；在代码中执行权限，而不是在提示中。
- **将秘密和其他用户的数据从提示中排除 (LLM02 / LLM07).** 上下文中任何内容都可以被回显。不要将 API 密钥、跨租户数据或完整的系统提示放在模型可以重复的地方。
- **限制工具和代理权限 (LLM06: Excessive Agency).** 将工具的范围限制到最小，要求对破坏性或不可逆操作进行确认，并验证每个工具参数。
- **限制消耗 (LLM10: Unbounded Consumption).** 限制令牌、请求速率和循环/递归深度，以便精心设计的输入无法运行成本或挂起系统。
- **隔离检索数据 (LLM08: Vector and Embedding Weaknesses).** 在 RAG 中，将向量存储视为一个信任边界：为每个租户划分嵌入，以便一个用户无法检索另一个用户的数据，并在索引之前验证文档，以便中毒内容无法引导答案。

```typescript
// BAD: 将模型输出视为命令或标记
const sql = await llm.generate(`Write SQL for: ${userQuestion}`);
await db.query(sql);                                   // 任意的查询执行
container.innerHTML = await llm.reply(userMessage);   // 存储的 XSS，通过模型

// GOOD: 模型输出是数据——防御性地解析，然后验证，然后编码
let intent;
try {
  intent = CommandSchema.parse(JSON.parse(await llm.replyJson(userMessage)));
} catch {
  throw new ValidationError('意外的模型输出'); // JSON.parse 或 schema 失败
}
await runAllowlistedAction(intent.action, intent.params);
container.textContent = await llm.reply(userMessage);
```

## 安全审查清单

```markdown
### 身份验证
- [ ] 密码使用 bcrypt/scrypt/argon2 哈希（盐轮数 ≥ 12）
- [ ] 会话令牌是 httpOnly、secure、sameSite
- [ ] 登录有速率限制
- [ ] 密码重置令牌过期

### 授权
- [ ] 每个端点检查用户权限
- [ ] 用户只能访问自己的资源
- [ ] 管理员操作需要管理员角色验证

### 输入
- [ ] 所有用户输入在系统边界处验证
- [ ] SQL 查询参数化
- [ ] 输出编码/转义
- [ ] 服务器端 URL 获取验证对允许列表（没有 SSRF 到内部服务）
- [ ] 破坏性文件操作从数据中解析符号链接，然后验证允许的根、至少下一级，以及操作之前属于您的证据（在操作之前和任何移除它之前的清理操作之前读取）——否则“缺失”和“不是我的”无法区分。拒绝时，记录被拒绝的目标并停止：回退到更广泛的默认路径的清理例程是这种保护要防止的失败。工作示例在 `../../references/security-checklist.md` 中。

### 数据
- [ ] 代码或版本控制中没有任何秘密
- [ ] 不在 API 响应中返回敏感字段
- [ ] PII 在静态时加密（如果适用）
- [ ] 个人数据分类、最小化到声明的目的，并具有保留期限
- [ ] 删除和导出请求端到端工作（包括备份、缓存和分析副本）

### 基础设施
- [ ] 配置安全标头（CSP、HSTS 等）
- [ ] CORS 限制为已知来源
- [ ] 依赖项审计漏洞
- [ ] 错误消息不暴露内部细节

### 供应链
- [ ] 一个权威的锁文件提交；CI 使用该管理器的冻结/不可变安装
- [ ] 原生审计按可访问性和修复风险进行分类；阻止未经明确批准的依赖项安装脚本
- [ ] 审查新依赖项（所有权、来源、发布年龄、传递图）和拼写劫持，例如 `cross-env` 与 `crossenv`（OWASP **A06**、**LLM03**）

### AI / LLM（如果使用）
- [ ] 模型输出被视为未受信任（不使用 eval/SQL/innerHTML/shell）
- [ ] 秘密、PII 或完整系统提示放在 LLM 上下文窗口内
- [ ] 个人数据收集没有任何声明的目的、保留期限或删除路径
- [ ] 向分析/广告/LLM 供应商发送 PII 时没有同意或数据处理协议
- [ ] “删除我的账户”只是切换一个标志，而个人数据仍然存在于存储和备份中
```
## 参考资料链接

有关详细安全清单和预提交验证步骤，请参阅 `../../references/security-checklist.md`。

## 常见借口

| 借口 | 真实情况 |
|---|---|
| “这是一个内部工具，安全不重要” | 内部工具也会被攻破。攻击者针对最薄弱的环节。 |
| “我们会稍后添加安全” | 安全重构比构建它困难 10 倍。现在添加它。 |
| “没有人会尝试利用这个” | 自动扫描器会找到它。安全通过隐蔽性不是安全。 |
| “框架处理安全” | 框架提供工具，而不是保证。您仍然需要正确使用它们。 |
| “只是一个原型” | 原型会变成生产。第一天就养成安全习惯。 |
| “威胁模型过于复杂” | 五分钟的“我会如何攻击这个？”可以防止设计缺陷，而控制无法在之后修复。 |
| “这是 LLM 输出，只是文本” | 这“文本”可以是 SQL 语句、脚本标签或 shell 命令。将其视为任何未受信任的输入。 |
| “审计通过，所以依赖项是安全的” | 审计仅匹配已知漏洞。它们无法检测到新恶意或拼写劫持的包。 |
| “收集它现在，我们以后可能需要它” | 您不持有的数据无法被泄露、传票或错误删除。 “可能需要它”是泄露范围，而不是一个目的。 |
| “我们会手动处理删除请求” | 手动删除遗漏了备份、缓存和分析副本。如果无法找到用户的数據，您无法执行请求——设计它。 |
