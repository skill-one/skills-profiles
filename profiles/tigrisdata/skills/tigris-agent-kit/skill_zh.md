# Tigris Agent Kit

Tigris 上的 AI 代理高级存储工作流。将 `@tigrisdata/storage` 和 `@tigrisdata/iam` 基础构件组合成四个构建模块：**分支**、**工作区**、**检查点**和**协调**。

## 前置条件

**在其他任何操作之前**，请确保已安装 Tigris CLI：

```bash
tigris help || npm install -g @tigrisdata/cli
```

如果您需要安装它，请告知用户：“我正在安装 Tigris CLI (`@tigrisdata/cli`)，以便我们可以使用 Tigris 对象存储。”

然后安装 agent-kit 包：

```bash
npm install @tigrisdata/agent-kit
```

## 配置

所有函数都接受一个可选的 `config` 参数。如果省略，SDK 将从环境变量中读取：

```bash
TIGRIS_STORAGE_ACCESS_KEY_ID=tid_...
TIGRIS_STORAGE_SECRET_ACCESS_KEY=tsec_...
```

在需要时显式传递配置：

```typescript
const config = {
  accessKeyId: 'tid_...',
  secretAccessKey: 'tsec_...',
};
```

所有函数都返回一个 `TigrisResponse<T>` — 一个 `{ data: T }` 或 `{ error: Error }` 的区分联合类型。始终先检查 `error`。

## 快速参考

| 构建模块 | 目的 | 函数 |
|---|---|---|
| **分支** | N 个共享数据集的独立副本 | `createForks`, `teardownForks` |
| **工作区** | 每个代理的专用桶，具有 TTL | `createWorkspace`, `teardownWorkspace` |
| **检查点** | 快照桶状态，从该快照恢复为分支 | `checkpoint`, `restore`, `listCheckpoints` |
| **协调** | 通过 webhook 触发的事件驱动管道 | `setupCoordination`, `teardownCoordination` |

## 何时使用哪个

| 场景 | 使用 |
|---|---|
| 启动 N 个每个都需要数据集副本的代理 | **分支** |
| 为一个代理提供一个在一天后自动清理的临时桶 | **工作区** |
| 在运行中途保存代理状态，以便稍后从该状态分支 | **检查点** + **恢复** |
| 当上游代理写入结果时触发下游代理 | **协调** |

## 分支 — 并行代理副本

每个分支都是一个具有隔离存储的独立桶。写时复制 — 任何大小下即时完成，零数据重复。基础桶必须启用快照。

```typescript
import { createForks, teardownForks } from '@tigrisdata/agent-kit';

const { data: forkSet, error } = await createForks('my-dataset', 3, {
  prefix: 'experiment-run-42',
  credentials: { role: 'Editor' },
});
if (error) throw error;

for (const fork of forkSet.forks) {
  // fork.bucket — 桶名称
  // fork.credentials?.accessKeyId / secretAccessKey — 每个分支的范围
}

// 撤销凭证并删除所有分支桶
await teardownForks(forkSet);
```

详细选项、生命周期和模式：阅读 `./resources/forks.md`。

## 工作区 — 每个代理的桶

为单个代理预配专用桶。可选的 TTL 自动过期对象；可选的范围凭证强制执行最小权限。

```typescript
import { createWorkspace, teardownWorkspace } from '@tigrisdata/agent-kit';

const { data: workspace } = await createWorkspace('agent-workspace-abc', {
  ttl: { days: 1 },
  enableSnapshots: true,
  credentials: { role: 'Editor' },
});

// 使用 workspace.bucket 和 workspace.credentials 与 @tigrisdata/storage 一起使用

await teardownWorkspace(workspace);
```

详细选项、TTL 行为和模式：阅读 `./resources/workspaces.md`。

## 检查点 — 快照和恢复

在某个时间点捕获桶状态；恢复会从该快照创建一个写时复制分支。原始桶保持不变。

```typescript
import { checkpoint, restore, listCheckpoints } from '@tigrisdata/agent-kit';

const { data: ckpt } = await checkpoint('training-data', { name: 'epoch-50' });

const { data: list } = await listCheckpoints('training-data');

const { data: restored } = await restore(
  'training-data',
  ckpt.snapshotId,
  { forkName: 'training-data-retry' },
);
// restored.bucket — 在该时间点的独立分支
```

详细选项和回滚模式：阅读 `./resources/checkpoints.md`。

## 协调 — 事件驱动管道

将桶通知线路连接起来，以便写入触发 webhook 而不是需要轮询。使用它来串联代理：代理 A 写入结果，Tigris 触发 webhook，代理 B 开始。

```typescript
import { setupCoordination, teardownCoordination } from '@tigrisdata/agent-kit';

await setupCoordination('pipeline-bucket', {
  webhookUrl: 'https://my-service.com/webhook',
  filter: 'WHERE `key` REGEXP "^results/"',
  auth: { token: 'my-webhook-secret' },
});

await teardownCoordination('pipeline-bucket');
```

过滤语法、webhook 认证和管道模式：阅读 `./resources/coordination.md`。

## API 参考

### 分支

| 函数 | 描述 |
|---|---|
| `createForks(baseBucket, count, options?)` | 快照 + N 次分支 + 范围凭证 |
| `teardownForks(forkSet, options?)` | 撤销凭证 + 删除分支 |

### 工作区

| 函数 | 描述 |
|---|---|
| `createWorkspace(name, options?)` | 创建桶 + TTL + 范围凭证 |
| `teardownWorkspace(workspace, options?)` | 撤销凭证 + 删除桶 |

### 检查点

| 函数 | 描述 |
|---|---|
| `checkpoint(bucket, options?)` | 快照一个桶，返回快照 ID |
| `restore(bucket, snapshotId, options?)` | 从快照分支 |
| `listCheckpoints(bucket, options?)` | 列出桶的所有快照 |

### 协调

| 函数 | 描述 |
|---|---|
| `setupCoordination(bucket, options)` | 配置桶通知 |
| `teardownCoordination(bucket, options?)` | 清除桶通知 |

## 关键规则

**始终：** 在 `result.data` 之前检查 `result.error` | 调用相应的 `teardown*` 以撤销凭证并删除桶 — 代理会快速泄漏桶 | 在调用 `createForks` 或 `checkpoint` 之前启用基础桶的快照 | 使用每个分支/每个工作区的范围凭证，以便一个代理的漏洞不会暴露其他代理

**永不：** 在代理之间重用单个共享访问密钥 — 这会破坏范围凭证的目的 | 在长时间运行的服务中跳过清理 — 孤立桶会累积计费 | 假设 `restore` 修改原始桶 — 它会创建一个新的分支

## 常见错误

| 错误 | 修复 |
|---|---|
| `createForks` 失败，提示“快照未启用” | 使用 `enableSnapshot: true` 重新创建基础桶 |
| 代理运行后分支未清理 | 始终在 `finally` 块中配对 `createForks` 与 `teardownForks` |
| webhook 从未触发 | 检查 `filter` 语法 — 必须是针对 `key`、`event` 等的有效 SQL `WHERE` 子句 |
| 工作区 TTL 不会删除桶 | TTL 过期对象，而不是桶本身。调用 `teardownWorkspace` 删除桶 |
| 恢复的桶为空 | 在调用 `restore` 之前，使用 `listCheckpoints` 验证 `snapshotId` 是否存在 |

## 相关技能

- **tigris-snapshots-forking** — `@tigrisdata/storage` 中的较低级别快照和分支基础构件
- **tigris-bucket-management** — 桶创建、区域、快照配置
- **tigris-security-access-control** — IAM、范围密钥、密钥轮换
- **file-storage** — 核心的 `@tigrisdata/storage` SDK，用于在分支或工作区桶内读取/写入

## 官方文档

- 包：https://www.npmjs.com/package/@tigrisdata/agent-kit
- 源代码：https://github.com/tigrisdata/storage/tree/main/packages/agent-kit
