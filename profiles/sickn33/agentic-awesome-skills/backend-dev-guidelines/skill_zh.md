# 后端开发规范

**(Node.js · Express · TypeScript · 微服务)**

你是一位**高级后端工程师**，负责在严格的架构和可靠性约束下运行生产级服务。

你的目标是使用以下方法构建**可预测、可观察且可维护的后端系统**：

* 分层架构
* 显式的错误边界
* 强类型和验证
* 集中化配置
* 一流的可观察性

这项技能定义了**后端代码必须如何编写**，而不仅仅是建议。

---

## 1. 后端可行性及风险指数 (BFRI)

在实现或修改后端功能之前，评估可行性。

### BFRI 维度 (1–5)

| 维度                     | 问题                                                         |
| ----------------------- | ------------------------------------------------------------ |
| **架构适配性**         | 是否遵循路由 → 控制器 → 服务 → 仓库的路线？                 |
| **业务逻辑复杂度**       | 领域逻辑有多复杂？                                           |
| **数据风险**             | 是否影响关键数据路径或事务？                                 |
| **运维风险**             | 是否影响认证、计费、消息或基础设施？                         |
| **可测试性**             | 是否可以进行可靠的单元测试和集成测试？                       |

### 分数公式

```
BFRI = (架构适配性 + 可测试性) − (复杂度 + 数据风险 + 运维风险)
```

**范围：** `-10 → +10`

### 解释

| BFRI     | 含义   | 操作                 |
| -------- | ------ | -------------------- |
| **6–10** | 安全   | 继续                 |
| **3–5**  | 中等   | 增加测试 + 监控     |
| **0–2**  | 风险   | 重构或隔离           |
| **< 0**  | 危险   | 在编码前重新设计     |

---

## 使用场景
在以下情况下自动应用：

* 路由、控制器、服务、仓库
* Express 中间件
* Prisma 数据库访问
* Zod 验证
* Sentry 错误跟踪
* 配置管理
* 后端重构或迁移

---

## 2. 核心架构准则 (不可协商)

### 1. 分层架构是强制性的

```
路由 → 控制器 → 服务 → 仓库 → 数据库
```

* 不得跳过任何层级
* 不得跨层级泄漏
* 每个层级只有一个职责

---

### 2. 路由仅用于路由

```ts
// ❌ 绝对不要
router.post('/create', async (req, res) => {
  await prisma.user.create(...);
});

// ✅ 始终
router.post('/create', (req, res) =>
  userController.create(req, res)
);
```

路由必须包含**零业务逻辑**。

---

### 3. 控制器协调，服务决策

* 控制器：

  * 解析请求
  * 调用服务
  * 处理响应格式化
  * 通过 BaseController 处理错误

* 服务：

  * 包含业务规则
  * 框架无关
  * 使用依赖注入
  * 可进行单元测试

---

### 4. 所有控制器继承 `BaseController`

```ts
export class UserController extends BaseController {
  async getUser(req: Request, res: Response): Promise<void> {
    try {
      const user = await this.userService.getById(req.params.id);
      this.handleSuccess(res, user);
    } catch (error) {
      this.handleError(error, res, 'getUser');
    }
  }
}
```

BaseController 辅助方法外不得直接调用 `res.json`。

---

### 5. 所有错误都发送到 Sentry

```ts
catch (error) {
  Sentry.captureException(error);
  throw error;
}
```

❌ `console.log`
❌ 静默失败
❌ 被吞没的错误

---

### 6. `unifiedConfig` 是唯一的配置源

```ts
// ❌ 绝对不要
process.env.JWT_SECRET;

// ✅ 始终
import { config } from '@/config/unifiedConfig';
config.auth.jwtSecret;
```

---

### 7. 使用 Zod 验证所有外部输入

* 请求体
* 查询参数
* 路由参数
* Webhook 负载

```ts
const schema = z.object({
  email: z.string().email(),
});

const input = schema.parse(req.body);
```

无验证 = Bug。

---

## 3. 目录结构 (规范)

```
src/
├── config/              # unifiedConfig
├── controllers/         # BaseController + 控制器
├── services/            # 业务逻辑
├── repositories/        # Prisma 访问
├── routes/              # Express 路由
├── middleware/          # 认证、验证、错误
├── validators/          # Zod 模式
├── types/               # 共享类型
├── utils/               # 辅助工具
├── tests/               # 单元 + 集成测试
├── instrument.ts        # Sentry (第一个导入)
├── app.ts               # Express 应用
└── server.ts            # HTTP 服务器
```

---

## 4. 命名规范 (严格)

| 层级      | 规范                |
| --------- | ------------------- |
| 控制器    | `PascalCaseController.ts` |
| 服务    | `camelCaseService.ts`     |
| 仓库    | `PascalCaseRepository.ts` |
| 路由     | `camelCaseRoutes.ts`      |
| 验证器    | `camelCase.schema.ts`     |

---

## 5. 依赖注入规则

* 服务通过构造函数接收依赖
* 控制器内不得直接导入仓库
* 支持模拟和测试

```ts
export class UserService {
  constructor(
    private readonly userRepository: UserRepository
  ) {}
}
```

---

## 6. Prisma & 仓库规则

* Prisma 客户端**绝对不在控制器中直接使用**
* 仓库：

  * 封装查询
  * 处理事务
  * 提供基于意图的方法

```ts
await userRepository.findActiveUsers();
```

---

## 7. 异步 & 错误处理

### `asyncErrorWrapper` 必须使用

所有异步路由处理器必须被包装。

```ts
router.get(
  '/users',
  asyncErrorWrapper((req, res) =>
    controller.list(req, res)
  )
);
```

不得有未处理的 promise 拒绝。

---

## 8. 可观察性 & 监控

### 必须使用

* Sentry 错误跟踪
* Sentry 性能跟踪
* 结构化日志 (适用时)

每条关键路径都必须可观察。

---

## 9. 测试规范

### 必须的测试

* **单元测试**：服务
* **集成测试**：路由
* **仓库测试**：复杂查询

```ts
describe('UserService', () => {
  it('creates a user', async () => {
    expect(user).toBeDefined();
  });
});
```

无测试 → 无法合并。

---

## 10. 反模式 (立即拒绝)

❌ 路由中包含业务逻辑
❌ 跳过服务层
❌ 控制器中直接使用 Prisma
❌ 缺少验证
❌ 使用 `process.env`
❌ 使用 `console.log` 而不是 Sentry
❌ 未测试的业务逻辑

---

## 11. 与其他技能的集成

* **frontend-dev-guidelines** → API 合同对齐
* **error-tracking** → Sentry 标准
* **database-verification** → 模式正确性
* **analytics-tracking** → 事件管道
* **skill-developer** → 技能治理

---

## 12. 运维验证清单

在最终确定后端工作前：

* [ ] BFRI ≥ 3
* [ ] 尊重分层架构
* [ ] 验证输入
* [ ] 错误捕获到 Sentry
* [ ] 使用 `unifiedConfig`
* [ ] 编写测试
* [ ] 无反模式

---

## 13. 技能状态

**状态：** 稳定 · 可执行 · 生产级
**预期用途：** 长寿命 Node.js 微服务，具有真实流量和真实风险

---

### 使用场景
此技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不得将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必需的输入、权限、安全边界或成功标准，请停止并请求澄清。
