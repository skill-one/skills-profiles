# NestJS 代码审查

## 概述

为 NestJS 应用程序提供结构化的代码审查。根据严重程度（关键、警告、建议）分类发现结果，并提供可操作的改进建议。将深度分析委托给 `nestjs-code-review-expert` 代理。

## 使用场景

- "审查 NestJS 代码"、"NestJS 代码审查"、"检查我的 NestJS 控制器/服务"
- 合并拉取请求之前或实现新功能之后
- 验证 NestJS 装饰器、依赖注入模式、守卫实现
- 验证 NestJS 模块和提供者的架构
- 审查 DTO、管道、拦截器和数据库集成（TypeORM、Prisma、Drizzle）

## 指南

1. **确定范围**：确定哪些 NestJS 文件和模块在审查范围内。使用 `glob` 和 `grep` 在目标区域发现控制器、服务、模块、守卫、拦截器和管道。

2. **分析模块结构**：验证模块组织的正确性——每个功能都应该有自己的模块，具有明确定义的导入、控制器、提供者和导出。检查循环依赖和正确的模块边界。

3. **审查依赖注入**：验证所有可注入服务都使用构造函数注入。检查提供者作用域（单例、请求、瞬态）是否与预期生命周期匹配。确保没有直接实例化绕过 DI 容器。

4. **评估控制器**：审查 HTTP 方法使用、路由命名、状态码、请求/响应 DTO、验证管道和 OpenAPI 装饰器。确认控制器是瘦的——业务逻辑属于服务。

5. **评估服务和业务逻辑**：检查服务是否正确封装业务逻辑。验证错误处理、事务管理和与基础设施问题的正确分离。查找方法过长或职责过多的服务。

6. **检查安全性**：审查守卫实现、认证/授权模式、使用 class-validator 的输入验证以及针对常见漏洞（注入、XSS、CSRF）的保护。

7. **审查测试**：评估控制器、服务、守卫和管道的测试覆盖率。验证模拟策略是否正确，并确保测试验证行为而不是实现细节。

8. **验证发现结果**（必需的检查点）：在最终确定之前，验证每个关键和警告发现结果都有可重复的证据（文件路径、行号、确切代码片段）和具体的可操作修复方案。删除或降级那些是风格偏好、过于主观或缺乏具体修复方案的结果。

9. **生成审查报告**：生成结构化报告，包含按严重程度分类的发现结果（关键、警告、建议）、积极观察和优先级建议，附带代码示例。

## 示例

### 示例 1：审查控制器

```typescript
// ❌ 不好：胖控制器包含业务逻辑和缺少验证
@Controller('users')
export class UserController {
  constructor(private readonly userRepo: Repository<User>) {}

  @Post()
  async create(@Body() body: any) {
    const user = this.userRepo.create(body);
    return this.userRepo.save(user);
  }
}

// ✅ 好：薄控制器具有正确的 DTO、验证和服务委托
@Controller('users')
@ApiTags('Users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: '创建新用户' })
  @ApiResponse({ status: 201, type: UserResponseDto })
  async create(
    @Body(ValidationPipe) createUserDto: CreateUserDto,
  ): Promise<UserResponseDto> {
    return this.userService.create(createUserDto);
  }
}
```

### 示例 2：审查依赖注入

```typescript
// ❌ 不好：直接实例化绕过 DI
@Injectable()
export class OrderService {
  private readonly logger = new Logger();
  private readonly emailService = new EmailService();

  async createOrder(dto: CreateOrderDto) {
    this.emailService.send(dto.email, 'Order created');
  }
}

// ✅ 好：正确的构造函数注入
@Injectable()
export class OrderService {
  private readonly logger = new Logger(OrderService.name);

  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly emailService: EmailService,
  ) {}

  async createOrder(dto: CreateOrderDto): Promise<Order> {
    const order = await this.orderRepository.create(dto);
    await this.emailService.send(dto.email, 'Order created');
    return order;
  }
}
```

### 示例 3：审查错误处理

```typescript
// ❌ 不好：通用错误处理导致信息泄露
@Get(':id')
async findOne(@Param('id') id: string) {
  try {
    return await this.service.findOne(id);
  } catch (error) {
    throw new HttpException(error.message, 500);
  }
}

// ✅ 好：特定领域的异常和正确的 HTTP 映射
@Get(':id')
async findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
  const user = await this.userService.findOne(id);
  if (!user) {
    throw new NotFoundException(`User with ID ${id} not found`);
  }
  return user;
}
```

### 示例 4：审查守卫实现

```typescript
// ❌ 不好：控制器中的认证逻辑
@Get('admin/dashboard')
async getDashboard(@Req() req: Request) {
  if (req.user.role !== 'admin') {
    throw new ForbiddenException();
  }
  return this.dashboardService.getData();
}

// ✅ 好：基于守卫的认证装饰器
@Get('admin/dashboard')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(Role.ADMIN)
async getDashboard(): Promise<DashboardDto> {
  return this.dashboardService.getData();
}
```

### 示例 5：审查模块组织

```typescript
// ❌ 不好：单体模块包含所有内容
@Module({
  imports: [TypeOrmModule.forFeature([User, Order, Product, Review])],
  controllers: [UserController, OrderController, ProductController],
  providers: [UserService, OrderService, ProductService, ReviewService],
})
export class AppModule {}

// ✅ 好：基于功能的模块组织
@Module({
  imports: [UserModule, OrderModule, ProductModule],
})
export class AppModule {}

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UserController],
  providers: [UserService, UserRepository],
  exports: [UserService],
})
export class UserModule {}
```

## 审查输出格式

按照以下结构组织所有代码审查发现结果：

### 1. 摘要
简要概述，包含整体质量评分（1-10）和关键观察结果。

### 2. 关键问题（必须修复）
可能导致安全漏洞、数据损坏或生产环境故障的问题。

### 3. 警告（建议修复）
违反最佳实践、降低可维护性或可能导致错误的问题。

### 4. 建议（考虑改进）
提高代码可读性、性能或开发者体验的改进建议。

### 5. 积极观察
良好实现的模式和良好实践，值得认可和鼓励。

### 6. 建议
按优先级排列的下一步行动，附带代码示例，以实现最显著的改进。

## 最佳实践

- 控制器应该是瘦的——将所有业务逻辑委托给服务
- 使用 DTO 和 class-validator 对所有请求/响应有效负载进行验证
- 应用 `ParseUUIDPipe`、`ParseIntPipe` 等进行参数验证
- 使用扩展自 `HttpException` 的特定领域异常类
- 将代码组织成基于功能的模块，具有清晰的边界和导出
- 优先使用构造函数注入——不要使用 `new` 注入可注入服务
- 使用守卫进行认证和授权，而不是内联检查
- 使用拦截器处理横切关注点（日志记录、缓存、转换）
- 为所有端点添加 OpenAPI 装饰器（`@ApiTags`、`@ApiOperation`、`@ApiResponse`）
- 为服务编写单元测试，为控制器编写集成测试

## 限制和警告

- 不要强制使用单个 ORM——代码库可能使用 TypeORM、Prisma、Drizzle 或 MikroORM
- 尊重现有项目约定，即使它们与 NestJS 默认值不同
- 专注于高置信度的问题——避免对风格偏好产生误报
- 在审查微服务模式时，考虑特定传输层的约束
- 除非关键问题需要，否则不要建议架构重写

## 参考

有关详细的审查清单和模式文档，请参阅 `references/` 目录：
- `references/patterns.md` — 带有示例的 NestJS 最佳实践模式
- `references/anti-patterns.md` — 审查期间应标记的常见 NestJS 反模式
- `references/checklist.md` — 按区域组织的综合审查清单
