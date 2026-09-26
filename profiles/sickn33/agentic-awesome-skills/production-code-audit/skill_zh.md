# 生产代码审计

## 详细指南

在执行此技能前，请阅读[详细指南](references/detailed-guide.md)。它保留了完整流程和参考资料。将其安全、前提条件和验证要求视为强制性。对于专注工作，加载相关章节；对于端到端工作，完整阅读指南。

## 何时使用此技能

- 当用户说"使代码生产就绪"时使用
- 当用户说"审计我的代码库"时使用
- 当用户说"使代码专业级/企业级"时使用
- 当用户说"优化所有内容"时使用
- 当用户需要企业级质量时使用
- 在准备生产部署时使用
- 当代码需要满足企业标准时使用

## 示例

### 示例 1：自主代码库转换

```markdown
用户：@生产代码审计 使代码生产就绪

AI：我将扫描您的整个代码库，并将其转换为生产级质量。

**阶段 1：发现代码库**（分析 247 个文件）
- 检测到：Node.js + Express + PostgreSQL + React
- 架构：MVC 模式与 REST API
- 目的：电子商务平台
- 入口点：server.js, src/index.tsx

**阶段 2：扫描问题**（逐行分析）

发现 127 个问题：
- 🔴 严重：8 个问题
- 🟠 高：23 个问题  
- 🟡 中：41 个问题
- 🔵 低：55 个问题

**阶段 3：自动修复问题**

🔴 严重修复（8/8 完成）：

1. ✅ 修复了 UserRepository.findByEmail() 中的 SQL 注入
   - 之前：查询中的字符串拼接
   - 之后：使用 $1 占位符的参数化查询

2. ✅ 从 config/database.ts 中移除硬编码的数据库密码
   - 之前：password: 'SuperSecret123!'
   - 之后：password: process.env.DB_PASSWORD

3. ✅ 为管理员路由添加认证
   - 之前：无认证中间件
   - 之后：authenticateToken + requireRole('admin')

4. ✅ 修复弱密码哈希（MD5 → bcrypt）
   - 之前：crypto.createHash('md5')
   - 之后：bcrypt.hash(password, 12)

5. ✅ 修复循环依赖：OrderService ↔ PaymentService
   - 之前：直接导入导致循环
   - 之后：使用 EventBus 的基于事件的解耦

6. ✅ 为所有 API 端点添加输入验证
   - 之前：无验证
   - 之后：Zod 模式验证所有输入

7. ✅ 修复认证中间件中的认证绕过
   - 之前：在缺少 token 时调用 next()
   - 之后：返回 401 错误

8. ✅ 修复 UserController 中的批量赋值漏洞
   - 之前：接受 req.body 的所有字段
   - 之后：仅白名单允许的字段

🟠 高优先级修复（23/23 完成）：

9. ✅ 修复 OrderService.getOrdersWithItems() 中的 N+1 查询
   - 之前：循环中的单独查询（2.8s）
   - 之后：使用连接的单个查询（45ms）
   - 性能：提升 98%

10. ✅ 重构 UserService 神类（850 行 → 4 个专注服务）
    - UserAuthenticationService（登录、登出、密码）
    - UserProfileService（CRUD 操作）
    - UserNotificationService（电子邮件、短信）
    - UserPermissionService（角色、权限）

11. ✅ 为产品查询添加 Redis 缓存
    - 之前：每次请求数据库查询
    - 之后：1 小时 TTL 的缓存
    - 性能：提升 95%

12. ✅ 优化包大小
    - 之前：850KB（gzip 压缩：280KB）
    - 之后：380KB（gzip 压缩：120KB）
    - 改进：减少 55%

13. ✅ 添加数据库索引
    - orders(user_id, status, created_at)
    - products(category, price)
    - 查询性能：提升 98%

[... 11 个高优先级修复 ...]

🟡 中优先级修复（41/41 完成）：
[... 所有中优先级修复 ...]

🔵 低优先级改进（55/55 完成）：
[... 所有低优先级改进 ...]

**阶段 4：添加生产基础设施**

✅ 添加结构化日志（Winston）
✅ 添加错误跟踪（Sentry）
✅ 添加健康检查端点（/health, /ready）
✅ 添加监控（Prometheus 指标）
✅ 添加速率限制（基于 Redis）
✅ 添加 API 文档（Swagger/OpenAPI）
✅ 添加全面 README
✅ 添加部署指南
✅ 添加 CI/CD 管道（.github/workflows）

**阶段 5：验证**

✅ 所有测试通过（1,247 个测试）
✅ 测试覆盖率：42% → 87%
✅ 安全扫描：0 个漏洞
✅ 性能：API 响应时间 3.2s → 180ms
✅ 包大小：850KB → 380KB
✅ Lighthouse 分数：62 → 94

**转换完成**

您的代码库现在已达到生产就绪的企业级质量：

📊 指标：
- 修复问题：127/127（100%）
- 测试覆盖率：87%（目标：80%+）
- API 性能：提升 94%
- 安全：OWASP Top 10 合规
- 代码质量：A级-

📁 修改文件：89 个文件
📝 修改行数：+3,247 / -1,892

🚀 准备生产部署！

```

### 示例 2：自动安全加固

```markdown
用户：@生产代码审计 加固此代码库

AI：扫描安全漏洞...

**安全扫描完成**

发现 15 个安全问题：
- 🔴 严重：5 个
- 🟠 高：7 个
- 🟡 中：3 个

**自动修复所有安全问题...**

🔴 严重（5/5 修复）：

1. ✅ UserRepository 中的 SQL 注入
\`\`\`typescript
// 之前（易受攻击）
const query = \`SELECT * FROM users WHERE email = '\${email}'\`;

// 之后（安全）
const query = 'SELECT * FROM users WHERE email = $1';
await db.query(query, [email]);
\`\`\`

2. ✅ 移除硬编码密钥
\`\`\`typescript
// 之前（不安全）
const tokenSigningKey = '[隐藏的弱值]';

// 之后（安全）
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) throw new Error('JWT_SECRET required');
\`\`\`

3. ✅ 管理员路由添加认证
\`\`\`typescript
// 之前（易受攻击）
router.delete('/api/admin/users/:id', deleteUser);

// 之后（安全）
router.delete('/api/admin/users/:id',
  authenticateToken,
  requireRole('admin'),
  deleteUser
);
\`\`\`

4. ✅ 密码哈希升级
\`\`\`typescript
// 之前（弱）
const hash = crypto.createHash('md5').update(password).digest('hex');

// 之后（强）
const hash = await bcrypt.hash(password, 12);
\`\`\`

5. ✅ 添加输入验证
\`\`\`typescript
// 之前（易受攻击）
const user = await db.user.create({ data: req.body });

// 之后（安全）
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(12),
  name: z.string().min(2).max(100)
});
const validated = schema.parse(req.body);
const user = await db.user.create({ data: validated });
\`\`\`

**安全状态：**
- ✅ OWASP Top 10：合规
- ✅ SQL 注入：受保护
- ✅ XSS：受保护
- ✅ CSRF：受保护
- ✅ 认证：安全
- ✅ 密钥：环境变量
- ✅ 依赖：无漏洞

🔒 代码库现在已安全且生产就绪！
```

### 示例 3：性能优化

```markdown
用户：@生产代码审计 优化性能

AI：分析性能瓶颈...

**性能分析完成**

当前指标：
- API 响应时间：3.2s（目标：<200ms）
- 页面加载时间：8.5s（目标：<2s）
- 包大小：850KB（目标：<200KB）

**自动优化...**

✅ 修复 N+1 查询（3.2s → 180ms - 提升 94%）
✅ 添加 Redis 缓存（95% 缓存命中率）
✅ 优化数据库索引（查询速度提升 98%）
✅ 减少包大小（850KB → 380KB - 减小 55%）
✅ 优化图像（28MB → 3.2MB - 减小 89%）
✅ 实现代码拆分
✅ 添加懒加载
✅ 并行化异步操作

**性能结果：**

| 指标 | 之前 | 之后 | 改进 |
|------|------|------|------|
| API 响应 | 3.2s | 180ms | 94% |
| 页面加载 | 8.5s | 1.8s | 79% |
| 包大小 | 850KB | 380KB | 55% |
| 图像大小 | 28MB | 3.2MB | 89% |
| Lighthouse | 42 | 94 | +52 分 |

🚀 性能优化至生产标准！
```

## 限制
- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必需的输入、权限、安全边界或成功标准，请停止并请求澄清。
