# 持久化对象

使用 Durable Objects 构建基于 Cloudflare 边缘的具有状态和协调能力的应用程序。

## 检索来源

您对 Durable Objects API 和配置的认知可能已过时。**对于任何 Durable Objects 任务，优先使用检索而非预训练。**

| 资源 | URL |
|----------|-----|
| 文档 | https://developers.cloudflare.com/durable-objects/ |
| API 参考 | https://developers.cloudflare.com/durable-objects/api/ |
| 最佳实践 | https://developers.cloudflare.com/durable-objects/best-practices/ |
| 示例 | https://developers.cloudflare.com/durable-objects/examples/ |

实现功能时，获取相关文档页面。

## 何时使用

- 为有状态协调创建新的 Durable Object 类
- 实现 RPC 方法、报警或 WebSocket 处理器
- 审查现有 DO 代码的最佳实践
- 为 DO 绑定和迁移配置 wrangler.jsonc/toml
- 使用 Cloudflare 的 Vitest 集成编写测试
- 设计分片策略及父子关系

## 参考文档

- `./references/rules.md` - 核心规则、存储、并发、RPC、报警
- [测试参考](./references/testing.md) - 当前 Vitest 文档、迁移选项及测试选择
- `./references/workers.md` - Workers 处理器、类型、wrangler 配置、可观测性

搜索：`blockConcurrencyWhile`、`idFromName`、`getByName`、`setAlarm`、`sql.exec`

## 核心原则

### 使用 Durable Objects

| 需求 | 示例 |
|------|---------|
| 协调 | 聊天室、多人游戏、协作文档 |
| 强一致性 | 库存、预订系统、回合制游戏 |
| 按实体存储 | 多租户 SaaS、按用户数据 |
| 持久连接 | WebSocket、实时通知 |
| 每个实体的定时工作 | 订阅续期、游戏超时 |

### 禁止使用

- 无状态请求处理（使用普通 Workers）
- 全局最大分发需求
- 大规模扇出独立请求

## 快速参考

### Wrangler 配置

```jsonc
// wrangler.jsonc
{
  "durable_objects": {
    "bindings": [{ "name": "MY_DO", "class_name": "MyDurableObject" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyDurableObject"] }]
}
```

### 基础 Durable Object 模式

```typescript
import { DurableObject } from "cloudflare:workers";

export interface Env {
  MY_DO: DurableObjectNamespace<MyDurableObject>;
}

export class MyDurableObject extends DurableObject<Env> {
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      this.ctx.storage.sql.exec(`
        CREATE TABLE IF NOT EXISTS items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          data TEXT NOT NULL
        )
      `);
    });
  }

  async addItem(data: string): Promise<number> {
    const result = this.ctx.storage.sql.exec<{ id: number }>(
      "INSERT INTO items (data) VALUES (?) RETURNING id",
      data
    );
    return result.one().id;
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const stub = env.MY_DO.getByName("my-instance");
    const id = await stub.addItem("hello");
    return Response.json({ id });
  },
};
```

## 关键规则

1. **围绕协调原子建模** - 每个聊天室/游戏/用户一个 DO，而非一个全局 DO
2. **使用 `getByName()` 进行确定性路由** - 相同输入 = 相同的 DO 实例
3. **使用 SQLite 存储** - 在迁移中配置 `new_sqlite_classes`
4. **在构造函数中初始化** - 仅使用 `blockConcurrencyWhile()` 进行模式设置
5. **使用 RPC 方法** - 而非 fetch() 处理器（兼容性日期 >= 2024-04-03）
6. **先持久化，后缓存** - 在更新内存状态之前，始终写入存储
7. **每个 DO 一个报警** - `setAlarm()` 会替换已有的任何报警

## 反模式（禁止使用）

- 单个全局 DO 处理所有请求（存在瓶颈）
- 在每个请求上使用 `blockConcurrencyWhile()`（会破坏吞吐量）
- 仅将关键状态存储在内存中（在驱逐或崩溃时丢失）
- 在相关存储写入之间使用 `await`（破坏原子性）
- 在 `fetch()` 或外部 I/O 中跨过 `blockConcurrencyWhile()`

## 桩创建

```typescript
// 确定性的 - 适用于大多数情况
const stub = env.MY_DO.getByName("room-123");

// 来自现有 ID 字符串
const id = env.MY_DO.idFromString(storedIdString);
const stub = env.MY_DO.get(id);

// 新的唯一 ID - 在外部存储映射
const id = env.MY_DO.newUniqueId();
const stub = env.MY_DO.get(id);
```

## 存储操作

```typescript
// SQL（同步，推荐）
this.ctx.storage.sql.exec("INSERT INTO t (c) VALUES (?)", value);
const rows = this.ctx.storage.sql.exec<Row>("SELECT * FROM t").toArray();

// KV（异步）
await this.ctx.storage.put("key", value);
const val = await this.ctx.storage.get<Type>("key");
```

## 报警

```typescript
// 调度（替换已有）
await this.ctx.storage.setAlarm(Date.now() + 60_000);

// 处理器
async alarm(): Promise<void> {
  // 处理定时工作
  // 可选重新调度：await this.ctx.storage.setAlarm(...)
}

// 取消
await this.ctx.storage.deleteAlarm();
```

## 测试

在配置测试套件或编写 Durable Object 测试之前，请阅读测试参考文档[./references/testing.md]。该文档将路由至当前设置、API 及示例，并明确需要覆盖的行为。
