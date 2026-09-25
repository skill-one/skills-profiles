# Drizzle ORM 模式指南

> **添加模型或仓库？** 在同一 PR 中提交兄弟测试——`packages/database/src/models/**` 或 `src/repositories/**` 下每个新文件都需要一个匹配的 `__tests__/<name>.test.ts`。有关 `getTestDB()` 集成模式、用户隔离测试、BM25 `describe.skipIf(!isServerDB)` 守卫和模式陷阱，请参阅 **测试** 技能（`.agents/skills/testing/references/db-model-test.md`）。CI 的覆盖率补丁门不会可靠地捕获全新的未测试文件，所以这取决于你。

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
- **新表**：命名新表前检查附近现有的表。保留已建立的名词家族和后缀。例如，如果用户范围表是 `user_xxx_logs`，则工作区范围对应表应为 `workspace_xxx_logs`，而不是 `workspace_xxx_records` 或其他新同义词。

```typescript
// ✅ 良好：遵循现有的用户/工作区表家族。
export const userSignupLogs = pgTable('user_signup_logs', { ... });
export const workspaceSignupLogs = pgTable('workspace_signup_logs', { ... });

// ❌ 不良：为同一概念引入新的后缀。
export const workspaceSignupRecords = pgTable('workspace_signup_records', { ... });
```

## 列定义

### 主键

不要使用自动递增的主键（`serial`, `bigserial`, 生成的身份列）。它们在跨数据库迁移、恢复和数据复制作业期间会创建序列状态问题。优先考虑来自应用程序生成器的文本 ID（`idGenerator`, `createNanoId`）或 `uuid` 用于内部表。

当表通常拥有 ID 生成时保留 `$defaultFn(...)`。调用者仍然可以传递显式的 `id`；默认仅在插入省略它时运行。不要因为一个流程需要提供请求范围的 ID 而删除默认值。

```typescript
// ✅ 良好：应用程序生成的文本 ID；显式插入仍然可以覆盖它。
id: text('id')
  .primaryKey()
  .$defaultFn(() => idGenerator('agents'))
  .notNull(),

// ❌ 不良：序列状态在数据库迁移和恢复中很脆弱。
id: serial('id').primaryKey(),
```

ID 前缀使实体类型可区分。对于内部表，使用 `uuid`。

不要在新表上使用复合主键。给每个表一个单列的代理 PK，并在 `uniqueIndex` 中携带业务唯一性。PK 列不能为空，所以当唯一性范围后来通过可空维度增长时，必须拆分并重建复合 PK——当 `ai_providers` / `ai_models` 为工作区范围时（迁移 0110 用代理 `_id` 加部分唯一索引替换了它们的复合 PK）就是这样发生的。唯一索引仍然可以作为 `onConflictDoUpdate` 插入的仲裁者。

```typescript
// ✅ 良好：代理 PK；唯一性范围可以在不重建 PK 的情况下演变。
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

// ❌ 不良：锁定到确切这些列；添加可空的范围列（workspaceId, deviceId, …）后被迫进行完整的 PK 重构迁移。
(t) => [primaryKey({ columns: [t.workspaceId, t.userId] })],
```

现有的复合 PK 是遗留的——除非它们阻止范围更改，否则不要单独处理，然后按 0110 的方式迁移。

### 外键

```typescript
userId: text('user_id')
  .references(() => users.id, { onDelete: 'cascade' })
  .notNull(),
```

### 时间戳

```typescript
...timestamps,  // 从 _helpers.ts 展开
```

### 可选和未定义值

除非领域已有该明确状态且现有代码一致使用它，否则不要引入人工哨兵字符串表示缺失值，例如 `unknown`。优先考虑可空列、可选 TypeScript 字段或当值确实不存在时使用单独的具体状态枚举。

```typescript
// ✅ 良好：直到最终阶段写入真实决策前不存在。
export type UserSignupLogFinalDecision = 'allow' | 'block' | 'error';

finalDecision: varchar('final_decision', { length: 32 }).$type<UserSignupLogFinalDecision>(),

// ❌ 不良：发明了一个新的状态，调用者现在需要在每个地方处理它。
export type UserSignupLogFinalDecision = 'allow' | 'block' | 'error' | 'unknown';

finalDecision: varchar('final_decision', { length: 32 })
  .$type<UserSignupLogFinalDecision>()
  .notNull()
  .default('unknown');
```

### 数据库枚举

默认不使用 PostgreSQL/Drizzle `pgEnum`。数据库枚举在安全演进方面成本很高：添加成员需要迁移，删除或重命名成员很笨拙，部署顺序变得更加脆弱。

对于产品/业务状态，使用 `text()` 或 `varchar()` 并通过 `$type<...>()` 提供 TypeScript 值类型。将那些仅限 TS 的值类型保留在领域/共享类型模块中，然后导入到模式中。对于云数据库模式，这通常意味着 `cloudDB/types.ts`。

不要将现有数据库枚举作为模式复制。将它们视为遗留或明确审查的例外。如果似乎需要新的 `pgEnum`，请停止并说明为什么值集实际上是不可变的，以及为什么迁移成本可以接受。

### 字段描述

对于名称本身无法说明其含义的列，在模式字段上添加 JSDoc。当它澄清存储的值或写入它的生命周期时刻时，包含具体示例。这对于外部 ID、生命周期状态、非规范化快照、JSONB 信号以及名称可能表示请求 ID 或持久化行 ID 的字段尤其重要。

```typescript
// ✅ 良好：首先解释表的业务对象，然后仅文档化非明显的生命周期或风险控制字段。
/**
 * 用户注册日志 - 每个注册流程一行，收集认证提供者在创建用户前后各阶段的风险控制决策。
 */
export const userSignupLogs = pgTable('user_signup_logs', {
  /** 最终注册结果原因，例如 user_created, llm_block 或 guard_error */
  finalReason: text('final_reason'),

  /** 从阶段决策派生的聚合风险级别，例如 block -> high */
  riskLevel: varchar('risk_level', { length: 16 }).$type<UserSignupLogRiskLevel>(),

  /** 按注册审查阶段分组的有序阶段决策和元数据 */
  stageResults: jsonb('stage_results').$type<UserSignupLogStageResults>(),
});

// ❌ 不良：注释重述明显的列名，未添加领域含义。
/** 用户邮箱 */
email: text('email'),
```

### JSONB 类型

避免使用 `Record<string, unknown>` 或类似的松散 JSONB 类型作为模式列。定义一个描述预期 JSON 形状的具象接口，即使大多数属性是可选的。这使调用者、迁移和审查查询对齐相同的数据合同。

```typescript
interface UserSignupLogMetadata {
  payloadPath?: string;
  requestPath?: string;
}

metadata: jsonb('metadata').$type<UserSignupLogMetadata>(),
```

```typescript
// ❌ 不良：隐藏了合同，使下游访问无类型。
metadata: jsonb('metadata').$type<Record<string, unknown>>(),
```

松散类型的 JSONB 列通常是更深层次问题的症状：该列是推测性保留的（“用于未来扩展”），但实际上没有写入它。不要添加 `metadata` / `extra` JSONB 列用于假设的未来需求——只有当具体写入与它一起发布时，列才配得上其位置。当审查发现此类列时，修复方法是**删除列**，而不是为不存在的数据发明接口；当实际需求到来时再添加正确类型的列。

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

上述代理-PK 规则也适用于连接表——配对唯一性放在 `uniqueIndex` 中，而不是复合 PK（许多现有的连接表仍然使用复合 PK；这是遗留的，不是模板）：

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
// ✅ 良好
const [result] = await this.db.select().from(agents).where(eq(agents.id, id)).limit(1);
return result;

// ❌ 不良：关系 API
return this.db.query.agents.findFirst({
  where: eq(agents.id, id),
});
```

### 带连接选择

```typescript
// ✅ 良好：显式选择 + leftJoin
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

// ❌ 不良：关系 API，带 `with:`
return this.db.query.agentEvalRunTopics.findMany({
  where: eq(agentEvalRunTopics.runId, runId),
  with: { testCase: true, topic: true },
});
```

### 带聚合选择

```typescript
// ✅ 良好：select + leftJoin + groupBy
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

优先使用 Drizzle 构建器，只要查询清晰地使用 `select`、`insert().select()`、`update().from()`、连接、CTE 和 `groupBy`——这使表/列引用与模式绑定，因此更改会作为 TypeScript 错误出现。在构建器内，表达式级 `sql<T>` 对于缺少辅助功能的特性（JSON 路径、转换、聚合、`CASE`、`NOW()`）是合适的。行锁是子句，不是表达式——使用 `.for('update')`，永远不要使用原始 `FOR UPDATE`。

仅在 null 处理是必需的数据库语义的一部分时（可空的 JSONB 追加/合并，“保留第一个非 null”）才使用 `COALESCE`。不要在普通的插入标量中散布 `COALESCE(excluded.col, current.col)` 只是为了避免更新对象——仅从定义的值构建 `set`，并将任何剩余的 SQL 隐藏在命名的辅助函数（`appendJsonbArray`、`mergeJsonbObject`、`keepFirstValue`）后面，使方法读起来像业务意图，而不是 SQL 引擎。

```typescript
// ✅ 标量仅当存在时包含；SQL 隐藏在命名的辅助函数后面。
const updateValues = compactUndefined({
  email: record.email ?? undefined,
  ip: record.ip ?? undefined,
});
await db.insert(userSignupLogs).values(values).onConflictDoUpdate({
  set: { ...updateValues, stageResults: appendStageResult(stage, result), updatedAt: now },
  target: userSignupLogs.id,
});

// ❌ 每个标量都变成 SQL 引擎。
set: {
  email: sql`COALESCE(excluded.email, ${userSignupLogs.email})`,
  ip: sql`COALESCE(excluded.ip, ${userSignupLogs.ip})`,
}
```

在重构原生 SQL 时：

- 在延迟敏感路径上保留查询形状。如果原生 SQL 是单往返，不要将其拆分为多个基于深度的查询，只是为了丢弃 `execute`。
- 使用 `$with(...)` + `insert().select()` / `update().from()` 进行多步骤单往返写入，Drizzle 可以表达的。
- 不要依赖 `execute<MyRow>(sql...)` 的安全性——它类型化行，但不会将选定的列与模式更改同步。
- 如果只有 PostgreSQL 功能 Drizzle 无法表达才有效，保留原生 SQL 并收紧它：插值中的模式引用、显式用户范围、窄行接口和回归测试。

递归 CTE 是“保留原生”的典型用例——没有干净的 `WITH RECURSIVE` 构建器，重写会添加基于深度的往返：

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
// ✅ 良好：两个简单查询
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

请参阅 `db-migrations` 技能的详细迁移指南。
