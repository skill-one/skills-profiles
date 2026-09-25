# Prisma SQL 驱动适配器实现

使用本指南时，请确保已安装目标 Prisma 版本所指定的确切 `@prisma/driver-adapter-utils` 版本。驱动适配器是一个协议边界：类型兼容的代码仍然可能损坏值、泄露连接或破坏事务。

## 应用场景

- 实现 `SqlDriverAdapterFactory`、`SqlMigrationAwareDriverAdapterFactory`、`SqlDriverAdapter` 或 `Transaction`
- 添加嵌套事务/保存点支持
- 映射驱动值、列元数据、绑定参数或数据库错误
- 调试 `P2039`、事务泄漏、影子数据库失败或适配器特定查询行为

## 合约快照

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

`IsolationLevel` 目前包括 `READ UNCOMMITTED`、`READ COMMITTED`、`REPEATABLE READ`、`SNAPSHOT` 和 `SERIALIZABLE`；验证具体数据库支持的情况。

## 优先级规则

| 优先级 | 规则 | 影响 |
|--------|------|------|
| 关键 | 每个事务一个专用连接 | 防止交错和泄漏 |
| 关键 | `commit`/`rollback` 是生命周期清理钩子 | 防止重复 COMMIT/ROLLBACK |
| 关键 | 保存点存在于 `Transaction` 中，而非适配器全局深度 | 使嵌套作用域连接局部化 |
| 关键 | 保留原始数据库错误代码/消息 | 使 `P2039` 回退有用 |
| 高 | 精确映射参数和结果元数据 | 防止静默值损坏 |
| 高 | 影子数据库是隔离的，并且始终被清理 | 使 Migrate 安全 |
| 高 | 仅释放适配器拥有的资源 | 防止关闭调用者拥有的连接池 |

## 查询实现

`SqlQuery` 包含 `sql`、`args` 和并行的 `argTypes`。使用值和 `ArgType` 都映射每个参数；不要丢弃类型/参数数量信息。在驱动器的数组/元组行模式下执行，以使列顺序稳定。

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

返回 `columnNames`、`columnTypes` 和 `rows` 具有相同的长度/顺序。故意将驱动器元数据映射到 `ColumnTypeEnum`：

- 有符号整数宽度映射到 `Int32`/`Int64`；保留 64 位值而不进行 JS 数字截断
- 十进制/数值映射到 `Numeric`，使用 Prisma 期望的表示
- 二进制映射到 `Uint8Array`/`Bytes`
- 日期、时间、时间戳映射到 `Date`、`Time` 和 `DateTime`
- UUID、JSON、枚举、数组和提供程序特定未知值映射到它们的显式类型
- 不支持的本地类型映射到 `DriverAdapterError({ kind: 'UnsupportedNativeDataType', type })`

测试 `null`、空数组、数组元素类型、大整数、十进制、字节数组、JSON、日期和用户定义/未知本地类型。

### 脚本执行

`executeScript` 必须像提供程序期望的那样执行迁移脚本。优先使用驱动器的原生多语句/脚本功能或真实的 SQL 解析器。简单地按 `;` 分割会破坏函数、触发器、引号字符串和方言特定块。

## 事务协议

`startTransaction` 必须获取一个专用连接，启动数据库事务，应用请求的隔离级别，并返回一个绑定到该相同连接的 `Transaction`。如果设置失败，请立即释放它。

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

### 提交和回滚

Prisma 通过 `executeRaw` 协调 SQL `COMMIT`/`ROLLBACK`。事务对象的 `commit()` 和 `rollback()` 方法是生命周期钩子：断开监听器并精确一次释放专用连接。它们不得发出第二个 SQL 提交/回滚。

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

仅在提供程序支持保存点时实现可选的保存点方法。验证/引用保存点标识符。对于保存点有意为空操作的提供程序，请记录并测试该限制。

永远不要在共享适配器上保持事务深度。并行事务使适配器全局深度不正确；嵌套状态属于返回的事务连接和 Prisma 的保存点调用。

## 错误映射

将已识别的驱动器失败包装在 `DriverAdapterError` 中。将已知条件映射到 `MappedError` 类似于约束违反、身份验证/可达性、缺少表/列/数据库、超时、关闭的事务、无效输入、值范围和写入冲突。

对于数据库错误，即使回退到提供程序特定的原始变体，也要保留 `originalCode` 和 `originalMessage`：

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

Prisma 在未映射的驱动器错误成为 `P2039` 时使用保留的原始详细信息。不要用虚构的 `GenericJs` ID 替换每个未知异常；重新抛出真正意外的非驱动器错误，以便编程错误仍然可见。

## 工厂、所有权和影子数据库

- `connect()` 返回一个新鲜可用的适配器连接/池包装器。
- 跟踪工厂是否创建了池。`dispose()` 关闭拥有的池，并且除非显式选项转移所有权，否则仅从调用者拥有的池中断开监听器。
- 仅在 `connectToShadowDb()` 可以创建隔离的影子数据库、连接到它并在清理/失败时删除它时实现 `SqlMigrationAwareDriverAdapterFactory`。
- 永远不要将影子适配器指向主数据库。引用生成的标识符并使用加密唯一名称。
- `getConnectionInfo()` 应准确报告 `schemaName`、`maxBindValues`（适用时）和 `supportsRelationJoins`。

## 验证检查清单

- [ ] 与目标 `@prisma/driver-adapter-utils` 版本进行类型检查
- [ ] `queryRaw` 保留列顺序、类型、null 和精度
- [ ] `executeRaw` 正确报告受影响的行
- [ ] `executeScript` 处理提供程序特定的多语句语法
- [ ] 并行交互式事务使用不同的专用连接
- [ ] 成功提交和释放一次；失败回滚和释放一次
- [ ] 嵌套事务测试执行创建/回滚/释放保存点钩子
- [ ] 不支持的隔离级别失败为 `InvalidIsolationLevel`
- [ ] 已知约束映射到结构化错误
- [ ] 未映射的数据库错误保留原始代码/消息并显示有用的 `P2039`
- [ ] 测试内部和外部池的所有权
- [ ] 影子数据库的创建、使用、失败清理和释放是隔离的
- [ ] 运行 Prisma Client 集成/E2E 测试，而不仅仅是适配器单元测试

## 源引用

- [驱动器适配器接口](https://github.com/prisma/prisma/blob/v7/packages/driver-adapter-utils/src/types.ts)
- [PostgreSQL 适配器事务实现](https://github.com/prisma/prisma/blob/v7/packages/adapter-pg/src/pg.ts)
- [PostgreSQL 适配器错误映射](https://github.com/prisma/prisma/blob/v7/packages/adapter-pg/src/errors.ts)
