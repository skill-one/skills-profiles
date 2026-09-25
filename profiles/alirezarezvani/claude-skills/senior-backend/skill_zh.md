# 高级后端工程师

后端开发模式、API设计、数据库优化和安全实践。

---

## 快速入门

```bash
# 从OpenAPI规范生成API路由
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/

# 分析数据库模式并生成迁移文件
python scripts/database_migration_tool.py --connection postgres://localhost/mydb --analyze

# 对API端点进行负载测试
python scripts/api_load_tester.py https://api.example.com/users --concurrency 50 --duration 30
```

---

## 工具概述

### 1. API生成器

根据模式定义生成API路由处理器、中间件和OpenAPI规范。

**输入：** OpenAPI规范（YAML/JSON）或数据库模式
**输出：** 路由处理器、验证中间件、TypeScript类型

**使用方法：**
```bash
# 从OpenAPI规范生成Express路由
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/
# 输出：生成12个路由处理器、验证中间件和TypeScript类型

# 从数据库模式生成
python scripts/api_scaffolder.py --from-db postgres://localhost/mydb --output src/routes/

# 从现有路由生成OpenAPI规范
python scripts/api_scaffolder.py src/routes/ --generate-spec --output openapi.yaml
```

**支持的框架：**
- Express.js (`--framework express`)
- Fastify (`--framework fastify`)
- Koa (`--framework koa`)

---

### 2. 数据库迁移工具

分析数据库模式、检测变更并生成带回滚支持的迁移文件。

**输入：** 数据库连接字符串或模式文件
**输出：** 迁移文件、模式差异报告、优化建议

**使用方法：**
```bash
# 分析当前模式并建议优化
python scripts/database_migration_tool.py --connection postgres://localhost/mydb --analyze
# 输出：缺失索引、N+1查询风险和建议的迁移文件

# 从模式差异生成迁移
python scripts/database_migration_tool.py --connection postgres://localhost/mydb \
  --compare schema/v2.sql --output migrations/

# 迁移干运行
python scripts/database_migration_tool.py --connection postgres://localhost/mydb \
  --migrate migrations/20240115_add_user_indexes.sql --dry-run
```

---

### 3. API负载测试器

执行HTTP负载测试，可配置并发，测量延迟百分位数和吞吐量。

**输入：** API端点URL和测试配置
**输出：** 性能报告，包含延迟分布、错误率和吞吐量指标

**使用方法：**
```bash
# 基本负载测试
python scripts/api_load_tester.py https://api.example.com/users --concurrency 50 --duration 30
# 输出：吞吐量（req/sec）、延迟百分位数（P50/P95/P99）、错误计数和扩展建议

# 使用自定义头部和正文测试
python scripts/api_load_tester.py https://api.example.com/orders \
  --method POST \
  --header "Authorization: Bearer token123" \
  --body '{"product_id": 1, "quantity": 2}' \
  --concurrency 100 \
  --duration 60

# 比较两个端点
python scripts/api_load_tester.py https://api.example.com/v1/users https://api.example.com/v2/users \
  --compare --concurrency 50 --duration 30
```

---

## 后端开发工作流

### API设计工作流

用于设计新API或重构现有端点。

**步骤1：定义资源和操作**
```yaml
# openapi.yaml
openapi: 3.0.3
info:
  title: 用户服务API
  version: 1.0.0
paths:
  /users:
    get:
      summary: 列出用户
      parameters:
        - name: "limit"
          in: query
          schema:
            type: integer
            default: 20
    post:
      summary: 创建用户
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
```

**步骤2：生成路由脚手架**
```bash
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/
```

**步骤3：实现业务逻辑**
```typescript
// src/routes/users.ts (生成后自定义)
export const createUser = async (req: Request, res: Response) => {
  const { email, name } = req.body;

  // 添加业务逻辑
  const user = await userService.create({ email, name });

  res.status(201).json(user);
};
```

**步骤4：添加验证中间件**
```bash
# 验证从OpenAPI模式自动生成
# src/middleware/validators.ts 包含：
# - 请求正文验证
# - 查询参数验证
# - 路径参数验证
```

**步骤5：生成更新的OpenAPI规范**
```bash
python scripts/api_scaffolder.py src/routes/ --generate-spec --output openapi.yaml
```

---

### 数据库优化工作流

用于查询缓慢或需要改进数据库性能时。

**步骤1：分析当前性能**
```bash
python scripts/database_migration_tool.py --connection $DATABASE_URL --analyze
```

**步骤2：识别慢查询**
```sql
-- 检查查询执行计划
EXPLAIN ANALYZE SELECT * FROM orders
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 10;

-- 查看：Seq Scan（差），Index Scan（好）
```

**步骤3：生成索引迁移**
```bash
python scripts/database_migration_tool.py --connection $DATABASE_URL \
  --suggest-indexes --output migrations/
```

**步骤4：迁移测试（干运行）**
```bash
python scripts/database_migration_tool.py --connection $DATABASE_URL \
  --migrate migrations/add_indexes.sql --dry-run
```

**步骤5：应用并验证**
```bash
# 应用迁移
python scripts/database_migration_tool.py --connection $DATABASE_URL \
  --migrate migrations/add_indexes.sql

# 验证改进
python scripts/database_migration_tool.py --connection $DATABASE_URL --analyze
```

---

### 安全加固工作流

用于准备API进行生产或安全审查后。

**步骤1：审查认证设置**
```typescript
// 验证JWT配置
const jwtConfig = {
  secret: process.env.JWT_SECRET,  // 必须来自环境变量，不要硬编码
  expiresIn: '1h',                 // 短期令牌
  algorithm: 'RS256'               // 优先非对称
};
```

**步骤2：添加速率限制**
```typescript
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15分钟
  max: 100,                   // 每个窗口100个请求
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', apiLimiter);
```

**步骤3：验证所有输入**
```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100),
  age: z.number().int().positive().optional()
});

// 在路由处理器中使用
const data = CreateUserSchema.parse(req.body);
```

**步骤4：使用攻击模式进行负载测试**
```bash
# 测试速率限制
python scripts/api_load_tester.py https://api.example.com/login \
  --concurrency 200 --duration 10 --expect-rate-limit

# 测试输入验证
python scripts/api_load_tester.py https://api.example.com/users \
  --method POST \
  --body '{"email": "not-an-email"}' \
  --expect-status 400
```

**步骤5：审查安全头部**
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: true,
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: true,
  crossOriginResourcePolicy: true,
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));
```

---

## 参考文档

| 文件 | 包含内容 | 使用场景 |
|------|----------|----------|
| `references/api_design_patterns.md` | REST与GraphQL、版本控制、错误处理、分页 | 设计新API |
| `references/database_optimization_guide.md` | 索引策略、查询优化、N+1解决方案 | 修复慢查询 |
| `references/backend_security_practices.md` | OWASP Top 10、认证模式、输入验证 | 安全加固 |

---

## 常见模式快速参考

### REST API响应格式
```json
{
  "data": { "id": 1, "name": "John" },
  "meta": { "requestId": "abc-123" }
}
```

### 错误响应格式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "无效的邮箱格式",
    "details": [{ "field": "email", "message": "必须是有效的邮箱" }]
  },
  "meta": { "requestId": "abc-123" }
}
```

### HTTP状态码
| 码 | 使用场景 |
|------|----------|
| 200 | 成功（GET、PUT、PATCH） |
| 201 | 创建（POST） |
| 204 | 无内容（DELETE） |
| 400 | 验证错误 |
| 401 | 需要认证 |
| 403 | 权限拒绝 |
| 404 | 资源未找到 |
| 429 | 速率限制超出 |
| 500 | 服务器内部错误 |

### 数据库索引策略
```sql
-- 单列（等值查找）
CREATE INDEX idx_users_email ON users(email);

-- 复合（多列查询）
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 部分索引（过滤查询）
CREATE INDEX idx_orders_active ON orders(created_at) WHERE status = 'active';

-- 覆盖索引（避免表查找）
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name);
```

---

## 常见命令

```bash
# API开发
python scripts/api_scaffolder.py openapi.yaml --framework express
python scripts/api_scaffolder.py src/routes/ --generate-spec

# 数据库操作
python scripts/database_migration_tool.py --connection $DATABASE_URL --analyze
python scripts/database_migration_tool.py --connection $DATABASE_URL --migrate file.sql

# 性能测试
python scripts/api_load_tester.py https://api.example.com/endpoint --concurrency 50
python scripts/api_load_tester.py https://api.example.com/endpoint --compare baseline.json
```

---

## 假设和可验证的成功标准（Karpathy纪律）

在此技能脚手架、推荐模式或修改模式之前，必须明确以下四个假设。如果任何假设未知，技能将停止并使用[Forcing-question库](#forcing-question-library-matt-pocock-grill)。

1. **读写比例+一年p99 QPS** — 决定DB、缓存、队列和分区选择。Kleppmann, *DDIA* (2017)。
2. **租户模型** — 单租户、共享多租户、隔离多租户。决定数据访问模式。
3. **数据敏感性级别** — 公开/内部/PII/PHI/PCI。决定合规底线。
4. **SLO+命名错误预算消费者** — Google SRE Workbook规范。无SLO=无可靠性工作优先级。

**可验证的成功标准**（Karpathy #4）— 此技能发出的每个推荐都必须包含：

- 延迟目标（p50、p95、p99，单位毫秒）
- 可用性/SLO目标
- RPO+RTO

如果其中任何一项未说明，推荐不完整 — 返回Q7的Forcing-question库。

`scripts/backend_decision_engine.py`工具编码了这些检查：它拒绝在没有读写比例+QPS+租户+数据敏感性+模式偏好的情况下推荐配置。

---

## 定制配置文件

`profiles/`中的四个内置配置文件校准了每个推荐：

| 配置文件 | 选择时机 | 模式 | p99延迟底线 |
|---|---|---|---|
| `node-express` | TS团队，< 15工程师，面向客户的SaaS | 模块化单体，Postgres | 600ms |
| `fastapi-python` | Python团队，< 20工程师，ML相关 | 模块化单体，Postgres（异步） | 500ms |
| `django-monolith` | 内容密集型CRUD+管理，< 25工程师 | 模块化单体，Postgres | 800ms |
| `go-or-rust-microservice` | 提取服务，≥ 30工程师，平台团队，QPS ≥ 1000 | 提取服务 | 200ms |

通过以下方式选择配置文件：

```bash
python scripts/backend_decision_engine.py \
  --team-size 8 --qps-p99 50 --read-write-ratio 20 \
  --tenancy shared-multi-tenant --data-sensitivity pii \
  --pattern modular-monolith --language-preference typescript
```

工具返回最佳匹配配置文件、次优权衡（如果差距在15%以内）、技术栈选择、反模式、命名批准者和SLO底线。**此工具从不自动批准。**

要添加自定义配置文件：复制`profiles/node-express.json`到`profiles/<your-org>.json`并调整`constraints` + `success_thresholds` + `named_approver_chain`。

---

## 组合映射

此技能不重新实现由POWERFUL级专家拥有的范围。它分支到他们。参见`references/composition_map.md`获取完整路由表。关键分支：

| 关注点 | 分支到 |
|---|---|
| API合同/破坏风险 | `engineering/skills/api-design-reviewer/` |
| 模式设计+ERD+索引 | `engineering/skills/database-designer/` |
| 零停机模式迁移 | `engineering/skills/migration-architect/` |
| SLO+SLI+错误预算 | `engineering/slo-architect/` |
| 可观察性/黄金信号 | `engineering/skills/observability-designer/` |
| CI/CD管道 | `engineering/skills/ci-cd-pipeline-builder/` |
| 安全/威胁模型 | `engineering-team/skills/senior-security/`, `adversarial-reviewer` |
| 合规证据（HIPAA / ISO 27001） | `ra-qm-team/` |
| 预提交Karpathy审查 | `engineering/karpathy-coder/` |
| 预飞行架构审查 | `engineering/grill-me/` |

`cs-backend-engineer`代理通过`context: fork`协调这些分支。从另一个代理调用它：`Agent({subagent_type: "cs-backend-engineer", prompt: "..."})`或通过`/cs:backend-review <你的问题>`。

---

## Forcing-question库（Matt Pocock审查）

在锁定任何后端决策之前，按`references/forcing_questions.md`中的七个问题顺序进行。纪律：

1. 每次一个问题。不要捆绑。
2. 总是引用规范推荐答案。
3. 在`/tmp/backend-grill-<date>.md`中跟踪答案。
4. 如果触发终止标准，停止。不要围绕未解决的差距脚手架。
5. Q7后，运行`backend_decision_engine.py`使用七个答案。

总结：

1. 读写比例+p99 QPS预测？
2. 租户模型—单租户/共享/隔离？
3. 同步/异步/事件驱动—默认+例外？
4. 数据敏感性级别—PII/PHI/PCI？
5. 单体/模块化单体/微服务—团队规模理由？
6. RPO+RTO？
7. SLO+命名错误预算消费者？

---

## 其他代理和技能的调用

三个表面：

1. **斜杠命令：** `/cs:backend-review <提示>` — 完整审查+决策引擎+组合路由。
2. **代理子代理：** `Agent({subagent_type: "cs-backend-engineer", prompt: "..."})` — 分支上下文，返回≤ 200字摘要。
3. **直接工具调用：** `python scripts/backend_decision_engine.py ...` — 输入已知时的确定性配置匹配。

参见`agents/engineering/cs-backend-engineer.md`获取完整调用合同。
