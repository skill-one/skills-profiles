# DynamoDB-Toolbox v2 模式 (TypeScript)

## 概述

本技能提供使用 DynamoDB-Toolbox v2 与 AWS SDK v3 DocumentClient 的实用 TypeScript 模式。它专注于类型安全的模式建模、`.build()` 命令的使用以及生产就绪的单表设计。

## 何时使用

- 使用严格的 TypeScript 推断定义 DynamoDB 表和实体
- 使用 `item`、`string`、`number`、`list`、`set`、`map` 和 `record` 建模模式
- 通过 `.build()` 实现 `GetItem`、`PutItem`、`UpdateItem`、`DeleteItem`
- 使用主键和 GSI 构建查询和扫描访问路径
- 处理批量和事务性操作
- 设计使用计算键和实体模式的单表系统

## 说明

1. **从访问模式开始**：首先识别读写查询，然后设计键。
2. **创建表 + 实体边界**：使用单表设计时，一个表，多个实体。
3. **定义带约束的模式**：应用 `.key()`、`.required()`、`.default()`、`.transform()`、`.link()`。
4. **到处使用 `.build()` 命令**：避免临时构建命令以保持一致性和类型安全。
5. **添加查询/索引覆盖**：验证每个所需访问模式的 GSI/LSI 路径。
6. **有意使用批量和事务**：批量用于吞吐量，事务用于原子性。
7. **保持项目可进化**：使用可选字段、默认值和派生属性进行模式进化。

## 示例

### 安装和设置

```bash
npm install dynamodb-toolbox @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb
```

```typescript
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { Table } from 'dynamodb-toolbox/table';
import { Entity } from 'dynamodb-toolbox/entity';
import { item, string, number, list, map } from 'dynamodb-toolbox/schema';

const client = new DynamoDBClient({ region: process.env.AWS_REGION ?? 'eu-west-1' });
const documentClient = DynamoDBDocumentClient.from(client);

export const AppTable = new Table({
  name: 'app-single-table',
  partitionKey: { name: 'PK', type: 'string' },
  sortKey: { name: 'SK', type: 'string' },
  indexes: {
    byType: { type: 'global', partitionKey: { name: 'GSI1PK', type: 'string' }, sortKey: { name: 'GSI1SK', type: 'string' } }
  },
  documentClient
});
```

### 带修饰符和复杂属性的实体模式

```typescript
const now = () => new Date().toISOString();

export const UserEntity = new Entity({
  name: 'User',
  table: AppTable,
  schema: item({
    tenantId: string().required('always'),
    userId: string().required('always'),
    email: string().required('always').transform(input => input.toLowerCase()),
    role: string().enum('admin', 'member').default('member'),
    loginCount: number().default(0),
    tags: list(string()).default([]),
    profile: map({
      displayName: string().optional(),
      timezone: string().default('UTC')
    }).default({ timezone: 'UTC' })
  }),
  computeKey: ({ tenantId, userId }) => ({
    PK: `TENANT#${tenantId}`,
    SK: `USER#${userId}`,
    GSI1PK: `TENANT#${tenantId}#TYPE#USER`,
    GSI1SK: `EMAIL#${userId}`
  })
});
```

### `.build()` CRUD 命令

```typescript
import { PutItemCommand } from 'dynamodb-toolbox/entity/actions/put';
import { GetItemCommand } from 'dynamodb-toolbox/entity/actions/get';
import { UpdateItemCommand, $add } from 'dynamodb-toolbox/entity/actions/update';
import { DeleteItemCommand } from 'dynamodb-toolbox/entity/actions/delete';

await UserEntity.build(PutItemCommand)
  .item({ tenantId: 't1', userId: 'u1', email: 'A@Example.com' })
  .send();

const { Item } = await UserEntity.build(GetItemCommand)
  .key({ tenantId: 't1', userId: 'u1' })
  .send();

await UserEntity.build(UpdateItemCommand)
  .item({ tenantId: 't1', userId: 'u1', loginCount: $add(1) })
  .send();

await UserEntity.build(DeleteItemCommand)
  .key({ tenantId: 't1', userId: 'u1' })
  .send();
```

### 查询和扫描模式

```typescript
import { QueryCommand } from 'dynamodb-toolbox/table/actions/query';
import { ScanCommand } from 'dynamodb-toolbox/table/actions/scan';

const byTenant = await AppTable.build(QueryCommand)
  .query({
    partition: `TENANT#t1`,
    range: { beginsWith: 'USER#' }
  })
  .send();

const byTypeIndex = await AppTable.build(QueryCommand)
  .query({
    index: 'byType',
    partition: 'TENANT#t1#TYPE#USER'
  })
  .options({ limit: 25 })
  .send();

const scanned = await AppTable.build(ScanCommand)
  .options({ limit: 100 })
  .send();
```

### 批量和事务工作流

```typescript
import { BatchWriteCommand } from 'dynamodb-toolbox/table/actions/batchWrite';
import { TransactWriteCommand } from 'dynamodb-toolbox/table/actions/transactWrite';

await AppTable.build(BatchWriteCommand)
  .requests(
    UserEntity.build(PutItemCommand).item({ tenantId: 't1', userId: 'u2', email: 'u2@example.com' }),
    UserEntity.build(PutItemCommand).item({ tenantId: 't1', userId: 'u3', email: 'u3@example.com' })
  )
  .send();

await AppTable.build(TransactWriteCommand)
  .requests(
    UserEntity.build(PutItemCommand).item({ tenantId: 't1', userId: 'u4', email: 'u4@example.com' }),
    UserEntity.build(UpdateItemCommand).item({ tenantId: 't1', userId: 'u1', loginCount: $add(1) })
  )
  .send();
```

## 单表设计指南

- 将每个业务概念建模为严格的模式实体。
- 保持 PK/SK 可预测且可组合 (`TENANT#`、`USER#`、`ORDER#`)。
- 将访问路径编码到 GSI 键中，而不是内存过滤器中。
- 优先使用仅追加的时间线用于审计/历史数据。
- 通过范围分区和需要时分片控制热分区。

## 最佳实践

- 首先从访问模式设计键，然后派生实体属性。
- 保持键组合 (`computeKey`) 的单一事实来源以避免漂移。
- 仅在需要严格读后写时使用 `.options({ consistent: true })`。
- 优先使用目标查询而不是扫描以进行运行时请求路径。
- 添加条件表达式以实现幂等性和乐观并发控制。
- 在执行前验证批量和事务大小限制以避免部分失败。

## 约束和警告

- DynamoDB-Toolbox v2 依赖于 AWS SDK v3 DocumentClient 集成。
- 除非明确限制，否则避免在请求路径中使用表扫描。
- 使用条件写入进行并发敏感的更新。
- 事务有限且比单项写入慢；仅用于真正的原子需求。
- 在实现前验证键设计以针对目标吞吐量。

## 参考

Context7 精心策划的主要参考可在以下位置找到：

- `references/api-dynamodb-toolbox-v2.md`
