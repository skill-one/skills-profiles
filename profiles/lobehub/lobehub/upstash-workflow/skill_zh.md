# Upstash 工作流实现指南

在 LobeHub 代码库中实现 Upstash Workflow + QStash 异步工作流的标准模式。

## 🎯 三个核心模式

LobeHub 中的每个工作流都结合了这三个模式。它们的存在是因为平台在三个方面对您进行了约束：速率限制使得盲目的发散执行变得危险，步骤限制限制了单个工作流的大小，幂等性要求重试不会重复处理。

1. **🔍 干运行模式** — 获取统计数据而不触发实际执行
2. **🌟 发散模式** — 将大批量拆分为更小的块进行并行处理
3. **🎯 单任务执行** — 每个工作流的执行处理 **恰好一个项目**

---

## 架构概述

所有工作流都遵循相同的 3 层架构：

```text
第 1 层：入口点 (process-*)
  ├─ 验证前提条件
  ├─ 计算要处理的项目总数
  ├─ 过滤现有项目
  ├─ 支持干运行模式（仅统计）
  └─ 如有必要则触发第 2 层

第 2 层：分页 (paginate-*)
  ├─ 处理基于游标的分页
  ├─ 为大批量实现发散
  ├─ 递归处理所有页面
  └─ 为每个项目触发第 3 层

第 3 层：单任务执行 (execute-* / generate-*)
  └─ 对一个项目执行实际业务逻辑
```

**代码库中的真实示例：** `welcome-placeholder`, `agent-welcome` — 查看 [`references/examples.md`](./references/examples.md)。

---

## 60 秒内了解三个模式

### 1. 干运行模式

在产生任何副作用之前短路第 1 层，以便调用者可以预览会发生什么：

```typescript
if (dryRun) {
  return {
    ...result,
    dryRun: true,
    message: `[DryRun] 将处理 ${itemsNeedingProcessing.length} 个项目`,
  };
}
```

用例：在提交之前检查将处理多少个项目。

### 2. 发散模式

第 2 层将过大的批量拆分为块，并递归地使用每个块重新触发自身。这避免了当一页包含太多项目时超出工作流步骤限制：

```typescript
const CHUNK_SIZE = 20;

if (itemIds.length > CHUNK_SIZE) {
  const chunks = chunk(itemIds, CHUNK_SIZE);
  await Promise.all(
    chunks.map((ids, idx) =>
      context.run(`workflow:fanout:${idx + 1}/${chunks.length}`, () =>
        WorkflowClass.triggerPaginateItems({ itemIds: ids }),
      ),
    ),
  );
}
```

默认值：`PAGE_SIZE = 50`（每页项目数），`CHUNK_SIZE = 20`（发散块中的项目数）。

### 3. 单任务执行

第 3 层始终每个调用处理恰好一个项目。并行性来自第 2 层发散到许多第 3 层调用，由 `flowControl` 控制：

```typescript
export const { POST } = serve<ExecutePayload>(
  async (context) => {
    const { itemId } = context.requestPayload ?? {};
    if (!itemId) return { success: false, error: 'Missing itemId' };

    const item = await context.run('workflow:get-item', () => getItem(itemId));
    const result = await context.run('workflow:execute', () => processItem(item));
    await context.run('workflow:save', () => saveResult(itemId, result));

    return { success: true, itemId, result };
  },
  {
    flowControl: { key: 'workflow.execute', parallelism: 10, ratePerSecond: 5 },
  },
);
```

---

## 文件结构

```text
src/
├── app/(backend)/api/workflows/
│   └── {workflow-name}/
│       ├── process-{entities}/route.ts      # 第 1 层
│       ├── paginate-{entities}/route.ts     # 第 2 层
│       └── execute-{entity}/route.ts        # 第 3 层
│
└── server/workflows/
    └── {workflowName}/
        └── index.ts                          # 工作流类
```

---

## 下一步该做什么

选择与您正在做的事情匹配的参考：

| 您想要...                                       | 阅读                                                             |
| ---------------------------------------------------- | ---------------------------------------------------------------- |
| 从头开始编写 Workflow 类 + 3 个路由             | [`references/implementation.md`](./references/implementation.md) |
| 调整 flowControl、错误处理、日志记录、测试   | [`references/best-practices.md`](./references/best-practices.md) |
| 查看两个端到端的真实工作流                      | [`references/examples.md`](./references/examples.md)             |
| 在 lobehub-cloud 上部署（重导出、仅云操作） | [`references/cloud.md`](./references/cloud.md)                   |

---

## 环境变量

```bash
# 所有工作流都需要
APP_URL=https://your-app.com # 工作流端点的基 URL
QSTASH_TOKEN=qstash_xxx      # QStash 认证令牌

# 可选（用于自定义 QStash URL）
QSTASH_URL=https://custom-qstash.com
```

---

## 新工作流的检查清单

### 规划

- [ ] 确定要处理的项目实体（用户、代理、项目、…）
- [ ] 定义每个项目的业务逻辑
- [ ] 确定过滤逻辑（Redis 缓存、数据库状态、…）

### 实现

- [ ] 使用 TypeScript 接口定义有效载荷类型
- [ ] 创建具有静态触发方法的 Workflow 类
- [ ] **第 1 层：** 具有干运行支持的入口点
- [ ] **第 1 层：** 避免重复工作的过滤逻辑
- [ ] **第 2 层：** 带有发散的分页
- [ ] **第 3 层：** 单任务执行（每个运行处理 **一个项目**）
- [ ] 为每一层配置适当的 `flowControl`
- [ ] 使用工作流前缀进行一致日志记录
- [ ] 验证所有必需的有效载荷参数
- [ ] 确保所有 `context.run()` 步骤名称唯一

### 质量与部署

- [ ] 返回一致的有效载荷形状
- [ ] 配置云部署（如果在 lobehub-cloud 上，请参考 [`references/cloud.md`](./references/cloud.md)）
- [ ] 编写集成测试（`dryRun` 路径 + 完整路径）
- [ ] 首先使用干运行进行冒烟测试
- [ ] 在全面推广之前使用小批量进行测试

---

## 其他资源

- [Upstash Workflow 文档](https://upstash.com/docs/workflow)
- [QStash 文档](https://upstash.com/docs/qstash)
- [代码库中的示例工作流](<../../src/app/(backend)/api/workflows/>)
- [Workflow 类](../../apps/server/src/workflows/)
