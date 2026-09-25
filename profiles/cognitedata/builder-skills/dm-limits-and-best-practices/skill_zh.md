# CDF 数据建模：限制、并发与最佳实践

这是一个参考技能。在编写或审查调用 CDF 数据建模 API 的代码时，请应用以下模式。

此技能拥有运行时可靠性问题：限制、并发、重试、吞吐量和批处理行为。
有关遍历有效载荷正确性和图特定错误特征的详细信息，请参阅 `dm-graph-traversal`。

---

## DMS 限制参考

有关最新的并发限制、资源限制和属性值限制，请参阅官方文档：
**https://docs.cognite.com/cdf/dm/dm_reference/dm_limits_and_restrictions**

需要注意的关键事项：
- 实例的 **apply**、**delete** 和 **query** 操作每个都有自己的并发请求限制
- 超过这些限制将返回 **429 Too Many Requests**
- 转换消耗大量并发预算，留给其他客户端的预算更少
- `instances.list` 有最大页大小（使用分页获取完整结果）
- `instances.query` 表达式每个都有自己的项目限制
- `instances.upsert` 每次调用最多接受 1000 个项目
- `in` 过滤器每个表达式最多接受 1000 个值；更大的集合必须拆分成批次

---

## 搜索与过滤：何时使用哪个

### `instances.search` — 文本属性的模糊/文本匹配

当你需要在字符串字段（名称、描述等）上进行模糊/文本匹配时，使用 `instances.search`。它支持 `operator` 参数：

- **`AND`**（默认）— 精确搜索。所有术语必须匹配。当用户提供特定查询时使用。
- **`OR`** — 广泛的“霰弹”搜索。任何术语都可以匹配。用于探索/自动完成搜索，其中你想获得最大的召回率。

```typescript
// 精确搜索：通过名称查找特定单元格（AND — 所有术语必须匹配）
const exactResults = await client.instances.search({
  view: { type: 'view', ...PROCESS_CELL_VIEW },
  query: 'reactor tank A',
  properties: ['name'],
  operator: 'AND',
  limit: 10,
});

// 广泛搜索：自动完成（OR — 任何术语都可以匹配）
const broadResults = await client.instances.search({
  view: { type: 'view', ...BATCH_VIEW },
  query: 'BUDE completed',
  properties: ['name', 'description', 'batchStatus'],
  operator: 'OR',
  limit: 10,
});
```

你可以将 `search` 与 `filter` 结合使用，以使用精确匹配条件进一步约束结果：

```typescript
// 文本搜索 + 精确过滤：搜索“pump”，但仅在活动节点中
const filtered = await client.instances.search({
  view: { type: 'view', ...PROCESS_CELL_VIEW },
  query: 'pump',
  properties: ['name', 'description'],
  filter: {
    equals: {
      property: getContainerProperty(MY_CONTAINER, 'status'),
      value: 'active',
    },
  },
  limit: 20,
});
```

### `instances.list` / `instances.query` 与 `filter` — 精确匹配过滤

当你需要精确、确定性匹配（equals、range、in、hasData 等）时，使用 `filter`。没有模糊匹配——值必须完全匹配。

```typescript
// 精确匹配：获取所有已完成的批次
const completedBatches = await client.instances.list({
  instanceType: 'node',
  sources: [{ source: { type: 'view', ...BATCH_VIEW } }],
  filter: {
    equals: {
      property: getContainerProperty(BATCH_CONTAINER, 'batchStatus'),
      value: 'completed',
    },
  },
  limit: 1000,
});
```

### 决策指南

| 需求                          | 使用                                     |
| ----------------------------- | ---------------------------------------- |
| 用户在搜索框中输入             | `instances.search` with `OR`             |
| 通过名称查找特定项目           | `instances.search` with `AND`             |
| 按状态、日期范围、枚举过滤     | `filter` on list/query                   |
| 文本搜索 + 精确约束           | `instances.search` + `filter`            |

### `in` 过滤器值限制（1000）和分批

CDF `in` 过滤器在单个过滤表达式中支持最多 1000 个值。如果你需要过滤超过 1000 个 ID，请将值拆分成块并发出多个请求，然后合并结果。

```typescript
const IN_FILTER_BATCH_SIZE = 1000;
// 重用分批写入操作部分定义的块处理工具。

async function listByExternalIds(
  client: CogniteClient,
  externalIds: string[]
): Promise<NodeOrEdge[]> {
  const idBatches = chunk(externalIds, IN_FILTER_BATCH_SIZE);
  const responses = await Promise.all(
    idBatches.map((batch) =>
      cdfTaskRunner.schedule(() =>
        client.instances.list({
          instanceType: 'node',
          sources: [{ source: { type: 'view', ...MY_VIEW } }],
          filter: {
            in: {
              property: ['node', 'externalId'],
              values: batch,
            },
          },
          limit: 1000,
        })
      )
    )
  );

  return responses.flatMap((r) => r.items);
}
```

---

## 队列任务运行器（信号量）

**始终使用全局 `cdfTaskRunner`** 来包装 CDF API 调用。它限制并发请求并防止 429 错误和死锁。

### 源代码

如果项目还没有信号量工具，请创建 `src/shared/utils/semaphore.ts` 并包含此实现：

```typescript
/**
 * 当队列任务被取消时抛出AbortError
 */
export class AbortError extends Error {
  public constructor(message: string = 'Aborted') {
    super(message);
    this.name = 'AbortError';
  }
}

type PendingTask<AsyncFn, AsyncFnResult> = {
  resolve: (result: AsyncFnResult) => void;
  reject: (error: unknown) => void;
  fn: AsyncFn;
  key?: string;
};

const DEFAULT_MAX_CONCURRENT_TASKS = 15;

/**
 * 队列任务运行器用于控制并发操作
 * 用于限制并发 CDF API 请求以避免速率限制和死锁
 * 本质上是一个允许一次运行有限数量的任务的信号量。
 */
export default class QueuedTaskRunner<
  AsyncFn extends () => Promise<AsyncFnResult>,
  AsyncFnResult = Awaited<ReturnType<AsyncFn>>
> {
  private pendingTasks: PendingTask<AsyncFn, AsyncFnResult>[] = [];
  private currentPendingTasks: number = 0;
  private readonly maxConcurrentTasks: number = 1;

  public constructor(
    maxConcurrentTasks: number = DEFAULT_MAX_CONCURRENT_TASKS
  ) {
    this.maxConcurrentTasks = maxConcurrentTasks;
  }

  public schedule(
    fn: AsyncFn,
    options: { key?: string } = {}
  ): Promise<AsyncFnResult> {
    this.startTrackingTime();

    return new Promise((resolve, reject) => {
      if (options.key !== undefined) {
        // 取消具有相同 key 的现有任务（去重）
        this.pendingTasks
          .filter((task) => task.key === options.key)
          .forEach((task) => task.reject(new AbortError()));

        this.pendingTasks = this.pendingTasks.filter(
          (task) => task.key !== options.key
        );
      }

      this.pendingTasks.push({
        resolve,
        reject,
        fn,
        key: options.key,
      });

      this.attemptConsumingNextTask();
    });
  }

  public async attemptConsumingNextTask(): Promise<void> {
    if (this.pendingTasks.length === 0) return;
    if (this.currentPendingTasks >= this.maxConcurrentTasks) return;

    const pendingTask = this.pendingTasks.shift();
    if (pendingTask === undefined) {
      throw new Error('pendingTask is undefined, this should never happen');
    }

    this.currentPendingTasks++;
    const { fn, resolve, reject } = pendingTask;

    try {
      const result = await fn();
      resolve(result);
    } catch (e) {
      reject(e);
    } finally {
      this.currentPendingTasks--;
      this.tick();
      this.attemptConsumingNextTask();
    }
  }

  public clearQueue = (): void => {
    this.pendingTasks = [];
  };

  private startTime: number | null = null;

  private startTrackingTime = (): void => {
    if (this.startTime === null) {
      this.startTime = performance.now();
    }
  };

  private tick = (): void => {
    if (this.pendingTasks.length === 0) {
      this.startTime = null;
    }
  };
}

/**
 * 用于 CDF API 请求的全局任务运行器
 * 限制并发请求以避免 429 速率限制和死锁
 */
export const cdfTaskRunner = new QueuedTaskRunner(DEFAULT_MAX_CONCURRENT_TASKS);
```

### 使用模式

始终使用 `cdfTaskRunner.schedule()` 包装 CDF 调用：

```typescript
import { cdfTaskRunner } from '../../../../shared/utils/semaphore';

// 单个查询
export async function fetchBatches(client: CogniteClient): Promise<CDFBatch[]> {
  return cdfTaskRunner.schedule(async () => {
    const response = await client.instances.query({
      with: { /* ... */ },
      select: { /* ... */ },
    });
    return response.items?.nodes || [];
  });
}

// 多个并行查询（安全——信号量限制并发）
export async function enrichBatch(
  client: CogniteClient,
  batch: CDFBatch
): Promise<BatchEnrichment> {
  const [currentOp, lastOp, cells, material] = await Promise.all([
    fetchCurrentOperation(client, batch.space, batch.externalId),
    fetchLastCompletedOperation(client, batch.space, batch.externalId),
    fetchProcessCells(client, batch.space, batch.externalId),
    fetchMaterial(client, batch.space, batch.externalId),
  ]);
  return { currentOp, lastOp, cells, material };
}

// 以上每个函数内部都使用 cdfTaskRunner.schedule()，
// 因此 Promise.all 是安全的——信号量防止超过并发限制
```

### 使用 Key 进行去重

使用 `key` 选项在再次触发相同查询时取消过时的请求（例如，用户快速更改过滤器）：

```typescript
const result = await cdfTaskRunner.schedule(
  async () => client.instances.query({ /* ... */ }),
  { key: `batch-flow-${batchId}` }
);
// 如果在完成之前到达具有相同 key 的另一个调用，
// 之前的挂起调用将被 AbortError 拒绝
```

---

## 分页

DMS `instances.list` 最多返回 `limit` 个项目，并提供 `nextCursor` 用于下一页。
DMS `instances.query` 使用按表表达式名称键化的 `cursors` 对象。

### instances.list 分页

```typescript
async function fetchAllNodes(client: CogniteClient): Promise<CDFNodeResponse[]> {
  const allItems: CDFNodeResponse[] = [];
  let cursor: string | undefined = undefined;

  do {
    const response = await client.instances.list({
      instanceType: 'node',
      sources: [{ source: { type: 'view', ...MY_VIEW } }],
      filter: {
        equals: {
          property: getContainerProperty(MY_CONTAINER, 'status'),
          value: 'active',
        },
      },
      limit: 1000,
      cursor,
    });

    allItems.push(...response.items);
    cursor = response.nextCursor;

  } while (cursor);

  return allItems;
}
```

### instances.query 分页

`query` 端点将 `nextCursor` 作为 `Record<string, string>` 返回（每个表表达式一个游标）。使用 `cursors` 参数：

```typescript
import { isEmpty } from 'lodash';

async function fetchAllResults(
  client: CogniteClient
): Promise<{ results: CDFResult[]; edges: EdgeDefinition[] }> {
  const QUERY_LIMIT = 10_000;

  const fetchPage = async (
    nextCursors?: Record<string, string>
  ): Promise<{ results: CDFResult[]; edges: EdgeDefinition[] }> => {
    const { items, nextCursor } = await client.instances.query({
      with: {
        results: {
          limit: QUERY_LIMIT,
          nodes: {
            filter: {
              hasData: [{ type: 'view', ...RESULT_VIEW }],
            },
          },
        },
        relatedEdges: {
          limit: QUERY_LIMIT,
          edges: {
            from: 'results' as const,
            maxDistance: 1,
            direction: 'outwards' as const,
            filter: {
              equals: {
                property: ['edge', 'type'],
                value: MY_EDGE_TYPE,
              },
            },
          },
        },
      },
      cursors: nextCursors, // 传递前一页的游标
      select: {
        results: {
          sources: [
            { source: { type: 'view', ...RESULT_VIEW }, properties: ['*'] },
          ],
        },
        relatedEdges: {},
      },
    });

    const results = (items?.results || []) as CDFResult[];
    const edges = (items?.relatedEdges || []).filter(
      (e) => e.instanceType === 'edge'
    );

    // 如果存在更多页面，则递归
    if (!isEmpty(nextCursor)) {
      const next = await fetchPage(nextCursor);
      return {
        results: [...results, ...next.results],
        edges: [...edges, ...next.edges],
      };
    }

    return { results, edges };
  };

  return fetchPage();
}
```

### 分页 + 队列任务运行器组合

始终使用信号量包装分页获取以避免耗尽并发预算：

```typescript
export async function fetchAllWithPagination(
  client: CogniteClient
): Promise<CDFNodeResponse[]> {
  return cdfTaskRunner.schedule(async () => {
    const allItems: CDFNodeResponse[] = [];
    let cursor: string | undefined = undefined;

    do {
      const response = await client.instances.list({
        instanceType: 'node',
        sources: [{ source: { type: 'view', ...MY_VIEW } }],
        filter: { /* ... */ },
        limit: 1000,
        cursor,
      });

      allItems.push(...response.items);
      cursor = response.nextCursor;

      // 可选：如果数据足够，则提前退出
      if (allItems.length >= 500) break;
    } while (cursor);

    return allItems;
  });
}
```

---

## 批量写入操作

当执行大量实例 upsert 时，将其分块以保持在 apply 并发限制之下。每个 `instances.upsert` 调用最多接受 1000 个项目。

### 分块工具

```typescript
function chunk<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}
```

### 使用队列任务运行器进行批量 upsert

```typescript
const UPSERT_BATCH_SIZE = 1000;

async function batchUpsertNodes(
  client: CogniteClient,
  nodes: NodeOrEdgeCreate[]
): Promise<void> {
  const chunks = chunk(nodes, UPSERT_BATCH_SIZE);

  // 通过信号量处理块——即使使用 Promise.all 也是安全的
  await Promise.all(
    chunks.map((batch) =>
      cdfTaskRunner.schedule(async () => {
        await client.instances.upsert({
          items: batch,
        });
      })
    )
  );
}
```

### 使用队列任务运行器进行批量删除

实例删除具有更严格的并发限制。使用单独的、更严格的任务运行器：

```typescript
import QueuedTaskRunner from '../../../../shared/utils/semaphore';

// 用于删除的专用运行器（更严格的并发——请查阅文档获取当前限制）
const deleteTaskRunner = new QueuedTaskRunner(2);

async function batchDeleteNodes(
  client: CogniteClient,
  nodeIds: { space: string; externalId: string }[]
): Promise<void> {
  const chunks = chunk(nodeIds, 1000);

  for (const batch of chunks) {
    await deleteTaskRunner.schedule(async () => {
      await client.instances.delete(
        batch.map((id) => ({
          instanceType: 'node' as const,
          ...id,
        }))
      );
    });
  }
}
```

---

## 硬性限制——查询结果上的 LLM 调用

不要在 `instances.list` / `query` / `search` 命中映射聊天完成。优先使用一个 Atlas / EOS 侧边栏轮次（`integrate-fusion-agent`）。如果需要每个项目的完成：**每个用户操作最多 5 个**，上限 **50 个**，按 `space:externalId:lastUpdatedTime` 缓存，仅用户发起。

---

## 常见陷阱

### 1. 嵌套信号量导致的死锁

如果函数 A 持有信号量槽并调用需要槽的函数 B，如果所有槽都占用，则可能死锁。**将信号量保持在最外层调用级别**，或确保内部调用不通过相同的信号量。

```typescript
// 错误：嵌套信号量——可能导致死锁
async function fetchAndEnrich(client: CogniteClient) {
  return cdfTaskRunner.schedule(async () => {
    const batches = await fetchBatches(client); // 这也会调用 cdfTaskRunner.schedule()！
    // 如果所有槽都被 fetchAndEnrich 调用占用，fetchBatches 将永远不会运行
  });
}

// 正确：让内部函数拥有信号量
async function fetchAndEnrich(client: CogniteClient) {
  const batches = await fetchBatches(client); // 有自己的信号量调用
  const enriched = await Promise.all(
    batches.map((b) => enrichBatch(client, b)) // 每个都有自己的信号量调用
  );
  return enriched;
}
```

### 2. 忘记分页

DMS 最多返回 `limit` 个项目。如果你不分页，会无声地丢失数据。始终检查 `nextCursor`：

```typescript
// 错误：可能丢失数据
const response = await client.instances.list({ limit: 1000, /* ... */ });
const items = response.items; // 可能不完整！

// 正确：分页
const allItems = [];
let cursor;
do {
  const response = await client.instances.list({ limit: 1000, cursor, /* ... */ });
  allItems.push(...response.items);
  cursor = response.nextCursor;
} while (cursor);
```

### 3. 无信号量的无限制 Promise.all

发起许多并行 API 调用会立即触发 429 限制：

```typescript
// 错误：同时请求过多
await Promise.all(batchIds.map((id) => client.instances.query({ /* ... */ })));

// 正确：每个调用都通过信号量
await Promise.all(
  batchIds.map((id) =>
    cdfTaskRunner.schedule(() => client.instances.query({ /* ... */ }))
  )
);
```

### 4. 每个表表达式查询的限制

`instances.query` 中的每个表表达式都有自己的 `limit`。如果你的遍历可能在单个表达式中返回比限制更多的项目，你必须使用 `cursors` 参数分页。

### 5. 过大的 `in` 过滤器

`in` 过滤器每个表达式最多接受 1000 个值。传递超过 1000 个值在单个 `in` 过滤器中可能会失败或根据端点/版本产生不完整行为。始终将值分块并运行批量请求。

---

## 总结检查清单

- [ ] 将所有 CDF API 调用包装在 `cdfTaskRunner.schedule()`
- [ ] 使用 `cursor` / `nextCursor` 分页 `instances.list` 调用
- [ ] 使用 `cursors` / `nextCursor` 分页 `instances.query` 调用，当数据可能超过限制时
- [ ] 将写入操作分块，每个 `instances.upsert` 调用最多 1000 个项目
- [ ] 使用单独的、更严格的任务运行器进行删除
- [ ] 避免嵌套 `cdfTaskRunner.schedule()` 调用以防止死锁
- [ ] 使用 `Promise.all` 与信号量包装的函数，而不是原始 API 调用
- [ ] 使用 `instances.search` 进行文本匹配，`filter` 进行精确匹配查询
- [ ] 将 `in` 过滤器值分块，最多 1000 个，并合并响应
- [ ] 查询结果上的 LLM 调用限制（每个用户操作最多 5 个，最多 50 个）并缓存，或不存在
- [ ] 参考 https://docs.cognite.com/cdf/dm/dm_reference/dm_limits_and_restrictions 获取当前限制
