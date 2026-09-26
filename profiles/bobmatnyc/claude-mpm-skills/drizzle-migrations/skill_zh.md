# Drizzle ORM 数据库迁移 (TypeScript)

使用 Drizzle ORM 为 TypeScript/JavaScript 项目进行迁移优先的数据库开发工作流程。

## 何时使用此技能

在以下情况下使用此技能：
- 在 TypeScript/JavaScript 项目中使用 Drizzle ORM
- 需要创建或修改数据库模式
- 希望采用迁移优先的开发工作流程
- 设置新的数据库表或列
- 需要确保跨环境模式的一致性

## 核心原则：迁移优先开发

**关键规则**：模式变更必须始终以迁移开始，绝不能先代码后迁移。

### 为什么采用迁移优先？
- ✅ SQL 迁移是唯一的真实来源
- ✅ 防止不同环境之间的模式漂移
- ✅ 支持回滚和版本控制
- ✅ 强制显式模式设计决策
- ✅ 从迁移生成 TypeScript 类型
- ✅ CI/CD 可以验证模式变更

### 反模式（先代码后迁移）
❌ **错误**：先编写 TypeScript 模式
```typescript
// 不要这样开始
export const users = pgTable('users', {
  id: uuid('id').primaryKey(),
  email: text('email').notNull(),
});
```

### 正确模式（迁移优先）
✅ **正确**：先编写 SQL 迁移
```sql
-- drizzle/0001_add_users_table.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 完整迁移工作流程

### 第 1 步：在 SQL 迁移中设计模式

创建描述性的 SQL 迁移文件：

```sql
-- drizzle/0001_create_school_calendars.sql
CREATE TABLE school_calendars (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  academic_year TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 为查询性能添加索引
CREATE INDEX idx_school_calendars_school_id ON school_calendars(school_id);
CREATE INDEX idx_school_calendars_academic_year ON school_calendars(academic_year);

-- 添加约束
ALTER TABLE school_calendars
  ADD CONSTRAINT check_date_range
  CHECK (end_date > start_date);
```

**命名规范**：
- 使用连续编号：`0001_`，`0002_` 等
- 描述性名称：`create_school_calendars`，`add_user_roles`
- 格式：`XXXX_descriptive_name.sql`

### 第 2 步：生成 TypeScript 定义

Drizzle Kit 从 SQL 生成 TypeScript 类型：

```bash
# 生成 TypeScript 模式和快照
pnpm drizzle-kit generate

# 或使用 npm
npm run db:generate
```

**这将创建**：
1. TypeScript 模式文件（如果使用 `drizzle-kit push`）
2. `drizzle/meta/XXXX_snapshot.json` 中的快照文件
3. 迁移元数据

### 第 3 步：创建模式快照

快照用于检测模式漂移：

```json
// drizzle/meta/0001_snapshot.json (自动生成)
{
  "version": "5",
  "dialect": "postgresql",
  "tables": {
    "school_calendars": {
      "name": "school_calendars",
      "columns": {
        "id": {
          "name": "id",
          "type": "uuid",
          "primaryKey": true,
          "notNull": true,
          "default": "gen_random_uuid()"
        },
        "school_id": {
          "name": "school_id",
          "type": "uuid",
          "notNull": true
        }
      }
    }
  }
}
```

**快照在版本控制中**：
- ✅ 提交快照到 git
- ✅ 在 CI 中启用漂移检测
- ✅ 记录模式历史

### 第 4 步：实现 TypeScript 模式

现在编写与 SQL 迁移镜像的 TypeScript 模式：

```typescript
// src/lib/db/schema/school/calendar.ts
import { pgTable, uuid, date, text, timestamp } from 'drizzle-orm/pg-core';
import { schools } from './school';

export const schoolCalendars = pgTable('school_calendars', {
  id: uuid('id').primaryKey().defaultRandom(),
  schoolId: uuid('school_id')
    .notNull()
    .references(() => schools.id, { onDelete: 'cascade' }),
  startDate: date('start_date').notNull(),
  endDate: date('end_date').notNull(),
  academicYear: text('academic_year').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

// 类型推断
export type SchoolCalendar = typeof schoolCalendars.$inferSelect;
export type NewSchoolCalendar = typeof schoolCalendars.$inferInsert;
```

**关键点**：
- 列名与 SQL 完全匹配：`school_id` → `'school_id'`
- TypeScript 属性名使用 camelCase：`schoolId`
- 约束和索引在 SQL 中定义，不在 TypeScript 中
- 外键引用其他表

### 第 5 步：按领域组织模式

按可维护性组织模式结构：

```
src/lib/db/schema/
├── index.ts              # 导出所有模式
├── school/
│   ├── index.ts
│   ├── district.ts
│   ├── holiday.ts
│   ├── school.ts
│   └── calendar.ts
├── providers.ts
├── cart.ts
└── users.ts
```

**index.ts** (导出所有)：
```typescript
// src/lib/db/schema/index.ts
export * from './school';
export * from './providers';
export * from './cart';
export * from './users';
```

**school/index.ts**：
```typescript
// src/lib/db/schema/school/index.ts
export * from './district';
export * from './holiday';
export * from './school';
export * from './calendar';
```

### 第 6 步：在 CI 中添加质量检查

在 CI/CD 中验证模式一致性：

```yaml
# .github/workflows/quality.yml
name: 质量检查

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: 设置 Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: 安装依赖
        run: pnpm install --frozen-lockfile

      - name: 检查数据库模式漂移
        run: pnpm drizzle-kit check

      - name: 验证迁移（干运行）
        run: pnpm drizzle-kit push --dry-run
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}

      - name: 运行类型检查
        run: pnpm tsc --noEmit

      - name: 代码风格检查
        run: pnpm lint
```

**CI 检查说明**：
- `drizzle-kit check`：验证快照与模式匹配
- `drizzle-kit push --dry-run`：测试迁移但不应用
- 类型检查：确保 TypeScript 可以编译
- 代码风格检查：强制执行代码风格

### 第 7 步：在预发布环境测试

在生产环境之前，在预发布环境测试迁移：

```bash
# 1. 在预发布环境运行迁移
STAGING_DATABASE_URL="..." pnpm drizzle-kit push

# 2. 验证模式
pnpm drizzle-kit check

# 3. 测试受影响的 API 路由
curl https://staging.example.com/api/schools/calendars

# 4. 检查数据完整性问题
# 运行查询以验证数据是否正确

# 5. 监控日志以查找错误
# 检查应用程序日志以查找与迁移相关的错误
```

**预发布环境检查清单**：
- [ ] 迁移无错误运行
- [ ] 模式漂移检查通过
- [ ] 使用新模式的 API 路由工作正常
- [ ] 无数据完整性问题
- [ ] 应用程序日志无错误
- [ ] 查询性能可接受

## 常见迁移模式

### 添加列

```sql
-- drizzle/0005_add_user_phone.sql
ALTER TABLE users
ADD COLUMN phone TEXT;

-- 如果按电话查询，添加索引
CREATE INDEX idx_users_phone ON users(phone);
```

TypeScript:
```typescript
export const users = pgTable('users', {
  id: uuid('id').primaryKey(),
  email: text('email').notNull(),
  phone: text('phone'), // 新列
});
```

### 创建关联表

```sql
-- drizzle/0006_create_provider_specialties.sql
CREATE TABLE provider_specialties (
  provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
  specialty_id UUID NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
  PRIMARY KEY (provider_id, specialty_id)
);

CREATE INDEX idx_provider_specialties_provider ON provider_specialties(provider_id);
CREATE INDEX idx_provider_specialties_specialty ON provider_specialties(specialty_id);
```

TypeScript:
```typescript
export const providerSpecialties = pgTable('provider_specialties', {
  providerId: uuid('provider_id')
    .notNull()
    .references(() => providers.id, { onDelete: 'cascade' }),
  specialtyId: uuid('specialty_id')
    .notNull()
    .references(() => specialties.id, { onDelete: 'cascade' }),
}, (table) => ({
  pk: primaryKey(table.providerId, table.specialtyId),
}));
```

### 修改列类型

```sql
-- drizzle/0007_change_price_to_decimal.sql
ALTER TABLE services
ALTER COLUMN price TYPE DECIMAL(10, 2);
```

TypeScript:
```typescript
import { decimal } from 'drizzle-orm/pg-core';

export const services = pgTable('services', {
  id: uuid('id').primaryKey(),
  name: text('name').notNull(),
  price: decimal('price', { precision: 10, scale: 2 }).notNull(),
});
```

### 添加约束

```sql
-- drizzle/0008_add_email_constraint.sql
ALTER TABLE users
ADD CONSTRAINT users_email_unique UNIQUE (email);

ALTER TABLE users
ADD CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');
```

## 配置

### drizzle.config.ts

```typescript
import type { Config } from 'drizzle-kit';

export default {
  schema: './src/lib/db/schema/index.ts',
  out: './drizzle',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
} satisfies Config;
```

### package.json 脚本

```json
{
  "scripts": {
    "db:generate": "drizzle-kit generate:pg",
    "db:push": "drizzle-kit push:pg",
    "db:studio": "drizzle-kit studio",
    "db:check": "drizzle-kit check:pg",
    "db:up": "drizzle-kit up:pg"
  }
}
```

## 迁移测试工作流程

### 本地测试

```bash
# 1. 创建迁移
echo "CREATE TABLE test (...)" > drizzle/0009_test.sql

# 2. 生成 TypeScript
pnpm db:generate

# 3. 推送到本地数据库
pnpm db:push

# 4. 验证模式
pnpm db:check

# 5. 在应用程序中测试
pnpm dev
# 手动测试受影响的特性

# 6. 运行测试
pnpm test
```

### 回滚策略

```sql
-- drizzle/0010_add_feature.sql (up 迁移)
CREATE TABLE new_feature (...);

-- drizzle/0010_add_feature_down.sql (down 迁移)
DROP TABLE new_feature;
```

应用回滚：
```bash
# 手动运行 down 迁移
psql $DATABASE_URL -f drizzle/0010_add_feature_down.sql
```

## 最佳实践

### 应做
- ✅ 先编写 SQL 迁移
- ✅ 使用描述性迁移名称
- ✅ 为外键添加索引
- ✅ 在迁移中包含约束
- ✅ 在生产前在预发布环境测试迁移
- ✅ 将快照提交到版本控制
- ✅ 按领域组织模式
- ✅ 在 CI 中使用 `drizzle-kit check`

### 不应做
- ❌ 绝不先编写 TypeScript 模式
- ❌ 不要跳过预发布测试
- ❌ 不要修改旧的迁移（创建新的）
- ❌ 不要忘记添加索引
- ❌ 不要在生产中使用 `drizzle-kit push`（使用适当的迁移）
- ❌ 不要提交未包含快照的生成文件

## 故障排除

### 检测到模式漂移
**错误**：`Schema drift detected`

**解决方案**：
```bash
# 查看变更
pnpm drizzle-kit check

# 重新生成快照
pnpm drizzle-kit generate

# 审查变更并提交
git add drizzle/meta/
git commit -m "更新模式快照"
```

### 迁移在预发布环境失败
**错误**：迁移因数据约束违规失败

**解决方案**：
1. 回滚迁移
2. 创建数据迁移脚本
3. 先运行数据迁移
4. 然后运行模式迁移

```sql
-- 首先：迁移数据
UPDATE users SET status = 'active' WHERE status IS NULL;

-- 然后：添加约束
ALTER TABLE users
ALTER COLUMN status SET NOT NULL;
```

### TypeScript 类型与数据库不同步
**错误**：TypeScript 类型与数据库不匹配

**解决方案**：
```bash
# 重新生成所有内容
pnpm db:generate
pnpm tsc --noEmit

# 如果仍然损坏，检查模式文件
# 确保列名与 SQL 完全匹配
```

## 相关技能

- `universal-data-database-migration` - 通用迁移模式
- `toolchains-typescript-data-drizzle` - Drizzle ORM 使用模式
- `toolchains-typescript-core` - TypeScript 最佳实践
- `universal-debugging-verification-before-completion` - 验证工作流程
