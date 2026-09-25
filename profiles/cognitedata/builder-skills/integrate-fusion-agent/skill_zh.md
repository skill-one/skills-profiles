# 集成 Atlas / EOS 侧边栏

默认 AI 路径：通过 `@cognite/app-sdk` 使用平台 Atlas 侧边栏（EOS / Fusion PAIA）。不要嵌入 `useAtlasChat`、供应商 `atlas-agent` 或调用第三方 LLM API。

仅在用户明确要求应用内聊天 **并且** `connectToHostApp` 无法提供侧边栏（独立应用；始终拒绝）时，才使用 `integrate-atlas-chat`。没有用于此目的的清单字段。

仅实现所需功能：

1. **打开** — 顶部栏 Atlas 按钮；`sendAgentLayoutMode` 用于应用内触发
2. **消息** — `sendAgentMessage` 用于注入上下文
3. **服务器** — 资源（应用状态）和操作（工具）

---

## 第 0 步 — 阅读应用

- `package.json` — 包管理器，`@cognite/app-sdk`
- `src/App.tsx` — 结构，现有 SDK 使用

询问需要哪三种功能中的哪些。除非他们已经坚持，否则不要提供应用内聊天。

---

## 第 1 步 — 安装

`pnpm add @cognite/app-sdk`（或 npm/yarn）。最低版本 `0.3.1`。

---

## 第 2 步 — 连接到主机

`connectToHostApp` 在 Fusion 外部（独立 `vite dev`）时拒绝。捕获该错误；当 `api` 为 null 时隐藏代理触发器。

Comlink 代理可调用 — `setApi(proxy)` 使 React 将代理视为更新器并存储一个 Promise。始终 `setApi(() => resolvedApi)`。

```typescript
// src/hooks/useHostApp.ts
import { useState, useEffect } from 'react';
import { connectToHostApp, type HostAppAPI } from '@cognite/app-sdk';

export function useHostApp(): HostAppAPI | null {
  const [api, setApi] = useState<HostAppAPI | null>(null);

  useEffect(() => {
    connectToHostApp({ applicationName: 'my-app' })
      .then(({ api: resolvedApi }) => setApi(() => resolvedApi))
      .catch(() => { /* 在 Fusion 外部 — 无操作 */ });
  }, []);

  return api;
}
```

在根处调用；将 `api` 向下传递或通过上下文传递。`typeof proxy.method === 'function'` 始终为 true — 不要使用 `typeof` 进行特性检测；使用 try/catch。

---

## 第 3 步 — 打开侧边栏

主要启动器：Aura 顶部栏 Atlas (`systemActions.atlas.visible: true`，参见 `use-topbar`)。没有第二个“打开助手”控制。

`sendAgentLayoutMode` 仅用于上下文触发 (`sidebar` | `fullscreen` | `closed`)：

```typescript
await api.sendAgentLayoutMode({ mode: 'sidebar' });
```

---

## 第 4 步 — 发送消息

与 `sendAgentLayoutMode` 配对。`newSession: true` 用于从项目创建新任务；省略以继续线程。将名称/ID/状态放入消息中 — 一次侧边栏交互，而不是 N 次查询行上的完成。

```typescript
await api.sendAgentLayoutMode({ mode: 'sidebar' });
await api.sendAgentMessage({
  message: `分析 "${itemName}" 的日程并建议如何减少总持续时间。`,
  newSession: true,
});
```

---

## 第 5 步 — 代理服务器

挂载时注册，卸载时注销。工厂接受服务作为参数，因此可以在不使用 React 的情况下进行单元测试：

```
src/features/agent/
  agentActions.ts     — (deps) => Action[]
  agentResources.ts   — (deps) => Resource[]
  useAgentServer.ts   — 注册 / 注销
```

资源 `read()` 返回 `{ type: 'json', data }`（首选）或 `{ type: 'text', text }`。写 `description` 像文档字符串。

```typescript
// src/features/agent/agentResources.ts
import { createAgentResource } from '@cognite/app-sdk';

export function buildAgentResources(storage: StorageService) {
  return [
    createAgentResource({
      uri: 'my-app://current-state',
      name: '当前应用状态',
      description:
        '当前可见的项目、它们的状态和活动过滤器。在回答有关用户正在查看的内容的问题之前读取。',
      async read() {
        return [{ type: 'json', data: storage.getAll() }];
      },
    }),
  ];
}
```

操作：`snake_case` 名称，Zod 参数，每个字段上的 `.describe()`。代理**不会**在调用前确认 — 变更操作必须在 `description` 中说明，并需要先获得用户批准。

```typescript
// src/features/agent/agentActions.ts
import { createAgentAction } from '@cognite/app-sdk';
import { z } from 'zod';

export function buildAgentActions(dataService: DataService) {
  return [
    createAgentAction({
      name: 'get_item_details',
      description: '通过 ID 获取项目的详细信息，包括历史记录。',
      parameters: z.object({
        item_id: z.string().describe('要检索的项目 ID'),
      }),
      async handler({ item_id }) {
        const item = await dataService.getItem(item_id);
        return { content: [{ type: 'json', data: item }] };
      },
    }),
  ];
}
```

```typescript
createAgentAction({
  name: 'update_item_status',
  description:
    '更新项目状态。仅在用户明确批准更改时调用。',
  parameters: z.object({
    item_id: z.string().describe('要更新的项目'),
    status: z.enum(['active', 'closed', 'pending']).describe('新的状态'),
  }),
  async handler({ item_id, status }) {
    storage.updateStatus(item_id, status);
    return { content: [{ type: 'json', data: { success: true } }] };
  },
})
```

```typescript
// src/features/agent/useAgentServer.ts
import { useEffect } from 'react';
import { createAgentServer, registerAgentServer, type HostAppAPI } from '@cognite/app-sdk';
import { buildAgentActions } from './agentActions';
import { buildAgentResources } from './agentResources';
import { useStorageService } from '../storage/StorageServiceContext';
import { useDataService } from '../data/DataServiceContext';

export function useAgentServer(api: HostAppAPI | null): void {
  const storage = useStorageService();
  const dataService = useDataService();

  useEffect(() => {
    if (!api) return;
    const server = createAgentServer({
      uri: 'my-app', // Fusion 命名空间与实例 ID
      actions: buildAgentActions(dataService),
      resources: buildAgentResources(storage),
    });
    void registerAgentServer(api, server).catch((err: unknown) => {
      console.warn('[agent] registerAgentServer failed:', err);
    });
    return () => {
      void api.unregisterAgentServer('my-app').catch((err: unknown) => {
        console.warn('[agent] unregisterAgentServer failed:', err);
      });
    };
  }, [api, storage, dataService]);
}
```

---

## 第 6 步 — 连接在一起

```tsx
function App() {
  const api = useHostApp();
  useAgentServer(api);

  return (
    <AppLayout>
      <MainContent onAnalyseItem={async (item) => {
        if (!api) return;
        await api.sendAgentLayoutMode({ mode: 'sidebar' });
        await api.sendAgentMessage({
          message: `分析 "${item.name}" (id: ${item.id}).`,
          newSession: true,
        });
      }} />
    </AppLayout>
  );
}
```

直接测试工厂：

```typescript
const [getItemAction] = buildAgentActions({
  getItem: vi.fn().mockResolvedValue({ id: '1', name: 'Test' }),
});
const result = await getItemAction.handler({ item_id: '1' });
expect(result.content[0].data).toEqual({ id: '1', name: 'Test' });
```

---

## 严格限制 — 查询结果上的 LLM 调用

不要将聊天完成（Atlas `agents/chat`、OpenAI/Anthropic、`useAtlasChat().send`）映射到 DMS/SDK 行。优先使用一个 `sendAgentMessage` 或侧边栏代理可以读取的资源。

如果每项完成是明确的产品要求（默认：否）：

| 规则 | 限制 |
| --- | --- |
| 默认 | **5** 每个用户发起操作的完成 |
| 上限 | **50** — 永不生成可以超过此限制的代码 |
| 缓存 | `space:externalId:lastUpdatedTime`；命中不会消耗预算 |
| 批量 | 一个涵盖 N 个项目的提示，而不是 N 次调用 |
| 触发器 | 仅用户发起 — 永不在渲染、轮询或无界列表上 |
| 用户体验 | 当限制截断集合时说明 |

禁止：`items.map((row) => complete(row))`，`Promise.all` 查询页面上的完成。

---

## 清单

- [ ] 顶部栏 Atlas 启动器 (`use-topbar`)；无应用内聊天小部件
- [ ] `@cognite/app-sdk@0.3.1+`；`setApi(() => resolvedApi)`；捕获外部-Fusion 拒绝
- [ ] 当 `api` 为 null 时隐藏触发器；服务器注册/注销时 `.catch()`
- [ ] 资源描述说明什么/何时；操作名称 `snake_case`；变更操作需要先获得用户批准
- [ ] 工厂接受服务作为参数；LLM-覆盖行限制（5 / 最大 50）并缓存（如果存在）
