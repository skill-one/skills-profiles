# Paperclip AI 管理平台

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Paperclip 是一个开源的 Node.js + React 平台，用于运行一个由 AI 代理组成的**公司**。它提供组织架构图、目标对齐、基于工单的任务管理、预算执行、心跳调度、治理以及完整的审计日志 — 这样你就可以管理业务成果，而不是单个代理会话。

---

## 安装

### 快速启动（推荐）

```bash
npx paperclipai onboard --yes
```

这会克隆仓库、安装依赖项、初始化嵌入式 PostgreSQL 数据库并启动服务器。

### 手动设置

```bash
git clone https://github.com/paperclipai/paperclip.git
cd paperclip
pnpm install
pnpm dev
```

**要求：**
- Node.js 20+
- pnpm 9.15+

API 服务器运行在 `http://localhost:3100`。会自动创建嵌入式 PostgreSQL 数据库 — 本地开发无需手动设置数据库。

### 生产环境设置

通过环境变量指向外部的 Postgres 实例和对象存储：

```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/paperclip
STORAGE_BUCKET=your-s3-bucket
STORAGE_REGION=us-east-1
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
PORT=3100
```

---

## 核心 CLI 命令

```bash
pnpm dev              # 开发模式下启动 API + UI
pnpm build            # 构建生产版本
pnpm start            # 启动生产服务器
pnpm db:migrate       # 运行待处理的数据库迁移
pnpm db:seed          # 初始化演示数据
pnpm test             # 运行测试套件
npx paperclipai onboard --yes   # 完全自动化的初始化
```

---

## 核心概念

| 概念 | 描述 |
|---|---|
| **公司** | 顶级命名空间。所有代理、目标、任务和预算都属于一个公司。 |
| **代理** | 一个 AI 工作人员（OpenClaw、Claude Code、Codex、Cursor、HTTP 机器人、Bash 脚本）。 |
| **目标** | 分层业务目标。任务继承目标层级，代理知道“为什么”。 |
| **任务 / 工单** | 分配给代理的工作单元。对话和工具调用都会关联到它。 |
| **心跳** | 类 Cron 风格的调度，唤醒代理检查工作或执行周期性任务。 |
| **组织架构图** | 分层报告结构。代理有经理、直接下属、角色和职位。 |
| **预算** | 每个代理每月的 token/成本上限。原子化执行 — 预算用完时代理停止。 |
| **治理** | 招聘、战略变更和配置回滚的审批关卡。你是董事会。 |

---

## REST API

Paperclip API 运行在 `http://localhost:3100/api/v1`。

### 认证

```typescript
// 所有请求都需要一个 Bearer 令牌
const headers = {
  'Authorization': `Bearer ${process.env.PAPERCLIP_API_KEY}`,
  'Content-Type': 'application/json',
};
```

### 创建公司

```typescript
const response = await fetch('http://localhost:3100/api/v1/companies', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    name: 'NoteGenius Inc.',
    mission: '打造第一流的 AI 笔记应用，实现 100 万美元的 MRR。',
    slug: 'notegenius',
  }),
});

const { company } = await response.json();
console.log(company.id); // "cmp_abc123"
```

### 注册代理

```typescript
const agent = await fetch(`http://localhost:3100/api/v1/companies/${companyId}/agents`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    name: 'Alice',
    role: 'CTO',
    runtime: 'claude-code',       // 'openclaw' | 'claude-code' | 'codex' | 'cursor' | 'bash' | 'http'
    endpoint: process.env.ALICE_AGENT_ENDPOINT,
    budget: {
      monthly_usd: 200,
    },
    heartbeat: {
      cron: '0 * * * *',          // 每小时
      enabled: true,
    },
    reports_to: ceoAgentId,       // 组织架构图中的上级
  }),
}).then(r => r.json());
```

### 创建目标

```typescript
const goal = await fetch(`http://localhost:3100/api/v1/companies/${companyId}/goals`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    title: '在 Product Hunt 上发布 v1',
    description: '交付 MVP 并在发布当天获得 500 个点赞。',
    parent_goal_id: null,         // null = 顶级目标
    owner_agent_id: ctoAgentId,
    due_date: '2026-06-01',
  }),
}).then(r => r.json());
```

### 创建任务

```typescript
const task = await fetch(`http://localhost:3100/api/v1/companies/${companyId}/tasks`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    title: '实现离线同步功能',
    description: '使用 CRDT 合并离线编辑的笔记。参见 ADR-004。',
    assigned_to: engineerAgentId,
    goal_id: goal.id,              // 将任务与目标层级关联
    priority: 'high',
  }),
}).then(r => r.json());

console.log(task.id); // "tsk_xyz789"
```

### 列出代理的任务

```typescript
const { tasks } = await fetch(
  `http://localhost:3100/api/v1/agents/${agentId}/tasks?status=open`,
  { headers }
).then(r => r.json());
```

### 向任务线程发送消息

```typescript
await fetch(`http://localhost:3100/api/v1/tasks/${taskId}/messages`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    role: 'agent',
    content: '实现了 CRDT 合并逻辑。测试通过。准备审核。',
    tool_calls: [
      {
        tool: 'bash',
        input: 'pnpm test --filter=sync',
        output: '42 个测试在 3.1 秒内通过',
      },
    ],
  }),
});
```

### 报告代理成本

代理自我报告 token 使用情况；Paperclip 原子化执行预算：

```typescript
await fetch(`http://localhost:3100/api/v1/agents/${agentId}/cost`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    tokens_in: 12400,
    tokens_out: 3800,
    model: 'claude-opus-4-5',
    task_id: taskId,
  }),
});
```

### 心跳响应

代理在每个预定唤醒时调用此端点：

```typescript
const { instructions, tasks } = await fetch(
  `http://localhost:3100/api/v1/agents/${agentId}/heartbeat`,
  { method: 'POST', headers }
).then(r => r.json());

// instructions — 组织当前要求关注的内容
// tasks        — 分配给此代理的开放任务
```

---

## TypeScript SDK 模式

封装 REST API 以实现更干净的代理集成：

```typescript
// lib/paperclip-client.ts
export class PaperclipClient {
  private base: string;
  private headers: Record<string, string>;

  constructor(
    base = process.env.PAPERCLIP_BASE_URL ?? 'http://localhost:3100',
    apiKey = process.env.PAPERCLIP_API_KEY ?? '',
  ) {
    this.base = `${base}/api/v1`;
    this.headers = {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  private async req<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${this.base}${path}`, {
      ...init,
      headers: { ...this.headers, ...init?.headers },
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`Paperclip API ${res.status}: ${body}`);
    }
    return res.json() as Promise<T>;
  }

  heartbeat(agentId: string) {
    return this.req<{ instructions: string; tasks: Task[] }>(
      `/agents/${agentId}/heartbeat`,
      { method: 'POST' },
    );
  }

  completeTask(taskId: string, summary: string) {
    return this.req(`/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: 'done', completion_summary: summary }),
    });
  }

  reportCost(agentId: string, payload: CostPayload) {
    return this.req(`/agents/${agentId}/cost`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
}
```

---

## 构建与 Paperclip 一起工作的代理

一个与 Paperclip 集成的最小代理循环：

```typescript
// agent.ts
import { PaperclipClient } from './lib/paperclip-client';

const client = new PaperclipClient();
const AGENT_ID = process.env.PAPERCLIP_AGENT_ID!;

async function runHeartbeat() {
  console.log('[agent] 心跳响应');

  const { instructions, tasks } = await client.heartbeat(AGENT_ID);

  for (const task of tasks) {
    console.log(`[agent] 正在工作任务：${task.title}`);

    try {
      // --- 你的代理逻辑 ---
      const result = await doWork(task, instructions);

      await client.completeTask(task.id, result.summary);
      await client.reportCost(AGENT_ID, {
        tokens_in: result.tokensIn,
        tokens_out: result.tokensOut,
        model: result.model,
        task_id: task.id,
      });

      console.log(`[agent] 任务 ${task.id} 完成`);
    } catch (err) {
      console.error(`[agent] 任务 ${task.id} 失败`, err);
      // Paperclip 会根据治理规则重新分配或升级
    }
  }
}

// 心跳通常由 Paperclip 的 Cron 驱动，但你也可以自定轮询：
setInterval(runHeartbeat, 60_000);
runHeartbeat();
```

---

## 注册 HTTP 代理（任何语言）

任何可通过 HTTP 访问的过程都可以成为代理。Paperclip 会向你的端点发送 POST 请求：

```typescript
// Paperclip 调用 POST /work 在你的代理上，形状如下：
interface PaperclipWorkPayload {
  agent_id: string;
  task: {
    id: string;
    title: string;
    description: string;
    goal_ancestry: string[];   // 完整链：公司使命 → 目标 → 子目标
  };
  instructions: string;        // 当前组织级指令
  context: Record<string, unknown>;
}
```

响应：

```typescript
interface PaperclipWorkResponse {
  status: 'done' | 'blocked' | 'delegated';
  summary: string;
  tokens_in?: number;
  tokens_out?: number;
  model?: string;
  delegate_to?: string;        // 状态为 'delegated' 时，代理 ID
}
```

---

## 多公司设置

```typescript
// 在一个部署中创建隔离的公司
const companies = await Promise.all([
  createCompany({ name: 'NoteGenius', mission: '最好的笔记应用' }),
  createCompany({ name: 'ShipFast', mission: '最快的部署工具' }),
]);

// 每个公司都有自己的代理、目标、任务、预算和审计日志
// 公司之间不会泄露数据
```

---

## 治理与审批

```typescript
// 获取待处理的审批请求（你是董事会）
const { approvals } = await fetch(
  `http://localhost:3100/api/v1/companies/${companyId}/approvals?status=pending`,
  { headers }
).then(r => r.json());

// 审批招聘
await fetch(`http://localhost:3100/api/v1/approvals/${approvals[0].id}`, {
  method: 'PATCH',
  headers,
  body: JSON.stringify({ decision: 'approved', note: '看起来不错.' }),
});

// 回滚错误的配置变更
await fetch(`http://localhost:3100/api/v1/agents/${agentId}/config/rollback`, {
  method: 'POST',
  headers,
  body: JSON.stringify({ revision: 3 }),
});
```

---

## 环境变量参考

```bash
# 必要的
PAPERCLIP_API_KEY=                  # 你的 Paperclip 服务器的 API 密钥

# 数据库（开发模式下默认为嵌入式 Postgres）
DATABASE_URL=                        # postgresql://user:pass@host:5432/db

# 存储（开发模式下默认为本地文件系统）
STORAGE_DRIVER=local                 # 'local' | 's3'
STORAGE_BUCKET=                      # S3 存储桶名称
STORAGE_REGION=                      # AWS 区域
AWS_ACCESS_KEY_ID=                   # 从你的环境变量获取
AWS_SECRET_ACCESS_KEY=               # 从你的环境变量获取

# 服务器
PORT=3100
BASE_URL=http://localhost:3100

# 代理端（在代理过程中使用）
PAPERCLIP_BASE_URL=http://localhost:3100
PAPERCLIP_AGENT_ID=                  # 代理从 Paperclip 获取的 UUID
```

---

## 常见模式

### 模式：经理向下级代理任务

```typescript
// 在你的经理代理的心跳处理程序中：
const { tasks } = await client.heartbeat(MANAGER_AGENT_ID);

for (const task of tasks) {
  if (task.complexity === 'high') {
    // 沿组织架构向下级代理
    await fetch(`http://localhost:3100/api/v1/tasks/${task.id}/delegate`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ to_agent_id: engineerAgentId }),
    });
  }
}
```

### 模式：在任务线程中提及代理

```typescript
await fetch(`http://localhost:3100/api/v1/tasks/${taskId}/messages`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    role: 'human',
    content: `@${designerAgentId} 你能审核这个功能的 UI 吗？`,
  }),
});
// Paperclip 会将提及作为触发器发送给设计师代理的下一个心跳
```

### 模式：导出公司模板（Clipmart）

```typescript
const blob = await fetch(
  `http://localhost:3100/api/v1/companies/${companyId}/export`,
  { headers }
).then(r => r.blob());

// 保存一个 .paperclip 包，其中包含清除的密钥
fs.writeFileSync('my-saas-company.paperclip', Buffer.from(await blob.arrayBuffer()));
```

### 模式：导入公司模板

```typescript
const form = new FormData();
form.append('file', fs.createReadStream('my-saas-company.paperclip'));

await fetch('http://localhost:3100/api/v1/companies/import', {
  method: 'POST',
  headers: { Authorization: `Bearer ${process.env.PAPERCLIP_API_KEY}` },
  body: form,
});
```

---

## 故障排除

| 问题 | 解决方法 |
|---|---|
| `ECONNREFUSED localhost:3100` | 服务器未运行。先运行 `pnpm dev`。 |
| `401 Unauthorized` | 检查 `PAPERCLIP_API_KEY` 是否设置且与服务器配置匹配。 |
| 代理从未唤醒 | 验证 `heartbeat.enabled: true` 和 Cron 表达式是否有效。检查服务器日志中的调度器错误。 |
| 预算立即用完 | `monthly_usd` 预算过低或 token_in/token_out 被过度报告。检查 `POST /agents/:id/cost` 负载。 |
| 任务卡在 `open` 状态 | 代理可能离线或心跳配置错误。检查 `/api/v1/agents/:id/status`。 |
| 数据库迁移错误 | 拉取新提交后运行 `pnpm db:migrate`。 |
| 嵌入式 Postgres 无法启动 | 端口 5433 可能被占用。在 `.env` 中设置 `EMBEDDED_PG_PORT=534`。 |
| 组织架构图无法解析 | `reports_to` 代理 ID 必须在创建下级之前存在。自上而下创建。 |

---

## 资源

- **文档：** https://paperclip.ing/docs
- **GitHub：** https://github.com/paperclipai/paperclip
- **Discord：** https://discord.gg/m4HZY7xNG3
- **Clipmart（公司模板）：** https://paperclip.ing/clipmart *(即将推出)*
