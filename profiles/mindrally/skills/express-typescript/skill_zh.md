# Express TypeScript 开发

您是 Express.js 和 TypeScript 开发的专家，对构建可扩展、可维护的 API 具有深入的了解。

## TypeScript 一般指南

### 基本原则

- 所有代码和文档均使用英文
- 始终为变量和函数声明类型（参数和返回值）
- 避免使用 `any` 类型 - 而是创建必要的类型
- 使用 JSDoc 文档化公共类和方法
- 编写简洁、可维护且技术准确的代码
- 使用函数式和声明式编程模式；尽可能避免使用类
- 优先使用迭代和模块化以遵循 DRY 原则

### 命名规范

- 使用 PascalCase 命名类型和接口
- 使用 camelCase 命名变量、函数和方法
- 使用 kebab-case 命名文件和目录名
- 使用 UPPERCASE 命名环境变量
- 使用描述性变量名并带有辅助动词：`isLoading`、`hasError`、`canDelete`
- 每个函数以动词开头

### 函数

- 编写具有单一目的的短函数
- 使用箭头函数编写中间件和处理器
- 在整个代码库中一致地使用 async/await
- 使用 RO-RO 模式处理多个参数

### 类型与接口

- 优先使用接口而不是类型定义对象结构
- 避免使用枚举；使用映射或 const 对象代替
- 使用 Zod 进行运行时验证并推断类型
- 使用 `readonly` 声明不可变属性

## Express 特定指南

### 项目结构

```
src/
  routes/
    {资源}/
      index.ts
      controller.ts
      validators.ts
  middleware/
    auth.ts
    errorHandler.ts
    requestLogger.ts
    validateRequest.ts
  services/
    {领域}Service.ts
  models/
    {实体}.ts
  types/
    express.d.ts
    index.ts
  utils/
  config/
  app.ts
  server.ts
```

### 应用程序设置

```typescript
import express, { Express } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';
import routes from './routes';

const createApp = (): Express => {
  const app = express();

  // 安全中间件
  app.use(helmet());
  app.use(cors());

  // 请求体解析
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // 请求日志记录
  app.use(requestLogger);

  // 路由
  app.use('/api', routes);

  // 错误处理（必须放在最后）
  app.use(errorHandler);

  return app;
};

export default createApp;
```

### 中间件模式

- 使用中间件处理横切关注点
- 按执行顺序链式调用中间件
- 在专门的错误中间件中处理错误

```typescript
import { Request, Response, NextFunction } from 'express';

// 请求日志记录中间件
const requestLogger = (req: Request, res: Response, next: NextFunction): void => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
  });

  next();
};

// 身份验证中间件
const authenticate = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
      res.status(401).json({ error: '未提供令牌' });
      return;
    }

    const user = await verifyToken(token);
    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: '无效的令牌' });
  }
};
```

### 路由

- 按资源组织路由
- 使用 Router 进行模块化路由定义
- 在适当的级别应用中间件

```typescript
import { Router } from 'express';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validateRequest';
import { createUserSchema, updateUserSchema } from './validators';
import * as controller from './controller';

const router = Router();

router.get('/', controller.listUsers);
router.get('/:id', controller.getUser);
router.post('/', validateRequest(createUserSchema), controller.createUser);
router.put('/:id', authenticate, validateRequest(updateUserSchema), controller.updateUser);
router.delete('/:id', authenticate, controller.deleteUser);

export default router;
```

### 请求验证

- 验证所有传入请求
- 使用 Zod 定义和验证模式
- 创建可重用的验证中间件

```typescript
import { z } from 'zod';
import { Request, Response, NextFunction } from 'express';

const createUserSchema = z.object({
  body: z.object({
    name: z.string().min(1),
    email: z.string().email(),
    password: z.string().min(8),
  }),
});

const validateRequest = (schema: z.ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          error: '验证失败',
          details: error.errors,
        });
        return;
      }
      next(error);
    }
  };
};
```

### 错误处理

- 创建自定义错误类
- 使用集中式错误处理中间件
- 返回一致的错误响应

```typescript
class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public code: string = 'INTERNAL_ERROR'
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, `${resource} 未找到`, 'NOT_FOUND');
  }
}

// 错误处理中间件
const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction): void => {
  if (err instanceof AppError) {
    res.status(err.statusCode).json({
      error: err.code,
      message: err.message,
    });
    return;
  }

  console.error(err);
  res.status(500).json({
    error: 'INTERNAL_ERROR',
    message: '发生意外错误',
  });
};
```

### TypeScript 扩展

扩展 Express 类型以添加自定义属性：

```typescript
// types/express.d.ts
import { User } from '../models/User';

declare global {
  namespace Express {
    interface Request {
      user?: User;
      requestId?: string;
    }
  }
}
```

### 安全最佳实践

- 使用 helmet 添加安全头部
- 实现速率限制
- 清理用户输入
- 生产环境中使用 HTTPS
- 正确配置 CORS

```typescript
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

app.use(helmet());

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个窗口期内每个 IP 限制为 100 个请求
});

app.use('/api', limiter);
```

### 测试

- 使用 Jest 和 supertest 进行集成测试
- 独立测试中间件
- 模拟外部依赖

```typescript
import request from 'supertest';
import createApp from '../app';

describe('用户 API', () => {
  const app = createApp();

  it('应该创建用户', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'John', email: 'john@example.com', password: 'password123' })
      .expect(201);

    expect(response.body).toHaveProperty('id');
    expect(response.body.name).toBe('John');
  });
});
```
