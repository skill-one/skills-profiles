# NestJS 最佳实践

## 概述

基于 [官方 NestJS 文档](https://docs.nestjs.com/)，本指南强制执行模块化架构、依赖注入作用域、异常过滤器、使用 `class-validator` 的 DTO 验证以及 Drizzle ORM 集成模式。

## 何时使用

- 设计/重构 NestJS 模块或依赖注入
- 创建异常过滤器、验证 DTO 或集成 Drizzle ORM
- 审查代码以查找反模式或在 NestJS 代码库中入职

## 说明

### 1. 模块化架构

遵循严格的模块封装。每个领域功能都应该是自己的 `@Module()`：

- 仅导出其他模块需要的 — 保持内部提供者私有
- 仅在最后手段时使用 `forwardRef()` 以解决循环依赖；优先重构
- 将相关的控制器、服务和存储库分组在同一模块内
- 使用 `SharedModule` 处理横切关注点（日志记录、配置、缓存）

有关强制执行规则的详细信息，请参阅 `references/arch-module-boundaries.md`。

### 2. 依赖注入

根据用例选择正确的提供者作用域：

| 作用域       | 生命周期                    | 用例                                   |
|-------------|------------------------------|---------------------------------------------|
| `DEFAULT`   | 单例（共享）           | 无状态服务、存储库            |
| `REQUEST`   | 每个请求实例         | 请求范围数据（租户、用户上下文）  |
| `TRANSIENT` | 每次注入新实例   | 有状态工具、每个消费者缓存     |

- 默认使用 `DEFAULT` 作用域 — 仅在合理时使用 `REQUEST` 或 `TRANSIENT`
- 仅使用构造函数注入 — 避免属性注入
- 使用 `useClass`、`useValue`、`useFactory` 或 `useExisting` 注册自定义提供者

有关强制执行规则的详细信息，请参阅 `references/di-provider-scoping.md`。

### 3. 请求生命周期

理解和尊重 NestJS 请求处理管道：

```
Middleware → Guards → Interceptors (before) → Pipes → Route Handler → Interceptors (after) → Exception Filters
```

- **Middleware**：横切关注点（日志记录、CORS、请求体解析）
- **Guards**：授权和身份验证检查（返回 `true`/`false`）
- **Interceptors**：转换响应数据、添加缓存、测量时间
- **Pipes**：验证和转换输入参数
- **Exception Filters**：捕获和格式化错误响应

### 4. 错误处理

跨应用程序标准化错误响应：

- 扩展 `HttpException` 以处理 HTTP 特定错误
- 创建特定于领域的异常类（例如，`OrderNotFoundException`）
- 实现全局 `ExceptionFilter` 以保持一致的错误格式化
- 使用 Result 模式处理预期的业务逻辑失败
- 永远不要无声地吞下异常

有关强制执行规则的详细信息，请参阅 `references/error-exception-filters.md`。

### 5. 验证

在 API 边界强制执行输入验证：

- 使用 `transform: true` 和 `whitelist: true` 全局启用 `ValidationPipe`
- 使用 `class-validator` 装饰器装饰所有 DTO 属性
- 使用 `class-transformer` 进行类型转换（`@Type()`、`@Transform()`）
- 为创建、更新和响应操作创建单独的 DTO
- 永远不要信任原始用户输入 — 验证所有内容

有关强制执行规则的详细信息，请参阅 `references/api-validation-dto.md`。

### 6. 数据库模式（Drizzle ORM）

遵循 NestJS 提供者约定集成 Drizzle ORM：

- 将 Drizzle 客户端包装在可注入提供者中
- 使用 Repository 模式进行数据访问封装
- 在每个领域模块的专用模式文件中定义模式
- 使用事务处理多步骤操作
- 将数据库逻辑从控制器中分离

有关强制执行规则的详细信息，请参阅 `references/db-drizzle-patterns.md`。

## 最佳实践

| 领域               | 应该                                      | 不应该                                    |
|--------------------|------------------------------------------|------------------------------------------|
| 模块            | 每个模块对应一个领域功能            | 将所有内容都放在 `AppModule` 中           |
| DI 作用域         | 默认使用单例作用域               | 无合理理由使用 `REQUEST` 作用域         |
| 错误处理     | 自定义异常过滤器 + 领域错误            | 使用 `try/catch` 并 `console.log`      |
| 验证         | 全局 `ValidationPipe` + DTO 装饰器            | 控制器中手动 `if` 检查                |
| 数据库           | 使用注入客户端的 Repository 模式  | 控制器中直接执行数据库查询         |
| 测试            | 单元测试服务，端到端测试控制器            | 跳过测试或测试实现细节                |
| 配置      | 使用 `@nestjs/config` 和类型化模式      | 硬编码值或使用 `process.env`     |

## 示例

### 示例：带验证的新领域模块

在构建 "产品" 功能时，请遵循以下工作流程：

**1. 创建具有适当封装的模块：**
```typescript
// product/product.module.ts
@Module({
  imports: [DatabaseModule],
  controllers: [ProductController],
  providers: [ProductService, ProductRepository],
  exports: [ProductService], // 仅导出其他模块需要的
})
export class ProductModule {}
```

**2. 创建经过验证的 DTO：**
```typescript
// product/dto/create-product.dto.ts
import { IsString, IsNumber, IsPositive, MaxLength } from 'class-validator';

export class CreateProductDto {
  @IsString() @MaxLength(255) readonly name: string;
  @IsNumber() @IsPositive() readonly price: number;
}
```

**3. 带错误处理的 Service：**
```typescript
@Injectable()
export class ProductService {
  constructor(private readonly productRepository: ProductRepository) {}

  async findById(id: string): Promise<Product> {
    const product = await this.productRepository.findById(id);
    if (!product) throw new ProductNotFoundException(id);
    return product;
  }
}
```

**4. 验证模块注册：**
```bash
# 检查模块是否在 AppModule 中导入
grep -r "ProductModule" src/app.module.ts

# 运行端到端测试以确认导出是否正常工作
npx jest --testPathPattern="product"
```

## 限制和警告

1. **不要无合理理由混合作用域** — `REQUEST` 作用域提供者会级联到所有依赖项
2. **永远不要从控制器直接访问数据库** — 始终通过服务和存储库层
3. **避免使用 `forwardRef()`** — 重构模块以消除循环依赖
4. **不要跳过 `ValidationPipe`** — 始终使用 DTO 在 API 边界进行验证
5. **永远不要硬编码密钥** — 使用 `@nestjs/config` 和环境变量
6. **保持模块专注** — 每个模块一个领域功能，避免 "神模块"

## 参考

- `references/architecture.md` — 深入探讨 NestJS 架构模式
- `references/` — 带有正确/错误示例的单独强制执行规则
- `assets/templates/` — 常见 NestJS 组件的启动模板
