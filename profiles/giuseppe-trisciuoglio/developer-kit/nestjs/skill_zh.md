# 使用 Drizzle ORM 的 NestJS 框架

## 概述

提供使用 Drizzle ORM 的 NestJS 模式，用于构建生产就绪的服务器端应用程序。涵盖 CRUD 模块、JWT 身份验证、数据库操作、迁移、测试、微服务以及 GraphQL 集成。

## 使用场景

- 使用 NestJS 构建 REST API 或 GraphQL 服务器
- 使用 JWT 设置身份验证和授权
- 使用 Drizzle ORM 实现数据库操作
- 使用 TCP/Redis 传输创建微服务
- 编写单元测试和集成测试
- 使用 drizzle-kit 运行数据库迁移

## 使用说明

1. **安装依赖项**：`npm i drizzle-orm pg && npm i -D drizzle-kit tsx`
2. **定义模式**：创建 `src/db/schema.ts` 并使用 Drizzle 表定义
3. **创建 DatabaseService**：将 Drizzle 客户端作为 NestJS 提供者注入
4. **构建 CRUD 模块**：控制器 → 服务 → 仓库模式
5. **添加验证**：使用 class-validator DTOs 与 ValidationPipe
6. **实现守卫**：创建 JWT/Roles 守卫以保护路由
7. **编写测试**：使用 `@nestjs/testing` 并使用模拟的仓库
8. **运行迁移**：`npx drizzle-kit generate` → **验证 SQL** → `npx drizzle-kit migrate`

## 示例

### 使用 Drizzle 的完整 CRUD 模块

```typescript
// src/db/schema.ts
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow(),
});

// src/users/dto/create-user.dto.ts
export class CreateUserDto {
  @IsString() @IsNotEmpty() name: string;
  @IsEmail() email: string;
}

// src/users/user.repository.ts
@Injectable()
export class UserRepository {
  constructor(private db: DatabaseService) {}

  async findAll() {
    return this.db.database.select().from(users);
  }

  async create(data: typeof users.$inferInsert) {
    return this.db.database.insert(users).values(data).returning();
  }
}

// src/users/users.service.ts
@Injectable()
export class UsersService {
  constructor(private repo: UserRepository) {}

  async create(dto: CreateUserDto) {
    return this.repo.create(dto);
  }
}

// src/users/users.controller.ts
@Controller('users')
export class UsersController {
  constructor(private service: UsersService) {}

  @Post()
  create(@Body() dto: CreateUserDto) {
    return this.service.create(dto);
  }
}

// src/users/users.module.ts
@Module({
  controllers: [UsersController],
  providers: [UsersService, UserRepository, DatabaseService],
  exports: [UsersService],
})
export class UsersModule {}
```

### JWT 身份验证守卫

```typescript
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  canActivate(context: ExecutionContext) {
    const token = context.switchToHttp().getRequest()
      .headers.authorization?.split(' ')[1];
    if (!token) return false;
    try {
      const decoded = this.jwtService.verify(token);
      context.switchToHttp().getRequest().user = decoded;
      return true;
    } catch {
      return false;
    }
  }
}
```

### 数据库事务

```typescript
async transferFunds(fromId: number, toId: number, amount: number) {
  return this.db.database.transaction(async (tx) => {
    await tx.update(accounts)
      .set({ balance: sql`${accounts.balance} - ${amount}` })
      .where(eq(accounts.id, fromId));
    await tx.update(accounts)
      .set({ balance: sql`${accounts.balance} + ${amount}` })
      .where(eq(accounts.id, toId));
  });
}
```

### 使用 Mocks 的单元测试

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let repo: jest.Mocked<UserRepository>;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: UserRepository, useValue: { findAll: jest.fn(), create: jest.fn() } },
      ],
    }).compile();
    service = module.get(UsersService);
    repo = module.get(UserRepository);
  });

  it('should create user', async () => {
    const dto = { name: 'John', email: 'john@example.com' };
    repo.create.mockResolvedValue({ id: 1, ...dto, createdAt: new Date() });
    expect(await service.create(dto)).toMatchObject(dto);
  });
});
```

## 限制和警告

- **DTOs 必须使用**：始终使用 class-validator 的 DTOs，绝不接受原始对象
- **事务**：保持事务简短；避免嵌套事务
- **守卫顺序**：JWT 守卫必须在 Roles 守卫之前运行
- **环境变量**：不要硬编码 DATABASE_URL 或 JWT_SECRET
- **迁移**：在模式更改后部署前运行 `drizzle-kit generate`
- **循环依赖**：谨慎使用 `forwardRef()`；优先考虑模块重构

## 最佳实践

- 使用全局 `ValidationPipe` 验证所有输入
- 使用事务进行多表操作
- 使用 OpenAPI/Swagger 装饰器记录 API

## 参考

高级模式和详细示例可在以下位置找到：
- `references/reference.md` - 核心模式、守卫、拦截器、微服务、GraphQL
- `references/drizzle-reference.md` - Drizzle ORM 安装、配置、查询
- `references/workflow-optimization.md` - 开发工作流、并行执行策略
