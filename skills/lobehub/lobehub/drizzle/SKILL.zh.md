---
name: drizzle
description: 用于 Drizzle 模式和查询：表、索引、关系、连接和推断类型。发布属于 db-migrations。
---

# Drizzle ORM 模式指南

> **添加模型或存储库？** 在相同的 PR 中提交一个兄弟测试——`packages/database/src/models/**` 或 `src/repositories/**` 下每个新文件都需要一个匹配的 `__tests__/<name>.test.ts`。有关 `getTestDB()` 集成模式、用户隔离测试、BM25 `describe.skipIf(!isServerDB)` 守卫和模式陷阱，请参阅 **测试** 技能（`.agents/skills/testing/references/db-model-test.md`）。CI 的覆盖率补丁门不会可靠地捕获全新的未测试文件，所以这是你的责任。

## 配置

- 配置：`drizzle.config.ts`
- 模式：`packages/database/src/schemas/`
- 迁移：`packages/database/migrations/`
- 语法：`postgresql` with `strict: true`

## 辅助函数

位置：`packages/database/src/schemas/_helpers.ts`

- `timestamptz(name)`：带时区的时间戳
- `createdAt()`, `updatedAt()`, `accessedAt()`：标准时间戳列
- `timestamps`：包含所有三个的易于展开的对象

## 命名约定

- **表**：复数蛇形命名（`users`, `session_groups`）
- **列**：蛇形命名（`user_id`, `created_at`）
- **新表**：命名新表之前检查附近现有的表。保留已建立的名词家族和后缀。例如，如果用户范围表是 `user_xxx_logs`，则工作区范围的对立表应该是 `workspace_xxx_logs`，而不是 `workspace_xxx_records` 或其他新同义词。

```typescript
// ✅ 好：遵循现有的用户/工作区表家族（名称是说明性的——用真实的名词替换 `widget`）。
export const userWidgetLogs = pgTable('user_widget_logs', { ... });
export const workspaceWidgetLogs = pgTable('workspace_widget_logs', { ... });

// ❌ 坏：为同一概念引入新的后缀。
export const workspaceWidgetRecords = pgTable('workspace_widget_records', { ... });
```

## 列定义

### 主键

不要使用自增主键（`serial`, `bigserial`, 生成的身份列）。它们在跨数据库迁移、恢复和数据复制作业期间会创建序列状态问题。优先考虑来自应用程序生成器的文本 ID（`idGenerator`, `createNanoId`）或内部表使用 `uuid`。

当表通常拥有 ID 生成时，保留 `$defaultFn(...)`。调用者仍然可以传递一个显式的 `id`；默认仅在插入省略它时运行。不要因为一个流程需要提供请求范围的 ID 就删除默认值。

```typescript
// ✅ 好：应用程序生成的文本 ID；显式插入仍然可以覆盖它。
id: text('id')
  .primaryKey()
  .$defaultFn(() => idGenerator('agents'))
  .notNull(),

// ❌ 坏：序列状态在数据库迁移和恢复时很脆弱。
id: serial('id').primaryKey(),
```

ID 前缀使实体类型可区分。对于内部表，使用 `uuid`。

不要在新表上使用复合主键。给每个表一个单列的代理 PK，并在 `uniqueIndex` 中携带业务唯一性。PK 列不能为空，所以当唯一性范围后来通过可空的维度增长时，必须拆分和重建复合 PK——当 `ai_providers` / `ai_models` 为工作区范围时（迁移 0110–0111 用代理 `_id` 加部分唯一索引替换了它们的复合 PK）就是这样发生的。唯一索引仍然可以作为 `onConflictDoUpdate` 插入的仲裁者。

```typescript
// ✅ 好：代理 PK；唯一性范围可以在不重建 PK 的情况下演变。
export const workspaceUserSettings = pgTable(
  'workspace_user_settings',
  {
    id: uuid('id').defaultRandom().notNull().primaryKey(),
    workspaceId: text('workspace_id').references(() => workspaces.id, { onDelete: 'cascade' }).notNull(),
    userId: text('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
    ...timestamps,
  },
  (t) => [uniqueIndex('workspace_user_settings_workspace_id_user_id_unique').on(t.workspaceId, t.userId)],
);

// ❌ 坏：锁定到这些确切列；添加可空的范围列（workspaceId, deviceId, …）后被迫进行完整的 PK 重建迁移。
(t) => [primaryKey({ columns: [t.workspaceId, t.userId] })],
```

现有的复合 PK 是遗留的——除非它们阻止范围更改，否则不要单独处理，然后按 0110–0111 的方式迁移。

### 外键

```typescript
userId: text('user_id')
  .references(() => users.id, { onDelete: 'cascade' })
  .notNull(),
```

### 时间戳

```typescript
...timestamps,  // 从 _helpers.ts 展开而来
```

### 可选和未定义值

除非领域已经具有该明确状态并且现有代码始终一致地使用它，否则不要引入人为的哨兵字符串来表示缺失值，例如 `unknown`。优先考虑可空列、可选 TypeScript 字段或在值确实缺失时使用单独的具体状态枚举。

```typescript
// ✅ 好：直到自定义执行尝试实际运行时才存在（`packages/database/src/schemas/agentIntervention.ts`）。
export const AGENT_INTERVENTION_CUSTOM_EXECUTION_STATES = ['pending', 'executing', 'completed'] as const;
export type AgentInterventionCustomExecutionState =
  (typeof AGENT_INTERVENTION_CUSTOM_EXECUTION_STATES)[number];

customExecutionState: text('custom_execution_state').$type<AgentInterventionCustomExecutionState>(),

// ❌ 坏：发明了一个新的状态，调用者现在需要在每个地方处理它。
export type AgentInterventionCustomExecutionState = 'pending' | 'executing' | 'completed' | 'unknown';

customExecutionState: text('custom_execution_state')
  .$type<AgentInterventionCustomExecutionState>()
  .notNull()
  .default('unknown');
```

### 数据库枚举

默认情况下**不**使用 PostgreSQL/Drizzle `pgEnum`。数据库枚举在安全地演变时很昂贵：添加成员需要迁移，删除或重命名成员很笨拙，部署顺序变得更加脆弱。

对于产品/业务状态，使用 `text()` 或 `varchar()` 并通过 `$type<...>()` 提供 TypeScript 值类型。将那些仅限 TypeScript 的值类型保留在领域/共享类型模块中，然后将它们导入模式中。对于云数据库模式，这通常意味着 `cloudDB/types.ts`。

不要复制现有的数据库枚举作为模式。将它们视为遗留或明确审查的例外。如果似乎需要新的 `pgEnum`，请停止并说明为什么值集实际上是不可变的，以及为什么迁移成本是可接受的。

### 字段描述

对于名称本身无法说明其含义的列，在模式字段上添加 JSDoc。当它澄清存储的值或写入它的生命周期时刻时，包含一个具体示例。这对于外部 ID、生命周期状态、非规范快照、JSONB 信号以及名称可能意味着请求 ID 或持久化行 ID 的字段尤其重要。

```typescript
// ✅ 好：首先解释表的业务对象，然后仅记录非明显生命周期字段
// (`packages/database/src/schemas/agentIntervention.ts`)。
/**
 * 私有解决/发件箱记录。与 `agent_interventions` 不同，此表可能会保留用户编辑的参数，以便在应用程序断开连接后可靠地交付已声明的决定。它永远不会是通知有效负载。
 */
export const agentInterventionResolutions = pgTable('agent_intervention_resolutions', {
  /** 持久化操作的拥有者，与解决者不同。 */
  userId: text('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),

  /** 私有执行结果；永远不会选择到 Review 或通知 DTO 中。 */
  customExecutionResult: jsonb('custom_execution_result').$type<AgentInterventionCustomExecutionResult>(),

  /** 单调租赁尝试，在等待时从零开始。 */
  customExecutionAttempt: integer('custom_execution_attempt'),
});

// ❌ 坏：注释重述明显的列名，而没有添加领域含义。
/** 用户邮箱 */
email: text('email'),
```

### JSONB 类型

避免使用 `Record<string, unknown>` 或类似的松散 JSONB 类型作为模式列。定义一个描述预期 JSON 形状的具体接口，即使大多数属性是可选的。这使调用者、迁移和审查查询对齐相同的合同。

```typescript
// packages/types/src/agent/agentIntervention.ts +
// packages/database/src/schemas/agentIntervention.ts
interface AgentInterventionCustomExecutionResult {
  content: string;
  pluginState: Record<string, unknown>;
}

customExecutionResult: jsonb('custom_execution_result').$type<AgentInterventionCustomExecutionResult>(),
```

```typescript
// ❌ 坏：隐藏了合同，并使下游访问无类型。
customExecutionResult: jsonb('custom_execution_result').$type<Record<string, unknown>>(),
```

松散类型的 JSONB 列通常是更深层次问题的症状：该列是推测性保留的（“用于未来扩展”），并且实际上没有写入它。不要添加 `metadata` / `extra` JSONB 列以供假设的未来需要——只有当具体写入与它一起交付时，列才配得上它的位置。当审查发现此类列时，修复方法是**删除列**，而不是为不存在的数据发明接口；一旦实际需求到来，就添加一个正确类型的列。

### 索引

```typescript
// 返回数组（对象样式已弃用）
(t) => [uniqueIndex('client_id_user_id_unique').on(t.clientId, t.userId)],
```

## 类型推断

```typescript
export const insertAgentSchema = createInsertSchema(agents);
export type NewAgent = typeof agents.$inferInsert;
export type AgentItem = typeof agents.$inferSelect;
```

## 示例模式

```typescript
export const agents = pgTable(
  'agents',
  {
    id: text('id')
      .primaryKey()
      .$defaultFn(() => idGenerator('agents'))
      .notNull(),
    slug: varchar('slug', { length: 100 })
      .$defaultFn(() => randomSlug(4))
      .unique(),
    userId: text('user_id')
      .references(() => users.id, { onDelete: 'cascade' })
      .notNull(),
    clientId: text('client_id'),
    chatConfig: jsonb('chat_config').$type<LobeAgentChatConfig>(),
    ...timestamps,
  },
  (t) => [uniqueIndex('client_id_user_id_unique').on(t.clientId, t.userId)],
);
```

## 常见模式

### 连接表（多对多）

上述代理-PK 规则也适用于连接表——配对唯一性应放在 `uniqueIndex` 中，而不是复合 PK（许多现有的连接表仍然使用复合 PK；这是遗留的，不是模板）：

```typescript
export const agentsKnowledgeBases = pgTable(
  'agents_knowledge_bases',
  {
    id: uuid('id').defaultRandom().notNull().primaryKey(),
    agentId: text('agent_id')
      .references(() => agents.id, { onDelete: 'cascade' })
      .notNull(),
    knowledgeBaseId: text('knowledge_base_id')
      .references(() => knowledgeBases.id, { onDelete: 'cascade' })
      .notNull(),
    userId: text('user_id')
      .references(() => users.id, { onDelete: 'cascade' })
      .notNull(),
    enabled: boolean('enabled').default(true),
    ...timestamps,
  },
  (t) => [
    uniqueIndex('agents_knowledge_bases_agent_id_knowledge_base_id_unique').on(
      t.agentId,
      t.knowledgeBaseId,
    ),
  ],
);
```

## 查询风格

**始终使用 `db.select()` 构建器 API。永远不要使用 `db.query.*` 关系 API**（`findMany`, `findFirst`, `with:`）。

关系 API 生成复杂的横向连接，使用 `json_build_array`，这些连接脆弱且难以调试。

### 选择单行

```typescript
// ✅ 好
const [result] = await this.db.select().from(agents).where(eq(agents.id, id)).limit(1);
return result;

// ❌ 坏：关系 API
return this.db.query.agents.findFirst({
  where: eq(agents.id, id),
});
```

### 带连接选择

```typescript
// ✅ 好：显式选择 + leftJoin
const rows = await this.db
  .select({
    runId: agentEvalRunTopics.runId,
    score: agentEvalRunTopics.score,
    testCase: agentEvalTestCases,
    topic: topics,
  })
  .from(agentEvalRunTopics)
  .leftJoin(agentEvalTestCases, eq(agentEvalRunTopics.testCaseId, agentEvalTestCases.id))
  .leftJoin(topics, eq(agentEvalRunTopics.topicId, topics.id))
  .where(eq(agentEvalRunTopics.runId, runId))
  .orderBy(asc(agentEvalRunTopics.createdAt));

// ❌ 坏：关系 API 使用 `with:`
return this.db.query.agentEvalRunTopics.findMany({
  where: eq(agentEvalRunTopics.runId, runId),
  with: { testCase: true, topic: true },
});
```

### 带聚合选择

```typescript
// ✅ 好：选择 + leftJoin + groupBy
const rows = await this.db
  .select({
    id: agentEvalDatasets.id,
    name: agentEvalDatasets.name,
    testCaseCount: count(agentEvalTestCases.id).as('testCaseCount'),
  })
  .from(agentEvalDatasets)
  .leftJoin(agentEvalTestCases, eq(agentEvalDatasets.id, agentEvalTestCases.datasetId))
  .groupBy(agentEvalDatasets.id);
```

### 原生 SQL 和高级查询

尽可能使用 Drizzle 构建器，当查询清晰地使用 `select`、`insert().select()`、`update().from()`、连接、CTE 和 `groupBy` 时——这使表/列引用与模式绑定，因此更改会作为 TypeScript 错误出现。在构建器内，表达式级 `sql<T>` 对于缺少辅助功能的特性（JSON 路径、转换、聚合、`CASE`、`NOW()`）是好的。行锁定是子句，不是表达式——使用 `.for('update')`，永远不要使用原始 `FOR UPDATE`。

仅在 null 处理是必需的数据库语义的一部分时（可空的 JSONB 追加/合并，“保留第一个非 null”）才使用 `COALESCE`。不要在普通的插入标量中散布 `COALESCE(excluded.col, current.col)` 只是为了避免更新对象——仅从定义的值构建 `set`，并将任何剩余的 SQL 隐藏在命名的辅助函数（`appendJsonbArray`、`mergeJsonbObject`、`keepFirstValue`）后面，以便方法读取为业务意图，而不是 SQL 管道。

```typescript
// ✅ 标量仅当存在时包含；SQL 隐藏在命名的辅助函数后面。
// (`userWidgetLogs` 是说明性的——用实际表替换它。)
const updateValues = compactUndefined({
  email: record.email ?? undefined,
  ip: record.ip ?? undefined,
});
await db.insert(userWidgetLogs).values(values).onConflictDoUpdate({
  set: { ...updateValues, events: appendJsonbArray(userWidgetLogs.events, event), updatedAt: now },
  target: userWidgetLogs.id,
});

// ❌ 每个标量都变成 SQL 管道。
set: {
  email: sql`COALESCE(excluded.email, ${userWidgetLogs.email})`,
  ip: sql`COALESCE(excluded.ip, ${userWidgetLogs.ip})`,
}
```

在重构原生 SQL 时：

- 在延迟敏感路径上保留查询形状。如果原生 SQL 是单轮次，不要将其拆分为多个基于深度的查询，只是为了丢弃 `execute`。
- 使用 `$with(...)` + `insert().select()` / `update().from()` 进行多步骤单轮次写入，Drizzle 可以表达的。
- 不要依赖 `execute<MyRow>(sql...)` 的安全性——它类型化行，但不会将选定的列与模式更改同步。
- 如果只有 PostgreSQL 功能 Drizzle 无法表达才起作用，请保留原生 SQL 并收紧它：插值中的模式引用、显式用户范围、狭窄的行接口和回归测试。

递归 CTE 是“保留原生”的典型用例——没有干净的 `WITH RECURSIVE` 构建器，重写将增加基于深度的轮次：

```typescript
interface TaskTreeRow {
  id: string;
  parent_task_id: string | null;
}

// execute<T> 可接受：没有干净的 WITH RECURSIVE 构建器。保留插值中的模式引用，并将每条腿限制到用户。
const { rows } = await db.execute<TaskTreeRow>(sql`
  WITH RECURSIVE task_tree AS (
    SELECT ${tasks.id}, ${tasks.parentTaskId}
    FROM ${tasks}
    WHERE ${tasks.id} = ${rootTaskId} AND ${tasks.createdByUserId} = ${userId}
    UNION ALL
    SELECT ${tasks.id}, ${tasks.parentTaskId}
    FROM ${tasks}
    JOIN task_tree ON ${tasks.parentTaskId} = task_tree.id
    WHERE ${tasks.createdByUserId} = ${userId}
  )
  SELECT * FROM task_tree
`);
```

### 一对多（分离查询）

当你需要一个父记录及其子记录时，使用两个查询而不是关系 `with:`：

```typescript
// ✅ 良好：两个简单的查询
const [dataset] = await this.db
  .select()
  .from(agentEvalDatasets)
  .where(eq(agentEvalDatasets.id, id))
  .limit(1);

if (!dataset) return undefined;

const testCases = await this.db
  .select()
  .from(agentEvalTestCases)
  .where(eq(agentEvalTestCases.datasetId, id))
  .orderBy(asc(agentEvalTestCases.sortOrder));

return { ...dataset, testCases };
```

## 数据库迁移

请参考 `db-migrations` 技能获取详细的迁移指南。
