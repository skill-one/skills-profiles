# 持久化对象

使用持久化对象在 Cloudflare 边缘构建具有状态协调的应用。

## 获取资源

您对持久化对象 API 和配置的了解可能已经过时。对于任何持久化对象任务，**优先考虑获取（retrieval）而非预训练（pre-training）**。

| 资源 | URL |
|------|-----|
| 文档 | https://developers.cloudflare.com/durable-objects/ |
| API 参考 | https://developers.cloudflare.com/durable-objects/api/ |
| 最佳实践 | https://developers.cloudflare.com/durable-objects/best-practices/ |
| 示例 | https://developers.cloudflare.com/durable-objects/examples/ |

实现功能时，请获取相关的文档页面。

## 使用场景

- 创建新的持久化对象类用于状态协调
- 实现RPC方法、闹钟或WebSocket处理器
- 审查现有DO代码以遵循最佳实践
- 配置wrangler.jsonc/toml用于DO绑定和迁移
- 使用Cloudflare的Vitest集成编写测试
- 设计分片策略和父子关系

## 参考文档

- `./references/rules.md` - 核心规则、存储、并发、RPC、闹钟
- [测试参考](./references/testing.md) - 当前Vitest文档、迁移选择和测试选择
- `./references/workers.md` - Workers处理器、类型、wrangler配置、可观察性

搜索：`blockConcurrencyWhile`，`idFromName`，`getByName`，`setAlarm`，`sql.exec`

## 核心原则

### 持久化对象用于

| 需求 | 示例 |
|------|-----|
| 协调 | 聊天室、多人游戏、协作文档 |
| 强一致性 | 库存、预订系统、回合制游戏 |
| 按实体存储 | 多租户SaaS、按用户数据 |
| 持久连接 | WebSockets、实时通知 |
| 按实体计划工作 | 订阅续订、游戏超时 |

### 不要使用

- 无状态请求处理（使用普通Workers）
- 最大全局分布需求
- 高扇出独立请求

## 快速参考

### Wrangler配置

```jsonc
// wrangler.jsonc
{
  "durable_objects": {
    "bindings": [{ "name": "MY_DO", "class_name": "MyDurableObject" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyDurableObject"] }]
}
```

### 基本持久化对象模式

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

1. **围绕协调原子建模** - 每个聊天室/游戏/用户一个DO，而不是一个全局DO
2. **使用`getByName()`进行确定性路由** - 相同输入=相同DO实例
3. **使用SQLite存储** - 在迁移中配置`new_sqlite_classes`
4. **在构造函数中初始化** - 仅用于模式设置使用`blockConcurrencyWhile()`
5. **使用RPC方法** - 不是fetch()处理器（兼容性日期 >= 2024-04-03）
6. **先持久化，后缓存** - 始终在更新内存状态前写入存储
7. **每个DO一个闹钟** - `setAlarm()`替换任何现有闹钟

## 反模式（绝对不要）

- 单个全局DO处理所有请求（瓶颈）
- 在每个请求上使用`blockConcurrencyWhile()`（降低吞吐量）
- 仅在内存中存储关键状态（在驱逐/崩溃时丢失）
- 在相关的存储写入之间使用`await`（破坏原子性）
- 跨`fetch()`或外部I/O保持`blockConcurrencyWhile()`

## 实例创建

```typescript
// 确定性 - 大多数情况下首选
const stub = env.MY_DO.getByName("room-123");

// 从现有ID字符串
const id = env.MY_DO.idFromString(storedIdString);
const stub = env.MY_DO.get(id);

// 新唯一ID - 外部存储映射
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

## 闹钟

```typescript
// 安排（替换现有）
await this.ctx.storage.setAlarm(Date.now() + 60_000);

// 处理器
async alarm(): Promise<void> {
  // 处理计划工作
  // 可选地重新安排：await this.ctx.storage.setAlarm(...)
}

// 取消
await this.ctx.storage.deleteAlarm();
```

## 测试

在配置套件或编写持久化对象测试前，请阅读[测试参考](./references/testing.md)。它路由到当前设置、API和示例，并确定要覆盖的行为。
