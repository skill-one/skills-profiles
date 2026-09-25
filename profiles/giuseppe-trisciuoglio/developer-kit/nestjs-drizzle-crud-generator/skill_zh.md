# NestJS Drizzle CRUD 生成器

## 概述

使用 Drizzle ORM 自动为 NestJS 应用生成完整的 CRUD 模块。遵循 zaccheroni-monorepo 模式创建所有必要文件：功能模块、控制器、服务、Zod 验证的 DTO、Drizzle 模式以及 Jest 单元测试。

## 使用场景

- 创建具有完整 CRUD 端点的实体模块
- 在 NestJS 中构建数据库支持的功能
- 生成具有 Zod 验证的类型安全 DTO
- 添加使用 Drizzle ORM 查询的服务
- 使用模拟数据库创建单元测试

## 使用说明

### 第 1 步：定义实体字段

收集实体定义：
- 实体名称（例如，`user`、`product`、`order`）
- 字段列表及其类型（支持的类型请参阅 `references/field-types.md`）
- 必填字段与可选字段及其默认值

### 第 2 步：运行生成器

```bash
python scripts/generate_crud.py --feature <name> --fields '<json-array>' --output <path>
```

### 第 3 步：验证生成的文件

检查是否创建了所有预期文件：

```bash
ls -la libs/server/<feature-name>/src/lib/
```

预期结构：
```
controllers/
services/
dto/
schema/
<feature>-feature.module.ts
```

### 第 4 步：运行 TypeScript 编译

```bash
cd libs/server && npx tsc --noEmit
```

### 第 5 步：执行单元测试

```bash
cd libs/server && npm test -- --testPathPattern=<feature-name>
```

## 示例

### 生成 User 模块

```bash
python scripts/generate_crud.py \
  --feature user \
  --fields '[{"name": "name", "type": "string", "required": true}, {"name": "email", "type": "email", "required": true}, {"name": "password", "type": "string", "required": true}]' \
  --output ./libs/server
```

### 生成 Product 模块

```bash
python scripts/generate_crud.py \
  --feature product \
  --fields '[{"name": "title", "type": "string", "required": true}, {"name": "price", "type": "number", "required": true}, {"name": "description", "type": "text", "required": false}, {"name": "inStock", "type": "boolean", "required": false, "default": true}]' \
  --output ./libs/server
```

## 生成的结构

```
libs/server/{feature-name}/
├── src/
│   ├── index.ts
│   └── lib/
│       ├── {feature}-feature.module.ts
│       ├── controllers/
│       │   ├── index.ts
│       │   └── {feature}.controller.ts
│       ├── services/
│       │   ├── index.ts
│       │   ├── {feature}.service.ts
│       │   └── {feature}.service.spec.ts
│       ├── dto/
│       │   ├── index.ts
│       │   └── {feature}.dto.ts
│       └── schema/
│           └── {feature}.table.ts
```

## 功能特性

### 模块
- 使用 `forRootAsync` 模式进行懒加载配置
- 导出生成的服务供其他模块使用
- 为功能表导入 DatabaseModule

### 控制器
- 完整的 CRUD 端点：POST、GET、PATCH、DELETE
- 分页的查询参数验证
- Zod 验证管道集成

### 服务
- Drizzle ORM 查询方法
- 支持软删除（通过 `deletedAt` 列）
- 基于 limit/offset 的分页
- 过滤支持
- 类型安全的返回类型

### DTO
- 创建和更新用的 Zod 模式
- 过滤用的查询参数模式
- NestJS DTO 集成

### 测试
- Jest 测试套件
- 模拟的 Drizzle 数据库
- 所有 CRUD 操作的测试用例

## 手动集成

生成后，集成到您的应用模块：

```typescript
// app.module.ts
import { {{FeatureName}}FeatureModule } from '@your-org/server-{{feature}}';

@Module({
  imports: [
    {{FeatureName}}FeatureModule.forRootAsync({
      useFactory: () => ({
        defaultPageSize: 10,
        maxPageSize: 100,
      }),
    }),
  ],
})
export class AppModule {}
```

## 依赖项

必需的包：
- `@nestjs/common`
- `@nestjs/core`
- `drizzle-orm`
- `drizzle-zod`
- `zod`
- `nestjs-zod`

## 最佳实践

1. **提交前验证**：在提交生成的代码前，始终运行 `tsc --noEmit` 和测试
2. **自定义服务**：在验证后向生成的服务添加业务逻辑
3. **数据库迁移**：为生成的 Drizzle 模式单独创建迁移
4. **使用生成类型**：在应用代码中引用生成类型
5. **审查 DTO**：根据 API 需求调整 Zod 验证规则

## 限制和警告

- **仅软删除**：删除操作使用软删除（`deletedAt` 时间戳）。硬删除需要手动修改
- **无认证**：生成的代码不包含认证守卫 - 根据安全需求添加它们
- **仅基本 CRUD**：复杂的查询、事务或业务逻辑必须手动实现
- **JSON 转义**：在命令行传递字段时，使用单引号包围 JSON 数组
