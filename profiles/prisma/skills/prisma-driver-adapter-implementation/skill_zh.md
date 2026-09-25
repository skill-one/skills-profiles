# Prisma SQL 驱动适配器实现

请使用目标 Prisma 版本安装的确切 `@prisma/driver-adapter-utils` 版本配合本指南使用。驱动适配器是协议边界：类型兼容的代码仍可能损坏值、泄露连接或破坏事务。

## 适用场景

- 实现 `SqlDriverAdapterFactory`、`SqlMigrationAwareDriverAdapterFactory`、`SqlDriverAdapter` 或 `Transaction`
- 添加嵌套事务/保存点支持
- 映射驱动器值、列元数据、绑定参数或数据库错误
- 调试 `P2039`、事务泄露、影子数据库故障或适配器特定的查询行为

## 契约快照

```typescript
interface SqlDriverAdapterFactory extends AdapterInfo {
  connect(): Promise<SqlDriverAdapter>
}

interface SqlMigrationAwareDriverAdapterFactory extends SqlDriverAdapterFactory {
  connectToShadowDb(): Promise<SqlDriverAdapter>
}

interface SqlDriverAdapter extends AdapterInfo {
  queryRaw(query: SqlQuery): Promise<SqlResultSet>
  executeRaw(query: SqlQuery): Promise<number>
  executeScript(script: string): Promise<void>
  startTransaction(isolationLevel?: IsolationLevel): Promise<Transaction>
  getConnectionInfo?(): ConnectionInfo
  dispose(): Promise<void>
}

interface Transaction extends AdapterInfo {
  readonly options: { usePhantomQuery: boolean }
  queryRaw(query: SqlQuery): Promise<SqlResultSet>
  executeRaw(query: SqlQuery): Promise<number>
  commit(): Promise<void>
  rollback(): Promise<void>
  createSavepoint?(name: string): Promise<void>
  rollbackToSavepoint?(name: string): Promise<void>
  releaseSavepoint?(name: string): Promise<void>
}
```

`IsolationLevel` 目前包含 `READ UNCOMMITTED`、`READ COMMITTED`、`REPEATABLE READ`、`SNAPSHOT` 和 `SERIALIZABLE`；请验证具体数据库支持哪些级别。

## 优先级规则

### 优先级与规则

| 优先级 | 规则 | 影响 |
|--------|------|------|
| CRITICAL | 每个事务使用专用连接 | 防止交错和泄露 |
| CRITICAL | `commit`/`rollback` 是生命周期清理钩子 | 防止重复的 COMMIT/ROLLBACK |
| CRITICAL | 保存点位于 `Transaction` 上，而非适配器全局深度 | 使嵌套作用域与连接本地化 |
| CRITICAL | 保留原始数据库错误代码/消息 | 启用有用的 `P2039` 回退 |
| HIGH | 精确映射参数和结果元数据 | 防止静默值损坏 |
| HIGH | 影子数据库相互隔离且始终被清理 | 使 Migrate 安全 |
| HIGH | 仅销毁适配器拥有的资源 | 防止关闭调用方拥有的连接池 |

## 查询实现

`SqlQuery` 包含 `sql`、`args` 和并行的 `argTypes`。使用值和 `ArgType` 映射每个参数；不要丢弃类型/个数信息。以驱动程序的数组/元组行模式执行，确保列顺序稳定。

```typescript
class ExampleQueryable {
  readonly provider = 'postgres' as const
  readonly adapterName = '@acme/adapter-example'

  constructor(protected readonly connection: DriverConnection) {}

  async queryRaw(query: SqlQuery): Promise<SqlResultSet> {
    try {
      const result = await this.connection.query({
        text: query.sql,
        values: query.args.map((value, index) =>
          mapArg(value, query.argTypes[index]),
        ),
        rowMode: 'array',
      })

      return {
        columnNames: result.fields.map((field) => field.name),
        columnTypes: result.fields.map(mapColumnType),
        rows: result.rows,
      }
    } catch (error) {
      throwAdapterError(error)
    }
  }

  async executeRaw(query: SqlQuery): Promise<number> {
    try {
      const result = await this.connection.execute(
        query.sql,
        query.args.map((value, index) => mapArg(value, query.argTypes[index])),
      )
      return result.rowsAffected ?? 0
    } catch (error) {
      throwAdapterError(error)
    }
  }
}
```

### 结果映射

以相同的长度和顺序返回 `columnNames`、`columnTypes` 和 `rows`。刻意地将驱动器元数据映射到 `ColumnTypeEnum`：

- 有符号整数宽度映射为 `Int32`/`Int64`；在不使用 JS 数字截断的情况下保留 64 位值
- 将小数/数值映射为 `Numeric`，使用 Prisma 期望的表示方式
- 二进制映射为 `Uint8Array`/`Bytes`
- 仅日期、仅时间和时间戳映射为 `Date`、`Time` 和 `DateTime`
- UUID、JSON、枚举、数组和提供程序特定的未知值映射到其显式类型
- 不支持的原始类型映射为 `DriverAdapterError({ kind: 'UnsupportedNativeDataType', type })`

测试 `null`、空数组、数组元素类型、大整数、小数、字节数组、JSON、日期和用户自定义/未知原始类型。

### 脚本执行

`executeScript` 必须按照提供程序的预期执行迁移脚本。优先使用驱动程序的原生多语句/脚本功能或真实 SQL 解析器。简单按 `;` 分割会破坏函数、触发器、带引号的字符串和特定方言的代码块。

## 事务协议

`startTransaction` 必须获取专用连接，启动数据库事务，应用请求的隔离级别，并返回绑定到该相同连接的 `Transaction`。如果设置失败，立即释放它。

```typescript
async startTransaction(level?: IsolationLevel): Promise<Transaction> {
  const connection = await this.pool.acquire()
  try {
    const tx = new ExampleTransaction(connection, () => connection.release())
    await tx.executeRaw({ sql: 'BEGIN', args: [], argTypes: [] })
    if (level) {
      await tx.executeRaw({
        sql: `SET TRANSACTION ISOLATION LEVEL ${validateLevel(level)}`,
        args: [],
        argTypes: [],
      })
    }
    return tx
  } catch (error) {
    connection.release(error)
    throwAdapterError(error)
  }
}
```

### 提交与回滚

Prisma 通过 `executeRaw` 协调 SQL `COMMIT`/`ROLLBACK`。事务对象的 `commit()` 和 `rollback()` 方法是生命周期钩子：准确断开监听器并恰好释放一次专用连接。它们不能发出第二次 SQL 提交/回滚。

```typescript
class ExampleTransaction extends ExampleQueryable implements Transaction {
  readonly options = { usePhantomQuery: false }
  #closed = false

  constructor(connection: DriverConnection, private readonly release: () => void) {
    super(connection)
  }

  async commit() { this.finish() }
  async rollback() { this.finish() }

  private finish() {
    if (this.#closed) return
    this.#closed = true
    this.release()
  }

  async createSavepoint(name: string) {
    await this.control(`SAVEPOINT ${safeSavepoint(name)}`)
  }

  async rollbackToSavepoint(name: string) {
    await this.control(`ROLLBACK TO SAVEPOINT ${safeSavepoint(name)}`)
  }

  async releaseSavepoint(name: string) {
    await this.control(`RELEASE SAVEPOINT ${safeSavepoint(name)}`)
  }

  private async control(sql: string) {
    await this.executeRaw({ sql, args: [], argTypes: [] })
  }
}
```

仅在提供程序支持时实现可选的保存点方法。验证/引用保存点标识符。对于保存点为故意无操作的提供程序，记录并测试该限制。

切勿在共享适配器上保持事务深度。并行事务会使适配器全局深度不正确；嵌套状态属于返回的事务连接和 Prisma 的保存点调用。

## 错误映射

将识别的驱动器失败封装在 `DriverAdapterError` 中。将已知条件映射为 `MappedError` 类型，如约束违规、认证/可达性、缺少表/列/数据库、超时、已关闭的事务、无效输入、值范围以及写入冲突等。

对于数据库错误，即使在回退到提供程序特定的原始变体时，也需保留 `originalCode` 和 `originalMessage`：

```typescript
import {
  DriverAdapterError,
  type Error as DriverAdapterErrorObject,
  type MappedError,
} from '@prisma/driver-adapter-utils'

function convertDriverError(error: DatabaseError): DriverAdapterErrorObject {
  return {
    originalCode: String(error.code),
    originalMessage: error.message,
    ...mapKnownOrRaw(error),
  }
}

function mapKnownOrRaw(error: DatabaseError): MappedError {
  if (error.code === '23505') {
    return { kind: 'UniqueConstraintViolation', constraint: parsedConstraint(error) }
  }
  return {
    kind: 'postgres',
    code: String(error.code ?? 'N/A'),
    severity: error.severity ?? 'N/A',
    message: error.message,
    detail: error.detail,
    column: error.column,
    hint: error.hint,
  }
}

function throwAdapterError(error: unknown): never {
  if (!isDatabaseError(error)) throw error
  throw new DriverAdapterError(convertDriverError(error))
}
```

Prisma 在将未映射的驱动器错误转换为 `P2039` 时使用保留的原始细节。不要将每个未知异常替换为伪造的 `GenericJs` id；重新抛出真正意外且非驱动器的错误，使编程错误保持可见。

## 工厂、所有权与影子数据库

- `connect()` 返回全新的可用适配器连接/连接池包装器。
- 跟踪工厂是否创建了连接池。`dispose()` 关闭拥有的连接池，仅在明确选项转移所有权时从调用方拥有的连接池中分离监听器。
- 仅在 `connectToShadowDb()` 能够创建独立影子数据库、连接至它，并在销毁/故障清理时删除它的情况下，实现 `SqlMigrationAwareDriverAdapterFactory`。
- 切勿将影子适配器指向主数据库。引用生成的标识符并使用加密唯一名称。
- `getConnectionInfo()` 应准确报告 `schemaName`、`maxBindValues`（适用时）和 `supportsRelationJoins`。

## 验证清单

- [ ] 针对确切的目标 `@prisma/driver-adapter-utils` 版本进行类型检查
- [ ] `queryRaw` 保持列顺序、类型、null 和精度
- [ ] `executeRaw` 正确报告受影响的行数
- [ ] `executeScript` 处理提供程序特定的多语句语法
- [ ] 并发交互式事务使用不同的专用连接
- [ ] 成功的提交和释放仅执行一次；失败回滚和释放仅执行一次
- [ ] 嵌套事务测试涵盖创建/回滚/释放保存点钩子
- [ ] 不支持的隔离级别以 `InvalidIsolationLevel` 失败
- [ ] 已知约束映射为结构化错误
- [ ] 未映射的数据库错误保留原始代码/消息并呈现有用的 `P2039`
- [ ] 测试内部和外部连接池的所有权销毁
- [ ] 影子数据库的创建、使用、故障清理和销毁相互隔离
- [ ] 运行 Prisma Client 集成/E2E 测试，而不仅仅是适配器单元测试

## 来源参考

- [驱动适配器接口](https://github.com/prisma/prisma/blob/v7/packages/driver-adapter-utils/src/types.ts)
- [PostgreSQL 适配器事务实现](https://github.com/prisma/prisma/blob/v7/packages/adapter-pg/src/pg.ts)
- [PostgreSQL 适配器错误映射](https://github.com/prisma/prisma/blob/v7/packages/adapter-pg/src/errors.ts)
